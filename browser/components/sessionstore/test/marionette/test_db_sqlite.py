# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

# add this directory to the path
sys.path.append(os.path.dirname(__file__))

from session_store_test_case import SessionStoreTestCase, inline


class TestSqliteMode(SessionStoreTestCase):
    """
    In the "sqlite" backend mode, most saves write only the session database,
    and startup restores from it when it is newer than the JSON files. This
    test checks that a kill after such a save restores the newest session.
    """

    def setUp(self):
        super().setUp(startup_page=3, include_private=False)
        self.marionette.enforce_gecko_prefs({
            "browser.sessionstore.backend": "sqlite",
            "browser.sessionstore.resume_from_crash": True,
        })
        self.marionette.set_context("chrome")
        self.marionette.timeout.script = 90

    def save(self):
        """Saves the session, and returns how many saves wrote no JSON file."""
        return self.marionette.execute_async_script(
            """
            let [resolve] = arguments;
            let { SessionFile } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/SessionFile.sys.mjs"
            );
            let { SessionSaver } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/SessionSaver.sys.mjs"
            );
            let { TabStateFlusher } = ChromeUtils.importESModule(
              "moz-src:///browser/components/sessionstore/TabStateFlusher.sys.mjs"
            );
            (async () => {
              for (let win of Services.wm.getEnumerator("navigator:browser")) {
                await TabStateFlusher.flushWindow(win);
              }
              await SessionFile.dbCrossCheck;
              await SessionSaver.run();
              return Glean.sessionRestore.dbExport.skipped.testGetValue() ?? 0;
            })().then(resolve);
            """
        )

    def test_kill_after_database_save(self):
        win = self.marionette.current_chrome_window_handle
        self.open_tabs(win, (inline("<div>first</div>"),))
        self.save()
        self.marionette.switch_to_window(self.open_tab())
        with self.marionette.using_context("content"):
            self.marionette.navigate(inline("<div>second</div>"))
        self.marionette.switch_to_window(win)
        windows = self.convert_open_windows_to_set()
        self.assertGreater(self.save(), 0, msg="The save wrote no JSON file.")

        self.marionette.restart(in_app=False)
        self.wait_for_windows(windows, "The session restored from the database.")
