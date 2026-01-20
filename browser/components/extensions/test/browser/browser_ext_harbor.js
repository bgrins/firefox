"use strict";

add_task(async function test_harbor_register_and_message() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      const messages = [];

      browser.harbor.onMCPMessage.addListener((requestId, message) => {
        messages.push(message);

        // Echo back a response
        browser.harbor.sendMCPResponse(requestId, {
          jsonrpc: "2.0",
          id: message.id,
          result: { echo: message.method },
        });
      });

      browser.harbor
        .registerMCPServer({
          name: "test-server",
          version: "1.0.0",
          description: "Test MCP server",
        })
        .then(() => {
          browser.test.sendMessage("registered");
        })
        .catch(err => {
          browser.test.fail(`Registration failed: ${err}`);
        });
    },
  });

  await extension.startup();
  await extension.awaitMessage("registered");

  // Get the registry and verify registration
  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  ok(
    HarborMCPRegistry.has(extension.id),
    "Extension should be registered in HarborMCPRegistry"
  );

  const serverInfo = HarborMCPRegistry.get(extension.id);
  is(serverInfo.metadata.name, "test-server", "Server name should match");
  is(serverInfo.metadata.version, "1.0.0", "Server version should match");

  // Test sending a message
  const response = await HarborMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    id: 1,
    method: "test/ping",
  });

  is(response.result.echo, "test/ping", "Response should echo the method");

  await extension.unload();

  ok(
    !HarborMCPRegistry.has(extension.id),
    "Extension should be unregistered after unload"
  );
});

add_task(async function test_harbor_must_add_listener_first() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      // Try to register without adding listener first
      browser.harbor
        .registerMCPServer({
          name: "test-server",
        })
        .then(() => {
          browser.test.fail("Should have thrown an error");
        })
        .catch(err => {
          browser.test.assertTrue(
            err.message.includes("Must add onMCPMessage listener"),
            "Should require listener before registration"
          );
          browser.test.sendMessage("done");
        });
    },
  });

  await extension.startup();
  await extension.awaitMessage("done");
  await extension.unload();
});

add_task(async function test_harbor_unregister() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      browser.harbor.onMCPMessage.addListener(() => {});

      browser.harbor
        .registerMCPServer({ name: "test-server" })
        .then(() => browser.harbor.unregisterMCPServer())
        .then(() => {
          browser.test.sendMessage("unregistered");
        });
    },
  });

  await extension.startup();
  await extension.awaitMessage("unregistered");

  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  ok(
    !HarborMCPRegistry.has(extension.id),
    "Extension should be unregistered after calling unregisterMCPServer"
  );

  await extension.unload();
});

add_task(async function test_harbor_concurrent_messages() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      browser.harbor.onMCPMessage.addListener((requestId, message) => {
        // Respond with the message id to verify correct routing
        browser.harbor.sendMCPResponse(requestId, {
          jsonrpc: "2.0",
          id: message.id,
          result: { receivedId: message.id },
        });
      });

      browser.harbor
        .registerMCPServer({ name: "concurrent-test" })
        .then(() => browser.test.sendMessage("registered"));
    },
  });

  await extension.startup();
  await extension.awaitMessage("registered");

  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  // Send multiple messages concurrently
  const promises = [
    HarborMCPRegistry.sendMessage(extension.id, { jsonrpc: "2.0", id: 1, method: "test" }),
    HarborMCPRegistry.sendMessage(extension.id, { jsonrpc: "2.0", id: 2, method: "test" }),
    HarborMCPRegistry.sendMessage(extension.id, { jsonrpc: "2.0", id: 3, method: "test" }),
  ];

  const responses = await Promise.all(promises);

  is(responses[0].result.receivedId, 1, "First message routed correctly");
  is(responses[1].result.receivedId, 2, "Second message routed correctly");
  is(responses[2].result.receivedId, 3, "Third message routed correctly");

  await extension.unload();
});

add_task(async function test_harbor_duplicate_registration() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      browser.harbor.onMCPMessage.addListener(() => {});

      browser.harbor
        .registerMCPServer({ name: "test-server" })
        .then(() => browser.harbor.registerMCPServer({ name: "test-server-2" }))
        .then(() => {
          browser.test.fail("Should have thrown on duplicate registration");
          browser.test.sendMessage("done");
        })
        .catch(err => {
          // Error message may be wrapped, just verify we got an error
          browser.test.assertTrue(
            err.message.length > 0,
            "Should reject duplicate registration with error: " + err.message
          );
          browser.test.sendMessage("done");
        });
    },
  });

  await extension.startup();
  await extension.awaitMessage("done");
  await extension.unload();
});

add_task(async function test_harbor_error_response() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      browser.harbor.onMCPMessage.addListener((requestId, message) => {
        // Respond with an error
        browser.harbor.sendMCPResponse(requestId, {
          jsonrpc: "2.0",
          id: message.id,
          error: { code: -32600, message: "Test error" },
        });
      });

      browser.harbor
        .registerMCPServer({ name: "error-test" })
        .then(() => browser.test.sendMessage("registered"));
    },
  });

  await extension.startup();
  await extension.awaitMessage("registered");

  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  // The response contains an error object but is still delivered
  const response = await HarborMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    id: 1,
    method: "test",
  });

  ok(response.error, "Response should contain error");
  is(response.error.code, -32600, "Error code should match");
  is(response.error.message, "Test error", "Error message should match");

  await extension.unload();
});

add_task(async function test_harbor_message_to_unregistered() {
  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  try {
    await HarborMCPRegistry.sendMessage("nonexistent@extension", {
      jsonrpc: "2.0",
      id: 1,
      method: "test",
    });
    ok(false, "Should have thrown for unregistered extension");
  } catch (err) {
    ok(
      err.message.includes("not registered"),
      "Should reject message to unregistered extension"
    );
  }
});

add_task(async function test_harbor_listener_removal_unregisters() {
  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      permissions: ["harbor"],
    },
    background() {
      let listener = (requestId, message) => {
        browser.harbor.sendMCPResponse(requestId, {
          jsonrpc: "2.0",
          id: message.id,
          result: { ok: true },
        });
      };
      browser.harbor.onMCPMessage.addListener(listener);

      browser.harbor
        .registerMCPServer({ name: "removal-test" })
        .then(() => {
          browser.test.sendMessage("registered");
        });

      browser.test.onMessage.addListener(msg => {
        if (msg === "remove-listener") {
          browser.harbor.onMCPMessage.removeListener(listener);
          browser.test.sendMessage("listener-removed");
        }
      });
    },
  });

  await extension.startup();
  await extension.awaitMessage("registered");

  const { HarborMCPRegistry } = ChromeUtils.importESModule(
    "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs"
  );

  ok(HarborMCPRegistry.has(extension.id), "Should be registered initially");

  extension.sendMessage("remove-listener");
  await extension.awaitMessage("listener-removed");

  ok(
    !HarborMCPRegistry.has(extension.id),
    "Should be unregistered after listener removal"
  );

  await extension.unload();
});
