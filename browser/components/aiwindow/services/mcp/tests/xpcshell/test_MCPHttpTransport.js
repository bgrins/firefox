/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPHttpTransport } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPHttpTransport.sys.mjs"
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

add_setup(async function () {
  // Start HTTP server for testing
  gHttpServer = new HttpServer();
  gHttpServer.registerPathHandler("/mcp", handleMCPRequest);
  gHttpServer.start(-1);
  gServerUrl = `http://localhost:${gHttpServer.identity.primaryPort}/mcp`;
  info(`Test server running at ${gServerUrl}`);
});

registerCleanupFunction(async () => {
  if (gHttpServer) {
    await new Promise(resolve => gHttpServer.stop(resolve));
  }
});

/**
 * Handle MCP JSON-RPC requests
 */
function handleMCPRequest(request, response) {
  response.setHeader("Content-Type", "application/json", false);
  response.setHeader("Cache-Control", "no-cache", false);

  if (request.method !== "POST") {
    response.setStatusLine("1.1", 405, "Method Not Allowed");
    response.write(JSON.stringify({
      jsonrpc: "2.0",
      error: { code: -32600, message: "Only POST requests are supported" },
      id: null,
    }));
    return;
  }

  const body = NetUtil.readInputStreamToString(
    request.bodyInputStream,
    request.bodyInputStream.available()
  );

  let message;
  try {
    message = JSON.parse(body);
  } catch (e) {
    response.setStatusLine("1.1", 400, "Bad Request");
    response.write(JSON.stringify({
      jsonrpc: "2.0",
      error: { code: -32700, message: "Parse error" },
      id: null,
    }));
    return;
  }

  const SERVER_INFO = { name: "echo", version: "1.0.0" };
  const TOOLS = [
    {
      name: "echo",
      description: "Returns the input message unchanged",
      inputSchema: {
        type: "object",
        properties: { message: { type: "string" } },
        required: ["message"],
      },
    },
    {
      name: "reverse",
      description: "Reverses a string",
      inputSchema: {
        type: "object",
        properties: { text: { type: "string" } },
        required: ["text"],
      },
    },
    {
      name: "math/add",
      description: "Adds two numbers",
      inputSchema: {
        type: "object",
        properties: {
          a: { type: "number" },
          b: { type: "number" },
        },
        required: ["a", "b"],
      },
    },
  ];

  const { method, params, id } = message;

  function sendResponse(result) {
    response.setStatusLine("1.1", 200, "OK");
    response.write(JSON.stringify({ jsonrpc: "2.0", result, id }));
  }

  function sendError(code, msg) {
    response.setStatusLine("1.1", 200, "OK");
    response.write(JSON.stringify({
      jsonrpc: "2.0",
      error: { code, message: msg },
      id,
    }));
  }

  try {
    switch (method) {
      case "initialize":
        sendResponse({
          protocolVersion: "2024-11-05",
          serverInfo: SERVER_INFO,
          capabilities: { tools: {} },
        });
        break;

      case "tools/list":
        sendResponse({ tools: TOOLS });
        break;

      case "tools/call":
        const { name, arguments: args } = params;
        let result;

        if (name === "echo") {
          result = { content: [{ type: "text", text: args.message }] };
        } else if (name === "reverse") {
          result = {
            content: [
              { type: "text", text: args.text.split("").reverse().join("") },
            ],
          };
        } else if (name === "math/add") {
          result = {
            content: [
              { type: "text", text: `${args.a} + ${args.b} = ${args.a + args.b}` },
            ],
          };
        } else {
          sendError(-32601, "Unknown tool: " + name);
          return;
        }

        sendResponse(result);
        break;

      case "ping":
        sendResponse({ pong: true, timestamp: Date.now() });
        break;

      default:
        sendError(-32601, "Method not found: " + method);
    }
  } catch (error) {
    sendError(-32603, "Internal error: " + error.message);
  }
}

