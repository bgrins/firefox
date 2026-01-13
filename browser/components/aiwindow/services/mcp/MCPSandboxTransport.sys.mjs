/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { MCPClient } from "moz-src:///browser/components/aiwindow/services/mcp/MCPClient.sys.mjs";
import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  CapabilityBridge:
    "moz-src:///browser/components/aiwindow/services/mcp/CapabilityBridge.sys.mjs",
  CapabilityGate:
    "moz-src:///browser/components/aiwindow/services/mcp/CapabilityGate.sys.mjs",
  CapabilityProfileStore:
    "moz-src:///browser/components/aiwindow/services/mcp/CapabilityProfileStore.sys.mjs",
});

// Services is a global in .sys.mjs files

// Resource limits for sandbox servers
const MAX_CODE_SIZE = 1024 * 1024; // 1MB max code size
const MAX_RESPONSE_SIZE = 10 * 1024 * 1024; // 10MB max response size

/**
 * MCP Sandbox Transport
 *
 * Implements MCP protocol transport using Cu.Sandbox for in-browser
 * JavaScript MCP servers. Communication happens via message passing
 * using Cu.exportFunction and Cu.cloneInto.
 */

export class MCPSandboxTransport extends MCPClient {
  constructor(serverCode, options = {}) {
    super({ clientId: options.serverId || "sandbox-server" });
    this.serverCode = serverCode;
    this.serverId = options.serverId || "sandbox-server";
    this.sandbox = null;
    this.responseHandlers = new Map();
    this.onConsole = options.onConsole || null;
    this.capabilityBridge = null;
  }

  /**
   * Transport-specific connection logic.
   * Initialize the sandbox and load the server code.
   *
   * @protected
   */
  async _connect() {
    // Validate code size before creating sandbox
    if (!this.serverCode || typeof this.serverCode !== "string") {
      throw new Error("Server code must be a non-empty string");
    }
    if (this.serverCode.length > MAX_CODE_SIZE) {
      throw new Error(
        `Server code exceeds maximum size of ${MAX_CODE_SIZE} bytes (got ${this.serverCode.length})`
      );
    }

    // Create sandbox with minimal privileges using null principal for isolation
    const principal = Services.scriptSecurityManager.createNullPrincipal({});

    this.sandbox = Cu.Sandbox(principal, {
      sandboxName: `MCP Server: ${this.clientId}`,
      wantXrays: true,
      wantGlobalProperties: [],
      wantComponents: false,
      wantExportHelpers: false,
    });

    // Inject a Promise polyfill into the sandbox since null principal sandboxes
    // don't have Promise by default
    Cu.evalInSandbox(
      `
      (function() {
        function Promise(executor) {
          this._state = 'pending';
          this._value = undefined;
          this._handlers = [];
          var self = this;

          function resolve(value) {
            if (self._state !== 'pending') return;
            self._state = 'fulfilled';
            self._value = value;
            self._handlers.forEach(function(h) {
              if (h.onFulfilled) h.onFulfilled(value);
            });
          }

          function reject(reason) {
            if (self._state !== 'pending') return;
            self._state = 'rejected';
            self._value = reason;
            self._handlers.forEach(function(h) {
              if (h.onRejected) h.onRejected(reason);
            });
          }

          try {
            executor(resolve, reject);
          } catch (e) {
            reject(e);
          }
        }

        Promise.prototype.then = function(onFulfilled, onRejected) {
          var self = this;
          return new Promise(function(resolve, reject) {
            function handle() {
              try {
                var value = self._value;
                if (self._state === 'fulfilled') {
                  resolve(onFulfilled ? onFulfilled(value) : value);
                } else if (self._state === 'rejected') {
                  if (onRejected) {
                    resolve(onRejected(value));
                  } else {
                    reject(value);
                  }
                }
              } catch (e) {
                reject(e);
              }
            }

            if (self._state === 'pending') {
              self._handlers.push({ onFulfilled: handle, onRejected: handle });
            } else {
              handle();
            }
          });
        };

        Promise.prototype.catch = function(onRejected) {
          return this.then(null, onRejected);
        };

        Promise.resolve = function(value) {
          return new Promise(function(resolve) { resolve(value); });
        };

        Promise.reject = function(reason) {
          return new Promise(function(_, reject) { reject(reason); });
        };

        globalThis.Promise = Promise;
      })();
      `,
      this.sandbox,
      "1.8",
      "moz-src://mcp/promise-polyfill.js",
      1
    );

    // Store reference to sandbox's Promise for use in wrapAsync
    this.SandboxPromise = this.sandbox.Promise;

    try {
      // Export message sending function to sandbox
      // This allows sandbox code to send responses back to us
      this.sandbox.sendToHost = Cu.exportFunction(message => {
        return this._handleSandboxMessage(message);
      }, this.sandbox);

      // Export console for debugging
      this.sandbox.console = Cu.cloneInto(
        {
          log: (...args) => {
            console.log(`[MCP Sandbox ${this.clientId}]`, ...args);
            if (this.onConsole) {
              this.onConsole("log", args);
            }
          },
          error: (...args) => {
            console.error(`[MCP Sandbox ${this.clientId}]`, ...args);
            if (this.onConsole) {
              this.onConsole("error", args);
            }
          },
          warn: (...args) => {
            console.warn(`[MCP Sandbox ${this.clientId}]`, ...args);
            if (this.onConsole) {
              this.onConsole("warn", args);
            }
          },
        },
        this.sandbox,
        { cloneFunctions: true }
      );

      // Export capability APIs based on server's profile
      this._exportCapabilityAPIs();

      // Load the MCP server code into the sandbox
      // Use moz-src:// scheme which passes Firefox's filename validation
      Cu.evalInSandbox(
        this.serverCode,
        this.sandbox,
        "1.8",
        `moz-src://mcp/sandbox/${this.clientId}.js`,
        1
      );

      // Verify the server exposed the required interface
      if (typeof this.sandbox.handleMessage !== "function") {
        throw new Error(
          "MCP server must expose a handleMessage(message) function"
        );
      }
    } catch (error) {
      // Extract message before nuking sandbox to avoid "dead object" error
      const errorMessage = String(error.message || error);

      // Clean up sandbox on error (fix #3)
      if (this.sandbox) {
        Cu.nukeSandbox(this.sandbox);
        this.sandbox = null;
      }
      throw new Error(errorMessage);
    }
  }

