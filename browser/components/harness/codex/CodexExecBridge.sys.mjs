/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { WebSocketServer } from "moz-src:///browser/components/harness/codex/WebSocketServer.sys.mjs";
import { setTimeout } from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  HarnessAgent: "moz-src:///browser/components/harness/HarnessAgent.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "CodexExecBridge",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const WORKSPACE = "/workspace";
const EXEC_TIMEOUT_MS = 10 * 60 * 1000;
const FS_TIMEOUT_MS = 30 * 1000;
const MAX_READ_WAIT_MS = 30 * 1000;
const AUDIT_LOG_LIMIT = 1000;

function shQuote(value) {
  return `'${value.replaceAll("'", `'\\''`)}'`;
}

function textToB64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  const CHUNK = 0x8000;
  for (let i = 0; i < bytes.length; i += CHUNK) {
    binary += String.fromCharCode(...bytes.subarray(i, i + CHUNK));
  }
  return btoa(binary);
}

// Lexically normalize a guest path: resolve '.', '..' and duplicate slashes
// without consulting any filesystem (host or guest).
function normalizeGuestPath(path) {
  const out = [];
  for (const part of path.split("/")) {
    if (part == "" || part == ".") {
      continue;
    }
    if (part == "..") {
      out.pop();
    } else {
      out.push(part);
    }
  }
  return `/${out.join("/")}`;
}

function pathFromUri(uri) {
  if (typeof uri != "string" || !uri.startsWith("file://")) {
    throw new Error(`unsupported path uri: ${uri}`);
  }
  // file://<authority>/<path>; loopback bridge only accepts empty authority.
  const withoutScheme = uri.slice("file://".length);
  if (!withoutScheme.startsWith("/")) {
    throw new Error(`unsupported path uri authority: ${uri}`);
  }
  return normalizeGuestPath(decodeURIComponent(withoutScheme));
}

function toFileUri(path) {
  return `file://${path.split("/").map(encodeURIComponent).join("/")}`;
}

/**
 * Impersonates `codex exec-server` on a loopback WebSocket and routes every
 * process and filesystem operation into the micro-VM guest via HarnessAgent.
 * There is deliberately no code path that touches the host: unknown methods
 * and out-of-workspace paths are rejected, and everything is audit-logged.
 *
 * fs ops are executed *inside the guest* (via shell) rather than host-side on
 * the shared workspace dir, so symlinks and .. resolve in the guest
 * namespace.
 */
