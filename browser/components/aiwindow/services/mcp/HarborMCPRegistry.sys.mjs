/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * HarborMCPRegistry - Central registry for extension-based MCP servers.
 *
 * This module is shared between:
 * - ext-harbor.js (WebExtension API implementation)
 * - MCPExtensionTransport.sys.mjs (Harbor's transport layer)
 */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";

// Request ID format: req_{counter}_{timestamp}
const REQUEST_ID_PATTERN = /^req_\d+_\d+$/;

/**
 * Central registry for extension-based MCP servers.
 */
class HarborMCPRegistryClass {
  constructor() {
    this._servers = new Map();
    this._pendingRequests = new Map();
    this._requestIdCounter = 0;
    this._listeners = new Set();
  }

  register(extensionId, metadata, fireEvent) {
    if (this._servers.has(extensionId)) {
      throw new Error(`Extension ${extensionId} is already registered`);
    }

    this._servers.set(extensionId, {
      metadata,
      fireEvent,
      registeredAt: Date.now(),
    });

    for (let listener of this._listeners) {
      try {
        listener("registered", extensionId, metadata);
      } catch (e) {
        console.error("[HarborMCPRegistry] Listener error:", e);
      }
    }
  }

  unregister(extensionId) {
    const had = this._servers.delete(extensionId);

    // Reject any pending requests for this extension and clear their timeouts
    for (let [requestId, pending] of this._pendingRequests) {
      if (pending.extensionId === extensionId) {
        clearTimeout(pending.timeoutId);
        pending.reject(new Error("Extension unregistered"));
        this._pendingRequests.delete(requestId);
      }
    }

    if (had) {
      for (let listener of this._listeners) {
        try {
          listener("unregistered", extensionId);
        } catch (e) {
          console.error("[HarborMCPRegistry] Listener error:", e);
        }
      }
    }

    return had;
  }

  has(extensionId) {
    return this._servers.has(extensionId);
  }

  get(extensionId) {
    return this._servers.get(extensionId);
  }

  list() {
    return Array.from(this._servers.entries()).map(([id, info]) => ({
      extensionId: id,
      ...info.metadata,
      registeredAt: info.registeredAt,
    }));
  }

  async sendMessage(extensionId, message) {
    const server = this._servers.get(extensionId);
    if (!server) {
      throw new Error(`Extension not registered: ${extensionId}`);
    }

    const requestId = `req_${++this._requestIdCounter}_${Date.now()}`;

    return new Promise((resolve, reject) => {
      const timeoutMs = 30000;
      const timeoutId = setTimeout(() => {
        this._pendingRequests.delete(requestId);
        reject(new Error(`MCP request timeout after ${timeoutMs}ms`));
      }, timeoutMs);

      this._pendingRequests.set(requestId, {
        extensionId,
        resolve,
        reject,
        timeoutId,
      });

      try {
        server.fireEvent(requestId, message);
      } catch (e) {
        clearTimeout(timeoutId);
        this._pendingRequests.delete(requestId);
        reject(e);
      }
    });
  }

  handleResponse(extensionId, requestId, response) {
    // Validate requestId format to prevent forged responses
    if (typeof requestId !== "string" || !REQUEST_ID_PATTERN.test(requestId)) {
      console.warn(`[HarborMCPRegistry] Invalid requestId format: ${requestId}`);
      return;
    }

    const pending = this._pendingRequests.get(requestId);
    if (!pending) {
      console.warn(`[HarborMCPRegistry] No pending request: ${requestId}`);
      return;
    }

    if (pending.extensionId !== extensionId) {
      console.warn(`[HarborMCPRegistry] Request/extension mismatch`);
      return;
    }

    clearTimeout(pending.timeoutId);
    this._pendingRequests.delete(requestId);
    pending.resolve(response);
  }

  addListener(listener) {
    this._listeners.add(listener);
  }

  removeListener(listener) {
    this._listeners.delete(listener);
  }
}

// Singleton instance
export const HarborMCPRegistry = new HarborMCPRegistryClass();
