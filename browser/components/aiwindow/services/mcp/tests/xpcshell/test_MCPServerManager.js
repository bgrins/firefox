/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPServerManager, ServerStatus } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs"
);

const { HttpServer } = ChromeUtils.importESModule(
  "resource://testing-common/httpd.sys.mjs"
);

ChromeUtils.defineLazyGetter(this, "NetUtil", () => {
  return ChromeUtils.importESModule("resource://gre/modules/NetUtil.sys.mjs")
    .NetUtil;
});

let gHttpServer;
let gServerUrl;
let echoServerCode;

add_setup(async function () {
  gHttpServer = new HttpServer();
  gHttpServer.registerPathHandler("/mcp", handleMCPRequest);
  gHttpServer.start(-1);
  gServerUrl = `http://localhost:${gHttpServer.identity.primaryPort}/mcp`;

  const echoServerPath = do_get_file("echo-server.js").path;
  echoServerCode = await IOUtils.readUTF8(echoServerPath);

  info(`Test HTTP server running at ${gServerUrl}`);
});

registerCleanupFunction(async () => {
  if (gHttpServer) {
    await new Promise(resolve => gHttpServer.stop(resolve));
  }
});

function handleMCPRequest(request, response) {
  response.setHeader("Content-Type", "application/json", false);

  if (request.method !== "POST") {
    response.setStatusLine("1.1", 405, "Method Not Allowed");
    return;
  }

  const body = NetUtil.readInputStreamToString(
    request.bodyInputStream,
    request.bodyInputStream.available()
  );

  const message = JSON.parse(body);
  const { method, id } = message;

  const SERVER_INFO = { name: "test-http-server", version: "1.0.0" };

  if (method === "initialize") {
    response.setStatusLine("1.1", 200, "OK");
    response.write(
      JSON.stringify({
        jsonrpc: "2.0",
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: SERVER_INFO,
          capabilities: {},
        },
        id,
      })
    );
  } else {
    response.setStatusLine("1.1", 200, "OK");
    response.write(
      JSON.stringify({
        jsonrpc: "2.0",
        result: { success: true },
        id,
      })
    );
  }
}

add_task(async function test_register_http_server() {
  info("Testing HTTP server registration");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "test-http",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  const servers = manager.listServers();
  Assert.equal(servers.length, 1, "Should have 1 registered server");
  Assert.equal(servers[0].id, "test-http", "Server ID should match");
  Assert.equal(servers[0].type, "http", "Server type should be http");
  Assert.equal(
    servers[0].status,
    ServerStatus.STOPPED,
    "Server should be stopped"
  );
});

add_task(async function test_register_sandbox_server() {
  info("Testing sandbox server registration");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "test-sandbox",
    type: "sandbox",
    code: echoServerCode,
    enabled: false,
  });

  const servers = manager.listServers();
  Assert.equal(servers.length, 1, "Should have 1 registered server");
  Assert.equal(servers[0].id, "test-sandbox", "Server ID should match");
  Assert.equal(servers[0].type, "sandbox", "Server type should be sandbox");
  Assert.equal(
    servers[0].status,
    ServerStatus.STOPPED,
    "Server should be stopped"
  );
});

add_task(async function test_register_invalid_configs() {
  info("Testing invalid server registration");

  const manager = new MCPServerManager();

  await Assert.rejects(
    manager.registerServer({ type: "http" }),
    /id is required/,
    "Should reject missing id"
  );

  await Assert.rejects(
    manager.registerServer({ id: "test" }),
    /type must be/,
    "Should reject missing type"
  );

  await Assert.rejects(
    manager.registerServer({ id: "test", type: "invalid" }),
    /type must be/,
    "Should reject invalid type"
  );

  await Assert.rejects(
    manager.registerServer({ id: "test", type: "http" }),
    /requires url/,
    "Should reject HTTP server without url"
  );

  await Assert.rejects(
    manager.registerServer({ id: "test", type: "sandbox" }),
    /requires code/,
    "Should reject sandbox server without code"
  );
});

