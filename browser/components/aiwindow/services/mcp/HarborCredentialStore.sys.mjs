/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * HarborCredentialStore - Secure storage for MCP server credentials
 *
 * Uses Firefox's Login Manager (nsILoginManager) to securely store
 * bearer tokens and other credentials for MCP HTTP servers.
 *
 * Credentials are stored with:
 * - hostname: "mcp://harbor" (pseudo-protocol to identify Harbor credentials)
 * - httpRealm: serverId (to identify which server the credential belongs to)
 * - username: "bearer" (credential type)
 * - password: the actual bearer token
 */

const HARBOR_ORIGIN = "mcp://harbor";

const nsLoginInfo = Components.Constructor(
  "@mozilla.org/login-manager/loginInfo;1",
  "nsILoginInfo",
  "init"
);

export const HarborCredentialStore = {
  /**
   * Store a bearer token for an MCP server.
   *
   * @param {string} serverId - The server ID
   * @param {string} bearerToken - The bearer token to store
   * @returns {Promise<void>}
   */
  async storeBearerToken(serverId, bearerToken) {
    if (!serverId || !bearerToken) {
      throw new Error("serverId and bearerToken are required");
    }

    // Remove any existing credential for this server
    await this.removeBearerToken(serverId);

    // Create and store the new login
    const loginInfo = new nsLoginInfo(
      HARBOR_ORIGIN,
      null, // formSubmitURL - null for non-form credentials
      serverId, // httpRealm - use serverId to identify the credential
      "bearer", // username - credential type
      bearerToken, // password - the actual token
      "", // usernameField
      "" // passwordField
    );

    await Services.logins.addLoginAsync(loginInfo);
  },

  /**
   * Retrieve a bearer token for an MCP server.
   *
   * @param {string} serverId - The server ID
   * @returns {string|null} The bearer token, or null if not found
   */
  getBearerToken(serverId) {
    if (!serverId) {
      return null;
    }

    const logins = Services.logins.findLogins(HARBOR_ORIGIN, null, serverId);

    for (const login of logins) {
      if (login.username === "bearer") {
        return login.password;
      }
    }

    return null;
  },

  /**
   * Remove a bearer token for an MCP server.
   *
   * @param {string} serverId - The server ID
   * @returns {Promise<void>}
   */
  async removeBearerToken(serverId) {
    if (!serverId) {
      return;
    }

    const logins = Services.logins.findLogins(HARBOR_ORIGIN, null, serverId);

    for (const login of logins) {
      if (login.username === "bearer") {
        Services.logins.removeLogin(login);
      }
    }
  },

  /**
   * Check if a bearer token exists for an MCP server.
   *
   * @param {string} serverId - The server ID
   * @returns {boolean} True if a token exists
   */
  hasBearerToken(serverId) {
    return this.getBearerToken(serverId) !== null;
  },

  /**
   * Remove all Harbor credentials.
   * Use with caution - this removes credentials for all MCP servers.
   *
   * @returns {Promise<void>}
   */
  async removeAllCredentials() {
    const logins = Services.logins.findLogins(HARBOR_ORIGIN, null, "");

    for (const login of logins) {
      Services.logins.removeLogin(login);
    }
  },
};
