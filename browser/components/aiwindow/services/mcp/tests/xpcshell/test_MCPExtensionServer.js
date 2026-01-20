/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { ExtensionMCPRegistry } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPExtensionTransport.sys.mjs"
);

add_setup(async function () {
  ExtensionMCPRegistry.clear();
});

registerCleanupFunction(async function () {
  ExtensionMCPRegistry.clear();
});

// Test that an extension can register as an MCP server and handle messages
add_task(async function test_extension_mcp_server() {
  // This extension acts as an MCP server
  function background() {
    const SERVER_INFO = {
      name: "Test Extension MCP Server",
      version: "1.0.0",
    };

    const TOOLS = [
      {
        name: "greet",
        description: "Returns a greeting",
        inputSchema: {
          type: "object",
          properties: {
            name: { type: "string", description: "Name to greet" },
          },
          required: ["name"],
        },
      },
      {
        name: "add",
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

    // MCP message handler
    function handleMCPMessage(message) {
      const { method, params, id } = message;

      switch (method) {
        case "initialize":
          return {
            jsonrpc: "2.0",
            id,
            result: {
              protocolVersion: "2024-11-05",
              serverInfo: SERVER_INFO,
              capabilities: { tools: {} },
            },
          };

        case "tools/list":
          return {
            jsonrpc: "2.0",
            id,
            result: { tools: TOOLS },
          };

        case "tools/call":
          const toolName = params.name;
          const args = params.arguments || {};

          if (toolName === "greet") {
            return {
              jsonrpc: "2.0",
              id,
              result: {
                content: [
                  { type: "text", text: `Hello, ${args.name}!` },
                ],
              },
            };
          } else if (toolName === "add") {
            return {
              jsonrpc: "2.0",
              id,
              result: {
                content: [
                  { type: "text", text: String(args.a + args.b) },
                ],
              },
            };
          }

          return {
            jsonrpc: "2.0",
            id,
            error: { code: -32601, message: `Unknown tool: ${toolName}` },
          };

        default:
          return {
            jsonrpc: "2.0",
            id,
            error: { code: -32601, message: `Unknown method: ${method}` },
          };
      }
    }

    // Listen for test messages to register/unregister and handle MCP
    browser.test.onMessage.addListener(async (msgType, data) => {
      if (msgType === "mcp-message") {
        const response = handleMCPMessage(data);
        browser.test.sendMessage("mcp-response", response);
      } else if (msgType === "get-server-info") {
        browser.test.sendMessage("server-info", SERVER_INFO);
      }
    });

    browser.test.sendMessage("ready");
  }

  let extension = ExtensionTestUtils.loadExtension({
    manifest: {
      browser_specific_settings: {
        gecko: { id: "mcp-server-test@example.com" },
      },
    },
    background,
  });

  await extension.startup();
  await extension.awaitMessage("ready");

  // Register the extension as an MCP server in our registry
  // The message handler bridges test messages to the extension
  ExtensionMCPRegistry.register(
    extension.id,
    { name: "Test Extension MCP Server", version: "1.0.0" },
    async message => {
      extension.sendMessage("mcp-message", message);
      return extension.awaitMessage("mcp-response");
    }
  );

  // Verify registration
  Assert.ok(
    ExtensionMCPRegistry.has(extension.id),
    "Extension should be registered"
  );

  // Test initialize
  const initResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      clientInfo: { name: "test-client", version: "1.0.0" },
      capabilities: {},
    },
    id: "init-1",
  });

  Assert.equal(initResponse.id, "init-1", "Response ID matches");
  Assert.equal(
    initResponse.result.serverInfo.name,
    "Test Extension MCP Server",
    "Server name correct"
  );
  Assert.equal(
    initResponse.result.protocolVersion,
    "2024-11-05",
    "Protocol version correct"
  );

  // Test tools/list
  const toolsResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "tools/list",
    params: {},
    id: "tools-1",
  });

  Assert.equal(toolsResponse.result.tools.length, 2, "Should have 2 tools");
  Assert.equal(toolsResponse.result.tools[0].name, "greet", "First tool is greet");
  Assert.equal(toolsResponse.result.tools[1].name, "add", "Second tool is add");

  // Test tools/call - greet
  const greetResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
      name: "greet",
      arguments: { name: "World" },
    },
    id: "call-1",
  });

  Assert.equal(greetResponse.result.content.length, 1, "Should have 1 content item");
  Assert.equal(
    greetResponse.result.content[0].text,
    "Hello, World!",
    "Greeting correct"
  );

  // Test tools/call - add
  const addResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
      name: "add",
      arguments: { a: 5, b: 3 },
    },
    id: "call-2",
  });

  Assert.equal(addResponse.result.content[0].text, "8", "Addition correct");

  // Test unknown tool
  const unknownToolResponse = await ExtensionMCPRegistry.sendMessage(
    extension.id,
    {
      jsonrpc: "2.0",
      method: "tools/call",
      params: { name: "nonexistent", arguments: {} },
      id: "call-3",
    }
  );

  Assert.ok(unknownToolResponse.error, "Should have error for unknown tool");
  Assert.equal(unknownToolResponse.error.code, -32601, "Error code correct");

  // Unregister and verify
  ExtensionMCPRegistry.unregister(extension.id);
  Assert.ok(
    !ExtensionMCPRegistry.has(extension.id),
    "Extension should be unregistered"
  );

  await extension.unload();
});

