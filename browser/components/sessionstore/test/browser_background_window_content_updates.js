/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const URL = HTTPSROOT + "browser_formdata_sample.html";

/**
 * Checks that a content update in a background window marks that window for
 * collection, so that the next save includes it.
 */
add_task(async function test_content_update_in_background_window() {
  // Content sends its updates after this interval.
  await SpecialPowers.pushPrefEnv({
    set: [["browser.sessionstore.interval", 100]],
  });
  let win = await BrowserTestUtils.openNewBrowserWindow();
  let browser = win.gBrowser.selectedBrowser;
  BrowserTestUtils.startLoadingURIString(browser, URL);
  await promiseBrowserLoaded(browser, true, URL);
  await TabStateFlusher.flush(browser);
  await SimpleTest.promiseFocus(window);
  Assert.equal(
    BrowserWindowTracker.getTopWindow(),
    window,
    "The new window is in the background"
  );
  // Collect every window, so that none is left to collect.
  SessionStore.getCurrentState(true);

  await setPropertyOfFormField(browser, "#txt", "value", "typed");
  // Wait for the update without flushing, since a flush marks the window.
  await TestUtils.waitForCondition(
    () =>
      JSON.parse(ss.getTabState(win.gBrowser.selectedTab)).formdata?.id.txt ==
      "typed",
    "The form data update arrived"
  );
  let { windows } = SessionStore.getCurrentState();
  let winState = windows.find(({ tabs }) =>
    tabs.some(tab => tab.entries.some(entry => entry.url == URL))
  );
  Assert.equal(
    winState.tabs[0].formdata?.id.txt,
    "typed",
    "The background window was collected with the new form data"
  );

  await BrowserTestUtils.closeWindow(win);
});
