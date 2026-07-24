/* Any copyright is dedicated to the Public Domain.
   http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

add_task(async function test_session_metadata_and_activity() {
  const port = await MCPServer.start({ port: -1 });
  const session = MCPServer.session;
  Assert.ok(session, "session created on start");
  Assert.greater(session.token.length, 8, "session has a minted token");
  Assert.equal(session.state, "active", "session starts active");
  Assert.equal(session.clientInfo, null, "no client before the handshake");
  Assert.equal(session.scope, null, "unscoped session has no tab scope");

  await mcpRpc(port, "initialize", {
    protocolVersion: "2025-03-26",
    capabilities: {},
    clientInfo: {
      name: "mochitest-agent",
      version: "1.2",
      title: "Mochitest Agent",
    },
  });
  Assert.equal(
    session.clientInfo.name,
    "mochitest-agent",
    "client name captured"
  );
  Assert.equal(session.clientInfo.version, "1.2", "client version captured");
  Assert.equal(
    session.clientInfo.title,
    "Mochitest Agent",
    "client title captured"
  );
  Assert.equal(
    session.activity.at(-1).label,
    "initialize",
    "handshake recorded"
  );

  await callTool(port, "list_pages");
  Assert.equal(
    session.activity.at(-1).label,
    "list_pages",
    "tool call recorded"
  );

  MCPServer.stop();
});

add_task(async function test_pause_resume_revoke() {
  const port = await MCPServer.start({ port: -1 });
  const session = MCPServer.session;

  const before = await callTool(port, "list_pages");
  Assert.ok(!before.isError, "tool calls work while active");

  MCPSessions.pause(session);
  Assert.equal(session.state, "paused");
  const activityLength = session.activity.length;
  const paused = await callTool(port, "list_pages");
  Assert.ok(paused.isError, "tool calls fail while paused");
  Assert.ok(
    toolText(paused).includes("paused"),
    "pause is reported to the agent"
  );
  Assert.equal(
    session.activity.length,
    activityLength,
    "blocked calls are not recorded as activity"
  );

  MCPSessions.resume(session);
  Assert.equal(session.state, "active");
  const resumed = await callTool(port, "list_pages");
  Assert.ok(!resumed.isError, "tool calls work after resume");

  // In auth=none mode a revoked session is replaced with a fresh one on the
  // next call; strict revocation (401) is covered in browser_mcp_oauth.js.
  MCPSessions.revoke(session);
  const afterRevoke = await callTool(port, "list_pages");
  Assert.ok(!afterRevoke.isError, "auth=none recovers after revocation");
  Assert.notEqual(
    MCPServer.session,
    session,
    "a fresh session replaces the revoked one"
  );

  MCPServer.stop();
});

add_task(async function test_session_events() {
  const port = await MCPServer.start({ port: -1 });
  const session = MCPServer.session;
  const events = [];
  const listener = (type, s) => {
    if (s === session) {
      events.push(type);
    }
  };
  MCPSessions.addListener(listener);

  await callTool(port, "list_pages");
  Assert.ok(events.includes("activity"), "activity event fired");

  MCPSessions.pause(session);
  Assert.ok(events.includes("updated"), "updated event fired on pause");

  MCPSessions.removeListener(listener);
  MCPServer.stop();
});

add_task(async function test_stop_revokes_session() {
  await MCPServer.start({ port: -1 });
  const session = MCPServer.session;
  MCPServer.stop();
  Assert.equal(session.state, "revoked", "stop revokes the session");
  Assert.equal(MCPServer.session, null, "server drops the session on stop");
});
