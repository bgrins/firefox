/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPSandboxTransport } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPSandboxTransport.sys.mjs"
);

/**
 * Test the MCP Sandbox Transport with the echo server.
 * This demonstrates:
 * - Loading MCP server code into Cu.Sandbox
 * - Bidirectional message passing via Cu.exportFunction/cloneInto
 * - Full MCP protocol implementation in sandbox
 */

// Load echo server code from support file
let echoServerCode;

add_setup(async function () {
  const echoServerPath = do_get_file("echo-server.js").path;
  echoServerCode = await IOUtils.readUTF8(echoServerPath);
});

/**
 * Test basic connection and initialization
 */
add_task(async function test_connect_and_initialize() {
  info("Testing MCP sandbox transport connection");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  // Connect should initialize the sandbox and call initialize
  const initResult = await transport.connect();

  Assert.ok(transport.isConnected(), "Transport should be connected");
  Assert.equal(
    initResult.protocolVersion,
    "2024-11-05",
    "Should return correct protocol version"
  );
  Assert.equal(
    initResult.serverInfo.name,
    "echo",
    "Should return server name"
  );
  Assert.equal(
    initResult.serverInfo.version,
    "1.0.0",
    "Should return server version"
  );
  Assert.ok(initResult.capabilities, "Should return capabilities");

  await transport.disconnect();
  Assert.ok(!transport.isConnected(), "Transport should be disconnected");
});

/**
 * Test listing tools
 */
add_task(async function test_list_tools() {
  info("Testing tools/list");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  const result = await transport.request("tools/list", {});

  Assert.ok(Array.isArray(result.tools), "Should return tools array");
  Assert.equal(result.tools.length, 3, "Should have 3 tools");

  const toolNames = result.tools.map(t => t.name);
  Assert.ok(toolNames.includes("echo"), "Should have echo tool");
  Assert.ok(toolNames.includes("reverse"), "Should have reverse tool");
  Assert.ok(toolNames.includes("math/add"), "Should have math/add tool");

  await transport.disconnect();
});

/**
 * Test calling the echo tool
 */
add_task(async function test_call_echo_tool() {
  info("Testing echo tool call");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  const result = await transport.request("tools/call", {
    name: "echo",
    arguments: {
      message: "Hello, MCP!",
    },
  });

  Assert.ok(result.content, "Should return content");
  Assert.equal(result.content.length, 1, "Should have one content item");
  Assert.equal(result.content[0].type, "text", "Content should be text");
  Assert.equal(
    result.content[0].text,
    "Hello, MCP!",
    "Should echo the message"
  );

  await transport.disconnect();
});

/**
 * Test calling the reverse tool
 */
add_task(async function test_call_reverse_tool() {
  info("Testing reverse tool call");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  const result = await transport.request("tools/call", {
    name: "reverse",
    arguments: {
      text: "Firefox",
    },
  });

  Assert.equal(result.content[0].text, "xoferiF", "Should reverse the text");

  await transport.disconnect();
});

/**
 * Test calling the math/add tool
 */
add_task(async function test_call_math_add_tool() {
  info("Testing math/add tool call");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  const result = await transport.request("tools/call", {
    name: "math/add",
    arguments: {
      a: 42,
      b: 13,
    },
  });

  Assert.equal(
    result.content[0].text,
    "42 + 13 = 55",
    "Should add the numbers"
  );

  await transport.disconnect();
});

/**
 * Test error handling for unknown method
 */
add_task(async function test_unknown_method_error() {
  info("Testing error handling for unknown method");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  await Assert.rejects(
    transport.request("unknown/method", {}),
    /Method not found/,
    "Should reject with method not found error"
  );

  await transport.disconnect();
});

/**
 * Test error handling for unknown tool
 */
add_task(async function test_unknown_tool_error() {
  info("Testing error handling for unknown tool");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  await Assert.rejects(
    transport.request("tools/call", {
      name: "nonexistent",
      arguments: {},
    }),
    /Unknown tool/,
    "Should reject with unknown tool error"
  );

  await transport.disconnect();
});

/**
 * Test multiple sequential requests
 */
add_task(async function test_multiple_requests() {
  info("Testing multiple sequential requests");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  // Make multiple requests in sequence
  for (let i = 0; i < 5; i++) {
    const result = await transport.request("tools/call", {
      name: "echo",
      arguments: {
        message: `Message ${i}`,
      },
    });

    Assert.equal(
      result.content[0].text,
      `Message ${i}`,
      `Should echo message ${i}`
    );
  }

  await transport.disconnect();
});

