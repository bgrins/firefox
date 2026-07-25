/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// With browser.harness.rootfs.overlay (the default), the VM boots the
// shared rootfs template read-only (host-enforced) and pivots onto a tmpfs
// overlay: guest writes outside /workspace succeed but are ephemeral, and
// the template on the host never changes.

function templatePath() {
  const file = Services.dirsvc.get("GreD", Ci.nsIFile);
  file.append("harness");
  file.append("rootfs-template");
  return file.path;
}

add_task(async function test_overlay_rootfs() {
  if (!(await vmDepsPresent()) || !(await IOUtils.exists(templatePath()))) {
    todo(false, "VM deps not present; run setup scripts");
    return;
  }
  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.enabled", true],
      ["browser.harness.rootfs.overlay", true],
    ],
  });
  await startVM();

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
  await stopVM();
  await startVM();

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

  await stopVM();
});
