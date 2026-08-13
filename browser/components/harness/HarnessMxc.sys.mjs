/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import {
  snapshotPlacesTo,
  refreshPlacesSnapshotIfStale,
} from "moz-src:///browser/components/harness/PlacesSnapshot.sys.mjs";

import {
  setTimeout,
  clearTimeout,
} from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  Subprocess: "resource://gre/modules/Subprocess.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessMxc",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

const HOST_TIMEOUT_SLACK_MS = 5000;
const MAX_OUTPUT_BYTES = 1024 * 1024;

export function mxcBinaryPath() {
  const file = Services.dirsvc.get("GreD", Ci.nsIFile);
  for (const leaf of ["harness", "mxc", "mxc-exec-mac"]) {
    file.append(leaf);
  }
  return file.path;
}

/**
 * HarnessAgent-compatible surface over one-shot mxc-exec-mac spawns: every
 * exec is its own Seatbelt-sandboxed host process (the macOS backend is
 * process-scoped by design — there is no session to provision). Commands
 * run ON THE HOST under a policy profile; see docs/mxc-spike.md for how
 * this differs from the micro-VM security posture.
 */
class MxcAgent {
  constructor(session) {
    this._session = session;
    this._jobs = new Map();
    this._nextId = 1;
  }

  // The bridge advertises this as the exec cwd / path-policy root. Unlike
  // the VM there is no /workspace mount illusion: paths are real host paths.
  get workspaceRoot() {
    return this._session.workspacePath;
  }

  async request(fields, _timeoutMs = 5000) {
    switch (fields.op) {
      case "ping":
        return { ok: true };
      case "input": {
        const proc = await this._procFor(fields.targetId);
        await proc.stdin.write(
          Uint8Array.from(atob(fields.stdinB64), c => c.charCodeAt(0))
        );
        return { ok: true };
      }
      case "inputEof": {
        const proc = await this._procFor(fields.targetId);
        await proc.stdin.close();
        return { ok: true };
      }
      case "kill":
        return this.kill(fields.targetId);
      default:
        throw new Error(`unsupported op ${fields.op}`);
    }
  }

  exec(cmd, options) {
    return this.execStart(cmd, options).result;
  }

  execStart(cmd, options = {}) {
    const requestId = this._nextId++;
    // Registered synchronously: input/kill can arrive before the async
    // spawn completes.
    const job = { proc: null };
    job.ready = new Promise(resolve => {
      job.setProc = proc => {
        job.proc = proc;
        resolve(proc);
      };
    });
    this._jobs.set(requestId, job);
    return { requestId, result: this._run(requestId, job, cmd, options) };
  }

  async _procFor(requestId) {
    const job = this._jobs.get(requestId);
    if (!job) {
      throw new Error(`unknown job ${requestId}`);
    }
    return job.ready;
  }

  async kill(requestId) {
    const job = this._jobs.get(requestId);
    if (job) {
      await (await job.ready).kill();
    }
    return { ok: true };
  }

  async _run(
    requestId,
    job,
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
    const session = this._session;
    if (tty) {
      // The wrapper has no pty allocation; run without one (nestedPty in
      // the profile still lets the inner command allocate its own).
      lazy.logConsole.warn("tty requested; running without a host pty");
    }
    const config = {
      containment: "seatbelt",
      process: {
        commandLine: cmd,
        cwd: session.toHostPath(cwd),
        env: Object.entries({
          PATH: "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
          HOME: session.homePath,
          TMPDIR: session.tmpPath,
          ...env,
        }).map(([key, value]) => `${key}=${value}`),
        timeout: timeoutMs,
      },
      filesystem: {
        readwritePaths: [session.workspacePath, session.homePath, session.tmpPath],
        readonlyPaths: ["/opt/homebrew"],
      },
      network: { defaultPolicy: "block" },
      seatbelt: { nestedPty: true },
    };
    const configPath = PathUtils.join(
      session.configDir,
      `cfg-${session.id}-${requestId}.json`
    );
    await IOUtils.writeUTF8(configPath, JSON.stringify(config));

    const proc = await lazy.Subprocess.call({
      command: mxcBinaryPath(),
      arguments: [configPath],
      environment: { PATH: "/usr/bin:/bin" },
      stderr: "pipe",
    });
    job.setProc(proc);

    let timedOut = false;
    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill();
    }, timeoutMs + HOST_TIMEOUT_SLACK_MS);

    if (stdin !== undefined) {
      await proc.stdin.write(stdin);
    }
    if (!interactive) {
      proc.stdin.close();
    }

    const output = { stdout: "", stderr: "" };
    let truncated = false;
    const drain = async (pipe, stream) => {
      let chunk;
      while ((chunk = await pipe.readString())) {
        if (output[stream].length < MAX_OUTPUT_BYTES) {
          output[stream] += chunk;
        } else {
          truncated = true;
        }
        try {
          onOutput?.(stream, chunk);
        } catch (e) {
          console.error(e);
        }
      }
    };
    const drained = Promise.all([
      drain(proc.stdout, "stdout"),
      drain(proc.stderr, "stderr"),
    ]);

    try {
      const { exitCode } = await proc.wait();
      await drained;
      return {
        exitCode,
        stdout: output.stdout,
        stderr: output.stderr,
        truncated,
        timedOut,
      };
    } finally {
      clearTimeout(timer);
      this._jobs.delete(requestId);
      IOUtils.remove(configPath, { ignoreAbsent: true });
    }
  }
}

