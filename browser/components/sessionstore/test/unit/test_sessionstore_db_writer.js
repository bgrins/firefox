/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { SessionChangeJournal } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionChangeJournal.sys.mjs"
);
const { SessionDBWriter } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs"
);
const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
);

do_get_profile();

const ARITY = {
  guard: 2,
  clear: 0,
  node: 4,
  nullnode: 3,
  delnode: 1,
  order: 3,
  delorder: 2,
  section: 3,
  delsection: 2,
  root: 2,
  delroot: 1,
  meta: 2,
};

/**
 * Splits a flat batch into [name, ...args] operations, leaving out guards
 * and meta values, which every batch has.
 */
function contentOps(ops) {
  let result = [];
  for (let i = 0; i < ops.length; ) {
    let name = ops[i];
    let op = ops.slice(i, i + 1 + ARITY[name]);
    i += op.length;
    if (name != "guard" && name != "meta") {
      result.push(op);
    }
  }
  return result;
}

let gCount = 0;

async function openDB() {
  let path = PathUtils.join(PathUtils.profileDir, `writer-${gCount++}.sqlite`);
  return { db: await SessionStoreDB.open(path), path };
}

async function writeAndCheck(db, writer, state, message) {
  let ops = writer.materialize(state);
  await db.write(ops);
  Assert.deepEqual(
    (await db.read()).state,
    JSON.parse(JSON.stringify(state)),
    message
  );
  return contentOps(ops);
}

function makeTab(url, extra = {}) {
  return {
    entries: [{ url, title: url, triggeringPrincipal_base64: "principal" }],
    index: 1,
    lastAccessed: 1,
    hidden: false,
    userContextId: 0,
    attributes: {},
    image: null,
    ...extra,
  };
}

function makeState() {
  return {
    version: ["sessionrestore", 1],
    windows: [
      {
        tabs: [
          makeTab("https://a.test/"),
          makeTab("https://b.test/", {
            scroll: { scroll: "0,5" },
            formdata: { id: { q: "x" }, url: "https://b.test/" },
          }),
        ],
        selected: 1,
        _closedTabs: [
          {
            state: makeTab("https://c.test/"),
            title: "c",
            pos: 1,
            closedAt: 5,
            closedId: 1,
          },
        ],
        closedGroups: [],
        groups: [{ id: "g1", name: "G", color: "blue", collapsed: false }],
        width: 800,
      },
    ],
    _closedWindows: [],
    savedGroups: [
      {
        id: "g2",
        saved: true,
        tabs: [{ state: makeTab("https://d.test/"), title: "d" }],
      },
    ],
    session: { lastUpdate: 1, startTime: 1, recentCrashes: 0 },
    global: { key: "v" },
    cookies: [{ host: "a.test", value: "1", name: "c" }],
    selectedWindow: 1,
  };
}

add_task(async function test_first_batch_rewrites_everything() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let ops = await writeAndCheck(db, writer, makeState(), "Full round trip");
  Assert.deepEqual(ops[0], ["clear"], "The first batch starts from scratch");
  await db.close();
});

add_task(async function test_unchanged_state_writes_nothing() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  await writeAndCheck(db, writer, state);

  Assert.deepEqual(
    await writeAndCheck(db, writer, state),
    [],
    "Nothing changes for the same objects"
  );
  Assert.deepEqual(
    await writeAndCheck(db, writer, makeState()),
    [],
    "Nothing changes for recreated objects with the same content"
  );
  await db.close();
});

