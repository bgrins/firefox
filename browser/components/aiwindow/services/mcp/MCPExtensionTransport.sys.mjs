/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { MCPClient } from "moz-src:///browser/components/aiwindow/services/mcp/MCPClient.sys.mjs";
import { HarborMCPRegistry } from "moz-src:///browser/components/aiwindow/services/mcp/HarborMCPRegistry.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  ExtensionParent: "resource://gre/modules/ExtensionParent.sys.mjs",
});

/**
 * MCP Extension Transport
 *
 * Implements MCP protocol transport for WebExtension-based MCP servers.
 * Extensions use the browser.harbor API to register as MCP servers and
 * receive messages.
 *
 * Communication flow:
 * 1. Extension calls browser.harbor.registerMCPServer() on startup
 * 2. Harbor (this transport) sends JSON-RPC messages via HarborMCPRegistry
 * 3. Extension receives messages via browser.harbor.onMCPMessage
 * 4. Extension responds via browser.harbor.sendMCPResponse()
 */
export class MCPExtensionTransport extends MCPClient {
  #extensionId;
  #connected = false;

  constructor(extensionId, options = {}) {
    super({ clientId: options.serverId || `extension-${extensionId}` });
    this.#extensionId = extensionId;
  }

  get extensionId() {
    return this.#extensionId;
  }

  /**
   * Transport-specific connection logic.
   * Verifies the extension is installed and registered with Harbor.
   */
  async _connect() {
    // Verify extension exists
    const extension = lazy.ExtensionParent.GlobalManager.getExtension(
      this.#extensionId
    );

    if (!extension) {
      throw new Error(`Extension not found: ${this.#extensionId}`);
    }

    // Check if already registered
    if (HarborMCPRegistry.has(this.#extensionId)) {
      this.#connected = true;
      return;
    }

    // Wait for extension to register using event listener instead of polling
    const maxWaitMs = 5000;
    await new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        HarborMCPRegistry.removeListener(listener);
        reject(
          new Error(
            `Extension ${this.#extensionId} did not register with Harbor within ${maxWaitMs}ms. ` +
              `Extensions must call browser.harbor.registerMCPServer().`
          )
        );
      }, maxWaitMs);

      const listener = (event, extensionId) => {
        if (event === "registered" && extensionId === this.#extensionId) {
          clearTimeout(timeoutId);
          HarborMCPRegistry.removeListener(listener);
          resolve();
        }
      };

      HarborMCPRegistry.addListener(listener);

      // Check again in case it registered between our first check and adding the listener
      if (HarborMCPRegistry.has(this.#extensionId)) {
        clearTimeout(timeoutId);
        HarborMCPRegistry.removeListener(listener);
        resolve();
      }
    });

    this.#connected = true;
  }

  /**
   * Transport-specific cleanup logic.
   */
  async _disconnect() {
    this.#connected = false;
  }

  /**
   * Send a JSON-RPC message to the extension and wait for response.
   *
   * @param {object} message - JSON-RPC 2.0 message
   * @returns {Promise<any>} Response result
   */
  async _sendRequest(message) {
    if (!this.#connected) {
      throw new Error("Not connected to extension");
    }

    if (!HarborMCPRegistry.has(this.#extensionId)) {
      throw new Error(`Extension ${this.#extensionId} is not registered`);
    }

    const response = await HarborMCPRegistry.sendMessage(
      this.#extensionId,
      message
    );

    if (response.error) {
      throw new Error(response.error.message || "Extension returned error");
    }

    return response.result;
  }
}
