/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
);
const { Sqlite } = ChromeUtils.importESModule(
  "resource://gre/modules/Sqlite.sys.mjs"
);

do_get_profile();

let gCount = 0;

function newPath() {
  return PathUtils.join(
    PathUtils.profileDir,
    `sessionstore-${gCount++}.sqlite`
  );
}

const STATE_OPS = [
  ["root", "state", '{"version":["sessionrestore",1],"session":{"a":1}}'],
  ["root", "global", '{"key":"value"}'],
  ["node", 1, 0, "windows", '{"selected":1}'],
  ["order", 0, "windows", "[1]"],
  ["node", 2, 1, "tabs", '{"pinned":true}'],
  [
    "section",
    2,
    "history",
    '{"entries":[{"url":"https://a.test/"}],"index":1}',
  ],
  ["section", 2, "scroll", '{"scroll":{"scroll":"0,10"}}'],
  ["nullnode", 3, 1, "tabs"],
  ["node", 4, 1, "tabs", "{}"],
  ["order", 1, "tabs", "[2,3,4]"],
  ["order", 1, "_closedTabs", "[]"],
  ["node", 5, 0, "_closedWindows", '{"closedId":7}'],
  ["order", 0, "_closedWindows", "[5]"],
  ["node", 6, 5, "_closedTabs", '{"title":"closed"}'],
  ["order", 5, "_closedTabs", "[6]"],
  ["node", 7, 6, "state", '{"entries":[]}'],
  ["order", 6, "state", "7"],
  ["meta", "seq", "1"],
].flat();

const STATE = {
  version: ["sessionrestore", 1],
  session: { a: 1 },
  global: { key: "value" },
  windows: [
    {
      selected: 1,
      tabs: [
        {
          pinned: true,
          entries: [{ url: "https://a.test/" }],
          index: 1,
          scroll: { scroll: "0,10" },
        },
        null,
        {},
      ],
      _closedTabs: [],
    },
  ],
  _closedWindows: [
    {
      closedId: 7,
      _closedTabs: [{ title: "closed", state: { entries: [] } }],
    },
  ],
};

async function assertRejects(promise, result, message) {
  await Assert.rejects(promise, ex => ex.result == result, message);
}

add_task(async function test_empty() {
  let db = await SessionStoreDB.open(newPath());
  Assert.deepEqual(await db.read(), { meta: {}, state: null, dropped: 0 });
  await db.close();
});

add_task(async function test_round_trip_and_reopen() {
  let path = newPath();
  let db = await SessionStoreDB.open(path);
  await db.write(STATE_OPS);
  let result = await db.read();
  Assert.deepEqual(result.state, STATE, "The rows assemble into the state");
  Assert.deepEqual(result.meta, { seq: "1" });
  Assert.deepEqual(await db.readMeta(), { seq: "1" });
  Assert.deepEqual(JSON.parse(await db.readText()), result);
  await db.close();

  db = await SessionStoreDB.open(path);
  Assert.deepEqual((await db.read()).state, STATE, "The state persisted");
  await db.close();
});

add_task(async function test_incremental_changes() {
  let db = await SessionStoreDB.open(newPath());
  await db.write(STATE_OPS);
  await db.write(
    [
      ["delsection", 2, "scroll"],
      ["node", 8, 1, "tabs", '{"hidden":true}'],
      ["order", 1, "tabs", "[8,2]"],
      ["delnode", 3],
      ["delnode", 4],
      ["delnode", 7],
      ["delnode", 6],
      ["delnode", 5],
      ["order", 0, "_closedWindows", "[]"],
    ].flat()
  );
  let expected = structuredClone(STATE);
  delete expected.windows[0].tabs[0].scroll;
  expected.windows[0].tabs = [{ hidden: true }, expected.windows[0].tabs[0]];
  expected._closedWindows = [];
  Assert.deepEqual((await db.read()).state, expected);
  await db.close();
});

add_task(async function test_guard_rolls_back_the_batch() {
  let db = await SessionStoreDB.open(newPath());
  await db.write(STATE_OPS);
  await assertRejects(
    db.write(
      [
        ["node", 9, 0, "windows", "{}"],
        ["order", 0, "windows", "[1,9]"],
        ["guard", "seq", "2"],
      ].flat()
    ),
    Cr.NS_ERROR_ABORT,
    "A guard mismatch aborts the batch"
  );
  Assert.deepEqual(
    (await db.read()).state,
    STATE,
    "Nothing from the aborted batch was applied"
  );

  await db.write(
    [
      ["guard", "seq", "1"],
      ["meta", "seq", "2"],
    ].flat()
  );
  await db.write(["guard", "unset", ""]);
  Assert.equal((await db.read()).meta.seq, "2", "Matching guards pass");
  await db.close();
});

