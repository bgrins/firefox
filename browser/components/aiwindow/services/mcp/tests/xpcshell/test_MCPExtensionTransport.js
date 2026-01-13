/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { ExtensionMCPRegistry } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPExtensionTransport.sys.mjs"
);

// Tests for ExtensionMCPRegistry

add_setup(async function () {
  ExtensionMCPRegistry.clear();
});

registerCleanupFunction(async function () {
  ExtensionMCPRegistry.clear();
});

add_task(async function test_registry_register_and_get() {
  const extensionId = "test-mcp-server@example.com";
  const metadata = { name: "Test MCP Server", version: "1.0.0" };
  const messageHandler = async msg => ({ jsonrpc: "2.0", id: msg.id, result: {} });

  ExtensionMCPRegistry.register(extensionId, metadata, messageHandler);

  Assert.ok(
    ExtensionMCPRegistry.has(extensionId),
    "Registry should have the extension"
  );

  const registration = ExtensionMCPRegistry.get(extensionId);
  Assert.ok(registration, "Should get registration");
  Assert.equal(registration.metadata.name, "Test MCP Server", "Metadata name matches");
  Assert.equal(registration.metadata.version, "1.0.0", "Metadata version matches");
  Assert.ok(registration.messageHandler, "Has message handler");
  Assert.ok(registration.registeredAt > 0, "Has registration timestamp");
});

add_task(async function test_registry_list_extensions() {
  ExtensionMCPRegistry.clear();

  const ext1 = "ext1@example.com";
  const ext2 = "ext2@example.com";
  const handler = async () => ({});

  ExtensionMCPRegistry.register(ext1, { name: "Ext1" }, handler);
  ExtensionMCPRegistry.register(ext2, { name: "Ext2" }, handler);

  const extensions = ExtensionMCPRegistry.listExtensions();
  Assert.equal(extensions.length, 2, "Should have 2 extensions");
  Assert.ok(extensions.includes(ext1), "Should include ext1");
  Assert.ok(extensions.includes(ext2), "Should include ext2");
});

add_task(async function test_registry_unregister() {
  ExtensionMCPRegistry.clear();

  const extensionId = "to-remove@example.com";
  ExtensionMCPRegistry.register(extensionId, { name: "ToRemove" }, async () => ({}));

  Assert.ok(ExtensionMCPRegistry.has(extensionId), "Should exist before unregister");

  const result = ExtensionMCPRegistry.unregister(extensionId);
  Assert.ok(result, "Unregister should return true");
  Assert.ok(!ExtensionMCPRegistry.has(extensionId), "Should not exist after unregister");

  const result2 = ExtensionMCPRegistry.unregister(extensionId);
  Assert.ok(!result2, "Second unregister should return false");
});

add_task(async function test_registry_send_message() {
  ExtensionMCPRegistry.clear();

  const extensionId = "message-handler@example.com";
  const receivedMessages = [];

  const messageHandler = async msg => {
    receivedMessages.push(msg);

    if (msg.method === "initialize") {
      return {
        jsonrpc: "2.0",
        id: msg.id,
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "Test Server", version: "1.0.0" },
          capabilities: {},
        },
      };
    }

    if (msg.method === "tools/list") {
      return {
        jsonrpc: "2.0",
        id: msg.id,
        result: {
          tools: [
            { name: "test_tool", inputSchema: { type: "object" } },
          ],
        },
      };
    }

    return { jsonrpc: "2.0", id: msg.id, result: {} };
  };

  ExtensionMCPRegistry.register(extensionId, { name: "MessageHandler" }, messageHandler);

  // Test initialize message
  const initResponse = await ExtensionMCPRegistry.sendMessage(extensionId, {
    jsonrpc: "2.0",
    method: "initialize",
    params: {},
    id: "init-1",
  });

  Assert.equal(initResponse.id, "init-1", "Response ID matches");
  Assert.equal(
    initResponse.result.serverInfo.name,
    "Test Server",
    "Server name in response"
  );

  // Test tools/list message
  const toolsResponse = await ExtensionMCPRegistry.sendMessage(extensionId, {
    jsonrpc: "2.0",
    method: "tools/list",
    params: {},
    id: "tools-1",
  });

  Assert.equal(toolsResponse.result.tools.length, 1, "Should have 1 tool");
  Assert.equal(toolsResponse.result.tools[0].name, "test_tool", "Tool name matches");

  Assert.equal(receivedMessages.length, 2, "Handler received 2 messages");
});

add_task(async function test_registry_send_message_unregistered() {
  ExtensionMCPRegistry.clear();

  await Assert.rejects(
    ExtensionMCPRegistry.sendMessage("nonexistent@example.com", {}),
    /Extension not registered/,
    "Should throw for unregistered extension"
  );
});

add_task(async function test_registry_listener() {
  ExtensionMCPRegistry.clear();

  const events = [];
  const listener = (event, extensionId, metadata) => {
    events.push({ event, extensionId, metadata });
  };

  ExtensionMCPRegistry.addListener(listener);

  const extensionId = "listener-test@example.com";
  ExtensionMCPRegistry.register(extensionId, { name: "ListenerTest" }, async () => ({}));

  Assert.equal(events.length, 1, "Should have 1 event");
  Assert.equal(events[0].event, "registered", "Event type is registered");
  Assert.equal(events[0].extensionId, extensionId, "Extension ID matches");
  Assert.equal(events[0].metadata.name, "ListenerTest", "Metadata passed to listener");

  ExtensionMCPRegistry.unregister(extensionId);

  Assert.equal(events.length, 2, "Should have 2 events");
  Assert.equal(events[1].event, "unregistered", "Event type is unregistered");
  Assert.equal(events[1].extensionId, extensionId, "Extension ID matches");

  ExtensionMCPRegistry.removeListener(listener);

  ExtensionMCPRegistry.register("another@example.com", {}, async () => ({}));
  Assert.equal(events.length, 2, "Should still have 2 events after removing listener");
});

add_task(async function test_registry_clear() {
  ExtensionMCPRegistry.clear();

  ExtensionMCPRegistry.register("a@example.com", {}, async () => ({}));
  ExtensionMCPRegistry.register("b@example.com", {}, async () => ({}));

  Assert.equal(ExtensionMCPRegistry.listExtensions().length, 2, "Should have 2");

  ExtensionMCPRegistry.clear();

  Assert.equal(ExtensionMCPRegistry.listExtensions().length, 0, "Should have 0 after clear");
});
