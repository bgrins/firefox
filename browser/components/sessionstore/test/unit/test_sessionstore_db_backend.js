/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { SessionDBBackend } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionDBBackend.sys.mjs"
);

do_get_profile();
Services.fog.initializeFOG();

const PATH = PathUtils.join(PathUtils.profileDir, "sessionstore.sqlite");

function makeState(title) {
  return {
    version: ["sessionrestore", 1],
    windows: [
      {
        tabs: [{ entries: [{ url: "https://a.test/", title }], index: 1 }],
        _closedTabs: [],
      },
    ],
    _closedWindows: [],
    session: { lastUpdate: 1 },
  };
}

/**
 * Starts a backend that compares the database with `source`, and returns it
 * with the cross-check result.
 */
async function startBackend(source, origin = "clean") {
  let backend = new SessionDBBackend(PATH);
  backend.start({ origin, source });
  return { backend, result: await backend.crossCheck };
}

/**
 * Writes `state` through a new backend, as a session would, and returns the
 * JSON the JSON backend would have written for the same save.
 */
async function writeSession(
  state,
  { comparable = true, isFinalWrite = true } = {}
) {
  let { backend } = await startBackend("", "empty");
  backend.annotate(state);
  await backend.write(state, { isFinalWrite, comparable });
  await backend.close();
  return JSON.stringify(state);
}

add_task(async function test_missing_database() {
  let { backend, result } = await startBackend(
    JSON.stringify(makeState("a")),
    "clean"
  );
  Assert.deepEqual(result, { result: "db_missing" });
  await backend.close();
  Assert.equal(Glean.sessionRestore.dbCrossCheck.db_missing.testGetValue(), 1);
});

add_task(async function test_match_and_mismatch() {
  let source = await writeSession(makeState("a"));

  let { backend, result } = await startBackend(source);
  Assert.deepEqual(result, { result: "match" }, "Identical states match");
  await backend.close();
  Assert.equal(Glean.sessionRestore.dbCrossCheck.match.testGetValue(), 1);

  let changed = JSON.parse(source);
  changed.windows[0].tabs[0].entries[0].title = "b";
  delete changed.windows[0]._closedTabs;
  ({ backend, result } = await startBackend(JSON.stringify(changed)));
  Assert.deepEqual(result, {
    result: "mismatch",
    paths: [".windows[0].tabs[0].entries[0].title", ".windows[0]._closedTabs"],
  });
  await backend.close();
});

add_task(async function test_generations_that_cannot_be_compared() {
  let source = await writeSession(makeState("a"));
  let json = JSON.parse(source);

  let older = structuredClone(json);
  older.session.writeSeq--;
  let { backend, result } = await startBackend(JSON.stringify(older));
  Assert.equal(result.result, "skew_db_newer", "The database is a save ahead");
  await backend.close();

  let otherLineage = structuredClone(json);
  otherLineage.session.lineage = "someone-else";
  ({ backend, result } = await startBackend(JSON.stringify(otherLineage)));
  Assert.equal(result.result, "lineage_mismatch");
  await backend.close();

  let unstamped = structuredClone(json);
  delete unstamped.session.writeSeq;
  ({ backend, result } = await startBackend(JSON.stringify(unstamped)));
  Assert.equal(result.result, "json_seq_missing");
  await backend.close();

  ({ backend, result } = await startBackend("", "empty"));
  Assert.equal(result.result, "json_missing");
  await backend.close();

  source = await writeSession(makeState("b"), { comparable: false });
  ({ backend, result } = await startBackend(source));
  Assert.equal(result.result, "not_comparable");
  await backend.close();
});

add_task(async function test_annotate_matches_the_written_generation() {
  let state = makeState("a");
  let source = await writeSession(state);
  let { backend } = await startBackend(source);
  let next = makeState("c");
  backend.annotate(next);
  Assert.equal(next.session.writeSeq, state.session.writeSeq + 1);
  Assert.equal(next.session.lineage, state.session.lineage);
  await backend.close();
});

