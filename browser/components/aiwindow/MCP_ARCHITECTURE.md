# MCP Architecture for aiwindow

> **Note:** This is a design document created during initial development. The actual
> implementation may differ in details. For current implementation, see the source files
> in `browser/components/aiwindow/services/mcp/` and the README.md in that directory.

## Overview

This document describes the architecture for integrating MCP (Model Context Protocol) support into Firefox's aiwindow component. The design supports remote HTTP servers, sandboxed JavaScript servers running in Cu.Sandbox, and WebExtension-based MCP servers using the browser.harbor API.

## Architecture Principles

1. **HTTP-first**: Start with remote MCP servers over HTTP/SSE
2. **Sandbox-based JS servers**: Use Cu.Sandbox for in-browser JavaScript MCP servers
3. **Message passing transport**: Custom transport using Cu.exportFunction/cloneInto
4. **No Node.js/Docker**: Pure Firefox implementation
5. **Permission-based security**: Origin-scoped capability grants

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    aiwindow Chat                         │
│                  (Chat.sys.mjs)                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Tool Calls
                  ▼
┌─────────────────────────────────────────────────────────┐
│              MCPToolRegistry.sys.mjs                     │
│  - Namespaced tools (serverId/toolName)                 │
│  - Permission checks                                     │
│  - Tool routing                                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Tool Execution
                  ▼
┌─────────────────────────────────────────────────────────┐
│            MCPServerManager.sys.mjs                      │
│  - Server lifecycle (start/stop/restart)                │
│  - Health monitoring                                     │
│  - Transport abstraction                                 │
└───────┬─────────────────────┬──────────────┬────────────┘
        │                     │              │
        │ HTTP                │ Sandbox      │ Extension
        ▼                     ▼              ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  HTTP Transport  │  │   Sandbox    │  │    Extension     │
│  (remote)        │  │   Transport  │  │    Transport     │
└─────────┬────────┘  └──────┬───────┘  └────────┬─────────┘
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Remote MCP      │  │  Cu.Sandbox  │  │ HarborMCPRegistry│
│  Server          │  │  JS code     │  │       ↓          │
│  (HTTP/SSE)      │  │              │  │  ext-harbor.js   │
│                  │  │              │  │       ↓          │
│                  │  │              │  │ browser.harbor   │
│                  │  │              │  │       ↓          │
│                  │  │              │  │  WebExtension    │
└──────────────────┘  └──────────────┘  └──────────────────┘
```

## Transport Layer

### 1. HTTP Transport (Phase 1)

For remote MCP servers (Ollama, cloud services, localhost servers):

```javascript
// browser/components/aiwindow/services/mcp/MCPHttpTransport.sys.mjs

export class MCPHttpTransport {
  constructor(baseUrl, options = {}) {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.abortController = null;
  }

  async connect() {
    // Connect to HTTP/SSE endpoint
    const response = await fetch(`${this.baseUrl}/mcp/v1/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          clientInfo: {
            name: 'firefox-aiwindow',
            version: Services.appinfo.version,
          },
          capabilities: {},
        },
      }),
    });

    const result = await response.json();
    this.sessionId = result.sessionId;
    return result;
  }

  async request(method, params) {
    const response = await fetch(`${this.baseUrl}/mcp/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-MCP-Session': this.sessionId,
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method,
        params,
        id: Date.now(),
      }),
    });

    return response.json();
  }

  async disconnect() {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.sessionId = null;
  }
}
```

### 2. Sandbox Transport (Phase 2)

For JavaScript-based MCP servers running in Cu.Sandbox:

```javascript
// browser/components/aiwindow/services/mcp/MCPSandboxTransport.sys.mjs

export class MCPSandboxTransport {
  constructor(serverCode, options = {}) {
    this.serverCode = serverCode;
    this.sandbox = null;
    this.messageQueue = [];
    this.responseHandlers = new Map();
    this.nextRequestId = 1;
  }

