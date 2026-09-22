/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

do_get_profile();
Services.fog.initializeFOG();
Services.prefs.setStringPref("browser.sessionstore.backend", "export");

const { SessionFile } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionFile.sys.mjs"
);
const { updateAppInfo } = ChromeUtils.importESModule(
  "resource://testing-common/AppInfo.sys.mjs"
);
updateAppInfo({
  name: "SessionRestoreTest",
  ID: "{230de50e-4cd1-11dc-8314-0800200c9a66}",
  version: "1",
  platformVersion: "",
});

const Paths = SessionFile.Paths;

function makeState(url) {
  return {
    version: ["sessionrestore", 1],
    windows: [{ tabs: [{ entries: [{ url }], index: 1 }], _closedTabs: [] }],
    _closedWindows: [],
    session: { lastUpdate: 1 },
  };
}

function readFile(path) {
  return IOUtils.readJSON(path, { decompress: true });
}

add_task(async function test_export_mode() {
  await SessionFile.read();

  let first = makeState("https://first.test/");
  await SessionFile.write(first);
  Assert.equal(
    Glean.sessionRestore.dbExport.not_written.testGetValue(),
    1,
    "A write before the database is ready serializes the state"
  );
  Assert.deepEqual(await readFile(Paths.recovery), first);

  await SessionFile.dbCrossCheck;
  let second = makeState("https://second.test/");
  await SessionFile.write(second);
  Assert.equal(Glean.sessionRestore.dbExport.exported.testGetValue(), 1);
  Assert.deepEqual(
    await readFile(Paths.recovery),
    JSON.parse(JSON.stringify(second)),
    "The recovery file is exported from the database"
  );
  Assert.deepEqual(
    await readFile(Paths.recoveryBackup),
    first,
    "The previous recovery file is the backup"
  );
  Assert.ok(!(await IOUtils.exists(Paths.recovery + ".tmp")));
});

add_task(async function test_final_write_is_serialized() {
  let { RunState } = ChromeUtils.importESModule(
    "moz-src:///browser/components/sessionstore/RunState.sys.mjs"
  );
  RunState.setRunning();
  RunState.setQuitting();
  RunState.setClosing();
  let exported = Glean.sessionRestore.dbExport.exported.testGetValue();

  let final = makeState("https://final.test/");
  await SessionFile.write(final);
  Assert.equal(
    Glean.sessionRestore.dbExport.exported.testGetValue(),
    exported,
    "The final write isn't exported"
  );
  Assert.deepEqual(
    await readFile(Paths.clean),
    JSON.parse(JSON.stringify(final))
  );
});
