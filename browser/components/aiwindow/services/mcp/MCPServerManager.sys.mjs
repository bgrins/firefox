/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { MCPHttpTransport } from "moz-src:///browser/components/aiwindow/services/mcp/MCPHttpTransport.sys.mjs";
import { MCPSandboxTransport } from "moz-src:///browser/components/aiwindow/services/mcp/MCPSandboxTransport.sys.mjs";
import { MCPExtensionTransport } from "moz-src:///browser/components/aiwindow/services/mcp/MCPExtensionTransport.sys.mjs";

const ServerStatus = {
  STOPPED: "stopped",
  STARTING: "starting",
  RUNNING: "running",
  STOPPING: "stopping",
  ERROR: "error",
};

// Resource limits (fix #15)
const MAX_SERVERS = 100;

export class MCPServerManager {
  constructor() {
    this.servers = new Map();
    this.transports = new Map();
    this.startingServers = new Map(); // Track concurrent starts (fix #6)
    this.stoppingServers = new Map(); // Track concurrent stops (fix #6)
  }

  async registerServer(config) {
    const { id, type, enabled = true } = config;

    if (!id) {
      throw new Error("Server id is required");
    }

    if (!type || !["http", "sandbox", "extension"].includes(type)) {
      throw new Error("Server type must be 'http', 'sandbox', or 'extension'");
    }

    if (this.servers.has(id)) {
      throw new Error(`Server ${id} is already registered`);
    }

    // Fix #15: Check resource limits
    if (this.servers.size >= MAX_SERVERS) {
      throw new Error(`Cannot register server, limit of ${MAX_SERVERS} reached`);
    }

    if (type === "http" && !config.url) {
      throw new Error("HTTP server requires url");
    }

    if (type === "sandbox" && !config.code) {
      throw new Error("Sandbox server requires code");
    }

    if (type === "extension" && !config.extensionId) {
      throw new Error("Extension server requires extensionId");
    }

    this.servers.set(id, {
      config,
      status: ServerStatus.STOPPED,
      serverInfo: null,
      lastError: null,
      startTime: null,
    });

    console.log(`[MCPServerManager] Registered server: ${id}`);

    if (enabled) {
      try {
        await this.startServer(id);
      } catch (error) {
        // Don't throw if auto-start fails - server is registered but not started
        console.warn(`[MCPServerManager] Auto-start failed for ${id}:`, error.message);
      }
    }
  }

  async unregisterServer(serverId) {
    if (!this.servers.has(serverId)) {
      throw new Error(`Server ${serverId} not found`);
    }

    await this.stopServer(serverId);
    this.servers.delete(serverId);

    console.log(`[MCPServerManager] Unregistered server: ${serverId}`);
  }

  async startServer(serverId) {
    const server = this.servers.get(serverId);

    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    if (server.status === ServerStatus.RUNNING) {
      console.log(`[MCPServerManager] Server ${serverId} already running`);
      return;
    }

    // Fix #6: Return existing promise if already starting
    if (this.startingServers.has(serverId)) {
      return this.startingServers.get(serverId);
    }

    this._updateServerStatus(serverId, ServerStatus.STARTING);

    const startPromise = (async () => {
      try {
        const transport = this._createTransport(server.config);
        const initResult = await transport.connect();

        this.transports.set(serverId, transport);

        this._updateServerStatus(serverId, ServerStatus.RUNNING, {
          serverInfo: initResult.serverInfo,
          startTime: Date.now(),
          lastError: null,
        });

        console.log(`[MCPServerManager] Started server: ${serverId}`, {
          serverInfo: initResult.serverInfo,
        });
      } catch (error) {
        this._updateServerStatus(serverId, ServerStatus.ERROR, {
          lastError: error.message,
        });

        // Don't log here - let caller decide how to handle the error
        throw new Error(`Failed to start server ${serverId}: ${error.message}`);
      } finally {
        this.startingServers.delete(serverId);
      }
    })();

    this.startingServers.set(serverId, startPromise);
    return startPromise;
  }

