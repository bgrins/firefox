/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

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

add_task(async function test_codex_app_server_client() {
  if (!(await IOUtils.exists(CodexAppServerClient.defaultBinaryPath()))) {
    todo(
      false,
      "codex-app-server not present; run browser/components/harness/vm/setup-codex.sh"
    );
    return;
  }

  const client = new CodexAppServerClient({
    codexHome: PathUtils.join(PathUtils.profileDir, "codex-test-home"),
  });
  registerCleanupFunction(() => client.stop());

  const init = await client.start();
  ok(client.running, "sidecar is running");
  ok(
    init.userAgent.startsWith("firefox-harness/"),
    `initialize handshake completed (${init.userAgent})`
  );
  ok(
    // macOS reports the /private-canonicalized path.
    init.codexHome.endsWith("codex-test-home"),
    `sidecar uses the dedicated CODEX_HOME (${init.codexHome})`
  );

  const threadResult = await client.request("thread/start", {
    cwd: PathUtils.join(client._codexHome, "cwd"),
    ephemeral: true,
  });
  const thread = threadResult.thread;
  ok(thread.id, `thread started (${thread.id})`);
  is(
    threadResult.modelProvider,
    "ollama",
    "ollama provider from template config"
  );
  is(
    threadResult.sandbox.networkAccess,
    false,
    "default sandbox has no network access"
  );

  if (await ollamaAvailable()) {
    const notifications = [];
    let deltas = "";
    const completed = new Promise(resolve => {
      client.addListener(notification => {
        notifications.push(notification.method);
        if (notification.method == "item/agentMessage/delta") {
          deltas += notification.params.delta;
        }
        if (notification.method == "turn/completed") {
          resolve();
        }
      });
    });
    await client.request("turn/start", {
      threadId: thread.id,
      input: [{ type: "text", text: "Reply with exactly one word: pong" }],
    });
    await completed;
    ok(deltas.length, `streamed agent deltas (${deltas.slice(0, 40)})`);
    ok(
      notifications.includes("turn/started"),
      "turn lifecycle notifications observed"
    );
  } else {
    todo(false, "ollama not running; skipped live turn");
  }

  // Unsolicited server->client requests must fail closed by default.
  client._handleLine(
    JSON.stringify({ id: 9999, method: "execCommandApproval", params: {} })
  );

  await client.stop();
  ok(!client.running, "sidecar stopped");
  await Assert.rejects(
    client.request("thread/start", {}),
    /not running/,
    "requests after stop are rejected"
  );
});
