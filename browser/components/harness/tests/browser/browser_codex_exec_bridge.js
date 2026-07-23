/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

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

// Minimal exec-server client over a real WebSocket, mirroring how the
// app-server drives the bridge (Codex JSON-RPC dialect: no jsonrpc field).
/**
 *
 */
class BridgeClient {
  constructor(url) {
    this.url = url;
    this.pending = new Map();
    this.notifications = [];
    this.nextId = 1;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.socket = new WebSocket(this.url);
      this.socket.onopen = resolve;
      this.socket.onerror = () => reject(new Error("websocket error"));
      this.socket.onmessage = event => {
        const message = JSON.parse(event.data);
        if (message.id !== undefined) {
          const pending = this.pending.get(message.id);
          this.pending.delete(message.id);
          if (message.error) {
            pending.reject(new Error(message.error.message));
          } else {
            pending.resolve(message.result);
          }
        } else {
          this.notifications.push(message);
        }
      };
    });
  }

  request(method, params) {
    const id = this.nextId++;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  close() {
    this.socket?.close();
  }
}

function b64(text) {
  return btoa(String.fromCharCode(...new TextEncoder().encode(text)));
}

function fromB64(data) {
  return new TextDecoder().decode(
    Uint8Array.from(atob(data), c => c.charCodeAt(0))
  );
}

add_task(async function test_exec_bridge_routing() {
  requestLongerTimeout(3);
  if (!(await IOUtils.exists(greBinPath("libkrun.dylib")))) {
    todo(false, "harness VM deps not present; run setup-deps.sh");
    return;
  }
  // Earlier tests may still be tearing their VM down (or left it running).
  for (
    let i = 0;
    !["stopped", "running"].includes(HarnessVM.state) && i < 60;
    i++
  ) {
    // eslint-disable-next-line mozilla/no-arbitrary-setTimeout
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  await SpecialPowers.pushPrefEnv({
    set: [["browser.harness.enabled", true]],
  });
  registerCleanupFunction(async () => {
    CodexExecBridge.stop();
    if (HarnessVM.state == "running") {
      await HarnessVM.stop();
    }
  });

  // Boot the VM (unless a previous test left it running) and wait for the
  // guest agent.
  if (HarnessVM.state != "running") {
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
  }
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

  const url = CodexExecBridge.start();
  const client = new BridgeClient(url);
  await client.connect();

  const init = await client.request("initialize", {
    clientName: "bridge-test",
  });
  ok(init.sessionId, "initialize returns a session id");

  const info = await client.request("environment/info", {});
  is(info.shell.path, "/bin/sh", "environment shell reported");
  is(info.cwd, "file:///workspace", "environment cwd is the workspace");

  const status = await client.request("environment/status", {});
  is(status.status, "ready", "environment status ready");

  // process/start routes into the guest.
  await client.request("process/start", {
    processId: "p1",
    argv: ["/bin/sh", "-c", "uname -sm; pwd"],
    cwd: "file:///workspace",
    env: {},
    tty: false,
  });
  let read;
  for (let i = 0; i < 40; i++) {
    read = await client.request("process/read", {
      processId: "p1",
      afterSeq: 0,
      waitMs: 1000,
    });
    if (read.exited && read.chunks.length) {
      break;
    }
  }
  const output = read.chunks.map(c => fromB64(c.chunk)).join("");
  ok(
    output.includes("Linux aarch64"),
    `command ran in guest (${output.trim()})`
  );
  ok(output.includes("/workspace"), "command cwd is the guest workspace");
  is(read.exitCode, 0, "exit code propagated");
  ok(
    client.notifications.some(n => n.method == "process/exited"),
    "process/exited notification emitted"
  );

  // fs ops route into the guest and round-trip bytes.
  await client.request("fs/writeFile", {
    path: "file:///workspace/bridge.txt",
    dataBase64: b64("bridge-bytes\n"),
  });
  const readFile = await client.request("fs/readFile", {
    path: "file:///workspace/bridge.txt",
  });
  is(
    fromB64(readFile.dataBase64),
    "bridge-bytes\n",
    "fs read/write round-trip"
  );

  const hostSide = PathUtils.join(HarnessVM.workspacePath, "bridge.txt");
  is(
    await IOUtils.readUTF8(hostSide),
    "bridge-bytes\n",
    "guest write visible via workspace mount"
  );

  const meta = await client.request("fs/getMetadata", {
    path: "file:///workspace/bridge.txt",
  });
  ok(meta.isFile && !meta.isDirectory, "metadata kind");
  is(meta.size, 13, "metadata size");

  const listing = await client.request("fs/readDirectory", {
    path: "file:///workspace",
  });
  ok(
    listing.entries.some(e => e.fileName == "bridge.txt" && e.isFile),
    "directory listing includes the file"
  );

  const canonical = await client.request("fs/canonicalize", {
    path: "file:///workspace/../workspace/bridge.txt",
  });
  is(canonical.path, "file:///workspace/bridge.txt", "canonicalize");

  await client.request("fs/copy", {
    sourcePath: "file:///workspace/bridge.txt",
    destinationPath: "file:///workspace/bridge2.txt",
    recursive: false,
  });
  await client.request("fs/remove", {
    path: "file:///workspace/bridge2.txt",
    force: true,
  });
  ok(true, "copy and remove complete");

  // Path policy: everything outside /workspace is denied.
  for (const [method, params] of [
    ["fs/readFile", { path: "file:///etc/passwd" }],
    ["fs/writeFile", { path: "file:///tmp/x", dataBase64: b64("x") }],
    ["fs/readFile", { path: "file:///workspace/../etc/passwd" }],
    [
      "process/start",
      {
        processId: "p2",
        argv: ["/bin/sh", "-c", "id"],
        cwd: "file:///etc",
        env: {},
        tty: false,
      },
    ],
  ]) {
    await Assert.rejects(
      client.request(method, params),
      /denied/,
      `${method} outside workspace denied (${params.path?.slice(7) ?? "cwd"})`
    );
  }

  // Unknown methods fail closed.
  await Assert.rejects(
    client.request("http/request", { url: "https://example.com" }),
    /not supported/,
    "unlisted methods are rejected"
  );

  // process/terminate kills a long-running guest process.
  await client.request("process/start", {
    processId: "p3",
    argv: ["/bin/sh", "-c", "sleep 300"],
    cwd: "file:///workspace",
    env: {},
    tty: false,
  });
  await client.request("process/terminate", { processId: "p3" });
  let killed;
  for (let i = 0; i < 40; i++) {
    killed = await client.request("process/read", {
      processId: "p3",
      afterSeq: 0,
      waitMs: 500,
    });
    if (killed.exited) {
      break;
    }
  }
  is(killed.exitCode, 137, "terminated process reports SIGKILL exit");

  // The audit log saw every routed operation.
  const audited = CodexExecBridge.auditLog.map(e => e.method);
  for (const expected of ["process/start", "fs/writeFile", "fs/readFile"]) {
    ok(audited.includes(expected), `audit log recorded ${expected}`);
  }
  ok(
    CodexExecBridge.auditLog.some(e => e.verdict != "ok"),
    "audit log recorded denials"
  );

  client.close();
  CodexExecBridge.stop();
  await HarnessVM.stop();
});
