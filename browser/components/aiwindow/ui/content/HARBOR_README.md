# Harbor - MCP Development Interface

Harbor is a dedicated development UI for testing and managing Model Context Protocol (MCP) servers and tools in Firefox.

## Features

### Core
- **MCP Server Management**: Create, edit, delete, and toggle servers
- **Sandbox Servers**: JavaScript servers running in Cu.Sandbox with code editor
- **HTTP Servers**: Connect to external MCP servers with bearer token auth
- **Tool Registry**: See all available tools from all servers
- **Interactive Chat**: Test MCP tools with Ollama integration

### Development Tools
- **Syntax Highlighting**: JavaScript code editor with syntax highlighting
- **Server Templates**: 5 built-in templates (Hello, Time, Calculator, String Utils, Random)
- **Tool Inspector**: View detailed tool info, schemas, and test tools directly
- **Execution Log**: Track tool call timing and results
- **Console Output**: View console.log output from sandbox servers
- **Import/Export**: Share server configurations as JSON

### UI/UX
- **Dark Mode**: Full dark mode support using Firefox design tokens
- **Model Info Panel**: Shows current endpoint/model status
- **Type Badges**: Visual distinction between sandbox and HTTP servers
- **Test Connection**: Verify HTTP server connectivity before saving

## Access Harbor

Navigate to:
```
chrome://browser/content/aiwindow/harbor.html
```

## Quick Start

### 1. Make sure Ollama is running

```bash
# Start Ollama (if not already running)
ollama serve

# Pull a model that supports function calling
ollama pull functiongemma
```

### 2. Open Harbor in Firefox

```bash
# Start Firefox with the right profile
./mach run --temp-profile \
  --setpref browser.aiwindow.enabled=true \
  --setpref browser.aiwindow.endpoint=http://localhost:11434/v1 \
  --setpref browser.aiwindow.model=functiongemma \
  --setpref browser.aiwindow.apiKey=ollama \
  --setpref browser.ml.logLevel=All \
  --setpref browser.aiwindow.firstrun.hasCompleted=true

# Then navigate to:
chrome://browser/content/aiwindow/harbor.html
```

Or if you already have Firefox running, just navigate to the URL and Harbor will set the prefs for you.

### 3. Test with Real Ollama Streaming

Harbor is fully wired with Ollama. The chat uses real streaming with tool calling support.

Try asking the model to use tools:
- "Can you call the hello_mcp tool with my name?"
- "Please use the echo tool to repeat 'MCP is working'"
- "What tools do you have available?"

## UI Layout

```
+-------------------------------------------------------------+
| Harbor - MCP Development                      [Status Bar]  |
+--------------+--------------------------+-------------------+
|              |                          | Model Info        |
| MCP Servers  |   Chat Interface         | - Endpoint        |
| ----------   |   ----------------       | - Model           |
| * Hello      |   Messages...            | - Status          |
|   [SANDBOX]  |                          |-------------------|
| * Time       |   [Tool Call: hello]     | Tool Inspector    |
|   [SANDBOX]  |   [Tool Result: ...]     | - Name            |
|              |                          | - Description     |
| + Add Server |   [Input]                | - Schema          |
| Import/Export|   [Send] (Ctrl+Enter)    | - Test Form       |
|              |                          |-------------------|
| Tools        |                          | Console Output    |
| -----        |                          |-------------------|
| * hello_mcp  |                          | Execution Log     |
| * get_time   |                          |                   |
+--------------+--------------------------+-------------------+
```

## Implemented Features

### Phase 1 (Complete)
- [x] Real LLM integration using Chat.sys.mjs
- [x] Add Server dialog with code editor
- [x] Server start/stop controls
- [x] Tool execution display in chat

### Phase 2 (Complete)
- [x] Server code editor with syntax highlighting
- [x] Tool execution history/logs
- [x] Better error handling and display
- [x] Console output capture

### Additional Features (Complete)
- [x] Server templates (5 templates)
- [x] Import/Export functionality
- [x] Dark mode support
- [x] HTTP server support with bearer token
- [x] Test connection for HTTP servers
- [x] Model info display
- [x] Keyboard shortcuts (Ctrl+Enter, Escape)

