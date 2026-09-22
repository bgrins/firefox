/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

import {
  BackupResource,
  bytesToFuzzyKilobytes,
} from "moz-src:///browser/components/backup/resources/BackupResource.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  BrowserWindowTracker: "resource:///modules/BrowserWindowTracker.sys.mjs",
  SessionStore:
    "moz-src:///browser/components/sessionstore/SessionStore.sys.mjs",
  setTimeout: "resource://gre/modules/Timer.sys.mjs",
  TabStateFlusher:
    "moz-src:///browser/components/sessionstore/TabStateFlusher.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", function () {
  return console.createInstance({
    prefix: "SessionStoreBackupResource",
    maxLogLevel: Services.prefs.getBoolPref("browser.backup.log", false)
      ? "Debug"
      : "Warn",
  });
});

XPCOMUtils.defineLazyPreferenceGetter(
  lazy,
  "TAB_FLUSH_TIMEOUT",
  "browser.backup.tab-flush-timeout",
  5000
);

/**
 * Returns a copy of a tab state without its session storage.
 *
 * @param {object} tabState
 * @returns {object}
 */
function withoutStorage(tabState) {
  if (!tabState) {
    return tabState;
  }
  let copy = { ...tabState };
  delete copy.storage;
  return copy;
}

/**
 * Class representing Session store related files within a user profile.
 */
export class SessionStoreBackupResource extends BackupResource {
  // Allow creator to provide a "SessionStore" object, so we can use mocks in
  // testing.  Passing `null` means use the real service.
  constructor(sessionStore = null) {
    super();
    this._sessionStore = sessionStore;
  }

  static get key() {
    return "sessionstore";
  }

  static get requiresEncryption() {
    // Session store data does not require encryption, but if encryption is
    // disabled, then session cookies will be cleared from the backup before
    // writing it to the disk.
    return false;
  }

  get #sessionStore() {
    return this._sessionStore || lazy.SessionStore;
  }

  /**
   * The session state to back up. The windows, tabs and groups it filters are
   * copies, since those that SessionStore returns belong to the live session.
   *
   * @type {object}
   */
  get filteredSessionStoreState() {
    let sessionStoreState = this.#sessionStore.getCurrentState(true);
    // Preserving session cookies in a backup used on a different machine
    // may break behavior for websites. So we leave them out of the backup.
    sessionStoreState.cookies = [];

    // Remove session storage.
    if (sessionStoreState.windows) {
      // We don't want to backup private windows
      sessionStoreState.windows = sessionStoreState.windows
        .filter(w => !w?.isPrivate)
        .map(win => {
          if (!win) {
            return win;
          }
          let copy = { ...win };
          if (win.tabs) {
            copy.tabs = win.tabs.map(withoutStorage);
          }
          if (win._closedTabs) {
            copy._closedTabs = win._closedTabs.map(closedTab => ({
              ...closedTab,
              state: withoutStorage(closedTab.state),
            }));
          }
          return copy;
        });
    }
    if (sessionStoreState.savedGroups) {
      sessionStoreState.savedGroups = sessionStoreState.savedGroups.map(
        group =>
          group.tabs
            ? {
                ...group,
                tabs: group.tabs.map(tab => ({
                  ...tab,
                  state: withoutStorage(tab.state),
                })),
              }
            : group
      );
    }

    return sessionStoreState;
  }

  async backup(
    stagingPath,
    profilePath = PathUtils.profileDir,
    _isEncrypting = false
  ) {
    // Flush tab state so backups receive the correct url to restore.
    await Promise.race([
      Promise.allSettled(
        lazy.BrowserWindowTracker.orderedWindows.map(
          lazy.TabStateFlusher.flushWindow
        )
      ),
      new Promise((_, reject) =>
        lazy.setTimeout(reject, lazy.TAB_FLUSH_TIMEOUT, { timeout: true })
      ),
    ]).catch(e => {
      if (e?.timeout) {
        lazy.logConsole.warn("Timed out waiting while flushing tab state.");
      } else {
        lazy.logConsole.error(
          "Unrecognized error while flushing tab state.",
          e
        );
      }
    });

    let sessionStorePath = PathUtils.join(stagingPath, "sessionstore.jsonlz4");

    await IOUtils.writeJSON(sessionStorePath, this.filteredSessionStoreState, {
      compress: true,
    });
    await BackupResource.copyFiles(profilePath, stagingPath, [
      "sessionstore-backups",
    ]);

    return null;
  }

  async recover(_manifestEntry, recoveryPath, destProfilePath) {
    await BackupResource.copyFiles(recoveryPath, destProfilePath, [
      "sessionstore.jsonlz4",
      "sessionstore-backups",
    ]);

    return null;
  }

  async measure(profilePath = PathUtils.profileDir) {
    // Get the current state of the session store JSON and
    // measure it's uncompressed size.
    let sessionStoreJson = this.#sessionStore.getCurrentState(true);
    let sessionStoreSize = new TextEncoder().encode(
      JSON.stringify(sessionStoreJson)
    ).byteLength;
    let sessionStoreNearestTenKb = bytesToFuzzyKilobytes(sessionStoreSize);

    Glean.browserBackup.sessionStoreSize.set(sessionStoreNearestTenKb);

    let sessionStoreBackupsDirectoryPath = PathUtils.join(
      profilePath,
      "sessionstore-backups"
    );
    let sessionStoreBackupsDirectorySize =
      await BackupResource.getDirectorySize(sessionStoreBackupsDirectoryPath);

    Glean.browserBackup.sessionStoreBackupsDirectorySize.set(
      sessionStoreBackupsDirectorySize
    );
  }
}
