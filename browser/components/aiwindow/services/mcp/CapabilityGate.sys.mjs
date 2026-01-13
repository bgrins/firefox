/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// PathUtils is a global in system modules

// Paths that are always denied regardless of configuration
const DEFAULT_DENY_PATTERNS = [
  "**/.env",
  "**/.env.*",
  "**/*.key",
  "**/*.pem",
  "**/credentials*",
  "**/.ssh/**",
  "**/.gnupg/**",
  "**/.aws/**",
  "**/id_rsa*",
  "**/id_ed25519*",
];

// Maximum allowed complexity for glob patterns
const MAX_PATTERN_LENGTH = 200;
const MAX_GLOB_STARS = 10;

// Valid server ID pattern (alphanumeric, underscore, hyphen)
const SERVER_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

/**
 * CapabilityGate - Central permission checker for MCP server capabilities.
 *
 * Enforces what operations an MCP server is allowed to perform, regardless
 * of what tools it exposes. This is the security boundary.
 */
export class CapabilityGate {
  #profileStore;
  #profileCache = new Map();

  constructor(profileStore = null) {
    this.#profileStore = profileStore;
  }

  /**
   * Check if an operation is allowed for a server.
   *
   * @param {string} serverId - The server identifier
   * @param {string} category - "system" or "browser"
   * @param {string} capability - The capability name (e.g., "filesystem", "tabs")
   * @param {string} operation - The operation (e.g., "read", "write", "create")
   * @param {object} params - Operation-specific parameters
   * @returns {{ allowed: boolean, reason: string|null }}
   */
  checkPermission(serverId, category, capability, operation, params = {}) {
    // Validate server ID to prevent pref injection
    if (!this.#validateServerId(serverId)) {
      return { allowed: false, reason: "Invalid server ID" };
    }

    const profile = this.#getProfile(serverId);

    if (category === "system") {
      return this.#checkSystemCapability(
        profile,
        capability,
        operation,
        params
      );
    }
    if (category === "browser") {
      return this.#checkBrowserCapability(
        profile,
        capability,
        operation,
        params
      );
    }

    return { allowed: false, reason: "Unknown capability category" };
  }

  /**
   * Invalidate cached profile for a server.
   * Call this when a profile is modified externally.
   *
   * @param {string} serverId - The server identifier
   */
  invalidateCache(serverId) {
    this.#profileCache.delete(serverId);
  }

  /**
   * Clear all cached profiles.
   */
  clearCache() {
    this.#profileCache.clear();
  }

  // Private methods

  #validateServerId(serverId) {
    if (!serverId || typeof serverId !== "string") {
      return false;
    }
    if (serverId.length > 100) {
      return false;
    }
    return SERVER_ID_PATTERN.test(serverId);
  }

  #getProfile(serverId) {
    if (!this.#profileCache.has(serverId)) {
      const loaded = this.#profileStore?.load(serverId);
      this.#profileCache.set(serverId, loaded || null);
    }
    return this.#profileCache.get(serverId) || this.#getDefaultProfile();
  }

  #getDefaultProfile() {
    return {
      level: "isolated",
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
    };
  }

  #checkSystemCapability(profile, capability, operation, params) {
    const cap = profile.system?.[capability];

    switch (capability) {
      case "filesystem":
        return this.#checkFilesystem(cap, operation, params.path);
      case "network":
        return this.#checkNetwork(cap, params.url);
      case "subprocess":
        return this.#checkSubprocess(cap, params.command);
      case "clipboard":
        return this.#checkSimpleCapability(cap, operation, "Clipboard");
      case "notifications":
        return {
          allowed: cap?.enabled === true,
          reason: cap?.enabled ? null : "Notifications not enabled",
        };
      default:
        return {
          allowed: false,
          reason: `Unknown system capability: ${capability}`,
        };
    }
  }

  #checkBrowserCapability(profile, capability, operation, params) {
    // Check private browsing isolation first
    if (params?.isPrivate && !profile.browser?.allowPrivateBrowsing) {
      return {
        allowed: false,
        reason: "Private browsing access not permitted",
      };
    }

    const cap = profile.browser?.[capability];
    if (!cap) {
      return { allowed: false, reason: `${capability} not configured` };
    }

    // Simple boolean check for the operation
    const allowed = cap[operation] === true;
    return {
      allowed,
      reason: allowed ? null : `${capability}.${operation} not permitted`,
    };
  }

  #checkFilesystem(cap, operation, path) {
    if (!cap?.enabled) {
      return { allowed: false, reason: "Filesystem access disabled" };
    }

    if (!path || typeof path !== "string") {
      return { allowed: false, reason: "Invalid path" };
    }

    // Normalize and validate path
    const normalized = this.#normalizePath(path);
    if (!normalized.valid) {
      return { allowed: false, reason: normalized.reason };
    }
    const normalizedPath = normalized.path;

    // Check deny patterns first (highest priority)
    const denyPatterns = [...DEFAULT_DENY_PATTERNS, ...(cap.deny || [])];
    for (const pattern of denyPatterns) {
      const match = this.#matchGlob(normalizedPath, pattern);
      if (match.error) {
        return { allowed: false, reason: "Invalid deny pattern" };
      }
      if (match.matches) {
        return { allowed: false, reason: "Access denied" };
      }
    }

    // Check allow patterns
    const allowList = operation === "read" ? cap.read : cap.write;
    if (!Array.isArray(allowList) || allowList.length === 0) {
      return { allowed: false, reason: `No ${operation} paths configured` };
    }

    for (const allowedPath of allowList) {
      const withinResult = this.#isWithinAllowedPath(
        normalizedPath,
        allowedPath
      );
      if (withinResult.error) {
        continue; // Skip invalid patterns
      }
      if (withinResult.within) {
        return { allowed: true, reason: null };
      }
    }

    return { allowed: false, reason: "Path not in allowlist" };
  }

  #checkNetwork(cap, url) {
    if (!cap?.enabled) {
      return { allowed: false, reason: "Network access disabled" };
    }

    if (!url || typeof url !== "string") {
      return { allowed: false, reason: "Invalid URL" };
    }

    let parsedUrl;
    try {
      parsedUrl = new URL(url);
    } catch {
      return { allowed: false, reason: "Invalid URL format" };
    }

    // Only allow http/https
    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
      return { allowed: false, reason: "Only http/https URLs allowed" };
    }

    // Check if private network access is denied
    if (cap.denyPrivate !== false) {
      if (this.#isPrivateHost(parsedUrl.hostname)) {
        return { allowed: false, reason: "Private network access denied" };
      }
    }

    // Check host allowlist
    const allowedHosts = cap.allowedHosts || [];
    if (allowedHosts.length === 0) {
      return { allowed: false, reason: "No allowed hosts configured" };
    }

    for (const pattern of allowedHosts) {
      if (this.#matchHostPattern(parsedUrl.hostname, pattern)) {
        return { allowed: true, reason: null };
      }
    }

    return { allowed: false, reason: "Host not in allowlist" };
  }

  // SECURITY NOTE: Subprocess execution is intentionally NOT implemented in
  // CapabilityBridge. This permission check exists for future use but any
  // implementation must:
  // 1. Use array-based command execution (not string parsing)
  // 2. Validate all arguments, not just the executable name
  // 3. Undergo thorough security review
  // The current check is conservative but insufficient for safe subprocess execution.
  #checkSubprocess(cap, command) {
    // Subprocess is disabled by default and should remain so until a secure
    // implementation is added to CapabilityBridge.
    if (!cap?.enabled) {
      return { allowed: false, reason: "Subprocess execution disabled" };
    }

    if (!command || typeof command !== "string") {
      return { allowed: false, reason: "Invalid command" };
    }

    // Reject any command containing shell metacharacters
    const shellMetachars = /[;&|`$()<>!\\'"]/;
    if (shellMetachars.test(command)) {
      return { allowed: false, reason: "Command contains shell metacharacters" };
    }

    // Extract the executable name (first word)
    const executable = command.split(/\s+/)[0];
    const baseName = executable.split("/").pop();

    // Check shell denial
    const shells = [
      "sh",
      "bash",
      "zsh",
      "fish",
      "csh",
      "tcsh",
      "cmd",
      "powershell",
      "pwsh",
    ];
    if (cap.denyShell !== false && shells.includes(baseName.toLowerCase())) {
      return { allowed: false, reason: "Shell execution denied" };
    }

    // Check command allowlist
    const allowedCommands = cap.allowedCommands || [];
    if (allowedCommands.length === 0) {
      return { allowed: false, reason: "No allowed commands configured" };
    }

    if (allowedCommands.includes(baseName)) {
      return { allowed: true, reason: null };
    }

    return { allowed: false, reason: "Command not in allowlist" };
  }

  #checkSimpleCapability(cap, operation, name) {
    if (!cap) {
      return { allowed: false, reason: `${name} not configured` };
    }
    const allowed = cap[operation] === true;
    return {
      allowed,
      reason: allowed ? null : `${name} ${operation} not permitted`,
    };
  }

  #normalizePath(path) {
    if (!path || typeof path !== "string") {
      return { valid: false, reason: "Path must be a non-empty string" };
    }

    // Reject null bytes
    if (path.includes("\0")) {
      return { valid: false, reason: "Path contains null byte" };
    }

    // Must be absolute path
    if (!path.startsWith("/")) {
      return { valid: false, reason: "Path must be absolute" };
    }

    // Normalize the path manually to avoid PathUtils.normalize requiring existing dirs
    const parts = path.split("/");
    const normalized = [];

    for (const part of parts) {
      if (part === "" || part === ".") {
        continue;
      }
      if (part === "..") {
        if (normalized.length > 0) {
          normalized.pop();
        }
        // If trying to go above root, that's invalid
        // (normalized is empty means we're at root)
      } else {
        normalized.push(part);
      }
    }

    const result = "/" + normalized.join("/");

    // Final check: no remaining .. components
    if (result.includes("..")) {
      return { valid: false, reason: "Path traversal detected" };
    }

    return { valid: true, path: result };
  }

  #matchGlob(path, pattern) {
    // Validate pattern complexity to prevent ReDoS
    if (pattern.length > MAX_PATTERN_LENGTH) {
      return { error: true, reason: "Pattern too long" };
    }

    const starCount = (pattern.match(/\*/g) || []).length;
    if (starCount > MAX_GLOB_STARS) {
      return { error: true, reason: "Pattern too complex" };
    }

    try {
      // Convert glob pattern to regex
      // ** matches any characters including /
      // * matches any characters except /
      let regexStr = pattern
        .replace(/[.+^${}()|[\]\\]/g, "\\$&") // Escape regex special chars
        .replace(/\*\*/g, "<<<GLOBSTAR>>>")
        .replace(/\*/g, "[^/]*")
        .replace(/<<<GLOBSTAR>>>/g, ".*")
        .replace(/\?/g, "[^/]");

      const regex = new RegExp(`^${regexStr}$`);
      const matches = regex.test(path);
      return { matches, error: false };
    } catch {
      return { error: true, reason: "Invalid pattern" };
    }
  }

  #isWithinAllowedPath(targetPath, allowedPath) {
    // Normalize the allowed path
    const normalizedAllowed = this.#normalizePath(allowedPath);
    if (!normalizedAllowed.valid) {
      return { error: true };
    }

    // If allowed path contains glob, use glob matching
    if (allowedPath.includes("*")) {
      const match = this.#matchGlob(targetPath, allowedPath);
      return { within: match.matches, error: match.error };
    }

    const basePath = normalizedAllowed.path;

    // Check if target is exactly the allowed path or within it
    if (targetPath === basePath) {
      return { within: true, error: false };
    }

    // Check if target is within the allowed directory
    // Must use proper path separator handling
    const baseWithSep = basePath.endsWith("/") ? basePath : basePath + "/";
    if (targetPath.startsWith(baseWithSep)) {
      return { within: true, error: false };
    }

    return { within: false, error: false };
  }

  #isPrivateHost(hostname) {
    // Check for localhost
    if (
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      hostname === "::1"
    ) {
      return true;
    }

    // Check for private IP ranges
    // 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
    const ipv4Match = hostname.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
    if (ipv4Match) {
      const [, a, b] = ipv4Match.map(Number);
      if (a === 10) {
        return true;
      }
      if (a === 172 && b >= 16 && b <= 31) {
        return true;
      }
      if (a === 192 && b === 168) {
        return true;
      }
      if (a === 169 && b === 254) {
        return true; // Link-local
      }
    }

    // Check for .local domains
    if (hostname.endsWith(".local")) {
      return true;
    }

    return false;
  }

  #matchHostPattern(hostname, pattern) {
    // Exact match
    if (hostname === pattern) {
      return true;
    }

    // Wildcard subdomain match: *.example.com matches foo.example.com
    if (pattern.startsWith("*.")) {
      const baseDomain = pattern.slice(2);
      if (hostname === baseDomain) {
        return true; // *.example.com also matches example.com
      }
      if (hostname.endsWith("." + baseDomain)) {
        return true;
      }
    }

    return false;
  }
}