  async connect() {
    // Create sandbox with restricted capabilities
    const principal = Services.scriptSecurityManager.createNullPrincipal({});

    this.sandbox = Cu.Sandbox(principal, {
      sandboxName: 'MCP Server Sandbox',
      wantXrays: true,
      wantGlobalProperties: [], // Start with no globals
      wantComponents: false,
      wantExportHelpers: false,
    });

    // Export message passing API to sandbox
    this.sandbox.sendToHost = Cu.exportFunction((message) => {
      return this._handleSandboxMessage(message);
    }, this.sandbox);

    // Export limited console for debugging
    this.sandbox.console = Cu.cloneInto({
      log: (...args) => console.log('[MCP Sandbox]', ...args),
      error: (...args) => console.error('[MCP Sandbox]', ...args),
    }, this.sandbox, { cloneFunctions: true });

    // Load server code into sandbox
    try {
      Cu.evalInSandbox(this.serverCode, this.sandbox, '1.8', 'mcp-server.js', 1);

      // Initialize MCP server in sandbox
      const initResult = await this._sendToSandbox('initialize', {
        protocolVersion: '2024-11-05',
        clientInfo: {
          name: 'firefox-aiwindow',
          version: Services.appinfo.version,
        },
      });

      return initResult;
    } catch (error) {
      Cu.nukeSandbox(this.sandbox);
      throw new Error(`Failed to initialize MCP sandbox: ${error.message}`);
    }
  }

  async request(method, params) {
    return this._sendToSandbox(method, params);
  }

  async disconnect() {
    if (this.sandbox) {
      Cu.nukeSandbox(this.sandbox);
      this.sandbox = null;
    }
  }

  // Private methods
  _sendToSandbox(method, params) {
    const requestId = this.nextRequestId++;

    return new Promise((resolve, reject) => {
      this.responseHandlers.set(requestId, { resolve, reject });

      const message = Cu.cloneInto({
        jsonrpc: '2.0',
        method,
        params,
        id: requestId,
      }, this.sandbox);

      // Call into sandbox
      try {
        const sandboxHandler = this.sandbox.handleMessage;
        if (typeof sandboxHandler === 'function') {
          sandboxHandler(message);
        } else {
          reject(new Error('Sandbox does not expose handleMessage function'));
        }
      } catch (error) {
        this.responseHandlers.delete(requestId);
        reject(error);
      }
    });
  }

  _handleSandboxMessage(sandboxMessage) {
    // Clone message out of sandbox into parent context
    const message = Cu.cloneInto(sandboxMessage, {});

    if (message.id && this.responseHandlers.has(message.id)) {
      const { resolve, reject } = this.responseHandlers.get(message.id);
      this.responseHandlers.delete(message.id);

      if (message.error) {
        reject(new Error(message.error.message));
      } else {
        resolve(message.result);
      }
    }

    // Handle notifications (no id)
    if (!message.id && message.method) {
      this._handleNotification(message);
    }
  }

  _handleNotification(message) {
    // Handle server-initiated notifications
    console.log('[MCP] Server notification:', message.method, message.params);
  }
}
```

### 3. Extension Transport

For WebExtension-based MCP servers using the browser.harbor API:

```javascript
// browser/components/aiwindow/services/mcp/MCPExtensionTransport.sys.mjs

export class MCPExtensionTransport extends MCPClient {
  #extensionId;
  #connected = false;

  constructor(extensionId, options = {}) {
    super({ clientId: options.serverId || `extension-${extensionId}` });
    this.#extensionId = extensionId;
  }