add_task(async function test_small_changes_write_small_batches() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  await writeAndCheck(db, writer, state);

  let [win] = state.windows;
  win.tabs[1] = { ...win.tabs[1], scroll: { scroll: "0,99" } };
  let ops = await writeAndCheck(db, writer, state, "Scroll change");
  Assert.deepEqual(
    ops.map(([name, , section]) => [name, section]),
    [["section", "scroll"]],
    "A scroll change writes only the scroll section"
  );

  win.tabs.splice(1, 0, makeTab("https://new.test/"));
  ops = await writeAndCheck(db, writer, state, "Tab insertion");
  Assert.deepEqual(
    ops.map(([name, ...args]) =>
      name == "section" ? [name, args[1]] : [name]
    ),
    [["node"], ["section", "history"], ["section", "image"], ["order"]],
    "A new tab writes its own rows and its window's order"
  );

  state._closedWindows.unshift(win);
  state.windows = [];
  win.closedAt = 10;
  ops = await writeAndCheck(db, writer, state, "Window close");
  Assert.deepEqual(
    ops.map(([name, ...args]) => [name, ...args.slice(1, 3)]),
    [
      ["node", 0, "_closedWindows"],
      ["order", "windows", "[]"],
      ["order", "_closedWindows", ops[2][3]],
    ],
    "Closing a window moves its node without rewriting its tabs"
  );

  win._closedTabs = [];
  ops = await writeAndCheck(db, writer, state, "Forgotten closed tab");
  Assert.deepEqual(
    ops.map(([name]) => name),
    ["order", "delnode", "delnode"],
    "Forgetting a closed tab deletes it and its state"
  );
  await db.close();
});

add_task(async function test_values_json_treats_specially() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  let [win] = state.windows;
  // eslint-disable-next-line no-sparse-arrays
  win.tabs = [makeTab("https://a.test/"), , makeTab("https://b.test/")];
  win.tabs.push(undefined, () => {}, new Date(0), 5, "text", [1, [2]]);
  win.tabs.push({ toJSON: () => ({ replaced: true }) });
  win.tabs.push(makeTab("https://e.test/", { image: "data:x", unknown: [{}] }));
  win._closedTabs.push({ state: null, title: "no state", permanentKey: {} });
  win.closedGroups.push({ id: "g3", tabs: [] });
  state.lastSessionState = {
    windows: [{ tabs: [makeTab("https://f.test/")] }],
  };
  state.global = undefined;
  state.extra = { nested: { deeper: [null, true] } };
  await writeAndCheck(db, writer, state, "Unusual values round-trip");

  delete state.lastSessionState;
  state.global = { back: 1 };
  await writeAndCheck(db, writer, state, "Root members come and go");
  await db.close();
});

add_task(async function test_failed_batch_forces_rewrite() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  await writeAndCheck(db, writer, state);

  state.windows[0].width = 1;
  writer.materialize(state);
  state.windows[0].width = 2;
  let queued = writer.materialize(state);
  await Assert.rejects(
    db.write(queued),
    ex => ex.result == Cr.NS_ERROR_ABORT,
    "A batch queued behind a lost one fails its guard"
  );

  writer.reset();
  let ops = await writeAndCheck(db, writer, state, "Rewrite after failure");
  Assert.deepEqual(ops[0], ["clear"], "The writer starts over after a reset");
  await db.close();
});

add_task(async function test_new_writer_continues_the_generation() {
  let { db, path } = await openDB();
  let writer = new SessionDBWriter();
  let ops = writer.materialize(makeState());
  await db.write(ops);
  let maxId = Math.max(
    ...contentOps(ops)
      .filter(([name]) => name == "node" || name == "nullnode")
      .map(([, id]) => Number(id))
  );
  await db.close();

  db = await SessionStoreDB.open(path);
  let { meta } = await db.read();
  Assert.equal(meta.seq, "1");
  writer = new SessionDBWriter(meta);
  ops = writer.materialize(makeState());
  await db.write(ops);
  let { meta: newMeta } = await db.read();
  Assert.equal(newMeta.seq, "2", "The seq continues");
  Assert.equal(newMeta.lineage, meta.lineage, "The lineage is kept");
  let newIds = contentOps(ops)
    .filter(([name]) => name == "node" || name == "nullnode")
    .map(([, id]) => Number(id));
  Assert.ok(
    newIds.every(id => id > maxId),
    "Node ids are never reused"
  );
  await db.close();
});

