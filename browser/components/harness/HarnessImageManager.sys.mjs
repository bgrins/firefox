/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  Subprocess: "resource://gre/modules/Subprocess.sys.mjs",
});

ChromeUtils.defineLazyGetter(lazy, "logConsole", () =>
  console.createInstance({
    prefix: "HarnessImageManager",
    maxLogLevelPref: "browser.harness.loglevel",
  })
);

/**
 * Resolves the sandbox image (guest kernel dylib + rootfs template) for
 * HarnessVM. See docs/image-download-plan.md: the GPL bits must never ship
 * in the installer, so production installs fetch them at runtime.
 *
 * Sources (pref browser.harness.image.source):
 *  - "build"  (default): artifacts from the objdir, installed by
 *    vm/setup-deps.sh — the development path.
 *  - "remote": a manifest (pref browser.harness.image.manifestUrl) lists
 *    version + files with sha256; artifacts are downloaded, verified, and
 *    installed under profile/harness/image/<version>/. Prototype plumbing
 *    for the eventual Remote Settings delivery: the manifest schema mirrors
 *    what an RS record would carry.
 *
 * Manifest schema:
 *   { "version": "1", "files": [
 *       { "name": "libkrunfw.5.dylib", "url": "...", "sha256": "...",
 *         "size": 31457280 },
 *       { "name": "rootfs-template.tar.gz", "url": "...", "sha256": "...",
 *         "size": 129499136, "extract": true }
 *   ] }
 * "size" is optional but recommended: it caps the download (a server
 * cannot stream forever) and gives progress a denominator.
 */

