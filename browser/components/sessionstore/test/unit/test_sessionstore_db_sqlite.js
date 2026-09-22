/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

do_get_profile();
Services.fog.initializeFOG();
Services.prefs.setStringPref("browser.sessionstore.backend", "sqlite");

const { SessionFile } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionFile.sys.mjs"
);
const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
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

async function recoveryURL() {
  let state = await IOUtils.readJSON(Paths.recovery, { decompress: true });
  return state.windows[0].tabs[0].entries[0].url;
}

async function databaseURL() {
  let db = await SessionStoreDB.open(Paths.database);
  let { state } = await db.read();
  await db.close();
  return state.windows[0].tabs[0].entries[0].url;
}

add_task(async function test_json_files_are_exported_less_often() {
  await SessionFile.read();
  Assert.equal(
    Glean.sessionRestore.dbSourceSelected.json.testGetValue(),
    1,
    "Startup restores from JSON when there is no database"
  );
  await SessionFile.dbCrossCheck;

  await SessionFile.write(makeState("https://first.test/"));
  Assert.equal(await recoveryURL(), "https://first.test/");

  await SessionFile.write(makeState("https://second.test/"));
  Assert.equal(
    Glean.sessionRestore.dbExport.skipped.testGetValue(),
    1,
    "A save soon after the previous JSON file writes none"
  );
  Assert.equal(await recoveryURL(), "https://first.test/");
  Assert.equal(await databaseURL(), "https://second.test/");

  Services.prefs.setIntPref("browser.sessionstore.db_export_interval", 0);
  await SessionFile.write(makeState("https://third.test/"));
  Assert.equal(await recoveryURL(), "https://third.test/");
  Services.prefs.clearUserPref("browser.sessionstore.db_export_interval");

  await SessionFile.write(makeState("https://purged.test/"), {
    immediate: true,
  });
  Assert.equal(
    await recoveryURL(),
    "https://purged.test/",
    "A save requested right away, like after purging data, writes JSON"
  );

  await SessionFile.wipe();
  await SessionFile.write(makeState("https://wiped.test/"));
  Assert.equal(
    await recoveryURL(),
    "https://wiped.test/",
    "The first save after a wipe writes JSON"
  );
});
