/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import {
  parseMarkdown,
  CHAT_WRAPPER_ELEMENTS,
} from "chrome://browser/content/aiwindow/modules/ChatMarkdownParser.mjs";

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

/* ---- Sandbox VM tools (secondary UI) ---- */

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
  HarnessVM.start().catch(e =>
    appendOutput(`[start failed: ${e.message}]\n`, "meta")
  );
});

function renderSessions() {
  const list = $("sessions-list");
  list.textContent = "";
  for (const info of HarnessVM.listSessions()) {
    const row = document.createElement("div");
    row.className = "session-row";
    const label = document.createElement("code");
    const uptime = info.startedAtMs
      ? `${Math.round((Date.now() - info.startedAtMs) / 1000)}s`
      : "-";
    label.textContent = `${info.id}  ${info.state}  pid=${info.pid ?? "-"}  up=${uptime}`;
    row.appendChild(label);
    if (info.state == "running") {
      const stopButton = document.createElement("button");
      stopButton.type = "button";
      stopButton.textContent = "Stop";
      stopButton.addEventListener("click", async () => {
        await HarnessVM.session(info.id)?.stop();
        renderSessions();
      });
      row.appendChild(stopButton);
    }
    if (info.removable) {
      const destroyButton = document.createElement("button");
      destroyButton.type = "button";
      destroyButton.textContent = "Destroy";
      destroyButton.addEventListener("click", async () => {
        await HarnessVM.session(info.id)?.destroy();
        renderSessions();
      });
      row.appendChild(destroyButton);
    }
    list.appendChild(row);
  }
}

$("vm-tools").addEventListener("toggle", () => {
  if ($("vm-tools").open) {
    renderSessions();
  }
});
setInterval(() => {
  if ($("vm-tools").open) {
    renderSessions();
  }
}, 5000);

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