add_task(async function test_start_stop_http_server() {
  info("Testing HTTP server lifecycle");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "lifecycle-http",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  Assert.equal(
    manager.getServerStatus("lifecycle-http"),
    ServerStatus.STOPPED,
    "Server should start stopped"
  );

  await manager.startServer("lifecycle-http");

  Assert.equal(
    manager.getServerStatus("lifecycle-http"),
    ServerStatus.RUNNING,
    "Server should be running"
  );

  const serverInfo = manager.getServerInfo("lifecycle-http");
  Assert.equal(serverInfo.serverInfo.name, "test-http-server", "Should have server info");
  Assert.ok(serverInfo.startTime, "Should have start time");
  Assert.ok(serverInfo.uptime >= 0, "Should have uptime");
  Assert.equal(serverInfo.lastError, null, "Should have no error");

  await manager.stopServer("lifecycle-http");

  Assert.equal(
    manager.getServerStatus("lifecycle-http"),
    ServerStatus.STOPPED,
    "Server should be stopped"
  );

  const stoppedInfo = manager.getServerInfo("lifecycle-http");
  Assert.equal(stoppedInfo.serverInfo, null, "Server info should be cleared");
  Assert.equal(stoppedInfo.startTime, null, "Start time should be cleared");
  Assert.equal(stoppedInfo.uptime, null, "Uptime should be null");
});

add_task(async function test_start_stop_sandbox_server() {
  info("Testing sandbox server lifecycle");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "lifecycle-sandbox",
    type: "sandbox",
    code: echoServerCode,
    enabled: false,
  });

  await manager.startServer("lifecycle-sandbox");

  Assert.equal(
    manager.getServerStatus("lifecycle-sandbox"),
    ServerStatus.RUNNING,
    "Server should be running"
  );

  const serverInfo = manager.getServerInfo("lifecycle-sandbox");
  Assert.equal(serverInfo.serverInfo.name, "echo", "Should have server info");

  await manager.stopServer("lifecycle-sandbox");

  Assert.equal(
    manager.getServerStatus("lifecycle-sandbox"),
    ServerStatus.STOPPED,
    "Server should be stopped"
  );
});

add_task(async function test_restart_server() {
  info("Testing server restart");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "restart-test",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  await manager.startServer("restart-test");
  const firstStartTime = manager.getServerInfo("restart-test").startTime;

  await manager.restartServer("restart-test");

  Assert.equal(
    manager.getServerStatus("restart-test"),
    ServerStatus.RUNNING,
    "Server should be running after restart"
  );

  const secondStartTime = manager.getServerInfo("restart-test").startTime;
  Assert.ok(
    secondStartTime > firstStartTime,
    "Start time should be updated"
  );
});

add_task(async function test_multiple_servers() {
  info("Testing multiple servers");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "multi-http",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  await manager.registerServer({
    id: "multi-sandbox",
    type: "sandbox",
    code: echoServerCode,
    enabled: false,
  });

  const servers = manager.listServers();
  Assert.equal(servers.length, 2, "Should have 2 servers");

  await manager.startServer("multi-http");
  await manager.startServer("multi-sandbox");

  Assert.equal(
    manager.getServerStatus("multi-http"),
    ServerStatus.RUNNING,
    "HTTP server should be running"
  );
  Assert.equal(
    manager.getServerStatus("multi-sandbox"),
    ServerStatus.RUNNING,
    "Sandbox server should be running"
  );

  await manager.stopServer("multi-http");
  await manager.stopServer("multi-sandbox");
});