add_task(async function test_unchanged_tabs_are_not_serialized() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let serializations = 0;
  let entry = {
    url: "https://a.test/",
    toJSON() {
      serializations++;
      return { url: this.url };
    },
  };
  let state = makeState();
  let [win] = state.windows;
  win.tabs[0].entries = [entry];
  let save = async () => {
    let before = serializations;
    await db.write(writer.materialize(state));
    return serializations - before;
  };

  Assert.equal(await save(), 1, "The first batch serializes the history");
  Assert.equal(await save(), 0, "The same objects aren't serialized again");
  win.tabs = win.tabs.map(tab => ({
    ...tab,
    attributes: { ...tab.attributes },
  }));
  Assert.equal(
    await save(),
    0,
    "Recollected tab states that share their history aren't serialized"
  );
  win.tabs[0].entries.push({ url: "https://b.test/" });
  SessionChangeJournal.markChanged(win.tabs[0].entries);
  Assert.equal(await save(), 1, "A marked history is serialized again");
  await writeAndCheck(db, writer, state, "The database has the edit");
  await db.close();
});

add_task(async function test_audit_finds_unmarked_edits() {
  let { db } = await openDB();
  let writer = new SessionDBWriter({}, { audit: true });
  let state = makeState();
  await writeAndCheck(db, writer, state);
  let [tab] = state.windows[0].tabs;

  tab.entries.push({ url: "https://unmarked.test/" });
  await writeAndCheck(db, writer, state, "The audit writes the missed edit");
  Assert.deepEqual(writer.misses, [{ kind: "tab", group: "history" }]);

  tab.entries.push({ url: "https://marked.test/" });
  SessionChangeJournal.markChanged(tab.entries);
  await writeAndCheck(db, writer, state);
  Assert.deepEqual(writer.misses, [], "A marked edit is no miss");

  tab.index = 2;
  delete tab.image;
  await writeAndCheck(db, writer, state);
  Assert.deepEqual(writer.misses, [], "Edits of the tab state need no mark");
  await db.close();
});

add_task(async function test_identities_match_recollected_tabs() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  let [win] = state.windows;
  let identities = win.tabs.map(() => ({}));
  let recollect = tabs =>
    tabs.map((tab, i) => {
      let copy = { ...tab };
      SessionChangeJournal.setIdentity(copy, identities[i]);
      return copy;
    });
  win.tabs = recollect(win.tabs);
  await writeAndCheck(db, writer, state);

  identities.unshift({});
  win.tabs = recollect([makeTab("https://new.test/"), ...win.tabs]);
  let ops = await writeAndCheck(db, writer, state, "Insertion");
  Assert.deepEqual(
    ops.map(([name]) => name),
    ["node", "section", "section", "order"],
    "Only the new tab and the order are written"
  );
  await db.close();
});

add_task(async function test_shared_objects_keep_their_nodes() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  let tab = makeTab("https://shared.test/");
  state._closedWindows.push({ tabs: [tab], _closedTabs: [], closedGroups: [] });
  state.savedGroups[0].tabs.push({ state: tab, title: "shared" });
  await writeAndCheck(db, writer, state);
  Assert.deepEqual(
    await writeAndCheck(db, writer, state),
    [],
    "An object in two places keeps both of its nodes"
  );
  await db.close();
});

add_task(async function test_previous_session_is_written_incrementally() {
  let { db } = await openDB();
  let writer = new SessionDBWriter();
  let state = makeState();
  // A deferred restore shares the saved groups with the previous session.
  state.lastSessionState = { ...makeState(), savedGroups: state.savedGroups };
  await writeAndCheck(db, writer, state);

  let [win] = state.windows;
  win.tabs[0] = { ...win.tabs[0], scroll: { scroll: "0,1" } };
  let ops = await writeAndCheck(db, writer, state, "Current session change");
  Assert.deepEqual(
    ops.map(([name, , section]) => [name, section]),
    [["section", "scroll"]],
    "Nothing of the previous session is written again"
  );
  await db.close();
});

/**
 * A small deterministic generator, so that failures reproduce.
 */
