/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

const TABS = 5000;

const PATTERNS = [
  "idle",
  "scroll",
  "type",
  "navigate",
  "replaceState",
  "open tab",
  "move tab",
  "close window",
];

var perfMetadata = {
  owner: "Session Restore",
  name: "SessionStoreChanges",
  description:
    "Main thread time and size of the session database batch for common changes to a 5,000 tab session, next to those of the JSON file that every save writes.",
  options: {
    default: {
      perfherder: true,
      perfherder_metrics: [
        { name: "json main thread", unit: "ms" },
        { name: "json bytes", unit: "bytes" },
        ...PATTERNS.flatMap(pattern => [
          { name: `${pattern} db main thread`, unit: "ms" },
          { name: `${pattern} db bytes`, unit: "bytes" },
        ]),
      ],
      verbose: true,
    },
  },
  tags: ["sessionstore"],
};

/**
 * Each change edits the state as SessionStore would before a save. The active
 * window is recollected on every save, so its tabs are new objects.
 */
const CHANGES = {
  idle() {},
  scroll(state) {
    let tab = state.windows[0].tabs[3];
    tab.scroll = { scroll: `0,${Math.floor(random() * 5000)}` };
  },
  type(state) {
    let tab = state.windows[0].tabs[3];
    tab.formdata = { id: { q: randomString(20) }, url: tab.entries[0].url };
  },
  navigate(state) {
    let tab = state.windows[0].tabs[3];
    // The tab state cache edits its history in place.
    tab.entries.push({
      ...tab.entries.at(-1),
      url: `https://${randomString(20)}.test/`,
    });
    SessionChangeJournal.markChanged(tab.entries);
    tab.index = tab.entries.length;
  },
  replaceState(state) {
    let tab = state.windows[0].tabs[3];
    tab.entries.splice(-1, 1, {
      ...tab.entries.at(-1),
      structuredCloneState: btoa(randomString(100000)),
      structuredCloneVersion: 8,
    });
    SessionChangeJournal.markChanged(tab.entries);
  },
  "open tab": function (state) {
    state.windows[0].tabs.splice(1, 0, makeTab(Math.floor(random() * 1e9)));
  },
  "move tab": function (state) {
    let { tabs } = state.windows[0];
    let [tab] = tabs.splice(10, 1);
    tabs.splice(100, 0, tab);
  },
  "close window": function (state) {
    state._closedWindows.unshift(state.windows.pop());
  },
};

/**
 * Undoes changes that would otherwise accumulate across iterations.
 */
const UNDO = {
  "close window": function (state) {
    state.windows.push(state._closedWindows.shift());
  },
};

function batchSize(ops) {
  let size = 0;
  for (let op of ops) {
    size += typeof op == "string" ? op.length : 0;
  }
  return size;
}

add_task(async function test_changes() {
  let metrics = {};
  let state = makeState(TABS);
  let jsonPath = PathUtils.join(PathUtils.profileDir, "changes.jsonlz4");
  let dbPath = PathUtils.join(PathUtils.profileDir, "changes.sqlite");

  let jsonMain = [];
  await measure(async () => {
    let start = ChromeUtils.now();
    let promise = IOUtils.writeJSON(jsonPath, state, { compress: true });
    jsonMain.push(ChromeUtils.now() - start);
    await promise;
  });
  metrics["json main thread"] = median(jsonMain);
  metrics["json bytes"] = await fileSize(jsonPath);

  let db = await SessionStoreDB.open(dbPath);
  let writer = new SessionDBWriter();
  await db.write(writer.materialize(state));
  let save = async () => {
    recollect(state.windows[0]);
    let start = ChromeUtils.now();
    let ops = writer.materialize(state);
    let time = ChromeUtils.now() - start;
    await db.write(ops);
    return { time, size: batchSize(ops) };
  };

  for (let pattern of PATTERNS) {
    let times = [];
    let sizes = [];
    await measure(async () => {
      CHANGES[pattern](state);
      let { time, size } = await save();
      times.push(time);
      sizes.push(size);
      if (UNDO[pattern]) {
        UNDO[pattern](state);
        await save();
      }
    });
    metrics[`${pattern} db main thread`] = median(times);
    metrics[`${pattern} db bytes`] = median(sizes);
  }
  await db.close();

  info("perfMetrics", metrics);
  Assert.ok(true, "Benchmarks ran");
});
