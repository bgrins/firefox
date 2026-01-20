/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const { clearTimeout, setTimeout } = ChromeUtils.importESModule(
  "resource://gre/modules/Timer.sys.mjs"
);

/**
 * Utility functions for Harbor that need to run in a privileged context.
 */
export const HarborUtils = {
  /**
   * Check if an Ollama-compatible endpoint is reachable.
   * Runs from privileged context to bypass CSP restrictions.
   *
   * @param {string} endpoint - The configured endpoint (e.g., "http://localhost:11434/v1")
   * @returns {Promise<{status: string, modelCount?: number}>}
   */
  async checkEndpointStatus(endpoint) {
    try {
      // For Ollama endpoints, check /api/tags to verify connectivity
      // The /v1 endpoint returns 404 on GET, so we need the base URL
      const baseUrl = endpoint.replace(/\/v1\/?$/, "");
      const tagsUrl = `${baseUrl}/api/tags`;

      // Create abort controller with manual timeout (AbortSignal.timeout needs window)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await fetch(tagsUrl, {
          method: "GET",
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          const data = await response.json();
          const models = (data.models || []).map(m => m.name || m.model);
          return { status: "connected", modelCount: models.length, models };
        }
        // Server responded but endpoint not available - still "up"
        return { status: "connected", models: [] };
      } finally {
        clearTimeout(timeoutId);
      }
    } catch (error) {
      if (error.name === "AbortError") {
        return { status: "timeout" };
      }
      return { status: "offline", error: `${error.name}: ${error.message}` };
    }
  },
};
