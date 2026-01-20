/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import { MCPClient } from "moz-src:///browser/components/aiwindow/services/mcp/MCPClient.sys.mjs";
import { setTimeout } from "resource://gre/modules/Timer.sys.mjs";

const lazy = {};

ChromeUtils.defineESModuleGetters(lazy, {
  AppConstants: "resource://gre/modules/AppConstants.sys.mjs",
});

// Maximum response size (10MB) to prevent memory exhaustion
const MAX_RESPONSE_SIZE = 10 * 1024 * 1024;

/**
 *
 */
export class MCPHttpTransport extends MCPClient {
  constructor(url, options = {}) {
    super({
      clientId: options.clientId || "firefox-aiwindow",
      timeout: options.timeout || 30000,
    });
    this.url = url;
    this.bearerToken = options.bearerToken;
    this.abortController = null; // Fix #16: Track requests for abort
    this.maxRetries = options.maxRetries || 3; // Fix #17: Retry logic
    this.retryDelay = options.retryDelay || 1000; // 1 second between retries
  }

  async _connect() {
    let urlObj;
    try {
      urlObj = new URL(this.url);
    } catch (error) {
      throw new Error(`Invalid URL: ${error.message}`);
    }

    // Security check: require HTTPS in production unless explicitly allowed
    if (
      urlObj.protocol !== "https:" &&
      !Services.prefs.getBoolPref("browser.ml.mcp.allowInsecure", false) &&
      lazy.AppConstants.RELEASE_OR_BETA
    ) {
      throw new Error(
        "MCP HTTP servers require HTTPS in release builds. Set browser.ml.mcp.allowInsecure=true to override (not recommended)."
      );
    }

    // Warn about insecure connections in all builds
    if (urlObj.protocol !== "https:") {
      console.warn(
        `[MCPHttpTransport] Using insecure HTTP connection to ${this.url}`
      );
    }
  }

  async _sendRequest(message) {
    // Fix #17: Retry logic for transient network failures
    let lastError;
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await this._sendRequestOnce(message);
      } catch (error) {
        lastError = error;
        // Don't retry on non-network errors or final attempt
        if (
          attempt === this.maxRetries ||
          error.message.includes("Response ID mismatch") ||
          error.message.includes("Invalid JSON") ||
          error.message.includes("Expected JSON response")
        ) {
          throw error;
        }
        // Wait before retry with exponential backoff
        await new Promise(resolve =>
          setTimeout(resolve, this.retryDelay * Math.pow(2, attempt))
        );
      }
    }
    throw lastError;
  }

  async _sendRequestOnce(message) {
    // MCP Streamable HTTP transport headers per spec
    const headers = {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      "MCP-Protocol-Version": "2025-03-26",
    };

    // Add bearer token if configured
    if (this.bearerToken) {
      headers.Authorization = `Bearer ${this.bearerToken}`;
    }

    // Fix #16: Create abort controller for this request
    this.abortController = new AbortController();

    try {
      const response = await fetch(this.url, {
        method: "POST",
        headers,
        body: JSON.stringify(message),
        credentials: "omit", // Don't send cookies for security
        mode: "cors", // Enforce CORS
        redirect: "follow",
        referrerPolicy: "no-referrer",
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Fix #10: Check response size BEFORE reading
      const contentLength = response.headers.get("content-length");
      if (contentLength) {
        const size = parseInt(contentLength);
        if (size > MAX_RESPONSE_SIZE) {
          throw new Error(
            `Response too large: ${size} bytes (max ${MAX_RESPONSE_SIZE})`
          );
        }
      }

      // Check content-type - MCP supports both JSON and SSE
      const contentType = response.headers.get("content-type") || "";
      const isJson = contentType.toLowerCase().includes("application/json");
      const isSSE = contentType.toLowerCase().includes("text/event-stream");
      if (!isJson && !isSSE) {
        throw new Error(`Expected JSON or SSE response, got ${contentType}`);
      }

      // Read response with size limit
      const text = await response.text();
      if (text.length > MAX_RESPONSE_SIZE) {
        throw new Error(
          `Response too large: ${text.length} bytes (max ${MAX_RESPONSE_SIZE})`
        );
      }

      // Parse response - handle both JSON and SSE formats
      let data;
      try {
        if (isSSE) {
          // SSE format: extract JSON from "data:" lines
          const dataMatch = text.match(/^data:\s*(.+)$/m);
          if (dataMatch) {
            data = JSON.parse(dataMatch[1]);
          } else {
            throw new Error("Invalid SSE response - no data line found");
          }
        } else {
          data = JSON.parse(text);
        }
      } catch (parseError) {
        throw new Error(`Invalid JSON response: ${parseError.message}`);
      }

      if (data.error) {
        throw new Error(data.error.message || "Unknown error from MCP server");
      }

      if (data.id !== message.id) {
        throw new Error(
          `Response ID mismatch: expected ${message.id}, got ${data.id}`
        );
      }

      return data.result;
    } finally {
      this.abortController = null;
    }
  }

  async _disconnect() {
    // Fix #16: Abort in-flight requests
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}
