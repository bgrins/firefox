/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* global browser */

/**
 * Time Server MCP Extension
 *
 * This extension acts as an MCP server providing time-related tools.
 * It uses the browser.harbor API to communicate with Harbor.
 */

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

// Use the Harbor API to register as an MCP server
browser.harbor.onMCPMessage.addListener((requestId, message) => {
  const response = handleMCPMessage(message);
  browser.harbor.sendMCPResponse(requestId, response);
});

browser.harbor
  .registerMCPServer({
    name: SERVER_INFO.name,
    version: SERVER_INFO.version,
    description: "Provides current time functionality",
  })
  .catch(err => {
    console.error("[Time Server MCP] Failed to register:", err);
  });