/**
 * Test basic connection and initialization
 */
add_task(async function test_connect_and_initialize() {
  info("Testing MCP HTTP transport connection");

  const transport = new MCPHttpTransport(gServerUrl);

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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
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

  const transport = new MCPHttpTransport(gServerUrl);
  await transport.connect();

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

  const transport = new MCPHttpTransport(gServerUrl);
  await transport.connect();

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

  const transport = new MCPHttpTransport(gServerUrl);
  await transport.connect();

  const result = await transport.request("ping", {});

  Assert.ok(result.pong, "Should return pong");
  Assert.ok(typeof result.timestamp === "number", "Should return timestamp");

  await transport.disconnect();
});

/**
 * Test invalid URL handling
 */
add_task(async function test_invalid_url() {
  info("Testing invalid URL handling");

  const transport = new MCPHttpTransport("not-a-valid-url");

  await Assert.rejects(
    transport.connect(),
    /Invalid URL/,
    "Should reject with invalid URL error"
  );
});

/**
 * Test connection to non-existent server
 */
add_task(async function test_connection_error() {
  info("Testing connection to non-existent server");

  const transport = new MCPHttpTransport("http://localhost:1/nonexistent");

  await Assert.rejects(
    transport.connect(),
    /Failed to connect/,
    "Should reject when server is unreachable"
  );
});

/**
 * Test HTTPS enforcement (in non-release builds, should warn but allow)
 */
add_task(async function test_http_warning() {
  info("Testing HTTP connection warning");

  const transport = new MCPHttpTransport(gServerUrl); // gServerUrl is http://

  // Should connect but log warning (we're not in release build)
  await transport.connect();
  Assert.ok(transport.isConnected(), "Should connect with HTTP in dev build");

  await transport.disconnect();
});

/**
 * Test bearer token authentication
 */
add_task(async function test_bearer_token() {
  info("Testing bearer token authentication");

  const transport = new MCPHttpTransport(gServerUrl, {
    bearerToken: "test-token-123",
  });

  await transport.connect();

  // The test server doesn't validate tokens, but we can verify it connects
  Assert.ok(transport.isConnected(), "Should connect with bearer token");
  Assert.equal(
    transport.bearerToken,
    "test-token-123",
    "Bearer token should be stored"
  );

  await transport.disconnect();
});

/**
 * Test custom timeout
 */
add_task(async function test_custom_timeout() {
  info("Testing custom timeout configuration");

  const transport = new MCPHttpTransport(gServerUrl, {
    timeout: 5000,
  });

  Assert.equal(transport.timeout, 5000, "Custom timeout should be set");

  await transport.connect();
  await transport.disconnect();
});

/**
 * Test request timeout
 */
add_task(async function test_http_request_timeout() {
  info("Testing HTTP request timeout");

  const transport = new MCPHttpTransport(gServerUrl, {
    timeout: 100, // Very short timeout
  });

  await transport.connect();

  // Create a request that will timeout
  // Since the test server responds quickly, we'd need a hanging endpoint
  // For now, just verify the timeout is configured
  Assert.equal(transport.timeout, 100, "Timeout should be configured");

  await transport.disconnect();
});

add_task(async function test_case_insensitive_content_type() {
  info("Testing case-insensitive content-type handling (fix #9)");

  // Add a handler that returns uppercase content-type
  gHttpServer.registerPathHandler("/mcp-uppercase", (request, response) => {
    const body = NetUtil.readInputStreamToString(
      request.bodyInputStream,
      request.bodyInputStream.available()
    );
    const message = JSON.parse(body);

    response.setHeader("Content-Type", "Application/JSON", false);
    response.setStatusLine("1.1", 200, "OK");

    if (message.method === "initialize") {
      response.write(JSON.stringify({
        jsonrpc: "2.0",
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "test", version: "1.0.0" },
          capabilities: {},
        },
        id: message.id,
      }));
    } else {
      response.write(JSON.stringify({
        jsonrpc: "2.0",
        result: { ok: true },
        id: message.id,
      }));
    }
  });

  const transport = new MCPHttpTransport(
    `http://localhost:${gHttpServer.identity.primaryPort}/mcp-uppercase`
  );
  await transport.connect();

  const result = await transport.request("test", {});
  Assert.ok(result.ok, "Should handle uppercase content-type");

  await transport.disconnect();
});

