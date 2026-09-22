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
async function writeSession(state, { comparable = true } = {}) {
  let { backend } = await startBackend("", "empty");
  backend.annotate(state);
  await backend.write(state, { isFinalWrite: true, comparable });
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

add_task(async function test_metrics() {
  Services.fog.testResetFOG();
  await writeSession(makeState("a"));
  Assert.equal(Glean.sessionRestore.dbRead.testGetValue().count, 1);
  let { count, sum } = Glean.sessionRestore.dbBatchSize.testGetValue();
  Assert.equal(count, 1, "The batch was measured");
  Assert.greater(sum, 0);
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
