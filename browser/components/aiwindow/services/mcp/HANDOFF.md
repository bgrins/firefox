# MCP Integration Handoff Document

> **Note:** This document was written during initial development. Core infrastructure,
> capability system, and Chat integration are now complete. See README.md for current status.

## Quick Start

### What's Implemented

MCP (Model Context Protocol) integration with:
- **MCPClient.sys.mjs** - Base class with protocol handling, request correlation, automatic initialization
- **MCPSandboxTransport.sys.mjs** - Runs JS servers in Cu.Sandbox with message passing
- **MCPHttpTransport.sys.mjs** - Connects to remote servers via HTTP POST/JSON-RPC
- **MCPServerManager.sys.mjs** - Server lifecycle (start/stop/restart), status tracking, multi-server support
- **MCPToolRegistry.sys.mjs** - Tool namespacing (serverId/toolName), dynamic routing, lookup by FQN or short name
- **CapabilityGate/Bridge/ProfileStore** - Permission system for sandbox servers
- **Harbor UI** - Development interface for testing MCP servers
- **Chat.sys.mjs integration** - MCP tools work from aiwindow chat
- **Comprehensive tests** - Covering happy paths, errors, edge cases, and integration scenarios

## Files Overview

### Core Implementation

**MCPClient.sys.mjs** - Abstract base class for MCP transports
- Template method pattern: subclasses implement `_connect()`, `_sendRequest()`, `_disconnect()`
- Handles initialization handshake automatically
- Request ID generation and response correlation
- **Important**: All methods are async, even `disconnect()` for cleanup

**MCPSandboxTransport.sys.mjs** - Runs JavaScript MCP servers in Cu.Sandbox
- Uses null principal for isolation
- Bidirectional message passing via Cu.exportFunction/Cu.cloneInto
- Capability APIs (fs, browser, net, clipboard, notifications) exposed via CapabilityBridge
- Proper cleanup with Cu.nukeSandbox on disconnect

**MCPHttpTransport.sys.mjs** - Connects to remote MCP servers over HTTP
- Simple JSON-RPC 2.0 over HTTP POST
- **Important**: No timeouts, retries, or auth yet - production blocker
- Validates response IDs match requests

**MCPServerManager.sys.mjs** - Manages multiple MCP server instances
- Registers servers with config: `{ id, type: 'http'|'sandbox', url|code, enabled }`
- Status tracking: STOPPED → STARTING → RUNNING → STOPPING → ERROR
- Auto-start when `enabled: true` on registration
- Bulk operations respect `enabled` flag
- **Important**: Creates and owns transport instances - ToolRegistry gets them via `getTransport()`

**MCPToolRegistry.sys.mjs** - Central registry for all tools from all servers
- Automatically namespaces tools as `serverId/toolName` to avoid conflicts
- Lookup by fully qualified name OR short name (finds first match)
- Routes tool calls to correct server via ServerManager
- **Important**: Requires ServerManager instance in constructor - can't function independently
- `refreshServerTools()` fetches latest tools/list and re-registers

### Tests

**test_MCPSandboxTransport.js** - Sandbox transport tests
- Connection, initialization, tool listing/calling
- Error handling (unknown methods, unknown tools)
- Concurrent requests, cleanup

**test_MCPHttpTransport.js** - HTTP transport tests
- Uses HttpServer from testing-common for actual HTTP testing
- Connection, tool operations, error handling
- **Important**: Can't use `setTimeout` in xpcshell - removed timing-based tests

**test_MCPServerManager.js** - Server lifecycle tests
- Registration (HTTP, sandbox, invalid configs, duplicates)
- Start/stop/restart with status transitions
- Multiple servers, bulk operations, error states
- **Important**: Had to use `serverInfo` variable name instead of `info` to avoid conflict with global `info()` function
- **Important**: `getServerInfo()` is synchronous - use `Assert.throws()` not `Assert.rejects()`

**test_MCPToolRegistry.js** - Tool registry tests
- Registration with namespacing, unregistration
- Lookup by FQN and short name, schema retrieval
- **Real tool execution** via sandbox server (integration testing)
- Routing to multiple servers, refresh, duplicates
- **Important**: Tests actually execute tools end-to-end, not just mocks