add_task(async function test_invalid_json_response() {
  info("Testing invalid JSON response handling (fix #11)");

  let callCount = 0;
  gHttpServer.registerPathHandler("/mcp-bad-json", (request, response) => {
    const body = NetUtil.readInputStreamToString(
      request.bodyInputStream,
      request.bodyInputStream.available()
    );
    const message = JSON.parse(body);

    response.setHeader("Content-Type", "application/json", false);
    response.setStatusLine("1.1", 200, "OK");

    callCount++;
    if (callCount === 1 && message.method === "initialize") {
      // First call (init) succeeds
      response.write(JSON.stringify({
        jsonrpc: "2.0",
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "test", version: "1.0.0" },
          capabilities: {},
        },
        id: message.id,
      }));
    } else {
      // Subsequent calls return invalid JSON
      response.write("{ invalid json }");
    }
  });

  const transport = new MCPHttpTransport(
    `http://localhost:${gHttpServer.identity.primaryPort}/mcp-bad-json`
  );
  await transport.connect();

  await Assert.rejects(
    transport.request("test", {}),
    /Invalid JSON response/,
    "Should reject with JSON parse error"
  );

  await transport.disconnect();
});

add_task(async function test_abort_on_disconnect() {
  info("Testing abort controller cleanup (fix #16)");

  const transport = new MCPHttpTransport(
    `http://localhost:${gHttpServer.identity.primaryPort}/mcp`
  );
  await transport.connect();

  // Verify no abort controller before request
  Assert.equal(transport.abortController, null, "Should start with no abort controller");

  // Make a request to list tools
  await transport.listTools();

  // Verify abort controller is cleaned up after request completes
  Assert.equal(transport.abortController, null, "Should clean up abort controller after request");

  await transport.disconnect();
});

add_task(async function test_retry_logic() {
  info("Testing retry logic for transient failures (fix #17)");

  let attemptCount = 0;
  gHttpServer.registerPathHandler("/mcp-retry", (request, response) => {
    const message = JSON.parse(NetUtil.readInputStreamToString(
      request.bodyInputStream,
      request.bodyInputStream.available()
    ));

    response.setHeader("Content-Type", "application/json", false);

    if (message.method === "initialize") {
      // Initialize always succeeds
      response.setStatusLine("1.1", 200, "OK");
      response.write(JSON.stringify({
        jsonrpc: "2.0",
        result: {
          protocolVersion: "2024-11-05",
          serverInfo: { name: "retry-test", version: "1.0.0" },
          capabilities: {},
        },
        id: message.id,
      }));
    } else {
      // Test requests fail first 2 times
      attemptCount++;
      if (attemptCount < 3) {
        response.setStatusLine("1.1", 500, "Internal Server Error");
        return;
      }
      response.setStatusLine("1.1", 200, "OK");
      response.write(JSON.stringify({
        jsonrpc: "2.0",
        result: { success: true, attempts: attemptCount },
        id: message.id,
      }));
    }
  });

  const transport = new MCPHttpTransport(
    `http://localhost:${gHttpServer.identity.primaryPort}/mcp-retry`,
    { maxRetries: 3, retryDelay: 10 }
  );
  await transport.connect();

  const result = await transport.request("test", {});
  Assert.equal(result.attempts, 3, "Should succeed on 3rd attempt");
  Assert.ok(attemptCount >= 3, "Should have made at least 3 attempts");

  await transport.disconnect();
});
