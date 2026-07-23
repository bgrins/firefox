/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

add_task(async function test_server_lifecycle() {
  const port = await MCPServer.start({ port: -1 });
  Assert.greater(port, 0, "server bound to an ephemeral port");
  Assert.ok(MCPServer.running, "server reports running");
  Assert.ok(!MCPServer.scoped, "server is not tab-scoped");

  const init = await mcpRpc(port, "initialize", {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: { name: "mochitest", version: "0" },
  });
  Assert.equal(init.status, 200, "initialize succeeds");
  Assert.equal(
    init.json.result.serverInfo.name,
    "firefox-devtools-mcp-extension",
    "server identifies itself"
  );

  const list = await mcpRpc(port, "tools/list");
  const names = list.json.result.tools.map(t => t.name);
  Assert.ok(names.includes("list_pages"), "tools/list includes list_pages");
  Assert.ok(
    names.includes("take_snapshot"),
    "tools/list includes take_snapshot"
  );

  const unauthorized = await mcpRpc(port, "ping", {}, { token: "wrong-token" });
  Assert.equal(unauthorized.status, 401, "bad bearer token is rejected");

  const missingAuth = await mcpRpc(port, "ping", {}, { token: null });
  Assert.equal(missingAuth.status, 401, "missing bearer token is rejected");

  const notFound = await rawHttpRequest(port, {
    path: "/other",
    headers: { Authorization: `Bearer ${MCP_DEV_TOKEN}` },
    body: "{}",
  });
  Assert.equal(notFound.status, 404, "non-/mcp path is rejected");

  MCPServer.stop();
  Assert.ok(!MCPServer.running, "server reports stopped");

  const afterStop = await rawHttpRequest(port, { body: "{}" });
  Assert.equal(afterStop.status, 0, "no response after stop");
});

add_task(async function test_tool_call() {
  const port = await MCPServer.start({ port: -1 });
  const tab = await BrowserTestUtils.openNewForegroundTab(
    gBrowser,
    testPageUrl("example.com", "MCPServerPage")
  );

  const pages = toolText(await callTool(port, "list_pages"));
  Assert.ok(
    pages.includes("MCPServerPage"),
    `list_pages sees the open tab: ${pages}`
  );

  BrowserTestUtils.removeTab(tab);
  MCPServer.stop();
});
