/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);

add_task(async function test_agent_service_conversation() {
  requestLongerTimeout(3);
  if (!(await codexDepsPresent())) {
    todo(false, "codex binary or VM deps not present; run setup scripts");
    return;
  }

  registerCleanupFunction(async () => {
    await AgentService.shutdown();
    // Conversations auto-start the sandbox VM; leave a clean slate.
    await stopVM();
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

add_task(async function test_delete_conversation() {
  if (!(await codexDepsPresent())) {
    todo(false, "codex binary or VM deps not present; run setup scripts");
    return;
  }
  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  registerCleanupFunction(async () => {
    await AgentService.shutdown();
    await stopVM();
  });

  if (!(await ollamaAvailable())) {
    // Threads only persist (and list) once they have a turn.
    todo(false, "ollama not running; skipped delete roundtrip");
    return;
  }
  const conversation = await AgentService.createConversation();
  const completed = new Promise(resolve => {
    const listener = event => {
      if (event.type == "turnCompleted") {
        AgentService.removeListener(listener);
        resolve();
      }
    };
    AgentService.addListener(listener);
  });
  await AgentService.sendMessage(
    conversation.conversationId,
    "Reply with exactly one word: ping"
  );
  await completed;
  const listed = await AgentService.listConversations();
  ok(
    listed.some(c => c.conversationId == conversation.conversationId),
    "conversation appears in the list"
  );
  await AgentService.deleteConversation(conversation.conversationId);
  const after = await AgentService.listConversations();
  ok(
    !after.some(c => c.conversationId == conversation.conversationId),
    "deleted conversation no longer listed"
  );
});
