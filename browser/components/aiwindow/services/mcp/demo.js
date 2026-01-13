#!/usr/bin/env -S firefox --headless --chrome
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * MCP Sandbox Transport Demo
 *
 * This is a standalone demo that shows the MCP sandbox transport in action.
 * Run this in the Browser Console to see it work.
 *
 * Usage:
 * 1. Open Firefox
 * 2. Open Browser Console (Ctrl+Shift+J)
 * 3. Copy and paste this entire file
 * 4. Press Enter
 */

(async function mcpSandboxDemo() {
  console.log("=== MCP Sandbox Transport Demo ===\n");

  // The echo server code (this would normally be loaded from a file)
  const echoServerCode = `
    (function() {
      "use strict";

      const SERVER_INFO = { name: "echo", version: "1.0.0" };

      const TOOLS = [
        {
          name: "echo",
          description: "Returns the input message unchanged",
          inputSchema: {
            type: "object",
            properties: {
              message: { type: "string" }
            },
            required: ["message"]
          }
        },
        {
          name: "reverse",
          description: "Reverses a string",
          inputSchema: {
            type: "object",
            properties: {
              text: { type: "string" }
            },
            required: ["text"]
          }
        },
        {
          name: "math/add",
          description: "Adds two numbers",
          inputSchema: {
            type: "object",
            properties: {
              a: { type: "number" },
              b: { type: "number" }
            },
            required: ["a", "b"]
          }
        }
      ];

      globalThis.handleMessage = function(message) {
        const { method, params, id } = message;

        function sendResponse(result) {
          sendToHost({ jsonrpc: "2.0", result, id });
        }

        function sendError(code, msg) {
          sendToHost({ jsonrpc: "2.0", error: { code, message: msg }, id });
        }

        try {
          switch (method) {
            case "initialize":
              sendResponse({
                protocolVersion: "2024-11-05",
                serverInfo: SERVER_INFO,
                capabilities: { tools: {} }
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
                result = { content: [{ type: "text", text: args.text.split("").reverse().join("") }] };
              } else if (name === "math/add") {
                result = { content: [{ type: "text", text: \`\${args.a} + \${args.b} = \${args.a + args.b}\` }] };
              } else {
                sendError(-32601, "Unknown tool: " + name);
                return;
              }

              sendResponse(result);
              break;

            default:
              sendError(-32601, "Method not found: " + method);
          }
        } catch (error) {
          sendError(-32603, "Internal error: " + error.message);
        }
      };
    })();
  `;

  // Simple inline transport implementation for demo
  class MCPSandboxTransport {
    constructor(serverCode, serverId = "demo") {
      this.serverCode = serverCode;
      this.serverId = serverId;
      this.sandbox = null;
      this.responseHandlers = new Map();
      this.nextRequestId = 1;
    }

    async connect() {
      const principal = Services.scriptSecurityManager.createNullPrincipal({});

      this.sandbox = Cu.Sandbox(principal, {
        sandboxName: `MCP Demo: ${this.serverId}`,
        wantXrays: true,
        wantGlobalProperties: [],
        wantComponents: false,
      });

      this.sandbox.sendToHost = Cu.exportFunction(message => {
        const msg = Cu.cloneInto(message, {});
        if (msg.id && this.responseHandlers.has(msg.id)) {
          const { resolve, reject } = this.responseHandlers.get(msg.id);
          this.responseHandlers.delete(msg.id);
          msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
        }
      }, this.sandbox);

      this.sandbox.console = Cu.cloneInto(
        {
          log: (...args) => console.log(`[Sandbox]`, ...args),
        },
        this.sandbox,
        { cloneFunctions: true }
      );

      Cu.evalInSandbox(this.serverCode, this.sandbox, "1.8", "mcp-server.js", 1);

      return this.request("initialize", {
        protocolVersion: "2024-11-05",
        clientInfo: { name: "firefox-demo", version: "1.0" },
      });
    }

    async request(method, params = {}) {
      const id = this.nextRequestId++;
      return new Promise((resolve, reject) => {
        this.responseHandlers.set(id, { resolve, reject });
        const message = Cu.cloneInto({ jsonrpc: "2.0", method, params, id }, this.sandbox);
        this.sandbox.handleMessage(message);
      });
    }

    disconnect() {
      if (this.sandbox) {
        Cu.nukeSandbox(this.sandbox);
        this.sandbox = null;
      }
    }
  }

  try {
    // Create transport
    console.log("1. Creating MCP sandbox transport...");
    const transport = new MCPSandboxTransport(echoServerCode);

    // Connect
    console.log("\n2. Connecting and initializing...");
    const initResult = await transport.connect();
    console.log("   ✓ Connected to:", initResult.serverInfo.name, initResult.serverInfo.version);

    // List tools
    console.log("\n3. Listing available tools...");
    const toolsResult = await transport.request("tools/list", {});
    console.log(`   ✓ Found ${toolsResult.tools.length} tools:`);
    toolsResult.tools.forEach(tool => {
      console.log(`     - ${tool.name}: ${tool.description}`);
    });

    // Call echo tool
    console.log("\n4. Calling 'echo' tool...");
    const echoResult = await transport.request("tools/call", {
      name: "echo",
      arguments: { message: "Hello from Firefox!" },
    });
    console.log("   ✓ Result:", echoResult.content[0].text);

    // Call reverse tool
    console.log("\n5. Calling 'reverse' tool...");
    const reverseResult = await transport.request("tools/call", {
      name: "reverse",
      arguments: { text: "MCP Sandbox" },
    });
    console.log("   ✓ Result:", reverseResult.content[0].text);

    // Call math/add tool
    console.log("\n6. Calling 'math/add' tool...");
    const addResult = await transport.request("tools/call", {
      name: "math/add",
      arguments: { a: 42, b: 13 },
    });
    console.log("   ✓ Result:", addResult.content[0].text);

    // Test concurrent requests
    console.log("\n7. Testing 5 concurrent requests...");
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(
        transport.request("tools/call", {
          name: "echo",
          arguments: { message: `Concurrent request ${i}` },
        })
      );
    }
    const results = await Promise.all(promises);
    console.log(`   ✓ All ${results.length} requests completed successfully`);
    results.forEach((r, i) => {
      console.log(`     ${i}: ${r.content[0].text}`);
    });

    // Disconnect
    console.log("\n8. Disconnecting...");
    transport.disconnect();
    console.log("   ✓ Disconnected and sandbox destroyed");

    console.log("\n=== Demo Complete! ===");
    console.log("\n✅ MCP Sandbox Transport POC is working!");
    console.log("   - Cu.Sandbox can run MCP server code");
    console.log("   - Message passing works bidirectionally");
    console.log("   - Multiple concurrent requests work");
    console.log("   - Full MCP protocol implemented in sandbox");
  } catch (error) {
    console.error("\n❌ Demo failed:", error);
    console.error(error.stack);
  }
})();
