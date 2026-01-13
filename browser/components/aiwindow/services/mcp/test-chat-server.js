/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Simple Test MCP Server for Chat Integration
 *
 * This server provides a simple "hello_mcp" tool to validate
 * that MCP tools can be called from the Chat interface.
 */

(function () {
  "use strict";

  const SERVER_INFO = {
    name: "test-chat-server",
    version: "1.0.0",
  };

  const TOOLS = [
    {
      name: "hello_mcp",
      description:
        "A test tool that returns a greeting message to confirm MCP integration is working",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "Name to greet (optional)",
          },
        },
      },
    },
  ];

  globalThis.handleMessage = function (message) {
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
            capabilities: { tools: {} },
          });
          break;

        case "tools/list":
          sendResponse({ tools: TOOLS });
          break;

        case "tools/call":
          const { name, arguments: args } = params;

          if (name === "hello_mcp") {
            const greetName = args?.name || "World";
            const message = `Hello ${greetName}! This message comes from an MCP tool running in a Firefox sandbox. The MCP integration is working! 🎉`;

            sendResponse({
              content: [{ type: "text", text: message }],
            });
          } else {
            sendError(-32601, "Unknown tool: " + name);
          }
          break;

        default:
          sendError(-32601, "Method not found: " + method);
      }
    } catch (error) {
      sendError(-32603, "Internal error: " + error.message);
    }
  };
})();
