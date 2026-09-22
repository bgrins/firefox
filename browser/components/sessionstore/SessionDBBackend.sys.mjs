/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Writes session state to the session store database next to the JSON
 * session file, and checks after startup that the database agrees with the
 * JSON file that startup read. Used in the "shadow" and "export" modes of
 * `browser.sessionstore.backend`, where startup still restores from JSON. In
 * the "export" mode, the JSON file is exported from the database.
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

const CROSS_CHECK_TOPIC = "sessionstore-db-cross-check";
const PREF_AUDIT = "browser.sessionstore.db_audit";
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
  #epoch = 0;

  /**
   * Resolves with the result of the startup cross-check.
   *
   * @type {Promise<CrossCheckResult>|null}
   */
  crossCheck = null;

  /**
   * @param {string} path
   *        The path of the database file.
   */
  constructor(path) {
    this.#path = path;
  }

  /**
   * Opens and reads the database before any write can change it, then
   * schedules the cross-check with the JSON file that startup read.
   *
   * @param {object} jsonRead
   * @param {string} jsonRead.origin
   *        The load-order key of the JSON file, or "empty".
   * @param {string} jsonRead.source
   *        The JSON file's text, or "" if none was read.
   */
  start({ origin, source }) {
    this.#db = lazy.SessionStoreDB.open(this.#path);
    this.#db.catch(() => {});
    // Writes before this read finishes are skipped, since there is no writer
    // yet.
    let read = this.#db.then(db => db.read());
    read.then(
      ({ meta }) => {
        this.#writer = new lazy.SessionDBWriter(meta, {
          audit: Services.prefs.getBoolPref(PREF_AUDIT, false),
        });
      },
      () => {}
    );

    this.crossCheck = read
      .then(
        async dbRead => {
          await new Promise(resolve =>
            ChromeUtils.idleDispatch(resolve, { timeout: 60000 })
          );
          return compare(source, dbRead);
        },
        ex => ({ result: "db_unreadable", error: String(ex) })
      )
      .catch(ex => ({ result: "error", error: String(ex) }))
      .then(result => {
        report(origin, result);
        return result;
      });
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
   * @returns {Promise<boolean>} Whether the batch was written.
   */
  write(state, { isFinalWrite, comparable }) {
    if (!this.#writer) {
      lazy.sessionStoreLogger.debug(
        "SessionDBBackend: skipping a write before the database was read"
      );
      return Promise.resolve(false);
    }
    let writer = this.#writer;
    let start = ChromeUtils.now();
    let ops = writer.materialize(state);
    ops.push(
      "meta",
      "run_state",
      isFinalWrite ? "clean" : "running",
      "meta",
      "comparable",
      comparable ? "1" : "0"
    );
    Glean.sessionRestore.dbWriteMainThread.accumulateSingleSample(
      Math.round((ChromeUtils.now() - start) * 1000)
    );
    if (writer.misses.length) {
      lazy.sessionStoreLogger.error(
        "SessionDBBackend: the change journal missed edits",
        writer.misses
      );
      for (let { group } of writer.misses) {
        Glean.sessionRestore.dbJournalMiss[group].add(1);
      }
    }
    let epoch = this.#epoch;
    return this.#db
      .then(async db => {
        if (!db || epoch != this.#epoch) {
          return false;
        }
        await db.write(ops);
        return true;
      })
      .catch(ex => {
        lazy.sessionStoreLogger.error("SessionDBBackend: write failed", ex);
        writer.reset();
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
    return db.exportJSON(path, options);
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
    this.#epoch++;
    this.#writer?.reset();
    if (!reopen) {
      this.#writer = null;
    }
    let previous = this.#db;
    this.#db = (async () => {
      let db = await previous.catch(() => null);
      await db?.close();
      for (let suffix of ["", "-wal", "-shm", "-journal"]) {
        await IOUtils.remove(this.#path + suffix, { ignoreAbsent: true });
      }
      return reopen ? lazy.SessionStoreDB.open(this.#path) : null;
    })();
    await this.#db.catch(ex =>
      lazy.sessionStoreLogger.error("SessionDBBackend: wipe failed", ex)
    );
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
  Services.obs.notifyObservers(null, CROSS_CHECK_TOPIC, JSON.stringify(result));
}