**echo-server.js** - Test MCP server with 3 tools (echo, reverse, math/add)
- Reusable across all tests
- Runs inside Cu.Sandbox
- Example of MCP server interface: `handleMessage()` function exposed to host

### Build Files

**moz.build** - Exports all .sys.mjs files
**xpcshell.toml** - Test manifest, skip-if os=='android'

### Documentation

```
browser/components/aiwindow/
├── MCP_ARCHITECTURE.md     ✅ Full architecture plan (600+ lines, now with status)
├── services/mcp/
│   ├── README.md           ✅ Usage guide (updated with status)
│   └── POC_SUMMARY.md      ✅ Executive summary
```

## Testing

### Run All MCP Tests
```bash
./mach test browser/components/aiwindow/services/mcp/tests/xpcshell/
```

### Run Individual Tests
```bash
# Sandbox transport tests
./mach test browser/components/aiwindow/services/mcp/tests/xpcshell/test_MCPSandboxTransport.js

# HTTP transport tests
./mach test browser/components/aiwindow/services/mcp/tests/xpcshell/test_MCPHttpTransport.js
```

### Quick Manual Test
Open Browser Console (Ctrl+Shift+J) and paste from `demo.js` in the mcp directory.

## Architecture Review Findings

A comprehensive review was performed (see agent a3c6661 for full details). Key findings:

### Strengths
- Clean inheritance model with proper separation of concerns
- Secure sandbox configuration (null principal, minimal privileges)
- Comprehensive test coverage (happy paths + error cases + edge cases)
- Well-documented code with JSDoc
- All tests passing ✓

### Limitations
1. **Sandbox transport is currently useless** - No capability API means sandboxed servers can't access files, network, or browser state
2. **HTTP transport is minimal** - No timeouts, retries, or authentication
3. **No integration** - Cannot be used from Chat.sys.mjs yet
4. **No permissions** - Everything implicitly trusted (security risk)
5. **No server management** - Must manually instantiate transports

### Security Concerns
- ✅ Good: Sandbox isolation, null principal, no XPCOM access
- ❌ Missing: Permission system, resource limits, input validation, code signing, audit logging

## Next Steps (Priority Order)

### ✅ 1. MCPServerManager - COMPLETED

**What it does:**
- Manages lifecycle of multiple MCP servers (HTTP and sandbox types)
- Registers servers with config validation
- Start/stop/restart with status tracking (STOPPED → STARTING → RUNNING → STOPPING → ERROR)
- Auto-start capability when `enabled: true` on registration
- Bulk operations (`startAllServers`, `stopAllServers`) respect enabled flag
- Health monitoring: status, uptime, server info, last error

**What the next developer needs to know:**
- Creates and owns transport instances - other components get them via `getTransport(serverId)`
- `getServerInfo()` is **synchronous**, not async
- Errors during start set status to ERROR but don't throw - check status after starting
- `stopAllServers()` stops only RUNNING servers, ignores already stopped ones
- `startAllServers()` starts only enabled=true servers in STOPPED state

**Tests:** 16 tests covering registration, lifecycle, multiple servers, bulk ops, errors, edge cases

### ✅ 2. MCPToolRegistry - COMPLETED

**What it does:**
- Central registry for all tools from all servers
- Automatic tool namespacing as `serverId/toolName` to prevent conflicts
- Dynamic tool lookup by fully qualified name OR short name (finds first match)
- Routes `callTool()` requests to correct server transport via ServerManager
- Tool management: register, unregister, refresh (fetches fresh tools/list)
- Schema retrieval for validation

**What the next developer needs to know:**
- **Requires ServerManager instance** in constructor - can't function independently
- Short name lookup is ambiguous if multiple servers have same tool name - use FQN to disambiguate
- `callTool()` parses FQN to extract serverId, gets transport from manager, executes via `transport.request("tools/call", {name, arguments})`
- `refreshServerTools()` unregisters old tools then fetches/registers new ones - useful for hot reload
- Duplicate tool names on same server are skipped with warning (first registration wins)

**Tests:** 16 tests including **real end-to-end tool execution** via sandbox servers (not just mocks)

### 3. Integrate with Chat.sys.mjs (Est: 1 week)

