/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { HarnessAgent } from "moz-src:///browser/components/harness/HarnessAgent.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  HarnessImageManager:
    "moz-src:///browser/components/harness/HarnessImageManager.sys.mjs",
  HarnessProxy: "moz-src:///browser/components/harness/HarnessProxy.sys.mjs",
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

const STAGE2_PATH = "/usr/local/lib/harness-stage2.sh";

// Stage 1 (overlay boots only): root is a host-enforced read-only virtio-fs
// (the shared template); pivot onto a whole-root tmpfs overlay so every
// write outside /workspace is ephemeral.
const STAGE1_SCRIPT = `#!/bin/sh
mount -t tmpfs tmpfs /mnt || exec /bin/sh
mkdir -p /mnt/up /mnt/wk /mnt/nr
mount -t overlay overlay -o lowerdir=/,upperdir=/mnt/up,workdir=/mnt/wk /mnt/nr || exec /bin/sh
mkdir -p /mnt/nr/oldroot
cd /mnt/nr
pivot_root . oldroot
exec chroot . /bin/sh ${STAGE2_PATH}
`;

// Stage 2 (all boots): kernel virtual filesystems are not part of the
// overlay and must be (re-)mounted, including devpts for PTY support; the
// dynamic per-start bits (loopback, user volume mounts) are sourced from a
// host-written file in the workspace. The ready echo gives a visible boot
// marker: busybox sh over piped stdio prints no prompt.
const STAGE2_SCRIPT = `#!/bin/sh
mount -t proc proc /proc 2>/dev/null
mount -t sysfs sys /sys 2>/dev/null
mount -t devtmpfs dev /dev 2>/dev/null
mkdir -p /dev/pts
mount -t devpts devpts /dev/pts 2>/dev/null
umount -l /oldroot 2>/dev/null
mkdir -p /workspace
mount -t virtiofs workspace /workspace
[ -f /workspace/.harness/boot.sh ] && . /workspace/.harness/boot.sh
/usr/local/bin/guest-agent &
echo '[guest ready]'
exec /bin/sh
`;

// mach build relinks the helper with a plain ad-hoc signature, dropping the
// hypervisor entitlement, so re-sign unconditionally before each start.
async function signHelper(helperPath) {
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
}

/**
 * One micro-VM: rootfs + workspace + helper process + guest-agent
 * connection. The "default" session backs the legacy singleton facade and
 * about:harness tools; additional sessions (e.g. per conversation) get
 * ephemeral rootfs clones under profile/harness/sessions/<id>/ and are
 * removed on destroy(). States: stopped -> starting -> running -> stopping.
 */
export class HarnessSession {
  constructor({ id, baseDir, removable = false }) {
    this.id = id;
    this.removable = removable;
    this._baseDir = baseDir;
    this.state = "stopped";
    this.startedAtMs = null;
    this.agent = new HarnessAgent();
    this.proxy = null;
    this._proc = null;
    this._listeners = new Set();
    this._socketPath = null;
    this._proxySocketPath = null;
  }

  get rootfsPath() {
    return PathUtils.join(this._baseDir, "rootfs");
  }

  get workspacePath() {
    return PathUtils.join(this._baseDir, "workspace");
  }

  get pid() {
    return this._proc?.pid ?? null;
  }

  // Keep the socket path short: unix socket paths are capped at 104 bytes
  // on macOS, and profile paths can get close to that.
  get socketPath() {
    if (!this._socketPath) {
      const suffix = Services.uuid.generateUUID().toString().slice(1, 9);
      this._socketPath = PathUtils.join(
        Services.dirsvc.get("TmpD", Ci.nsIFile).path,
        `harness-${suffix}.sock`
      );
    }
    return this._socketPath;
  }