## Capability Sandboxing Plan

MCP servers need controlled access to system and browser capabilities. This plan outlines a permission-based system for granting and restricting what MCP tools can do.

### Design Principles

1. **Default Deny**: All capabilities disabled by default
2. **Least Privilege**: Grant minimum permissions needed
3. **User Consent**: User explicitly approves capability grants
4. **Audit Trail**: Log all capability usage for review
5. **Revocable**: Permissions can be revoked at any time

### Permission Layers

There are two distinct permission layers:

```
+--------------------------------------------------+
|                    USER REQUEST                   |
|            "Find my open tabs about React"        |
+--------------------------------------------------+
                         |
                         v
+--------------------------------------------------+
|              LLM TOOL SELECTION                   |
|  LLM decides which tool to call based on         |
|  available tools and user intent                  |
|  -> Calls: browser.listTabs({ query: "React" })  |
+--------------------------------------------------+
                         |
                         v
+--------------------------------------------------+
|           CAPABILITY GATE (this layer)           |
|  Checks if server has permission to use the      |
|  browser.tabs capability before execution        |
|  -> Check: Does server have tabs.read?           |
+--------------------------------------------------+
                         |
                         v
+--------------------------------------------------+
|              TOOL EXECUTION                       |
|  If allowed, execute the tool and return result  |
+--------------------------------------------------+
```

**Layer 1: LLM Tool Selection** - The LLM decides WHICH tools to call based on available tools and user intent. This is NOT a security boundary.

**Layer 2: Capability Gate** - Enforces WHAT the server is allowed to do regardless of what tools it exposes. This IS the security boundary.

### Capability Categories

#### System Capabilities

```javascript
{
  filesystem: {
    enabled: false,
    read: [],                    // Allowed read paths (globs)
    write: [],                   // Allowed write paths (globs)
    deny: ["**/.env", "**/*.key", "**/credentials*"]
  },
  network: {
    enabled: false,
    allowedHosts: [],            // ["api.example.com"]
    allowedPorts: [80, 443],
    denyPrivate: true            // Block local network
  },
  subprocess: {
    enabled: false,
    allowedCommands: [],         // ["git", "npm", "node"]
    denyShell: true              // Block sh, bash, cmd
  },
  clipboard: { read: false, write: false },
  notifications: { enabled: false }
}
```

#### Browser Capabilities

```javascript
{
  tabs: {
    read: false,                 // List tabs, get tab info
    navigate: false,             // Change tab URLs
    create: false,               // Open new tabs
    close: false,                // Close tabs
    captureScreenshot: false     // Screenshot tab content
  },
  history: {
    read: false,                 // Search/list history
    write: false                 // Add/delete history entries
  },
  bookmarks: {
    read: false,                 // List/search bookmarks
    write: false                 // Create/edit/delete bookmarks
  },
  downloads: {
    read: false,                 // List downloads
    initiate: false,             // Start downloads
    manage: false                // Pause/cancel/remove
  },
  cookies: {
    read: false,                 // Read cookies (SENSITIVE)
    write: false                 // Set/delete cookies (SENSITIVE)
  },
  storage: {
    read: false,                 // Read localStorage/sessionStorage
    write: false
  },
  activeTab: {
    readContent: false,          // Read page DOM/text
    executeScript: false         // Inject scripts (DANGEROUS)
  }
}
```

### Capability Profile Schema

```javascript
{
  serverId: "my-server",
  version: 1,

  // Pre-defined level or "custom"
  level: "isolated" | "browser-readonly" | "workspace" | "developer" | "custom",

  // System capabilities
  system: {
    filesystem: { /* ... */ },
    network: { /* ... */ },
    subprocess: { /* ... */ },
    clipboard: { /* ... */ },
    notifications: { /* ... */ }
  },

  // Browser capabilities
  browser: {
    tabs: { /* ... */ },
    history: { /* ... */ },
    bookmarks: { /* ... */ },
    downloads: { /* ... */ },
    cookies: { /* ... */ },
    storage: { /* ... */ },
    activeTab: { /* ... */ }
  },

  // Audit settings
  audit: {
    logAllChecks: true,          // Log allowed and denied
    logDeniedOnly: false,        // Only log denials
    retentionDays: 7
  }
}
```