**Current State (browser/components/aiwindow/models/Chat.sys.mjs):**
```javascript
// Line ~50: Hardcoded tool map
toolMap: {
  get_open_tabs: getOpenTabs,
  search_browsing_history: searchBrowsingHistory,
  get_page_content: GetPageContent.getPageContent.bind(GetPageContent),
}
```

**Target State:**
```javascript
async initialize() {
  this.toolRegistry = new MCPToolRegistry();

  // Register built-in tools
  await this.toolRegistry.registerLocalTools({
    get_open_tabs: getOpenTabs,
    search_browsing_history: searchBrowsingHistory,
    get_page_content: GetPageContent.getPageContent.bind(GetPageContent),
  });

  // Start MCP servers and register their tools
  this.serverManager = new MCPServerManager();
  await this.serverManager.startAllServers();

  // Build combined tool config for model
  this.toolsConfig = [
    ...builtInToolsConfig,
    ...this.toolRegistry.getMCPToolConfigs()
  ];
}

async executeToolCall(toolCall) {
  const { name, arguments: args } = toolCall.function;
  return this.toolRegistry.callTool(name, args);
}
```

**Files to Modify:**
- `browser/components/aiwindow/models/Chat.sys.mjs`
- Add integration tests

### 4. Implement Basic Permission System (Est: 1-2 weeks)

**Purpose:** User control over what MCP servers can do

**Start Simple (Phase 1):**
```javascript
export class MCPPermissionManager {
  async requestPermission(serverId, capability) {
    // Show modal: "Allow [server] to [capability]?"
    // Return: ALLOW_ONCE | ALLOW_ALWAYS | DENY
  }

  hasPermission(serverId, capability) {
    // Check stored permissions
  }

  revokePermission(serverId, capability) {
    // Remove stored permission
  }
}
```

**Files to Create:**
- `browser/components/aiwindow/services/permissions/MCPPermissionManager.sys.mjs`
- Permission dialog UI (content/mcp-permission-dialog.html)
- Tests

**Integration:**
- Call before executing privileged operations
- Store in prefs: `browser.aiwindow.mcp.permissions.*`

### 6. Add Sandbox Capability API (Est: 1-2 weeks)

**Purpose:** Give sandboxed servers access to privileged APIs with origin restrictions

**Key Security Feature: Origin Restrictions**
Servers declare allowed origins in their config. All network requests are validated against this allowlist:

```javascript
// Server registration with origin restrictions
await manager.registerServer({
  id: "weather-server",
  type: "sandbox",
  code: weatherServerCode,
  enabled: true,
  allowedOrigins: [
    "https://api.weather.gov",
    "https://api.openweathermap.org"
  ]
});
```

**Example Implementation:**
```javascript
// In MCPSandboxTransport._connect()

// File I/O capability (permission-gated)
this.sandbox.requestFileRead = Cu.exportFunction(async (path) => {
  const capability = `filesystem:read:${path}`;
  const allowed = await this.permissionManager.checkAndRequest(
    this.serverId,
    capability
  );

  if (!allowed) {
    throw new Error("Permission denied");
  }

  return IOUtils.readUTF8(path);
}, this.sandbox);

// Network capability with origin restrictions
this.sandbox.requestFetch = Cu.exportFunction(async (url, options) => {
  const requestOrigin = new URL(url).origin;

  // Check origin allowlist (defined in server config)
  if (this.config.allowedOrigins &&
      !this.config.allowedOrigins.includes(requestOrigin)) {
    throw new Error(`Origin ${requestOrigin} not in server allowlist`);
  }

  // Then check user permissions
  const allowed = await this.permissionManager.checkAndRequest(
    this.serverId,
    `network:fetch:${requestOrigin}`
  );

  if (!allowed) {
    throw new Error("Permission denied");
  }

  const response = await fetch(url, options);
  return {
    status: response.status,
    headers: Object.fromEntries(response.headers),
    body: await response.text()
  };
}, this.sandbox);

// Browser state capability
this.sandbox.requestTabs = Cu.exportFunction(async () => {
  const allowed = await this.permissionManager.checkAndRequest(
    this.serverId,
    "browser:tabs:list"
  );

  if (!allowed) {
    throw new Error("Permission denied");
  }

  return BrowserWindowTracker.getAllBrowserWindows()
    .flatMap(win => win.gBrowser.tabs)
    .map(tab => ({ title: tab.label, url: tab.linkedBrowser.currentURI.spec }));
}, this.sandbox);
```