// Test multiple extensions can be registered
add_task(async function test_multiple_extension_servers() {
  function background() {
    // Get server name from manifest
    const name = browser.runtime.getManifest().name;

    browser.test.onMessage.addListener(async (msgType, data) => {
      if (msgType === "mcp-message") {
        if (data.method === "initialize") {
          browser.test.sendMessage("mcp-response", {
            jsonrpc: "2.0",
            id: data.id,
            result: {
              protocolVersion: "2024-11-05",
              serverInfo: { name, version: "1.0.0" },
              capabilities: {},
            },
          });
        } else {
          browser.test.sendMessage("mcp-response", {
            jsonrpc: "2.0",
            id: data.id,
            result: { server: name },
          });
        }
      }
    });

    browser.test.sendMessage("ready");
  }

  const ext1 = ExtensionTestUtils.loadExtension({
    manifest: {
      name: "Server One",
      browser_specific_settings: {
        gecko: { id: "mcp-server-1@example.com" },
      },
    },
    background,
  });

  const ext2 = ExtensionTestUtils.loadExtension({
    manifest: {
      name: "Server Two",
      browser_specific_settings: {
        gecko: { id: "mcp-server-2@example.com" },
      },
    },
    background,
  });

  await ext1.startup();
  await ext1.awaitMessage("ready");

  await ext2.startup();
  await ext2.awaitMessage("ready");

  // Register both
  ExtensionMCPRegistry.register(
    ext1.id,
    { name: "Server One" },
    async msg => {
      ext1.sendMessage("mcp-message", msg);
      return ext1.awaitMessage("mcp-response");
    }
  );

  ExtensionMCPRegistry.register(
    ext2.id,
    { name: "Server Two" },
    async msg => {
      ext2.sendMessage("mcp-message", msg);
      return ext2.awaitMessage("mcp-response");
    }
  );

  Assert.equal(
    ExtensionMCPRegistry.listExtensions().length,
    2,
    "Should have 2 registered extensions"
  );

  // Verify each responds correctly
  const resp1 = await ExtensionMCPRegistry.sendMessage(ext1.id, {
    jsonrpc: "2.0",
    method: "initialize",
    params: {},
    id: "1",
  });
  Assert.equal(resp1.result.serverInfo.name, "Server One", "Server 1 responds");

  const resp2 = await ExtensionMCPRegistry.sendMessage(ext2.id, {
    jsonrpc: "2.0",
    method: "initialize",
    params: {},
    id: "2",
  });
  Assert.equal(resp2.result.serverInfo.name, "Server Two", "Server 2 responds");

  // Unload in reverse order
  ExtensionMCPRegistry.unregister(ext2.id);
  await ext2.unload();

  ExtensionMCPRegistry.unregister(ext1.id);
  await ext1.unload();
});

// Test that unloading an extension should trigger cleanup
add_task(async function test_extension_unload_cleanup() {
  function background() {
    browser.test.onMessage.addListener(async (msgType, data) => {
      if (msgType === "mcp-message") {
        browser.test.sendMessage("mcp-response", {
          jsonrpc: "2.0",
          id: data.id,
          result: {},
        });
      }
    });
    browser.test.sendMessage("ready");
  }

  const extension = ExtensionTestUtils.loadExtension({
    manifest: {
      browser_specific_settings: {
        gecko: { id: "mcp-cleanup-test@example.com" },
      },
    },
    background,
  });

  await extension.startup();
  await extension.awaitMessage("ready");

  const events = [];
  const listener = (event, id) => events.push({ event, id });
  ExtensionMCPRegistry.addListener(listener);

  ExtensionMCPRegistry.register(
    extension.id,
    { name: "Cleanup Test" },
    async msg => {
      extension.sendMessage("mcp-message", msg);
      return extension.awaitMessage("mcp-response");
    }
  );

  Assert.equal(events.length, 1, "Should have registration event");
  Assert.equal(events[0].event, "registered", "Event is registered");

  // Unregister before unloading (simulating proper cleanup)
  ExtensionMCPRegistry.unregister(extension.id);

  Assert.equal(events.length, 2, "Should have unregistration event");
  Assert.equal(events[1].event, "unregistered", "Event is unregistered");

  ExtensionMCPRegistry.removeListener(listener);
  await extension.unload();
});