### Capability Levels

| Level | System | Browser | Use Case |
|-------|--------|---------|----------|
| **Isolated** | None | None | Math, text processing, pure computation |
| **Browser Read** | None | tabs.read, history.read, bookmarks.read | Tab search, history lookup |
| **Browser Full** | None | All browser (except cookies, executeScript) | Browser automation |
| **Workspace** | filesystem (project dir) | None | Code editing, file operations |
| **Developer** | filesystem + subprocess | tabs.read | Full dev environment |
| **Custom** | User-defined | User-defined | Advanced configuration |

### Dangerous Capabilities

Some capabilities require extra confirmation:

| Capability | Risk | Mitigation |
|------------|------|------------|
| `cookies.read` | Session hijacking | Require explicit domain allowlist |
| `cookies.write` | Auth bypass | Double confirmation dialog |
| `activeTab.executeScript` | XSS, data theft | Disabled by default, special approval |
| `subprocess.enabled` | System compromise | Command allowlist only |
| `filesystem.write` | Data loss | Path restrictions, no system dirs |

### Architecture

```
+------------------------------------------------------------------+
|                         Tool Call Request                         |
|              (from LLM via MCPToolRegistry.callTool)              |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      CapabilityGate                               |
|  - Loads profile for serverId                                     |
|  - Checks capability + operation against profile                  |
|  - Returns { allowed, reason, auditId }                           |
+------------------------------------------------------------------+
                              |
            +----------------+----------------+
            |                                 |
            v                                 v
      +-----------+                    +-----------+
      |  ALLOWED  |                    |  DENIED   |
      +-----------+                    +-----------+
            |                                 |
            v                                 v
+-------------------+              +--------------------+
| CapabilityBridge  |              | Return error to    |
| - Provides safe   |              | tool caller with   |
| - API wrappers    |              | permission details |
+-------------------+              +--------------------+
            |
            v
+-------------------+
| Execute operation |
| via Firefox APIs  |
+-------------------+
            |
            v
+-------------------+
|   AuditLogger     |
| - Log operation   |
| - Track usage     |
+-------------------+
```

### Key Components

#### 1. CapabilityGate.sys.mjs

Central permission checker. Simple, testable, no side effects.

