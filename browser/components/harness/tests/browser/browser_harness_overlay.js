/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// With browser.harness.rootfs.overlay (the default), the VM boots the
// shared rootfs template read-only (host-enforced) and pivots onto a tmpfs
// overlay: guest writes outside /workspace succeed but are ephemeral, and
// the template on the host never changes.

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);

function templatePath() {
  const file = Services.dirsvc.get("GreD", Ci.nsIFile);
  file.append("harness");
  file.append("rootfs-template");
  return file.path;
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

add_task(async function test_overlay_rootfs() {
  requestLongerTimeout(3);
  const greBinD = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  greBinD.append("libkrun.dylib");
  if (
    !(await IOUtils.exists(greBinD.path)) ||
    !(await IOUtils.exists(templatePath()))
  ) {
    todo(false, "VM deps not present; run setup scripts");
    return;
  }
  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.enabled", true],
      ["browser.harness.rootfs.overlay", true],
    ],
  });
  registerCleanupFunction(async () => {
    if (HarnessVM.state == "running") {
      const stopped = waitForState("stopped");
      await HarnessVM.stop();
      await stopped;
    }
  });

  async function waitForAgent() {
    for (let i = 0; ; i++) {
      try {
        await HarnessVM.exec("true");
        return;
      } catch (e) {
        if (i > 40) {
          throw e;
        }
        // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
        await new Promise(resolve => setTimeout(resolve, 250));
      }
    }
  }

  let running = waitForState("running");
  await HarnessVM.start();
  await running;
  await waitForAgent();

  // Writes outside /workspace succeed (the overlay absorbs them)...
  const write = await HarnessVM.exec(
    "echo ephemeral > /usr/local/bin/overlay-marker && " +
      "echo persistent > /workspace/overlay-marker && " +
      "cat /usr/local/bin/overlay-marker"
  );
  is(write.exitCode, 0, `guest writes succeed (${write.stderr.slice(0, 60)})`);
  ok(write.stdout.includes("ephemeral"), "overlay write readable in guest");

  // ...but never reach the host template.
  ok(
    !(await IOUtils.exists(
      PathUtils.join(templatePath(), "usr", "local", "bin", "overlay-marker")
    )),
    "host template untouched"
  );

  // PTYs still work on the pivoted root (devpts is re-mounted).
  const tty = await HarnessVM.exec("test -t 0 && echo is-tty", {
    tty: true,
    timeoutMs: 30000,
  });
  ok(tty.stdout.includes("is-tty"), "pty works under the overlay");

  // Restart: overlay contents vanish, workspace persists.
  let stopped = waitForState("stopped");
  await HarnessVM.stop();
  await stopped;

  running = waitForState("running");
  await HarnessVM.start();
  await running;
  await waitForAgent();

  const check = await HarnessVM.exec(
    "test -f /usr/local/bin/overlay-marker && echo leaked; " +
      "cat /workspace/overlay-marker"
  );
  ok(!check.stdout.includes("leaked"), "overlay contents ephemeral");
  ok(check.stdout.includes("persistent"), "workspace persists");

  // Regression: concurrent large requests must not corrupt the vsock JSONL
  // stream (short writes on the non-blocking socket used to truncate
  // frames; observed as heredoc file writes silently failing mid-session).
  const payload = "y".repeat(32 * 1024);
  const results = await Promise.all(
    Array.from({ length: 12 }, (_, index) =>
      HarnessVM.exec(`printf '%s' '${payload}' | wc -c && echo job-${index}`, {
        timeoutMs: 60000,
      })
    )
  );
  for (const [index, result] of results.entries()) {
    is(result.exitCode, 0, `concurrent job ${index} succeeded`);
    ok(
      result.stdout.includes("32768") && result.stdout.includes(`job-${index}`),
      `concurrent job ${index} output intact`
    );
  }

  stopped = waitForState("stopped");
  await HarnessVM.stop();
  await stopped;
});