  async _connect() {
    // Verify extension exists
    const extension = lazy.ExtensionParent.GlobalManager.getExtension(
      this.#extensionId
    );
    if (!extension) {
      throw new Error(`Extension not found: ${this.#extensionId}`);
    }

    // Wait for extension to register with HarborMCPRegistry
    const maxWaitMs = 5000;
    const pollIntervalMs = 100;
    let waited = 0;
    while (!HarborMCPRegistry.has(this.#extensionId) && waited < maxWaitMs) {
      await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
      waited += pollIntervalMs;
    }

    if (!HarborMCPRegistry.has(this.#extensionId)) {
      throw new Error(`Extension did not register within ${maxWaitMs}ms`);
    }

    this.#connected = true;
  }

  async _sendRequest(message) {
    if (!this.#connected) {
      throw new Error("Not connected to extension");
    }
    const response = await HarborMCPRegistry.sendMessage(
      this.#extensionId,
      message
    );
    return response.result;
  }
}
```

The extension transport relies on HarborMCPRegistry, which bridges the transport to the browser.harbor WebExtension API:

```javascript
// browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs

class HarborMCPRegistryClass {
  _servers = new Map();      // extensionId -> { metadata, fireEvent }
  _pendingRequests = new Map(); // requestId -> { resolve, reject, timeoutId }

  register(extensionId, metadata, fireEvent) {
    this._servers.set(extensionId, { metadata, fireEvent });
  }

  async sendMessage(extensionId, message) {
    const server = this._servers.get(extensionId);
    const requestId = generateRequestId();

    return new Promise((resolve, reject) => {
      // Set timeout for response
      const timeoutId = setTimeout(() => reject(new Error("Timeout")), 30000);
      this._pendingRequests.set(requestId, { resolve, reject, timeoutId });

      // Fire event to extension (via ext-harbor.js)
      server.fireEvent(requestId, message);
    });
  }

  handleResponse(extensionId, requestId, response) {
    const pending = this._pendingRequests.get(requestId);
    if (pending && pending.extensionId === extensionId) {
      clearTimeout(pending.timeoutId);
      this._pendingRequests.delete(requestId);
      pending.resolve(response);
    }
  }
}
```

## MCP Server JavaScript Interface

For JS-based MCP servers to run in sandbox, they need to conform to this interface:

```javascript
// Example: filesystem MCP server in sandbox
// This code runs INSIDE the Cu.Sandbox

(function() {
  'use strict';

  // Server state
  const tools = [
    {
      name: 'read_file',
      description: 'Read a file from allowed directory',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string' },
        },
        required: ['path'],
      },
    },
  ];

  // Message handler exposed to host
  globalThis.handleMessage = function(message) {
    const { method, params, id } = message;

    switch (method) {
      case 'initialize':
        sendToHost({
          jsonrpc: '2.0',
          result: {
            protocolVersion: '2024-11-05',
            serverInfo: {
              name: 'filesystem',
              version: '1.0.0',
            },
            capabilities: {
              tools: {},
            },
          },
          id,
        });
        break;

      case 'tools/list':
        sendToHost({
          jsonrpc: '2.0',
          result: { tools },
          id,
        });
        break;

      case 'tools/call':
        handleToolCall(params, id);
        break;

      default:
        sendToHost({
          jsonrpc: '2.0',
          error: {
            code: -32601,
            message: 'Method not found',
          },
          id,
        });
    }
  };

  function handleToolCall(params, id) {
    const { name, arguments: args } = params;

    if (name === 'read_file') {
      // Request file read from host via capability API
      requestCapability('filesystem.read', { path: args.path })
        .then(content => {
          sendToHost({
            jsonrpc: '2.0',
            result: {
              content: [{ type: 'text', text: content }],
            },
            id,
          });
        })
        .catch(error => {
          sendToHost({
            jsonrpc: '2.0',
            error: {
              code: -32000,
              message: error.message,
            },
            id,
          });
        });
    }
  }

  // Helper to request capabilities from host
  function requestCapability(capability, params) {
    return new Promise((resolve, reject) => {
      // This would be implemented via another exportFunction
      // For now, simplified
      reject(new Error('Capability system not yet implemented'));
    });
  }
})();
```

## Security Model

### Permission System

Permissions are scoped by origin and server:

```javascript
// Permission scopes
const PERMISSION_SCOPES = {
  'mcp:server.install': 'Install new MCP servers',
  'mcp:server.start': 'Start MCP servers',
  'mcp:tools.list': 'List available tools',
  'mcp:tools.call': 'Execute tools',
  'mcp:resources.read': 'Read resources',
};

