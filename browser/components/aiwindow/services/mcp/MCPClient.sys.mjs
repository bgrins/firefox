/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import {
  setTimeout,
  clearTimeout,
} from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  AppConstants: "resource://gre/modules/AppConstants.sys.mjs",
});

/**
 * MCP Client Base Class
 *
 * Provides a common interface for MCP protocol clients, regardless of
 * transport mechanism (sandbox, HTTP, stdio, etc.).
 *
 * Subclasses must implement:
 * - _connect(): Transport-specific connection logic
 * - _disconnect(): Transport-specific cleanup
 * - _sendRequest(message): Transport-specific message sending
 */

export class MCPClient {
  constructor(options = {}) {
    this.clientId = options.clientId || "firefox-aiwindow";
    this.connected = false;
    this.serverInfo = null;
    this.timeout = options.timeout || 30000; // Default 30s timeout
  }

  /**
   * Connect to the MCP server and perform initialization handshake.
   *
   * @returns {Promise<object>} Server initialization result
   */
  async connect() {
    if (this.connected) {
      throw new Error("Already connected");
    }

    try {
      // Transport-specific connection setup
      await this._connect();

      // Mark as connected so requests can be sent
      this.connected = true;

      // Send initialization request
      const initResult = await this.request("initialize", {
        protocolVersion: "2024-11-05",
        clientInfo: {
          name: this.clientId,
          version: lazy.AppConstants.MOZ_APP_VERSION,
        },
        capabilities: {},
      });

      // Validate response structure (fix #5)
      if (!initResult || typeof initResult !== "object") {
        throw new Error("Invalid initialization response");
      }
      if (!initResult.serverInfo || typeof initResult.serverInfo !== "object") {
        throw new Error("Missing serverInfo in initialization response");
      }
      if (!initResult.serverInfo.name) {
        throw new Error("serverInfo missing required 'name' field");
      }

      this.serverInfo = initResult.serverInfo;

      console.log(`[MCPClient] Connected to ${this.clientId}`, {
        serverInfo: this.serverInfo,
      });

      return initResult;
    } catch (error) {
      // Clean up on failure
      this.connected = false;
      this.serverInfo = null;

      try {
        await this._disconnect();
      } catch (cleanupError) {
        console.error("[MCPClient] Cleanup error:", cleanupError);
      }

      throw new Error(`Failed to connect: ${error.message}`);
    }
  }

  /**
   * Send a request to the MCP server with timeout.
   *
   * @param {string} method - MCP method name (e.g., "tools/list")
   * @param {object} params - Method parameters
   * @param {number} timeout - Optional timeout in ms (defaults to this.timeout)
   * @returns {Promise<any>} Method result
   */
  async request(method, params = {}, timeout = this.timeout) {
    if (!this.connected) {
      throw new Error("Not connected");
    }

    const message = {
      jsonrpc: "2.0",
      method,
      params,
      id: this._generateRequestId(),
    };

    // Wrap request with timeout - must clear timeout to prevent memory leak
    let timeoutId;
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(
        () =>
          reject(
            new Error(
              `Request timeout after ${timeout}ms for method: ${method}`
            )
          ),
        timeout
      );
    });

    try {
      const result = await Promise.race([
        this._sendRequest(message),
        timeoutPromise,
      ]);
      clearTimeout(timeoutId);
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Disconnect from the MCP server and clean up resources.
   */
  async disconnect() {
    if (this.connected) {
      console.log(`[MCPClient] Disconnecting ${this.clientId}`);
      await this._disconnect();
      this.connected = false;
      this.serverInfo = null;
    }
  }

  /**
   * Check if connected to the server.
   *
   * @returns {boolean}
   */
  isConnected() {
    return this.connected;
  }

  /**
   * Get server information from initialization.
   *
   * @returns {object|null}
   */
  getServerInfo() {
    return this.serverInfo;
  }

  /**
   * List available tools from the MCP server.
   *
   * @returns {Promise<Array>} Array of tool definitions
   */
  async listTools() {
    const result = await this.request("tools/list", {});
    return result.tools || [];
  }

  /**
   * Call a tool on the MCP server.
   *
   * @param {string} name - Tool name
   * @param {object} args - Tool arguments
   * @returns {Promise<object>} Tool result with content array
   */
  async callTool(name, args = {}) {
    return this.request("tools/call", {
      name,
      arguments: args,
    });
  }

  /**
   * List available resources from the MCP server.
   *
   * @returns {Promise<Array>} Array of resource definitions
   */
  async listResources() {
    const result = await this.request("resources/list", {});
    return result.resources || [];
  }

  /**
   * Read a resource from the MCP server.
   *
   * @param {string} uri - Resource URI
   * @returns {Promise<object>} Resource contents
   */
  async readResource(uri) {
    return this.request("resources/read", { uri });
  }

  /**
   * List available prompts from the MCP server.
   *
   * @returns {Promise<Array>} Array of prompt definitions
   */
  async listPrompts() {
    const result = await this.request("prompts/list", {});
    return result.prompts || [];
  }

  /**
   * Get a prompt from the MCP server.
   *
   * @param {string} name - Prompt name
   * @param {object} args - Prompt arguments
   * @returns {Promise<object>} Prompt with messages
   */
  async getPrompt(name, args = {}) {
    return this.request("prompts/get", {
      name,
      arguments: args,
    });
  }

  // Protected methods to be implemented by subclasses

  /**
   * Transport-specific connection logic.
   * Called during connect() before initialization.
   *
   * @protected
   * @returns {Promise<void>}
   */
  async _connect() {
    throw new Error("Subclass must implement _connect()");
  }

  /**
   * Transport-specific cleanup logic.
   * Called during disconnect() to clean up resources.
   *
   * @protected
   * @returns {Promise<void>}
   */
  async _disconnect() {
    throw new Error("Subclass must implement _disconnect()");
  }

  /**
   * Transport-specific message sending.
   * Must handle JSON-RPC request/response correlation.
   *
   * @protected
   * @param {object} message - JSON-RPC 2.0 message
   * @returns {Promise<any>} Response result
   */
  async _sendRequest(message) {
    throw new Error("Subclass must implement _sendRequest()");
  }

  /**
   * Generate a unique request ID.
   * Uses crypto.randomUUID() to avoid overflow and collision issues (fix #4).
   *
   * @protected
   * @returns {string}
   */
  _generateRequestId() {
    return crypto.randomUUID();
  }
}