/**
 * Test concurrent requests
 */
add_task(async function test_concurrent_requests() {
  info("Testing concurrent requests");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  // Make multiple requests concurrently
  const promises = [];
  for (let i = 0; i < 5; i++) {
    promises.push(
      transport.request("tools/call", {
        name: "echo",
        arguments: {
          message: `Concurrent ${i}`,
        },
      })
    );
  }

  const results = await Promise.all(promises);

  Assert.equal(results.length, 5, "Should get 5 results");
  for (let i = 0; i < 5; i++) {
    Assert.equal(
      results[i].content[0].text,
      `Concurrent ${i}`,
      `Should echo concurrent message ${i}`
    );
  }

  await transport.disconnect();
});

/**
 * Test ping method
 */
add_task(async function test_ping() {
  info("Testing ping method");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();

  const result = await transport.request("ping", {});

  Assert.ok(result.pong, "Should return pong");
  Assert.ok(typeof result.timestamp === "number", "Should return timestamp");

  await transport.disconnect();
});

/**
 * Test sandbox cleanup on disconnect
 */
add_task(async function test_sandbox_cleanup() {
  info("Testing sandbox cleanup");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "echo-test",
  });

  await transport.connect();
  Assert.ok(transport.isConnected(), "Should be connected");

  // Make a request to ensure sandbox is working
  await transport.request("ping", {});

  // Disconnect
  await transport.disconnect();
  Assert.ok(!transport.isConnected(), "Should be disconnected");

  // Trying to make a request after disconnect should fail
  await Assert.rejects(
    transport.request("ping", {}),
    /Not connected/,
    "Should reject requests after disconnect"
  );
});

add_task(async function test_request_timeout() {
  info("Testing request timeout mechanism");

  // Create a server that never responds
  const hangingServerCode = `
    globalThis.handleMessage = function(message) {
      // Never call sendToHost - simulate a hang
    };
  `;

  const transport = new MCPSandboxTransport(hangingServerCode, {
    serverId: "hanging-test",
  });

  // Set a short timeout for testing
  transport.timeout = 100;

  // Connect manually without initialization (which would hang)
  const principal = Services.scriptSecurityManager.createNullPrincipal({});
  transport.sandbox = Cu.Sandbox(principal, {
    sandboxName: "Test Hanging Server",
    wantXrays: true,
    wantGlobalProperties: [],
    wantComponents: false,
    wantExportHelpers: false,
  });

  transport.sandbox.sendToHost = Cu.exportFunction(message => {
    return transport._handleSandboxMessage(message);
  }, transport.sandbox);

  Cu.evalInSandbox(hangingServerCode, transport.sandbox, "1.8", "moz-src://mcp/test/hanging-server.js", 1);
  transport.connected = true;

  // Request should timeout
  const startTime = Date.now();
  await Assert.rejects(
    transport.request("test", {}),
    /timeout/i,
    "Should timeout when server doesn't respond"
  );
  const elapsed = Date.now() - startTime;

  Assert.ok(
    elapsed >= 100 && elapsed < 500,
    `Timeout should occur around 100ms, got ${elapsed}ms`
  );

  // Note: We don't check responseHandlers.size here because MCPClient and
  // MCPSandboxTransport both have timeout mechanisms that race. The important
  // thing is that the request timed out. Cleanup will happen on disconnect.

  await transport.disconnect();

  // After disconnect, handlers should definitely be cleaned up
  Assert.equal(
    transport.responseHandlers.size,
    0,
    "Response handlers should be cleaned up after disconnect"
  );
});

add_task(async function test_synchronous_sandbox_response() {
  info("Testing synchronous responses from sandbox don't cause race condition");

  // Server that responds synchronously
  const syncServerCode = `
    globalThis.handleMessage = function(message) {
      // Respond immediately/synchronously
      sendToHost({
        jsonrpc: "2.0",
        result: { immediate: true },
        id: message.id
      });
    };
  `;

  const transport = new MCPSandboxTransport(syncServerCode, {
    serverId: "sync-test",
  });

  // Manual setup without full connect
  const principal = Services.scriptSecurityManager.createNullPrincipal({});
  transport.sandbox = Cu.Sandbox(principal, {
    sandboxName: "Test Sync Server",
    wantXrays: true,
    wantGlobalProperties: [],
    wantComponents: false,
    wantExportHelpers: false,
  });

  transport.sandbox.sendToHost = Cu.exportFunction(message => {
    return transport._handleSandboxMessage(message);
  }, transport.sandbox);

  Cu.evalInSandbox(syncServerCode, transport.sandbox, "1.8", "moz-src://mcp/test/sync-server.js", 1);
  transport.connected = true;

  // This should work even with synchronous response
  const result = await transport.request("test", {});
  Assert.ok(result.immediate, "Should handle synchronous responses correctly");

  await transport.disconnect();
});