  /**
   * Transport-specific message sending.
   * Send request to sandbox and wait for response.
   *
   * @protected
   */
  async _sendRequest(message) {
    if (!this.sandbox) {
      throw new Error("Sandbox not initialized");
    }

    // Verify sandbox exposes handleMessage before proceeding
    if (typeof this.sandbox.handleMessage !== "function") {
      throw new Error(
        "Sandbox does not expose handleMessage function - server code may be invalid"
      );
    }

    return new Promise((resolve, reject) => {
      // Set up timeout to prevent memory leaks from unfulfilled responses
      // Default timeout is 30s, but parent class may override
      const timeoutMs = this.timeout || 30000;
      const timeoutId = setTimeout(() => {
        // Clean up handler and reject if no response received
        if (this.responseHandlers.has(message.id)) {
          this.responseHandlers.delete(message.id);
          reject(
            new Error(
              `Sandbox request timeout after ${timeoutMs}ms for method: ${message.method}`
            )
          );
        }
      }, timeoutMs);

      // Store response handler with timeout ID for cleanup
      // This ensures the handler is in place even if sandbox responds synchronously
      this.responseHandlers.set(message.id, { resolve, reject, timeoutId });

      try {
        // Clone message into sandbox
        const sandboxMessage = Cu.cloneInto(message, this.sandbox);

        // Call into sandbox - this may trigger synchronous response via sendToHost
        this.sandbox.handleMessage(sandboxMessage);
      } catch (error) {
        // Clean up handler and timeout on error
        const handler = this.responseHandlers.get(message.id);
        if (handler) {
          clearTimeout(handler.timeoutId);
          this.responseHandlers.delete(message.id);
        }
        reject(
          new Error(`Failed to send message to sandbox: ${error.message}`)
        );
      }
    });
  }

  /**
   * Transport-specific cleanup logic.
   * Destroy the sandbox and clean up resources.
   *
   * @protected
   */
  async _disconnect() {
    if (this.sandbox) {
      // Clear pending handlers and their timeouts
      for (const { reject, timeoutId } of this.responseHandlers.values()) {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        reject(new Error("Disconnected"));
      }
      this.responseHandlers.clear();

      // Destroy sandbox
      Cu.nukeSandbox(this.sandbox);
      this.sandbox = null;
    }
  }

