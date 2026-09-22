/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Implementation of all the disk I/O required by the session store.
 * This is a private API, meant to be used only by the session store.
 * It will change. Do not use it for any other purpose.
 *
 * Note that this module depends on SessionWriter and that it enqueues its I/O
 * requests and never attempts to simultaneously execute two I/O requests on
 * the files used by this module from two distinct threads.
 * Otherwise, we could encounter bugs, especially under Windows,
 * e.g. if a request attempts to write sessionstore.js while
 * another attempts to copy that file. JSON files exported from the session
 * database are the exception: the database's thread writes them, while
 * SessionWriter waits.
 */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

const lazy = XPCOMUtils.declareLazy({
  capSessionHistory:
    "moz-src:///browser/components/sessionstore/SessionWriter.sys.mjs",
  sessionStoreLogger:
    "moz-src:///browser/components/sessionstore/SessionLogger.sys.mjs",
  removeDatabase:
    "moz-src:///browser/components/sessionstore/SessionDBBackend.sys.mjs",
  RunState: "moz-src:///browser/components/sessionstore/RunState.sys.mjs",
  SessionDBBackend:
    "moz-src:///browser/components/sessionstore/SessionDBBackend.sys.mjs",
  SessionStore:
    "moz-src:///browser/components/sessionstore/SessionStore.sys.mjs",
  SessionWriter:
    "moz-src:///browser/components/sessionstore/SessionWriter.sys.mjs",
});

const PREF_UPGRADE_BACKUP = "browser.sessionstore.upgradeBackup.latestBuildID";
const PREF_MAX_UPGRADE_BACKUPS =
  "browser.sessionstore.upgradeBackup.maxUpgradeBackups";

const PREF_MAX_SERIALIZE_BACK = "browser.sessionstore.max_serialize_back";
const PREF_MAX_SERIALIZE_FWD = "browser.sessionstore.max_serialize_forward";

// "json" writes only the JSON session files. "shadow" also writes the session
// database, and compares it with the JSON files after startup. "export" writes
// the database and exports all but the final JSON file of a session from it.
// "sqlite" writes the database, and exports a JSON file at most every
// PREF_EXPORT_INTERVAL ms. The modes that write the database restore from it
// after a crash that left it ahead of the JSON files.
const PREF_BACKEND = "browser.sessionstore.backend";
const PREF_EXPORT_INTERVAL = "browser.sessionstore.db_export_interval";
const DB_MODES = ["shadow", "export", "sqlite"];
const EXPORT_MODES = ["export", "sqlite"];

export var SessionFile = {
  /**
   * Read the contents of the session file, asynchronously.
   */
  read() {
    return SessionFileInternal.read();
  },
  /**
   * Write the contents of the session file, asynchronously.
   *
   * @param aData - May get changed on shutdown.
   * @param {object} [options]
   * @param {boolean} [options.immediate]
   *        Whether the save was requested right away, like after purging
   *        data, in which case the "sqlite" mode writes the JSON files too.
   */
  write(aData, options) {
    return SessionFileInternal.write(aData, options);
  },
  /**
   * Wipe the contents of the session file, asynchronously.
   */
  wipe() {
    return SessionFileInternal.wipe();
  },

  /**
   * Return the paths to the files used to store, backup, etc.
   * the state of the file.
   */
  get Paths() {
    return SessionFileInternal.Paths;
  },

  /**
   * In the backend modes that write the session database, a promise for the
   * result of comparing it with the JSON file read at startup. Null otherwise.
   *
   * @type {Promise<object>|null}
   */
  get dbCrossCheck() {
    return SessionFileInternal._dbBackend?.crossCheck ?? null;
  },
};

Object.freeze(SessionFile);

const profileDir = PathUtils.profileDir;

