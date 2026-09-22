/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

/**
 * Checks that SessionChangeJournal sees every in-place edit that real
 * collection makes. After each change, the session state goes through a
 * database writer that audits its judgments, and the database must then hold
 * the state.
 */

const { capSessionHistory } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionWriter.sys.mjs"
);
const { SessionDBWriter } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs"
);
const { SessionStoreBackupResource } = ChromeUtils.importESModule(
  "moz-src:///browser/components/backup/resources/SessionStoreBackupResource.sys.mjs"
);
const { SessionStoreDB } = ChromeUtils.importESModule(
  "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
);

const FORM_URL = HTTPSROOT + "browser_formdata_sample.html";
const SCROLL_URL = HTTPSROOT + "browser_scrollPositions_sample.html";

let gDB;
let gWriter;

add_setup(async function () {
  let path = PathUtils.join(PathUtils.tempDir, "sessionstore-journal.sqlite");
  gDB = await SessionStoreDB.open(path);
  gWriter = new SessionDBWriter({}, { audit: true });
  registerCleanupFunction(async () => {
    await gDB.close();
    for (let suffix of ["", "-wal", "-shm"]) {
      await IOUtils.remove(path + suffix, { ignoreAbsent: true });
    }
  });
});

/**
 * Writes the current session state, as a save would.
 *
 * @param {string} message
 * @param {object} [options]
 * @param {boolean} [options.full]
 *        Whether to collect every window, rather than the active and dirty
 *        ones.
 * @param {(state: object) => void} [options.transform]
 *        Edits the state before it's written, as the final write does.
 * @returns {Promise<void>} Resolves once the database was checked.
 */
function save(message, { full = false, transform } = {}) {
  let state = SessionStore.getCurrentState(full);
  transform?.(state);
  let ops = gWriter.materialize(state);
  Assert.deepEqual(gWriter.misses, [], `${message}: no change was missed`);
  let expected = JSON.parse(JSON.stringify(state));
  return (async () => {
    await gDB.write(ops);
    Assert.deepEqual(
      (await gDB.read()).state,
      expected,
      `${message}: the database holds the state`
    );
  })();
}

async function flushAndSave(message, options) {
  for (let win of Services.wm.getEnumerator("navigator:browser")) {
    await TabStateFlusher.flushWindow(win);
  }
  await save(message, options);
}

function waitForStorage(tab, key) {
  return TestUtils.waitForCondition(async () => {
    await TabStateFlusher.flush(tab.linkedBrowser);
    let { storage = {} } = JSON.parse(ss.getTabState(tab));
    return Object.values(storage).some(values => key in values);
  }, `Session storage has ${key}`);
}

async function load(browser, url) {
  BrowserTestUtils.startLoadingURIString(browser, url);
  await promiseBrowserLoaded(browser, true, url);
}

add_task(async function test_journal() {
  await flushAndSave("Initial state", { full: true });

  let tab = BrowserTestUtils.addTab(gBrowser, FORM_URL);
  let browser = tab.linkedBrowser;
  await promiseBrowserLoaded(browser);
  await flushAndSave("Opened a tab");

  await load(browser, SCROLL_URL);
  await flushAndSave("Navigated");
  await setScrollPosition(browser, 0, 500);
  await flushAndSave("Scrolled");
  let replaced = promiseOnHistoryReplaceEntry(browser);
  await SpecialPowers.spawn(browser, [], () =>
    content.history.replaceState(null, "", "#replaced")
  );
  await replaced;
  await flushAndSave("Replaced the current history entry");

  await load(browser, FORM_URL);
  await setPropertyOfFormField(browser, "#txt", "value", "typed");
  await flushAndSave("Typed into a form");

  await modifySessionStorage(browser, { first: "1" });
  await waitForStorage(tab, "first");
  await flushAndSave("Stored a value in session storage");
  await modifySessionStorage(browser, { second: "2" });
  await waitForStorage(tab, "second");
  await flushAndSave("Stored another value for the same origin");

  gBrowser.pinTab(tab);
  await flushAndSave("Pinned the tab");
  gBrowser.unpinTab(tab);
  tab.toggleMuteAudio();
  await flushAndSave("Unpinned and muted the tab");

  SessionStore.setCustomTabValue(tab, "key", "first");
  await flushAndSave("Set a custom tab value");
  SessionStore.setCustomTabValue(tab, "key", "second");
  await flushAndSave("Changed the custom tab value");
  SessionStore.deleteCustomTabValue(tab, "key");
  await flushAndSave("Deleted the custom tab value");

  let win = await BrowserTestUtils.openNewBrowserWindow();
  let otherBrowser = win.gBrowser.selectedBrowser;
  await load(otherBrowser, SCROLL_URL);
  await flushAndSave("Opened a window");
  await SimpleTest.promiseFocus(window);
  await load(otherBrowser, FORM_URL);
  await flushAndSave("Navigated in a background window");
  await flushAndSave("Capped the history", {
    transform: state => capSessionHistory(state, 0, 0),
  });

  // The form data update is still on its way when the tab closes, and edits
  // the closed tab's state once it arrives.
  await setPropertyOfFormField(browser, "#txt", "value", "in flight");
  let removed = promiseRemoveTabAndSessionState(tab);
  let saved = save("Closed the tab");
  await removed;
  await saved;
  await flushAndSave("Received the closed tab's final update");

  void new SessionStoreBackupResource().filteredSessionStoreState;
  await flushAndSave("Let the backup strip session storage");

  let restored = SessionStore.undoCloseTab(window, 0);
  await promiseTabRestored(restored);
  await flushAndSave("Restored the closed tab");

  await BrowserTestUtils.closeWindow(win);
  await flushAndSave("Closed the window");
  let reopened = SessionStore.undoCloseWindow(0);
  await BrowserTestUtils.waitForEvent(reopened, "SSWindowRestored");
  await flushAndSave("Reopened the window");
  await flushAndSave("Collected every window", { full: true });

  await BrowserTestUtils.closeWindow(reopened);
  BrowserTestUtils.removeTab(restored);
});