  /**
   * Handle a message sent from the sandbox back to the host.
   * This is called when sandbox code invokes sendToHost().
   *
   * @param {object} sandboxMessage - Message from sandbox (in sandbox compartment)
   * @private
   */
  _handleSandboxMessage(sandboxMessage) {
    // Clone message out of sandbox into our context
    const message = Cu.cloneInto(sandboxMessage, {});

    // Validate response size to prevent memory exhaustion
    const messageSize = JSON.stringify(message).length;
    if (messageSize > MAX_RESPONSE_SIZE) {
      console.error(
        `[MCPSandboxTransport] Response too large: ${messageSize} bytes (max ${MAX_RESPONSE_SIZE})`
      );
      // If this is a response to a pending request, reject it
      if (message.id !== undefined && this.responseHandlers.has(message.id)) {
        const { reject, timeoutId } = this.responseHandlers.get(message.id);
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        this.responseHandlers.delete(message.id);
        reject(
          new Error(
            `Response too large: ${messageSize} bytes (max ${MAX_RESPONSE_SIZE})`
          )
        );
      }
      return;
    }

    // Handle JSON-RPC response
    if (message.id !== undefined && this.responseHandlers.has(message.id)) {
      const { resolve, reject, timeoutId } = this.responseHandlers.get(
        message.id
      );

      // Clear timeout and remove handler
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      this.responseHandlers.delete(message.id);

      if (message.error) {
        reject(
          new Error(message.error.message || "Unknown error from MCP server")
        );
      } else {
        resolve(message.result);
      }
      return;
    }

    // Handle notifications (no id field)
    if (message.id === undefined && message.method) {
      this._handleNotification(message);
      return;
    }

    console.warn(
      `[MCPSandboxTransport] Unexpected message from sandbox:`,
      message
    );
  }

  /**
   * Handle server-initiated notifications.
   *
   * @param {object} message - Notification message
   * @private
   */
  _handleNotification(message) {
    console.log(
      `[MCPSandboxTransport] Notification from ${this.clientId}:`,
      message.method,
      message.params
    );
  }

  /**
   * Export capability APIs to the sandbox based on the server's profile.
   * Creates wrapper functions that check permissions and call privileged APIs.
   *
   * @private
   */
  _exportCapabilityAPIs() {
    // Create gate with profile store
    const gate = new lazy.CapabilityGate(lazy.CapabilityProfileStore);

    // Create bridge for this server
    this.capabilityBridge = new lazy.CapabilityBridge(this.serverId, gate);

    // Get the APIs
    const apis = this.capabilityBridge.createAPIs();

    // Helper to wrap async functions for sandbox compatibility.
    // Creates a Promise in the sandbox's compartment so it can be awaited.
    const wrapAsync = fn => {
      return Cu.exportFunction((...args) => {
        // Create a new Promise using the sandbox's Promise polyfill
        return new this.SandboxPromise((resolve, reject) => {
          Promise.resolve(fn(...args))
            .then(result => {
              // Clone the result into the sandbox compartment
              if (result === undefined || result === null) {
                resolve(result);
              } else {
                resolve(Cu.cloneInto(result, this.sandbox));
              }
            })
            .catch(error => {
              // Clone error info into sandbox
              reject(
                Cu.cloneInto(
                  { message: String(error.message || error) },
                  this.sandbox
                )
              );
            });
        });
      }, this.sandbox);
    };

    // Export each API namespace to the sandbox
    this.sandbox.capabilities = Cu.cloneInto({}, this.sandbox);

    // Filesystem API
    this.sandbox.capabilities.fs = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.fs)) {
      this.sandbox.capabilities.fs[name] = wrapAsync(fn);
    }

    // Browser API (nested structure)
    this.sandbox.capabilities.browser = Cu.cloneInto({}, this.sandbox);

    this.sandbox.capabilities.browser.tabs = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.browser.tabs)) {
      this.sandbox.capabilities.browser.tabs[name] = wrapAsync(fn);
    }

    this.sandbox.capabilities.browser.history = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.browser.history)) {
      this.sandbox.capabilities.browser.history[name] = wrapAsync(fn);
    }

    this.sandbox.capabilities.browser.bookmarks = Cu.cloneInto(
      {},
      this.sandbox
    );
    for (const [name, fn] of Object.entries(apis.browser.bookmarks)) {
      this.sandbox.capabilities.browser.bookmarks[name] = wrapAsync(fn);
    }

    // Network API
    this.sandbox.capabilities.net = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.net)) {
      this.sandbox.capabilities.net[name] = wrapAsync(fn);
    }

    // Clipboard API
    this.sandbox.capabilities.clipboard = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.clipboard)) {
      this.sandbox.capabilities.clipboard[name] = wrapAsync(fn);
    }

    // Notifications API
    this.sandbox.capabilities.notifications = Cu.cloneInto({}, this.sandbox);
    for (const [name, fn] of Object.entries(apis.notifications)) {
      this.sandbox.capabilities.notifications[name] = wrapAsync(fn);
    }
  }
}
