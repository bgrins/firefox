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
let turnActivity = null;
const activityRows = new Map();

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
      }
      chatAgentBubble.textContent += event.text;
      scrollChat();
      break;
    case "message":
      if (chatAgentBubble) {
        chatAgentBubble.textContent = event.text;
      } else {
        chatBubble("agent", event.text);
      }
      chatAgentBubble = null;
      break;
    case "item":
      renderItem(event.item);
      break;
    case "approvalRequest":
      renderApproval(event);
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

function resetChat() {
  chatConversationId = null;
  chatAgentBubble = null;
  turnActivity = null;
  activityRows.clear();
  $("chat-log").textContent = "";
  $("chat-history").value = "";
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
      const date = new Date(conversation.updatedAt * 1000);
      option.textContent = `${date.toLocaleDateString()} ${conversation.preview.slice(0, 70)}`;
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
        chatBubble("agent", item.text ?? "");
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
      const conversation = await AgentService.createConversation({
        persist: !temporaryMode,
      });
      chatConversationId = conversation.conversationId;
      chatBubble(
        "meta",
        `conversation ready (${conversation.modelProvider}/${conversation.model})` +
          (temporaryMode ? " - temporary" : "")
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
  $(provider == "openai" ? "provider-openai" : "provider-ollama").checked =
    true;
  $("model-input").value = Services.prefs.getStringPref(
    "browser.harness.codex.model",
    ""
  );
  $("settings-login").hidden = provider != "openai";
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

for (const id of ["provider-ollama", "provider-openai"]) {
  $(id).addEventListener("change", () => {
    $("settings-login").hidden = !$("provider-openai").checked;
  });
}

$("settings-save").addEventListener("click", async () => {
  const provider = $("provider-openai").checked ? "openai" : "ollama";
  Services.prefs.setStringPref("browser.harness.codex.provider", provider);
  Services.prefs.setStringPref(
    "browser.harness.codex.model",
    $("model-input").value.trim()
  );
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
