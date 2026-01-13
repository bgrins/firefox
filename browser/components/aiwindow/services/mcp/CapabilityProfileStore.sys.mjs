/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const PREF_PREFIX = "browser.aiwindow.harbor.capabilities.";

// Valid server ID pattern (matches CapabilityGate)
const SERVER_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

// Current schema version for migrations
const SCHEMA_VERSION = 1;

// Capability levels with their default profiles
const CAPABILITY_LEVELS = {
  isolated: {
    description: "No system or browser access. Safe for pure computation.",
    system: {
      filesystem: { enabled: false, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: {
        read: false,
        navigate: false,
        create: false,
        close: false,
        captureScreenshot: false,
      },
      history: { read: false, write: false },
      bookmarks: { read: false, write: false },
      downloads: { read: false, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  },

  "browser-readonly": {
    description: "Read-only browser access. Can list tabs, search history.",
    system: {
      filesystem: { enabled: false, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: false },
    },
    browser: {
      tabs: {
        read: true,
        navigate: false,
        create: false,
        close: false,
        captureScreenshot: false,
      },
      history: { read: true, write: false },
      bookmarks: { read: true, write: false },
      downloads: { read: true, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  },

  "browser-full": {
    description:
      "Full browser access except cookies and script injection. Browser automation.",
    system: {
      filesystem: { enabled: false, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: false, write: false },
      notifications: { enabled: true },
    },
    browser: {
      tabs: {
        read: true,
        navigate: true,
        create: true,
        close: true,
        captureScreenshot: true,
      },
      history: { read: true, write: true },
      bookmarks: { read: true, write: true },
      downloads: { read: true, initiate: true, manage: true },
      cookies: { read: false, write: false },
      storage: { read: true, write: true },
      activeTab: { readContent: true, executeScript: false },
      allowPrivateBrowsing: false,
    },
  },

  workspace: {
    description:
      "Filesystem access to a project directory. Good for code editing.",
    system: {
      filesystem: { enabled: true, read: [], write: [], deny: [] },
      network: { enabled: false, allowedHosts: [], denyPrivate: true },
      subprocess: { enabled: false, allowedCommands: [], denyShell: true },
      clipboard: { read: true, write: true },
      notifications: { enabled: true },
    },
    browser: {
      tabs: {
        read: false,
        navigate: false,
        create: false,
        close: false,
        captureScreenshot: false,
      },
      history: { read: false, write: false },
      bookmarks: { read: false, write: false },
      downloads: { read: false, initiate: false, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: false, executeScript: false },
      allowPrivateBrowsing: false,
    },
  },

  developer: {
    description:
      "Filesystem + subprocess + browser read. Full dev environment.",
    system: {
      filesystem: { enabled: true, read: [], write: [], deny: [] },
      network: { enabled: true, allowedHosts: ["*"], denyPrivate: false },
      subprocess: { enabled: true, allowedCommands: [], denyShell: true },
      clipboard: { read: true, write: true },
      notifications: { enabled: true },
    },
    browser: {
      tabs: {
        read: true,
        navigate: false,
        create: true,
        close: false,
        captureScreenshot: true,
      },
      history: { read: true, write: false },
      bookmarks: { read: true, write: false },
      downloads: { read: true, initiate: true, manage: false },
      cookies: { read: false, write: false },
      storage: { read: false, write: false },
      activeTab: { readContent: true, executeScript: false },
      allowPrivateBrowsing: false,
    },
  },
};

/**
 * CapabilityProfileStore - Persistence layer for capability profiles.
 *
 * Stores profiles in Firefox preferences. Each server has its own profile
 * keyed by server ID.
 */
export const CapabilityProfileStore = {
  /**
   * Load a capability profile for a server.
   *
   * @param {string} serverId - The server identifier
   * @returns {object|null} The profile or null if not found
   */
  load(serverId) {
    if (!this._validateServerId(serverId)) {
      return null;
    }

    try {
      const json = Services.prefs.getStringPref(
        `${PREF_PREFIX}${serverId}`,
        ""
      );
      if (!json) {
        return null;
      }

      const profile = JSON.parse(json);
      if (!this._validateProfile(profile)) {
        console.error(
          `[CapabilityProfileStore] Invalid profile for ${serverId}`
        );
        return null;
      }

      return profile;
    } catch (error) {
      console.error(
        `[CapabilityProfileStore] Failed to load profile for ${serverId}:`,
        error
      );
      return null;
    }
  },

  /**
   * Save a capability profile for a server.
   *
   * @param {string} serverId - The server identifier
   * @param {object} profile - The profile to save
   * @throws {Error} If serverId or profile is invalid
   */
  save(serverId, profile) {
    if (!this._validateServerId(serverId)) {
      throw new Error("Invalid server ID");
    }

    if (!this._validateProfile(profile)) {
      throw new Error("Invalid profile structure");
    }

    const toSave = {
      ...profile,
      version: SCHEMA_VERSION,
      updatedAt: Date.now(),
    };

    try {
      Services.prefs.setStringPref(
        `${PREF_PREFIX}${serverId}`,
        JSON.stringify(toSave)
      );
    } catch (error) {
      console.error(
        `[CapabilityProfileStore] Failed to save profile for ${serverId}:`,
        error
      );
      throw error;
    }
  },

  /**
   * Delete a capability profile for a server.
   *
   * @param {string} serverId - The server identifier
   * @returns {boolean} True if deleted, false if not found or invalid
   */
  delete(serverId) {
    if (!this._validateServerId(serverId)) {
      return false;
    }

    try {
      if (Services.prefs.prefHasUserValue(`${PREF_PREFIX}${serverId}`)) {
        Services.prefs.clearUserPref(`${PREF_PREFIX}${serverId}`);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  /**
   * List all server IDs that have saved profiles.
   *
   * @returns {string[]} Array of server IDs
   */
  listServerIds() {
    const serverIds = [];
    try {
      const prefBranch = Services.prefs.getBranch(PREF_PREFIX);
      const children = prefBranch.getChildList("");
      for (const name of children) {
        if (this._validateServerId(name)) {
          serverIds.push(name);
        }
      }
    } catch (error) {
      console.error(
        "[CapabilityProfileStore] Failed to list profiles:",
        error
      );
    }
    return serverIds;
  },

  /**
   * Get the default profile for a capability level.
   *
   * @param {string} level - The capability level name
   * @returns {object|null} The default profile or null if level unknown
   */
  getDefaultProfile(level) {
    const template = CAPABILITY_LEVELS[level];
    if (!template) {
      return null;
    }

    return {
      level,
      version: SCHEMA_VERSION,
      system: JSON.parse(JSON.stringify(template.system)),
      browser: JSON.parse(JSON.stringify(template.browser)),
    };
  },

  /**
   * Get all available capability level names.
   *
   * @returns {string[]} Array of level names
   */
  getAvailableLevels() {
    return Object.keys(CAPABILITY_LEVELS);
  },

  /**
   * Get description for a capability level.
   *
   * @param {string} level - The capability level name
   * @returns {string|null} Description or null if level unknown
   */
  getLevelDescription(level) {
    return CAPABILITY_LEVELS[level]?.description || null;
  },

  /**
   * Create a profile from a level with custom modifications.
   *
   * @param {string} level - Base capability level
   * @param {object} customizations - Custom overrides
   * @returns {object} The customized profile
   */
  createCustomProfile(level, customizations = {}) {
    const base = this.getDefaultProfile(level) || this.getDefaultProfile("isolated");

    const profile = {
      ...base,
      level: "custom",
    };

    // Apply system customizations
    if (customizations.system) {
      for (const [cap, settings] of Object.entries(customizations.system)) {
        if (profile.system[cap]) {
          profile.system[cap] = { ...profile.system[cap], ...settings };
        }
      }
    }

    // Apply browser customizations
    if (customizations.browser) {
      for (const [cap, settings] of Object.entries(customizations.browser)) {
        if (profile.browser[cap]) {
          profile.browser[cap] = { ...profile.browser[cap], ...settings };
        }
      }
    }

    return profile;
  },

  /**
   * Clear all stored profiles (for testing).
   */
  clearAll() {
    for (const serverId of this.listServerIds()) {
      this.delete(serverId);
    }
  },

  // Private methods

  _validateServerId(serverId) {
    if (!serverId || typeof serverId !== "string") {
      return false;
    }
    if (serverId.length > 100) {
      return false;
    }
    return SERVER_ID_PATTERN.test(serverId);
  },

  _validateProfile(profile) {
    if (!profile || typeof profile !== "object") {
      return false;
    }

    // Must have level
    if (!profile.level || typeof profile.level !== "string") {
      return false;
    }

    // Must have system object
    if (!profile.system || typeof profile.system !== "object") {
      return false;
    }

    // Must have browser object
    if (!profile.browser || typeof profile.browser !== "object") {
      return false;
    }

    // Validate system capabilities
    if (!this._validateSystemCapabilities(profile.system)) {
      return false;
    }

    // Validate browser capabilities
    if (!this._validateBrowserCapabilities(profile.browser)) {
      return false;
    }

    return true;
  },

  _validateSystemCapabilities(system) {
    // filesystem
    if (system.filesystem) {
      const fs = system.filesystem;
      if (typeof fs.enabled !== "boolean") {
        return false;
      }
      if (fs.read && !Array.isArray(fs.read)) {
        return false;
      }
      if (fs.write && !Array.isArray(fs.write)) {
        return false;
      }
      if (fs.deny && !Array.isArray(fs.deny)) {
        return false;
      }
    }

    // network
    if (system.network) {
      const net = system.network;
      if (typeof net.enabled !== "boolean") {
        return false;
      }
      if (net.allowedHosts && !Array.isArray(net.allowedHosts)) {
        return false;
      }
    }

    // subprocess
    if (system.subprocess) {
      const proc = system.subprocess;
      if (typeof proc.enabled !== "boolean") {
        return false;
      }
      if (proc.allowedCommands && !Array.isArray(proc.allowedCommands)) {
        return false;
      }
    }

    return true;
  },

  _validateBrowserCapabilities(browser) {
    // All browser capability objects should have boolean values
    for (const [capName, cap] of Object.entries(browser)) {
      if (capName === "allowPrivateBrowsing") {
        if (typeof cap !== "boolean") {
          return false;
        }
        continue;
      }

      if (!cap || typeof cap !== "object") {
        return false;
      }

      for (const [opName, value] of Object.entries(cap)) {
        if (typeof value !== "boolean") {
          return false;
        }
      }
    }

    return true;
  },
};
