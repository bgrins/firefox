/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * Harbor - MCP Development Interface
 *
 * A development UI for testing and managing MCP servers and tools.
 */

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  MCPServerManager:
    "moz-src:///browser/components/aiwindow/services/mcp/MCPServerManager.sys.mjs",
  MCPToolRegistry:
    "moz-src:///browser/components/aiwindow/services/mcp/MCPToolRegistry.sys.mjs",
  HarborServerStore:
    "moz-src:///browser/components/aiwindow/services/mcp/HarborServerStore.sys.mjs",
  HarborCredentialStore:
    "moz-src:///browser/components/aiwindow/services/mcp/HarborCredentialStore.sys.mjs",
  HarborUtils:
    "moz-src:///browser/components/aiwindow/services/mcp/HarborUtils.sys.mjs",
  CapabilityProfileStore:
    "moz-src:///browser/components/aiwindow/services/mcp/CapabilityProfileStore.sys.mjs",
  HarborBuiltinServers:
    "moz-src:///browser/components/aiwindow/services/mcp/HarborBuiltinServers.sys.mjs",
  Chat: "moz-src:///browser/components/aiwindow/models/Chat.sys.mjs",
  ChatConversation:
    "moz-src:///browser/components/aiwindow/ui/modules/ChatConversation.sys.mjs",
  AddonManager: "resource://gre/modules/AddonManager.sys.mjs",
});

/**
 *
 */
class HarborUI {
  constructor() {
    this.manager = null;
    this.registry = null;
    this.selectedTool = null;
    this.chatMessages = [];
    this.editingServerId = null;
    this.executionLog = [];
    this.consoleLog = [];
    this.maxLogEntries = 50;
    this.pendingToolCalls = new Map(); // Track timing for chat tool calls
  }

  async init() {
    this.setupOllamaPrefs();

    try {
      this.manager = new lazy.MCPServerManager();
      this.registry = new lazy.MCPToolRegistry(this.manager);
    } catch (error) {
      console.error("[Harbor] Failed to initialize MCP:", error);
      this.showError("Failed to initialize MCP infrastructure");
      return;
    }

    this.setupEventHandlers();
    await this.loadServersFromStore();

    this.renderServers();
    this.renderTools();
    this.updateStatus();
    this.updateModelInfo();
  }

  updateModelInfo() {
    const endpointEl = document.getElementById("model-endpoint");
    const modelSelector = document.getElementById("model-selector");
    const statusEl = document.getElementById("model-status");

    try {
      const endpoint = Services.prefs.getStringPref(
        "browser.aiwindow.endpoint",
        ""
      );

      endpointEl.textContent = endpoint || "-";
      endpointEl.title = endpoint;

      if (endpoint) {
        this.checkModelStatus(endpoint, statusEl, modelSelector);
      } else {
        statusEl.textContent = "Not configured";
        statusEl.className = "model-info-value status-error";
        modelSelector.innerHTML = '<option value="">No endpoint</option>';
      }
    } catch (error) {
      console.warn("[Harbor] Failed to read model prefs:", error);
      endpointEl.textContent = "-";
      statusEl.textContent = "Error reading prefs";
      statusEl.className = "model-info-value status-error";
    }
  }

  async checkModelStatus(endpoint, statusEl, modelSelector) {
    statusEl.textContent = "Checking...";
    statusEl.className = "model-info-value";
    modelSelector.innerHTML = '<option value="">Loading...</option>';
    modelSelector.disabled = true;

    const result = await lazy.HarborUtils.checkEndpointStatus(endpoint);

    switch (result.status) {
      case "connected":
        if (result.modelCount !== undefined) {
          statusEl.textContent = `Connected (${result.modelCount} models)`;
        } else {
          statusEl.textContent = "Connected";
        }
        statusEl.className = "model-info-value status-ok";

        this.populateModelSelector(modelSelector, result.models || []);
        break;
      case "timeout":
        statusEl.textContent = "Timeout";
        statusEl.className = "model-info-value status-error";
        modelSelector.innerHTML = '<option value="">Timeout</option>';
        break;
      default:
        statusEl.textContent = "Offline";
        statusEl.className = "model-info-value status-error";
        modelSelector.innerHTML = '<option value="">Offline</option>';
    }
  }

  populateModelSelector(selector, models) {
    const currentModel = Services.prefs.getStringPref(
      "browser.aiwindow.model",
      ""
    );

    selector.innerHTML = "";

    if (models.length === 0) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "No models available";
      selector.appendChild(option);
      selector.disabled = true;
      return;
    }

    for (const model of models) {
      const option = document.createElement("option");
      option.value = model;
      option.textContent = model;
      if (model === currentModel) {
        option.selected = true;
      }
      selector.appendChild(option);
    }

    if (currentModel && !models.includes(currentModel)) {
      const option = document.createElement("option");
      option.value = currentModel;
      option.textContent = `${currentModel} (not found)`;
      option.selected = true;
      selector.insertBefore(option, selector.firstChild);
    }