// Grant types
const GRANT_TYPES = {
  ALLOW_ONCE: 'once',    // Session-scoped
  ALLOW_ALWAYS: 'always', // Persistent
  DENY: 'deny',          // Explicitly denied
};
```

### Capability System for Sandboxed Servers

**Two-Layer Security Model:**

1. **Origin Allowlist (Config-Level)**
   - Servers declare which origins they need access to in their config
   - All network requests validated against this allowlist
   - Prevents accidental or malicious requests to arbitrary URLs

2. **User Permissions (Runtime-Level)**
   - User must approve each capability (filesystem, network, browser state)
   - Can grant ALLOW_ONCE or ALLOW_ALWAYS
   - Checked on every capability request

**Example Configuration:**
```javascript
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

**Capability Implementation:**
```javascript
// In MCPSandboxTransport
this.sandbox.requestFetch = Cu.exportFunction(async (url, options) => {
  const requestOrigin = new URL(url).origin;

  // Layer 1: Check origin allowlist
  if (this.config.allowedOrigins &&
      !this.config.allowedOrigins.includes(requestOrigin)) {
    throw new Error(`Origin ${requestOrigin} not in server allowlist`);
  }

  // Layer 2: Check user permissions
  if (!await this.permissionManager.hasPermission(
    this.serverId,
    `network:fetch:${requestOrigin}`
  )) {
    throw new Error('Permission denied');
  }

  return fetch(url, options);
}, this.sandbox);

this.sandbox.requestFileRead = Cu.exportFunction(async (path) => {
  // Check user permission for filesystem access
  if (!await this.permissionManager.hasPermission(
    this.serverId,
    `filesystem:read:${path}`
  )) {
    throw new Error('Permission denied');
  }

  return IOUtils.readUTF8(path);
}, this.sandbox);
```

## Implementation Status

**Last Updated:** 2026-01-20

### ✅ Completed Components

**Transport Layer (Foundation)**
- **MCPClient.sys.mjs** - Base class with common protocol handling
  - Clean inheritance model with template method pattern
  - Automatic initialization handshake
  - Promise-based async API
  - Request ID generation and correlation

