/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Writes session state to the session store database next to the JSON
 * session files, and checks after startup that the database agrees with the
 * JSON file that startup read. Used in the "shadow", "export" and "sqlite"
 * modes of `browser.sessionstore.backend`. In the "export" mode, the JSON
 * files are exported from the database, and in the "sqlite" mode less often.
 * In every one of these modes, startup restores from the database after a
 * crash that left it ahead of the JSON files.
 *
 * Both backends store a generation: a lineage, which identifies the database,
 * and a seq, which increments with every save. The JSON file carries them in
 * `session.lineage` and `session.writeSeq`, the database in its meta values.
 * The two are only compared when their generations match, because after a
 * crash one of them can be a save ahead of the other.
 */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

/**
 * @import { SessionDBWriter } from "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs"
 * @import { SessionStoreDB } from "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs"
 */

const lazy = XPCOMUtils.declareLazy({
  SessionDBWriter:
    "moz-src:///browser/components/sessionstore/SessionDBWriter.sys.mjs",
  SessionStoreDB:
    "moz-src:///browser/components/sessionstore/SessionStoreDB.sys.mjs",
  sessionStoreLogger:
    "moz-src:///browser/components/sessionstore/SessionLogger.sys.mjs",
});

const PREF_AUDIT = "browser.sessionstore.db_audit";
// The files SQLite keeps next to the database.
const SIDE_FILES = ["-wal", "-shm", "-journal"];
const MAX_MISMATCH_PATHS = 20;

/**
 * @typedef {object} CrossCheckResult
 * @property {string} result
 *   One of "match", "mismatch", "db_missing", "db_unreadable", "json_missing",
 *   "json_seq_missing", "lineage_mismatch", "skew_json_newer",
 *   "skew_db_newer", "not_comparable", "error".
 * @property {string[]} [paths]
 *   For a mismatch, where the two states differ.
 * @property {number} [jsonSeq]
 * @property {number} [dbSeq]
 *   For a skew, the seq of each side.
 * @property {string} [error]
 *   For an unreadable database or an error, what went wrong.
 */

export class SessionDBBackend {
  #path;
  /**
   * The database, or null after a wipe that doesn't reopen it. A wipe
   * replaces it right away with a promise for the recreated database, so that
   * writes made during the wipe wait for it.
   *
   * @type {Promise<SessionStoreDB|null>}
   */
  #db = Promise.resolve(null);
  /** @type {SessionDBWriter|null} */
  #writer = null;
  // Incremented by each wipe, so that batches built before it are dropped.
  #wipes = 0;
  /** @type {Promise<Record<string, string>>|null} */
  #startupMeta = null;
  /** @type {Promise<Record<string, Record<string, number|number[]>>>|null} */
  #startupOrders = null;
  /** @type {Promise<string>|null} */
  #startupText = null;
  /** @type {CrossCheckResult|null} */
  #crossCheckResult = null;
  // Whether the writer was seeded with the JSON file's state, and the
  // cross-check hasn't confirmed yet that the database holds it.
  #unconfirmedSeed = false;

  /**
   * Resolves with the result of the startup cross-check.
   *
   * @type {Promise<CrossCheckResult>|null}
   */
  crossCheck = null;

  /**
   * Whether JSON files can be exported from the database. They can't while the
   * writer starts from a JSON file's state that the cross-check hasn't
   * confirmed as the database's, since rows the writer judges unchanged may
   * then be stale.
   *
   * @type {boolean}
   */
  get exportable() {
    return !this.#unconfirmedSeed;
  }

  /**
   * @param {string} path
   *        The path of the database file.
   */
  constructor(path) {
    this.#path = path;
  }

