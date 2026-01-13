/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const SERVERS_PREF = "browser.aiwindow.harbor.servers";

/**
 * HarborServerStore handles persistence of MCP server configurations.
 * Servers are stored as JSON in a preference string.
 *
 * Server Configuration Schema:
 * {
 *   id: string,           // Unique identifier
 *   name: string,         // Display name
 *   type: "sandbox"|"http", // Server type
 *   code: string,         // JavaScript code (for sandbox servers)
 *   url: string|null,     // Server URL (for http servers)
 *   enabled: boolean,     // Whether server should auto-start
 *   createdAt: number,    // Timestamp of creation
 *   updatedAt: number     // Timestamp of last update
 * }
 */
export const HarborServerStore = {
  /**
   * Load all server configurations from preferences.
   *
   * @returns {Array<object>} Array of server configurations
   */
  loadServers() {
    try {
      const json = Services.prefs.getStringPref(SERVERS_PREF, "[]");
      const servers = JSON.parse(json);
      if (!Array.isArray(servers)) {
        console.error("[HarborServerStore] Invalid servers pref format");
        return [];
      }
      return servers;
    } catch (error) {
      console.error("[HarborServerStore] Failed to load servers:", error);
      return [];
    }
  },

  /**
   * Save the servers array to preferences.
   *
   * @param {Array<object>} servers - Array of server configurations
   */
  _saveServers(servers) {
    try {
      const json = JSON.stringify(servers);
      Services.prefs.setStringPref(SERVERS_PREF, json);
    } catch (error) {
      console.error("[HarborServerStore] Failed to save servers:", error);
      throw error;
    }
  },

  /**
   * Get a single server configuration by ID.
   *
   * @param {string} serverId - The server ID
   * @returns {object|null} Server configuration or null if not found
   */
  getServer(serverId) {
    const servers = this.loadServers();
    return servers.find(s => s.id === serverId) || null;
  },

  /**
   * Save a server configuration (create or update).
   *
   * @param {object} config - Server configuration object
   * @param {string} config.id - Unique identifier (optional for new servers)
   * @param {string} config.name - Display name
   * @param {string} config.type - Server type ("sandbox" or "http")
   * @param {string} [config.code] - JavaScript code (for sandbox servers)
   * @param {string} [config.url] - Server URL (for http servers)
   * @param {boolean} [config.enabled=true] - Whether server should auto-start
   * @returns {object} The saved server configuration (with generated ID if new)
   */
  saveServer(config) {
    const servers = this.loadServers();
    const now = Date.now();

    // Validate required fields
    if (!config.name || !config.type) {
      throw new Error("Server name and type are required");
    }

    if (config.type === "sandbox" && !config.code) {
      throw new Error("Sandbox servers require code");
    }

    if (config.type === "http" && !config.url) {
      throw new Error("HTTP servers require a URL");
    }

    // Check if updating existing server
    const existingIndex = config.id
      ? servers.findIndex(s => s.id === config.id)
      : -1;

    const serverConfig = {
      id: config.id || this._generateId(),
      name: config.name,
      type: config.type,
      code: config.code || null,
      url: config.url || null,
      enabled: config.enabled !== false,
      // Store flag indicating bearer token exists (actual token stored securely)
      hasBearerToken: config.hasBearerToken || false,
      createdAt: existingIndex >= 0 ? servers[existingIndex].createdAt : now,
      updatedAt: now,
    };

    if (existingIndex >= 0) {
      servers[existingIndex] = serverConfig;
    } else {
      servers.push(serverConfig);
    }

    this._saveServers(servers);
    return serverConfig;
  },

  /**
   * Delete a server configuration.
   *
   * @param {string} serverId - The server ID to delete
   * @returns {boolean} True if server was deleted, false if not found
   */
  deleteServer(serverId) {
    const servers = this.loadServers();
    const index = servers.findIndex(s => s.id === serverId);

    if (index === -1) {
      return false;
    }

    servers.splice(index, 1);
    this._saveServers(servers);
    return true;
  },

  /**
   * Update a server's enabled state.
   *
   * @param {string} serverId - The server ID
   * @param {boolean} enabled - New enabled state
   * @returns {boolean} True if updated, false if server not found
   */
  setServerEnabled(serverId, enabled) {
    const servers = this.loadServers();
    const server = servers.find(s => s.id === serverId);

    if (!server) {
      return false;
    }

    server.enabled = enabled;
    server.updatedAt = Date.now();
    this._saveServers(servers);
    return true;
  },

  /**
   * Export all server configurations as JSON string.
   *
   * @returns {string} JSON string of all servers
   */
  exportConfigs() {
    return JSON.stringify(this.loadServers(), null, 2);
  },

  /**
   * Import server configurations from JSON string.
   * Merges with existing servers, updating by ID if exists.
   *
   * @param {string} json - JSON string of servers to import
   * @returns {number} Number of servers imported/updated
   */
  importConfigs(json) {
    const imported = JSON.parse(json);
    if (!Array.isArray(imported)) {
      throw new Error("Import data must be an array of servers");
    }

    let count = 0;
    for (const config of imported) {
      if (config.name && config.type) {
        this.saveServer(config);
        count++;
      }
    }
    return count;
  },

  /**
   * Clear all server configurations.
   */
  clearAll() {
    this._saveServers([]);
  },

  /**
   * Generate a unique server ID.
   *
   * @returns {string} Generated ID
   */
  _generateId() {
    return `server-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  },
};
