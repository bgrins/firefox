/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { MCPClient } from "moz-src:///browser/components/aiwindow/services/mcp/MCPClient.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  ExtensionParent: "resource://gre/modules/ExtensionParent.sys.mjs",
});

/**
 * MCP Extension Transport
 *
 * Implements MCP protocol transport for WebExtension-based MCP servers.
 * The extension's background script acts as the MCP server, receiving
 * JSON-RPC messages via browser.runtime.onMessage.
 *
 * Communication flow:
 * 1. Harbor (this transport) sends JSON-RPC messages to the extension
 * 2. Extension background script handles the message and responds
 * 3. Response is returned to Harbor
 *
 * Extensions must:
 * - Listen on browser.runtime.onMessage for JSON-RPC 2.0 messages
 * - Return a Promise that resolves to the JSON-RPC response
 */
export class MCPExtensionTransport extends MCPClient {
  #extensionId;
  #extension;
  #messagePort;
  #pendingRequests;

  constructor(extensionId, options = {}) {
    super({ clientId: options.serverId || `extension-${extensionId}` });
    this.#extensionId = extensionId;
    this.#extension = null;
    this.#messagePort = null;
    this.#pendingRequests = new Map();
  }

  get extensionId() {
    return this.#extensionId;
  }

  /**
   * Transport-specific connection logic.
   * Finds the extension and establishes communication channel.
   */
  async _connect() {
    // Get the extension from GlobalManager
    this.#extension = lazy.ExtensionParent.GlobalManager.getExtension(
      this.#extensionId
    );

    if (!this.#extension) {
      throw new Error(`Extension not found: ${this.#extensionId}`);
    }

    // Verify extension is running
    if (!this.#extension.hasShutdown === false) {
      throw new Error(`Extension is not running: ${this.#extensionId}`);
    }
  }

  /**
   * Transport-specific cleanup logic.
   */
  async _disconnect() {
    // Reject any pending requests
    for (const [id, { reject }] of this.#pendingRequests) {
      reject(new Error("Transport disconnected"));
    }
    this.#pendingRequests.clear();

    this.#extension = null;
    this.#messagePort = null;
  }

  /**
   * Send a JSON-RPC message to the extension and wait for response.
   *
   * @param {object} message - JSON-RPC 2.0 message
   * @returns {Promise<any>} Response result
   */
  async _sendRequest(message) {
    if (!this.#extension) {
      throw new Error("Not connected to extension");
    }

    return new Promise((resolve, reject) => {
      this.#pendingRequests.set(message.id, { resolve, reject });

      // Send message to extension via internal messaging
      this.#sendToExtension(message)
        .then(response => {
          this.#pendingRequests.delete(message.id);

          if (response.error) {
            reject(
              new Error(response.error.message || "Extension returned error")
            );
          } else {
            resolve(response.result);
          }
        })
        .catch(error => {
          this.#pendingRequests.delete(message.id);
          reject(error);
        });
    });
  }

  /**
   * Internal method to send a message to the extension's background script.
   * Uses the extension's internal messaging infrastructure.
   *
   * @param {object} message - Message to send
   * @returns {Promise<object>} Response from extension
   */
  async #sendToExtension(message) {
    // Use the extension's testMessage for testing, or find another way
    // to send messages to the background script.
    //
    // For production, we need to either:
    // 1. Create a new API that extensions can use to register as MCP servers
    // 2. Use existing messaging conduits
    // 3. Have extension register a callback that we can invoke
    //
    // For now, we'll use a direct approach through the extension's contexts

    const context = this.#getBackgroundContext();
    if (!context) {
      throw new Error("Extension background context not available");
    }

    // Send the message and wait for response
    // This uses the internal extension messaging system
    return this.#dispatchToBackground(context, message);
  }

  /**
   * Get the extension's background context if available.
   */
  #getBackgroundContext() {
    if (!this.#extension) {
      return null;
    }

    // Try to get the background page context
    // The extension may have a persistent or event page background
    for (const context of this.#extension.views) {
      if (
        context.viewType === "background" ||
        context.viewType === "background_worker"
      ) {
        return context;
      }
    }

    return null;
  }

  /**
   * Dispatch a message to the background script and get response.
   * This simulates what runtime.sendMessage does internally.
   */
  async #dispatchToBackground(context, message) {
    // For the initial implementation, we'll use the extension's
    // message event system. The extension should have a listener
    // on browser.runtime.onMessage that handles MCP messages.

    // Create a promise that will be resolved when the extension responds
    return new Promise((resolve, reject) => {
      const timeoutMs = 30000;
      const timeoutId = setTimeout(() => {
        reject(new Error(`Extension message timeout after ${timeoutMs}ms`));
      }, timeoutMs);

      // Emit a message event to the extension
      // The extension's onMessage listeners will receive this
      try {
        // Use the extension's emit to trigger onMessage handlers
        // This is an internal API that may need adjustment
        const responsePromise = this.#extension.emit(
          "runtime-message",
          message,
          {
            id: this.#extensionId,
            url: "harbor://mcp-client",
          }
        );

        // Handle the response
        Promise.resolve(responsePromise)
          .then(response => {
            clearTimeout(timeoutId);
            // If response is undefined, the extension didn't handle it
            if (response === undefined) {
              resolve({
                jsonrpc: "2.0",
                id: message.id,
                error: {
                  code: -32601,
                  message: "Extension did not handle MCP message",
                },
              });
            } else {
              resolve(response);
            }
          })
          .catch(error => {
            clearTimeout(timeoutId);
            reject(error);
          });
      } catch (error) {
        clearTimeout(timeoutId);
        reject(error);
      }
    });
  }

  /**
   * Set a custom message handler for testing purposes.
   * This allows tests to inject a mock message handler.
   *
   * @param {Function} handler - Function that receives messages and returns responses
   */
  setMessageHandler(handler) {
    this._testMessageHandler = handler;
  }
}

