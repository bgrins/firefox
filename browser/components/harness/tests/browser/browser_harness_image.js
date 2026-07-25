/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// HarnessImageManager: "remote" source downloads manifest-listed artifacts,
// verifies sha256, installs to profile/harness/image/<version>/, and caches.

const { HarnessImageManager } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessImageManager.sys.mjs"
);
const { HttpServer } = ChromeUtils.importESModule(
  "resource://testing-common/httpd.sys.mjs"
);

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), b =>
    b.toString(16).padStart(2, "0")
  ).join("");
}

add_task(async function test_image_manager_remote() {
  // A fake kernel plus a tarball holding a one-file rootfs template.
  const kernelBytes = new TextEncoder().encode("fake-kernel-dylib");
  const templateDir = PathUtils.join(PathUtils.profileDir, "image-src");
  await IOUtils.makeDirectory(
    PathUtils.join(templateDir, "rootfs-template", "etc"),
    { createAncestors: true }
  );
  await IOUtils.writeUTF8(
    PathUtils.join(templateDir, "rootfs-template", "etc", "os-release"),
    "NAME=FakeAlpine"
  );
  const tarPath = PathUtils.join(
    PathUtils.profileDir,
    "rootfs-template.tar.gz"
  );
  const tar = await (
    await import("resource://gre/modules/Subprocess.sys.mjs")
  ).Subprocess.call({
    command: "/usr/bin/tar",
    arguments: ["-czf", tarPath, "-C", templateDir, "rootfs-template"],
  });
  is((await tar.wait()).exitCode, 0, "test tarball created");
  const tarBytes = await IOUtils.read(tarPath);

  let downloads = 0;
  const server = new HttpServer();
  server.registerPathHandler("/kernel", (request, response) => {
    downloads++;
    response.setHeader("Content-Type", "application/octet-stream");
    const stream = response.bodyOutputStream;
    const data = String.fromCharCode(...kernelBytes);
    stream.write(data, data.length);
  });
  server.registerPathHandler("/rootfs", (request, response) => {
    downloads++;
    response.setHeader("Content-Type", "application/octet-stream");
    const data = String.fromCharCode(...tarBytes);
    response.bodyOutputStream.write(data, data.length);
  });
  const manifest = {
    version: "42",
    files: [
      {
        name: "libkrunfw.5.dylib",
        url: "",
        sha256: await sha256Hex(kernelBytes),
      },
      {
        name: "rootfs-template.tar.gz",
        url: "",
        sha256: await sha256Hex(tarBytes),
        extract: true,
      },
    ],
  };
  server.registerPathHandler("/manifest.json", (request, response) => {
    response.setHeader("Content-Type", "application/json");
    const body = JSON.stringify(manifest);
    response.bodyOutputStream.write(body, body.length);
  });
  server.start(-1);
  const base = `http://localhost:${server.identity.primaryPort}`;
  manifest.files[0].url = `${base}/kernel`;
  manifest.files[1].url = `${base}/rootfs`;
  registerCleanupFunction(() => new Promise(resolve => server.stop(resolve)));

  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.image.source", "remote"],
      ["browser.harness.image.manifestUrl", `${base}/manifest.json`],
    ],
  });

  const progress = [];
  const listener = event => progress.push(event.message);
  HarnessImageManager.addListener(listener);
  registerCleanupFunction(() => HarnessImageManager.removeListener(listener));

  const image = await HarnessImageManager.resolve();
  ok(
    image.kernelPath.includes("harness/image/42"),
    "kernel installed under versioned dir"
  );
  is(
    await IOUtils.readUTF8(image.kernelPath),
    "fake-kernel-dylib",
    "kernel bytes verified and installed"
  );
  is(
    await IOUtils.readUTF8(
      PathUtils.join(image.templatePath, "etc", "os-release")
    ),
    "NAME=FakeAlpine",
    "rootfs template extracted"
  );
  is(downloads, 2, "both artifacts downloaded");
  ok(progress.length, `progress events emitted (${progress.length})`);

  // Second resolve: cached, no re-download.
  await HarnessImageManager.resolve();
  is(downloads, 2, "cached image is not re-downloaded");

  // Corrupt manifest hash: install must fail and leave no valid image.
  manifest.version = "43";
  manifest.files[0].sha256 = "0".repeat(64);
  await Assert.rejects(
    HarnessImageManager.resolve(),
    /sha256 mismatch/,
    "hash mismatch rejects the install"
  );
  ok(
    !(await IOUtils.exists(
      PathUtils.join(PathUtils.profileDir, "harness", "image", "43")
    )),
    "torn install leaves no versioned dir"
  );

  // Build source still resolves to objdir paths.
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.image.source", "build"]],
  });
  const build = await HarnessImageManager.resolve();
  ok(
    build.kernelPath.endsWith("libkrunfw.5.dylib") &&
      !build.kernelPath.includes("harness/image"),
    "build source uses objdir artifacts"
  );
});
