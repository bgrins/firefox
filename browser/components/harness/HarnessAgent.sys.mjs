/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { setTimeout } from "resource://gre/modules/Timer.sys.mjs";
import {
  LineSplitter,
  RequestTable,
} from "moz-src:///browser/components/harness/JsonLines.sys.mjs";

const lazy = {};

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessAgent",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const HOST_TIMEOUT_SLACK_MS = 5000;

const NON_ASCII_RE = new RegExp("[\\u0080-\\uffff]", "g");

function textToB64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary);
}

/**
 * JSON-lines client for the guest-agent running inside a micro-VM,
 * connected through the unix socket that libkrun forwards to the guest's
 * vsock port. One instance per VM session; HarnessSession owns the
 * lifecycle.
 */
export class HarnessAgent {
  _transport = null;
  _outStream = null;
  _inStream = null;
  _scriptableIn = null;
  _splitter = new LineSplitter();
  _requests = new RequestTable();

  get connected() {
    return !!this._transport;
  }

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
  }

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
    this._splitter = new LineSplitter();
    this._waitForData();
  }

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
  }

  _onData() {
    if (!this._scriptableIn) {
      return;
    }
    let lines;
    try {
      const available = this._scriptableIn.available();
      lines = available
        ? this._splitter.push(this._scriptableIn.readBytes(available))
        : [];
    } catch (e) {
      this.close();
      return;
    }
    for (const line of lines) {
      this._handleLine(line);
    }
    this._waitForData();
  }

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
    const pending = this._requests.peek(message.id);
    if (!pending) {
      lazy.logConsole.warn(`response for unknown id ${message.id}`);
      return;
    }
    if (message.stream) {
      const text = message.data ?? "";
      pending.data.output[message.stream] += text;
      try {
        pending.data.onOutput?.(message.stream, text);
      } catch (e) {
        lazy.logConsole.warn(`onOutput callback threw: ${e.message}`);
      }
      return;
    }
    if (message.error) {
      this._requests.reject(message.id, new Error(message.error));
    } else if (message.done) {
      this._requests.resolve(message.id, {
        exitCode: message.exitCode,
        stdout: pending.data.output.stdout,
        stderr: pending.data.output.stderr,
        truncated: message.truncated,
        timedOut: message.timedOut,
      });
    } else {
      this._requests.resolve(message.id, message);
    }
  }

  request(fields, timeoutMs = 30000, onOutput) {
    return this.requestWithId(fields, timeoutMs, onOutput).promise;
  }

  requestWithId(fields, timeoutMs = 30000, onOutput) {
    if (!this._outStream) {
      return {
        id: 0,
        promise: Promise.reject(new Error("not connected to guest-agent")),
      };
    }
    const { id, promise } = this._requests.register({
      timeoutMs,
      timeoutMessage: `guest-agent request timed out after ${timeoutMs}ms`,
      data: { onOutput, output: { stdout: "", stderr: "" } },
    });
    // Escape non-ASCII so the payload is byte-safe through write().
    const data = `${JSON.stringify({ id, ...fields }).replace(
      NON_ASCII_RE,
      ch => `\\u${ch.charCodeAt(0).toString(16).padStart(4, "0")}`
    )}\n`;
    try {
      this._outStream.write(data, data.length);
      this._outStream.flush();
    } catch (e) {
      this._requests.reject(id, e);
    }
    return { id, promise };
  }

  /**
   * Run a command inside the guest via /bin/sh -c. Output is streamed to
   * onOutput as it arrives and also accumulated into the final result.
   *
   * @param {string} cmd shell command to run
   * @param {object} [options]
   * @param {string} [options.cwd] guest working directory
   * @param {number} [options.timeoutMs] guest-side timeout
   * @param {Function} [options.onOutput] called with (stream, text) chunks
   * @param {object} [options.env] extra environment variables for the command
   * @param {string} [options.stdin] data piped to the command's stdin
   *   (base64-transported so arbitrary UTF-8 survives byte-exact); without
   *   it the command gets immediate EOF
   * @returns {Promise<{exitCode, stdout, stderr, truncated, timedOut}>}
   */
  exec(cmd, options) {
    return this.execStart(cmd, options).result;
  }

  /**
   * Like exec(), but also returns the request id so the job can be killed
   * with kill() while it runs.
   *
   * @param {string} cmd shell command to run
   * @param {object} [options] same options as exec()
   * @param {string} [options.cwd]
   * @param {number} [options.timeoutMs]
   * @param {Function} [options.onOutput]
   * @param {object} [options.env]
   * @param {string} [options.stdin]
   * @param {boolean} [options.tty] run under a pseudo-terminal (merged
   *   output, input echoed by the pty)
   * @param {boolean} [options.interactive] keep stdin open for input()
   *   until inputEof()
   * @returns {{requestId: number, result: Promise}}
   */
  execStart(
    cmd,
    {
      cwd = "/workspace",
      timeoutMs = 30000,
      onOutput,
      env,
      stdin,
      tty = false,
      interactive = false,
    } = {}
  ) {
    const fields = { op: "exec", cmd, cwd, timeoutMs };
    if (env) {
      fields.env = env;
    }
    if (tty) {
      fields.tty = true;
    }
    if (interactive) {
      fields.interactive = true;
    }
    if (stdin !== undefined) {
      fields.stdinB64 = textToB64(stdin);
    }
    const { id, promise } = this.requestWithId(
      fields,
      timeoutMs + HOST_TIMEOUT_SLACK_MS,
      onOutput
    );
    return { requestId: id, result: promise };
  }

  kill(requestId) {
    return this.request({ op: "kill", targetId: requestId }, 5000);
  }

  /**
   * Writes to a running job's stdin (tty or interactive jobs).
   *
   * @param {number} requestId
   * @param {string} text
   */
  input(requestId, text) {
    return this.request(
      { op: "input", targetId: requestId, stdinB64: textToB64(text) },
      5000
    );
  }

  /**
   * Signals stdin EOF on an interactive job (Ctrl-D on tty jobs).
   *
   * @param {number} requestId
   */
  inputEof(requestId) {
    return this.request({ op: "inputEof", targetId: requestId }, 5000);
  }

  close() {
    this._requests.rejectAll(new Error("guest-agent connection closed"));
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
    this._splitter = new LineSplitter();
  }
}
