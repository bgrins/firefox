/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

// MXC (Seatbelt host sandbox) backend spike: commands run on the host under
// a policy profile. See docs/mxc-spike.md.

const { MxcSession, mxcBinaryPath } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessMxc.sys.mjs"
);

add_task(async function test_mxc_backend() {
  if (!(await IOUtils.exists(mxcBinaryPath()))) {
    todo(false, "mxc not built; run browser/components/harness/vm/setup-mxc.sh");
    return;
  }
  const baseDir = PathUtils.join(PathUtils.profileDir, "mxc-test");
  const session = new MxcSession({ id: "mxctest", baseDir });
  registerCleanupFunction(() => session.destroy());

  await session.start();
  is(session.state, "running", "session starts without any boot");

  const echo = await session.exec("echo hello; echo err >&2; exit 3");
  is(echo.exitCode, 3, "exit code propagates");
  is(echo.stdout, "hello\n", "stdout captured");
  is(echo.stderr, "err\n", "stderr captured separately");

  const env = await session.exec("echo $MXC_VAR", {
    env: { MXC_VAR: "mxc-value" },
  });
  is(env.stdout.trim(), "mxc-value", "env vars reach the command");

  const stdin = await session.exec("cat", { stdin: "héllo wörld\n" });
  is(stdin.stdout, "héllo wörld\n", "stdin round-trips");

  // Workspace shared with the host, both directions.
  await IOUtils.writeUTF8(
    PathUtils.join(session.workspacePath, "from-host.txt"),
    "host-to-sandbox\n"
  );
  const read = await session.exec("cat from-host.txt");
  is(read.stdout, "host-to-sandbox\n", "host file visible in sandbox");
  await session.exec("echo sandbox-to-host > from-sandbox.txt");
  is(
    (
      await IOUtils.readUTF8(
        PathUtils.join(session.workspacePath, "from-sandbox.txt")
      )
    ).trim(),
    "sandbox-to-host",
    "sandbox write visible on host"
  );

  // Containment: writes outside the granted roots are denied...
  const escape = await session.exec(
    "touch /Users/mxc-escape-probe 2>&1; touch /tmp/mxc-escape-probe 2>&1; echo rc=$?"
  );
  ok(
    escape.stdout.includes("Operation not permitted"),
    `outside writes denied (${escape.stdout.trim().slice(0, 80)})`
  );
  // ...and so are reads of profile files outside the workspace grant.
  const prefsPath = PathUtils.join(PathUtils.profileDir, "prefs.js");
  const spy = await session.exec(`cat ${prefsPath} 2>&1; echo rc=$?`);
  ok(
    !spy.stdout.includes("user_pref") && spy.stdout.includes("rc="),
    "profile prefs are not readable"
  );

  // Network is blocked outright in the spike.
  const net = await session.exec(
    "curl -m 3 -s http://example.com >/dev/null 2>&1; echo rc=$?",
    { timeoutMs: 15000 }
  );
  isnot(net.stdout.trim(), "rc=0", "outbound network denied");

  // Interactive stdin via the agent op surface (what the bridge uses).
  const { requestId, result } = session.agent.execStart("cat", {
    interactive: true,
    timeoutMs: 15000,
  });
  await session.agent.request({
    op: "input",
    targetId: requestId,
    stdinB64: btoa("interactive-line\n"),
  });
  await session.agent.request({ op: "inputEof", targetId: requestId });
  const interactive = await result;
  is(interactive.stdout, "interactive-line\n", "interactive stdin works");

  // Places snapshot flows through the shared helper and is queryable with
  // the host sqlite3 from inside the sandbox.
  await session.snapshotPlacesToWorkspace();
  const query = await session.exec(
    "sqlite3 places.sqlite 'select count(*) from moz_places'"
  );
  is(query.exitCode, 0, `sandbox sqlite3 queries the snapshot`);
  ok(/^\d+$/.test(query.stdout.trim()), `row count (${query.stdout.trim()})`);

  is(
    session.toHostPath("/workspace/a/b.txt"),
    PathUtils.join(session.workspacePath, "a", "b.txt"),
    "guest-style paths map into the host workspace"
  );

  await session.stop();
  is(session.state, "stopped", "session stops");
});

add_task(async function test_backend_pref_selects_mxc() {
  const { HarnessVM } = ChromeUtils.importESModule(
    "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
  );
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.backend", "mxc"]],
  });
  HarnessVM._sessions.delete("default");
  ok(
    HarnessVM.session() instanceof MxcSession,
    "backend pref selects the mxc session"
  );
  is(
    HarnessVM.session().agent.workspaceRoot,
    HarnessVM.session().workspacePath,
    "bridge path root is the host workspace under mxc"
  );
  HarnessVM._sessions.delete("default");
  await SpecialPowers.popPrefEnv();
  HarnessVM._sessions.delete("default");
});
