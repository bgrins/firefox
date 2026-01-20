/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { HarborMCPRegistry } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
);

// Helper to clear registry between tests
function clearRegistry() {
  for (const { extensionId } of HarborMCPRegistry.list()) {
    HarborMCPRegistry.unregister(extensionId);
  }
}

add_setup(async function () {
  clearRegistry();
});

registerCleanupFunction(async function () {
  clearRegistry();
});

add_task(async function test_registry_register_and_get() {
  clearRegistry();

  const extensionId = "test-mcp-server@example.com";
  const metadata = { name: "Test MCP Server", version: "1.0.0" };
  const fireEvent = () => {};

  HarborMCPRegistry.register(extensionId, metadata, fireEvent);

  Assert.ok(
    HarborMCPRegistry.has(extensionId),
    "Registry should have the extension"
  );

  const registration = HarborMCPRegistry.get(extensionId);
  Assert.ok(registration, "Should get registration");
  Assert.equal(registration.metadata.name, "Test MCP Server", "Metadata name matches");
  Assert.equal(registration.metadata.version, "1.0.0", "Metadata version matches");
  Assert.ok(registration.fireEvent, "Has fire event function");
  Assert.ok(registration.registeredAt > 0, "Has registration timestamp");
});

add_task(async function test_registry_list() {
  clearRegistry();

  const ext1 = "ext1@example.com";
  const ext2 = "ext2@example.com";
  const fireEvent = () => {};

  HarborMCPRegistry.register(ext1, { name: "Ext1" }, fireEvent);
  HarborMCPRegistry.register(ext2, { name: "Ext2" }, fireEvent);

  const list = HarborMCPRegistry.list();
  Assert.equal(list.length, 2, "Should have 2 extensions");
  Assert.ok(
    list.some(e => e.extensionId === ext1),
    "Should include ext1"
  );
  Assert.ok(
    list.some(e => e.extensionId === ext2),
    "Should include ext2"
  );
});

add_task(async function test_registry_unregister() {
  clearRegistry();

  const extensionId = "to-remove@example.com";
  HarborMCPRegistry.register(extensionId, { name: "ToRemove" }, () => {});

  Assert.ok(HarborMCPRegistry.has(extensionId), "Should exist before unregister");

  const result = HarborMCPRegistry.unregister(extensionId);
  Assert.ok(result, "Unregister should return true");
  Assert.ok(!HarborMCPRegistry.has(extensionId), "Should not exist after unregister");

  const result2 = HarborMCPRegistry.unregister(extensionId);
  Assert.ok(!result2, "Second unregister should return false");
});

