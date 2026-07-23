/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);
const { AgentService } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/codex/AgentService.sys.mjs"
);

const $ = id => document.getElementById(id);

const enabled = Services.prefs.getBoolPref("browser.harness.enabled", false);

// eslint-disable-next-line no-control-regex
const ANSI_RE = /\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*(\x07|\x1b\\)/g;

function appendOutput(text, className) {
  const output = $("output");
  const atBottom =
    output.scrollTop + output.clientHeight >= output.scrollHeight - 4;
  const span = document.createElement("span");
  if (className) {
    span.className = className;
  }
  span.textContent = text.replace(ANSI_RE, "");
  output.appendChild(span);
  if (atBottom) {
    output.scrollTop = output.scrollHeight;
  }
}

function updateState(state) {
  const statusEl = $("status");
  statusEl.textContent = state;
  statusEl.dataset.state = state;
  $("start").disabled = !enabled || state != "stopped";
  $("stop").disabled = state != "running";
  $("reset").disabled = state != "stopped";
  const command = $("command");
  command.disabled = state != "running";
  $("exec-command").disabled = state != "running";
  $("exec-run").disabled = state != "running";
  if (state == "running") {
    command.focus();
  }
}

function onEvent(event) {
  switch (event.type) {
    case "state":
      updateState(event.state);
      break;
    case "stdout":
      appendOutput(event.data);
      break;
    case "stderr":
      appendOutput(event.data, "stderr");
      break;
    case "log":
      appendOutput(`[${event.message}]\n`, "meta");
      break;
    case "exit":
      appendOutput(`[VM exited with code ${event.exitCode}]\n`, "meta");
      break;
    case "error":
      appendOutput(`[error: ${event.message}]\n`, "meta");
      break;
  }
}

$("start").addEventListener("click", () => {
  appendOutput("[starting VM]\n", "meta");
  HarnessVM.start();
});

$("stop").addEventListener("click", () => {
  HarnessVM.stop();
});

$("reset").addEventListener("click", async () => {
  try {
    await HarnessVM.resetRootfs();
    appendOutput(
      "[rootfs reset; a fresh copy is made on next start]\n",
      "meta"
    );
  } catch (e) {
    appendOutput(`[error: ${e.message}]\n`, "meta");
  }
});

$("input-row").addEventListener("submit", event => {
  event.preventDefault();
  const command = $("command");
  const line = command.value;
  command.value = "";
  appendOutput(`$ ${line}\n`, "echo");
  HarnessVM.write(`${line}\n`);
});

$("exec-row").addEventListener("submit", async event => {
  event.preventDefault();
  const input = $("exec-command");
  const cmd = input.value;
  if (!cmd) {
    return;
  }
  input.value = "";
  appendOutput(`> ${cmd}\n`, "echo");
  const started = Date.now();
  try {
    const result = await HarnessVM.exec(cmd, {
      onOutput(stream, text) {
        appendOutput(text, stream == "stderr" ? "stderr" : undefined);
      },
    });
    const flags = [
      result.timedOut ? "timed out" : "",
      result.truncated ? "output truncated" : "",
    ]
      .filter(Boolean)
      .map(f => `, ${f}`)
      .join("");
    appendOutput(
      `[exit ${result.exitCode}, ${Date.now() - started}ms${flags}]\n`,
      "meta"
    );
  } catch (e) {
    appendOutput(`[exec error: ${e.message}]\n`, "meta");
  }
});

let chatConversationId = null;
let chatAgentBubble = null;
const chatItemBubbles = new Map();

