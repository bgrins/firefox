/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import {
  LineSplitter,
  RequestTable,
} from "moz-src:///browser/components/harness/JsonLines.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  Subprocess: "resource://gre/modules/Subprocess.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "CodexAppServer",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const MAX_BUFFERED_BYTES = 32 * 1024 * 1024;
const DEFAULT_REQUEST_TIMEOUT_MS = 60000;

function greDPath(...leafs) {
  const file = Services.dirsvc.get("GreD", Ci.nsIFile);
  for (const leaf of leafs) {
    file.append(leaf);
  }
  return file.path;
}

function appDirPath(...leafs) {
  const file = Services.dirsvc.get("XCurProcD", Ci.nsIFile);
  for (const leaf of leafs) {
    file.append(leaf);
  }
  return file.path;
}

/**
 * Owns one `codex app-server` sidecar process and speaks its JSONL protocol
 * over stdio. Security posture: launched with a fully explicit environment
 * (dedicated CODEX_HOME/HOME/TMPDIR, minimal PATH, nothing inherited) and a
 * neutral empty working directory; incoming server->client *requests* (e.g.
 * approvals) fail closed unless a handler explicitly allows them.
 */
export class CodexAppServerClient {
  // The pinned sidecar is installed by vm/setup-codex.sh, not the build.
  static defaultBinaryPath() {
    return greDPath("harness", "codex", "codex-app-server");
  }

  // Packaged copy of codex/ollama-codex-home/config.toml (see moz.build).
  static defaultConfigTemplatePath() {
    return appDirPath("harness", "codex", "config.toml");
  }

  constructor({ binaryPath, codexHome, configTemplatePath } = {}) {
    this._binaryPath = binaryPath ?? CodexAppServerClient.defaultBinaryPath();
    this._codexHome =
      codexHome ??
      PathUtils.join(PathUtils.profileDir, "harness", "codex-home");
    this._configTemplatePath =
      configTemplatePath ?? CodexAppServerClient.defaultConfigTemplatePath();
    this._proc = null;
    this._requests = new RequestTable();
    this._splitter = new LineSplitter();
    this._listeners = new Set();
    this._initializeResult = null;
    // Server->client requests are denied unless replaced.
    this.onServerRequest = async request => {
      lazy.logConsole.warn(`denying server request ${request.method}`);
      throw new Error(`${request.method} not permitted`);
    };
  }

  get running() {
    return !!this._proc;
  }

  get initializeResult() {
    return this._initializeResult;
  }

  addListener(listener) {
    this._listeners.add(listener);
  }

  removeListener(listener) {
    this._listeners.delete(listener);
  }

  _emit(notification) {
    for (const listener of this._listeners) {
      try {
        listener(notification);
      } catch (e) {
        console.error(e);
      }
    }
  }

  async start() {
    if (this._proc) {
      throw new Error("already started");
    }
    if (!(await IOUtils.exists(this._binaryPath))) {
      throw new Error(
        `Missing ${this._binaryPath}; run browser/components/harness/vm/setup-codex.sh`
      );
    }
    const configPath = PathUtils.join(this._codexHome, "config.toml");
    if (!(await IOUtils.exists(configPath))) {
      await IOUtils.makeDirectory(this._codexHome, {
        createAncestors: true,
        ignoreExisting: true,
      });
      await IOUtils.copy(this._configTemplatePath, configPath);
    }
    const cwd = PathUtils.join(this._codexHome, "cwd");
    const tmp = PathUtils.join(this._codexHome, "tmp");
    for (const dir of [cwd, tmp]) {
      await IOUtils.makeDirectory(dir, {
        createAncestors: true,
        ignoreExisting: true,
      });
    }

    lazy.logConsole.log(
      `starting ${this._binaryPath} (CODEX_HOME=${this._codexHome})`
    );
    this._proc = await lazy.Subprocess.call({
      command: this._binaryPath,
      arguments: [],
      workdir: cwd,
      // Fully explicit environment: nothing (SSH agents, cloud/git
      // credentials, dev shell state) is inherited from the Firefox process.
      environment: {
        CODEX_HOME: this._codexHome,
        HOME: this._codexHome,
        TMPDIR: tmp,
        PATH: "/usr/bin:/bin",
      },
      stderr: "pipe",
    });
    this._readLoop();
    this._stderrLoop();
    this._proc.wait().then(({ exitCode }) => {
      if (this._proc) {
        lazy.logConsole.warn(`sidecar exited unexpectedly (${exitCode})`);
        this._proc = null;
        this._requests.rejectAll(new Error(`app-server exited (${exitCode})`));
        this._emit({ method: "sidecarExited", params: { exitCode } });
      }
    });

    this._initializeResult = await this.request("initialize", {
      clientInfo: {
        name: "firefox-harness",
        title: "Firefox Harness",
        version: "0.1",
      },
      capabilities: { experimentalApi: true },
    });
    this.notify("initialized");
    return this._initializeResult;
  }