```javascript
const DEFAULT_DENY_PATHS = ["**/.env", "**/*.key", "**/credentials*", "**/.ssh/**"];

export class CapabilityGate {
  #profiles = new Map();

  constructor(profileStore) {
    this.profileStore = profileStore;
  }

  // Main entry point - check if operation is allowed
  checkPermission(serverId, category, capability, operation, params = {}) {
    const profile = this.#getProfile(serverId);

    if (category === "system") {
      return this.#checkSystemCapability(profile, capability, operation, params);
    } else if (category === "browser") {
      return this.#checkBrowserCapability(profile, capability, operation, params);
    }

    return { allowed: false, reason: "Unknown capability category" };
  }

  #checkSystemCapability(profile, capability, operation, params) {
    const cap = profile.system?.[capability];
    if (!cap?.enabled && capability !== "filesystem") {
      return { allowed: false, reason: `${capability} not enabled` };
    }

    switch (capability) {
      case "filesystem":
        return this.#checkFilesystem(cap, operation, params.path);
      case "network":
        return this.#checkNetwork(cap, params.url);
      case "subprocess":
        return this.#checkSubprocess(cap, params.command);
      default:
        return { allowed: cap?.enabled === true };
    }
  }

  #checkFilesystem(cap, operation, path) {
    if (!cap?.enabled) {
      return { allowed: false, reason: "Filesystem access disabled" };
    }

    const normalized = this.#normalizePath(path);
    if (!normalized) {
      return { allowed: false, reason: "Invalid path" };
    }

    // Check deny patterns first (highest priority)
    const denyPatterns = [...DEFAULT_DENY_PATHS, ...(cap.deny || [])];
    for (const pattern of denyPatterns) {
      if (this.#matchGlob(normalized, pattern)) {
        return { allowed: false, reason: `Path matches deny pattern` };
      }
    }

    // Check allow patterns
    const allowList = operation === "read" ? cap.read : cap.write;
    if (!allowList?.length) {
      return { allowed: false, reason: `No ${operation} paths configured` };
    }

    for (const allowed of allowList) {
      if (this.#isWithinPath(normalized, allowed)) {
        return { allowed: true };
      }
    }

    return { allowed: false, reason: "Path not in allowlist" };
  }

  #checkBrowserCapability(profile, capability, operation) {
    const cap = profile.browser?.[capability];
    if (!cap) {
      return { allowed: false, reason: `${capability} not configured` };
    }

    const allowed = cap[operation] === true;
    return {
      allowed,
      reason: allowed ? null : `${capability}.${operation} not permitted`
    };
  }

  #normalizePath(path) {
    if (!path || typeof path !== "string") return null;
    // Resolve to absolute, reject traversal attempts
    try {
      const resolved = PathUtils.normalize(path);
      if (resolved.includes("..")) return null;
      return resolved;
    } catch {
      return null;
    }
  }

  #matchGlob(path, pattern) {
    // Simple glob matching - * matches anything except /, ** matches anything
    const regex = pattern
      .replace(/\*\*/g, "<<<GLOBSTAR>>>")
      .replace(/\*/g, "[^/]*")
      .replace(/<<<GLOBSTAR>>>/g, ".*");
    return new RegExp(`^${regex}$`).test(path);
  }

  #isWithinPath(targetPath, allowedPath) {
    const normalizedAllowed = this.#normalizePath(allowedPath);
    if (!normalizedAllowed) return false;

    // Handle glob patterns in allowed path
    if (allowedPath.includes("*")) {
      return this.#matchGlob(targetPath, allowedPath);
    }

    // Check if target is within allowed directory
    return targetPath === normalizedAllowed ||
           targetPath.startsWith(normalizedAllowed + "/");
  }

  #getProfile(serverId) {
    if (!this.#profiles.has(serverId)) {
      this.#profiles.set(serverId, this.profileStore.load(serverId));
    }
    return this.#profiles.get(serverId) || this.#getDefaultProfile();
  }

  #getDefaultProfile() {
    return {
      level: "isolated",
      system: {
        filesystem: { enabled: false },
        network: { enabled: false },
        subprocess: { enabled: false },
        clipboard: { read: false, write: false },
        notifications: { enabled: false }
      },
      browser: {
        tabs: { read: false, navigate: false, create: false, close: false },
        history: { read: false, write: false },
        bookmarks: { read: false, write: false },
        downloads: { read: false, initiate: false },
        cookies: { read: false, write: false },
        storage: { read: false, write: false },
        activeTab: { readContent: false, executeScript: false }
      }
    };
  }
}
```

#### 2. CapabilityBridge.sys.mjs

Provides safe API wrappers that check permissions before execution.