function chatBubble(role, text) {
  const log = $("chat-log");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

function describeItem(item) {
  switch (item.type) {
    case "commandExecution": {
      const state =
        item.status == "completed"
          ? `exit ${item.exitCode ?? "?"}`
          : item.status;
      return `$ ${item.command}   [${state}]`;
    }
    case "reasoning":
      return `thinking: ${item.summary?.join(" ") || "..."}`;
    case "fileChange": {
      const paths = (item.changes ?? []).map(c => c.path).join(", ");
      return `file changes: ${paths || "(pending)"} [${item.status ?? ""}]`;
    }
    case "webSearch":
      return `web search: ${item.query ?? ""}`;
    case "mcpToolCall":
      return `tool call: ${item.server ?? ""}/${item.tool ?? ""} [${item.status ?? ""}]`;
    default:
      return `${item.type} [${item.status ?? ""}]`;
  }
}

function renderItem(item) {
  const text = describeItem(item);
  let bubble = chatItemBubbles.get(item.id);
  if (!bubble) {
    bubble = chatBubble("tool", text);
    chatItemBubbles.set(item.id, bubble);
  } else {
    bubble.textContent = text;
  }
}

function renderApproval(event) {
  const bubble = chatBubble("approval", "");
  const label = document.createElement("div");
  const command =
    event.params?.command ?? JSON.stringify(event.params ?? {}).slice(0, 200);
  label.textContent = `approval requested: ${command}`;
  bubble.appendChild(label);
  const respond = decision => {
    AgentService.respondToApproval(event.requestId, decision);
    bubble.textContent = `approval: ${decision} (${command})`;
  };
  for (const [text, decision] of [
    ["Allow", "accept"],
    ["Allow for session", "acceptForSession"],
    ["Deny", "decline"],
  ]) {
    const button = document.createElement("button");
    button.textContent = text;
    button.addEventListener("click", () => respond(decision));
    bubble.appendChild(button);
  }
  $("chat-log").scrollTop = $("chat-log").scrollHeight;
}

function onAgentEvent(event) {
  if (event.conversationId && event.conversationId != chatConversationId) {
    return;
  }
  switch (event.type) {
    case "turnStarted":
      $("chat-interrupt").hidden = false;
      break;
    case "delta":
      if (!chatAgentBubble) {
        chatAgentBubble = chatBubble("agent", "");
      }
      chatAgentBubble.textContent += event.text;
      $("chat-log").scrollTop = $("chat-log").scrollHeight;
      break;
    case "message":
      if (chatAgentBubble) {
        chatAgentBubble.textContent = event.text;
      } else {
        chatBubble("agent", event.text);
      }
      chatAgentBubble = null;
      break;
    case "turnCompleted":
      $("chat-interrupt").hidden = true;
      $("chat-send").disabled = false;
      chatAgentBubble = null;
      break;
    case "item":
      renderItem(event.item);
      break;
    case "approvalRequest":
      renderApproval(event);
      break;
    case "log":
      chatBubble("meta", event.message);
      break;
    case "error":
      chatBubble("meta", `error: ${event.message}`);
      $("chat-interrupt").hidden = true;
      $("chat-send").disabled = false;
      break;
  }
}

$("chat-row").addEventListener("submit", async event => {
  event.preventDefault();
  const input = $("chat-input");
  const text = input.value.trim();
  if (!text) {
    return;
  }
  input.value = "";
  chatBubble("user", text);
  $("chat-send").disabled = true;
  try {
    if (!chatConversationId) {
      chatBubble("meta", "starting agent sidecar...");
      const conversation = await AgentService.createConversation();
      chatConversationId = conversation.conversationId;
      chatBubble(
        "meta",
        `conversation ready (${conversation.modelProvider}/${conversation.model})`
      );
    }
    await AgentService.sendMessage(chatConversationId, text);
  } catch (e) {
    chatBubble("meta", `error: ${e.message}`);
    $("chat-send").disabled = false;
  }
});

$("chat-interrupt").addEventListener("click", () => {
  if (chatConversationId) {
    AgentService.interrupt(chatConversationId);
  }
});

$("chat-copy").addEventListener("click", async () => {
  const lines = [...$("chat-log").children].map(element => {
    const role = element.classList[1] ?? "msg";
    return `[${role}] ${element.textContent}`;
  });
  await navigator.clipboard.writeText(lines.join("\n"));
  const button = $("chat-copy");
  button.textContent = "Copied";
  setTimeout(() => {
    button.textContent = "Copy transcript";
  }, 1500);
});

if (!enabled) {
  $("chat-input").disabled = true;
  $("chat-send").disabled = true;
}

HarnessVM.addListener(onEvent);
AgentService.addListener(onAgentEvent);
window.addEventListener("unload", () => {
  HarnessVM.removeListener(onEvent);
  AgentService.removeListener(onAgentEvent);
});

$("disabled-notice").hidden = enabled;
updateState(HarnessVM.state);