add_task(async function test_newer_state() {
  // The session didn't shut down cleanly.
  let json = JSON.parse(
    await writeSession(makeState("a"), { isFinalWrite: false })
  );
  let { backend } = await startBackend(JSON.stringify(json));
  Assert.equal(
    await backend.newerState(json),
    null,
    "The database isn't newer than JSON of the same generation"
  );
  let older = structuredClone(json);
  older.session.writeSeq--;
  Assert.deepEqual(
    await backend.newerState(older),
    json,
    "The database is newer than an older JSON file of its lineage"
  );
  older.session.lineage = "elsewhere";
  Assert.equal(
    await backend.newerState(older),
    null,
    "A JSON file of another lineage wins"
  );
  Assert.equal(
    await backend.newerState(null),
    null,
    "Without JSON files, which were deleted, the database isn't restored"
  );
  await backend.close();

  json = JSON.parse(await writeSession(makeState("b")));
  ({ backend } = await startBackend(JSON.stringify(json)));
  older = structuredClone(json);
  older.session.writeSeq--;
  Assert.equal(
    await backend.newerState(older),
    null,
    "After a clean shutdown, an older JSON file copied into place wins"
  );
  await backend.close();
});

add_task(async function test_metrics() {
  Services.fog.testResetFOG();
  await writeSession(makeState("a"));
  Assert.equal(Glean.sessionRestore.dbRead.testGetValue().count, 1);
  let { count, sum } = Glean.sessionRestore.dbBatchSize.testGetValue();
  Assert.equal(count, 1, "The batch was measured");
  Assert.greater(sum, 0);
});

add_task(async function test_a_throwing_state_writes_nothing() {
  let { backend } = await startBackend("", "empty");
  let state = makeState("a");
  Object.defineProperty(state.windows[0], "tabs", {
    enumerable: true,
    get() {
      throw new Error("Unreadable");
    },
  });
  Assert.equal(
    await backend.write(state, { isFinalWrite: false, comparable: true }),
    false
  );
  await backend.close();
});

add_task(async function test_unusable_databases_are_replaced() {
  let { SessionStoreDB } = ChromeUtils.importESModule(
    "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
  );
  let expected = JSON.parse(JSON.stringify(makeState("a")));
  let check = async message => {
    let { backend, result } = await startBackend("", "empty");
    info(`The cross-check found ${result.result}`);
    Assert.ok(
      await backend.write(makeState("a"), {
        isFinalWrite: true,
        comparable: true,
      })
    );
    await backend.close();
    let db = await SessionStoreDB.open(PATH);
    Assert.deepEqual(
      (await db.read()).state.windows,
      expected.windows,
      message
    );
    await db.close();
  };

  await IOUtils.writeUTF8(PATH, "not a database");
  await check("A file that isn't a database is replaced");
  Assert.equal(
    await IOUtils.readUTF8(PATH + ".corrupt"),
    "not a database",
    "It was moved aside"
  );

  let db = await SessionStoreDB.open(PATH);
  await db.write(["node", 999, 0, "windows", "{}"]);
  await db.close();
  await check("Rows that don't form a state are rewritten");
});

add_task(async function test_writes_around_a_wipe() {
  let { SessionStoreDB } = ChromeUtils.importESModule(
    "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
  );
  let { backend } = await startBackend("", "empty");
  let before = makeState("before");
  let after = makeState("after");

  // Neither write is awaited before the next call, as when purging history
  // saves right after starting the wipe.
  await Promise.all([
    backend.write(before, { isFinalWrite: false, comparable: true }),
    backend.wipe(),
    backend.write(after, { isFinalWrite: false, comparable: true }),
  ]);
  await backend.close();

  let db = await SessionStoreDB.open(PATH);
  Assert.deepEqual(
    (await db.read()).state,
    JSON.parse(JSON.stringify(after)),
    "The write made during the wipe reached the recreated database, and the one made before it didn't"
  );
  await db.close();
});

add_task(async function test_wipe() {
  await writeSession(makeState("a"));
  let { backend } = await startBackend("");
  await backend.wipe({ reopen: false });
  for (let suffix of ["", "-wal", "-shm"]) {
    Assert.ok(!(await IOUtils.exists(PATH + suffix)), `${suffix || "db"} gone`);
  }
  await backend.close();
});