```javascript
export class CapabilityBridge {
  constructor(serverId, gate) {
    this.serverId = serverId;
    this.gate = gate;
  }

  // Create APIs to expose to sandbox
  createAPIs() {
    return {
      fs: this.#createFilesystemAPI(),
      browser: this.#createBrowserAPI(),
      net: this.#createNetworkAPI()
    };
  }

  #createFilesystemAPI() {
    return {
      readFile: async (path) => {
        this.#requirePermission("system", "filesystem", "read", { path });
        return IOUtils.readUTF8(path);
      },

      writeFile: async (path, content) => {
        this.#requirePermission("system", "filesystem", "write", { path });
        return IOUtils.writeUTF8(path, content);
      },

      listDir: async (path) => {
        this.#requirePermission("system", "filesystem", "read", { path });
        const children = await IOUtils.getChildren(path);
        return children.map(p => PathUtils.filename(p));
      },

      exists: async (path) => {
        this.#requirePermission("system", "filesystem", "read", { path });
        return IOUtils.exists(path);
      }
    };
  }

  #createBrowserAPI() {
    return {
      tabs: {
        list: async (query = {}) => {
          this.#requirePermission("browser", "tabs", "read");
          // Return sanitized tab info
          const windows = Services.wm.getEnumerator("navigator:browser");
          const tabs = [];
          for (const win of windows) {
            for (const tab of win.gBrowser.tabs) {
              tabs.push({
                id: tab.linkedPanel,
                url: tab.linkedBrowser.currentURI.spec,
                title: tab.label,
                active: tab.selected
              });
            }
          }
          return tabs;
        },

        create: async (url) => {
          this.#requirePermission("browser", "tabs", "create");
          // Validate URL before opening
          const validUrl = this.#validateUrl(url);
          const win = Services.wm.getMostRecentWindow("navigator:browser");
          win.gBrowser.addTab(validUrl, { triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal() });
        },

        navigate: async (tabId, url) => {
          this.#requirePermission("browser", "tabs", "navigate");
          const validUrl = this.#validateUrl(url);
          // Find and navigate tab...
        }
      },

      history: {
        search: async (query, maxResults = 100) => {
          this.#requirePermission("browser", "history", "read");
          // Use Places API to search history
          // Return sanitized results
        }
      },

      bookmarks: {
        search: async (query) => {
          this.#requirePermission("browser", "bookmarks", "read");
          // Use Places API
        },

        create: async (title, url, folder) => {
          this.#requirePermission("browser", "bookmarks", "write");
          // Validate and create bookmark
        }
      }
    };
  }

  #createNetworkAPI() {
    return {
      fetch: async (url, options = {}) => {
        this.#requirePermission("system", "network", "fetch", { url });
        // Use fetch with appropriate restrictions
        return fetch(url, {
          ...options,
          credentials: "omit",  // Never send credentials
          mode: "cors"
        });
      }
    };
  }

  #requirePermission(category, capability, operation, params = {}) {
    const result = this.gate.checkPermission(
      this.serverId, category, capability, operation, params
    );
    if (!result.allowed) {
      throw new CapabilityError(capability, operation, result.reason);
    }
  }

  #validateUrl(url) {
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) {
        throw new Error("Only http/https URLs allowed");
      }
      return parsed.href;
    } catch (e) {
      throw new Error(`Invalid URL: ${e.message}`);
    }
  }
}

export class CapabilityError extends Error {
  constructor(capability, operation, reason) {
    super(`Permission denied: ${capability}.${operation} - ${reason}`);
    this.name = "CapabilityError";
    this.capability = capability;
    this.operation = operation;
    this.reason = reason;
  }
}
```

#### 3. CapabilityProfileStore.sys.mjs

Stores capability profiles in preferences.

```javascript
const PREF_PREFIX = "browser.aiwindow.harbor.capabilities.";

export class CapabilityProfileStore {
  load(serverId) {
    try {
      const json = Services.prefs.getStringPref(
        `${PREF_PREFIX}${serverId}`,
        null
      );
      return json ? JSON.parse(json) : null;
    } catch {
      return null;
    }
  }

  save(serverId, profile) {
    Services.prefs.setStringPref(
      `${PREF_PREFIX}${serverId}`,
      JSON.stringify(profile)
    );
  }

  delete(serverId) {
    Services.prefs.clearUserPref(`${PREF_PREFIX}${serverId}`);
  }

  listAll() {
    // Return all server IDs with saved profiles
    const profiles = [];
    const prefBranch = Services.prefs.getBranch(PREF_PREFIX);
    for (const name of prefBranch.getChildList("")) {
      profiles.push(name);
    }
    return profiles;
  }
}
```

### Security Considerations

1. **Path Traversal**: All paths normalized, `..` rejected, symlinks resolved
2. **Glob DoS**: Limit pattern complexity, timeout on matching
3. **URL Validation**: Only http/https, no file://, no javascript:
4. **Credential Isolation**: Network requests never include cookies/auth
5. **Script Injection**: `activeTab.executeScript` disabled by default, requires special approval
6. **Audit Everything**: All permission checks logged for review

### Implementation Phases

**Phase A - Core Gate**
- [x] CapabilityGate with filesystem permission checking
- [x] Path normalization and glob matching
- [x] Default deny patterns
- [x] Comprehensive unit tests (100+ tests)

