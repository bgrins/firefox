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
    after a clean restart and after a kill following a save.
    """

    def setUp(self):
        super().setUp(startup_page=3, include_private=True)
        self.marionette.enforce_gecko_prefs({"browser.sessionstore.backend": "shadow"})
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

    def test_kill_after_save(self):
        self.change_and_save()

        self.marionette.restart(in_app=False)
        self.marionette.set_context("chrome")
        self.assertEqual(
            self.cross_check(),
            {"result": "match"},
            msg="The database matches the JSON file after a kill.",
        )