    selector.disabled = false;
  }

  onModelSelected(event) {
    const model = event.target.value;
    if (model) {
      Services.prefs.setStringPref("browser.aiwindow.model", model);
    }
  }

  async loadServersFromStore() {
    const disabledServers = this.getDisabledServers();

    for (const builtin of lazy.HarborBuiltinServers.BUILTIN_SERVERS) {
      if (disabledServers.includes(builtin.id)) {
        continue;
      }

      try {
        const config =
          lazy.HarborBuiltinServers.getBuiltinServerConfig(builtin);
        await this.registerServerFromConfig(config);

        if (builtin.capabilityLevel) {
          const profile = lazy.CapabilityProfileStore.getDefaultProfile(
            builtin.capabilityLevel
          );
          if (profile) {
            lazy.CapabilityProfileStore.save(builtin.id, profile);
          }
        }
      } catch (error) {
        console.error(
          `[Harbor] Failed to register builtin server ${builtin.id}:`,
          error
        );
      }
    }

    const userServers = lazy.HarborServerStore.loadServers();
    for (const config of userServers) {
      if (disabledServers.includes(config.id)) {
        continue;
      }

      if (config.enabled) {
        try {
          await this.registerServerFromConfig(config);
        } catch (error) {
          console.error(
            `[Harbor] Failed to register server ${config.id}:`,
            error
          );
        }
      }
    }
  }

  getAllServers() {
    const builtinConfigs = lazy.HarborBuiltinServers.BUILTIN_SERVERS.map(b =>
      lazy.HarborBuiltinServers.getBuiltinServerConfig(b)
    );
    const userServers = lazy.HarborServerStore.loadServers();
    return [...builtinConfigs, ...userServers];
  }

  getDisabledServers() {
    try {
      const pref = Services.prefs.getStringPref(
        "browser.aiwindow.harbor.disabled",
        "[]"
      );
      return JSON.parse(pref);
    } catch {
      return [];
    }
  }

  setDisabledServers(disabledIds) {
    Services.prefs.setStringPref(
      "browser.aiwindow.harbor.disabled",
      JSON.stringify(disabledIds)
    );
  }

  isServerDisabled(serverId) {
    return this.getDisabledServers().includes(serverId);
  }

  async toggleServerEnabled(serverId) {
    const disabled = this.getDisabledServers();
    const isCurrentlyDisabled = disabled.includes(serverId);

    if (isCurrentlyDisabled) {
      this.setDisabledServers(disabled.filter(id => id !== serverId));
      const allServers = this.getAllServers();
      const config = allServers.find(s => s.id === serverId);
      if (config) {
        try {
          await this.registerServerFromConfig(config);
        } catch (error) {
          console.error(`[Harbor] Failed to start server ${serverId}:`, error);
        }
      }
    } else {
      this.setDisabledServers([...disabled, serverId]);
      if (this.manager.servers.has(serverId)) {
        try {
          await this.manager.unregisterServer(serverId);
          this.registry.unregisterServerTools(serverId);
        } catch (error) {
          console.error(`[Harbor] Failed to stop server ${serverId}:`, error);
        }
      }
    }

    this.renderServers();
    this.renderTools();
  }

  async registerServerFromConfig(config) {
    const onConsole = (level, args) => {
      this.addConsoleEntry(config.id, level, args);
    };

    if (config.type === "sandbox" && config.code) {
      await this.manager.registerServer({
        id: config.id,
        type: "sandbox",
        code: config.code,
        enabled: config.enabled,
        onConsole,
      });

      const serverStatus = this.manager.getServerStatus(config.id);
      if (serverStatus === "running") {
        await this.registry.refreshServerTools(config.id);
      } else {
        console.warn(
          `[Harbor] Server not running: ${config.name} (status: ${serverStatus})`
        );
      }
    } else if (config.type === "http" && config.url) {
      const httpConfig = {
        id: config.id,
        type: "http",
        url: config.url,
        enabled: config.enabled,
      };
      if (config.hasBearerToken) {
        const bearerToken = lazy.HarborCredentialStore.getBearerToken(
          config.id
        );
        if (bearerToken) {
          httpConfig.options = { bearerToken };
        }
      }
      await this.manager.registerServer(httpConfig);

      const serverStatus = this.manager.getServerStatus(config.id);
      if (serverStatus === "running") {
        await this.registry.refreshServerTools(config.id);
      } else {
        console.warn(
          `[Harbor] HTTP server not running: ${config.name} (status: ${serverStatus})`
        );
      }
    } else if (config.type === "extension" && config.extensionId) {
      // Install extension if it has a path
      if (config.extensionPath) {
        await this.installExtensionServer(config);
      }

      // Register with manager
      await this.manager.registerServer({
        id: config.id,
        type: "extension",
        extensionId: config.extensionId,
        enabled: config.enabled,
      });

      const serverStatus = this.manager.getServerStatus(config.id);
      if (serverStatus === "running") {
        await this.registry.refreshServerTools(config.id);
      } else {
        console.warn(
          `[Harbor] Extension server not running: ${config.name} (status: ${serverStatus})`
        );
      }
    }
  }

  /**
   * Install an extension-based MCP server.
   *
   * @param config
   */
  async installExtensionServer(config) {
    try {
      // Check if already installed
      const existing = await lazy.AddonManager.getAddonByID(config.extensionId);
      if (existing) {
        return existing;
      }

      let extensionDir;
      const extPath = config.extensionPath;

      if (extPath.startsWith("/")) {
        // Absolute file path
        extensionDir = Cc["@mozilla.org/file/local;1"].createInstance(
          Ci.nsIFile
        );
        extensionDir.initWithPath(extPath);
      } else if (
        extPath.startsWith("browser/") ||
        extPath.startsWith("toolkit/")
      ) {
        // Relative source tree path like "browser/components/aiwindow/extensions/time-server-mcp"
        // Resolve relative to source root
        // GreD is .../objdir/dist/Nightly.app/Contents/Resources (macOS)
        // or .../objdir/dist/bin (Linux)
        const greDir = Services.dirsvc.get("GreD", Ci.nsIFile);
        let sourceDir = greDir;

        // Navigate up to find the source root (where mach lives)
        // Keep going up until we find a directory containing "mach" or hit root
        for (let i = 0; i < 10 && sourceDir.parent; i++) {
          sourceDir = sourceDir.parent;
          const machFile = sourceDir.clone();
          machFile.append("mach");
          if (machFile.exists()) {
            break;
          }
        }

        extensionDir = sourceDir.clone();
        for (const part of extPath.split("/")) {
          extensionDir.append(part);
        }
      } else {
        throw new Error(
          `Invalid extension path format: "${extPath}". ` +
            `Expected absolute path (starting with /) or relative source path (starting with browser/ or toolkit/).`
        );
      }

      if (!extensionDir || !extensionDir.exists()) {
        throw new Error(
          `Extension directory not found: ${extPath} (resolved to: ${extensionDir?.path || "null"})`
        );
      }

      const addon = await lazy.AddonManager.installTemporaryAddon(extensionDir);
      return addon;
    } catch (error) {
      console.error(
        `[Harbor] Failed to install extension from path "${config.extensionPath}":`,
        error
      );
      throw error;
    }
  }

  /**
   * Uninstall an extension-based MCP server.
   *
   * @param extensionId
   */
  async uninstallExtensionServer(extensionId) {
    try {
      const addon = await lazy.AddonManager.getAddonByID(extensionId);
      if (addon) {
        await addon.uninstall();
        console.log(`[Harbor] Uninstalled extension: ${extensionId}`);
      }
    } catch (error) {
      console.error(`[Harbor] Failed to uninstall extension:`, error);
    }
  }

  setupOllamaPrefs() {
    const defaults = {
      "browser.aiwindow.enabled": true,
      "browser.aiwindow.endpoint": "http://localhost:11434/v1",
      "browser.aiwindow.model": "functiongemma",
      "browser.aiwindow.apiKey": "ollama",
      "browser.ml.logLevel": "All",
      "browser.aiwindow.firstrun.hasCompleted": true,
    };

    for (const [pref, value] of Object.entries(defaults)) {
      try {
        if (typeof value === "boolean") {
          if (!Services.prefs.prefHasUserValue(pref)) {
            Services.prefs.setBoolPref(pref, value);
          }
        } else if (!Services.prefs.prefHasUserValue(pref)) {
          Services.prefs.setStringPref(pref, value);
        }
      } catch (e) {
        console.warn(`[Harbor] Could not set pref ${pref}:`, e);
      }
    }
  }

  setupEventHandlers() {
    // Send button
    document.getElementById("send-btn").addEventListener("click", () => {
      this.sendMessage();
    });

    // Model selector
    document
      .getElementById("model-selector")
      .addEventListener("change", e => this.onModelSelected(e));

    // Enter key in textarea (Ctrl+Enter or Enter without shift)
    document.getElementById("chat-input").addEventListener("keydown", e => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey || !e.shiftKey)) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Escape key to close dialog
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") {
        const dialog = document.getElementById("server-editor-dialog");
        if (dialog.open) {
          dialog.close();
        }
      }
    });

    // Add server button
    document.getElementById("add-server-btn").addEventListener("click", () => {
      this.openServerDialog();
    });

    // Dialog event handlers
    const dialog = document.getElementById("server-editor-dialog");
    const form = document.getElementById("server-editor-form");
    const typeSelect = document.getElementById("server-type");

    // Toggle code/URL fields based on type
    typeSelect.addEventListener("change", () => {
      const isSandbox = typeSelect.value === "sandbox";
      document
        .getElementById("code-field")
        .classList.toggle("hidden", !isSandbox);
      document
        .getElementById("url-field")
        .classList.toggle("hidden", isSandbox);
      document
        .getElementById("template-field")
        .classList.toggle("hidden", !isSandbox);
      document
        .getElementById("token-field")
        .classList.toggle("hidden", isSandbox);
      document
        .getElementById("http-actions")
        .classList.toggle("hidden", isSandbox);
      // Clear connection status when switching types
      const statusEl = document.getElementById("connection-status");
      statusEl.textContent = "";
      statusEl.className = "connection-status";
    });

    // Test connection button
    document
      .getElementById("test-connection-btn")
      .addEventListener("click", () => {
        this.testHttpConnection();
      });

    // Template selection
    document.getElementById("server-template").addEventListener("change", e => {
      const templateCode = lazy.HarborBuiltinServers.getTemplateCode(
        e.target.value
      );
      if (templateCode) {
        document.getElementById("server-code").value = templateCode;
        this.updateCodeHighlight(templateCode);

        // Auto-set capability level based on template
        const capLevel = document.getElementById("capability-level");
        const templateCapLevels = {
          "browser-tabs": "browser-readonly",
          "history-search": "browser-readonly",
          "file-reader": "workspace",
          clipboard: "workspace",
        };
        const level = templateCapLevels[e.target.value];
        if (level) {
          capLevel.value = level;
          this.updateCapabilityDisplay(level);
        }
      }
    });

    // Form submit
    form.addEventListener("submit", e => {
      e.preventDefault();
      this.saveServer();
    });

    // Cancel button
    document
      .getElementById("dialog-cancel-btn")
      .addEventListener("click", () => {
        dialog.close();
      });

    // Delete button
    document
      .getElementById("dialog-delete-btn")
      .addEventListener("click", () => {
        if (this.editingServerId) {
          this.deleteServer(this.editingServerId);
        }
      });

    // Close dialog when clicking backdrop
    dialog.addEventListener("click", e => {
      if (e.target === dialog) {
        dialog.close();
      }
    });

    // Tab key handling and syntax highlighting in code textarea
    const codeTextarea = document.getElementById("server-code");
    codeTextarea.addEventListener("keydown", e => {
      if (e.key === "Tab") {
        e.preventDefault();
        const textarea = e.target;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        textarea.value =
          textarea.value.substring(0, start) +
          "  " +
          textarea.value.substring(end);
        textarea.selectionStart = textarea.selectionEnd = start + 2;
        this.updateCodeHighlight(textarea.value);
      }
    });

    // Update highlighting on input
    codeTextarea.addEventListener("input", e => {
      this.updateCodeHighlight(e.target.value);
    });

    // Sync scroll between textarea and highlight
    codeTextarea.addEventListener("scroll", e => {
      const highlight = document.getElementById("code-highlight");
      highlight.scrollTop = e.target.scrollTop;
      highlight.scrollLeft = e.target.scrollLeft;
    });

    // Clear log button
    document.getElementById("clear-log-btn").addEventListener("click", () => {
      this.clearExecutionLog();
    });

    // Clear console button
    document
      .getElementById("clear-console-btn")
      .addEventListener("click", () => {
        this.clearConsoleLog();
      });

    // Import/Export buttons
    document.getElementById("export-btn").addEventListener("click", () => {
      this.exportServers();
    });

    document.getElementById("import-btn").addEventListener("click", () => {
      document.getElementById("import-file-input").click();
    });

    document
      .getElementById("import-file-input")
      .addEventListener("change", e => {
        this.importServers(e);
      });

    document.getElementById("reset-btn").addEventListener("click", () => {
      this.resetToDefaults();
    });

    // Capability level selector
    document
      .getElementById("capability-level")
      .addEventListener("change", e => {
        this.updateCapabilityDisplay(e.target.value);
      });
  }

  updateCapabilityDisplay(level) {
    const descEl = document.getElementById("capability-level-description");
    const systemSummary = document.getElementById("cap-system-summary");
    const browserSummary = document.getElementById("cap-browser-summary");

    const descriptions = {
      isolated: "No system or browser access. Safe for pure computation.",
      "browser-readonly":
        "Read-only browser access. Can list tabs, search history and bookmarks.",
      "browser-full":
        "Full browser access except cookies and script injection. Good for browser automation.",
      workspace:
        "Filesystem access to a project directory. Good for code editing tasks.",
      developer:
        "Full filesystem, subprocess, and browser read access. For development environments.",
    };

    const systemCaps = {
      isolated: "None",
      "browser-readonly": "None",
      "browser-full": "Notifications",
      workspace: "Filesystem, Clipboard, Notifications",
      developer: "Filesystem, Network, Subprocess, Clipboard, Notifications",
    };

    const browserCaps = {
      isolated: "None",
      "browser-readonly":
        "Tabs (read), History (read), Bookmarks (read), Downloads (read)",
      "browser-full":
        "Tabs, History, Bookmarks, Downloads, Storage, ActiveTab content",
      workspace: "None",
      developer:
        "Tabs (read, create), History (read), Bookmarks (read), Downloads (read, initiate), ActiveTab content",
    };

    descEl.textContent = descriptions[level] || "";
    systemSummary.textContent = systemCaps[level] || "None";
    browserSummary.textContent = browserCaps[level] || "None";
  }

  async sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) {
      return;
    }

    input.value = "";
    this.addChatMessage("user", message);

    this.addChatMessage("assistant", "");
    const assistantMsgDiv = document.querySelector(
      `#chat-messages .chat-message:last-child .message-content`
    );

    try {
      const mcpTools = this.registry.listAllTools();
      const mcpToolsConfig = mcpTools.map(tool => ({
        type: "function",
        function: {
          name: tool.name,
          description: tool.description || "",
          parameters: tool.inputSchema || { type: "object", properties: {} },
        },
      }));

      lazy.Chat._mcpServerManager = this.manager;
      lazy.Chat._mcpToolRegistry = this.registry;
      lazy.Chat._mcpInitialized = true;

      const conversation = new lazy.ChatConversation({
        title: "Harbor Test",
        description: "MCP Tool Testing",
        pageUrl: "",
        pageMeta: {},
      });

      const systemPrompt = this.getHarborSystemPrompt(mcpTools);
      conversation.addSystemMessage("text", systemPrompt);
      conversation.addUserMessage(message);

      this.lastRequest = {
        systemPrompt,
        userMessage: message,
        tools: mcpToolsConfig,
        messages: conversation.getMessagesInOpenAiFormat(),
      };

      let assistantText = "";

      for await (const chunk of lazy.Chat.fetchWithHistory(conversation, {
        tools: mcpToolsConfig,
        toolMap: {},
      })) {
        // Check for error status in chunk
        if (chunk?.ok === false) {
          throw chunk;
        }
        if (typeof chunk === "string") {
          assistantText += chunk;
          assistantMsgDiv.textContent = assistantText;
        } else if (chunk?.type === "tool_call") {
          this.pendingToolCalls.set(chunk.name, Date.now());
          this.addToolCallMessage(chunk.name, chunk.arguments);
        } else if (chunk?.type === "tool_result") {
          const startTime = this.pendingToolCalls.get(chunk.name) || Date.now();
          const duration = Date.now() - startTime;
          this.pendingToolCalls.delete(chunk.name);

          this.addToolResultMessage(chunk.name, chunk.result, chunk.error);

          this.logExecution({
            tool: chunk.name,
            args: {},
            result:
              typeof chunk.result === "string"
                ? chunk.result
                : JSON.stringify(chunk.result),
            error: chunk.error ? chunk.result : null,
            duration,
            success: !chunk.error,
          });
        }
      }

      if (!assistantText) {
        assistantMsgDiv.textContent = "No response from model";
      }
    } catch (error) {
      console.error("[Harbor] Chat error:", error);
      const errorMsg = this.extractErrorMessage(error);
      assistantMsgDiv.textContent = `Error: ${errorMsg}`;
      assistantMsgDiv.parentElement.classList.add("error");
    }
  }

  extractErrorMessage(error) {
    if (!error) {
      return "Unknown error";
    }
    // Standard Error object
    if (error.message) {
      return error.message;
    }
    // BackendError with backendError property
    if (error.backendError?.message) {
      return error.backendError.message;
    }
    // Nested error object
    if (error.error?.message) {
      return error.error.message;
    }
    // Response object from Chat API with metadata containing error
    if (error.metadata?.error) {
      return error.metadata.error;
    }
    // Object with statusText that isn't just "done"
    if (error.statusText && error.statusText !== "done") {
      return error.statusText;
    }
    // Progress status object without error info - provide contextual message
    if (error.ok === false && error.type === "running_inference") {
      return "Model inference failed. The model may not support the requested features (e.g., tool calling).";
    }
    // Try to extract from string representation
    if (typeof error === "string") {
      return error;
    }
    // Last resort: stringify the object (but make it readable)
    try {
      const str = JSON.stringify(error);
      return str.length > 200 ? str.substring(0, 200) + "..." : str;
    } catch {
      return "Unknown error";
    }
  }

  getHarborSystemPrompt(mcpTools) {
    const toolNames = mcpTools.map(t => t.name).join(", ");
    return `You are a helpful assistant in a tool testing environment called Harbor.
You have access to MCP (Model Context Protocol) tools that you can call when relevant to the user's request.
Only call tools when the user's request specifically requires them. Do not call tools speculatively.

Available tools: ${toolNames || "none"}

When responding:
- Be concise and helpful
- Only use tools when the user explicitly needs their functionality
- Explain what you did if you called a tool`;
  }

  addChatMessage(role, content) {
    const messagesDiv = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message ${role}`;

    const headerDiv = document.createElement("div");
    headerDiv.className = "message-header";

    const roleDiv = document.createElement("div");
    roleDiv.className = "message-role";
    roleDiv.textContent = role;
    headerDiv.appendChild(roleDiv);

    // Add "Show Request" button for assistant messages
    if (role === "assistant") {
      const showRequestBtn = document.createElement("button");
      showRequestBtn.className = "show-request-btn";
      showRequestBtn.textContent = "Show Request";
      showRequestBtn.addEventListener("click", e => {
        e.stopPropagation();
        this.showLastRequest();
      });
      headerDiv.appendChild(showRequestBtn);
    }

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.textContent = content;

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return messageDiv;
  }

  showLastRequest() {
    if (!this.lastRequest) {
      // eslint-disable-next-line no-alert
      alert("No request data available");
      return;
    }

    const formatted = JSON.stringify(this.lastRequest, null, 2);

    // Show in a simple dialog using DOM methods
    const dialog = document.createElement("dialog");
    dialog.className = "request-debug-dialog";

    const h3 = document.createElement("h3");
    h3.textContent = "Last Request";
    dialog.appendChild(h3);

    const pre = document.createElement("pre");
    pre.textContent = formatted;
    dialog.appendChild(pre);

    const button = document.createElement("button");
    button.className = "primary";
    button.textContent = "Close";
    button.addEventListener("click", () => {
      dialog.close();
      dialog.remove();
    });
    dialog.appendChild(button);

    document.body.appendChild(dialog);
    dialog.showModal();
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  addToolCallMessage(toolName, args) {
    const messagesDiv = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = "chat-message tool-call";

    const roleDiv = document.createElement("div");
    roleDiv.className = "message-role";
    roleDiv.textContent = "Tool Call";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const headerDiv = document.createElement("div");
    headerDiv.className = "tool-call-header";

    const toolNameSpan = document.createElement("strong");
    toolNameSpan.textContent = toolName;
    headerDiv.appendChild(toolNameSpan);

    const toggleSpan = document.createElement("span");
    toggleSpan.className = "tool-call-toggle";
    headerDiv.appendChild(toggleSpan);

    contentDiv.appendChild(headerDiv);

    let argsDiv = null;
    const hasArgs = args && args !== "{}";

    if (hasArgs) {
      argsDiv = document.createElement("div");
      argsDiv.className = "tool-args collapsed";
      try {
        const parsedArgs = JSON.parse(args);
        argsDiv.textContent = JSON.stringify(parsedArgs, null, 2);
      } catch {
        argsDiv.textContent = args;
      }
      contentDiv.appendChild(argsDiv);
      toggleSpan.textContent = "[+] Click to expand";
    } else {
      toggleSpan.textContent = "No arguments";
    }

    messageDiv.appendChild(roleDiv);
    messageDiv.appendChild(contentDiv);

    // Add click handler after appending to enable toggle
    if (hasArgs && argsDiv) {
      messageDiv.addEventListener("click", () => {
        const isCollapsed = argsDiv.classList.contains("collapsed");
        if (isCollapsed) {
          argsDiv.classList.remove("collapsed");
          toggleSpan.textContent = "[-] Click to collapse";
        } else {
          argsDiv.classList.add("collapsed");
          toggleSpan.textContent = "[+] Click to expand";
        }
      });
    }

    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return messageDiv;
  }

  addToolResultMessage(toolName, result, isError = false) {
    const messagesDiv = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message tool-result ${isError ? "error" : ""}`;

    const roleDiv = document.createElement("div");
    roleDiv.className = "message-role";
    roleDiv.textContent = isError ? "Tool Error" : "Tool Result";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const toolNameSpan = document.createElement("strong");
    toolNameSpan.textContent = toolName;
    contentDiv.appendChild(toolNameSpan);

    const resultDiv = document.createElement("div");
    resultDiv.className = "tool-result-content";
    resultDiv.textContent =
      typeof result === "string" ? result : JSON.stringify(result, null, 2);
    contentDiv.appendChild(resultDiv);

    messageDiv.appendChild(roleDiv);
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return messageDiv;
  }

  renderServers() {
    const serverList = document.getElementById("server-list");
    serverList.innerHTML = "";

    const allServers = this.getAllServers();

    for (const config of allServers) {
      const isDisabled = this.isServerDisabled(config.id);

      const serverDiv = document.createElement("div");
      serverDiv.className = "server-item" + (isDisabled ? " disabled" : "");
      serverDiv.setAttribute("role", "listitem");

      const headerDiv = document.createElement("div");
      headerDiv.className = "server-item-header";

      const nameSpan = document.createElement("span");
      nameSpan.className = "server-name";
      nameSpan.textContent = config.name;

      const badgesDiv = document.createElement("div");
      badgesDiv.className = "server-badges";

      const typeBadge = document.createElement("span");
      typeBadge.className = `server-type-badge type-${config.type}`;
      typeBadge.textContent = config.type;

      let serverStatus;
      if (isDisabled) {
        serverStatus = "disabled";
      } else {
        const runtimeServer = this.manager.servers.get(config.id);
        serverStatus = runtimeServer ? runtimeServer.status : "stopped";
      }

      const statusSpan = document.createElement("span");
      statusSpan.className = `server-status ${serverStatus.toLowerCase()}`;
      statusSpan.textContent = serverStatus;

      badgesDiv.appendChild(typeBadge);
      badgesDiv.appendChild(statusSpan);

      // Show builtin badge for builtin servers
      if (config.builtin) {
        const builtinBadge = document.createElement("span");
        builtinBadge.className = "server-type-badge type-builtin";
        builtinBadge.textContent = "builtin";
        badgesDiv.appendChild(builtinBadge);
      }

      // Row 1: checkbox + name
      const nameRow = document.createElement("div");
      nameRow.className = "server-name-row";

      const enableCheckbox = document.createElement("input");
      enableCheckbox.type = "checkbox";
      enableCheckbox.className = "server-enable-checkbox";
      enableCheckbox.checked = !isDisabled;
      enableCheckbox.title = isDisabled ? "Enable server" : "Disable server";
      enableCheckbox.addEventListener("click", e => {
        e.stopPropagation();
      });
      enableCheckbox.addEventListener("change", async e => {
        e.stopPropagation();
        await this.toggleServerEnabled(config.id);
      });

      nameRow.appendChild(enableCheckbox);
      nameRow.appendChild(nameSpan);
      headerDiv.appendChild(nameRow);

      // Row 2: badges
      headerDiv.appendChild(badgesDiv);
      serverDiv.appendChild(headerDiv);

      // Click on server to open editor (readonly for builtins)
      serverDiv.addEventListener("click", () => {
        this.openServerDialog(config.id, { readonly: config.builtin });
      });

      serverList.appendChild(serverDiv);
    }
  }

  renderTools() {
    const toolList = document.getElementById("tool-list");
    toolList.innerHTML = "";

    const tools = this.registry.listAllTools();

    for (const tool of tools) {
      const toolDiv = document.createElement("div");
      toolDiv.className = "tool-item";
      toolDiv.setAttribute("role", "listitem");
      toolDiv.setAttribute("tabindex", "0");
      toolDiv.setAttribute("aria-label", `${tool.name} from ${tool.serverId}`);

      const nameDiv = document.createElement("div");
      nameDiv.className = "tool-item-name";
      nameDiv.textContent = tool.name;

      const serverDiv = document.createElement("div");
      serverDiv.className = "tool-item-server";
      serverDiv.textContent = tool.serverId;

      toolDiv.appendChild(nameDiv);
      toolDiv.appendChild(serverDiv);

      toolDiv.addEventListener("click", e => {
        this.selectTool(tool, e);
      });

      // Allow keyboard selection with Enter or Space
      toolDiv.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          this.selectTool(tool, e);
        }
      });

      toolList.appendChild(toolDiv);
    }
  }

  selectTool(tool, event) {
    this.selectedTool = tool;

    // Update selected state in UI
    document.querySelectorAll(".tool-item").forEach(item => {
      item.classList.remove("selected");
    });
    if (event?.currentTarget) {
      event.currentTarget.classList.add("selected");
    }

    // Render tool details
    this.renderToolDetails();
  }

  renderToolDetails() {
    const detailsDiv = document.getElementById("selected-tool-details");
    if (!this.selectedTool) {
      detailsDiv.innerHTML = "<p>Select a tool to view details</p>";
      return;
    }

    const tool = this.selectedTool;

    // Build info section using DOM APIs to prevent XSS
    detailsDiv.innerHTML = "";

    const createSection = (label, value) => {
      const section = document.createElement("div");
      section.className = "tool-detail-section";
      const labelDiv = document.createElement("div");
      labelDiv.className = "tool-detail-label";
      labelDiv.textContent = label;
      const valueDiv = document.createElement("div");
      valueDiv.textContent = value;
      section.appendChild(labelDiv);
      section.appendChild(valueDiv);
      return section;
    };

    detailsDiv.appendChild(createSection("Name", tool.name));
    detailsDiv.appendChild(createSection("Server", tool.serverId));
    detailsDiv.appendChild(
      createSection("Description", tool.description || "No description")
    );

    // Build arguments form using DOM APIs to prevent XSS
    const schema = tool.inputSchema || {};
    const properties = schema.properties || {};
    const required = schema.required || [];

    const testSection = document.createElement("div");
    testSection.className = "tool-detail-section";
    const testLabel = document.createElement("div");
    testLabel.className = "tool-detail-label";
    testLabel.textContent = "Test Tool";
    testSection.appendChild(testLabel);

    const form = document.createElement("form");
    form.id = "tool-test-form";
    form.className = "tool-test-form";

    const propNames = Object.keys(properties);
    if (propNames.length) {
      for (const propName of propNames) {
        const prop = properties[propName];
        const isRequired = required.includes(propName);
        const inputType = prop.type === "number" ? "number" : "text";

        const fieldDiv = document.createElement("div");
        fieldDiv.className = "tool-arg-field";

        const label = document.createElement("label");
        label.htmlFor = `arg-${propName}`;
        label.textContent = `${propName}${isRequired ? " *" : ""} `;
        const typeSpan = document.createElement("span");
        typeSpan.className = "arg-type";
        typeSpan.textContent = `(${prop.type || "string"})`;
        label.appendChild(typeSpan);

        const input = document.createElement("input");
        input.type = inputType;
        input.id = `arg-${propName}`;
        input.name = propName;
        input.placeholder = prop.description || "";
        if (isRequired) {
          input.required = true;
        }

        fieldDiv.appendChild(label);
        fieldDiv.appendChild(input);
        form.appendChild(fieldDiv);
      }
    } else {
      const noArgs = document.createElement("div");
      noArgs.className = "no-args";
      noArgs.textContent = "No arguments required";
      form.appendChild(noArgs);
    }

    const submitBtn = document.createElement("button");
    submitBtn.type = "submit";
    submitBtn.className = "primary execute-btn";
    submitBtn.textContent = "Execute Tool";
    form.appendChild(submitBtn);

    testSection.appendChild(form);
    detailsDiv.appendChild(testSection);

    // Result display area
    const resultSection = document.createElement("div");
    resultSection.className = "tool-detail-section";
    const resultLabel = document.createElement("div");
    resultLabel.className = "tool-detail-label";
    resultLabel.textContent = "Result";
    const resultDiv = document.createElement("div");
    resultDiv.id = "tool-result";
    resultDiv.className = "tool-result";
    const resultPlaceholder = document.createElement("span");
    resultPlaceholder.className = "result-placeholder";
    resultPlaceholder.textContent = "Click Execute to test the tool";
    resultDiv.appendChild(resultPlaceholder);
    resultSection.appendChild(resultLabel);
    resultSection.appendChild(resultDiv);
    detailsDiv.appendChild(resultSection);

    // Schema section
    const schemaSection = document.createElement("div");
    schemaSection.className = "tool-detail-section";
    const schemaLabel = document.createElement("div");
    schemaLabel.className = "tool-detail-label";
    schemaLabel.textContent = "Input Schema";
    const schemaDiv = document.createElement("div");
    schemaDiv.className = "tool-schema";
    schemaDiv.textContent = JSON.stringify(schema, null, 2);
    schemaSection.appendChild(schemaLabel);
    schemaSection.appendChild(schemaDiv);
    detailsDiv.appendChild(schemaSection);

    // Add form submit handler
    form.addEventListener("submit", e => {
      e.preventDefault();
      this.executeSelectedTool();
    });
  }

  async executeSelectedTool() {
    if (!this.selectedTool) {
      return;
    }

    const resultDiv = document.getElementById("tool-result");
    resultDiv.innerHTML = '<span class="result-loading">Executing...</span>';

    const form = document.getElementById("tool-test-form");
    const formData = new FormData(form);

    // Build arguments object
    const args = {};
    const schema = this.selectedTool.inputSchema || {};
    const properties = schema.properties || {};

    for (const [key, value] of formData.entries()) {
      if (value === "") {
        continue;
      }

      // Convert to appropriate type
      const propType = properties[key]?.type;
      if (propType === "number") {
        args[key] = Number(value);
      } else if (propType === "boolean") {
        args[key] = value === "true";
      } else {
        args[key] = value;
      }
    }

    const startTime = Date.now();

    try {
      const result = await this.registry.callTool(
        this.selectedTool.fullyQualifiedName,
        args
      );

      const duration = Date.now() - startTime;

      let resultText;
      if (result?.content?.[0]?.text) {
        resultText = result.content[0].text;
      } else {
        resultText = JSON.stringify(result, null, 2);
      }

      resultDiv.textContent = "";
      const successPre = document.createElement("pre");
      successPre.className = "result-success";
      successPre.textContent = resultText;
      resultDiv.appendChild(successPre);

      this.logExecution({
        tool: this.selectedTool.fullyQualifiedName,
        args,
        result: resultText,
        duration,
        success: true,
      });
    } catch (error) {
      const duration = Date.now() - startTime;
      console.error("[Harbor] Tool execution failed:", error);
      resultDiv.textContent = "";
      const errorPre = document.createElement("pre");
      errorPre.className = "result-error";
      errorPre.textContent = error.message;
      resultDiv.appendChild(errorPre);

      this.logExecution({
        tool: this.selectedTool.fullyQualifiedName,
        args,
        error: error.message,
        duration,
        success: false,
      });
    }
  }

  logExecution(entry) {
    entry.timestamp = Date.now();
    this.executionLog.unshift(entry);

    // Keep log size bounded
    if (this.executionLog.length > this.maxLogEntries) {
      this.executionLog.pop();
    }

    this.renderExecutionLog();
  }

  renderExecutionLog() {
    const logDiv = document.getElementById("execution-log");
    logDiv.textContent = "";

    if (this.executionLog.length === 0) {
      const placeholder = document.createElement("p");
      placeholder.className = "log-placeholder";
      placeholder.textContent = "Tool executions will appear here";
      logDiv.appendChild(placeholder);
      return;
    }

    for (const entry of this.executionLog) {
      const time = new Date(entry.timestamp).toLocaleTimeString();
      const statusClass = entry.success ? "log-success" : "log-error";
      const statusIcon = entry.success ? "[OK]" : "[FAIL]";
      const toolName = entry.tool.split("/").pop();

      const entryDiv = document.createElement("div");
      entryDiv.className = `log-entry ${statusClass}`;

      const headerDiv = document.createElement("div");
      headerDiv.className = "log-header";

      const iconSpan = document.createElement("span");
      iconSpan.className = "log-icon";
      iconSpan.textContent = statusIcon;

      const toolSpan = document.createElement("span");
      toolSpan.className = "log-tool";
      toolSpan.textContent = toolName;

      const timeSpan = document.createElement("span");
      timeSpan.className = "log-time";
      timeSpan.textContent = time;

      const durationSpan = document.createElement("span");
      durationSpan.className = "log-duration";
      durationSpan.textContent = `${entry.duration}ms`;

      headerDiv.appendChild(iconSpan);
      headerDiv.appendChild(toolSpan);
      headerDiv.appendChild(timeSpan);
      headerDiv.appendChild(durationSpan);

      const detailsDiv = document.createElement("div");
      detailsDiv.className = "log-details";

      const resultDiv = document.createElement("div");
      resultDiv.className = entry.success ? "log-result" : "log-error";
      if (entry.success) {
        const resultText = entry.result || "";
        resultDiv.textContent =
          resultText.length > 100
            ? resultText.substring(0, 100) + "..."
            : resultText;
      } else {
        resultDiv.textContent = entry.error || "Unknown error";
      }
      detailsDiv.appendChild(resultDiv);

      entryDiv.appendChild(headerDiv);
      entryDiv.appendChild(detailsDiv);
      logDiv.appendChild(entryDiv);
    }
  }

  clearExecutionLog() {
    this.executionLog = [];
    this.renderExecutionLog();
  }

  addConsoleEntry(serverId, level, args) {
    const entry = {
      serverId,
      level,
      message: args
        .map(a => (typeof a === "object" ? JSON.stringify(a) : String(a)))
        .join(" "),
      timestamp: Date.now(),
    };

    this.consoleLog.unshift(entry);

    if (this.consoleLog.length > this.maxLogEntries) {
      this.consoleLog.pop();
    }

    this.renderConsoleLog();
  }

  renderConsoleLog() {
    const logDiv = document.getElementById("console-log");
    logDiv.textContent = "";

    if (this.consoleLog.length === 0) {
      const placeholder = document.createElement("p");
      placeholder.className = "log-placeholder";
      placeholder.textContent = "Sandbox console output will appear here";
      logDiv.appendChild(placeholder);
      return;
    }

    for (const entry of this.consoleLog) {
      const time = new Date(entry.timestamp).toLocaleTimeString();

      const entryDiv = document.createElement("div");
      entryDiv.className = `console-entry console-${entry.level}`;

      const serverSpan = document.createElement("span");
      serverSpan.className = "console-server";
      serverSpan.textContent = `[${entry.serverId}]`;

      const messageSpan = document.createElement("span");
      messageSpan.className = "console-message";
      messageSpan.textContent = entry.message;

      const timeSpan = document.createElement("span");
      timeSpan.className = "log-time";
      timeSpan.textContent = time;

      entryDiv.appendChild(serverSpan);
      entryDiv.appendChild(messageSpan);
      entryDiv.appendChild(timeSpan);
      logDiv.appendChild(entryDiv);
    }
  }

  clearConsoleLog() {
    this.consoleLog = [];
    this.renderConsoleLog();
  }

  updateCodeHighlight(code) {
    const highlightEl = document.querySelector("#code-highlight code");
    if (!highlightEl) {
      return;
    }

    // Tokenize and highlight the code (highlightJavaScript escapes all text)
    const highlighted = this.highlightJavaScript(code);
    // eslint-disable-next-line no-unsanitized/property
    highlightEl.innerHTML = highlighted;
  }

  highlightJavaScript(code) {
    if (!code) {
      return "";
    }

    const keywords = new Set([
      "async",
      "await",
      "break",
      "case",
      "catch",
      "class",
      "const",
      "continue",
      "debugger",
      "default",
      "delete",
      "do",
      "else",
      "export",
      "extends",
      "finally",
      "for",
      "function",
      "if",
      "import",
      "in",
      "instanceof",
      "let",
      "new",
      "of",
      "return",
      "static",
      "super",
      "switch",
      "this",
      "throw",
      "try",
      "typeof",
      "var",
      "void",
      "while",
      "with",
      "yield",
    ]);

    const result = [];
    let i = 0;

    while (i < code.length) {
      // Comments
      if (code[i] === "/" && code[i + 1] === "/") {
        let end = code.indexOf("\n", i);
        if (end === -1) {
          end = code.length;
        }
        result.push(
          `<span class="token-comment">${this.escapeHtml(code.slice(i, end))}</span>`
        );
        i = end;
        continue;
      }

      if (code[i] === "/" && code[i + 1] === "*") {
        let end = code.indexOf("*/", i + 2);
        if (end === -1) {
          end = code.length;
        } else {
          end += 2;
        }
        result.push(
          `<span class="token-comment">${this.escapeHtml(code.slice(i, end))}</span>`
        );
        i = end;
        continue;
      }

      // Strings
      if (code[i] === '"' || code[i] === "'" || code[i] === "`") {
        const quote = code[i];
        let end = i + 1;
        while (end < code.length) {
          if (code[end] === "\\") {
            end += 2;
            continue;
          }
          if (code[end] === quote) {
            end++;
            break;
          }
          if (quote === "`" && code[end] === "\n") {
            end++;
            continue;
          }
          end++;
        }
        result.push(
          `<span class="token-string">${this.escapeHtml(code.slice(i, end))}</span>`
        );
        i = end;
        continue;
      }

      // Numbers
      if (/[0-9]/.test(code[i])) {
        let end = i;
        while (end < code.length && /[0-9.xXa-fA-FeEoObB_]/.test(code[end])) {
          end++;
        }
        result.push(
          `<span class="token-number">${this.escapeHtml(code.slice(i, end))}</span>`
        );
        i = end;
        continue;
      }

      // Identifiers and keywords
      if (/[a-zA-Z_$]/.test(code[i])) {
        let end = i;
        while (end < code.length && /[a-zA-Z0-9_$]/.test(code[end])) {
          end++;
        }
        const word = code.slice(i, end);

        if (keywords.has(word)) {
          result.push(
            `<span class="token-keyword">${this.escapeHtml(word)}</span>`
          );
        } else if (word === "true" || word === "false" || word === "null") {
          result.push(
            `<span class="token-boolean">${this.escapeHtml(word)}</span>`
          );
        } else if (code[end] === "(") {
          result.push(
            `<span class="token-function">${this.escapeHtml(word)}</span>`
          );
        } else {
          result.push(this.escapeHtml(word));
        }
        i = end;
        continue;
      }

      // Operators
      if (/[+\-*/%=<>!&|^~?:]/.test(code[i])) {
        result.push(
          `<span class="token-operator">${this.escapeHtml(code[i])}</span>`
        );
        i++;
        continue;
      }

      // Punctuation
      if (/[{}[\]();,.]/.test(code[i])) {
        result.push(
          `<span class="token-punctuation">${this.escapeHtml(code[i])}</span>`
        );
        i++;
        continue;
      }

      // Whitespace and other
      result.push(this.escapeHtml(code[i]));
      i++;
    }

    return result.join("");
  }

  async testHttpConnection() {
    const url = document.getElementById("server-url").value.trim();
    const bearerToken = document.getElementById("server-token").value.trim();
    const statusEl = document.getElementById("connection-status");

    if (!url) {
      statusEl.textContent = "Enter a URL first";
      statusEl.className = "connection-status status-error";
      return;
    }

    statusEl.textContent = "Testing...";
    statusEl.className = "connection-status status-testing";

    try {
      // MCP Streamable HTTP transport headers per spec
      const headers = {
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-03-26",
      };
      if (bearerToken) {
        headers.Authorization = `Bearer ${bearerToken}`;
      }

      const requestBody = {
        jsonrpc: "2.0",
        method: "initialize",
        params: {
          protocolVersion: "2025-03-26",
          clientInfo: { name: "harbor-test", version: "1.0.0" },
          capabilities: {},
        },
        id: 1,
      };

      const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => "");
        console.error("[Harbor] Response body:", errorText);
        throw new Error(
          `HTTP ${response.status}: ${response.statusText}${errorText ? ` - ${errorText.substring(0, 200)}` : ""}`
        );
      }

      const contentType = response.headers.get("content-type") || "";
      const text = await response.text();

      let data;
      if (contentType.includes("text/event-stream")) {
        // SSE response - parse the first data line
        const dataMatch = text.match(/^data:\s*(.+)$/m);
        if (dataMatch) {
          data = JSON.parse(dataMatch[1]);
        } else {
          throw new Error("Invalid SSE response format");
        }
      } else {
        data = JSON.parse(text);
      }

      if (data.error) {
        throw new Error(data.error.message || JSON.stringify(data.error));
      }

      const serverName = data.result?.serverInfo?.name || "MCP Server";
      const serverVersion = data.result?.serverInfo?.version;
      statusEl.textContent = serverVersion
        ? `Connected: ${serverName} v${serverVersion}`
        : `Connected: ${serverName}`;
      statusEl.className = "connection-status status-success";
    } catch (error) {
      console.error("[Harbor] HTTP connection test failed:", error);
      console.error("[Harbor] URL:", url);

      let message = "Connection failed";
      if (error.name === "TimeoutError") {
        message = "Connection timeout (10s)";
      } else if (
        error.name === "TypeError" &&
        error.message.includes("NetworkError")
      ) {
        message = "Network error - check URL and CORS";
      } else if (error.name === "TypeError") {
        message = `Network error: ${error.message}`;
      } else if (error.message) {
        message = error.message;
      }

      if (error.cause) {
        console.error("[Harbor] Cause:", error.cause);
      }

      statusEl.textContent = message;
      statusEl.className = "connection-status status-error";
      statusEl.title = `${error.name}: ${error.message}`;
    }
  }

  updateStatus() {
    const statusDiv = document.getElementById("harbor-status");
    const serverCount = this.manager.servers.size;
    const toolCount = this.registry.listAllTools().length;
    statusDiv.textContent = `${serverCount} server(s) | ${toolCount} tool(s)`;
  }

  openServerDialog(serverId = null, options = {}) {
    const { readonly = false } = options;
    const dialog = document.getElementById("server-editor-dialog");
    const form = document.getElementById("server-editor-form");
    const titleEl = document.getElementById("dialog-title");
    const deleteBtn = document.getElementById("dialog-delete-btn");
    const saveBtn = document.getElementById("dialog-save-btn");
    const templateField = document.getElementById("template-field");
    const templateSelect = document.getElementById("server-template");
    const codeErrorDiv = document.getElementById("code-error");

    // Reset form and clear errors
    form.reset();
    codeErrorDiv.classList.add("hidden");
    codeErrorDiv.textContent = "";
    this.editingServerId = serverId;
    this.dialogReadonly = readonly;

    // Get form elements for readonly handling
    const nameInput = document.getElementById("server-name");
    const typeSelect = document.getElementById("server-type");
    const enabledCheckbox = document.getElementById("server-enabled");
    const codeTextarea = document.getElementById("server-code");
    const urlInput = document.getElementById("server-url");
    const tokenInput = document.getElementById("server-token");
    const capLevelSelect = document.getElementById("capability-level");

    if (serverId) {
      // Look up in all servers (includes builtins)
      const config = this.getAllServers().find(s => s.id === serverId);

      if (readonly) {
        // View mode for builtin servers
        titleEl.textContent = "View Server";
        deleteBtn.classList.add("hidden");
        saveBtn.classList.add("hidden");
      } else {
        // Edit mode
        titleEl.textContent = "Edit Server";
        deleteBtn.classList.remove("hidden");
        saveBtn.classList.remove("hidden");
      }
      templateField.classList.add("hidden");

      if (config) {
        nameInput.value = config.name;
        typeSelect.value = config.type;
        enabledCheckbox.checked = config.enabled;

        if (config.type === "sandbox") {
          const code = config.code || "";
          codeTextarea.value = code;
          document.getElementById("code-field").classList.remove("hidden");
          document.getElementById("url-field").classList.add("hidden");
          document.getElementById("token-field").classList.add("hidden");
          document.getElementById("http-actions").classList.add("hidden");
          this.updateCodeHighlight(code);
        } else {
          urlInput.value = config.url || "";
          tokenInput.value = "";
          tokenInput.placeholder = config.hasBearerToken
            ? "(Token saved - enter new value to replace)"
            : "Optional bearer token";
          document.getElementById("code-field").classList.add("hidden");
          document.getElementById("url-field").classList.remove("hidden");
          document.getElementById("token-field").classList.remove("hidden");
          document.getElementById("http-actions").classList.remove("hidden");
        }
      }

      // Set readonly state on form elements
      nameInput.readOnly = readonly;
      typeSelect.disabled = readonly;
      enabledCheckbox.disabled = readonly;
      codeTextarea.readOnly = readonly;
      urlInput.readOnly = readonly;
      tokenInput.readOnly = readonly;
      capLevelSelect.disabled = readonly;
    } else {
      // Create mode - show template selector for sandbox type
      titleEl.textContent = "Add Server";
      deleteBtn.classList.add("hidden");
      saveBtn.classList.remove("hidden");
      templateField.classList.remove("hidden");
      templateSelect.value = "";
      document.getElementById("code-field").classList.remove("hidden");
      document.getElementById("url-field").classList.add("hidden");
      document.getElementById("token-field").classList.add("hidden");
      document.getElementById("http-actions").classList.add("hidden");
      tokenInput.placeholder = "Optional bearer token";
      this.updateCodeHighlight("");

      // Ensure not readonly for create mode
      nameInput.readOnly = false;
      typeSelect.disabled = false;
      enabledCheckbox.disabled = false;
      codeTextarea.readOnly = false;
      urlInput.readOnly = false;
      tokenInput.readOnly = false;
      capLevelSelect.disabled = false;
    }

    // Clear connection status
    const statusEl = document.getElementById("connection-status");
    statusEl.textContent = "";
    statusEl.className = "connection-status";

    // Load capability level
    if (serverId) {
      const profile = lazy.CapabilityProfileStore.load(serverId);
      capLevelSelect.value = profile?.level || "isolated";
    } else {
      capLevelSelect.value = "isolated";
    }
    this.updateCapabilityDisplay(capLevelSelect.value);

    dialog.showModal();
  }

  async saveServer() {
    const dialog = document.getElementById("server-editor-dialog");
    const serverName = document.getElementById("server-name").value.trim();
    const type = document.getElementById("server-type").value;
    const enabled = document.getElementById("server-enabled").checked;
    const codeErrorDiv = document.getElementById("code-error");

    codeErrorDiv.classList.add("hidden");
    codeErrorDiv.textContent = "";

    if (!serverName) {
      // eslint-disable-next-line no-alert
      alert("Server name is required");
      return;
    }

    const config = {
      name: serverName,
      type,
      enabled,
    };

    if (this.editingServerId) {
      config.id = this.editingServerId;
    }

    let bearerToken = null;
    if (type === "sandbox") {
      config.code = document.getElementById("server-code").value;
      if (!config.code.trim()) {
        // eslint-disable-next-line no-alert
        alert("Server code is required for sandbox servers");
        return;
      }
    } else {
      config.url = document.getElementById("server-url").value;
      bearerToken = document.getElementById("server-token").value.trim();
      config.hasBearerToken = !!bearerToken;
      if (!config.url.trim()) {
        // eslint-disable-next-line no-alert
        alert("Server URL is required for HTTP servers");
        return;
      }
    }

    try {
      // If editing, unregister the old server first
      if (
        this.editingServerId &&
        this.manager.servers.has(this.editingServerId)
      ) {
        await this.manager.unregisterServer(this.editingServerId);
      }

      // Save to store (without bearer token - just the flag)
      const saved = lazy.HarborServerStore.saveServer(config);

      // Store bearer token securely if provided
      if (type === "http" && bearerToken) {
        await lazy.HarborCredentialStore.storeBearerToken(
          saved.id,
          bearerToken
        );
      } else if (type === "http" && !bearerToken && this.editingServerId) {
        // If editing and token was cleared, remove from credential store
        await lazy.HarborCredentialStore.removeBearerToken(saved.id);
      }

      // Save capability profile
      const capabilityLevel = document.getElementById("capability-level").value;
      const capProfile =
        lazy.CapabilityProfileStore.getDefaultProfile(capabilityLevel);
      if (capProfile) {
        lazy.CapabilityProfileStore.save(saved.id, capProfile);
      }

      // Register the server if enabled
      if (enabled) {
        await this.registerServerFromConfig(saved);
      }

      dialog.close();
      this.renderServers();
      this.renderTools();
      this.updateStatus();
    } catch (error) {
      console.error("[Harbor] Failed to save server:", error);
      if (type === "sandbox" && error.message) {
        codeErrorDiv.textContent = error.message;
        codeErrorDiv.classList.remove("hidden");
      } else {
        alert(`Failed to save server: ${error.message}`);
      }
    }
  }

  async deleteServer(serverId) {
    // eslint-disable-next-line no-alert
    if (!confirm("Are you sure you want to delete this server?")) {
      return;
    }

    const dialog = document.getElementById("server-editor-dialog");

    try {
      if (this.manager.servers.has(serverId)) {
        await this.manager.unregisterServer(serverId);
      }
      await lazy.HarborCredentialStore.removeBearerToken(serverId);
      lazy.CapabilityProfileStore.delete(serverId);
      lazy.HarborServerStore.deleteServer(serverId);

      dialog.close();
      this.renderServers();
      this.renderTools();
      this.updateStatus();
    } catch (error) {
      console.error("[Harbor] Failed to delete server:", error);
      // eslint-disable-next-line no-alert
      alert(`Failed to delete server: ${error.message}`);
    }
  }

  async toggleServer(serverId) {
    const config = lazy.HarborServerStore.getServer(serverId);
    if (!config) {
      return;
    }

    const newEnabled = !config.enabled;

    try {
      if (newEnabled) {
        await this.registerServerFromConfig({ ...config, enabled: true });
      } else if (this.manager.servers.has(serverId)) {
        await this.manager.unregisterServer(serverId);
        this.registry.unregisterServerTools(serverId);
      }

      lazy.HarborServerStore.setServerEnabled(serverId, newEnabled);

      this.renderServers();
      this.renderTools();
      this.updateStatus();
    } catch (error) {
      console.error("[Harbor] Failed to toggle server:", error);
      // eslint-disable-next-line no-alert
      alert(`Failed to toggle server: ${error.message}`);
    }
  }

  showError(message) {
    console.error("[Harbor]", message);
  }

  exportServers() {
    let url = null;
    let a = null;

    try {
      const json = lazy.HarborServerStore.exportConfigs();
      const blob = new Blob([json], { type: "application/json" });
      url = URL.createObjectURL(blob);

      a = document.createElement("a");
      a.href = url;
      a.download = `harbor-servers-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
    } catch (error) {
      console.error("[Harbor] Export failed:", error);
      // eslint-disable-next-line no-alert
      alert(`Export failed: ${error.message}`);
    } finally {
      if (a && a.parentNode) {
        document.body.removeChild(a);
      }
      if (url) {
        URL.revokeObjectURL(url);
      }
    }
  }

  async resetToDefaults() {
    // eslint-disable-next-line no-alert
    if (
      !confirm(
        "This will delete all user-added servers and reset to defaults. Continue?"
      )
    ) {
      return;
    }

    try {
      const userServers = lazy.HarborServerStore.loadServers();
      for (const config of userServers) {
        if (this.manager.servers.has(config.id)) {
          await this.manager.unregisterServer(config.id);
        }
      }

      lazy.HarborServerStore.clearAll();

      for (const config of userServers) {
        lazy.CapabilityProfileStore.delete(config.id);
      }

      this.renderServers();
      this.renderTools();
      this.updateStatus();
    } catch (error) {
      console.error("[Harbor] Failed to reset:", error);
      // eslint-disable-next-line no-alert
      alert(`Failed to reset: ${error.message}`);
    }
  }

  async importServers(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const count = lazy.HarborServerStore.importConfigs(text);

      const servers = lazy.HarborServerStore.loadServers();
      for (const config of servers) {
        if (config.enabled && !this.manager.servers.has(config.id)) {
          await this.registerServerFromConfig(config);
        }
      }

      this.renderServers();
      this.renderTools();
      this.updateStatus();

      // eslint-disable-next-line no-alert
      alert(`Successfully imported ${count} server(s)`);
    } catch (error) {
      console.error("[Harbor] Import failed:", error);
      // eslint-disable-next-line no-alert
      alert(`Import failed: ${error.message}`);
    }

    event.target.value = "";
  }
}

// Initialize Harbor when DOM is ready
document.addEventListener("DOMContentLoaded", async () => {
  const harbor = new HarborUI();
  await harbor.init();

  // Make harbor available globally for debugging
  window.harbor = harbor;
});