  /**
   * Opens the database and reads it before any write can change it, then
   * schedules the cross-check with the JSON file that startup read.
   *
   * @param {object} jsonRead
   * @param {string} jsonRead.origin
   *        The load-order key of the JSON file, or "empty".
   * @param {string} jsonRead.source
   *        The JSON file's text, or "" if none was read.
   * @param {object} [jsonRead.session]
   *        The `session` of the JSON file's state.
   */
  start({ origin, source, session }) {
    let start = ChromeUtils.now();
    this.#db = this.#open();
    this.#db.catch(() => {});
    // The reads are queued before any write. Only the meta values are needed
    // to write, the child ids to seed the writer, and the state is only parsed
    // to restore it or, in idle, for the cross-check.
    let meta = (this.#startupMeta = this.#db.then(db => db.readMeta()));
    this.#startupOrders = this.#db.then(db => db.readOrders());
    this.#startupOrders.catch(() => {});
    let text = (this.#startupText = this.#db.then(db => db.readText()));
    meta.then(
      values => {
        this.#writer = new lazy.SessionDBWriter(values, {
          audit: Services.prefs.getBoolPref(PREF_AUDIT, false),
          // The JSON file is ahead when batches failed.
          minSeq:
            session && session.lineage == values.lineage
              ? Number(session.writeSeq)
              : 0,
        });
      },
      () => {}
    );
    text.then(
      () =>
        Glean.sessionRestore.dbRead.accumulateSingleSample(
          Math.round(ChromeUtils.now() - start)
        ),
      () => {}
    );

    this.crossCheck = text
      .then(
        async json => {
          await new Promise(resolve =>
            ChromeUtils.idleDispatch(resolve, { timeout: 60000 })
          );
          let dbRead;
          try {
            dbRead = JSON.parse(json);
          } catch (ex) {
            return { result: "db_unreadable", error: String(ex) };
          }
          return compare(source, dbRead);
        },
        ex => ({ result: "db_unreadable", error: String(ex) })
      )
      .catch(ex => ({ result: "error", error: String(ex) }))
      .then(result => {
        report(origin, result);
        this.#crossCheckResult = result;
        if (this.#unconfirmedSeed && result.result != "match") {
          this.#writer?.reset();
          Glean.sessionRestore.dbSeed.dropped.add(1);
        }
        this.#unconfirmedSeed = false;
        return result;
      });
  }