/**
 * Registry for extension-based MCP servers.
 * Extensions register themselves here to be discoverable by Harbor.
 */
export const ExtensionMCPRegistry = {
  _registered: new Map(),
  _listeners: new Set(),

  /**
   * Register an extension as an MCP server.
   *
   * @param {string} extensionId - The extension's ID
   * @param {object} metadata - Server metadata (name, version, etc.)
   * @param {Function} messageHandler - Function to handle MCP messages
   */
  register(extensionId, metadata, messageHandler) {
    this._registered.set(extensionId, {
      metadata,
      messageHandler,
      registeredAt: Date.now(),
    });

    // Notify listeners
    for (const listener of this._listeners) {
      try {
        listener("registered", extensionId, metadata);
      } catch (e) {
        console.error("ExtensionMCPRegistry listener error:", e);
      }
    }
  },

  /**
   * Unregister an extension MCP server.
   *
   * @param {string} extensionId - The extension's ID
   */
  unregister(extensionId) {
    const had = this._registered.delete(extensionId);

    if (had) {
      for (const listener of this._listeners) {
        try {
          listener("unregistered", extensionId);
        } catch (e) {
          console.error("ExtensionMCPRegistry listener error:", e);
        }
      }
    }

    return had;
  },

  /**
   * Get a registered extension's info.
   *
   * @param {string} extensionId - The extension's ID
   * @returns {object|null} Registration info or null
   */
  get(extensionId) {
    return this._registered.get(extensionId) || null;
  },

  /**
   * Check if an extension is registered as an MCP server.
   *
   * @param {string} extensionId - The extension's ID
   * @returns {boolean}
   */
  has(extensionId) {
    return this._registered.has(extensionId);
  },

  /**
   * Get all registered extension IDs.
   *
   * @returns {Array<string>}
   */
  listExtensions() {
    return Array.from(this._registered.keys());
  },

  /**
   * Send a message to a registered extension's MCP handler.
   *
   * @param {string} extensionId - The extension's ID
   * @param {object} message - JSON-RPC message
   * @returns {Promise<object>} Response
   */
  async sendMessage(extensionId, message) {
    const registration = this._registered.get(extensionId);
    if (!registration) {
      throw new Error(`Extension not registered: ${extensionId}`);
    }

    return registration.messageHandler(message);
  },

  /**
   * Add a listener for registry changes.
   *
   * @param {Function} listener - Callback(event, extensionId, metadata?)
   */
  addListener(listener) {
    this._listeners.add(listener);
  },

  /**
   * Remove a registry change listener.
   *
   * @param {Function} listener
   */
  removeListener(listener) {
    this._listeners.delete(listener);
  },

  /**
   * Clear all registrations (for testing).
   */
  clear() {
    this._registered.clear();
  },
};
