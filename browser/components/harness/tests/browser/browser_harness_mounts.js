/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { CodexExecBridge } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/CodexExecBridge.sys.mjs"
);

function b64(text) {
  return btoa(String.fromCharCode(...new TextEncoder().encode(text)));
}

add_task(async function test_user_volume_mounts() {
  if (!(await vmDepsPresent())) {
    todo(false, "harness VM deps not present; run setup-deps.sh");
    return;
  }
  for (let i = 0; HarnessVM.state != "stopped" && i < 60; i++) {
    // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  const base = PathUtils.join(PathUtils.profileDir, "mount-test");
  const rwDir = PathUtils.join(base, "rw");
  const roDir = PathUtils.join(base, "ro");
  for (const dir of [rwDir, roDir]) {
    await IOUtils.makeDirectory(dir, { createAncestors: true });
  }
  await IOUtils.writeUTF8(PathUtils.join(rwDir, "hello.txt"), "from-rw\n");
  await IOUtils.writeUTF8(PathUtils.join(roDir, "ref.txt"), "from-ro\n");

  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.enabled", true],
      [
        "browser.harness.mounts",
        JSON.stringify([
          { path: rwDir, tag: "data", readOnly: false },
          { path: roDir, tag: "refdata", readOnly: true },
          { path: roDir, tag: "BAD TAG!", readOnly: true },
        ]),
      ],
    ],
  });
  is(HarnessVM.mounts.length, 2, "invalid tags are filtered out");

  registerCleanupFunction(() => {
    CodexExecBridge.stop();
  });

  await startVM();

  // Host -> guest, both mounts.
  const readRw = await HarnessVM.exec("cat /mnt/data/hello.txt");
  is(readRw.stdout, "from-rw\n", "rw mount readable in guest");
  const readRo = await HarnessVM.exec("cat /mnt/refdata/ref.txt");
  is(readRo.stdout, "from-ro\n", "ro mount readable in guest");

  // Guest -> host on the rw mount.
  await HarnessVM.exec("echo guest-write > /mnt/data/from-guest.txt");
  is(
    (await IOUtils.readUTF8(PathUtils.join(rwDir, "from-guest.txt"))).trim(),
    "guest-write",
    "guest write to rw mount lands on the host"
  );

  // Writes to the ro mount fail, including after a remount attempt
  // (host-side virtio-fs read_only + seatbelt back the guest -o ro).
  const write = await HarnessVM.exec("touch /mnt/refdata/nope 2>&1");
  Assert.notStrictEqual(write.exitCode, 0, "write to ro mount fails");
  const remount = await HarnessVM.exec(
    "mount -o remount,rw /mnt/refdata 2>/dev/null; touch /mnt/refdata/nope2 2>&1"
  );
  Assert.notStrictEqual(
    remount.exitCode,
    0,
    "write still fails after remount attempt"
  );
  ok(
    !(await IOUtils.exists(PathUtils.join(roDir, "nope"))) &&
      !(await IOUtils.exists(PathUtils.join(roDir, "nope2"))),
    "no files appeared in the ro folder on the host"
  );

  // Exec-bridge path policy mirrors the mount permissions.
  const readViaBridge = await CodexExecBridge._handle("fs/readFile", {
    path: "file:///mnt/refdata/ref.txt",
  });
  ok(readViaBridge.dataBase64, "bridge can read from ro mount");
  await CodexExecBridge._handle("fs/writeFile", {
    path: "file:///mnt/data/bridge.txt",
    dataBase64: b64("via-bridge\n"),
  });
  is(
    await IOUtils.readUTF8(PathUtils.join(rwDir, "bridge.txt")),
    "via-bridge\n",
    "bridge write to rw mount lands on the host"
  );
  await Assert.rejects(
    CodexExecBridge._handle("fs/writeFile", {
      path: "file:///mnt/refdata/x",
      dataBase64: b64("x"),
    }),
    /read-only/,
    "bridge denies writes to ro mounts"
  );
  await Assert.rejects(
    CodexExecBridge._handle("fs/readFile", {
      path: "file:///mnt/other/x",
    }),
    /denied/,
    "bridge denies unknown mount roots"
  );

  await stopVM();
});
