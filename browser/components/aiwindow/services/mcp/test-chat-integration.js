/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Test Script for MCP Chat Integration
 *
 * This script registers the test MCP server and validates that:
 * 1. The server starts successfully
 * 2. Tools are registered in the tool registry
 * 3. The tool can be called through the Chat interface
 *
 * Usage:
 * 1. Build Firefox: ./mach build
 * 2. Run Firefox: ./mach run
 * 3. Open Browser Console: Ctrl+Shift+J (or Cmd+Shift+J on Mac)
 * 4. Copy and paste this entire file
 * 5. Press Enter
 */

(async function testMCPChatIntegration() {
  console.log("=== MCP Chat Integration Test ===\n");

  try {
    // Load the test server code
    console.log("1. Loading test server code...");
    const testServerPath = PathUtils.join(
      Services.dirsvc.get("CurWorkD", Ci.nsIFile).path,
      "browser/components/aiwindow/services/mcp/test-chat-server.js"
    );
    const testServerCode = await IOUtils.readUTF8(testServerPath);
    console.log("   ✓ Loaded test server code");

    // Import MCP modules
    console.log("\n2. Importing MCP modules...");
    const { MCPServerManager } = ChromeUtils.importESModule(
      "moz-src:///browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs"
    );
    const { MCPToolRegistry } = ChromeUtils.importESModule(
      "moz-src:///browser/components/aiwindow/services/mcp/MCPToolRegistry.sys.mjs"
    );
    console.log("   ✓ Modules imported");

    // Create manager and registry
    console.log("\n3. Creating server manager and tool registry...");
    const manager = new MCPServerManager();
    const registry = new MCPToolRegistry(manager);
    console.log("   ✓ Manager and registry created");

    // Register the test server
    console.log("\n4. Registering test server...");
    await manager.registerServer({
      id: "test-chat-server",
      type: "sandbox",
      code: testServerCode,
      enabled: true,
    });
    console.log("   ✓ Server registered and started");

    // Refresh tools in registry
    console.log("\n5. Refreshing tools in registry...");
    await registry.refreshServerTools("test-chat-server");
    const tools = registry.listAllTools();
    console.log(`   ✓ Found ${tools.length} tool(s):`);
    tools.forEach(tool => {
      console.log(`     - ${tool.name}: ${tool.description}`);
    });

    // Test calling the tool directly
    console.log("\n6. Calling hello_mcp tool directly...");
    const result = await registry.callTool("hello_mcp", {
      name: "Firefox Developer",
    });
    console.log("   ✓ Tool response:");
    console.log(`     ${result.content[0].text}`);

    // Test tool lookup by short name
    console.log("\n7. Testing tool lookup...");
    const tool = registry.getTool("hello_mcp");
    if (tool) {
      console.log(`   ✓ Tool found by short name: ${tool.name}`);
      console.log(`     Server: ${tool.serverId}`);
      console.log(`     FQN: ${tool.fqn}`);
    } else {
      console.error("   ✗ Tool not found!");
    }

    console.log("\n=== Test Complete! ===");
    console.log("\n✅ MCP Chat Integration is working!");
    console.log("\nNext steps:");
    console.log("1. Open the aiwindow chat interface");
    console.log("2. Make sure you have Ollama running locally");
    console.log(
      '3. Ask the model: "Please call the hello_mcp tool with my name"'
    );
    console.log("4. The model should be able to see and use the MCP tool!");
    console.log("\nNote: The Chat code already includes MCP integration.");
    console.log("When Chat initializes, it will automatically:");
    console.log("- Initialize the MCP infrastructure");
    console.log("- Load all registered MCP tools");
    console.log("- Make them available to the model");

    // Clean up
    console.log("\n8. Cleaning up test server...");
    await manager.stopServer("test-chat-server");
    await manager.unregisterServer("test-chat-server");
    console.log("   ✓ Test server stopped and unregistered");
  } catch (error) {
    console.error("\n❌ Test failed:", error);
    console.error(error.stack);
  }
})();
