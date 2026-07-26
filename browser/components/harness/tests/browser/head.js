/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

/* exported vmDepsPresent, codexDepsPresent, ollamaAvailable, waitForVMState,
   startVM, stopVM */

const { HarnessVM } = ChromeUtils.importESModule(
  "moz-src:///browser/components/harness/HarnessVM.sys.mjs"
);

// The micro-VM stack's runtime deps come from setup-deps.sh, not the build;
// tests skip gracefully when they are missing.
async function vmDepsPresent() {
  const libkrun = Services.dirsvc.get("GreBinD", Ci.nsIFile);
  libkrun.append("libkrun.dylib");
  return IOUtils.exists(libkrun.path);
}

async function codexDepsPresent() {
  const { CodexAppServerClient } = ChromeUtils.importESModule(
    "moz-src:///browser/components/harness/codex/CodexAppServerClient.sys.mjs"
  );
  return (
    (await IOUtils.exists(CodexAppServerClient.defaultBinaryPath())) &&
    (await vmDepsPresent())
  );
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

function waitForVMState(state, session = HarnessVM) {
  return new Promise(resolve => {
    const listener = event => {
      if (event.type == "state" && event.state == state) {
        session.removeListener(listener);
        resolve();
      }
    };
    session.addListener(listener);
  });
}

// Starts the VM and resolves once the guest-agent answers, so tests never
// need their own poll loops. Also registers cleanup that stops the VM.
async function startVM({ session = HarnessVM } = {}) {
  requestLongerTimeout(3);
  registerCleanupFunction(async () => {
    if (session.state == "running" || session.state == "starting") {
      await stopVM({ session });
    }
  });
  // Keep a boot transcript so a failed start reports what the guest said.
  const transcript = [];
  const transcriptListener = event => {
    if (["stdout", "stderr", "log", "error"].includes(event.type)) {
      transcript.push(`${event.type}: ${event.data ?? event.message}`);
    }
  };
  session.addListener(transcriptListener);
  try {
    const running = waitForVMState("running", session);
    await session.start();
    await running;
    await TestUtils.waitForCondition(
      async () => {
        try {
          await session.exec("true");
          return true;
        } catch (e) {
          if (session.state != "running") {
            throw new Error(
              `VM left running state: ${session.state}\n--- boot transcript:\n` +
                transcript.slice(-25).join("")
            );
          }
          return false;
        }
      },
      "guest-agent answers",
      500,
      60
    );
  } catch (e) {
    info(
      `VM boot transcript (${transcript.length} events):\n${transcript.slice(0, 30).join("")}\n...\n${transcript.slice(-8).join("")}`
    );
    throw e;
  } finally {
    session.removeListener(transcriptListener);
  }
}

async function stopVM({ session = HarnessVM } = {}) {
  if (session.state == "stopped") {
    return;
  }
  const stopped = waitForVMState("stopped", session);
  await session.stop();
  await stopped;
}
