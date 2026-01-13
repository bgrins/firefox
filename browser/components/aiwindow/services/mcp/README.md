# MCP (Model Context Protocol) Integration for Firefox AIWindow

This directory contains the MCP integration for Firefox's aiwindow component, supporting both remote HTTP servers and sandboxed JavaScript servers.

## 🚧 Status: Core Infrastructure Complete (Phase 1 at 70%)

**✅ What's Implemented:**
- **MCPClient** - Base class with protocol handling, request correlation, initialization
- **MCPSandboxTransport** - Runs JS servers in Cu.Sandbox with message passing
- **MCPHttpTransport** - Connects to remote servers (Ollama, cloud services, localhost)
- **MCPServerManager** - Server lifecycle (start/stop/restart), status tracking, multi-server
- **MCPToolRegistry** - Tool namespacing (serverId/toolName), dynamic routing, lookup by FQN/short name
- **Comprehensive test suite** - All passing, covering happy paths, errors, edge cases, integration
- **Full documentation** - README, HANDOFF, MCP_ARCHITECTURE, POC_SUMMARY

**❌ What's Missing (Production Blockers):**
- Permission system (MCPPermissionManager)
- Chat integration (can't be used from aiwindow chat yet)
- Capability API for sandbox (can't access files/network/browser state)
- Module import support (need zod and other libraries in sandbox)
- Settings UI for server management

**📅 Estimated Time to Production:** 2-3 additional weeks

See [MCP_ARCHITECTURE.md](../../MCP_ARCHITECTURE.md#implementation-status) for detailed status.

## Architecture

The POC demonstrates that we can run JavaScript MCP servers in-browser without Node.js or stdio, using Firefox's native sandboxing capabilities:

```
┌─────────────────────────────┐
│  Host Context (Firefox)     │
│  - MCPSandboxTransport      │
│  - Message routing          │
│  - Request/response handling│
└──────────┬──────────────────┘
           │
           │ Cu.exportFunction()
           │ Cu.cloneInto()
           ▼
┌─────────────────────────────┐
│  Cu.Sandbox                 │
│  - MCP server code          │
│  - handleMessage()          │
│  - sendToHost()             │
│  - Tool implementations     │
└─────────────────────────────┘
```

## Key Techniques

### 1. Bidirectional Message Passing

**Host → Sandbox:**
```javascript
const message = Cu.cloneInto({ method: "tools/list", id: 1 }, sandbox);
sandbox.handleMessage(message);
```

**Sandbox → Host:**
```javascript
// In sandbox code
sendToHost({ jsonrpc: "2.0", result: { tools: [...] }, id: 1 });

// sendToHost is exported from host via Cu.exportFunction
```

### 2. Sandbox Creation

```javascript
const principal = Services.scriptSecurityManager.createNullPrincipal({});

const sandbox = Cu.Sandbox(principal, {
  sandboxName: "MCP Server",
  wantXrays: true,              // Security isolation
  wantGlobalProperties: [],     // No globals by default
  wantComponents: false,        // No XPCOM access
});
```

### 3. MCP Protocol Implementation

The sandbox runs standard MCP server code that implements:
- `initialize` - Handshake and capability negotiation
- `tools/list` - Tool discovery
- `tools/call` - Tool execution
- Error handling with JSON-RPC error codes

## Files

### Core Implementation

- **`MCPClient.sys.mjs`** - Abstract base class; subclasses implement _connect(), _sendRequest(), _disconnect()
- **`MCPSandboxTransport.sys.mjs`** - Cu.Sandbox with null principal; NO capability API yet (can't access files/network)
- **`MCPHttpTransport.sys.mjs`** - Simple HTTP POST/JSON-RPC; NO timeouts, retries, or auth yet
- **`MCPServerManager.sys.mjs`** - Creates/owns transports; getServerInfo() is sync not async; auto-start on enabled=true
- **`MCPToolRegistry.sys.mjs`** - Requires ServerManager in constructor; short name lookup ambiguous with duplicate tools

### Testing

- **`tests/xpcshell/test_MCPSandboxTransport.js`** - Connection, tools, errors, concurrency
- **`tests/xpcshell/test_MCPHttpTransport.js`** - Uses HttpServer; no setTimeout in xpcshell
- **`tests/xpcshell/test_MCPServerManager.js`** - Avoid `info` variable name (conflicts with global function)
- **`tests/xpcshell/test_MCPToolRegistry.js`** - Real end-to-end tool execution (not mocks)
- **`tests/xpcshell/echo-server.js`** - Reusable test server with 3 tools
- **`tests/xpcshell/xpcshell.toml`** - Test manifest

### Build Files

- **`moz.build`** - Firefox build system integration

## Running the Demo

### Option 1: Browser Console (Easiest)

1. Build Firefox (if you haven't):
   ```bash
   ./mach build
   ```

2. Run Firefox:
   ```bash
   ./mach run
   ```

3. Open Browser Console: `Ctrl+Shift+J` (or `Cmd+Shift+J` on Mac)

4. Copy and paste the contents of `demo.js` into the console

5. Press Enter and watch the demo run!

You should see output like:
```
=== MCP Sandbox Transport Demo ===

1. Creating MCP sandbox transport...

2. Connecting and initializing...
   ✓ Connected to: echo 1.0.0

3. Listing available tools...
   ✓ Found 3 tools:
     - echo: Returns the input message unchanged
     - reverse: Reverses a string
     - math/add: Adds two numbers

4. Calling 'echo' tool...
   ✓ Result: Hello from Firefox!

5. Calling 'reverse' tool...
   ✓ Result: xobdnaS PCM

6. Calling 'math/add' tool...
   ✓ Result: 42 + 13 = 55

7. Testing 5 concurrent requests...
   ✓ All 5 requests completed successfully
     0: Concurrent request 0
     1: Concurrent request 1
     2: Concurrent request 2
     3: Concurrent request 3
     4: Concurrent request 4

8. Disconnecting...
   ✓ Disconnected and sandbox destroyed

=== Demo Complete! ===

✅ MCP Sandbox Transport POC is working!
```

### Option 2: xpcshell Tests

Run the automated tests:

```bash
./mach test browser/components/aiwindow/services/mcp/tests/xpcshell/test_MCPSandboxTransport.js
```

This runs comprehensive tests covering:
- Connection and initialization
- Tool listing
- Tool calling (echo, reverse, math/add)
- Error handling (unknown methods, unknown tools)
- Multiple sequential requests
- Concurrent requests
- Sandbox cleanup

## What This Proves

✅ **Cu.Sandbox works for MCP servers** - We can run untrusted MCP server code safely

✅ **Message passing is viable** - Cu.exportFunction/cloneInto provide clean bidirectional communication

✅ **Full MCP protocol** - Complete JSON-RPC 2.0 implementation in sandbox

✅ **Concurrent requests** - Multiple requests can be handled simultaneously

✅ **Proper isolation** - Sandbox has no access to privileged APIs unless explicitly granted

✅ **Clean lifecycle** - Cu.nukeSandbox properly cleans up resources

## Next Steps

### 1. Add Module Import Support

Enable sandboxed servers to use modern ES modules and third-party libraries:

```javascript
// In server code
import { z } from "zod";

const weatherSchema = z.object({
  location: z.string(),
  units: z.enum(["celsius", "fahrenheit"]).optional(),
});

export const serverInfo = {
  name: "weather",
  version: "1.0.0",
  schema: {
    tools: {
      get_weather: weatherSchema,
    },
  },
};
```

**Implementation:**
- Vendor zod into `browser/components/aiwindow/vendor/zod/`
- Create `MCPModuleLoader.sys.mjs` for module resolution
- Transform `import` statements to sandbox-compatible code
- Integrate schemas with tool validation

See HANDOFF.md section 7 for detailed implementation plan.

### 2. Add Capabilities API

Extend the transport to provide controlled access to Firefox APIs:

```javascript
// Export file read capability
sandbox.requestFileRead = Cu.exportFunction(async (path) => {
  // Check permissions
  if (!hasPermission(path)) {
    throw new Error("Permission denied");
  }
  return IOUtils.readUTF8(path);
}, sandbox);
```

### 3. Build Real MCP Servers

Create useful servers that run in sandbox:
- **filesystem** - File operations with permission checks
- **memory** - Key-value storage
- **browser** - Access tabs, history (with permissions)

### 4. Integrate with aiwindow

Connect to the Chat system:
```javascript
// In Chat.sys.mjs
const transport = new MCPSandboxTransport(serverCode);
await transport.connect();

// List tools
const { tools } = await transport.request("tools/list");

// Call tool
const result = await transport.request("tools/call", {
  name: "filesystem/read_file",
  arguments: { path: "/tmp/test.txt" }
});
```

### 5. Add HTTP Transport

For remote servers (Ollama, cloud MCP):
```javascript
const httpTransport = new MCPHttpTransport("http://localhost:11434");
await httpTransport.connect();
```

### 6. Build UI

Server management interface:
- Install/enable/disable servers
- View available tools
- Manage permissions
- Monitor usage

## Security Considerations

### ✅ What's Protected

- **No XPCOM access** - Sandbox cannot access privileged Firefox APIs
- **No filesystem access** - Unless explicitly granted via exportFunction
- **No network access** - Unless we provide fetch via wantGlobalProperties
- **Memory isolation** - Sandbox runs in separate compartment
- **Clean destruction** - Cu.nukeSandbox ensures no leaks

### ⚠️ What Needs More Work

- **Capability system** - Need formal permission model for file/network access
- **Resource limits** - Should limit CPU/memory usage per sandbox
- **Audit logging** - Track all MCP operations for security review
- **Code signing** - Verify server code before loading into sandbox

## Comparison to Harbor

| Aspect | Harbor (Extension) | This POC |
|--------|-------------------|----------|
| **Runtime** | Node.js bridge | Cu.Sandbox |
| **Communication** | Native messaging (stdio) | Message passing (exportFunction) |
| **Installation** | npm/docker | JavaScript files |
| **Process isolation** | OS process | SpiderMonkey compartment |
| **Network access** | Full (in Node) | Controlled (if granted) |
| **File access** | Full (in Node) | Controlled (via capabilities) |

## Technical Details

### Message Flow

1. **Host creates request:**
   ```javascript
   const request = { jsonrpc: "2.0", method: "tools/list", id: 1 };
   ```

2. **Host clones into sandbox:**
   ```javascript
   const sandboxRequest = Cu.cloneInto(request, sandbox);
   ```

3. **Host calls sandbox:**
   ```javascript
   sandbox.handleMessage(sandboxRequest);
   ```

4. **Sandbox processes and responds:**
   ```javascript
   sendToHost({ jsonrpc: "2.0", result: { tools: [...] }, id: 1 });
   ```

5. **Host receives via exported function:**
   ```javascript
   sandbox.sendToHost = Cu.exportFunction((msg) => {
     const response = Cu.cloneInto(msg, {});
     // Resolve promise
   }, sandbox);
   ```

### Request ID Management

- Each request gets a unique ID
- Response handler stored in Map<id, {resolve, reject}>
- When response arrives with matching ID, promise is resolved
- Supports concurrent requests with different IDs

### Error Handling

Uses JSON-RPC 2.0 error codes:
- `-32601` - Method not found
- `-32602` - Invalid params
- `-32603` - Internal error
- `-32000` - Application-specific errors (tool failures)

## Questions?

See:
- **Architecture doc:** `../MCP_ARCHITECTURE.md`
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Cu.Sandbox docs:** https://developer.mozilla.org/en-US/docs/Mozilla/Tech/XPCOM/Language_Bindings/Components.utils.Sandbox

## License

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