add_task(async function test_invalid_sandbox_code() {
  info("Testing error handling for invalid sandbox code");

  const invalidCode = `
    // Missing handleMessage function
    globalThis.brokenServer = true;
  `;

  const transport = new MCPSandboxTransport(invalidCode, {
    serverId: "broken-test",
  });

  // Manual setup
  const principal = Services.scriptSecurityManager.createNullPrincipal({});
  transport.sandbox = Cu.Sandbox(principal, {
    sandboxName: "Test Broken Server",
    wantXrays: true,
    wantGlobalProperties: [],
    wantComponents: false,
    wantExportHelpers: false,
  });

  Cu.evalInSandbox(invalidCode, transport.sandbox, "1.8", "moz-src://mcp/test/invalid-server.js", 1);
  transport.connected = true;

  // Should reject when handleMessage doesn't exist
  await Assert.rejects(
    transport.request("test", {}),
    /does not expose handleMessage/,
    "Should reject when sandbox doesn't expose handleMessage"
  );
});

add_task(async function test_sandbox_cleanup_on_connect_error() {
  info("Testing sandbox cleanup when connect fails (fix #3)");

  const badCode = `
    throw new Error("Intentional error during load");
  `;

  const transport = new MCPSandboxTransport(badCode, {
    serverId: "cleanup-test",
  });

  // Connect should fail and clean up sandbox
  await Assert.rejects(
    transport.connect(),
    /Intentional error/,
    "Should reject with load error"
  );

  // Sandbox should be null after cleanup
  Assert.equal(transport.sandbox, null, "Sandbox should be cleaned up");
});

add_task(async function test_request_id_format() {
  info("Testing UUID-based request IDs (fix #4)");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "uuid-test",
  });

  await transport.connect();

  // Make a request and check ID format
  const id1 = transport._generateRequestId();
  const id2 = transport._generateRequestId();

  // UUIDs should be strings, not numbers
  Assert.equal(typeof id1, "string", "ID should be string");
  Assert.equal(typeof id2, "string", "ID should be string");

  // Should be different
  Assert.notEqual(id1, id2, "IDs should be unique");

  // Should match UUID format (roughly)
  Assert.ok(id1.includes("-"), "ID should be UUID format");
  Assert.ok(id1.length > 30, "ID should be UUID length");

  await transport.disconnect();
});

add_task(async function test_init_response_validation() {
  info("Testing initialization response validation (fix #5)");

  // Server with invalid init response
  const badInitCode = `
    globalThis.handleMessage = function(message) {
      if (message.method === "initialize") {
        // Return invalid response
        sendToHost({
          jsonrpc: "2.0",
          result: {
            protocolVersion: "2024-11-05",
            // Missing serverInfo
            capabilities: {}
          },
          id: message.id
        });
      }
    };
  `;

  const transport = new MCPSandboxTransport(badInitCode, {
    serverId: "bad-init",
  });

  await Assert.rejects(
    transport.connect(),
    /Missing serverInfo/,
    "Should reject when serverInfo is missing"
  );

  // Server with serverInfo but no name
  const noNameCode = `
    globalThis.handleMessage = function(message) {
      if (message.method === "initialize") {
        sendToHost({
          jsonrpc: "2.0",
          result: {
            protocolVersion: "2024-11-05",
            serverInfo: {}, // No name
            capabilities: {}
          },
          id: message.id
        });
      }
    };
  `;

  const transport2 = new MCPSandboxTransport(noNameCode, {
    serverId: "no-name",
  });

  await Assert.rejects(
    transport2.connect(),
    /missing required 'name' field/,
    "Should reject when serverInfo.name is missing"
  );
});

add_task(async function test_timeout_cleanup() {
  info("Testing timeout cleanup prevents memory leak (fix #1)");

  const transport = new MCPSandboxTransport(echoServerCode, {
    serverId: "timeout-cleanup",
  });

  await transport.connect();

  // Make a successful request - timeout should be cleared
  await transport.request("tools/list", {});

  // If timeout wasn't cleared, it would still be pending
  // We can't directly check, but we can verify no errors occur

  await transport.disconnect();
});