// Absolute ceiling for a single artifact when the manifest omits "size".
const MAX_DOWNLOAD_BYTES = 1024 * 1024 * 1024;
export const HarnessImageManager = {
  _listeners: new Set(),

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

  get source() {
    return Services.prefs.getStringPref(
      "browser.harness.image.source",
      "build"
    );
  },

  _buildPaths() {
    const kernel = Services.dirsvc.get("GreBinD", Ci.nsIFile);
    kernel.append("libkrunfw.5.dylib");
    const template = Services.dirsvc.get("GreD", Ci.nsIFile);
    template.append("harness");
    template.append("rootfs-template");
    return { kernelPath: kernel.path, templatePath: template.path };
  },

  _imageRoot() {
    return PathUtils.join(PathUtils.profileDir, "harness", "image");
  },

  // Version and artifact names become path components under the image root
  // (and old versions are recursively deleted), so both must be plain
  // filenames: no separators, no "." / ".." traversal.
  _validName(name) {
    return (
      typeof name == "string" &&
      /^[a-zA-Z0-9._-]+$/.test(name) &&
      name != "." &&
      name != ".."
    );
  },

  _resolving: null,

  /**
   * Returns { kernelPath, templatePath }, downloading and installing the
   * image first when the remote source is selected and not yet installed.
   * Concurrent callers (multiple VM sessions starting) share one install.
   */
  async resolve() {
    if (this.source != "remote") {
      return this._buildPaths();
    }
    if (!this._resolving) {
      this._resolving = this._resolveRemote().finally(() => {
        this._resolving = null;
      });
    }
    return this._resolving;
  },

  async _resolveRemote() {
    const url = Services.prefs.getStringPref(
      "browser.harness.image.manifestUrl",
      ""
    );
    if (!url) {
      throw new Error(
        "browser.harness.image.source is 'remote' but no manifestUrl is set"
      );
    }
    // Config and security errors fail closed; only network failures below
    // are eligible for the installed-image fallback.
    this._checkScheme(url);
    let manifest;
    try {
      manifest = await this._fetchManifest(url);
    } catch (e) {
      // Offline (or manifest host down) must not brick a machine with a
      // valid installed image; fall back to the newest complete install.
      const installed = await this._newestInstalled();
      if (installed) {
        lazy.logConsole.warn(
          `manifest fetch failed (${e.message}); using installed image`
        );
        this._emit({
          type: "imageProgress",
          message: "image update check failed; using the installed image",
        });
        return installed;
      }
      this._emit({
        type: "imageProgress",
        message: `image download failed: ${e.message}`,
        error: true,
      });
      throw e;
    }
    // A manifest that fetched fine but fails validation is a red flag, not
    // an outage: fail closed rather than silently using the old image.
    if (!manifest.version || !Array.isArray(manifest.files)) {
      throw new Error("malformed image manifest");
    }
    if (!this._validName(manifest.version)) {
      throw new Error(`invalid image version: ${manifest.version}`);
    }
    const installDir = PathUtils.join(this._imageRoot(), manifest.version);
    const completeMarker = PathUtils.join(installDir, ".complete");
    if (!(await IOUtils.exists(completeMarker))) {
      try {
        await this._install(manifest, installDir);
      } catch (e) {
        this._emit({
          type: "imageProgress",
          message: `image install failed: ${e.message}`,
          error: true,
        });
        throw e;
      }
      await IOUtils.writeUTF8(completeMarker, new Date().toISOString());
      await this._sweepOldVersions(manifest.version);
    }
    return {
      kernelPath: PathUtils.join(installDir, "libkrunfw.5.dylib"),
      templatePath: PathUtils.join(installDir, "rootfs-template"),
    };
  },

  async _newestInstalled() {
    let children;
    try {
      children = await IOUtils.getChildren(this._imageRoot());
    } catch (e) {
      return null;
    }
    let best = null;
    for (const child of children) {
      try {
        const stat = await IOUtils.stat(PathUtils.join(child, ".complete"));
        if (!best || stat.lastModified > best.mtime) {
          best = { dir: child, mtime: stat.lastModified };
        }
      } catch (e) {
        // No marker: incomplete install or a stray .tmp dir.
      }
    }
    if (!best) {
      return null;
    }
    return {
      kernelPath: PathUtils.join(best.dir, "libkrunfw.5.dylib"),
      templatePath: PathUtils.join(best.dir, "rootfs-template"),
    };
  },

  async _fetchManifest(url) {
    const response = await fetch(url, { credentials: "omit" });
    if (!response.ok) {
      throw new Error(`image manifest fetch failed (${response.status})`);
    }
    return response.json();
  },

  async _install(manifest, installDir) {
    lazy.logConsole.log(`installing image ${manifest.version}`);
    // Stage into a temp dir and rename so a torn install never looks valid.
    const stageDir = `${installDir}.tmp`;
    await IOUtils.remove(stageDir, { recursive: true, ignoreAbsent: true });
    await IOUtils.makeDirectory(stageDir, { createAncestors: true });
    try {
      for (const file of manifest.files) {
        if (!this._validName(file.name)) {
          throw new Error(`invalid artifact name: ${file.name}`);
        }
        const target = PathUtils.join(stageDir, file.name);
        await this._download(file, target);
        const digest = await IOUtils.computeHexDigest(target, "sha256");
        if (digest != file.sha256) {
          throw new Error(
            `sha256 mismatch for ${file.name}: ${digest} != ${file.sha256}`
          );
        }
        if (file.extract) {
          this._emit({
            type: "imageProgress",
            message: `unpacking ${file.name}`,
          });
          const tar = await lazy.Subprocess.call({
            command: "/usr/bin/tar",
            arguments: ["-xzf", target, "-C", stageDir],
            stderr: "pipe",
          });
          const { exitCode } = await tar.wait();
          if (exitCode !== 0) {
            throw new Error(`extracting ${file.name} failed (${exitCode})`);
          }
          await IOUtils.remove(target);
        }
      }
      await IOUtils.remove(installDir, { recursive: true, ignoreAbsent: true });
      await IOUtils.move(stageDir, installDir);
      this._emit({ type: "imageProgress", message: "sandbox image installed" });
    } catch (e) {
      await IOUtils.remove(stageDir, { recursive: true, ignoreAbsent: true });
      throw e;
    }
  },

  // The payload includes a dylib the VM helper dlopens, so plain http is
  // native-code-execution-via-MITM; require https outside of tests.
  _checkScheme(url) {
    if (
      !url.startsWith("https://") &&
      !Services.prefs.getBoolPref("browser.harness.image.allowInsecure", false)
    ) {
      throw new Error(`image URLs must be https: ${url}`);
    }
  },

  async _download(file, target) {
    lazy.logConsole.log(`downloading ${file.url}`);
    this._checkScheme(file.url);
    const response = await fetch(file.url, { credentials: "omit" });
    if (!response.ok) {
      throw new Error(`download of ${file.name} failed (${response.status})`);
    }
    const declared = Number(file.size) || 0;
    const maxBytes = declared || MAX_DOWNLOAD_BYTES;
    const total = declared || Number(response.headers.get("Content-Length"));
    const reader = response.body.getReader();
    // Streamed to disk chunk by chunk: artifacts are hundreds of MB and
    // must never be buffered whole in the parent process.
    await IOUtils.remove(target, { ignoreAbsent: true });
    let received = 0;
    let lastReport = 0;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      received += value.byteLength;
      if (received > maxBytes) {
        await reader.cancel();
        throw new Error(
          `download of ${file.name} exceeded ${maxBytes} bytes` +
            (declared ? " (manifest size)" : "")
        );
      }
      await IOUtils.write(target, value, { mode: "appendOrCreate" });
      // Throttled progress: at most one event per 5% (or per chunk when the
      // total is unknown and crosses 8 MiB boundaries).
      const milestone = total
        ? Math.floor((received / total) * 20)
        : Math.floor(received / (8 * 1024 * 1024));
      if (milestone != lastReport) {
        lastReport = milestone;
        this._emit({
          type: "imageProgress",
          message: total
            ? `downloading ${file.name}: ${Math.floor((received / total) * 100)}%`
            : `downloading ${file.name}: ${Math.floor(received / (1024 * 1024))} MB`,
        });
      }
    }
    if (!received) {
      // A zero-length body never hit the write loop; still create the file
      // so the hash check reports a mismatch rather than a stat error.
      await IOUtils.write(target, new Uint8Array(0));
    }
  },

  async _sweepOldVersions(currentVersion) {
    const root = this._imageRoot();
    let children;
    try {
      children = await IOUtils.getChildren(root);
    } catch (e) {
      return;
    }
    for (const child of children) {
      if (PathUtils.filename(child) != currentVersion) {
        lazy.logConsole.log(`removing old image ${child}`);
        await IOUtils.remove(child, { recursive: true, ignoreAbsent: true });
      }
    }
  },
};