  async stopServer(serverId) {
    const server = this.servers.get(serverId);

    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    if (server.status === ServerStatus.STOPPED) {
      console.log(`[MCPServerManager] Server ${serverId} already stopped`);
      return;
    }

    // Fix #6: Return existing promise if already stopping
    if (this.stoppingServers.has(serverId)) {
      return this.stoppingServers.get(serverId);
    }

    this._updateServerStatus(serverId, ServerStatus.STOPPING);

    const stopPromise = (async () => {
      const transport = this.transports.get(serverId);

      try {
        if (transport) {
          await transport.disconnect();
        }

        // Always remove transport from map, even on error
        this.transports.delete(serverId);

        this._updateServerStatus(serverId, ServerStatus.STOPPED, {
          serverInfo: null,
          startTime: null,
        });

        console.log(`[MCPServerManager] Stopped server: ${serverId}`);
      } catch (error) {
        console.error(
          `[MCPServerManager] Error stopping server ${serverId}:`,
          error
        );

        // Remove transport even on disconnect error
        this.transports.delete(serverId);

        // Set to ERROR state since disconnect failed
        this._updateServerStatus(serverId, ServerStatus.ERROR, {
          lastError: `Disconnect error: ${error.message}`,
          serverInfo: null,
          startTime: null,
        });

        // Re-throw so caller knows stop failed
        throw new Error(`Failed to stop server ${serverId}: ${error.message}`);
      } finally {
        this.stoppingServers.delete(serverId);
      }
    })();

    this.stoppingServers.set(serverId, stopPromise);
    return stopPromise;
  }

  async restartServer(serverId) {
    const server = this.servers.get(serverId);

    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    console.log(`[MCPServerManager] Restarting server: ${serverId}`);

    // Fix #8: Better error handling for restart
    try {
      await this.stopServer(serverId);
    } catch (stopError) {
      console.warn(
        `[MCPServerManager] Stop failed during restart of ${serverId}, attempting start anyway:`,
        stopError
      );
      // Continue to start even if stop fails
    }

    try {
      await this.startServer(serverId);
    } catch (startError) {
      // If start fails, log and re-throw with context
      console.error(
        `[MCPServerManager] Failed to restart server ${serverId}:`,
        startError
      );
      throw new Error(
        `Failed to restart server ${serverId}: ${startError.message}`
      );
    }
  }

  getServerInfo(serverId) {
    const server = this.servers.get(serverId);

    if (!server) {
      throw new Error(`Server ${serverId} not found`);
    }

    return {
      id: serverId,
      type: server.config.type,
      status: server.status,
      serverInfo: server.serverInfo,
      startTime: server.startTime,
      lastError: server.lastError,
      uptime: server.startTime ? Date.now() - server.startTime : null,
    };
  }

  listServers() {
    return Array.from(this.servers.keys()).map(serverId =>
      this.getServerInfo(serverId)
    );
  }

  getServerStatus(serverId) {
    const server = this.servers.get(serverId);
    return server ? server.status : null;
  }

  getTransport(serverId) {
    return this.transports.get(serverId);
  }

  async startAllServers() {
    const serverIds = Array.from(this.servers.keys());
    const toStart = serverIds.filter(id => {
      const server = this.servers.get(id);
      return (
        server.config.enabled !== false &&
        server.status === ServerStatus.STOPPED
      );
    });

    // Fix #7: Track and return failures
    const results = await Promise.allSettled(
      toStart.map(id => this.startServer(id))
    );

    const failures = [];
    results.forEach((result, index) => {
      if (result.status === "rejected") {
        const serverId = toStart[index];
        console.error(`Failed to start server ${serverId}:`, result.reason);
        failures.push({ serverId, error: result.reason.message });
      }
    });

    return { started: toStart.length - failures.length, failures };
  }

  async stopAllServers() {
    const serverIds = Array.from(this.servers.keys());
    const toStop = serverIds.filter(id => {
      const server = this.servers.get(id);
      return server.status === ServerStatus.RUNNING;
    });

    // Fix #7: Track and return failures
    const results = await Promise.allSettled(
      toStop.map(id => this.stopServer(id))
    );

    const failures = [];
    results.forEach((result, index) => {
      if (result.status === "rejected") {
        const serverId = toStop[index];
        console.error(`Failed to stop server ${serverId}:`, result.reason);
        failures.push({ serverId, error: result.reason.message });
      }
    });

    return { stopped: toStop.length - failures.length, failures };
  }

  _createTransport(config) {
    const { type, url, code, extensionId, options = {}, onConsole } = config;

    if (type === "http") {
      return new MCPHttpTransport(url, {
        clientId: config.id,
        ...options,
      });
    }

    if (type === "sandbox") {
      return new MCPSandboxTransport(code, {
        serverId: config.id,
        onConsole,
        ...options,
      });
    }

    if (type === "extension") {
      return new MCPExtensionTransport(extensionId, {
        serverId: config.id,
        ...options,
      });
    }

    throw new Error(`Unknown transport type: ${type}`);
  }

  _updateServerStatus(serverId, status, updates = {}) {
    const server = this.servers.get(serverId);

    if (!server) {
      return;
    }

    server.status = status;
    Object.assign(server, updates);
  }
}

export { ServerStatus };
