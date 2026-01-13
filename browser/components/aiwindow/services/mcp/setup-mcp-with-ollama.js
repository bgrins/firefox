// ==== MCP Chat Integration Test with Ollama Setup ====
// Copy and paste this entire block into the Browser Console

(async function() {
  console.log("=== MCP Chat Integration Test ===\n");

  try {
    console.log("1. Setting aiwindow prefs for Ollama...");
    Services.prefs.setBoolPref("browser.aiwindow.enabled", true);
    Services.prefs.setStringPref("browser.aiwindow.endpoint", "http://localhost:11434/v1");
    Services.prefs.setStringPref("browser.aiwindow.model", "smollm2:135m");
    Services.prefs.setStringPref("browser.aiwindow.apiKey", "dummy");
    console.log("   ✓ Prefs set:");
    console.log("     - browser.aiwindow.enabled = true");
    console.log("     - browser.aiwindow.endpoint = http://localhost:11434/v1");
    console.log("     - browser.aiwindow.model = smollm2:135m");
    console.log("     - browser.aiwindow.apiKey = dummy");

    // Inline server code
    const testServerCode = `
      (function () {
        "use strict";

        const SERVER_INFO = {
          name: "test-chat-server",
          version: "1.0.0",
        };

        const TOOLS = [
          {
            name: "hello_mcp",
            description: "A test tool that returns a greeting message to confirm MCP integration is working",
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
                  const message = \`Hello \${greetName}! This message comes from an MCP tool running in a Firefox sandbox. The MCP integration is working! 🎉\`;

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
    `;

    console.log("\n2. Importing Chat module...");
    const { Chat } = ChromeUtils.importESModule(
      "moz-src:///browser/components/aiwindow/models/Chat.sys.mjs"
    );

    console.log("3. Initializing MCP...");
    await Chat._initializeMCP();

    console.log("4. Registering test MCP server...");
    await Chat._mcpServerManager.registerServer({
      id: "test-chat-server",
      type: "sandbox",
      code: testServerCode,
      enabled: true,
    });

    console.log("5. Refreshing tools in registry...");
    await Chat._mcpToolRegistry.refreshServerTools("test-chat-server");

    console.log("6. Verifying registration...");
    const tools = Chat._mcpToolRegistry.listAllTools();
    console.log(`   ✓ Found ${tools.length} MCP tool(s):`);
    tools.forEach(tool => {
      console.log(`     - ${tool.name}: ${tool.description}`);
    });

    console.log("\n7. Testing direct tool call...");
    const result = await Chat._mcpToolRegistry.callTool("hello_mcp", {
      name: "Firefox Developer",
    });
    console.log("   ✓ Tool response:");
    console.log(`     ${result.content[0].text}`);

    console.log("\n8. Checking tool config for Chat...");
    const allTools = await Chat._getAllToolsConfig();
    console.log(`   ✓ Chat has ${allTools.length} total tools available:`);
    const toolNames = allTools.map(t => t.function.name);
    console.log(`     ${toolNames.join(", ")}`);

    console.log("\n=== ✅ Test Complete! ===\n");
    console.log("Setup complete! Next steps:");
    console.log("1. Make sure Ollama is running: ollama serve");
    console.log("2. Make sure llama3 model is available: ollama pull llama3");
    console.log("3. Open the aiwindow chat interface");
    console.log('4. Try asking: "Please call the hello_mcp tool with my name"');
    console.log("5. The model should see hello_mcp in its tool list and call it!");
    console.log("\nNote: The MCP tool will persist for this browser session.");
    console.log("To unregister it, run:");
    console.log("  Chat._mcpServerManager.stopServer('test-chat-server')");
    console.log("  Chat._mcpServerManager.unregisterServer('test-chat-server')");

  } catch (error) {
    console.error("\n❌ Test failed:", error);
    console.error(error.stack);
  }
})();
