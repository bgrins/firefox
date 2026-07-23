/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { clearTimeout, setTimeout } from "resource://gre/modules/Timer.sys.mjs";

/** Accumulates stream chunks and yields complete newline-terminated lines. */
export class LineSplitter {
  constructor() {
    this._buffer = "";
  }

  get buffered() {
    return this._buffer.length;
  }

  push(chunk) {
    this._buffer += chunk;
    const lines = this._buffer.split("\n");
    this._buffer = lines.pop();
    return lines;
  }
}

/**
 * Correlates request ids with pending promises for JSON-lines protocols
 * (guest-agent, codex app-server). Entries carry arbitrary per-request
 * `data` for callers that route streamed messages before the final reply.
 */
export class RequestTable {
  constructor() {
    this._nextId = 1;
    this._entries = new Map();
  }

  get size() {
    return this._entries.size;
  }

  register({ timeoutMs, timeoutMessage, data } = {}) {
    const id = this._nextId++;
    const entry = { data };
    const promise = new Promise((resolve, reject) => {
      entry._resolve = resolve;
      entry._reject = reject;
    });
    entry._timer = timeoutMs
      ? setTimeout(() => {
          this._entries.delete(id);
          entry._reject(
            new Error(
              timeoutMessage ?? `request ${id} timed out after ${timeoutMs}ms`
            )
          );
        }, timeoutMs)
      : null;
    this._entries.set(id, entry);
    return { id, promise };
  }

  peek(id) {
    return this._entries.get(id);
  }

  resolve(id, value) {
    const entry = this._take(id);
    entry?._resolve(value);
    return !!entry;
  }

  reject(id, error) {
    const entry = this._take(id);
    entry?._reject(error);
    return !!entry;
  }

  rejectAll(error) {
    for (const id of [...this._entries.keys()]) {
      this.reject(id, error);
    }
  }

  _take(id) {
    const entry = this._entries.get(id);
    if (entry) {
      this._entries.delete(id);
      clearTimeout(entry._timer);
    }
    return entry;
  }
}
