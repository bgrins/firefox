/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  HarnessAgent: "moz-src:///browser/components/harness/HarnessAgent.sys.mjs",
  Sqlite: "resource://gre/modules/Sqlite.sys.mjs",
  Subprocess: "resource://gre/modules/Subprocess.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessVM",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

function greBinPath(leaf) {
  const file = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

// The helper Program and its entitlements file live in the app dir
// (dist/bin/browser) because moz.build files under browser/ get
// DIST_SUBDIR=browser; the dylibs placed by setup-deps.sh are in GreBinD.
function appBinPath(leaf) {
  const file = Services.dirsvc.get("XCurProcD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

// GreD is dist/bin for plain runs and Contents/Resources in the .app bundle;
// setup-deps.sh extracts to dist/bin/harness, which the bundle mirrors.
function rootfsTemplatePath() {
  const file = Services.dirsvc.get("GreD", Ci.nsIFile);
  file.append("harness");
  file.append("rootfs-template");
  return file.path;
}

/**
 * Manages a single libkrun micro-VM (Alpine guest) via the in-tree
 * harness-vm-helper process. The guest console is the helper's stdio.
 * States: stopped -> starting -> running -> stopping -> stopped.
 */
export const HarnessVM = {
  state: "stopped",
  _proc: null,
  _listeners: new Set(),

  // Events: {type: "state", state}, {type: "stdout"|"stderr", data},
  // {type: "exit", exitCode}, {type: "error", message}
  addListener(listener) {
    this._listeners.add(listener);
  },

  removeListener(listener) {
    this._listeners.delete(listener);
  },

  _emit(event) {
    for (const listener of this._listeners) {
      try {
        listener(event);
      } catch (e) {
        console.error(e);
      }
    }
  },

  _setState(state) {
    this.state = state;
    this._log(`state -> ${state}`);
    this._emit({ type: "state", state });
  },

  // Mirrored to the Browser Console and rendered as meta lines on the page.
  _log(message) {
    lazy.logConsole.log(message);
    this._emit({ type: "log", message });
  },

  get rootfsPath() {
    return PathUtils.join(PathUtils.profileDir, "harness", "rootfs");
  },

  get workspacePath() {
    return PathUtils.join(PathUtils.profileDir, "harness", "workspace");
  },

  /**
   * User-selected extra mounts from the browser.harness.mounts pref
   * (JSON array of {path, tag, readOnly}). Tags are restricted to a shell-
   * and path-safe alphabet and mount at /mnt/<tag> in the guest.
   *
   * @returns {Array<{path: string, tag: string, readOnly: boolean}>}
   */
  get mounts() {
    let parsed;
    try {
      parsed = JSON.parse(
        Services.prefs.getStringPref("browser.harness.mounts", "[]")
      );
    } catch (e) {
      lazy.logConsole.warn(`invalid browser.harness.mounts: ${e.message}`);
      return [];
    }
    if (!Array.isArray(parsed)) {
      return [];
    }
    const seen = new Set(["workspace"]);
    const mounts = [];
    for (const entry of parsed) {
      if (
        typeof entry?.path != "string" ||
        typeof entry?.tag != "string" ||
        !/^[a-z0-9][a-z0-9-]{0,31}$/.test(entry.tag) ||
        seen.has(entry.tag)
      ) {
        lazy.logConsole.warn(`skipping invalid mount ${JSON.stringify(entry)}`);
        continue;
      }
      seen.add(entry.tag);
      mounts.push({
        path: entry.path,
        tag: entry.tag,
        readOnly: !!entry.readOnly,
      });
    }
    return mounts;
  },

  // Keep the socket path short: unix socket paths are capped at 104 bytes
  // on macOS, and profile paths can get close to that.
  _socketPath: null,
  get socketPath() {
    if (!this._socketPath) {
      const id = Services.uuid.generateUUID().toString().slice(1, 9);
      this._socketPath = PathUtils.join(
        Services.dirsvc.get("TmpD", Ci.nsIFile).path,
        `harness-${id}.sock`
      );
    }
    return this._socketPath;
  },

  // The guest-agent is cross-compiled by setup-deps.sh into GreD/harness and
  // refreshed into the rootfs before each start so rebuilds take effect.
  async _installGuestAgent() {
    const source = (() => {
      const file = Services.dirsvc.get("GreD", Ci.nsIFile);
      file.append("harness");
      file.append("guest-agent");
      return file.path;
    })();
    if (!(await IOUtils.exists(source))) {
      throw new Error(
        `Missing ${source}; run browser/components/harness/vm/setup-deps.sh`
      );
    }
    const dest = PathUtils.join(
      this.rootfsPath,
      "usr",
      "local",
      "bin",
      "guest-agent"
    );
    await IOUtils.makeDirectory(PathUtils.parent(dest), {
      createAncestors: true,
      ignoreExisting: true,
    });
    await IOUtils.copy(source, dest);
    await IOUtils.setPermissions(dest, 0o755);
  },

  async _ensureRootfs() {
    if (await IOUtils.exists(this.rootfsPath)) {
      return;
    }
    const template = rootfsTemplatePath();
    if (!(await IOUtils.exists(template))) {
      throw new Error(
        `Missing rootfs template at ${template}; run browser/components/harness/vm/setup-deps.sh`
      );
    }
    this._log(`copying rootfs template to ${this.rootfsPath}`);
    const start = Date.now();
    await IOUtils.makeDirectory(PathUtils.parent(this.rootfsPath), {
      ignoreExisting: true,
    });
    // cp -Rc preserves the rootfs symlinks (IOUtils.copy would follow them)
    // and clones on APFS.
    const cp = await lazy.Subprocess.call({
      command: "/bin/cp",
      arguments: ["-Rc", template, this.rootfsPath],
      stderr: "stdout",
    });
    const { exitCode } = await cp.wait();
    if (exitCode !== 0) {
      throw new Error(`Failed to copy rootfs template (cp exited ${exitCode})`);
    }
    this._log(`rootfs copy done in ${Date.now() - start}ms`);
  },

  // mach build relinks the helper with a plain ad-hoc signature, dropping the
  // hypervisor entitlement, so re-sign unconditionally before each start.
  async _signHelper(helperPath) {
    this._log(`codesigning ${helperPath} with hypervisor entitlement`);
    const proc = await lazy.Subprocess.call({
      command: "/usr/bin/codesign",
      arguments: [
        "-f",
        "-s",
        "-",
        "--entitlements",
        appBinPath("harness-vm-helper.entitlements.xml"),
        helperPath,
      ],
      stderr: "stdout",
    });
    const { exitCode } = await proc.wait();
    if (exitCode !== 0) {
      throw new Error(`codesign failed (${exitCode})`);
    }
  },

  async start() {
    if (this.state != "stopped") {
      return;
    }
    this._setState("starting");
    try {
      const helper = appBinPath("harness-vm-helper");
      const libkrun = greBinPath("libkrun.dylib");
      const libkrunfw = greBinPath("libkrunfw.5.dylib");
      for (const path of [helper, libkrun, libkrunfw]) {
        if (!(await IOUtils.exists(path))) {
          throw new Error(
            `Missing ${path}; run ./mach build and browser/components/harness/vm/setup-deps.sh`
          );
        }
      }
      await this._ensureRootfs();
      await this._installGuestAgent();
      await this._signHelper(helper);
      await IOUtils.makeDirectory(this.workspacePath, {
        createAncestors: true,
        ignoreExisting: true,
      });

      const args = [
        "--lib",
        libkrun,
        "--krunfw",
        libkrunfw,
        "--root",
        this.rootfsPath,
        "--mem",
        "1024",
        "--cpus",
        "2",
        "--vsock",
        `1024:${this.socketPath}`,
        "--volume",
        `${this.workspacePath}:workspace`,
      ];
      const mountCmds = [
        "mkdir -p /workspace && mount -t virtiofs workspace /workspace",
      ];
      for (const mount of this.mounts) {
        if (!(await IOUtils.exists(mount.path))) {
          this._log(`skipping missing mount ${mount.path}`);
          continue;
        }
        args.push(
          "--volume",
          `${mount.path}:${mount.tag}${mount.readOnly ? ":ro" : ""}`
        );
        mountCmds.push(
          `mkdir -p /mnt/${mount.tag} && mount ${
            mount.readOnly ? "-o ro " : ""
          }-t virtiofs ${mount.tag} /mnt/${mount.tag}`
        );
      }
      if (Services.prefs.getBoolPref("browser.harness.allownet", false)) {
        args.push("--allow-net");
      }
      if (Services.prefs.getBoolPref("browser.harness.verbose", true)) {
        args.push("--verbose");
      }
      // The wrapper echo gives a visible readiness marker: busybox sh over
      // piped stdio prints no prompt, so a healthy boot is otherwise silent.
      args.push(
        "--",
        "/bin/sh",
        "-c",
        `${mountCmds.join("; ")}; ` +
          "/usr/local/bin/guest-agent & echo '[guest ready]'; exec /bin/sh"
      );
      this._log(`spawning ${helper} ${args.join(" ")}`);
      const proc = await lazy.Subprocess.call({
        command: helper,
        arguments: args,
        stderr: "pipe",
      });
      this._proc = proc;
      this._log(`helper running with pid ${proc.pid}`);
      this._setState("running");
      this._readLoop(proc.stdout, "stdout");
      this._readLoop(proc.stderr, "stderr");
      proc.wait().then(({ exitCode }) => {
        this._proc = null;
        lazy.HarnessAgent.close();
        IOUtils.remove(this.socketPath, { ignoreAbsent: true });
        this._socketPath = null;
        this._setState("stopped");
        this._emit({ type: "exit", exitCode });
      });
      lazy.HarnessAgent.connect(this.socketPath).then(
        () => this._log("guest-agent connected"),
        e => this._log(`guest-agent connection failed: ${e.message}`)
      );
    } catch (e) {
      this._proc = null;
      this._setState("stopped");
      this._emit({ type: "error", message: e.message });
    }
  },

  async _readLoop(pipe, type) {
    try {
      let chunk;
      while ((chunk = await pipe.readString())) {
        this._emit({ type, data: chunk });
      }
    } catch (e) {
      // Pipe closed on VM exit.
    }
  },

  write(data) {
    if (this.state == "running" && this._proc) {
      this._proc.stdin.write(data);
    } else {
      this._log(`write ignored, VM is ${this.state}: ${data.trim()}`);
    }
  },

  async stop() {
    if (this.state != "running" || !this._proc) {
      return;
    }
    this._setState("stopping");
    await this._proc.kill();
  },

  exec(cmd, options) {
    return lazy.HarnessAgent.exec(cmd, options);
  },

  /**
   * Copies a consistent snapshot of places.sqlite into the workspace so the
   * guest can query it with the sqlite CLI. The live DB cannot be shared:
   * it is WAL-mode with an open shm segment, and SQLite locking does not
   * survive virtio-fs. The online-backup API gives a coherent copy while
   * the profile keeps the DB open, and the guest only ever sees the copy.
   *
   * @returns {Promise<string>} the guest path of the snapshot
   */
  async snapshotPlacesToWorkspace() {
    await IOUtils.makeDirectory(this.workspacePath, {
      createAncestors: true,
      ignoreExisting: true,
    });
    const dest = PathUtils.join(this.workspacePath, "places.sqlite");
    await IOUtils.remove(dest, { ignoreAbsent: true });
    const conn = await lazy.Sqlite.openConnection({
      path: PathUtils.join(PathUtils.profileDir, "places.sqlite"),
      readOnly: true,
    });
    try {
      await conn.backup(dest);
    } finally {
      await conn.close();
    }
    this._log(`places snapshot written to ${dest}`);
    return "/workspace/places.sqlite";
  },

  async resetRootfs() {
    if (this.state != "stopped") {
      throw new Error("Stop the VM before resetting the rootfs");
    }
    await IOUtils.remove(this.rootfsPath, { recursive: true });
  },
};
