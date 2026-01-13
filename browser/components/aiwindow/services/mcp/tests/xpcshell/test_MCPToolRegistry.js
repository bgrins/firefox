/* Any copyright is dedicated to the Public Domain.
 * http://creativecommons.org/publicdomain/zero/1.0/ */

"use strict";

const { MCPServerManager } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs"
);

const { MCPToolRegistry } = ChromeUtils.importESModule(
  "moz-src:///browser/components/aiwindow/services/mcp/MCPToolRegistry.sys.mjs"
);

let echoServerCode;

add_setup(async function () {
  const echoServerPath = do_get_file("echo-server.js").path;
  echoServerCode = await IOUtils.readUTF8(echoServerPath);
});

add_task(async function test_register_tools() {
  info("Testing tool registration");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  const tools = [
    {
      name: "test-tool-1",
      description: "Test tool 1",
      inputSchema: { type: "object" },
    },
    {
      name: "test-tool-2",
      description: "Test tool 2",
      inputSchema: { type: "object" },
    },
  ];

  const registered = registry.registerServerTools("test-server", tools);

  Assert.equal(registered.length, 2, "Should register 2 tools");
  Assert.equal(
    registered[0],
    "test-server/test-tool-1",
    "First tool name should be namespaced"
  );
  Assert.equal(
    registered[1],
    "test-server/test-tool-2",
    "Second tool name should be namespaced"
  );

  Assert.equal(registry.getToolCount(), 2, "Registry should have 2 tools");
  Assert.equal(
    registry.getServerToolCount("test-server"),
    2,
    "Server should have 2 tools"
  );
});

add_task(async function test_unregister_tools() {
  info("Testing tool unregistration");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  const tools = [
    { name: "tool-1", description: "Tool 1" },
    { name: "tool-2", description: "Tool 2" },
  ];

  registry.registerServerTools("server-1", tools);
  Assert.equal(registry.getToolCount(), 2, "Should have 2 tools");

  const unregistered = registry.unregisterServerTools("server-1");
  Assert.equal(unregistered.length, 2, "Should unregister 2 tools");
  Assert.equal(registry.getToolCount(), 0, "Should have 0 tools");
  Assert.equal(
    registry.getServerToolCount("server-1"),
    0,
    "Server should have 0 tools"
  );
});

add_task(async function test_get_tool() {
  info("Testing getTool");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  const tools = [
    {
      name: "my-tool",
      description: "My tool",
      inputSchema: { type: "object", properties: { foo: { type: "string" } } },
    },
  ];

  registry.registerServerTools("my-server", tools);

  const toolByFQN = registry.getTool("my-server/my-tool");
  Assert.ok(toolByFQN, "Should find tool by fully qualified name");
  Assert.equal(toolByFQN.name, "my-tool", "Tool name should match");
  Assert.equal(toolByFQN.serverId, "my-server", "Server ID should match");
  Assert.equal(
    toolByFQN.fullyQualifiedName,
    "my-server/my-tool",
    "FQN should match"
  );

  const toolByShortName = registry.getTool("my-tool");
  Assert.ok(toolByShortName, "Should find tool by short name");
  Assert.equal(toolByShortName.name, "my-tool", "Tool name should match");

  const nonExistent = registry.getTool("nonexistent");
  Assert.equal(nonExistent, undefined, "Should return undefined for unknown tool");
});

add_task(async function test_get_tool_schema() {
  info("Testing getToolSchema");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  const tools = [
    {
      name: "schema-tool",
      description: "Tool with schema",
      inputSchema: {
        type: "object",
        properties: {
          arg1: { type: "string" },
          arg2: { type: "number" },
        },
        required: ["arg1"],
      },
    },
  ];

  registry.registerServerTools("schema-server", tools);

  const schema = registry.getToolSchema("schema-tool");
  Assert.ok(schema, "Should return schema");
  Assert.equal(schema.type, "object", "Schema type should match");
  Assert.ok(schema.properties, "Schema should have properties");
  Assert.ok(schema.required, "Schema should have required fields");

  const schemaByFQN = registry.getToolSchema("schema-server/schema-tool");
  Assert.deepEqual(schemaByFQN, schema, "Should get same schema by FQN");

  const noSchema = registry.getToolSchema("nonexistent");
  Assert.equal(noSchema, null, "Should return null for unknown tool");
});