  /**
   * Lets the writer start from `state`, the state that startup restores, if
   * the database holds it, so that the first save only writes what changed
   * since instead of rewriting everything. Must be called before anything
   * edits `state`.
   *
   * @param {object|null} state
   * @param {boolean} fromDatabase
   *        Whether `state` was read from the database. Otherwise it was read
   *        from a JSON file, and the database must hold the same generation.
   *        Until the cross-check confirms that it holds the same state, no
   *        file is exported, and if it doesn't, the writer rewrites everything.
   */
  async seed(state, fromDatabase) {
    let meta, orders;
    try {
      [meta, orders] = await Promise.all([
        this.#startupMeta,
        this.#startupOrders,
      ]);
    } catch (ex) {
      Glean.sessionRestore.dbSeed.skipped.add(1);
      return;
    }
    let session = state?.session;
    if (
      !this.#writer ||
      !meta?.lineage ||
      session?.lineage != meta.lineage ||
      String(session.writeSeq) != meta.seq ||
      (!fromDatabase &&
        (meta.comparable != "1" ||
          (this.#crossCheckResult && this.#crossCheckResult.result != "match")))
    ) {
      Glean.sessionRestore.dbSeed.skipped.add(1);
      return;
    }
    try {
      this.#writer.seed(state, orders);
    } catch (ex) {
      lazy.sessionStoreLogger.warn(
        "SessionDBBackend: the restored state doesn't have the database's structure",
        ex
      );
      Glean.sessionRestore.dbSeed.structure_mismatch.add(1);
      return;
    }
    this.#unconfirmedSeed = !fromDatabase;
    Glean.sessionRestore.dbSeed.seeded.add(1);
  }

  /**
   * Opens the database. A corrupt one is moved aside and replaced. Other
   * failures, like a database from a newer build or one that's locked, leave
   * it alone, and the JSON files are written on every save. A database that
   * opens but holds rows that don't form a state heals itself, since the
   * first batch of a writer rewrites everything.
   *
   * @returns {Promise<SessionStoreDB>}
   */
  async #open() {
    try {
      return await lazy.SessionStoreDB.open(this.#path);
    } catch (ex) {
      if (ex.result != Cr.NS_ERROR_FILE_CORRUPTED) {
        throw ex;
      }
      lazy.sessionStoreLogger.error(
        "SessionDBBackend: replacing a corrupt database",
        ex
      );
      await IOUtils.move(this.#path, this.#path + ".corrupt");
      for (let suffix of SIDE_FILES) {
        await IOUtils.remove(this.#path + suffix, { ignoreAbsent: true });
      }
      return lazy.SessionStoreDB.open(this.#path);
    }
  }

  /**
   * Returns the state that startup read from the database, if it should be
   * restored instead of `jsonState`, the state read from the JSON files. The
   * database only wins after a session that didn't shut down cleanly, over a
   * JSON file of the same lineage and an older seq. Otherwise JSON wins: a
   * file of another lineage was restored or copied from elsewhere, one copied
   * into place after a clean shutdown is the user's choice, and without any
   * file, the session files were deleted.
   *
   * @param {object|null} jsonState
   * @returns {Promise<object|null>}
   */
  async stateToRestore(jsonState) {
    let meta = await this.#startupMeta?.catch(() => null);
    let session = jsonState?.session;
    if (
      meta?.run_state != "running" ||
      !session ||
      session.lineage != meta.lineage ||
      !(Number(meta.seq) > Number(session.writeSeq))
    ) {
      return null;
    }
    try {
      return JSON.parse(await this.#startupText).state;
    } catch (ex) {
      lazy.sessionStoreLogger.error(
        "SessionDBBackend: the newer state can't be read",
        ex
      );
      return null;
    }
  }

  /**
   * Stamps the generation of the next write onto `state`, so that the JSON
   * file carries the same generation as the database.
   *
   * @param {object} state
   */
  annotate(state) {
    if (this.#writer && state.session) {
      state.session.lineage = this.#writer.lineage;
      state.session.writeSeq = this.#writer.seq + 1;
    }
  }

  /**
   * Writes the rows of `state` that changed since the previous write. The
   * batch is built synchronously, so later changes to `state` don't affect
   * it.
   *
   * @param {object} state
   * @param {object} options
   * @param {boolean} options.isFinalWrite
   * @param {boolean} options.comparable
   *        Whether the JSON backend serializes `state` in this same task, so
   *        that a cross-check at this generation compares like with like.
   * @param {boolean} [options.checkpoint]
   *        Whether to leave no copy of replaced rows in the write-ahead log,
   *        as after purging data.
   * @returns {Promise<boolean>} Whether the batch was written.
   */
  write(state, { isFinalWrite, comparable, checkpoint = false }) {
    if (!this.#writer) {
      lazy.sessionStoreLogger.debug(
        "SessionDBBackend: skipping a write, since the database isn't open"
      );
      return Promise.resolve(false);
    }
    let writer = this.#writer;
    let start = ChromeUtils.now();
    let ops;
    try {
      ops = writer.materialize(state);
    } catch (ex) {
      lazy.sessionStoreLogger.error(
        "SessionDBBackend: could not build a batch",
        ex
      );
      return Promise.resolve(false);
    }
    ops.push(
      "meta",
      "run_state",
      isFinalWrite ? "clean" : "running",
      "meta",
      "comparable",
      comparable ? "1" : "0"
    );
    if (checkpoint) {
      ops.push("checkpoint");
    }
    Glean.sessionRestore.dbWriteMainThread.accumulateSingleSample(
      Math.round((ChromeUtils.now() - start) * 1000)
    );
    let size = 0;
    for (let op of ops) {
      size += typeof op == "string" ? op.length : 0;
    }
    Glean.sessionRestore.dbBatchSize.accumulate(size);
    if (writer.misses.length) {
      lazy.sessionStoreLogger.error(
        "SessionDBBackend: the change journal missed edits",
        writer.misses
      );
      for (let { group } of writer.misses) {
        Glean.sessionRestore.dbJournalMiss[group].add(1);
      }
    }
    let wipes = this.#wipes;
    return this.#db
      .then(async db => {
        if (!db || wipes != this.#wipes) {
          return false;
        }
        await db.write(ops);
        return true;
      })
      .catch(ex => {
        lazy.sessionStoreLogger.error("SessionDBBackend: write failed", ex);
        writer.reset();
        if (writer == this.#writer) {
          // The next batch rewrites everything.
          this.#unconfirmedSeed = false;
        }
        return false;
      });
  }

  /**
   * Writes the JSON session file from the database, once the batches written
   * so far are applied.
   *
   * @param {string} path
   * @param {object} options
   *        As for SessionStoreDB.exportJSON().
   * @returns {Promise<number>} The size of the file.
   */
  async exportJSON(path, options) {
    let db = await this.#db;
    if (!db) {
      throw new Error("SessionDBBackend: the database is closed");
    }
    let start = ChromeUtils.now();
    try {
      let size = await db.exportJSON(path, options);
      Glean.sessionRestore.dbExportTime.accumulateSingleSample(
        Math.round(ChromeUtils.now() - start)
      );
      return size;
    } catch (ex) {
      if (ex.result == Cr.NS_ERROR_FILE_CORRUPTED) {
        // The next batch rewrites the rows that don't form a state.
        this.#writer?.reset();
        this.#unconfirmedSeed = false;
      }
      throw ex;
    }
  }

  /**
   * Records that the JSON file of the latest write wasn't exported from the
   * database, so that the cross-check doesn't compare it.
   */
  markNotComparable() {
    let wipes = this.#wipes;
    this.#db
      .then(db =>
        db && wipes == this.#wipes
          ? db.write(["meta", "comparable", "0"])
          : undefined
      )
      .catch(ex =>
        lazy.sessionStoreLogger.error("SessionDBBackend: write failed", ex)
      );
  }

  /**
   * Waits for pending writes, then closes the database.
   *
   * @returns {Promise<void>}
   */
  async close() {
    let db = await this.#db.catch(() => null);
    this.#db = Promise.resolve(null);
    this.#writer = null;
    await db?.close();
  }

  /**
   * Deletes the database files. Writes of batches built before the wipe are
   * dropped, and the next batch recreates the database from scratch, unless
   * `reopen` is false.
   *
   * @param {object} [options]
   * @param {boolean} [options.reopen]
   * @returns {Promise<void>}
   */
  async wipe({ reopen = true } = {}) {
    this.#wipes++;
    this.#writer?.reset();
    this.#unconfirmedSeed = false;
    if (!reopen) {
      this.#writer = null;
    }
    let previous = this.#db;
    this.#db = (async () => {
      let db = await previous.catch(() => null);
      await db?.close();
      await removeDatabase(this.#path);
      return reopen ? lazy.SessionStoreDB.open(this.#path) : null;
    })();
    await this.#db.catch(ex =>
      lazy.sessionStoreLogger.error("SessionDBBackend: wipe failed", ex)
    );
  }
}

/**
 * Removes the session database at `path`, with its side files.
 *
 * @param {string} path
 */
export async function removeDatabase(path) {
  for (let suffix of ["", ...SIDE_FILES, ".corrupt"]) {
    await IOUtils.remove(path + suffix, { ignoreAbsent: true });
  }
}

/**
 * @param {string} source
 * @param {{meta: Record<string, string>, state: object|null}} dbRead
 * @returns {CrossCheckResult}
 */
function compare(source, { meta, state: dbState }) {
  if (!dbState) {
    return { result: "db_missing" };
  }
  if (!source) {
    return { result: "json_missing" };
  }
  let jsonState = JSON.parse(source);
  let jsonSeq = jsonState.session?.writeSeq;
  if (jsonSeq === undefined) {
    return { result: "json_seq_missing" };
  }
  if (jsonState.session.lineage != meta.lineage) {
    return { result: "lineage_mismatch" };
  }
  if (String(jsonSeq) != meta.seq) {
    return {
      result:
        Number(jsonSeq) > Number(meta.seq)
          ? "skew_json_newer"
          : "skew_db_newer",
      jsonSeq,
      dbSeq: Number(meta.seq),
    };
  }
  if (meta.comparable == "0") {
    return { result: "not_comparable" };
  }
  let paths = [];
  diff(jsonState, dbState, "", paths);
  return paths.length ? { result: "mismatch", paths } : { result: "match" };
}

/**
 * Collects the paths where two parsed JSON values differ, ignoring the order
 * of object keys.
 */
function diff(a, b, path, paths) {
  if (paths.length >= MAX_MISMATCH_PATHS || a === b) {
    return;
  }
  let isObject = value => value !== null && typeof value == "object";
  if (!isObject(a) || !isObject(b) || Array.isArray(a) != Array.isArray(b)) {
    paths.push(path || "(root)");
    return;
  }
  if (Array.isArray(a)) {
    if (a.length != b.length) {
      paths.push(`${path}.length`);
    }
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      diff(a[i], b[i], `${path}[${i}]`, paths);
    }
    return;
  }
  for (let key of new Set([...Object.keys(a), ...Object.keys(b)])) {
    if (!Object.hasOwn(a, key) || !Object.hasOwn(b, key)) {
      paths.push(`${path}.${key}`);
    } else {
      diff(a[key], b[key], `${path}.${key}`, paths);
    }
  }
}

function report(origin, result) {
  let message = `SessionDBBackend: cross-check against ${origin}: ${result.result}`;
  if (result.result == "match") {
    lazy.sessionStoreLogger.info(message);
  } else {
    lazy.sessionStoreLogger.warn(message, result);
  }
  Glean.sessionRestore.dbCrossCheck[result.result].add(1);
}