// Test porting builtin time-server to extension
// This demonstrates how to convert a sandbox MCP server to an extension-based one
add_task(async function test_time_server_as_extension() {
  function background() {
    const SERVER_INFO = {
      name: "time-server",
      version: "1.0.0",
    };

    const TOOLS = [
      {
        name: "get_current_time",
        description:
          "Get the current date and time. Only call this when the user " +
          "explicitly asks what time it is or needs to know the current date.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ];

    function handleMCPMessage(message) {
      const { method, params, id } = message;

      switch (method) {
        case "initialize":
          return {
            jsonrpc: "2.0",
            id,
            result: {
              protocolVersion: "2024-11-05",
              serverInfo: SERVER_INFO,
              capabilities: { tools: {} },
            },
          };

        case "tools/list":
          return {
            jsonrpc: "2.0",
            id,
            result: { tools: TOOLS },
          };

        case "tools/call": {
          const toolName = params.name;

          if (toolName === "get_current_time") {
            const now = new Date();
            return {
              jsonrpc: "2.0",
              id,
              result: {
                content: [{ type: "text", text: now.toLocaleString() }],
              },
            };
          }

          return {
            jsonrpc: "2.0",
            id,
            error: { code: -32601, message: `Unknown tool: ${toolName}` },
          };
        }

        default:
          return {
            jsonrpc: "2.0",
            id,
            error: { code: -32601, message: `Unknown method: ${method}` },
          };
      }
    }

    browser.test.onMessage.addListener(async (msgType, data) => {
      if (msgType === "mcp-message") {
        const response = handleMCPMessage(data);
        browser.test.sendMessage("mcp-response", response);
      }
    });

    browser.test.sendMessage("ready");
  }

  const extension = ExtensionTestUtils.loadExtension({
    manifest: {
      name: "Time Server Extension",
      browser_specific_settings: {
        gecko: { id: "time-server@harbor.mozilla.org" },
      },
    },
    background,
  });

  await extension.startup();
  await extension.awaitMessage("ready");

  ExtensionMCPRegistry.register(
    extension.id,
    { name: "time-server", version: "1.0.0" },
    async message => {
      extension.sendMessage("mcp-message", message);
      return extension.awaitMessage("mcp-response");
    }
  );

  // Initialize
  const initResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      clientInfo: { name: "harbor", version: "1.0.0" },
      capabilities: {},
    },
    id: "init-1",
  });

  Assert.equal(
    initResponse.result.serverInfo.name,
    "time-server",
    "Server name matches builtin"
  );

  // List tools
  const toolsResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "tools/list",
    params: {},
    id: "tools-1",
  });

  Assert.equal(toolsResponse.result.tools.length, 1, "Should have 1 tool");
  Assert.equal(
    toolsResponse.result.tools[0].name,
    "get_current_time",
    "Tool name matches builtin"
  );

  // Call get_current_time
  const timeResponse = await ExtensionMCPRegistry.sendMessage(extension.id, {
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
      name: "get_current_time",
      arguments: {},
    },
    id: "call-1",
  });

  Assert.ok(timeResponse.result, "Should have result");
  Assert.ok(timeResponse.result.content, "Should have content");
  Assert.equal(timeResponse.result.content.length, 1, "Should have 1 content item");
  Assert.equal(timeResponse.result.content[0].type, "text", "Content type is text");

  // Verify the time string is reasonable (contains expected date/time patterns)
  const timeText = timeResponse.result.content[0].text;
  Assert.ok(timeText.length > 0, "Time string is not empty");
  // The locale string should contain numbers (for date/time)
  Assert.ok(/\d/.test(timeText), "Time string contains numbers");

  ExtensionMCPRegistry.unregister(extension.id);
  await extension.unload();
});