add_task(async function test_registry_send_message_and_response() {
  clearRegistry();

  const extensionId = "message-handler@example.com";
  const receivedMessages = [];

  // fireEvent is called by sendMessage, we need to respond via handleResponse
  const fireEvent = (requestId, message) => {
    receivedMessages.push({ requestId, message });

    // Simulate async response from extension
    let response;
    if (message.method === "initialize") {
      response = {
        jsonrpc: "2.0",
        id: message.id,
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "Test Server", version: "1.0.0" },
          capabilities: {},
        },
      };
    } else if (message.method === "tools/list") {
      response = {
        jsonrpc: "2.0",
        id: message.id,
        result: {
          tools: [{ name: "test_tool", inputSchema: { type: "object" } }],
        },
      };
    } else {
      response = { jsonrpc: "2.0", id: message.id, result: {} };
    }

    // Call handleResponse to complete the request
    HarborMCPRegistry.handleResponse(extensionId, requestId, response);
  };

  HarborMCPRegistry.register(extensionId, { name: "MessageHandler" }, fireEvent);

  // Test initialize message
  const initResponse = await HarborMCPRegistry.sendMessage(extensionId, {
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
  const toolsResponse = await HarborMCPRegistry.sendMessage(extensionId, {
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
  clearRegistry();

  await Assert.rejects(
    HarborMCPRegistry.sendMessage("nonexistent@example.com", {}),
    /Extension not registered/,
    "Should throw for unregistered extension"
  );
});

add_task(async function test_registry_duplicate_registration() {
  clearRegistry();

  const extensionId = "duplicate@example.com";
  HarborMCPRegistry.register(extensionId, { name: "First" }, () => {});

  Assert.throws(
    () => HarborMCPRegistry.register(extensionId, { name: "Second" }, () => {}),
    /already registered/,
    "Should throw on duplicate registration"
  );
});

add_task(async function test_registry_listener() {
  clearRegistry();

  const events = [];
  const listener = (event, extensionId, metadata) => {
    events.push({ event, extensionId, metadata });
  };

  HarborMCPRegistry.addListener(listener);

  const extensionId = "listener-test@example.com";
  HarborMCPRegistry.register(extensionId, { name: "ListenerTest" }, () => {});

  Assert.equal(events.length, 1, "Should have 1 event");
  Assert.equal(events[0].event, "registered", "Event type is registered");
  Assert.equal(events[0].extensionId, extensionId, "Extension ID matches");
  Assert.equal(events[0].metadata.name, "ListenerTest", "Metadata passed to listener");

  HarborMCPRegistry.unregister(extensionId);

  Assert.equal(events.length, 2, "Should have 2 events");
  Assert.equal(events[1].event, "unregistered", "Event type is unregistered");
  Assert.equal(events[1].extensionId, extensionId, "Extension ID matches");

  HarborMCPRegistry.removeListener(listener);

  HarborMCPRegistry.register("another@example.com", {}, () => {});
  Assert.equal(events.length, 2, "Should still have 2 events after removing listener");
});

add_task(async function test_registry_unregister_clears_pending_requests() {
  clearRegistry();

  const extensionId = "pending-test@example.com";

  // Register with a fireEvent that doesn't respond
  HarborMCPRegistry.register(extensionId, { name: "Pending" }, () => {
    // Don't call handleResponse - simulate unresponsive extension
  });

  // Start a request (it won't complete because fireEvent doesn't respond)
  const requestPromise = HarborMCPRegistry.sendMessage(extensionId, {
    jsonrpc: "2.0",
    method: "test",
    id: 1,
  });

  // Unregister should reject the pending request
  HarborMCPRegistry.unregister(extensionId);

  await Assert.rejects(
    requestPromise,
    /Extension unregistered/,
    "Pending request should be rejected when extension unregisters"
  );
});

add_task(async function test_registry_handleResponse_wrong_extension() {
  clearRegistry();

  const ext1 = "ext1@example.com";
  const ext2 = "ext2@example.com";
  let capturedRequestId = null;

  HarborMCPRegistry.register(ext1, { name: "Ext1" }, (requestId) => {
    capturedRequestId = requestId;
    // Don't respond - let ext2 try to respond
  });
  HarborMCPRegistry.register(ext2, { name: "Ext2" }, () => {});

  // Start a request to ext1
  const requestPromise = HarborMCPRegistry.sendMessage(ext1, {
    jsonrpc: "2.0",
    method: "test",
    id: 1,
  });

  // Try to respond from ext2 (should be ignored)
  HarborMCPRegistry.handleResponse(ext2, capturedRequestId, {
    jsonrpc: "2.0",
    id: 1,
    result: { from: "ext2" },
  });

  // Now respond correctly from ext1
  HarborMCPRegistry.handleResponse(ext1, capturedRequestId, {
    jsonrpc: "2.0",
    id: 1,
    result: { from: "ext1" },
  });

  const response = await requestPromise;
  Assert.equal(response.result.from, "ext1", "Should use response from correct extension");
});

add_task(async function test_registry_concurrent_messages() {
  clearRegistry();

  const extensionId = "concurrent@example.com";

  HarborMCPRegistry.register(extensionId, { name: "Concurrent" }, (requestId, message) => {
    // Respond with the message id to verify routing
    HarborMCPRegistry.handleResponse(extensionId, requestId, {
      jsonrpc: "2.0",
      id: message.id,
      result: { receivedId: message.id },
    });
  });

  // Send multiple messages concurrently
  const promises = [
    HarborMCPRegistry.sendMessage(extensionId, { jsonrpc: "2.0", id: 1, method: "test" }),
    HarborMCPRegistry.sendMessage(extensionId, { jsonrpc: "2.0", id: 2, method: "test" }),
    HarborMCPRegistry.sendMessage(extensionId, { jsonrpc: "2.0", id: 3, method: "test" }),
  ];

  const responses = await Promise.all(promises);

  Assert.equal(responses[0].result.receivedId, 1, "First message routed correctly");
  Assert.equal(responses[1].result.receivedId, 2, "Second message routed correctly");
  Assert.equal(responses[2].result.receivedId, 3, "Third message routed correctly");
});