add_task(async function test_list_tools() {
  info("Testing listAllTools and listServerTools");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("server-1", [
    { name: "tool-1a", description: "Tool 1A" },
    { name: "tool-1b", description: "Tool 1B" },
  ]);

  registry.registerServerTools("server-2", [
    { name: "tool-2a", description: "Tool 2A" },
  ]);

  const allTools = registry.listAllTools();
  Assert.equal(allTools.length, 3, "Should have 3 tools total");

  const server1Tools = registry.listServerTools("server-1");
  Assert.equal(server1Tools.length, 2, "Server 1 should have 2 tools");
  Assert.equal(server1Tools[0].name, "tool-1a", "First tool name should match");
  Assert.equal(server1Tools[1].name, "tool-1b", "Second tool name should match");

  const server2Tools = registry.listServerTools("server-2");
  Assert.equal(server2Tools.length, 1, "Server 2 should have 1 tool");

  const noServerTools = registry.listServerTools("nonexistent");
  Assert.equal(noServerTools.length, 0, "Nonexistent server should have 0 tools");
});

add_task(async function test_has_tool() {
  info("Testing hasTool");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("test-server", [
    { name: "exists", description: "Existing tool" },
  ]);

  Assert.ok(registry.hasTool("exists"), "Should find existing tool by short name");
  Assert.ok(
    registry.hasTool("test-server/exists"),
    "Should find existing tool by FQN"
  );
  Assert.ok(
    !registry.hasTool("nonexistent"),
    "Should not find nonexistent tool"
  );
});