  info() {
    return {
      id: this.id,
      state: this.state,
      pid: this.pid,
      startedAtMs: this.startedAtMs,
      removable: this.removable,
      workspacePath: this.workspacePath,
    };
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

  _setState(state) {
    this.state = state;
    this._log(`state -> ${state}`);
    this._emit({ type: "state", state });
  }

  // Mirrored to the Browser Console and rendered as meta lines on the page.
  _log(message) {
    lazy.logConsole.log(`[${this.id}] ${message}`);
    this._emit({ type: "log", message });
  }

  // With the overlay (default), sessions boot the shared template directly:
  // the helper mounts it read-only host-side and the guest pivots onto a
  // tmpfs overlay, so no per-session rootfs copy exists and nothing the
  // guest writes outside /workspace survives a stop.
  get _overlayEnabled() {
    return Services.prefs.getBoolPref("browser.harness.rootfs.overlay", true);
  }

  async _ensureRootfs(template = rootfsTemplatePath()) {
    if (await IOUtils.exists(this.rootfsPath)) {
      // Guest rootfs state is disposable by design: when the template was
      // rebuilt (new baked-in tooling), replace the stale profile copy.
      const readStamp = async path => {
        try {
          return await IOUtils.readUTF8(PathUtils.join(path, ".rootfs-stamp"));
        } catch (e) {
          return "";
        }
      };
      const templateStamp = await readStamp(template);
      if (
        !templateStamp ||
        templateStamp == (await readStamp(this.rootfsPath))
      ) {
        return;
      }
      this._log("rootfs template changed; refreshing rootfs");
      await IOUtils.remove(this.rootfsPath, { recursive: true });
    }
    if (!(await IOUtils.exists(template))) {
      throw new Error(
        `Missing rootfs template at ${template}; run browser/components/harness/vm/setup-deps.sh`
      );
    }
    this._log(`copying rootfs template to ${this.rootfsPath}`);
    const start = Date.now();
    await IOUtils.makeDirectory(PathUtils.parent(this.rootfsPath), {
      createAncestors: true,
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
  }

  // The guest-agent is cross-compiled by setup-deps.sh into GreD/harness and
  // refreshed into the rootfs before each start so rebuilds take effect.
  async _installGuestAgent(rootPath) {
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
    const dest = PathUtils.join(rootPath, "usr", "local", "bin", "guest-agent");
    await IOUtils.makeDirectory(PathUtils.parent(dest), {
      createAncestors: true,
      ignoreExisting: true,
    });
    await IOUtils.copy(source, dest);
    await IOUtils.setPermissions(dest, 0o755);

    const libDir = PathUtils.join(rootPath, "usr", "local", "lib");
    await IOUtils.makeDirectory(libDir, {
      createAncestors: true,
      ignoreExisting: true,
    });
    for (const [leaf, content] of [
      ["harness-stage1.sh", STAGE1_SCRIPT],
      ["harness-stage2.sh", STAGE2_SCRIPT],
    ]) {
      const path = PathUtils.join(libDir, leaf);
      await IOUtils.writeUTF8(path, content);
      await IOUtils.setPermissions(path, 0o755);
    }
  }

  async start() {
    if (this.state != "stopped") {
      return;
    }
    this._setState("starting");
    try {
      const helper = appBinPath("harness-vm-helper");
      const libkrun = greBinPath("libkrun.dylib");
      // The GPL image bits (guest kernel + rootfs template) come from the
      // image manager: the objdir in development, a verified download in
      // the remote configuration (docs/image-download-plan.md).
      const image = await lazy.HarnessImageManager.resolve();
      const libkrunfw = image.kernelPath;
      for (const path of [helper, libkrun, libkrunfw, image.templatePath]) {
        if (!(await IOUtils.exists(path))) {
          throw new Error(
            `Missing ${path}; run ./mach build and browser/components/harness/vm/setup-deps.sh`
          );
        }
      }
      const overlay = this._overlayEnabled;
      let rootPath;
      if (overlay) {
        rootPath = image.templatePath;
      } else {
        await this._ensureRootfs(image.templatePath);
        rootPath = this.rootfsPath;
      }
      await this._installGuestAgent(rootPath);
      await signHelper(helper);
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
        rootPath,
        "--mem",
        "1024",
        "--cpus",
        "2",
        "--vsock",
        `1024:${this.socketPath}`,
        "--volume",
        `${this.workspacePath}:workspace`,
      ];
      if (overlay) {
        args.push("--root-ro");
      }
      // Gated egress: the guest's proxy forwarder reaches the policy proxy
      // in the parent through this vsock->unix mapping. With the pref off
      // (or an empty allowlist) the guest has no network path at all.
      if (Services.prefs.getBoolPref("browser.harness.proxy.enabled", true)) {
        const suffix = Services.uuid.generateUUID().toString().slice(1, 9);
        this._proxySocketPath = PathUtils.join(
          Services.dirsvc.get("TmpD", Ci.nsIFile).path,
          `harness-px-${suffix}.sock`
        );
        await IOUtils.remove(this._proxySocketPath, { ignoreAbsent: true });
        this.proxy = new lazy.HarnessProxy();
        this.proxy.listen(this._proxySocketPath);
        args.push("--vsock-out", `1025:${this._proxySocketPath}`);
      }

      // Dynamic boot bits (loopback, user volume mounts) go in a file the
      // static stage-2 script sources from the workspace: libkrun's exec
      // argv transport cannot carry nested quoting, so the boot command must
      // stay a bare script path.
      const bootLines = ["ifconfig lo 127.0.0.1 up 2>/dev/null"];
      for (const mount of HarnessVM.mounts) {
        if (!(await IOUtils.exists(mount.path))) {
          this._log(`skipping missing mount ${mount.path}`);
          continue;
        }
        args.push(
          "--volume",
          `${mount.path}:${mount.tag}${mount.readOnly ? ":ro" : ""}`
        );
        bootLines.push(
          `mkdir -p /mnt/${mount.tag} && mount ${
            mount.readOnly ? "-o ro " : ""
          }-t virtiofs ${mount.tag} /mnt/${mount.tag}`
        );
      }
      const bootDir = PathUtils.join(this.workspacePath, ".harness");
      await IOUtils.makeDirectory(bootDir, {
        createAncestors: true,
        ignoreExisting: true,
      });
      await IOUtils.writeUTF8(
        PathUtils.join(bootDir, "boot.sh"),
        `${bootLines.join("\n")}\n`
      );
      if (Services.prefs.getBoolPref("browser.harness.allownet", false)) {
        args.push("--allow-net");
      }
      if (Services.prefs.getBoolPref("browser.harness.verbose", true)) {
        args.push("--verbose");
      }
      args.push(
        "--",
        "/bin/sh",
        overlay ? "/usr/local/lib/harness-stage1.sh" : STAGE2_PATH
      );
      this._log(`spawning ${helper} ${args.join(" ")}`);
      const proc = await lazy.Subprocess.call({
        command: helper,
        arguments: args,
        stderr: "pipe",
      });
      this._proc = proc;
      this.startedAtMs = Date.now();
      this._log(`helper running with pid ${proc.pid}`);
      this._setState("running");
      this._readLoop(proc.stdout, "stdout");
      this._readLoop(proc.stderr, "stderr");
      proc.wait().then(({ exitCode }) => {
        this._proc = null;
        this.startedAtMs = null;
        this.agent.close();
        this.proxy?.stop();
        this.proxy = null;
        IOUtils.remove(this.socketPath, { ignoreAbsent: true });
        if (this._proxySocketPath) {
          IOUtils.remove(this._proxySocketPath, { ignoreAbsent: true });
          this._proxySocketPath = null;
        }
        this._socketPath = null;
        this._setState("stopped");
        this._emit({ type: "exit", exitCode });
      });
      this.agent.connect(this.socketPath).then(
        () => this._log("guest-agent connected"),
        e => this._log(`guest-agent connection failed: ${e.message}`)
      );
    } catch (e) {
      this._proc = null;
      this._setState("stopped");
      this._emit({ type: "error", message: e.message });
      throw e;
    }
  }

  async _readLoop(pipe, type) {
    try {
      let chunk;
      while ((chunk = await pipe.readString())) {
        this._emit({ type, data: chunk });
      }
    } catch (e) {
      // Pipe closed on VM exit.
    }
  }

  write(data) {
    if (this.state == "running" && this._proc) {
      this._proc.stdin.write(data);
    } else {
      this._log(`write ignored, VM is ${this.state}: ${data.trim()}`);
    }
  }

  async stop() {
    if (this.state != "running" || !this._proc) {
      return;
    }
    const exited = new Promise(resolve => {
      const listener = event => {
        if (event.type == "state" && event.state == "stopped") {
          this.removeListener(listener);
          resolve();
        }
      };
      this.addListener(listener);
    });
    this._setState("stopping");
    await this._proc.kill();
    await exited;
  }

  /** Stops the VM and removes its rootfs/workspace (non-default sessions). */
  async destroy() {
    await this.stop();
    HarnessVM._sessions.delete(this.id);
    if (this.removable) {
      await IOUtils.remove(this._baseDir, {
        recursive: true,
        ignoreAbsent: true,
      });
    }
  }

  exec(cmd, options) {
    return this.agent.exec(cmd, options);
  }

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
  }

  async resetRootfs() {
    if (this.state != "stopped") {
      throw new Error("Stop the VM before resetting the rootfs");
    }
    // With the overlay there is no per-session copy; guest changes are
    // already discarded on every stop.
    await IOUtils.remove(this.rootfsPath, {
      recursive: true,
      ignoreAbsent: true,
    });
  }
}

/**
 * Session registry plus a legacy facade over the "default" session (used by
 * about:harness tools and most tests).
 */
export const HarnessVM = {
  _sessions: new Map(),
  _swept: false,

  get sessionsDir() {
    return PathUtils.join(PathUtils.profileDir, "harness", "sessions");
  },

  session(id = "default") {
    if (id == "default" && !this._sessions.has(id)) {
      this._sessions.set(
        id,
        new HarnessSession({
          id,
          baseDir: PathUtils.join(PathUtils.profileDir, "harness"),
        })
      );
    }
    return this._sessions.get(id);
  },

  /**
   * Creates a new ephemeral session with its own rootfs clone and workspace
   * under profile/harness/sessions/<id>/. Caller starts and destroys it.
   */
  async createSession() {
    await this._sweepOnce();
    const id = Services.uuid.generateUUID().toString().slice(1, 9);
    const session = new HarnessSession({
      id,
      baseDir: PathUtils.join(this.sessionsDir, id),
      removable: true,
    });
    this._sessions.set(id, session);
    return session;
  },

  listSessions() {
    return [...this._sessions.values()].map(session => session.info());
  },

  // Helpers die with Firefox (guest console EOF ends the workload), so
  // reconciliation after a crash is just removing leftover session dirs.
  async _sweepOnce() {
    if (this._swept) {
      return;
    }
    this._swept = true;
    if (!(await IOUtils.exists(this.sessionsDir))) {
      return;
    }
    for (const child of await IOUtils.getChildren(this.sessionsDir)) {
      const leaf = PathUtils.filename(child);
      if (!this._sessions.has(leaf)) {
        lazy.logConsole.log(`sweeping orphaned session dir ${child}`);
        await IOUtils.remove(child, { recursive: true, ignoreAbsent: true });
      }
    }
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

  /* ---- legacy facade over the default session ---- */

  get state() {
    return this.session().state;
  },

  get rootfsPath() {
    return this.session().rootfsPath;
  },

  get workspacePath() {
    return this.session().workspacePath;
  },

  addListener(listener) {
    this.session().addListener(listener);
  },

  removeListener(listener) {
    this.session().removeListener(listener);
  },

  start() {
    return this.session().start();
  },

  stop() {
    return this.session().stop();
  },

  write(data) {
    this.session().write(data);
  },

  exec(cmd, options) {
    return this.session().exec(cmd, options);
  },

  snapshotPlacesToWorkspace() {
    return this.session().snapshotPlacesToWorkspace();
  },

  resetRootfs() {
    return this.session().resetRootfs();
  },
};
