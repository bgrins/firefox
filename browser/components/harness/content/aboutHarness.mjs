/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
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

HarnessVM.addListener(onEvent);
window.addEventListener("unload", () => HarnessVM.removeListener(onEvent));

$("disabled-notice").hidden = enabled;
updateState(HarnessVM.state);
