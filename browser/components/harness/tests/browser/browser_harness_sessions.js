/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);
const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);
const { CodexAppServerClient } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs"
);

function greBinPath(leaf) {
  const file = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

async function awaitAgent(session) {
  for (let i = 0; ; i++) {
    try {
      await session.exec("true");
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

add_task(async function test_sessions_are_isolated() {
  requestLongerTimeout(3);
  if (!(await IOUtils.exists(greBinPath("libkrun.dylib")))) {
    todo(false, "harness VM deps not present; run setup-deps.sh");
    return;
  }
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });

  const first = await HarnessVM.createSession();
  const second = await HarnessVM.createSession();
  registerCleanupFunction(async () => {
    for (const session of [first, second]) {
      await session.destroy().catch(() => {});
    }
  });

  await first.start();
  await second.start();
  await awaitAgent(first);
  await awaitAgent(second);

  const infos = HarnessVM.listSessions();
  Assert.greaterOrEqual(infos.length, 2, "both sessions listed");
  Assert.greaterOrEqual(
    infos.filter(info => info.state == "running").length,
    2,
    "both sessions running"
  );

  // Rootfs and workspace are isolated between sessions.
  await first.exec(
    "echo one > /root/marker.txt && echo one > /workspace/w.txt"
  );
  const rootfsCheck = await second.exec("cat /root/marker.txt 2>&1");
  Assert.notStrictEqual(
    rootfsCheck.exitCode,
    0,
    "rootfs write in one session is invisible in the other"
  );
  const workspaceCheck = await second.exec("cat /workspace/w.txt 2>&1");
  Assert.notStrictEqual(
    workspaceCheck.exitCode,
    0,
    "workspaces are per-session"
  );
  ok(
    await IOUtils.exists(PathUtils.join(first.workspacePath, "w.txt")),
    "session workspace mirrors to its own host dir"
  );

  // destroy() stops the VM and removes the session directory.
  const firstBase = PathUtils.parent(first.workspacePath);
  await first.destroy();
  is(first.state, "stopped", "destroyed session stopped");
  ok(!(await IOUtils.exists(firstBase)), "session dir removed on destroy");
  ok(
    !HarnessVM.listSessions().some(info => info.id == first.id),
    "destroyed session no longer listed"
  );

  await second.destroy();
});

add_task(async function test_session_per_conversation() {
  requestLongerTimeout(3);
  if (
    !(await IOUtils.exists(greBinPath("libkrun.dylib"))) ||
    !(await IOUtils.exists(CodexAppServerClient.defaultBinaryPath()))
  ) {
    todo(false, "VM deps or codex binary not present; run setup scripts");
    return;
  }
  await SpecialPowers.pushPrefEnv({
    set: [
      ["browser.harness.enabled", true],
      ["browser.harness.sessionPerConversation", true],
    ],
  });
  registerCleanupFunction(() => AgentService.shutdown());

  const before = HarnessVM.listSessions().length;
  const conversationA = await AgentService.createConversation();
  const conversationB = await AgentService.createConversation();
  ok(conversationA.conversationId && conversationB.conversationId, "created");

  const sessions = HarnessVM.listSessions();
  Assert.greaterOrEqual(
    sessions.length,
    before + 2,
    "each conversation got its own session"
  );
  const recordA = AgentService._conversations.get(conversationA.conversationId);
  const recordB = AgentService._conversations.get(conversationB.conversationId);
  ok(recordA.session && recordB.session, "conversations own sessions");
  Assert.notStrictEqual(
    recordA.session.id,
    recordB.session.id,
    "sessions are distinct"
  );
  Assert.notEqual(
    recordA.bridge.url,
    recordB.bridge.url,
    "each conversation has its own exec bridge"
  );

  const sessionDirs = [recordA, recordB].map(record =>
    PathUtils.parent(record.session.workspacePath)
  );
  await AgentService.shutdown();
  for (const dir of sessionDirs) {
    ok(!(await IOUtils.exists(dir)), `session dir cleaned up (${dir})`);
  }
});