add_task(async function test_call_tool_with_sandbox_server() {
  info("Testing callTool with sandbox server");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  await manager.registerServer({
    id: "echo-server",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  const transport = manager.getTransport("echo-server");
  const toolsResult = await transport.request("tools/list", {});
  registry.registerServerTools("echo-server", toolsResult.tools);

  const resultByFQN = await registry.callTool("echo-server/echo", {
    message: "Hello from FQN",
  });

  Assert.ok(resultByFQN.content, "Should have content");
  Assert.equal(
    resultByFQN.content[0].text,
    "Hello from FQN",
    "Should echo message"
  );

  const resultByShortName = await registry.callTool("echo", {
    message: "Hello from short name",
  });

  Assert.equal(
    resultByShortName.content[0].text,
    "Hello from short name",
    "Should echo message with short name"
  );

  await manager.stopServer("echo-server");
});

add_task(async function test_call_tool_with_multiple_servers() {
  info("Testing callTool with multiple servers");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  await manager.registerServer({
    id: "server-a",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  await manager.registerServer({
    id: "server-b",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  const transportA = manager.getTransport("server-a");
  const toolsA = await transportA.request("tools/list", {});
  registry.registerServerTools("server-a", toolsA.tools);

  const transportB = manager.getTransport("server-b");
  const toolsB = await transportB.request("tools/list", {});
  registry.registerServerTools("server-b", toolsB.tools);

  const resultA = await registry.callTool("server-a/echo", {
    message: "From A",
  });
  Assert.equal(resultA.content[0].text, "From A", "Should route to server A");

  const resultB = await registry.callTool("server-b/echo", {
    message: "From B",
  });
  Assert.equal(resultB.content[0].text, "From B", "Should route to server B");

  await manager.stopAllServers();
});

add_task(async function test_call_tool_errors() {
  info("Testing callTool error handling");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  await Assert.rejects(
    registry.callTool("nonexistent", {}),
    /Tool not found/,
    "Should reject unknown tool"
  );

  registry.registerServerTools("stopped-server", [
    { name: "tool", description: "Tool" },
  ]);

  await Assert.rejects(
    registry.callTool("stopped-server/tool", {}),
    /not running/,
    "Should reject when server not running"
  );
});

add_task(async function test_refresh_server_tools() {
  info("Testing refreshServerTools");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  await manager.registerServer({
    id: "refresh-test",
    type: "sandbox",
    code: echoServerCode,
    enabled: true,
  });

  registry.registerServerTools("refresh-test", [
    { name: "old-tool", description: "Old tool" },
  ]);

  Assert.equal(registry.getToolCount(), 1, "Should have 1 tool initially");
  Assert.ok(registry.hasTool("old-tool"), "Should have old tool");

  await registry.refreshServerTools("refresh-test");

  Assert.ok(
    registry.getToolCount() > 1,
    "Should have multiple tools after refresh"
  );
  Assert.ok(!registry.hasTool("old-tool"), "Should not have old tool");
  Assert.ok(registry.hasTool("echo"), "Should have echo tool from server");

  await manager.stopServer("refresh-test");
});

add_task(async function test_duplicate_tool_names() {
  info("Testing duplicate tool names across servers");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("server-1", [
    { name: "duplicate", description: "From server 1" },
  ]);

  registry.registerServerTools("server-2", [
    { name: "duplicate", description: "From server 2" },
  ]);

  Assert.equal(registry.getToolCount(), 2, "Should have 2 tools with same name");

  const tool1 = registry.getTool("server-1/duplicate");
  Assert.equal(tool1.description, "From server 1", "Should get tool from server 1");

  const tool2 = registry.getTool("server-2/duplicate");
  Assert.equal(tool2.description, "From server 2", "Should get tool from server 2");

  const byShortName = registry.getTool("duplicate");
  Assert.ok(byShortName, "Should find a tool by short name");
});

add_task(async function test_tool_without_name() {
  info("Testing tool registration without name");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  const tools = [
    { name: "valid-tool", description: "Valid" },
    { description: "No name" },
    { name: "another-valid", description: "Valid" },
  ];

  const registered = registry.registerServerTools("test", tools);

  Assert.equal(registered.length, 2, "Should only register tools with names");
  Assert.ok(
    registered.includes("test/valid-tool"),
    "Should register valid tool"
  );
  Assert.ok(
    registered.includes("test/another-valid"),
    "Should register another valid tool"
  );
});

add_task(async function test_register_duplicate_on_same_server() {
  info("Testing duplicate registration on same server");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("dup-server", [
    { name: "tool", description: "First" },
  ]);

  // Fix #18: Re-registering clears old tools first
  const secondReg = registry.registerServerTools("dup-server", [
    { name: "tool", description: "Second" },
  ]);

  Assert.equal(secondReg.length, 1, "Should register new tool");
  Assert.equal(registry.getToolCount(), 1, "Should still have 1 tool");

  const tool = registry.getTool("dup-server/tool");
  Assert.equal(tool.description, "Second", "Should have new registration");
});

add_task(async function test_invalid_inputs() {
  info("Testing invalid inputs");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  await Assert.throws(
    () => registry.registerServerTools("test", "not-an-array"),
    /must be an array/,
    "Should reject non-array tools"
  );

  await Assert.throws(
    () => registry.registerServerTools("test", null),
    /must be an array/,
    "Should reject null tools"
  );
});

add_task(async function test_input_validation_for_tool_calls() {
  info("Testing input validation for tool calls");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  // Register a tool with schema
  registry.registerServerTools("validation-server", [
    {
      name: "validate-tool",
      description: "Tool with input validation",
      inputSchema: {
        type: "object",
        properties: {
          requiredString: { type: "string" },
          optionalNumber: { type: "number" },
        },
        required: ["requiredString"],
      },
    },
  ]);

  // Test invalid tool name types
  await Assert.rejects(
    registry.callTool(null, {}),
    /must be a non-empty string/,
    "Should reject null tool name"
  );

  await Assert.rejects(
    registry.callTool("", {}),
    /must be a non-empty string/,
    "Should reject empty tool name"
  );

  await Assert.rejects(
    registry.callTool(123, {}),
    /must be a non-empty string/,
    "Should reject non-string tool name"
  );

  // Test invalid arguments type
  await Assert.rejects(
    registry.callTool("validate-tool", "not-an-object"),
    /must be an object/,
    "Should reject non-object arguments"
  );

  await Assert.rejects(
    registry.callTool("validate-tool", null),
    /must be an object/,
    "Should reject null arguments"
  );

  await Assert.rejects(
    registry.callTool("validate-tool", []),
    /must be an object/,
    "Should reject array arguments"
  );

  // Test missing required field
  await Assert.rejects(
    registry.callTool("validate-tool", {}),
    /Missing required argument 'requiredString'/,
    "Should reject missing required field"
  );

  // Test wrong type for field
  await Assert.rejects(
    registry.callTool("validate-tool", {
      requiredString: 123,
    }),
    /must be a string/,
    "Should reject wrong type for string field"
  );

  await Assert.rejects(
    registry.callTool("validate-tool", {
      requiredString: "valid",
      optionalNumber: "not-a-number",
    }),
    /must be a number/,
    "Should reject wrong type for number field"
  );

  // Test invalid FQN format
  await Assert.rejects(
    registry.callTool("invalid/format/too/many/slashes", {}),
    /Invalid fully qualified tool name/,
    "Should reject invalid FQN format"
  );

  await Assert.rejects(
    registry.callTool("/missing-server", {}),
    /Invalid fully qualified tool name/,
    "Should reject FQN with empty server"
  );

  await Assert.rejects(
    registry.callTool("missing-tool/", {}),
    /Invalid fully qualified tool name/,
    "Should reject FQN with empty tool name"
  );
});

add_task(async function test_null_type_validation() {
  info("Testing null is rejected for object type (fix #12)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("test-server", [
    {
      name: "object-tool",
      description: "Tool requiring object",
      inputSchema: {
        type: "object",
        properties: {
          data: { type: "object" },
        },
        required: ["data"],
      },
    },
  ]);

  await Assert.rejects(
    registry.callTool("object-tool", { data: null }),
    /must be an object/,
    "Should reject null for object type"
  );
});

add_task(async function test_tool_lookup_performance() {
  info("Testing O(1) tool lookup with index (fix #13)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  // Register many tools
  const tools = [];
  for (let i = 0; i < 1000; i++) {
    tools.push({ name: `tool-${i}`, description: `Tool ${i}` });
  }
  registry.registerServerTools("perf-server", tools);

  // Lookup by short name should be fast (O(1))
  const startTime = Date.now();
  const tool = registry.getTool("tool-999");
  const elapsed = Date.now() - startTime;

  Assert.ok(tool, "Should find tool");
  Assert.equal(tool.name, "tool-999", "Should find correct tool");
  Assert.ok(elapsed < 10, `Lookup should be fast (was ${elapsed}ms)`);
});

add_task(async function test_consistent_error_handling() {
  info("Testing consistent undefined returns (fix #14)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  registry.registerServerTools("test", [
    { name: "exists", description: "Exists", inputSchema: { type: "object" } },
  ]);

  // getTool returns undefined for missing tools
  Assert.equal(
    registry.getTool("nonexistent"),
    undefined,
    "getTool should return undefined"
  );
  Assert.equal(
    registry.getTool(null),
    undefined,
    "getTool should return undefined for null"
  );

  // getToolSchema returns undefined for missing tools
  Assert.equal(
    registry.getToolSchema("nonexistent"),
    undefined,
    "getToolSchema should return undefined"
  );

  // Existing tool returns schema
  const schema = registry.getToolSchema("exists");
  Assert.ok(schema, "Should return schema for existing tool");
});

add_task(async function test_tool_limit() {
  info("Testing tool registration limits (fix #15)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  // Try to register 1001 tools (MAX_TOOLS_PER_SERVER = 1000)
  const tools = [];
  for (let i = 0; i < 1001; i++) {
    tools.push({ name: `tool-${i}`, description: `Tool ${i}` });
  }

  Assert.throws(
    () => registry.registerServerTools("limit-test", tools),
    /max 1000 per server/,
    "Should reject when exceeding per-server limit"
  );
});

add_task(async function test_stale_tool_cleanup() {
  info("Testing stale tool cleanup on re-registration (fix #18)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  // Register initial tools
  registry.registerServerTools("cleanup-server", [
    { name: "tool-1", description: "Tool 1" },
    { name: "tool-2", description: "Tool 2" },
  ]);

  Assert.equal(registry.getToolCount(), 2, "Should have 2 tools");

  // Re-register with different tools
  registry.registerServerTools("cleanup-server", [
    { name: "tool-3", description: "Tool 3" },
  ]);

  Assert.equal(registry.getToolCount(), 1, "Should have 1 tool after re-register");
  Assert.ok(!registry.hasTool("tool-1"), "Old tool-1 should be gone");
  Assert.ok(!registry.hasTool("tool-2"), "Old tool-2 should be gone");
  Assert.ok(registry.hasTool("tool-3"), "New tool-3 should exist");
});

add_task(async function test_validation_on_refresh() {
  info("Testing validation on refreshServerTools (fix #19)");

  const manager = new MCPServerManager();
  const registry = new MCPToolRegistry(manager);

  // Try to refresh non-existent server
  await Assert.rejects(
    registry.refreshServerTools("nonexistent"),
    /not running/,
    "Should reject for non-existent server"
  );

  // Register but don't start
  await manager.registerServer({
    id: "stopped-server",
    type: "sandbox",
    code: echoServerCode,
    enabled: false,
  });

  await Assert.rejects(
    registry.refreshServerTools("stopped-server"),
    /not running/,
    "Should reject for stopped server"
  );
});