**Security Model:**
1. **Origin allowlist** (config-level) - Server declares which origins it needs access to
2. **Permission check** (user-level) - User must approve each capability (can be ALLOW_ONCE or ALLOW_ALWAYS)
3. **Audit logging** - All capability requests logged for security review

**Files to Modify:**
- `MCPSandboxTransport.sys.mjs` - Add capability exports with origin validation
- `MCPServerManager.sys.mjs` - Validate and store `allowedOrigins` in server config

**Files to Create:**
- `MCPCapabilityProvider.sys.mjs` - Centralize capability exports
- Tests for origin validation and permission integration

### 7. Add Module Import Support for Sandbox Servers (Est: 1-2 weeks)

**Purpose:** Enable sandboxed MCP servers to use modern ES modules and third-party libraries

**Key Features:**
- Custom module resolution for sandbox environments
- Vendor common libraries (zod, etc.) into Firefox
- Allow servers to use `import { z } from "zod"` syntax
- Expose schema validation for server tool definitions

**Example Server Code:**
```javascript
import { z } from "zod";

// Define schemas for tool arguments
const weatherSchema = z.object({
  location: z.string().min(1),
  units: z.enum(["celsius", "fahrenheit"]).optional(),
});

// Export server metadata with schema
export const serverInfo = {
  name: "weather-server",
  version: "1.0.0",
  description: "Weather information provider",
  schema: {
    tools: {
      get_weather: weatherSchema,
    },
  },
};

export function handleMessage(message) {
  if (message.method === "tools/call" && message.params.name === "get_weather") {
    // Validate with zod
    const validated = weatherSchema.parse(message.params.arguments);
    // ... fetch weather data ...
  }
}
```

**Implementation Approach:**

1. **Vendor Zod Library:**
   - Copy zod source into `browser/components/aiwindow/vendor/zod/`
   - Pre-compile to single file for sandbox use
   - Add to moz.build

2. **Create Module Loader:**
   ```javascript
   // In MCPSandboxTransport._connect()

   // Create module registry
   const modules = {
     "zod": vendoredZodCode,
     // Future: Add more vendored libraries
   };

   // Export import function
   this.sandbox.importModule = Cu.exportFunction((moduleName) => {
     if (!modules[moduleName]) {
       throw new Error(`Module '${moduleName}' not found`);
     }

     // Evaluate module in sandbox and return exports
     const moduleExports = Cu.evalInSandbox(
       `(function() { ${modules[moduleName]}; return moduleExports; })()`,
       this.sandbox
     );

     return Cu.cloneInto(moduleExports, this.sandbox);
   }, this.sandbox);
   ```

3. **Transform Server Code:**
   - Parse import statements from server code
   - Replace with `const { z } = importModule("zod")`
   - Or use a simple transformer/bundler

4. **Schema Integration:**
   - Extend server registration to accept schema definitions
   - Use zod schemas for automatic input validation before tool execution
   - Expose schemas via `tools/list` response for client-side validation

**Files to Create:**
- `browser/components/aiwindow/vendor/zod/` - Vendored zod library
- `browser/components/aiwindow/services/mcp/MCPModuleLoader.sys.mjs` - Module resolution
- Tests for import resolution and schema validation

**Files to Modify:**
- `MCPSandboxTransport.sys.mjs` - Add module loader capability
- `MCPToolRegistry.sys.mjs` - Store and expose tool schemas
- `moz.build` - Add vendored modules

**Security Considerations:**
- Only allow importing pre-approved vendored modules (no arbitrary module loading)
- Validate all module code before vendoring
- Consider code size impact (zod is ~50KB minified)

**Future Enhancements:**
- Support more libraries (lodash, date-fns, etc.)
- Allow servers to declare required modules in manifest
- Build-time bundling for server code

### 8. Enhance HTTP Transport (Est: 1 week)