add_task(async function test_start_all_stop_all() {
  info("Testing startAllServers and stopAllServers");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "all-http-1",
    type: "http",
    url: gServerUrl,
    enabled: true,
  });

  await manager.registerServer({
    id: "all-http-2",
    type: "http",
    url: gServerUrl,
    enabled: true,
  });

  await manager.registerServer({
    id: "all-disabled",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  await manager.stopAllServers();

  await manager.startAllServers();

  Assert.equal(
    manager.getServerStatus("all-http-1"),
    ServerStatus.RUNNING,
    "Enabled server 1 should be running"
  );
  Assert.equal(
    manager.getServerStatus("all-http-2"),
    ServerStatus.RUNNING,
    "Enabled server 2 should be running"
  );
  Assert.equal(
    manager.getServerStatus("all-disabled"),
    ServerStatus.STOPPED,
    "Disabled server should remain stopped"
  );

  await manager.stopAllServers();

  Assert.equal(
    manager.getServerStatus("all-http-1"),
    ServerStatus.STOPPED,
    "Server 1 should be stopped"
  );
  Assert.equal(
    manager.getServerStatus("all-http-2"),
    ServerStatus.STOPPED,
    "Server 2 should be stopped"
  );
});

add_task(async function test_error_handling() {
  info("Testing error handling");

  const manager = new MCPServerManager();

  await Assert.rejects(
    manager.startServer("nonexistent"),
    /not found/,
    "Should reject starting nonexistent server"
  );

  await Assert.rejects(
    manager.stopServer("nonexistent"),
    /not found/,
    "Should reject stopping nonexistent server"
  );

  Assert.throws(
    () => manager.getServerInfo("nonexistent"),
    /not found/,
    "Should reject getting info for nonexistent server"
  );

  await manager.registerServer({
    id: "error-test",
    type: "http",
    url: "http://localhost:1/nonexistent",
    enabled: false,
  });

  await Assert.rejects(
    manager.startServer("error-test"),
    /Failed to start/,
    "Should reject when connection fails"
  );

  Assert.equal(
    manager.getServerStatus("error-test"),
    ServerStatus.ERROR,
    "Server should be in error state"
  );

  const serverInfo = manager.getServerInfo("error-test");
  Assert.ok(serverInfo.lastError, "Should have error message");
});

add_task(async function test_unregister_server() {
  info("Testing server unregistration");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "unregister-test",
    type: "http",
    url: gServerUrl,
    enabled: true,
  });

  Assert.equal(manager.listServers().length, 1, "Should have 1 server");

  await manager.unregisterServer("unregister-test");

  Assert.equal(manager.listServers().length, 0, "Should have 0 servers");

  Assert.equal(
    manager.getServerStatus("unregister-test"),
    null,
    "Server should not exist"
  );
});

add_task(async function test_auto_start_on_register() {
  info("Testing auto-start on registration");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "auto-start",
    type: "http",
    url: gServerUrl,
    enabled: true,
  });

  Assert.equal(
    manager.getServerStatus("auto-start"),
    ServerStatus.RUNNING,
    "Server should auto-start when enabled=true"
  );

  await manager.stopServer("auto-start");
});

add_task(async function test_duplicate_registration() {
  info("Testing duplicate server registration");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "duplicate",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  await Assert.rejects(
    manager.registerServer({
      id: "duplicate",
      type: "http",
      url: gServerUrl,
      enabled: false,
    }),
    /already registered/,
    "Should reject duplicate registration"
  );
});

add_task(async function test_get_transport() {
  info("Testing getTransport");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "transport-test",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  Assert.equal(
    manager.getTransport("transport-test"),
    undefined,
    "Should have no transport when stopped"
  );

  await manager.startServer("transport-test");

  const transport = manager.getTransport("transport-test");
  Assert.ok(transport, "Should have transport when running");
  Assert.ok(transport.isConnected(), "Transport should be connected");

  await manager.stopServer("transport-test");

  Assert.equal(
    manager.getTransport("transport-test"),
    undefined,
    "Transport should be removed after stop"
  );
});

