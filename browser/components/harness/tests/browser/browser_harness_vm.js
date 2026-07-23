/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);

function greBinPath(leaf) {
  const file = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

async function depsAvailable() {
  const greD = Services.dirsvc.get("GreD", Ci.nsIFile);
  greD.append("harness");
  const paths = [
    greBinPath("libkrun.dylib"),
    greBinPath("libkrunfw.5.dylib"),
    PathUtils.join(greD.path, "rootfs-template"),
    PathUtils.join(greD.path, "guest-agent"),
  ];
  for (const path of paths) {
    if (!(await IOUtils.exists(path))) {
      info(`missing ${path}`);
      return false;
    }
  }
  return true;
}

function waitForState(state) {
  return new Promise(resolve => {
    const listener = event => {
      if (event.type == "state" && event.state == state) {
        HarnessVM.removeListener(listener);
        resolve();
      }
    };
    HarnessVM.addListener(listener);
  });
}

// The agent connects shortly after boot; retry until the vsock channel is up.
async function execWithRetry(cmd, options) {
  for (let attempt = 0; ; attempt++) {
    try {
      return await HarnessVM.exec(cmd, options);
    } catch (e) {
      if (attempt >= 40) {
        throw e;
      }
      // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
      await new Promise(resolve => setTimeout(resolve, 250));
    }
  }
}

add_task(async function test_harness_vm_smoke() {
  requestLongerTimeout(3);
  // Earlier tests in the suite may still be tearing their VM down.
  for (let i = 0; HarnessVM.state != "stopped" && i < 60; i++) {
    // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  if (AppConstants.platform != "macosx") {
    ok(true, "harness VM is macOS-only");
    return;
  }
  if (!(await depsAvailable())) {
    todo(
      false,
      "harness VM deps not present; run browser/components/harness/vm/setup-deps.sh"
    );
    return;
  }

  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });

  registerCleanupFunction(async () => {
    if (HarnessVM.state == "running") {
      const stopped = waitForState("stopped");
      await HarnessVM.stop();
      await stopped;
    }
  });

  const running = waitForState("running");
  await HarnessVM.start();
  await running;
  is(HarnessVM.state, "running", "VM reaches running state");

  const uname = await execWithRetry("uname -sm");
  is(uname.exitCode, 0, "uname exits 0");
  is(uname.stdout.trim(), "Linux aarch64", "guest is aarch64 Linux");

  const env = await HarnessVM.exec("echo $SMOKE_VAR", {
    env: { SMOKE_VAR: "smoke-value" },
  });
  is(env.stdout.trim(), "smoke-value", "env vars reach the guest command");

  const stdin = await HarnessVM.exec("cat", { stdin: "héllo wörld\n" });
  is(stdin.stdout, "héllo wörld\n", "stdin round-trips byte-exact");

  const failing = await HarnessVM.exec("echo out; echo err >&2; exit 3");
  is(failing.exitCode, 3, "exit code is reported");
  is(failing.stdout, "out\n", "stdout is captured");
  is(failing.stderr, "err\n", "stderr is captured separately");

  const chunks = [];
  const streamed = await HarnessVM.exec("echo one; sleep 1; echo two", {
    onOutput: (stream, text) => chunks.push(text.trim()),
  });
  is(streamed.stdout, "one\ntwo\n", "streamed output accumulates");
  Assert.greaterOrEqual(chunks.length, 2, "output arrived in multiple chunks");

  const net = await HarnessVM.exec(
    "wget -T 2 -q -O- http://example.com; echo rc=$?"
  );
  ok(net.stdout.includes("rc=1"), "guest has no network access by default");

  const hostFile = PathUtils.join(HarnessVM.workspacePath, "from-host.txt");
  await IOUtils.writeUTF8(hostFile, "host-to-guest\n");
  const catHost = await HarnessVM.exec("cat /workspace/from-host.txt");
  is(catHost.stdout, "host-to-guest\n", "host file visible in guest");

  await HarnessVM.exec("echo guest-to-host > /workspace/from-guest.txt");
  const guestFile = PathUtils.join(HarnessVM.workspacePath, "from-guest.txt");
  is(
    (await IOUtils.readUTF8(guestFile)).trim(),
    "guest-to-host",
    "guest write visible on host"
  );

  const tools = await HarnessVM.exec(
    "node -v && jq --version && rg --version >/dev/null && yq --version && " +
      "uv --version && magick -version >/dev/null && echo tools-ok",
    { timeoutMs: 30000 }
  );
  is(tools.exitCode, 0, `dev tooling present (${tools.stderr.slice(0, 80)})`);
  ok(tools.stdout.includes("tools-ok"), "all tool version checks ran");

  // uv must find the baked-in CPython without network access.
  const py = await HarnessVM.exec(
    "uv run --no-project python3 -c 'print(40 + 2)'",
    { timeoutMs: 60000 }
  );
  is(py.exitCode, 0, `uv run python works offline (${py.stderr.slice(0, 80)})`);
  ok(py.stdout.includes("42"), "python executed via uv");

  const guestPlaces = await HarnessVM.snapshotPlacesToWorkspace();
  const query = await HarnessVM.exec(
    `sqlite3 ${guestPlaces} 'select count(*) from moz_places'`
  );
  is(query.exitCode, 0, "guest sqlite3 queries the places snapshot");
  ok(/^\d+$/.test(query.stdout.trim()), `row count (${query.stdout.trim()})`);

  const stopped = waitForState("stopped");
  await HarnessVM.stop();
  await stopped;
  is(HarnessVM.state, "stopped", "VM stops cleanly");
});