$("snapshot-places").addEventListener("click", async () => {
  try {
    const guestPath = await HarnessVM.snapshotPlacesToWorkspace();
    appendOutput(
      `[places snapshot at ${guestPath}; try: sqlite3 ${guestPath} ` +
        `'select url from moz_places order by visit_count desc limit 5']\n`,
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

/* ---- Agent chat (primary UI) ---- */

let chatConversationId = null;
let chatAgentBubble = null;
let chatAgentRawText = "";
let turnActivity = null;
const activityRows = new Map();

// Same sanitizer configuration as smart window's ai-chat-message: default
// Sanitizer plus the table wrapper element the markdown parser emits.
const markdownSanitizer = (() => {
  const sanitizer = new Sanitizer();
  for (const { element, attributes } of Object.values(CHAT_WRAPPER_ELEMENTS)) {
    sanitizer.allowElement(element);
    for (const attr of attributes) {
      sanitizer.allowAttribute({ name: attr, elements: [element] });
    }
  }
  return sanitizer;
})();

function renderMarkdown(element, text) {
  try {
    element.setHTML(parseMarkdown(text), { sanitizer: markdownSanitizer });
  } catch (e) {
    element.textContent = text;
  }
}

function scrollChat() {
  const log = $("chat-log");
  log.scrollTop = log.scrollHeight;
}

function chatBubble(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  $("chat-log").appendChild(div);
  scrollChat();
  return div;
}

const MIME_BY_EXTENSION = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  svg: "image/svg+xml",
};

function openArtifact(hostPath) {
  const file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
  file.initWithPath(hostPath);
  const uri = Services.io.newFileURI(file);
  const win = window.browsingContext.topChromeWindow;
  win.openTrustedLinkIn(uri.spec, "tab");
}

// Files presented by the agent (present_files tool): images render inline
// via blob URLs; everything else gets an open-in-tab button. Paths were
// validated to stay inside the workspace by HarnessBrowserTools.
async function renderPresentedFiles(event) {
  const card = document.createElement("div");
  card.className = "msg artifact";
  if (event.title) {
    const caption = document.createElement("div");
    caption.className = "artifact-title";
    caption.textContent = event.title;
    card.appendChild(caption);
  }
  for (const file of event.files) {
    if (file.kind == "image") {
      try {
        const bytes = await IOUtils.read(file.hostPath);
        const extension = file.name.split(".").pop().toLowerCase();
        const blob = new Blob([bytes], {
          type: MIME_BY_EXTENSION[extension] ?? "application/octet-stream",
        });
        const img = document.createElement("img");
        img.src = URL.createObjectURL(blob);
        img.alt = file.name;
        img.title = `${file.guestPath} — click to open`;
        img.addEventListener("click", () => openArtifact(file.hostPath));
        card.appendChild(img);
        continue;
      } catch (e) {
        // fall through to the file row
      }
    }
    const row = document.createElement("div");
    row.className = "artifact-file";
    const label = document.createElement("span");
    label.textContent = `${file.name} (${Math.ceil(file.size / 1024)} KB)`;
    const openButton = document.createElement("button");
    openButton.textContent = "Open";
    openButton.addEventListener("click", () => openArtifact(file.hostPath));
    row.append(label, openButton);
    card.appendChild(row);
  }
  $("chat-log").appendChild(card);
  scrollChat();
}

// Tool calls, thinking and approvals for the current turn are grouped in an
// expandable activity block that always sits above the streaming answer.
function ensureActivity() {
  if (!turnActivity) {
    const details = document.createElement("details");
    details.className = "activity working";
    const summary = document.createElement("summary");
    const spinner = document.createElement("span");
    spinner.className = "spinner";
    const label = document.createElement("span");
    label.textContent = "Working...";
    summary.append(spinner, label);
    const list = document.createElement("div");
    list.className = "activity-items";
    details.append(summary, list);
    const log = $("chat-log");
    if (chatAgentBubble?.parentNode == log) {
      log.insertBefore(details, chatAgentBubble);
    } else {
      log.appendChild(details);
    }
    turnActivity = { details, label, list, steps: 0 };
    scrollChat();
  }
  return turnActivity;
}

function finishActivity() {
  if (turnActivity) {
    turnActivity.details.classList.remove("working");
    turnActivity.label.textContent = `${turnActivity.steps} step${
      turnActivity.steps == 1 ? "" : "s"
    }`;
    turnActivity = null;
  }
  activityRows.clear();
}

function updateActivityLabel(activity) {
  activity.label.textContent = `Working... (${activity.steps} step${
    activity.steps == 1 ? "" : "s"
  })`;
}

function renderItem(item) {
  const activity = ensureActivity();
  let row = activityRows.get(item.id);
  if (!row) {
    activity.steps++;
    updateActivityLabel(activity);
    if (item.type == "reasoning") {
      row = document.createElement("details");
      row.className = "activity-row thinking";
      row.append(
        document.createElement("summary"),
        document.createElement("div")
      );
    } else {
      row = document.createElement("div");
      row.className = "activity-row";
    }
    activity.list.appendChild(row);
    activityRows.set(item.id, row);
    scrollChat();
  }
  switch (item.type) {
    case "reasoning": {
      const text = (
        item.summary?.join("\n") ||
        item.content?.join("\n") ||
        ""
      ).trim();
      const firstLine = text.split("\n")[0] || "...";
      row.querySelector("summary").textContent = `thinking: ${firstLine.slice(
        0,
        120
      )}`;
      row.querySelector("div").textContent = text;
      break;
    }
    case "commandExecution": {
      row.classList.add("command");
      row.textContent = `$ ${item.command}`;
      const chip = document.createElement("span");
      chip.className = `chip ${item.status ?? ""}`;
      chip.textContent =
        item.status == "completed"
          ? `exit ${item.exitCode ?? "?"}`
          : (item.status ?? "running");
      row.appendChild(chip);
      // Output is available once the item completes; expand it by default
      // for failures so errors are diagnosable from the UI.
      const output = (item.aggregatedOutput ?? "").trim();
      if (output) {
        const failed = item.status == "failed" || item.exitCode;
        const details = document.createElement("details");
        details.className = "command-output";
        details.open = !!failed;
        const summary = document.createElement("summary");
        summary.textContent = "output";
        const pre = document.createElement("pre");
        pre.textContent =
          output.length > 8000 ? `...${output.slice(-8000)}` : output;
        details.append(summary, pre);
        row.appendChild(details);
      }
      break;
    }
    case "fileChange": {
      const paths = (item.changes ?? []).map(c => c.path).join(", ");
      row.textContent = `file changes: ${paths || "(pending)"}`;
      break;
    }
    default:
      row.textContent = `${item.type} [${item.status ?? ""}]`;
  }
}

function renderApproval(event) {
  const activity = ensureActivity();
  activity.details.open = true;
  const row = document.createElement("div");
  row.className = "activity-row approval";
  const label = document.createElement("div");
  const command =
    event.params?.command ?? JSON.stringify(event.params ?? {}).slice(0, 200);
  label.textContent = `approval requested: ${command}`;
  row.appendChild(label);
  const respond = decision => {
    AgentService.respondToApproval(event.requestId, decision);
    row.textContent = `approval: ${decision} (${command})`;
  };
  for (const [text, decision] of [
    ["Allow", "accept"],
    ["Allow for session", "acceptForSession"],
    ["Deny", "decline"],
  ]) {
    const button = document.createElement("button");
    button.textContent = text;
    button.addEventListener("click", () => respond(decision));
    row.appendChild(button);
  }
  activity.list.appendChild(row);
  scrollChat();
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
        chatAgentRawText = "";
      }
      chatAgentRawText += event.text;
      renderMarkdown(chatAgentBubble, chatAgentRawText);
      scrollChat();
      break;
    case "message":
      renderMarkdown(chatAgentBubble ?? chatBubble("agent", ""), event.text);
      chatAgentBubble = null;
      chatAgentRawText = "";
      break;
    case "item":
      renderItem(event.item);
      break;
    case "approvalRequest":
      renderApproval(event);
      break;
    case "presentFiles":
      renderPresentedFiles(event);
      break;
    case "turnCompleted":
      finishActivity();
      $("chat-interrupt").hidden = true;
      $("chat-send").disabled = false;
      chatAgentBubble = null;
      break;
    case "log":
      chatBubble("meta", event.message);
      break;
    case "error":
      finishActivity();
      chatBubble("meta", `error: ${event.message}`);
      $("chat-interrupt").hidden = true;
      $("chat-send").disabled = false;
      break;
  }
}

let temporaryMode = false;

function updateDeleteButton() {
  $("chat-delete").disabled = !chatConversationId || temporaryMode;
}

$("chat-delete").addEventListener("click", async () => {
  if (!chatConversationId) {
    return;
  }
  const id = chatConversationId;
  try {
    await AgentService.deleteConversation(id);
    resetChat();
    chatBubble("meta", "conversation deleted");
  } catch (e) {
    chatBubble("meta", `error: ${e.message}`);
  }
});

function resetChat() {
  chatConversationId = null;
  chatAgentBubble = null;
  turnActivity = null;
  activityRows.clear();
  $("chat-log").textContent = "";
  $("chat-history").value = "";
  updateDeleteButton();
}

$("chat-new").addEventListener("click", resetChat);

$("chat-temporary").addEventListener("click", () => {
  temporaryMode = !temporaryMode;
  const button = $("chat-temporary");
  button.setAttribute("aria-pressed", String(temporaryMode));
  button.classList.toggle("active", temporaryMode);
  resetChat();
  if (temporaryMode) {
    chatBubble("meta", "temporary chat: this conversation will not be saved");
  }
});

function relativeTime(epochSeconds) {
  const delta = Date.now() / 1000 - epochSeconds;
  if (delta < 3600) {
    return `${Math.max(1, Math.round(delta / 60))}m ago`;
  }
  if (delta < 86400) {
    return `${Math.round(delta / 3600)}h ago`;
  }
  return `${Math.round(delta / 86400)}d ago`;
}

async function refreshHistory() {
  try {
    const conversations = await AgentService.listConversations();
    const select = $("chat-history");
    const current = select.value;
    select.textContent = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "History...";
    select.appendChild(placeholder);
    for (const conversation of conversations) {
      const option = document.createElement("option");
      option.value = conversation.conversationId;
      option.textContent = `${relativeTime(conversation.updatedAt)} · ${conversation.preview.slice(0, 70)}`;
      select.appendChild(option);
    }
    select.value = current;
  } catch (e) {
    // Sidecar not running yet; history fills in once it is.
  }
}

// Renders a persisted turn from thread/resume: user/agent messages as
// bubbles, everything else in a collapsed activity block.
function renderHistoryTurn(turn) {
  let steps = 0;
  let activityList = null;
  const ensureBlock = () => {
    if (!activityList) {
      const details = document.createElement("details");
      details.className = "activity";
      const summary = document.createElement("summary");
      summary.textContent = "";
      activityList = document.createElement("div");
      activityList.className = "activity-items";
      details.append(summary, activityList);
      $("chat-log").appendChild(details);
    }
    return activityList;
  };
  for (const item of turn.items ?? []) {
    switch (item.type) {
      case "userMessage":
        chatBubble(
          "user",
          (item.content ?? [])
            .map(part => part.text ?? "")
            .join("")
            .trim()
        );
        break;
      case "agentMessage":
        renderMarkdown(chatBubble("agent", ""), item.text ?? "");
        break;
      default: {
        const row = document.createElement("div");
        row.className = `activity-row${item.type == "commandExecution" ? " command" : ""}`;
        if (item.type == "commandExecution") {
          row.textContent = `$ ${item.command}`;
        } else if (item.type == "reasoning") {
          row.textContent = `thinking: ${(item.summary?.join(" ") ?? "").slice(0, 120)}`;
        } else {
          row.textContent = item.type;
        }
        ensureBlock().appendChild(row);
        steps++;
      }
    }
    if (activityList) {
      activityList.parentNode.querySelector("summary").textContent =
        `${steps} step${steps == 1 ? "" : "s"}`;
    }
  }
}

$("chat-history").addEventListener("focus", refreshHistory);
$("chat-history").addEventListener("change", async () => {
  const conversationId = $("chat-history").value;
  if (!conversationId) {
    return;
  }
  resetChat();
  $("chat-history").value = conversationId;
  $("chat-send").disabled = true;
  try {
    chatBubble("meta", "resuming conversation...");
    const resumed = await AgentService.resumeConversation(conversationId);
    chatConversationId = conversationId;
    updateDeleteButton();
    for (const turn of resumed.turns) {
      renderHistoryTurn(turn);
    }
    chatBubble(
      "meta",
      `resumed (${resumed.modelProvider ?? "?"}/${resumed.model ?? "?"})`
    );
  } catch (e) {
    chatBubble("meta", `error: ${e.message}`);
  } finally {
    $("chat-send").disabled = false;
  }
});

// Tabs the user attached to the next message; staged into the workspace at
// send time so the agent can read them.
let pendingAttachments = [];

function renderAttachments() {
  const container = $("chat-attachments");
  container.textContent = "";
  pendingAttachments.forEach((attachment, position) => {
    const chip = document.createElement("span");
    chip.className = "attachment-chip";
    chip.textContent = `@ ${attachment.title.slice(0, 40)} `;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.setAttribute("aria-label", `Remove ${attachment.title}`);
    remove.addEventListener("click", () => {
      pendingAttachments.splice(position, 1);
      renderAttachments();
    });
    chip.appendChild(remove);
    container.appendChild(chip);
  });
}

$("chat-attach").addEventListener("focus", () => {
  const select = $("chat-attach");
  select.textContent = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "@ Tab...";
  select.appendChild(placeholder);
  for (const tab of AgentService.listOpenTabs()) {
    const option = document.createElement("option");
    option.value = String(tab.index);
    option.textContent = tab.title.slice(0, 60);
    select.appendChild(option);
  }
});

$("chat-attach").addEventListener("change", () => {
  const select = $("chat-attach");
  if (!select.value) {
    return;
  }
  const tab = AgentService.listOpenTabs().find(
    entry => String(entry.index) == select.value
  );
  if (tab && !pendingAttachments.some(a => a.index == tab.index)) {
    pendingAttachments.push(tab);
    renderAttachments();
  }
  select.value = "";
});

$("chat-row").addEventListener("submit", async event => {
  event.preventDefault();
  const input = $("chat-input");
  let text = input.value.trim();
  if (!text && !pendingAttachments.length) {
    return;
  }
  input.value = "";
  const attachments = pendingAttachments;
  pendingAttachments = [];
  renderAttachments();
  chatBubble(
    "user",
    text +
      (attachments.length
        ? `\n${attachments.map(a => `@ ${a.title}`).join("  ")}`
        : "")
  );
  $("chat-send").disabled = true;
  try {
    if (!chatConversationId) {
      chatBubble("meta", "starting agent sidecar...");
      const conversation = await AgentService.createConversation({
        persist: !temporaryMode,
      });
      chatConversationId = conversation.conversationId;
      updateDeleteButton();
      chatBubble(
        "meta",
        `conversation ready (${conversation.modelProvider}/${conversation.model})` +
          (temporaryMode ? " - temporary" : "")
      );
    }
    for (const attachment of attachments) {
      const staged = await AgentService.stageTab(
        chatConversationId,
        attachment.index
      );
      text +=
        `\n\n[User attached tab "${staged.title}" (${staged.url}): ` +
        `${staged.chars} chars of untrusted page text saved at ` +
        `${staged.guestPath} — read it with sandbox commands as needed.]`;
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
  const lines = [];
  for (const element of $("chat-log").children) {
    if (element.classList.contains("activity")) {
      for (const row of element.querySelectorAll(".activity-row")) {
        lines.push(`[tool] ${row.textContent}`);
      }
    } else {
      lines.push(`[${element.classList[1] ?? "msg"}] ${element.textContent}`);
    }
  }
  await navigator.clipboard.writeText(lines.join("\n"));
  const button = $("chat-copy");
  button.textContent = "Copied";
  setTimeout(() => {
    button.textContent = "Copy transcript";
  }, 1500);
});

/* ---- Settings ---- */

function loadSettings() {
  const provider = Services.prefs.getStringPref(
    "browser.harness.codex.provider",
    "ollama"
  );
  const radios = {
    openai: "provider-openai",
    openrouter: "provider-openrouter",
    ollama: "provider-ollama",
  };
  $(radios[provider] ?? "provider-ollama").checked = true;
  $("model-input").value = Services.prefs.getStringPref(
    "browser.harness.codex.model",
    ""
  );
  $("settings-login").hidden = provider != "openai";
  $("openrouter-key-row").hidden = provider != "openrouter";
  $("session-per-conversation").checked = Services.prefs.getBoolPref(
    "browser.harness.sessionPerConversation",
    false
  );
  try {
    $("proxy-allowlist").value = JSON.parse(
      Services.prefs.getStringPref("browser.harness.proxy.allowlist", "[]")
    ).join(", ");
  } catch (e) {
    $("proxy-allowlist").value = "";
  }
}

$("proxy-save").addEventListener("click", () => {
  const entries = $("proxy-allowlist")
    .value.split(",")
    .map(entry => entry.trim())
    .filter(Boolean);
  Services.prefs.setStringPref(
    "browser.harness.proxy.allowlist",
    JSON.stringify(entries)
  );
  $("settings-status").textContent = entries.length
    ? `Network allowlist: ${entries.join(", ")} (applies immediately)`
    : "Network allowlist empty: the sandbox has no network access.";
});

$("session-per-conversation").addEventListener("change", () => {
  Services.prefs.setBoolPref(
    "browser.harness.sessionPerConversation",
    $("session-per-conversation").checked
  );
});

function selectedProvider() {
  if ($("provider-openai").checked) {
    return "openai";
  }
  if ($("provider-openrouter").checked) {
    return "openrouter";
  }
  return "ollama";
}

for (const id of [
  "provider-ollama",
  "provider-openai",
  "provider-openrouter",
]) {
  $(id).addEventListener("change", () => {
    $("settings-login").hidden = !$("provider-openai").checked;
    $("openrouter-key-row").hidden = !$("provider-openrouter").checked;
  });
}

$("settings-save").addEventListener("click", async () => {
  const provider = selectedProvider();
  Services.prefs.setStringPref("browser.harness.codex.provider", provider);
  Services.prefs.setStringPref(
    "browser.harness.codex.model",
    $("model-input").value.trim()
  );
  const key = $("openrouter-key").value.trim();
  if (provider == "openrouter" && key) {
    const { CodexAppServerClient } = ChromeUtils.importESModule(
      "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs"
    );
    await CodexAppServerClient.setOpenRouterKey(key);
    $("openrouter-key").value = "";
  }
  await AgentService.applySettings();
  chatConversationId = null;
  $("settings-status").textContent =
    "Saved. The agent restarts with the new settings on the next message.";
});

$("settings-login").addEventListener("click", async () => {
  const statusEl = $("settings-status");
  try {
    statusEl.textContent = "Starting sign-in...";
    const result = await AgentService.login();
    statusEl.textContent = "Complete the sign-in in the opened tab: ";
    const link = document.createElement("a");
    link.href = result.authUrl;
    link.target = "_blank";
    link.textContent = "open sign-in page";
    statusEl.appendChild(link);
  } catch (e) {
    statusEl.textContent = `sign-in failed: ${e.message}`;
  }
});

/* ---- Shared folder mounts ---- */

function readMounts() {
  try {
    const parsed = JSON.parse(
      Services.prefs.getStringPref("browser.harness.mounts", "[]")
    );
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

async function writeMounts(mounts) {
  Services.prefs.setStringPref(
    "browser.harness.mounts",
    JSON.stringify(mounts)
  );
  renderMounts();
  if (HarnessVM.state == "running") {
    $("settings-status").textContent =
      "Shared folders changed; restarting the sandbox VM...";
    await HarnessVM.stop();
    $("settings-status").textContent =
      "Shared folders changed; the VM restarts on the next message.";
  }
}

function mountTagFor(path, mounts) {
  let base = (path.split("/").filter(Boolean).pop() ?? "folder")
    .toLowerCase()
    .replaceAll(/[^a-z0-9-]/g, "-")
    .replaceAll(/^-+|-+$/g, "")
    .slice(0, 24);
  if (!/^[a-z0-9]/.test(base)) {
    base = `f-${base}`;
  }
  let tag = base || "folder";
  for (let n = 2; mounts.some(m => m.tag == tag) || tag == "workspace"; n++) {
    tag = `${base}-${n}`;
  }
  return tag;
}

function renderMounts() {
  const list = $("mounts-list");
  list.textContent = "";
  for (const mount of readMounts()) {
    const row = document.createElement("div");
    row.className = "mount-row";
    const label = document.createElement("code");
    label.textContent = `/mnt/${mount.tag} ← ${mount.path}`;
    const roLabel = document.createElement("label");
    const ro = document.createElement("input");
    ro.type = "checkbox";
    ro.checked = !!mount.readOnly;
    ro.addEventListener("change", () => {
      const mounts = readMounts();
      const target = mounts.find(m => m.tag == mount.tag);
      if (target) {
        target.readOnly = ro.checked;
        writeMounts(mounts);
      }
    });
    roLabel.append(ro, document.createTextNode(" read-only"));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      writeMounts(readMounts().filter(m => m.tag != mount.tag));
    });
    row.append(label, roLabel, remove);
    list.appendChild(row);
  }
}

$("mount-add").addEventListener("click", () => {
  const picker = Cc["@mozilla.org/filepicker;1"].createInstance(
    Ci.nsIFilePicker
  );
  picker.init(
    window.browsingContext,
    "Choose a folder to share with the sandbox",
    Ci.nsIFilePicker.modeGetFolder
  );
  picker.open(result => {
    if (result != Ci.nsIFilePicker.returnOK) {
      return;
    }
    const mounts = readMounts();
    mounts.push({
      path: picker.file.path,
      tag: mountTagFor(picker.file.path, mounts),
      readOnly: true,
    });
    writeMounts(mounts);
  });
});

if (!enabled) {
  $("chat-input").disabled = true;
  $("chat-send").disabled = true;
}
loadSettings();
renderMounts();

HarnessVM.addListener(onEvent);
AgentService.addListener(onAgentEvent);
window.addEventListener("unload", () => {
  HarnessVM.removeListener(onEvent);
  AgentService.removeListener(onAgentEvent);
});

$("disabled-notice").hidden = enabled;
updateState(HarnessVM.state);