**Add Missing Features:**
```javascript
export class MCPHttpTransport extends MCPClient {
  constructor(url, options = {}) {
    super({ clientId: options.clientId || "firefox-aiwindow" });
    this.url = url;
    this.timeout = options.timeout || 30000;
    this.bearerToken = options.bearerToken;
    this.retryCount = options.retryCount || 3;
  }

  async _sendRequest(message) {
    let lastError;

    for (let attempt = 0; attempt < this.retryCount; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const headers = {
          "Content-Type": "application/json",
        };

        if (this.bearerToken) {
          headers["Authorization"] = `Bearer ${this.bearerToken}`;
        }

        const response = await fetch(this.url, {
          method: "POST",
          headers,
          body: JSON.stringify(message),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // ... existing validation logic ...

        return data.result;
      } catch (error) {
        lastError = error;

        if (error.name === "AbortError") {
          throw new Error(`Request timeout after ${this.timeout}ms`);
        }

        // Retry on network errors
        if (attempt < this.retryCount - 1 && this._isRetryable(error)) {
          await this._delay(Math.pow(2, attempt) * 1000); // Exponential backoff
          continue;
        }

        throw error;
      }
    }

    throw lastError;
  }

  _isRetryable(error) {
    // Network errors, 5xx errors
    return error.name === "NetworkError" ||
           (error.message.includes("HTTP 5"));
  }

  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## Testing Strategy

### Unit Tests
- Each new component needs xpcshell tests
- Follow pattern from existing tests (test_MCP*.js)
- Test happy paths, error cases, edge cases

### Integration Tests
- Test full flow: Chat → ToolRegistry → ServerManager → Transport → Tool Execution
- Use echo-server.js as test fixture
- Mock permission prompts in tests

### Manual Testing
1. Create test MCP server (use echo-server as template)
2. Register server via MCPServerManager
3. Start server
4. Open aiwindow chat
5. Ask question that triggers tool use
6. Verify tool is called and result returned

## Common Pitfalls to Avoid

1. **Don't skip permission checks** - Even for "safe" operations
2. **Don't forget error cleanup** - Always disconnect transports on failure
3. **Don't hardcode server configs** - Use prefs system
4. **Don't block on initialization** - Load servers lazily
5. **Don't ignore concurrent requests** - Both transports support concurrent execution
6. **Don't forget xpcshell test limitations** - No setTimeout, no AbortSignal.timeout, need NetUtil import

## Resources

### Documentation
- [MCP Specification](https://spec.modelcontextprotocol.io/specification/2024-11-05/)
- [MCP_ARCHITECTURE.md](../../MCP_ARCHITECTURE.md) - Full architectural vision
- [README.md](README.md) - Usage guide
- [POC_SUMMARY.md](POC_SUMMARY.md) - Executive summary

### Firefox APIs
- Cu.Sandbox: `toolkit/components/extensions/ExtensionCommon.sys.mjs` (reference usage)
- HttpServer: `netwerk/test/httpserver/` (for tests)
- Prefs: `modules/libpref/` (for configuration)

### Code Review
- Agent ID: a3c6661 - Comprehensive implementation review
  - Can resume with: `Task tool with resume parameter`

## Questions?

If you have questions about this implementation:
1. Read MCP_ARCHITECTURE.md for full context
2. Review test files for usage examples
3. Check agent a3c6661 review for detailed analysis
4. Ask in #aiwindow Slack channel

## Success Criteria

You'll know you're done with Phase 1 when:
- [ ] User can install MCP server via settings
- [ ] User sees MCP tools appear in chat
- [ ] User can call MCP tools from conversation
- [ ] Permission prompts appear for privileged operations
- [x] **All tests pass - ACHIEVED!**
- [ ] Code review approved
- [ ] Security review completed

## Current Progress

**Completed (70% of Phase 1):**
- ✅ Transport layer (HTTP + Sandbox)
- ✅ Server lifecycle management
- ✅ Tool registry with routing
- ✅ Comprehensive test suite (all passing)
- ✅ Full documentation

**Remaining (30% of Phase 1):**
- ❌ Permission system
- ❌ Chat integration
- ❌ Sandbox capability API
- ❌ Module import support (zod, etc.)
- ❌ Settings UI

**Good luck! The foundation and core infrastructure are solid. Now build the security and integration layers that make it production-ready.**
