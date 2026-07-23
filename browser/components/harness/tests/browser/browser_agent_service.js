/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);
const { CodexAppServerClient } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs"
);

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

add_task(async function test_agent_service_conversation() {
  requestLongerTimeout(3);
  const greBinD = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  greBinD.append("libkrun.dylib");
  if (
    !(await IOUtils.exists(CodexAppServerClient.defaultBinaryPath())) ||
    !(await IOUtils.exists(greBinD.path))
  ) {
    todo(false, "codex binary or VM deps not present; run setup scripts");
    return;
  }

  const { HarnessVM } = ChromeUtils.importESModule(
    "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
  );
  registerCleanupFunction(async () => {
    await AgentService.shutdown();
    // Conversations auto-start the sandbox VM; leave a clean slate.
    if (HarnessVM.state == "running") {
      await HarnessVM.stop();
    }
  });
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });

  const conversation = await AgentService.createConversation();
  ok(conversation.conversationId, "conversation created");
  is(conversation.modelProvider, "ollama", "template provider used");

  await Assert.rejects(
    AgentService.sendMessage("no-such-conversation", "hi"),
    /unknown conversation/,
    "unknown conversation ids are rejected"
  );

  if (!(await ollamaAvailable())) {
    todo(false, "ollama not running; skipped live turn");
    return;
  }

  const events = [];
  let reply = "";
  const completed = new Promise(resolve => {
    AgentService.addListener(event => {
      events.push(event.type);
      if (event.type == "delta") {
        reply += event.text;
      }
      if (event.type == "turnCompleted") {
        resolve(event);
      }
    });
  });
  await AgentService.sendMessage(
    conversation.conversationId,
    "Reply with exactly one word: pong"
  );
  const done = await completed;
  is(done.status, "completed", "turn completed");
  ok(reply.length, `streamed reply (${reply.slice(0, 40)})`);
  ok(events.includes("turnStarted"), "turnStarted event emitted");

  await AgentService.shutdown();
  ok(true, "shutdown clean");
});
