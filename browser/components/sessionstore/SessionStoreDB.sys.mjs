/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * A connection to a session store database, which holds session state as
 * rows of JSON fragments. `mozISessionStoreDatabase` runs every operation in
 * order on the connection's own thread; this module wraps it in promises and
 * owns the connection's lifetime.
 *
 * The rows:
 *
 * - `root`: named payloads. "state" is the top-level state object without its
 *   split properties; every other name becomes a property of it.
 * - `nodes`: one element of a split array, or the value of a split object
 *   property. `parent` is the id of the node that holds it, or 0 for the
 *   top-level state, and `prop` is the property that holds it. A NULL payload
 *   encodes JSON null.
 * - `child_order`: for each split property of a node, a JSON array of child
 *   node ids in order, or a single id for an object property.
 * - `sections`: JSON objects whose members merge into their node.
 * - `meta`: bookkeeping strings that aren't part of the state.
 *
 * `write()` applies a batch of operations in one transaction, flattened into
 * an array of strings:
 *
 * - "guard", key, expected: abort the batch unless meta[key] equals expected,
 *   with "" for an unset key.
 * - "clear": delete every node, order, section and root.
 * - "node", id, parent, prop, payload: insert or replace a node.
 * - "nullnode", id, parent, prop: insert or replace a node that is null.
 * - "delnode", id: delete a node, its sections and its orders, but not its
 *   children.
 * - "order", parent, prop, ids: set the children of a split property.
 * - "delorder", parent, prop
 * - "section", node, name, payload
 * - "delsection", node, name
 * - "root", name, payload
 * - "delroot", name
 * - "meta", key, value
 */

import { XPCOMUtils } from "resource://gre/modules/XPCOMUtils.sys.mjs";

const lazy = XPCOMUtils.declareLazy({
  AsyncShutdown: "resource://gre/modules/AsyncShutdown.sys.mjs",
  FileUtils: "resource://gre/modules/FileUtils.sys.mjs",
});

export class SessionStoreDB {
  /**
   * Opens the database at `path`, creating it if needed.
   *
   * @param {string} path
   * @returns {Promise<SessionStoreDB>}
   */
  static async open(path) {
    let existed = await IOUtils.exists(path);
    let connection = await new Promise((resolve, reject) => {
      Services.storage.openAsyncDatabase(
        new lazy.FileUtils.File(path),
        Ci.mozIStorageService.OPEN_DEFAULT,
        Ci.mozIStorageService.CONNECTION_DEFAULT,
        (status, value) => {
          if (Components.isSuccessCode(status)) {
            resolve(value.QueryInterface(Ci.mozIStorageAsyncConnection));
          } else {
            reject(Components.Exception("Could not open " + path, status));
          }
        }
      );
    });
    let db = new SessionStoreDB(path, connection, existed);
    try {
      await db.#call(callback => db.#database.init(connection, callback));
    } catch (ex) {
      await db.close();
      throw ex;
    }
    return db;
  }

  #path;
  #connection;
  #database = Cc["@mozilla.org/browser/sessionstore-database;1"].createInstance(
    Ci.mozISessionStoreDatabase
  );
  #pending = new Set();
  #closePromise = null;
  #blocker = () => this.close();

  /**
   * Whether the database file existed before `open()` was called.
   *
   * @type {boolean}
   */
  existed;

  constructor(path, connection, existed) {
    this.#path = path;
    this.#connection = connection;
    this.existed = existed;
    lazy.AsyncShutdown.profileBeforeChange.addBlocker(
      "SessionStoreDB: closing the database",
      this.#blocker,
      { fetchState: () => ({ pending: this.#pending.size }) }
    );
  }

  /**
   * Reads the whole database.
   *
   * @param {object} [options]
   * @param {boolean} [options.validate]
   *        Whether to parse every fragment and leave out the nodes whose
   *        fragments are invalid, instead of failing.
   * @returns {Promise<{meta: Record<string, string>, state: object|null, dropped: number}>}
   */
  async read({ validate = false } = {}) {
    let json = await this.#call(callback =>
      this.#database.read(validate, callback)
    );
    return JSON.parse(json);
  }

  /**
   * Applies a batch of operations in one transaction.
   *
   * @param {Array<string|number>} ops
   *        The operations described at the top of this module. Numbers are
   *        converted to strings.
   * @returns {Promise<void>}
   */
  async write(ops) {
    await this.#call(callback =>
      this.#database.write(Array.from(ops, String), callback)
    );
  }

  /**
   * Waits for pending operations, then closes the connection.
   *
   * @returns {Promise<void>}
   */
  close() {
    if (!this.#closePromise) {
      this.#closePromise = this.#close();
    }
    return this.#closePromise;
  }

  async #close() {
    await Promise.allSettled(this.#pending);
    this.#database.reset();
    await new Promise(resolve => this.#connection.asyncClose(resolve));
    lazy.AsyncShutdown.profileBeforeChange.removeBlocker(this.#blocker);
  }

  #call(start) {
    if (this.#closePromise) {
      return Promise.reject(new Error(`${this.#path} is closed`));
    }
    let { promise, resolve, reject } = Promise.withResolvers();
    start({
      QueryInterface: ChromeUtils.generateQI([
        "mozISessionStoreDatabaseCallback",
      ]),
      onSuccess: resolve,
      onError: (status, message) =>
        reject(Components.Exception(message, status)),
    });
    this.#pending.add(promise);
    promise.finally(() => this.#pending.delete(promise)).catch(() => {});
    return promise;
  }
}