add_task(async function test_malformed_batches() {
  let db = await SessionStoreDB.open(newPath());
  for (let ops of [
    ["bogus"],
    ["node", "x", 0, "windows", "{}"],
    ["meta", "k"],
  ]) {
    await assertRejects(
      db.write(ops),
      Cr.NS_ERROR_INVALID_ARG,
      `${JSON.stringify(ops)} is rejected`
    );
  }
  await db.close();
});

add_task(async function test_structural_corruption() {
  for (let ops of [
    [
      ["root", "state", "{}"],
      ["node", 1, 0, "windows", "{}"],
    ],
    [
      ["root", "state", "{}"],
      ["order", 0, "windows", "[1]"],
    ],
    [
      ["root", "state", "{}"],
      ["node", 1, 0, "windows", "{}"],
      ["order", 0, "windows", "[1,1]"],
    ],
    [
      ["root", "state", "{}"],
      ["node", 1, 2, "windows", "{}"],
      ["order", 0, "windows", "[1]"],
    ],
  ]) {
    let db = await SessionStoreDB.open(newPath());
    await db.write(ops.flat());
    await assertRejects(
      db.read(),
      Cr.NS_ERROR_FILE_CORRUPTED,
      `${JSON.stringify(ops)} doesn't assemble`
    );
    await db.close();
  }
});

add_task(async function test_invalid_fragments() {
  let db = await SessionStoreDB.open(newPath());
  await db.write(STATE_OPS);
  await db.write(["node", 4, 1, "tabs", '{"broken":}']);
  await Assert.rejects(
    db.read(),
    ex => ex.name == "SyntaxError",
    "Without validation, the caller's parse catches the invalid fragment"
  );

  let { state, dropped } = await db.read({ validate: true });
  Assert.equal(dropped, 1, "Validation leaves out the invalid node");
  let expected = structuredClone(STATE);
  expected.windows[0].tabs.pop();
  Assert.deepEqual(state, expected, "The rest of the state is intact");
  await db.close();
});

add_task(async function test_export() {
  let db = await SessionStoreDB.open(newPath());
  let path = PathUtils.join(PathUtils.profileDir, "exported.jsonlz4");
  let tmpPath = path + ".tmp";
  let backupFile = path + ".bak";
  await assertRejects(
    db.exportJSON(path, { tmpPath }),
    Cr.NS_ERROR_NOT_AVAILABLE,
    "An empty database has nothing to export"
  );

  await db.write(STATE_OPS);
  let size = await db.exportJSON(path, { tmpPath });
  Assert.deepEqual(
    await IOUtils.readJSON(path, { decompress: true }),
    STATE,
    "The exported file holds the state"
  );
  Assert.equal(size, (await IOUtils.stat(path)).size);
  Assert.ok(!(await IOUtils.exists(tmpPath)), "The temporary file was moved");

  await db.write(["node", 4, 1, "tabs", '{"new":true}']);
  await db.exportJSON(path, { tmpPath, backupFile });
  Assert.deepEqual(
    await IOUtils.readJSON(backupFile, { decompress: true }),
    STATE,
    "The previous file became the backup"
  );
  Assert.deepEqual(
    (await IOUtils.readJSON(path, { decompress: true })).windows[0].tabs[2],
    { new: true }
  );

  await db.write(["node", 4, 1, "tabs", '{"broken":}']);
  await assertRejects(
    db.exportJSON(path, { tmpPath }),
    Cr.NS_ERROR_FILE_CORRUPTED,
    "A state that doesn't parse isn't exported"
  );
  Assert.deepEqual(
    (await IOUtils.readJSON(path, { decompress: true })).windows[0].tabs[2],
    { new: true },
    "The previous file is untouched"
  );
  await db.close();
});

add_task(async function test_checkpoint() {
  let path = newPath();
  let db = await SessionStoreDB.open(path);
  await db.write(STATE_OPS);
  Assert.greater((await IOUtils.stat(path + "-wal")).size, 0);
  await db.write(["delnode", 4, "checkpoint"]);
  Assert.equal(
    (await IOUtils.stat(path + "-wal")).size,
    0,
    "The write-ahead log keeps no copy of the deleted row"
  );
  await db.close();
});

add_task(async function test_newer_schema() {
  let path = newPath();
  let db = await SessionStoreDB.open(path);
  await db.close();

  let connection = await Sqlite.openConnection({ path });
  await connection.execute("PRAGMA user_version = 99");
  await connection.close();

  await assertRejects(
    SessionStoreDB.open(path),
    Cr.NS_ERROR_NOT_AVAILABLE,
    "A newer schema can't be opened"
  );
});
