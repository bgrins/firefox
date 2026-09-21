/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

"use strict";

const SIZES = [50, 500, 5000, 20000];
const ITERATIONS = 3;

const METRICS = [
  "json save main thread",
  "json save total",
  "db full save main thread",
  "db full save total",
  "db one-change save main thread",
  "db one-change save total",
  "db one-change save rows",
  "json read",
  "db read",
  "json file size",
  "db file size",
];

function unitOf(metric) {
  if (metric.endsWith("size")) {
    return "bytes";
  }
  return metric.endsWith("rows") ? "count" : "ms";
}

var perfMetadata = {
  owner: "Session Restore",
  name: "SessionStoreBackends",
  description:
    "Save and startup-read costs of the JSON session file and the session database, for synthetic sessions.",
  options: {
    default: {
      perfherder: true,
      perfherder_metrics: SIZES.flatMap(size =>
        METRICS.map(metric => ({
          name: `${metric} ${size} tabs`,
          unit: unitOf(metric),
        }))
      ),
      verbose: true,
    },
  },
  tags: ["sessionstore"],
};

const { SessionDBWriter } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs"
);
const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
);

do_get_profile();

let gSeed = 123456;
function random() {
  gSeed = Math.imul(gSeed, 22695477) + 1;
  return (gSeed >> 1) / 0x7fffffff + 0.5;
}

function randomString(length) {
  let chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(random() * chars.length)];
  }
  return result;
}

const PRINCIPAL = btoa(randomString(120));
const FAVICONS = Array.from(
  { length: 20 },
  () => "data:image/png;base64," + btoa(randomString(3000))
);

/**
 * Builds a tab state whose shape follows what SessionStore collects: a few
 * history entries, sometimes with pushState data, a favicon on some tabs,
 * and form data, scroll positions and sessionStorage on a few.
 */
function makeTab(i) {
  let entries = [];
  let count = 1 + Math.floor(random() * 5);
  for (let e = 0; e < count; e++) {
    let url = `https://site${i % 300}.test/${randomString(30)}`;
    let entry = {
      url,
      title: randomString(40),
      cacheKey: 0,
      ID: i * 10 + e,
      docshellUUID: `{${randomString(36)}}`,
      triggeringPrincipal_base64: PRINCIPAL,
      hasUserInteraction: true,
      docIdentifier: i * 10 + e,
      persist: true,
    };
    if (random() < 0.1) {
      entry.structuredCloneState = btoa(
        randomString(random() < 0.02 ? 50000 : 1000)
      );
      entry.structuredCloneVersion = 8;
    }
    entries.push(entry);
  }
  let tab = {
    entries,
    index: entries.length,
    lastAccessed: 1700000000000 + i,
    hidden: false,
    userContextId: 0,
    attributes: {},
    image: random() < 0.3 ? FAVICONS[i % FAVICONS.length] : null,
    searchMode: null,
  };
  if (random() < 0.3) {
    tab.scroll = { scroll: `0,${Math.floor(random() * 5000)}` };
  }
  if (random() < 0.05) {
    tab.formdata = { id: { q: randomString(20) }, url: entries[0].url };
  }
  if (random() < 0.1) {
    tab.storage = {
      [`https://site${i % 300}.test`]: { key: randomString(500) },
    };
  }
  return tab;
}

function makeState(tabCount) {
  let windows = [];
  for (let w = 0; w < Math.max(1, Math.ceil(tabCount / 2000)); w++) {
    windows.push({
      tabs: [],
      selected: 1,
      _closedTabs: [],
      closedGroups: [],
      width: 1200,
      height: 800,
    });
  }
  for (let i = 0; i < tabCount; i++) {
    windows[i % windows.length].tabs.push(makeTab(i));
  }
  for (let win of windows) {
    for (let c = 0; c < 10; c++) {
      win._closedTabs.push({
        state: makeTab(tabCount + c),
        title: randomString(20),
        closedAt: 1,
        closedId: c,
        pos: 0,
      });
    }
  }
  return {
    version: ["sessionrestore", 1],
    windows,
    _closedWindows: [],
    savedGroups: [],
    session: { lastUpdate: 1, startTime: 1, recentCrashes: 0 },
    global: {},
    cookies: [],
    selectedWindow: 1,
  };
}

function median(values) {
  let sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

async function measure(fn) {
  let times = [];
  for (let i = 0; i < ITERATIONS; i++) {
    times.push(await fn());
  }
  return median(times);
}

async function fileSize(path) {
  let total = 0;
  for (let suffix of ["", "-wal"]) {
    if (await IOUtils.exists(path + suffix)) {
      total += (await IOUtils.stat(path + suffix)).size;
    }
  }
  return total;
}

async function benchmark(tabCount) {
  let metrics = {};
  let record = (name, value) => (metrics[`${name} ${tabCount} tabs`] = value);
  let state = makeState(tabCount);
  let jsonPath = PathUtils.join(
    PathUtils.profileDir,
    `bench-${tabCount}.jsonlz4`
  );
  let dbPath = PathUtils.join(PathUtils.profileDir, `bench-${tabCount}.sqlite`);

  let jsonMain = [];
  record(
    "json save total",
    await measure(async () => {
      let start = ChromeUtils.now();
      let promise = IOUtils.writeJSON(jsonPath, state, {
        compress: true,
        tmpPath: jsonPath + ".tmp",
      });
      jsonMain.push(ChromeUtils.now() - start);
      await promise;
      return ChromeUtils.now() - start;
    })
  );
  record("json save main thread", median(jsonMain));

  let db = await SessionStoreDB.open(dbPath);
  let writer = new SessionDBWriter();
  let fullMain = [];
  record(
    "db full save total",
    await measure(async () => {
      writer.reset();
      let start = ChromeUtils.now();
      let ops = writer.materialize(state);
      fullMain.push(ChromeUtils.now() - start);
      await db.write(ops);
      return ChromeUtils.now() - start;
    })
  );
  record("db full save main thread", median(fullMain));

  let oneMain = [];
  let rows = [];
  record(
    "db one-change save total",
    await measure(async () => {
      let tabs = state.windows[0].tabs;
      tabs[0] = { ...tabs[0], scroll: { scroll: `0,${random()}` } };
      let start = ChromeUtils.now();
      let ops = writer.materialize(state);
      oneMain.push(ChromeUtils.now() - start);
      rows.push(ops.filter(op => op == "node" || op == "section").length);
      await db.write(ops);
      return ChromeUtils.now() - start;
    })
  );
  record("db one-change save main thread", median(oneMain));
  record("db one-change save rows", median(rows));

  record(
    "db read",
    await measure(async () => {
      let start = ChromeUtils.now();
      await db.read();
      return ChromeUtils.now() - start;
    })
  );
  await db.close();

  record(
    "json read",
    await measure(async () => {
      let start = ChromeUtils.now();
      JSON.parse(await IOUtils.readUTF8(jsonPath, { decompress: true }));
      return ChromeUtils.now() - start;
    })
  );

  record("json file size", await fileSize(jsonPath));
  record("db file size", await fileSize(dbPath));
  await IOUtils.remove(jsonPath);
  for (let suffix of ["", "-wal", "-shm"]) {
    await IOUtils.remove(dbPath + suffix, { ignoreAbsent: true });
  }
  return metrics;
}

add_task(async function test_backends() {
  let metrics = {};
  for (let size of SIZES) {
    Object.assign(metrics, await benchmark(size));
  }
  info("perfMetrics", metrics);
  Assert.ok(true, "Benchmarks ran");
});
