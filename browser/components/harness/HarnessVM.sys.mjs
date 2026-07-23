/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
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
      await this._signHelper(helper);

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
      ];
      if (Services.prefs.getBoolPref("browser.harness.verbose", true)) {
        args.push("--verbose");
      }
      // The wrapper echo gives a visible readiness marker: busybox sh over
      // piped stdio prints no prompt, so a healthy boot is otherwise silent.
      args.push("--", "/bin/sh", "-c", "echo '[guest ready]'; exec /bin/sh");
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
        this._setState("stopped");
        this._emit({ type: "exit", exitCode });
      });
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

  async resetRootfs() {
    if (this.state != "stopped") {
      throw new Error("Stop the VM before resetting the rootfs");
    }
    await IOUtils.remove(this.rootfsPath, { recursive: true });
  },
};