**Phase B - Profile Storage**
- [x] CapabilityProfileStore with pref persistence
- [x] Default profiles for capability levels (isolated, browser-readonly, browser-full, workspace, developer)
- [x] Profile validation
- [x] Custom profile creation with level-based templates

**Phase C - Browser Capabilities**
- [x] Tab API (list, get, create, navigate, close)
- [x] History API (search)
- [x] Bookmarks API (search, create)

**Phase D - Bridge Integration**
- [x] CapabilityBridge connecting gate to sandbox
- [x] Filesystem API (readFile, writeFile, exists, stat, listDir, mkdir, remove, copy, move)
- [x] Network API (fetch with credential isolation)
- [x] Clipboard API (read, write)
- [x] Notifications API (show)
- [x] Audit logging for all permission checks
- [x] CapabilityError for permission denials

**Phase E - UI**
- [x] Capability editor in server dialog (level selector + summary display)
- [ ] Runtime permission prompts
- [ ] Audit log viewer

## Future Roadmap

### Phase 3 - Security & Polish
1. **Permission System UI**: User approval for tool execution
2. **Resource Limits UI**: Configure sandbox memory/time limits
3. **Audit Logging**: Track all tool executions with user/timestamp
4. **Input Validation UI**: Preview/edit tool arguments before execution

### Phase 4 - Advanced Features
1. **Performance Monitoring**: Track execution time, memory usage
2. **Multi-server Orchestration**: Tool pipelines across servers
3. **Live Reload**: Auto-restart servers on code changes
4. **Tool Versioning**: Track changes to tool schemas

### Phase 5 - Ecosystem
1. **Server Marketplace**: Community-shared server templates
2. **Remote Server Discovery**: mDNS/DNS-SD for local MCP servers
3. **Integration Tests**: Automated testing framework
4. **Documentation Generator**: Auto-generate docs from tool schemas

## Architecture

```
Harbor UI (harbor.mjs)
    |
MCPServerManager + MCPToolRegistry
    |
MCPSandboxTransport / MCPHttpTransport
    |
MCP Servers (Cu.Sandbox or HTTP)
```

## Files

```
browser/components/aiwindow/
+-- ui/content/
|   +-- harbor.html          - Main HTML structure
|   +-- harbor.css           - Styles (dark mode, syntax highlighting)
|   +-- harbor.mjs           - UI logic and MCP integration
|   +-- HARBOR_README.md     - This file
+-- services/mcp/
|   +-- MCPServerManager.sys.mjs    - Server lifecycle management
|   +-- MCPToolRegistry.sys.mjs     - Tool discovery and routing
|   +-- MCPSandboxTransport.sys.mjs - Cu.Sandbox transport
|   +-- MCPHttpTransport.sys.mjs    - HTTP transport with retry logic
|   +-- MCPClient.sys.mjs           - Base client class
|   +-- HarborServerStore.sys.mjs   - Persistent server storage
|   +-- tests/xpcshell/             - Comprehensive test suite
```

## Test Coverage

All core modules have xpcshell tests:
- `test_MCPServerManager.js` - Server lifecycle, concurrent operations
- `test_MCPHttpTransport.js` - HTTP requests, retry logic, auth
- `test_MCPSandboxTransport.js` - Sandbox isolation, message passing
- `test_MCPToolRegistry.js` - Tool discovery, namespacing
- `test_HarborServerStore.js` - Persistence, validation

## Debugging

Harbor instance is available globally as `window.harbor`:

```javascript
// In Browser Console at chrome://browser/content/aiwindow/harbor.html
harbor.manager          // MCPServerManager instance
harbor.registry         // MCPToolRegistry instance
harbor.selectedTool     // Currently selected tool
harbor.renderServers()  // Refresh server list
harbor.renderTools()    // Refresh tool list
harbor.executionLog     // Recent tool executions
harbor.consoleLog       // Sandbox console output
```

## Contributing

To add new features to Harbor:

1. Edit the relevant files in `browser/components/aiwindow/`
2. Run `./mach build`
3. Refresh the Harbor page in Firefox
4. Test your changes

No need to restart Firefox - just refresh the page!