/**
 * HarnessSession-compatible session whose "sandbox" is the host itself
 * under MXC Seatbelt policies. There is nothing to boot: start() only
 * verifies the wrapper binary and creates the session directories.
 */
export class MxcSession {
  constructor({ id = "default", baseDir }) {
    this.id = id;
    this._baseDir = baseDir;
    this.state = "stopped";
    this.startedAtMs = null;
    this.pid = null;
    this._listeners = new Set();
    this.agent = new MxcAgent(this);
  }

  get workspacePath() {
    return PathUtils.join(this._baseDir, "workspace");
  }

  get homePath() {
    return PathUtils.join(this._baseDir, "mxc-home");
  }

  get tmpPath() {
    return PathUtils.join(this._baseDir, "mxc-tmp");
  }

  get configDir() {
    return PathUtils.join(this._baseDir, "mxc-config");
  }

  toHostPath(guestPath) {
    if (guestPath == "/workspace") {
      return this.workspacePath;
    }
    if (guestPath?.startsWith("/workspace/")) {
      return PathUtils.join(
        this.workspacePath,
        ...guestPath.slice("/workspace/".length).split("/")
      );
    }
    return guestPath;
  }

  addListener(listener) {
    this._listeners.add(listener);
  }

  removeListener(listener) {
    this._listeners.delete(listener);
  }

  _emit(event) {
    for (const listener of this._listeners) {
      try {
        listener(event);
      } catch (e) {
        console.error(e);
      }
    }
  }

  _log(message) {
    lazy.logConsole.log(`[${this.id}] ${message}`);
    this._emit({ type: "log", message });
  }

  _setState(state) {
    this.state = state;
    this._emit({ type: "state", state });
  }

  async start() {
    if (this.state != "stopped") {
      return;
    }
    this._setState("starting");
    if (!(await IOUtils.exists(mxcBinaryPath()))) {
      this._setState("stopped");
      throw new Error(
        `Missing ${mxcBinaryPath()}; run browser/components/harness/vm/setup-mxc.sh`
      );
    }
    for (const dir of [
      this.workspacePath,
      this.homePath,
      this.tmpPath,
      this.configDir,
    ]) {
      await IOUtils.makeDirectory(dir, {
        createAncestors: true,
        ignoreExisting: true,
      });
    }
    this.startedAtMs = Date.now();
    this._setState("running");
    this._log("mxc host-sandbox session ready (Seatbelt, one-shot per exec)");
  }

  async stop() {
    for (const requestId of [...this.agent._jobs.keys()]) {
      await this.agent.kill(requestId);
    }
    this.startedAtMs = null;
    this._setState("stopped");
  }

  write(_line) {
    this._log("interactive console is not available on the mxc backend");
  }

  exec(cmd, options) {
    return this.agent.exec(cmd, options);
  }

  snapshotPlacesToWorkspace() {
    return snapshotPlacesTo(this.workspacePath, message => this._log(message));
  }

  refreshPlacesSnapshotIfStale(maxAgeMs) {
    return refreshPlacesSnapshotIfStale(this.workspacePath, maxAgeMs);
  }

  async resetRootfs() {
    // No rootfs: the host is the root filesystem.
  }

  async destroy() {
    await this.stop();
    await IOUtils.remove(this._baseDir, {
      recursive: true,
      ignoreAbsent: true,
    });
  }
}
