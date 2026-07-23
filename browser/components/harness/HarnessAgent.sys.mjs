/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { clearTimeout, setTimeout } from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessAgent",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const HOST_TIMEOUT_SLACK_MS = 5000;

const NON_ASCII_RE = new RegExp("[\\u0080-\\uffff]", "g");

/**
 * JSON-lines client for the guest-agent running inside the micro-VM,
 * connected through the unix socket that libkrun forwards to the guest's
 * vsock port. One instance per VM run; HarnessVM owns the lifecycle.
 */
export const HarnessAgent = {
  _transport: null,
  _outStream: null,
  _inStream: null,
  _scriptableIn: null,
  _buffer: "",
  _pending: new Map(),
  _nextId: 1,

  get connected() {
    return !!this._transport;
  },

  async connect(socketPath, { retries = 40, delayMs = 250 } = {}) {
    for (let attempt = 1; ; attempt++) {
      try {
        this._open(socketPath);
        await this.request({ op: "ping" }, 2000);
        lazy.logConsole.log(`connected to guest-agent via ${socketPath}`);
        return;
      } catch (e) {
        this.close();
        if (attempt >= retries) {
          throw new Error(
            `guest-agent did not respond after ${attempt} attempts: ${e.message}`
          );
        }
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  },

  _open(socketPath) {
    const file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
    file.initWithPath(socketPath);
    const sts = Cc[
      "@mozilla.org/network/socket-transport-service;1"
    ].getService(Ci.nsISocketTransportService);
    this._transport = sts.createUnixDomainTransport(file);
    this._outStream = this._transport.openOutputStream(0, 0, 0);
    this._inStream = this._transport.openInputStream(0, 0, 0);
    this._scriptableIn = Cc[
      "@mozilla.org/scriptableinputstream;1"
    ].createInstance(Ci.nsIScriptableInputStream);
    this._scriptableIn.init(this._inStream);
    this._buffer = "";
    this._waitForData();
  },

  _waitForData() {
    if (!this._inStream) {
      return;
    }
    this._inStream.QueryInterface(Ci.nsIAsyncInputStream).asyncWait(
      {
        onInputStreamReady: () => this._onData(),
      },
      0,
      0,
      Services.tm.currentThread
    );
  },

  _onData() {
    if (!this._scriptableIn) {
      return;
    }
    try {
      const available = this._scriptableIn.available();
      if (available) {
        this._buffer += this._scriptableIn.readBytes(available);
      }
    } catch (e) {
      this._failAllPending(new Error("connection to guest-agent closed"));
      this.close();
      return;
    }
    let newlineIndex;
    while ((newlineIndex = this._buffer.indexOf("\n")) >= 0) {
      const line = this._buffer.slice(0, newlineIndex);
      this._buffer = this._buffer.slice(newlineIndex + 1);
      this._handleLine(line);
    }
    this._waitForData();
  },

  _handleLine(line) {
    // readBytes yields latin1 byte-chars; recover UTF-8.
    const bytes = Uint8Array.from(line, c => c.charCodeAt(0));
    let message;
    try {
      message = JSON.parse(new TextDecoder().decode(bytes));
    } catch (e) {
      lazy.logConsole.warn(`unparseable line from guest-agent: ${line}`);
      return;
    }
    const pending = this._pending.get(message.id);
    if (!pending) {
      lazy.logConsole.warn(`response for unknown id ${message.id}`);
      return;
    }
    if (message.stream) {
      const text = message.data ?? "";
      pending.output[message.stream] += text;
      try {
        pending.onOutput?.(message.stream, text);
      } catch (e) {
        lazy.logConsole.warn(`onOutput callback threw: ${e.message}`);
      }
      return;
    }
    this._pending.delete(message.id);
    if (message.error) {
      pending.reject(new Error(message.error));
    } else if (message.done) {
      pending.resolve({
        exitCode: message.exitCode,
        stdout: pending.output.stdout,
        stderr: pending.output.stderr,
        truncated: message.truncated,
        timedOut: message.timedOut,
      });
    } else {
      pending.resolve(message);
    }
  },

  request(fields, timeoutMs = 30000, onOutput) {
    if (!this._outStream) {
      return Promise.reject(new Error("not connected to guest-agent"));
    }
    const id = this._nextId++;
    // Escape non-ASCII so the payload is byte-safe through write().
    const data = `${JSON.stringify({ id, ...fields }).replace(
      NON_ASCII_RE,
      ch => `\\u${ch.charCodeAt(0).toString(16).padStart(4, "0")}`
    )}\n`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this._pending.delete(id);
        reject(new Error(`guest-agent request timed out after ${timeoutMs}ms`));
      }, timeoutMs);
      this._pending.set(id, {
        onOutput,
        output: { stdout: "", stderr: "" },
        resolve: value => {
          clearTimeout(timer);
          resolve(value);
        },
        reject: error => {
          clearTimeout(timer);
          reject(error);
        },
      });
      try {
        this._outStream.write(data, data.length);
        this._outStream.flush();
      } catch (e) {
        this._pending.delete(id);
        clearTimeout(timer);
        reject(e);
      }
    });
  },

  /**
   * Run a command inside the guest via /bin/sh -c. Output is streamed to
   * onOutput as it arrives and also accumulated into the final result.
   *
   * @param {string} cmd shell command to run
   * @param {object} [options]
   * @param {string} [options.cwd] guest working directory
   * @param {number} [options.timeoutMs] guest-side timeout
   * @param {Function} [options.onOutput] called with (stream, text) chunks
   * @returns {Promise<{exitCode, stdout, stderr, truncated, timedOut}>}
   */
  exec(cmd, { cwd = "/workspace", timeoutMs = 30000, onOutput } = {}) {
    return this.request(
      { op: "exec", cmd, cwd, timeoutMs },
      timeoutMs + HOST_TIMEOUT_SLACK_MS,
      onOutput
    );
  },

  _failAllPending(error) {
    for (const { reject } of this._pending.values()) {
      reject(error);
    }
    this._pending.clear();
  },

  close() {
    this._failAllPending(new Error("guest-agent connection closed"));
    try {
      this._scriptableIn?.close();
      this._outStream?.close();
      this._transport?.close(Cr.NS_OK);
    } catch (e) {
      // Already closed.
    }
    this._transport = null;
    this._outStream = null;
    this._inStream = null;
    this._scriptableIn = null;
    this._buffer = "";
  },
};
