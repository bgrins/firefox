/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);
const { CodexAppServerClient } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs"
);
const { CodexExecBridge } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/CodexExecBridge.sys.mjs"
);
const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);

function greBinPath(leaf) {
  const file = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  file.append(leaf);
  return file.path;
}

async function ollamaAvailable() {
  try {
    const response = await fetch("http://127.0.0.1:11434/api/version", {
      signal: AbortSignal.timeout(2000),
    });
    return response.ok;
  } catch (e) {
    return false;
  }
}

// Deterministic coverage of the approval plumbing: server request in,
// approvalRequest event out, respondToApproval resolves the reply promise.
add_task(async function test_approval_plumbing() {
  const events = [];
  const listener = event => events.push(event);
  AgentService.addListener(listener);
  registerCleanupFunction(() => AgentService.removeListener(listener));

  // Unknown server->client requests stay fail-closed.
  await Assert.rejects(
    Promise.resolve().then(() =>
      AgentService._onServerRequest({ id: 1, method: "process/spawn" })
    ),
    /not permitted/,
    "non-approval server requests are rejected"
  );

  // Known approval requests surface as events and resolve with the decision.
  const acceptPromise = AgentService._onServerRequest({
    id: 2,
    method: "item/commandExecution/requestApproval",
    params: { threadId: "t1", item: { command: "rm -rf /" } },
  });
  const event = events.find(e => e.type == "approvalRequest");
  ok(event, "approvalRequest event emitted");
  is(event.requestId, 2, "event carries the request id");
  AgentService.respondToApproval(2, "accept");
  Assert.deepEqual(
    await acceptPromise,
    { decision: "accept" },
    "reply resolves with the chosen decision"
  );

  const declinePromise = AgentService._onServerRequest({
    id: 3,
    method: "item/fileChange/requestApproval",
    params: {},
  });
  AgentService.respondToApproval(3, "decline");
  Assert.deepEqual(
    await declinePromise,
    { decision: "decline" },
    "decline resolves too"
  );

  AgentService.respondToApproval(999, "accept");
  ok(true, "responding to an unknown request id is a no-op");
});

// Live flow: approvalPolicy "untrusted" makes Codex request approval before
// running a command in the VM environment; accepting lets it execute through
// the exec bridge.
add_task(async function test_approval_live_roundtrip() {
  if (
    !(await IOUtils.exists(CodexAppServerClient.defaultBinaryPath())) ||
    !(await IOUtils.exists(greBinPath("libkrun.dylib")))
  ) {
    todo(false, "codex binary or VM deps not present; run setup scripts");
    return;
  }
  if (!(await ollamaAvailable())) {
    todo(false, "ollama not running; skipped live approval turn");
    return;
  }

  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  registerCleanupFunction(async () => {
    await AgentService.shutdown();
    if (HarnessVM.state == "running") {
      await HarnessVM.stop();
    }
  });

  const running = new Promise(resolve => {
    const listener = event => {
      if (event.type == "state" && event.state == "running") {
        HarnessVM.removeListener(listener);
        resolve();
      }
    };
    HarnessVM.addListener(listener);
  });
  await HarnessVM.start();
  await running;
  for (let i = 0; ; i++) {
    try {
      await HarnessVM.exec("true");
      break;
    } catch (e) {
      if (i > 40) {
        throw e;
      }
      // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
      await new Promise(resolve => setTimeout(resolve, 250));
    }
  }

  const approvals = [];
  const items = [];
  let turnCompleted;
  const completed = new Promise(resolve => {
    turnCompleted = resolve;
  });
  const listener = event => {
    if (event.type == "approvalRequest") {
      approvals.push(event);
      AgentService.respondToApproval(event.requestId, "accept");
    } else if (event.type == "item" && event.item.type == "commandExecution") {
      items.push(event);
    } else if (event.type == "turnCompleted") {
      turnCompleted(event);
    }
  };
  AgentService.addListener(listener);
  registerCleanupFunction(() => AgentService.removeListener(listener));

  const conversation = await AgentService.createConversation({
    approvalPolicy: "untrusted",
  });
  await AgentService.sendMessage(
    conversation.conversationId,
    "Run a shell command that creates a file named approved.txt containing" +
      " the word yes in your working directory."
  );
  await completed;

  Assert.greater(approvals.length, 0, "Codex requested approval");
  ok(
    approvals[0].params?.command,
    `approval request describes the command (${approvals[0].params?.command})`
  );
  const done = items.find(
    e => e.phase == "completed" && e.item.status == "completed"
  );
  ok(done, "approved command completed");
  is(done.item.exitCode, 0, "command exit code 0");
  ok(
    CodexExecBridge.auditLog.some(e => e.method == "process/start"),
    "command routed through the exec bridge into the VM"
  );
});