- **MCPSandboxTransport.sys.mjs** - Sandbox-based transport (basic)
  - Cu.Sandbox with null principal and minimal privileges
  - Bidirectional message passing via Cu.exportFunction/cloneInto
  - Concurrent request support with response handler map
  - Proper resource cleanup with Cu.nukeSandbox
  - ⚠️ **Limitation**: No capability API yet (can't access files, network, or browser state)

- **MCPHttpTransport.sys.mjs** - HTTP-based transport (basic)
  - JSON-RPC 2.0 over HTTP POST
  - URL validation and content-type checking
  - Response ID verification
  - ⚠️ **Limitations**: No timeout handling, retries, or authentication

- **MCPExtensionTransport.sys.mjs** - WebExtension-based transport
  - Connects to extensions using browser.harbor API
  - Polls for extension registration (up to 5 seconds)
  - Routes requests through HarborMCPRegistry

- **HarborMCPRegistry.sys.mjs** - Extension server registry
  - Central registry shared between ext-harbor.js and MCPExtensionTransport
  - Request/response routing with 30-second timeout
  - Listener system for registration events

- **browser.harbor API** (browser/components/extensions/)
  - WebExtension API for MCP servers
  - schemas/harbor.json - API schema definition
  - parent/ext-harbor.js - API implementation
  - Supports registerMCPServer, unregisterMCPServer, sendMCPResponse, onMCPMessage

**Server Management Layer**
- ✅ **MCPServerManager.sys.mjs** - Server lifecycle management (273 lines)
  - Server registration with validation (HTTP and sandbox types)
  - Start/stop/restart operations with status tracking
  - Status states: STOPPED, STARTING, RUNNING, STOPPING, ERROR
  - Health monitoring (uptime, error tracking, server info)
  - Bulk operations (startAllServers, stopAllServers)
  - Auto-start capability (enabled=true on registration)
  - Transport factory and lifecycle management
  - Multiple concurrent servers supported

**Tool Management Layer**
- ✅ **MCPToolRegistry.sys.mjs** - Tool registration and routing (180 lines)
  - Global tool registry with automatic namespacing (serverId/toolName)
  - Tool lookup by fully qualified name or short name
  - Dynamic tool routing to appropriate server transport
  - Tool schema retrieval for validation
  - Server tool management (register, unregister, refresh)
  - Duplicate tool handling across multiple servers
  - Full integration with MCPServerManager

**Test Infrastructure**
- Comprehensive xpcshell tests (all passing)
  - test_MCPSandboxTransport.js - Connection, tools, errors, concurrency
  - test_MCPHttpTransport.js - HTTP transport with HttpServer
  - test_MCPExtensionTransport.js - HarborMCPRegistry, extension messaging
  - test_MCPServerManager.js - Lifecycle, errors, bulk operations
  - test_MCPToolRegistry.js - Registration, routing, real tool execution
  - echo-server.js - Reusable test server with 3 tools
- Browser tests for extension API
  - browser_ext_harbor.js - browser.harbor API registration, messaging, errors

**Documentation**
- README.md - Usage guide with important caveats
- HANDOFF.md - Complete handoff with gotchas for next developer
- MCP_ARCHITECTURE.md - This document (architectural vision)
- POC_SUMMARY.md - Executive summary with performance data
- Well-commented code with JSDoc throughout

### 🔄 In Progress

- None (awaiting next phase decisions)

### ❌ Not Yet Started (Phase 1 Requirements)

**Security Layer**
- ❌ **MCPPermissionManager.sys.mjs** - Permission system
  - User permission prompts
  - Origin-scoped capability grants
  - Audit logging
  - Permission persistence

**Integration Layer**
- ❌ **Chat.sys.mjs Integration**
  - Dynamic tool loading from MCP servers
  - Replace hardcoded toolMap with registry
  - Tool execution routing
  - Error handling and fallbacks

**Capability System**
- ❌ **Sandbox Capability API**
  - Exported functions for file I/O
  - Network request capabilities
  - Browser state access (tabs, history, bookmarks)
  - Permission checking at runtime

### 📊 Phase Progress

| Phase | Status | Completion |
|-------|--------|------------|
| Phase 1: HTTP Remote Servers | 🟡 In Progress | 70% (7/10 deliverables) |
| Phase 2: Sandbox JS Servers | 🟡 Partial | 40% (transport + management, no capabilities) |
| Phase 3: Advanced Features | ⚪ Not Started | 0% |

**Phase 1 Deliverables:**
1. ✅ MCPClient base class
2. ✅ MCPHttpTransport
3. ✅ MCPSandboxTransport
4. ✅ MCPServerManager
5. ✅ MCPToolRegistry
6. ✅ Comprehensive tests
7. ✅ Documentation
8. ❌ MCPPermissionManager
9. ❌ Chat.sys.mjs integration
10. ❌ Settings UI

### 🎯 Current State

**What Works:**
- Both transports can connect to MCP servers
- Server lifecycle management (start, stop, restart, status tracking)
- Tool registry with automatic namespacing and routing
- Tool discovery (tools/list) works
- Tool execution (tools/call) works with dynamic routing
- Multiple servers can run concurrently
- Concurrent requests supported
- **Comprehensive test coverage (58 tests, all passing)**

**What Doesn't Work (Production Blockers):**
1. **Cannot be used from Chat** - No integration with aiwindow chat interface yet
2. **No permission system** - All operations implicitly trusted (security risk)
3. **Sandbox transport limited** - No capability API means sandboxed servers can't access files/network/browser state
4. **HTTP transport limited** - No timeouts, retries, or authentication
5. **No UI** - No settings interface for managing servers

**Estimated Time to Production:**
- Complete Phase 1 deliverables: **2-3 weeks** additional focused development
- Add Phase 2 capabilities: **2-3 weeks**
- **Total**: 4-6 weeks to production-ready state

### 📋 Next Steps (Priority Order)

1. ✅ **MCPServerManager - COMPLETED**
   - ✅ Server registration and lifecycle
   - ✅ Configuration management
   - ✅ Health monitoring
   - ✅ Comprehensive tests

2. ✅ **MCPToolRegistry - COMPLETED**
   - ✅ Tool registration with namespacing
   - ✅ Dynamic tool routing
   - ✅ Integration-ready for Chat.sys.mjs
   - ✅ Tests include real tool execution

3. **Integrate with Chat.sys.mjs** (1 week)
   - Replace hardcoded toolMap
   - Dynamic tool loading from registry
   - MCP tool execution routing
   - Built-in tool compatibility

4. **Basic Permission System** (1-2 weeks)
   - User permission prompts
   - Simple ALLOW/DENY grants
   - Permission persistence
   - Integration with tool execution

5. **Sandbox Capability API with Origin Restrictions** (1-2 weeks)
   - exportFunction APIs for file I/O
   - Network request capabilities with origin allowlist enforcement
   - Two-layer security: config-level allowlist + runtime permission checks
   - Browser state access (tabs, history)
   - Audit logging for all capability requests

6. **HTTP Transport Enhancements** (1 week)
   - Timeout support
   - Retry logic with exponential backoff
   - Bearer token authentication

7. **Settings UI** (1 week)
   - Server management interface
   - Enable/disable servers
   - View available tools
   - Permission management

### 🔒 Known Security Limitations

**Current State:**
- ✅ Sandbox uses null principal
- ✅ No XPCOM access
- ✅ No global properties
- ✅ Proper memory isolation

**Missing (Security Risks):**
- ❌ No permission system (everything implicitly allowed)
- ❌ No origin restrictions (sandbox servers can't declare allowed origins yet)
- ❌ No resource limits (CPU/memory can be exhausted)
- ❌ No input validation (tool arguments unchecked)
- ❌ No code signing (arbitrary code can be loaded)
- ❌ No audit logging (no record of operations)

**Planned Security Features:**
- Two-layer security: origin allowlist (config) + user permissions (runtime)
- Server declares allowed origins in registration config
- All network requests validated against allowlist
- Audit logging for all capability requests

### 📝 Technical Debt

1. **HTTP Transport:** No session management despite architecture doc mentioning sessionId
2. **Error Handling:** All errors are generic Error objects (no structured error types)
3. **Performance:** No benchmarking or profiling data yet
4. **Documentation:** Architecture doc examples don't match actual implementation

## Implementation Plan

### Phase 1: HTTP Remote Servers (Weeks 1-3)

**Goals:**
- Support remote MCP servers over HTTP
- Ollama integration
- Basic permission system

**Deliverables:**
1. `MCPHttpTransport.sys.mjs` - HTTP transport implementation
2. `MCPServerManager.sys.mjs` - Server lifecycle management
3. `MCPToolRegistry.sys.mjs` - Tool registration and routing
4. `MCPPermissionManager.sys.mjs` - Permission grants
5. Integration with `Chat.sys.mjs` for tool calling
6. Basic UI for server management

**Key Files:**
- `browser/components/aiwindow/services/mcp/MCPHttpTransport.sys.mjs`
- `browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs`
- `browser/components/aiwindow/services/mcp/MCPToolRegistry.sys.mjs`
- `browser/components/aiwindow/services/permissions/MCPPermissionManager.sys.mjs`
- `browser/components/aiwindow/models/OllamaProvider.sys.mjs`

### Phase 2: Sandbox-Based JS Servers (Weeks 4-6)

**Goals:**
- Support JavaScript MCP servers in Cu.Sandbox
- Message passing transport
- Capability-based security with origin restrictions

**Deliverables:**
1. `MCPSandboxTransport.sys.mjs` - Sandbox transport implementation
2. Capability API for sandboxed servers (filesystem, network, browser state)
3. **Origin restriction enforcement** - Servers declare allowed origins, requests validated
4. Example JS-based MCP servers
5. Security review and hardening

**Key Files:**
- `browser/components/aiwindow/services/mcp/MCPSandboxTransport.sys.mjs`
- `browser/components/aiwindow/services/mcp/MCPCapabilityProvider.sys.mjs`

**Security Features:**
- Two-layer model: origin allowlist (config) + user permissions (runtime)
- Audit logging for all capability requests
- Origin validation on every network request

### Phase 3: Advanced Features (Weeks 7-9)

**Goals:**
- Server catalog and discovery
- Advanced permission UI
- Performance optimization

**Deliverables:**
1. Server catalog (Remote Settings)
2. One-click server installation
3. Advanced permission management UI
4. Performance profiling and optimization

## Directory Structure

```
browser/components/aiwindow/
├── models/
│   ├── Chat.sys.mjs (integrate MCP tools)
│   ├── Tools.sys.mjs (extend with MCP)
│   ├── OllamaProvider.sys.mjs
│   └── LLMProvider.sys.mjs
├── services/
│   └── mcp/
│       ├── MCPClient.sys.mjs           - Base transport class
│       ├── MCPServerManager.sys.mjs    - Server lifecycle management
│       ├── MCPHttpTransport.sys.mjs    - HTTP transport
│       ├── MCPSandboxTransport.sys.mjs - Cu.Sandbox transport
│       ├── MCPExtensionTransport.sys.mjs - WebExtension transport
│       ├── HarborMCPRegistry.sys.mjs   - Extension server registry
│       ├── MCPToolRegistry.sys.mjs     - Tool discovery and routing
│       ├── HarborServerStore.sys.mjs   - Persistent server storage
│       ├── HarborBuiltinServers.sys.mjs - Built-in server templates
│       ├── moz.build
│       └── tests/xpcshell/             - Comprehensive test suite
├── extensions/
│   └── time-server-mcp/                - Example extension MCP server
│       ├── manifest.json
│       └── background.js
└── ui/
    └── content/
        ├── harbor.html                 - Main Harbor UI
        ├── harbor.css                  - Harbor styles
        ├── harbor.mjs                  - Harbor UI logic
        └── HARBOR_README.md            - Harbor documentation

browser/components/extensions/
├── schemas/
│   └── harbor.json                     - browser.harbor API schema
├── parent/
│   └── ext-harbor.js                   - browser.harbor implementation
└── test/browser/
    └── browser_ext_harbor.js           - Extension API tests
```

## Preferences

```
browser.aiwindow.mcp.enabled - Enable MCP system
browser.aiwindow.mcp.servers - JSON array of server configs
browser.aiwindow.mcp.sandbox.enabled - Enable sandboxed JS servers
browser.aiwindow.mcp.ollama.url - Ollama API URL (default: http://localhost:11434)
browser.aiwindow.mcp.http.timeout - HTTP request timeout (default: 30000ms)
```

## Next Steps

1. Create basic directory structure and build files
2. Implement `MCPHttpTransport.sys.mjs` for remote servers
3. Build `MCPServerManager.sys.mjs` for lifecycle management
4. Integrate with existing `Chat.sys.mjs` for tool calling
5. Create proof-of-concept with Ollama integration
6. Iterate on sandbox transport design

## Questions for Discussion

1. Should we support stdio transport via nsIProcess, or focus purely on HTTP + Sandbox?
2. What level of filesystem access should sandboxed servers have?
3. Should we use Remote Settings for server catalog, or local manifest files?
4. How should we handle server updates and versioning?
