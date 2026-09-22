# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

# add this directory to the path
sys.path.append(os.path.dirname(__file__))

from session_store_test_case import SessionStoreTestCase, inline


class TestDatabaseExport(SessionStoreTestCase):
    """
    In the "export" backend mode, the JSON session files are exported from the
    session database. These tests check that the session restores from them
    after a clean restart and after a kill following a save.
    """

    def setUp(self):
        super().setUp(startup_page=3, include_private=False)
        self.marionette.enforce_gecko_prefs({
            "browser.sessionstore.backend": "export",
            "browser.sessionstore.resume_from_crash": True,
        })
        self.marionette.set_context("chrome")
        self.marionette.timeout.script = 90

    def save(self):
        """Saves the session, and returns how many writes were exported."""
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
              return Glean.sessionRestore.dbExport.exported.testGetValue() ?? 0;
            })().then(resolve);
            """
        )

    def check_restart(self, in_app):
        self.open_tabs(
            self.marionette.current_chrome_window_handle,
            (inline("<div>first</div>"), inline("<div>second</div>")),
        )
        windows = self.convert_open_windows_to_set()
        self.assertGreater(self.save(), 0, msg="The save was exported.")
        self.marionette.restart(in_app=in_app)
        self.wait_for_windows(windows, "The session restored from the exported file.")

    def test_clean_restart(self):
        self.check_restart(in_app=True)

    def test_kill_after_save(self):
        self.check_restart(in_app=False)