export const CodexExecBridge = {
  _server: null,
  _processes: new Map(),
  auditLog: [],

  get running() {
    return !!this._server;
  },

  get url() {
    return `ws://127.0.0.1:${this._server?.port}`;
  },

  start() {
    if (this._server) {
      return this.url;
    }
    this._server = new WebSocketServer({
      onMessage: message => this._onMessage(message),
      onConnect: () => this._audit("connection", "app-server connected"),
      onDisconnect: () => this._audit("connection", "app-server disconnected"),
    });
    this._server.start();
    lazy.logConsole.log(`exec bridge at ${this.url}`);
    return this.url;
  },

  stop() {
    for (const record of this._processes.values()) {
      if (!record.exited) {
        lazy.HarnessAgent.kill(record.requestId).catch(() => {});
      }
    }
    this._processes.clear();
    this._server?.stop();
    this._server = null;
  },

  _audit(method, detail, verdict = "ok") {
    const entry = { timeMs: Date.now(), method, detail, verdict };
    this.auditLog.push(entry);
    if (this.auditLog.length > AUDIT_LOG_LIMIT) {
      this.auditLog.shift();
    }
    lazy.logConsole.log(`${verdict}: ${method} ${detail}`);
  },

  async _onMessage(message) {
    if (message.method === undefined || message.id === undefined) {
      return; // notifications from the client (e.g. initialized) need no reply
    }
    try {
      const result = await this._handle(message.method, message.params ?? {});
      this._server?.send({ id: message.id, result });
    } catch (e) {
      this._audit(message.method, e.message, "error");
      this._server?.send({
        id: message.id,
        error: { code: -32000, message: e.message },
      });
    }
  },

  _allowedPath(uri, { write = false } = {}) {
    const path = pathFromUri(uri);
    if (path != WORKSPACE && !path.startsWith(`${WORKSPACE}/`)) {
      throw new Error(
        `${write ? "write" : "read"} outside ${WORKSPACE} denied: ${path}`
      );
    }
    return path;
  },

  async _guest(cmd, options = {}) {
    const result = await lazy.HarnessAgent.exec(cmd, {
      cwd: WORKSPACE,
      timeoutMs: FS_TIMEOUT_MS,
      ...options,
    });
    if (result.exitCode !== 0) {
      throw new Error(result.stderr.trim() || `guest exit ${result.exitCode}`);
    }
    return result;
  },

  async _handle(method, params) {
    switch (method) {
      case "initialize":
        this._audit(method, params.clientName ?? "");
        return {
          sessionId: Services.uuid.generateUUID().toString().slice(1, -1),
        };
      case "environment/info":
        this._audit(method, "");
        return {
          shell: { name: "sh", path: "/bin/sh" },
          cwd: toFileUri(WORKSPACE),
          capabilities: { networkProxyLaunch: false },
        };
      case "environment/status":
        return { status: "ready" };
      case "process/start":
        return this._processStart(params);
      case "process/read":
        return this._processRead(params);
      case "process/write":
        // Upfront stdin only (see guest-agent); interactive stdin is not
        // supported yet.
        this._audit(method, params.processId, "unsupported");
        return { status: "stdinClosed" };
      case "process/signal":
      case "process/terminate":
        return this._processKill(method, params);
      case "fs/readFile": {
        const path = this._allowedPath(params.path);
        this._audit(method, path);
        const result = await this._guest(`base64 < ${shQuote(path)}`);
        return { dataBase64: result.stdout.replaceAll("\n", "") };
      }
      case "fs/writeFile": {
        const path = this._allowedPath(params.path, { write: true });
        this._audit(method, path);
        await this._guest(`base64 -d > ${shQuote(path)}`, {
          stdin: params.dataBase64,
        });
        return {};
      }
      case "fs/createDirectory": {
        const path = this._allowedPath(params.path, { write: true });
        this._audit(method, path);
        await this._guest(
          `mkdir ${params.recursive ? "-p " : ""}${shQuote(path)}`
        );
        return {};
      }
      case "fs/getMetadata": {
        const path = this._allowedPath(params.path);
        this._audit(method, path);
        const q = shQuote(path);
        const result = await this._guest(
          `if [ -L ${q} ]; then l=1; else l=0; fi; ` +
            `s=$(stat -c '%F|%s|%Y' ${q}) && printf '%s|%s' "$l" "$s"`
        );
        const [link, kind, size, mtime] = result.stdout.trim().split("|");
        return {
          isDirectory: kind == "directory",
          isFile: kind.includes("file"),
          isSymlink: link == "1",
          size: Number(size),
          createdAtMs: Number(mtime) * 1000,
          modifiedAtMs: Number(mtime) * 1000,
        };
      }
      case "fs/canonicalize": {
        const path = this._allowedPath(params.path);
        this._audit(method, path);
        const result = await this._guest(`realpath ${shQuote(path)}`);
        return { path: toFileUri(result.stdout.trim()) };
      }
      case "fs/readDirectory": {
        const path = this._allowedPath(params.path);
        this._audit(method, path);
        const result = await this._guest(
          `cd ${shQuote(path)} && for f in * .[!.]* ..?*; do ` +
            `[ -e "$f" ] || [ -L "$f" ] || continue; ` +
            `if [ -d "$f" ]; then t=d; elif [ -f "$f" ]; then t=f; else t=o; fi; ` +
            `printf '%s\\t%s\\n' "$t" "$f"; done`
        );
        const entries = [];
        for (const line of result.stdout.split("\n")) {
          if (!line) {
            continue;
          }
          const [type, ...name] = line.split("\t");
          entries.push({
            fileName: name.join("\t"),
            isDirectory: type == "d",
            isFile: type == "f",
          });
        }
        return { entries };
      }
      case "fs/remove": {
        const path = this._allowedPath(params.path, { write: true });
        this._audit(method, path);
        const flags = `${params.recursive ? "-r " : ""}${params.force ? "-f " : ""}`;
        await this._guest(`rm ${flags}${shQuote(path)}`);
        return {};
      }
      case "fs/copy": {
        const source = this._allowedPath(params.sourcePath);
        const dest = this._allowedPath(params.destinationPath, {
          write: true,
        });
        this._audit(method, `${source} -> ${dest}`);
        await this._guest(
          `cp ${params.recursive ? "-R " : ""}${shQuote(source)} ${shQuote(dest)}`
        );
        return {};
      }
      default:
        this._audit(method, "", "denied");
        throw new Error(`method not supported: ${method}`);
    }
  },

  _processStart(params) {
    const { processId, argv, cwd, env = {}, tty } = params;
    if (!Array.isArray(argv) || !argv.length) {
      throw new Error("argv required");
    }
    if (this._processes.has(processId)) {
      throw new Error(`duplicate processId ${processId}`);
    }
    const cwdPath = this._allowedPath(cwd, { write: true });
    const cmd = argv.map(shQuote).join(" ");
    this._audit(
      "process/start",
      `${cmd.slice(0, 200)}${tty ? " (tty requested; running piped)" : ""}`
    );

    const record = {
      chunks: [],
      nextSeq: 1,
      exited: false,
      exitCode: null,
      closed: false,
      failure: null,
      waiters: [],
    };
    this._processes.set(processId, record);
    const { requestId, result } = lazy.HarnessAgent.execStart(cmd, {
      cwd: cwdPath,
      timeoutMs: EXEC_TIMEOUT_MS,
      env,
      onOutput: (stream, text) => this._pushChunk(processId, stream, text),
    });
    record.requestId = requestId;
    result.then(
      r => this._finishProcess(processId, r.exitCode, null),
      e => this._finishProcess(processId, -1, e.message)
    );
    return { processId };
  },

  _pushChunk(processId, stream, text) {
    const record = this._processes.get(processId);
    if (!record) {
      return;
    }
    const chunk = {
      seq: record.nextSeq++,
      stream: stream == "stderr" ? "stderr" : "stdout",
      chunk: textToB64(text),
    };
    record.chunks.push(chunk);
    this._wake(record);
    this._server?.send({
      method: "process/output",
      params: { processId, ...chunk },
    });
  },

  _finishProcess(processId, exitCode, failure) {
    const record = this._processes.get(processId);
    if (!record) {
      return;
    }
    record.exited = true;
    record.closed = true;
    record.exitCode = exitCode;
    record.failure = failure;
    this._audit("process/exited", `${processId} code=${exitCode}`);
    this._wake(record);
    const seq = record.nextSeq++;
    this._server?.send({
      method: "process/exited",
      params: { processId, seq, exitCode: exitCode ?? -1 },
    });
    this._server?.send({
      method: "process/closed",
      params: { processId, seq: record.nextSeq++ },
    });
  },

  _wake(record) {
    for (const waiter of record.waiters.splice(0)) {
      waiter();
    }
  },

  async _processRead(params) {
    const record = this._processes.get(params.processId);
    if (!record) {
      throw new Error(`unknown process ${params.processId}`);
    }
    const after = params.afterSeq ?? 0;
    const pending = () => record.chunks.filter(c => c.seq > after);
    let chunks = pending();
    if (!chunks.length && !record.exited && params.waitMs) {
      await new Promise(resolve => {
        record.waiters.push(resolve);
        setTimeout(resolve, Math.min(params.waitMs, MAX_READ_WAIT_MS));
      });
      chunks = pending();
    }
    if (params.maxBytes) {
      let total = 0;
      chunks = chunks.filter(c => {
        total += (c.chunk.length * 3) / 4;
        return total <= params.maxBytes;
      });
    }
    return {
      chunks,
      nextSeq: record.nextSeq,
      exited: record.exited,
      exitCode: record.exitCode,
      closed: record.closed,
      failure: record.failure,
      sandboxDenied: false,
    };
  },

  async _processKill(method, params) {
    const record = this._processes.get(params.processId);
    if (!record) {
      throw new Error(`unknown process ${params.processId}`);
    }
    this._audit(method, params.processId);
    if (!record.exited) {
      await lazy.HarnessAgent.kill(record.requestId);
    }
    return method == "process/terminate" ? { running: !record.exited } : {};
  },
};