  async _readLoop() {
    const proc = this._proc;
    try {
      let chunk;
      while ((chunk = await proc.stdout.readString())) {
        if (this._splitter.buffered > MAX_BUFFERED_BYTES) {
          throw new Error("app-server message exceeded size limit");
        }
        for (const line of this._splitter.push(chunk)) {
          this._handleLine(line);
        }
      }
    } catch (e) {
      lazy.logConsole.warn(`read loop ended: ${e.message}`);
      await this.stop();
    }
  }

  async _stderrLoop() {
    const proc = this._proc;
    try {
      let chunk;
      while ((chunk = await proc.stderr.readString())) {
        lazy.logConsole.debug(`stderr: ${chunk.trimEnd()}`);
      }
    } catch (e) {
      // Closed on exit.
    }
  }

  _handleLine(line) {
    let message;
    try {
      message = JSON.parse(line);
    } catch (e) {
      lazy.logConsole.warn(`unparseable line: ${line.slice(0, 200)}`);
      return;
    }
    if (message.method !== undefined && message.id !== undefined) {
      this._handleServerRequest(message);
    } else if (message.id !== undefined) {
      if (message.error) {
        const { code, message: text } = message.error;
        this._requests.reject(
          message.id,
          new Error(`app-server error ${code}: ${text}`)
        );
      } else {
        this._requests.resolve(message.id, message.result);
      }
    } else if (message.method) {
      this._emit(message);
    }
  }

  async _handleServerRequest(message) {
    let reply;
    try {
      const result = await this.onServerRequest(message);
      reply = { id: message.id, result: result ?? {} };
    } catch (e) {
      reply = {
        id: message.id,
        error: { code: -32600, message: e.message },
      };
    }
    this._send(reply);
  }

  _send(obj) {
    if (!this._proc) {
      lazy.logConsole.warn("dropping message; app-server not running");
      return;
    }
    // Escape non-ASCII defensively; the protocol is UTF-8 JSONL but pure
    // ASCII avoids any transport encoding ambiguity.
    const data = `${JSON.stringify(obj).replace(
      new RegExp("[\\u0080-\\uffff]", "g"),
      ch => `\\u${ch.charCodeAt(0).toString(16).padStart(4, "0")}`
    )}\n`;
    this._proc.stdin.write(data);
  }

  request(method, params = {}, timeoutMs = DEFAULT_REQUEST_TIMEOUT_MS) {
    if (!this._proc) {
      return Promise.reject(new Error("app-server not running"));
    }
    const { id, promise } = this._requests.register({
      timeoutMs,
      timeoutMessage: `${method} timed out after ${timeoutMs}ms`,
    });
    this._send({ jsonrpc: "2.0", id, method, params });
    return promise;
  }

  notify(method, params) {
    if (!this._proc) {
      throw new Error("app-server not running");
    }
    const message = { jsonrpc: "2.0", method };
    if (params !== undefined) {
      message.params = params;
    }
    this._send(message);
  }

  async stop() {
    const proc = this._proc;
    if (!proc) {
      return;
    }
    this._proc = null;
    this._requests.rejectAll(new Error("app-server stopped"));
    await proc.kill();
    this._emit({ method: "sidecarExited", params: { exitCode: null } });
  }
}
