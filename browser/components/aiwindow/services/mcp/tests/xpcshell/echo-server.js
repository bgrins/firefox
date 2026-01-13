/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

/**
 * Echo MCP Server - Test Implementation
 *
 * A simple MCP server for testing that provides:
 * - echo: Returns input unchanged
 * - reverse: Reverses a string
 * - math/add: Adds two numbers
 */

(function () {
  "use strict";

  const SERVER_INFO = {
    name: "echo",
    version: "1.0.0",
  };

  const TOOLS = [
    {
      name: "echo",
      description: "Returns the input message unchanged",
      inputSchema: {
        type: "object",
        properties: {
          message: { type: "string" },
        },
        required: ["message"],
      },
    },
    {
      name: "reverse",
      description: "Reverses a string",
      inputSchema: {
        type: "object",
        properties: {
          text: { type: "string" },
        },
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

  // Main message handler exposed to sandbox host
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
            capabilities: {
              tools: {},
            },
          });
          break;

        case "tools/list":
          sendResponse({ tools: TOOLS });
          break;

        case "tools/call":
          const { name, arguments: args } = params;
          let result;

          if (name === "echo") {
            result = {
              content: [{ type: "text", text: args.message }],
            };
          } else if (name === "reverse") {
            result = {
              content: [
                {
                  type: "text",
                  text: args.text.split("").reverse().join(""),
                },
              ],
            };
          } else if (name === "math/add") {
            result = {
              content: [
                {
                  type: "text",
                  text: `${args.a} + ${args.b} = ${args.a + args.b}`,
                },
              ],
            };
          } else {
            sendError(-32601, "Unknown tool: " + name);
            return;
          }

          sendResponse(result);
          break;

        case "ping":
          sendResponse({
            pong: true,
            timestamp: Date.now(),
          });
          break;

        default:
          sendError(-32601, "Method not found: " + method);
      }
    } catch (error) {
      sendError(-32603, "Internal error: " + error.message);
    }
  };
})();