var SessionFileInternal = {
  Paths: Object.freeze({
    // The path to the latest version of sessionstore written during a clean
    // shutdown. After startup, it is renamed `cleanBackup`.
    clean: PathUtils.join(profileDir, "sessionstore.jsonlz4"),

    // The path at which we store the previous version of `clean`. Updated
    // whenever we successfully load from `clean`.
    cleanBackup: PathUtils.join(
      profileDir,
      "sessionstore-backups",
      "previous.jsonlz4"
    ),

    // The directory containing all sessionstore backups.
    backups: PathUtils.join(profileDir, "sessionstore-backups"),

    // The path to the latest version of the sessionstore written
    // during runtime. Generally, this file contains more
    // privacy-sensitive information than |clean|, and this file is
    // therefore removed during clean shutdown. This file is designed to protect
    // against crashes / sudden shutdown.
    recovery: PathUtils.join(
      profileDir,
      "sessionstore-backups",
      "recovery.jsonlz4"
    ),

    // The path to the previous version of the sessionstore written
    // during runtime (e.g. 15 seconds before recovery). In case of a
    // clean shutdown, this file is removed.  Generally, this file
    // contains more privacy-sensitive information than |clean|, and
    // this file is therefore removed during clean shutdown.  This
    // file is designed to protect against crashes that are nasty
    // enough to corrupt |recovery|.
    recoveryBackup: PathUtils.join(
      profileDir,
      "sessionstore-backups",
      "recovery.baklz4"
    ),

    // The path to a backup created during an upgrade of Firefox.
    // Having this backup protects the user essentially from bugs in
    // Firefox or add-ons, especially for users of Nightly. This file
    // does not contain any information more sensitive than |clean|.
    upgradeBackupPrefix: PathUtils.join(
      profileDir,
      "sessionstore-backups",
      "upgrade.jsonlz4-"
    ),

    // The session database, written next to the JSON files in the "shadow",
    // "export" and "sqlite" backend modes.
    database: PathUtils.join(profileDir, "sessionstore.sqlite"),

    // The path to the backup of the version of the session store used
    // during the latest upgrade of Firefox. During load/recovery,
    // this file should be used if both |path|, |backupPath| and
    // |latestStartPath| are absent/incorrect.  May be "" if no
    // upgrade backup has ever been performed. This file does not
    // contain any information more sensitive than |clean|.
    get upgradeBackup() {
      let latestBackupID = SessionFileInternal.latestUpgradeBackupID;
      if (!latestBackupID) {
        return "";
      }
      return this.upgradeBackupPrefix + latestBackupID;
    },

    // The path to a backup created during an upgrade of Firefox.
    // Having this backup protects the user essentially from bugs in
    // Firefox, especially for users of Nightly.
    get nextUpgradeBackup() {
      return this.upgradeBackupPrefix + Services.appinfo.platformBuildID;
    },

    /**
     * The order in which to search for a valid sessionstore file.
     */
    get loadOrder() {
      // If `clean` exists and has been written without corruption during
      // the latest shutdown, we need to use it.
      //
      // Otherwise, `recovery` and `recoveryBackup` represent the most
      // recent state of the session store.
      //
      // Finally, if nothing works, fall back to the last known state
      // that can be loaded (`cleanBackup`) or, if available, to the
      // backup performed during the latest upgrade.
      let order = ["clean", "recovery", "recoveryBackup", "cleanBackup"];
      if (SessionFileInternal.latestUpgradeBackupID) {
        // We have an upgradeBackup
        order.push("upgradeBackup");
      }
      return order;
    },
  }),

  // Number of attempted calls to `write`.
  // Note that we may have _attempts > _successes + _failures,
  // if attempts never complete.
  // Used for error reporting.
  _attempts: 0,

  // Number of successful calls to `write`.
  // Used for error reporting.
  _successes: 0,

  // Number of failed calls to `write`.
  // Used for error reporting.
  _failures: 0,

  // `true` once we have initialized SessionWriter.
  _initialized: false,

  // A string that will be set to the session file name part that was read from
  // disk. It will be available _after_ a session file read() is done.
  _readOrigin: null,

  // `true` if the old, uncompressed, file format was used to read from disk, as
  // a fallback mechanism.
  _usingOldExtension: false,

  // The SessionDBBackend in the backend modes that write the database, once
  // read() is done.
  _dbBackend: null,

  // The backend mode, once read() is done.
  _mode: "json",

  // When the latest JSON write started, which the "sqlite" mode uses to space
  // them out.
  _lastJSONWrite: 0,

  // The number of JSON writes started but not finished.
  _jsonWritesPending: 0,

  // Whether a JSON write has been started since the writer was initialized.
  // The first one of a session may move files before it serializes the state.
  _jsonWritten: false,

  // The ID of the latest version of Gecko for which we have an upgrade backup
  // or |undefined| if no upgrade backup was ever written.
  get latestUpgradeBackupID() {
    try {
      return Services.prefs.getCharPref(PREF_UPGRADE_BACKUP);
    } catch (ex) {
      return undefined;
    }
  },

  async _readInternal(useOldExtension) {
    let result;
    let noFilesFound = true;
    this._usingOldExtension = useOldExtension;

    // Attempt to load by order of priority from the various backups
    for (let key of this.Paths.loadOrder) {
      let corrupted = false;
      let exists = true;
      try {
        let path;
        let startMs = Date.now();

        let options = {};
        if (useOldExtension) {
          path = this.Paths[key]
            .replace("jsonlz4", "js")
            .replace("baklz4", "bak");
        } else {
          path = this.Paths[key];
          options.decompress = true;
        }
        let source = await IOUtils.readUTF8(path, options);
        let parsed = JSON.parse(source);

        if (parsed._cachedObjs) {
          try {
            let cacheMap = new Map(parsed._cachedObjs);
            for (let win of parsed.windows.concat(
              parsed._closedWindows || []
            )) {
              for (let tab of win.tabs.concat(win._closedTabs || [])) {
                tab.image = cacheMap.get(tab.image) || tab.image;
              }
            }
          } catch (e) {
            // This is temporary code to clean up after the backout of bug
            // 1546847. Just in case there are problems in the format of
            // the parsed data, continue on. Favicons might be broken, but
            // the session will at least be recovered
            lazy.sessionStoreLogger.error(e);
          }
        }

        if (
          !lazy.SessionStore.isFormatVersionCompatible(
            parsed.version || [
              "sessionrestore",
              0,
            ] /* fallback for old versions*/
          )
        ) {
          // Skip sessionstore files that we don't understand.
          lazy.sessionStoreLogger.warn(
            "Cannot extract data from Session Restore file ",
            path,
            ". Wrong format/version: " + JSON.stringify(parsed.version) + "."
          );
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason:
              "Wrong format/version: " + JSON.stringify(parsed.version) + ".",
          });
          continue;
        }
        result = {
          origin: key,
          source,
          parsed,
          useOldExtension,
        };
        Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
          can_load: "true",
          path_key: key,
          loadfail_reason: "N/A",
        });
        Glean.sessionRestore.readFile.accumulateSingleSample(
          Date.now() - startMs
        );
        lazy.sessionStoreLogger.debug(`Successful file read of ${key} file`);
        break;
      } catch (ex) {
        if (DOMException.isInstance(ex) && ex.name == "NotFoundError") {
          exists = false;
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason: "File doesn't exist.",
          });
          // A file not existing can be normal and expected.
          lazy.sessionStoreLogger.debug(
            `Can't read session file which doesn't exist: ${key}`
          );
        } else if (
          DOMException.isInstance(ex) &&
          ex.name == "NotReadableError"
        ) {
          // The file might incorrectly jsonlz4 encoded
          // We'll count it as "corrupted".
          lazy.sessionStoreLogger.error(
            `NotReadableError when reading session file: ${key}`,
            ex
          );
          corrupted = true;
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason: ` ${ex.name}: Could not read session file`,
          });
        } else if (
          DOMException.isInstance(ex) &&
          ex.name == "NotAllowedError"
        ) {
          // The file might be inaccessible due to wrong permissions
          // or similar failures. We'll just count it as "corrupted".
          lazy.sessionStoreLogger.error(
            `NotAllowedError when reading session file: ${key}`,
            ex
          );
          corrupted = true;
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason: ` ${ex.name}: Could not read session file`,
          });
        } else if (ex instanceof SyntaxError) {
          lazy.sessionStoreLogger.error(
            "Corrupt session file (invalid JSON found) ",
            ex,
            ex.stack
          );
          // File is corrupted, try next file
          corrupted = true;
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason: ` ${ex.name}: Corrupt session file (invalid JSON found)`,
          });
        } else {
          corrupted = true;
          lazy.sessionStoreLogger.error(
            `Unexpected error when reading session file: ${key}`,
            ex
          );
          Glean.sessionRestore.backupCanBeLoadedSessionFile.record({
            can_load: "false",
            path_key: key,
            loadfail_reason: ` ${ex.name}: Could not read session file`,
          });
        }
      } finally {
        if (exists) {
          noFilesFound = false;
          Glean.sessionRestore.corruptFile[corrupted ? "true" : "false"].add();
        }
      }
    }
    return { result, noFilesFound };
  },

  // Find the correct session file and read it.
  async read() {
    // Load session files with lz4 compression.
    let { result, noFilesFound } = await this._readInternal(false);
    if (!result) {
      // No result? Probably because of migration, let's
      // load uncompressed session files.
      let r = await this._readInternal(true);
      result = r.result;
    }

    // All files are corrupted if files found but none could deliver a result.
    let allCorrupt = !noFilesFound && !result;
    Glean.sessionRestore.allFilesCorrupt[allCorrupt ? "true" : "false"].add();

    if (!result) {
      // If everything fails, start with an empty session.
      lazy.sessionStoreLogger.warn(
        "No readable session files found to restore, starting with empty session"
      );
      result = {
        origin: "empty",
        source: "",
        parsed: null,
        useOldExtension: false,
      };
    }
    // The JSON writer starts from the JSON files, even when the database is
    // restored, so that it rotates them as usual.
    this._readOrigin = result.origin;

    let mode = Services.prefs.getStringPref(PREF_BACKEND, "json");
    if (DB_MODES.includes(mode) && !this._dbBackend) {
      this._mode = mode;
      this._dbBackend = new lazy.SessionDBBackend(this.Paths.database);
      this._dbBackend.start({
        origin: result.origin,
        source: result.source,
        session: result.parsed?.session,
      });
      let state = await this._dbBackend.stateToRestore(result.parsed);
      if (
        state &&
        !lazy.SessionStore.isFormatVersionCompatible(
          state.version || ["sessionrestore", 0]
        )
      ) {
        state = null;
      }
      Glean.sessionRestore.dbSourceSelected[state ? "database" : "json"].add(1);
      if (state) {
        result = {
          origin: "database",
          // Only built for observers that could rewrite it.
          source: Services.obs
            .enumerateObservers("sessionstore-state-read")
            .hasMoreElements()
            ? JSON.stringify(state)
            : "",
          parsed: state,
          useOldExtension: false,
        };
      }
      await this._dbBackend.seed(result.parsed, !!state);
    }

    return { ...result, noFilesFound };
  },

  // Initialize SessionWriter and return it as a resolved promise.
  getWriter() {
    if (!this._initialized) {
      if (!this._readOrigin) {
        return Promise.reject(
          "SessionFileInternal.getWriter() called too early! Please read the session file from disk first."
        );
      }

      this._initialized = true;
      lazy.SessionWriter.init(
        this._readOrigin,
        this._usingOldExtension,
        this.Paths,
        {
          maxUpgradeBackups: Services.prefs.getIntPref(
            PREF_MAX_UPGRADE_BACKUPS,
            3
          ),
          maxSerializeBack: Services.prefs.getIntPref(
            PREF_MAX_SERIALIZE_BACK,
            10
          ),
          maxSerializeForward: Services.prefs.getIntPref(
            PREF_MAX_SERIALIZE_FWD,
            -1
          ),
        }
      );
    }

    return Promise.resolve(lazy.SessionWriter);
  },

  /**
   * Writes `aData` to the session database, and returns whether it was
   * written.
   *
   * @param {object} aData
   * @param {object} options
   * @param {boolean} options.isFinalWrite
   * @param {boolean} options.exporting
   *        Whether the JSON file of this write is exported from the database.
   * @param {boolean} options.immediate
   * @returns {Promise<boolean>}
   */
  _writeDatabase(aData, { isFinalWrite, exporting, immediate }) {
    if (isFinalWrite) {
      // The JSON writer caps history too, but only once it gets to write,
      // and the database batch is built now.
      lazy.capSessionHistory(
        aData,
        Services.prefs.getIntPref(PREF_MAX_SERIALIZE_BACK, 10),
        Services.prefs.getIntPref(PREF_MAX_SERIALIZE_FWD, -1)
      );
    }
    // An exported file holds the database's state by construction. A
    // serialized one only if nothing could change the state before the JSON
    // writer serializes it.
    let comparable =
      exporting ||
      (this._jsonWritesPending == 0 &&
        (this._jsonWritten ||
          (this._readOrigin != "clean" && this._readOrigin != "empty")));
    this._dbBackend.annotate(aData);
    return this._dbBackend.write(aData, {
      isFinalWrite,
      comparable,
      // Saves requested right away follow purges.
      checkpoint: immediate,
    });
  },

  write(aData, { immediate = false } = {}) {
    if (lazy.RunState.isClosed) {
      return Promise.reject(new Error("SessionFile is closed"));
    }

    let isFinalWrite = false;
    if (lazy.RunState.isClosing) {
      // If shutdown has started, we will want to stop receiving
      // write instructions.
      isFinalWrite = true;
      lazy.RunState.setClosed();
    }

    let performShutdownCleanup =
      isFinalWrite && !lazy.SessionStore.willAutoRestore;

    let dbWrite = null;
    let exportJSON = null;
    if (this._dbBackend) {
      // The final write serializes the state even in the modes that export,
      // so that the session restored next doesn't depend on the change
      // journal. So do writes while the database may hold stale rows.
      let exporting =
        EXPORT_MODES.includes(this._mode) &&
        !isFinalWrite &&
        this._dbBackend.exportable;
      try {
        dbWrite = this._writeDatabase(aData, {
          isFinalWrite,
          exporting,
          immediate,
        });
      } catch (ex) {
        // The JSON write must happen regardless.
        lazy.sessionStoreLogger.error(
          "SessionFile: could not write the session database",
          ex
        );
        dbWrite = Promise.resolve(false);
      }
      if (exporting) {
        let backend = this._dbBackend;
        exportJSON = async (path, exportOptions) => {
          let reason = "failed";
          try {
            if (!(await dbWrite)) {
              reason = "not_written";
              throw new Error("The database doesn't hold this state");
            }
            let size = await backend.exportJSON(path, exportOptions);
            Glean.sessionRestore.dbExport.exported.add(1);
            return size;
          } catch (ex) {
            Glean.sessionRestore.dbExport[reason].add(1);
            // The state is serialized instead, later than the batch.
            backend.markNotComparable();
            throw ex;
          }
        };
      }
    }

    let options = { isFinalWrite, performShutdownCleanup, exportJSON };
    if (
      this._mode == "sqlite" &&
      !isFinalWrite &&
      !immediate &&
      this._jsonWritten &&
      this._dbBackend.exportable &&
      ChromeUtils.now() - this._lastJSONWrite <
        Services.prefs.getIntPref(PREF_EXPORT_INTERVAL, 600000)
    ) {
      // The database alone holds this save, unless its batch fails.
      return dbWrite.then(written => {
        if (written) {
          Glean.sessionRestore.dbExport.skipped.add(1);
          return undefined;
        }
        return this._writeJSON(aData, options, dbWrite);
      });
    }
    return this._writeJSON(aData, options, dbWrite);
  },

  /**
   * Writes the JSON session file.
   *
   * @param {object} aData
   * @param {object} options
   *        The options for SessionWriter.write().
   * @param {Promise<boolean>|null} dbWrite
   *        The database write of the same save, which callers wait for too.
   * @returns {Promise<void>}
   */
  _writeJSON(aData, options, dbWrite) {
    let { isFinalWrite } = options;
    this._attempts++;
    this._jsonWritesPending++;
    this._jsonWritten = true;
    this._lastJSONWrite = ChromeUtils.now();
    let write = this.getWriter()
      .then(writer => writer.write(aData, options))
      .finally(() => this._jsonWritesPending--);

    // Wait until the write is done.
    let promise = write.then(
      msg => {
        // Record how long the write took.
        if (msg.telemetry.writeFileMs) {
          Glean.sessionRestore.writeFile.accumulateSingleSample(
            msg.telemetry.writeFileMs
          );
        }
        if (msg.telemetry.fileSizeBytes) {
          Glean.sessionRestore.fileSizeBytes.accumulate(
            msg.telemetry.fileSizeBytes
          );
        }

        this._successes++;
        if (msg.result.upgradeBackup) {
          // We have just completed a backup-on-upgrade, store the information
          // in preferences.
          Services.prefs.setCharPref(
            PREF_UPGRADE_BACKUP,
            Services.appinfo.platformBuildID
          );
        }
      },
      err => {
        // Catch and report any errors.
        lazy.sessionStoreLogger.error(
          "Could not write session state file ",
          err,
          err.stack
        );
        this._failures++;
        // Retry at the next save in the "sqlite" mode.
        this._lastJSONWrite = 0;
        // By not doing anything special here we ensure that |promise| cannot
        // be rejected anymore. The shutdown/cleanup code at the end of the
        // function will thus always be executed.
      }
    );

    // Ensure that we can write sessionstore.js cleanly before the profile
    // becomes unaccessible.
    IOUtils.profileBeforeChange.addBlocker(
      "SessionFile: Finish writing Session Restore data",
      promise,
      {
        fetchState: () => ({
          options,
          attempts: this._attempts,
          successes: this._successes,
          failures: this._failures,
        }),
      }
    );

    // This code will always be executed because |promise| can't fail anymore.
    // We ensured that by having a reject handler that reports the failure but
    // doesn't forward the rejection.
    return promise.then(async () => {
      // Remove the blocker, no matter if writing failed or not.
      IOUtils.profileBeforeChange.removeBlocker(promise);

      if (isFinalWrite) {
        Services.obs.notifyObservers(
          null,
          "sessionstore-final-state-write-complete"
        );
      }
      // JSON is what startup restores from, so the checkpoint above doesn't
      // wait for the database, but callers see the save complete only once
      // both have it.
      await dbWrite;
    });
  },

  async wipe() {
    // Started synchronously, so that SessionWriter's queue runs it before the
    // save that follows a purge.
    let jsonWipe = this.getWriter().then(writer => writer.wipe());
    // The next save writes JSON again.
    this._jsonWritten = false;
    let dbWipe = this._dbBackend
      ? this._dbBackend.wipe({ reopen: !lazy.RunState.isQuitting })
      : lazy.removeDatabase(this.Paths.database);
    await Promise.all([jsonWipe, dbWipe]);
    // After a wipe, we need to make sure to re-initialize upon the next read(),
    // because the state variables as sent to the writer have changed.
    this._initialized = false;
  },
};
