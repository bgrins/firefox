# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

# add this directory to the path
sys.path.append(os.path.dirname(__file__))

from session_store_test_case import SessionStoreTestCase, inline


class TestShadowDatabaseCrossCheck(SessionStoreTestCase):
    """
    In the "shadow" backend mode, session state is written to the session
    database next to the JSON session file. After each startup, the two are
    compared. These tests check that the comparison finds them identical
    after a clean restart and after a kill following a save, and that saves
    after startup seeded the writer miss no edit.
    """

    def setUp(self):
        super().setUp(startup_page=3, include_private=True)
        self.marionette.enforce_gecko_prefs({
            "browser.sessionstore.backend": "shadow",
            "browser.sessionstore.db_audit": True,
        })
        self.marionette.set_context("chrome")
        self.marionette.timeout.script = 90

    def cross_check(self):
        return self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            let { SessionFile } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/SessionFile.sys.mjs"
            );
            SessionFile.dbCrossCheck.then(resolve);
            """
        )

    def restart(self):
        self.marionette.restart(in_app=True)
        self.marionette.set_context("chrome")
        # Reading a metric before FOG is initialized, in an idle task at
        # startup, blocks the main thread for good.
        self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            let { BrowserInitState } = ChromeUtils.importESModule(
              "resource:///modules/BrowserGlue.sys.mjs"
            );
            BrowserInitState.startupIdleTaskPromise.then(resolve);
            """
        )

    def metric(self, expression):
        return self.marionette.execute_script(
            f"return Glean.sessionRestore.{expression}.testGetValue();"
        )

    def journal_misses(self):
        return {
            group: count
            for group in ("core", "history", "formdata", "scroll", "storage", "image")
            if (count := self.metric(f"dbJournalMiss.{group}"))
        }

    def add_background_tabs(self):
        win = self.marionette.current_chrome_window_handle
        for title in ("first", "second"):
            self.marionette.switch_to_window(self.open_tab())
            with self.marionette.using_context("content"):
                self.marionette.navigate(inline(f"<title>{title}</title>"))
        self.marionette.switch_to_window(win)
        self.marionette.execute_script("gBrowser.selectedTab = gBrowser.tabs[0];")

    def restore_pending_tabs(self):
        self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            (async () => {
              for (let tab of gBrowser.tabs) {
                if (tab.hasAttribute("pending")) {
                  let restored = new Promise(done =>
                    tab.addEventListener("SSTabRestored", done, { once: true })
                  );
                  gBrowser.selectedTab = tab;
                  await restored;
                }
              }
            })().then(resolve);
            """
        )

    def save(self):
        self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            let { SessionSaver } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/SessionSaver.sys.mjs"
            );
            let { TabStateFlusher } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/TabStateFlusher.sys.mjs"
            );
            TabStateFlusher.flushWindow(window)
              .then(() => SessionSaver.run())
              .then(resolve);
            """
        )

    def change_and_save(self):
        self.open_tabs(
            self.marionette.current_chrome_window_handle,
            (inline("<title>navigated</title>"), inline("<title>added</title>")),
        )
        self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            let { SessionSaver } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/SessionSaver.sys.mjs"
            );
            let { TabStateFlusher } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/TabStateFlusher.sys.mjs"
            );
            (async () => {
              gBrowser.pinTab(gBrowser.tabs.at(-1));
              gBrowser.removeTab(gBrowser.tabs.at(-1));
              await TabStateFlusher.flushWindow(window);
              // The first save of a session moves files before serializing,
              // so its generation isn't comparable. Save twice.
              await SessionSaver.run();
              await SessionSaver.run();
            })().then(resolve);
            """
        )

    def test_clean_restart(self):
        self.assertEqual(
            self.cross_check()["result"],
            "db_missing",
            msg="The first startup in shadow mode has no database yet.",
        )
        self.change_and_save()

        self.marionette.restart(in_app=True)
        self.marionette.set_context("chrome")
        self.assertEqual(
            self.cross_check(),
            {"result": "match"},
            msg="The database matches the JSON file after a clean restart.",
        )

    def check_seeded_restart(self, audit):
        self.change_and_save()
        # They stay pending after the restart.
        self.add_background_tabs()

        self.restart()
        self.assertEqual(self.cross_check(), {"result": "match"})
        self.assertEqual(
            self.metric("dbSeed.seeded"),
            1,
            msg="Startup seeded the writer with the restored session.",
        )
        # Tabs that haven't loaded still have the restored objects.
        self.save()
        if audit:
            self.assertEqual(
                self.journal_misses(),
                {},
                msg="The save after seeding missed no edit of the restored session.",
            )

        self.restart()
        self.assertEqual(
            self.cross_check(),
            {"result": "match"},
            msg="The database matches the JSON file saved with pending tabs.",
        )
        self.restore_pending_tabs()
        self.change_and_save()
        if audit:
            self.assertEqual(
                self.journal_misses(),
                {},
                msg="The saves after the tabs loaded missed no edit.",
            )
        self.assertIsNone(self.metric("dbSeed.dropped"), msg="The seed was kept.")

        self.restart()
        self.assertEqual(
            self.cross_check(),
            {"result": "match"},
            msg="The database still matches the JSON file.",
        )

    def test_seeded_restart(self):
        self.check_seeded_restart(audit=True)

    def test_seeded_restart_without_audit(self):
        # The cross-check after the second restart catches what the audit
        # would, and this covers the writer as it runs by default.
        self.marionette.enforce_gecko_prefs({
            "browser.sessionstore.backend": "shadow",
            "browser.sessionstore.db_audit": False,
        })
        self.check_seeded_restart(audit=False)

    def test_kill_after_save(self):
        self.change_and_save()

        self.marionette.restart(in_app=False)
        self.marionette.set_context("chrome")
        self.assertEqual(
            self.cross_check(),
            {"result": "match"},
            msg="The database matches the JSON file after a kill.",
        )