function makeRandom(seed) {
  return () => {
    seed = (seed * 1103515245 + 12345) % 2147483648;
    return seed / 2147483648;
  };
}

async function randomChanges({ audit }) {
  let { db } = await openDB();
  let writer = new SessionDBWriter({}, { audit });
  let random = makeRandom(42);
  let pick = array => array[Math.floor(random() * array.length)];
  let state = makeState();
  let counter = 0;

  let mutations = [
    () => {
      let win = pick(state.windows) ?? state.windows[0];
      win?.tabs.splice(
        Math.floor(random() * (win.tabs.length + 1)),
        0,
        makeTab(`https://t${counter++}.test/`)
      );
    },
    () => {
      let win = pick(state.windows);
      if (win?.tabs.length > 1) {
        let [tab] = win.tabs.splice(Math.floor(random() * win.tabs.length), 1);
        win._closedTabs.unshift({
          state: tab,
          title: "t",
          closedId: counter++,
        });
      }
    },
    () => {
      let win = pick(state.windows);
      if (win?.tabs.length > 1) {
        let [tab] = win.tabs.splice(0, 1);
        win.tabs.push(tab);
      }
    },
    () => {
      let win = pick(state.windows);
      if (win?.tabs.length) {
        let i = Math.floor(random() * win.tabs.length);
        win.tabs[i] = { ...win.tabs[i], scroll: { scroll: `0,${counter++}` } };
      }
    },
    () => {
      let win = pick(state.windows);
      if (win?.tabs.length) {
        let tab = pick(win.tabs);
        tab.entries = [...tab.entries, { url: `https://n${counter++}.test/` }];
        tab.index = tab.entries.length;
      }
    },
    () => {
      let tab = pick(pick(state.windows)?.tabs ?? []);
      if (tab) {
        tab.attributes.custom = String(counter++);
        SessionChangeJournal.markChanged(tab.attributes);
      }
    },
    () => {
      let closedTab = pick(pick(state.windows)?._closedTabs ?? []);
      if (closedTab) {
        closedTab.state.scroll = { scroll: `0,${counter++}` };
      }
    },
    () => {
      let win = pick(state.windows);
      if (win) {
        win.tabs = win.tabs.map(tab => structuredClone(tab));
      }
    },
    () => {
      if (state.windows.length > 1) {
        let [win] = state.windows.splice(0, 1);
        state._closedWindows.unshift(win);
      }
    },
    () => {
      if (state._closedWindows.length) {
        state.windows.push(state._closedWindows.shift());
      }
    },
    () => {
      state.windows.push({
        tabs: [makeTab(`https://w${counter++}.test/`)],
        _closedTabs: [],
        closedGroups: [],
        selected: 1,
      });
    },
    () => {
      let win = pick(state.windows);
      if (win?._closedTabs.length) {
        win._closedTabs.pop();
      }
    },
    () => {
      state.cookies.push({ host: `c${counter++}.test`, value: "v" });
      if (state.cookies.length > 3) {
        state.cookies.splice(1, 1);
      }
    },
    () => {
      state.global = random() < 0.5 ? undefined : { n: counter++ };
    },
    () => {
      let group = pick(state.savedGroups);
      group?.tabs.push({ state: makeTab(`https://g${counter++}.test/`) });
    },
    () => {
      state.session = { ...state.session, lastUpdate: counter++ };
    },
    () => {
      state.lastSessionState = state.lastSessionState
        ? undefined
        : {
            windows: structuredClone(state.windows),
            savedGroups: state.savedGroups,
          };
    },
  ];

  await writeAndCheck(db, writer, state);
  for (let step = 0; step < 200; step++) {
    pick(mutations)();
    await writeAndCheck(db, writer, state, `Step ${step}`);
    if (audit) {
      Assert.deepEqual(writer.misses, [], `Step ${step} has no misses`);
    }
  }
  await db.close();
}

add_task(async function test_random_changes() {
  await randomChanges({ audit: false });
});

add_task(async function test_random_changes_audited() {
  await randomChanges({ audit: true });
});