add_task(async function test_stop_server_disconnect_error() {
  info("Testing stopServer handles disconnect errors properly");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "disconnect-error-test",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  // Get the transport and break its disconnect method
  const transport = manager.getTransport("disconnect-error-test");
  const originalDisconnect = transport.disconnect.bind(transport);
  transport.disconnect = async () => {
    throw new Error("Simulated disconnect error");
  };

  // Stop should throw and set ERROR state
  await Assert.rejects(
    manager.stopServer("disconnect-error-test"),
    /Failed to stop server/,
    "Should reject when disconnect fails"
  );

  Assert.equal(
    manager.getServerStatus("disconnect-error-test"),
    ServerStatus.ERROR,
    "Server should be in ERROR state after disconnect failure"
  );

  // Transport should still be removed from manager
  Assert.equal(
    manager.getTransport("disconnect-error-test"),
    undefined,
    "Transport should be removed even when disconnect fails"
  );

  // Clean up by forcing disconnect with original method
  await originalDisconnect();
});

add_task(async function test_concurrent_start_calls() {
  info("Testing concurrent start calls use same promise (fix #6)");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "concurrent-start",
    type: "http",
    url: gServerUrl,
    enabled: false,
  });

  // Start the same server concurrently
  const [result1, result2, result3] = await Promise.all([
    manager.startServer("concurrent-start"),
    manager.startServer("concurrent-start"),
    manager.startServer("concurrent-start"),
  ]);

  // All should succeed without error
  Assert.equal(
    manager.getServerStatus("concurrent-start"),
    ServerStatus.RUNNING,
    "Server should be running"
  );

  await manager.stopServer("concurrent-start");
});

add_task(async function test_start_stop_all_with_failures() {
  info("Testing startAllServers/stopAllServers return failure info (fix #7)");

  const manager = new MCPServerManager();

  // Register servers without auto-starting them
  const goodConfig = {
    id: "good-server",
    type: "http",
    url: gServerUrl,
  };
  manager.servers.set("good-server", {
    config: { ...goodConfig, enabled: true },
    status: ServerStatus.STOPPED,
    serverInfo: null,
    lastError: null,
    startTime: null,
  });

  const badConfig = {
    id: "bad-server",
    type: "http",
    url: "http://localhost:1/nonexistent",
  };
  manager.servers.set("bad-server", {
    config: { ...badConfig, enabled: true },
    status: ServerStatus.STOPPED,
    serverInfo: null,
    lastError: null,
    startTime: null,
  });

  // Both should be in STOPPED state with enabled=true, so startAllServers will try both
  const startResult = await manager.startAllServers();
  Assert.equal(startResult.started, 1, "Should have started 1 server");
  Assert.equal(startResult.failures.length, 1, "Should have 1 failure");
  Assert.equal(
    startResult.failures[0].serverId,
    "bad-server",
    "bad-server should have failed"
  );

  // Stop all
  const stopResult = await manager.stopAllServers();
  Assert.equal(stopResult.stopped, 1, "Should have stopped 1 server");
  Assert.equal(stopResult.failures.length, 0, "Should have no stop failures");
});

add_task(async function test_restart_with_stop_failure() {
  info("Testing restart continues even if stop fails (fix #8)");

  const manager = new MCPServerManager();

  await manager.registerServer({
    id: "restart-stop-fail",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  // Get transport and break disconnect
  const transport = manager.getTransport("restart-stop-fail");
  transport.disconnect = async () => {
    throw new Error("Simulated disconnect error");
  };

  // Restart should still work (start happens despite stop failure)
  await manager.restartServer("restart-stop-fail");

  Assert.equal(
    manager.getServerStatus("restart-stop-fail"),
    ServerStatus.RUNNING,
    "Server should be running after restart"
  );

  await manager.stopAllServers();
});

add_task(async function test_server_limit() {
  info("Testing server registration limit (fix #15)");

  const manager = new MCPServerManager();

  // This assumes MAX_SERVERS = 100
  // Register 100 servers
  for (let i = 0; i < 100; i++) {
    await manager.registerServer({
      id: `server-${i}`,
      type: "http",
      url: gServerUrl,
      enabled: false,
    });
  }

  Assert.equal(manager.listServers().length, 100, "Should have 100 servers");

  // 101st should fail
  await Assert.rejects(
    manager.registerServer({
      id: "server-101",
      type: "http",
      url: gServerUrl,
      enabled: false,
    }),
    /limit of 100 reached/,
    "Should reject when limit reached"
  );
});
