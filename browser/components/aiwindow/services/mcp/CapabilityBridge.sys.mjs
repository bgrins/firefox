/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * CapabilityError - Thrown when a capability check fails.
 */
export class CapabilityError extends Error {
  constructor(capability, operation, reason) {
    super(`Permission denied: ${capability}.${operation} - ${reason}`);
    this.name = "CapabilityError";
    this.capability = capability;
    this.operation = operation;
    this.reason = reason;
    // Fix prototype chain for proper instanceof checks
    Object.setPrototypeOf(this, CapabilityError.prototype);
  }
}

/**
 * CapabilityBridge - Creates safe API wrappers that check permissions.
 *
 * Provides APIs to expose to sandboxed MCP servers. Each API method
 * checks permissions via CapabilityGate before executing.
 */
export class CapabilityBridge {
  #serverId;
  #gate;
  #auditLog = [];

  constructor(serverId, gate) {
    if (!serverId || typeof serverId !== "string") {
      throw new Error("serverId must be a non-empty string");
    }
    if (!gate) {
      throw new Error("gate is required");
    }
    this.#serverId = serverId;
    this.#gate = gate;
  }

  get serverId() {
    return this.#serverId;
  }

  get auditLog() {
    return [...this.#auditLog];
  }

  clearAuditLog() {
    this.#auditLog = [];
  }

  /**
   * Create all capability APIs to expose to a sandbox.
   *
   * @returns {object} Object with fs, browser, net, clipboard, notifications APIs
   */
  createAPIs() {
    return {
      fs: this.#createFilesystemAPI(),
      browser: this.#createBrowserAPI(),
      net: this.#createNetworkAPI(),
      clipboard: this.#createClipboardAPI(),
      notifications: this.#createNotificationsAPI(),
    };
  }

  /**
   * Export APIs into a Cu.Sandbox for use by MCP server code.
   *
   * @param {object} sandbox - The Cu.Sandbox to export APIs into
   */
  exportToSandbox(sandbox) {
    const apis = this.createAPIs();

    sandbox.capabilities = Cu.cloneInto(
      {
        fs: this.#wrapForSandbox(apis.fs, sandbox),
        browser: this.#wrapForSandbox(apis.browser, sandbox),
        net: this.#wrapForSandbox(apis.net, sandbox),
        clipboard: this.#wrapForSandbox(apis.clipboard, sandbox),
        notifications: this.#wrapForSandbox(apis.notifications, sandbox),
      },
      sandbox,
      { cloneFunctions: true }
    );
  }

  #wrapForSandbox(api, sandbox) {
    const wrapped = {};
    for (const [key, value] of Object.entries(api)) {
      if (typeof value === "function") {
        wrapped[key] = Cu.exportFunction(value, sandbox);
      } else if (typeof value === "object" && value !== null) {
        wrapped[key] = this.#wrapForSandbox(value, sandbox);
      } else {
        wrapped[key] = value;
      }
    }
    return wrapped;
  }

  #requirePermission(category, capability, operation, params = {}) {
    const result = this.#gate.checkPermission(
      this.#serverId,
      category,
      capability,
      operation,
      params
    );

    this.#auditLog.push({
      timestamp: Date.now(),
      serverId: this.#serverId,
      category,
      capability,
      operation,
      params: this.#sanitizeParams(params),
      allowed: result.allowed,
      reason: result.reason,
    });

    if (!result.allowed) {
      throw new CapabilityError(capability, operation, result.reason);
    }

    return result;
  }

  #sanitizeParams(params) {
    const sanitized = {};
    for (const [key, value] of Object.entries(params)) {
      if (typeof value === "string" && value.length > 200) {
        sanitized[key] = value.slice(0, 200) + "...";
      } else {
        sanitized[key] = value;
      }
    }
    return sanitized;
  }

  #createFilesystemAPI() {
    return {
      readFile: async path => {
        this.#requirePermission("system", "filesystem", "read", { path });
        return IOUtils.readUTF8(path);
      },

      readBinary: async path => {
        this.#requirePermission("system", "filesystem", "read", { path });
        return IOUtils.read(path);
      },

      writeFile: async (path, content) => {
        this.#requirePermission("system", "filesystem", "write", { path });
        if (typeof content === "string") {
          return IOUtils.writeUTF8(path, content);
        }
        return IOUtils.write(path, content);
      },

      appendFile: async (path, content) => {
        this.#requirePermission("system", "filesystem", "write", { path });
        if (typeof content === "string") {
          return IOUtils.writeUTF8(path, content, { mode: "append" });
        }
        return IOUtils.write(path, content, { mode: "append" });
      },

      exists: async path => {
        this.#requirePermission("system", "filesystem", "read", { path });
        return IOUtils.exists(path);
      },

      stat: async path => {
        this.#requirePermission("system", "filesystem", "read", { path });
        const info = await IOUtils.stat(path);
        return {
          type: info.type,
          size: info.size,
          creationTime: info.creationTime,
          lastModified: info.lastModified,
        };
      },

      listDir: async path => {
        this.#requirePermission("system", "filesystem", "read", { path });
        const children = await IOUtils.getChildren(path);
        return children.map(p => PathUtils.filename(p));
      },

      mkdir: async (path, options = {}) => {
        this.#requirePermission("system", "filesystem", "write", { path });
        return IOUtils.makeDirectory(path, options);
      },

      remove: async (path, options = {}) => {
        this.#requirePermission("system", "filesystem", "write", { path });
        return IOUtils.remove(path, options);
      },

      move: async (sourcePath, destPath) => {
        this.#requirePermission("system", "filesystem", "read", {
          path: sourcePath,
        });
        this.#requirePermission("system", "filesystem", "write", {
          path: destPath,
        });
        return IOUtils.move(sourcePath, destPath);
      },

      copy: async (sourcePath, destPath) => {
        this.#requirePermission("system", "filesystem", "read", {
          path: sourcePath,
        });
        this.#requirePermission("system", "filesystem", "write", {
          path: destPath,
        });
        return IOUtils.copy(sourcePath, destPath);
      },
    };
  }

  #createBrowserAPI() {
    return {
      tabs: {
        list: async () => {
          this.#requirePermission("browser", "tabs", "read");
          return this.#getTabList();
        },

        get: async tabId => {
          this.#requirePermission("browser", "tabs", "read");
          return this.#getTabById(tabId);
        },

        create: async url => {
          this.#requirePermission("browser", "tabs", "create");
          const validUrl = this.#validateUrl(url);
          const win = Services.wm.getMostRecentWindow("navigator:browser");
          if (!win || !win.gBrowser) {
            throw new Error("No browser window available");
          }
          const tab = win.gBrowser.addTab(validUrl, {
            triggeringPrincipal:
              Services.scriptSecurityManager.getSystemPrincipal(),
          });
          return this.#tabToInfo(tab);
        },

        navigate: async (tabId, url) => {
          this.#requirePermission("browser", "tabs", "navigate");
          const validUrl = this.#validateUrl(url);
          const tab = this.#findTabById(tabId);
          if (!tab) {
            throw new Error(`Tab not found: ${tabId}`);
          }
          tab.linkedBrowser.loadURI(Services.io.newURI(validUrl), {
            triggeringPrincipal:
              Services.scriptSecurityManager.getSystemPrincipal(),
          });
        },

        close: async tabId => {
          this.#requirePermission("browser", "tabs", "close");
          const tab = this.#findTabById(tabId);
          if (!tab) {
            throw new Error(`Tab not found: ${tabId}`);
          }
          const win = tab.ownerGlobal;
          win.gBrowser.removeTab(tab);
        },
      },

      history: {
        search: async (query, maxResults = 100) => {
          this.#requirePermission("browser", "history", "read");
          const results = await this.#searchHistory(query, maxResults);
          return results;
        },
      },

      bookmarks: {
        search: async query => {
          this.#requirePermission("browser", "bookmarks", "read");
          return this.#searchBookmarks(query);
        },

        create: async (title, url, parentGuid = null) => {
          this.#requirePermission("browser", "bookmarks", "write");
          const validUrl = this.#validateUrl(url);
          return this.#createBookmark(title, validUrl, parentGuid);
        },
      },
    };
  }

  #createNetworkAPI() {
    return {
      fetch: async (url, options = {}) => {
        this.#requirePermission("system", "network", "fetch", { url });

        const response = await fetch(url, {
          ...options,
          credentials: "omit",
          mode: "cors",
        });

        return {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          text: () => response.text(),
          json: () => response.json(),
        };
      },
    };
  }

  #createClipboardAPI() {
    return {
      read: async () => {
        this.#requirePermission("system", "clipboard", "read");
        const trans = Cc["@mozilla.org/widget/transferable;1"].createInstance(
          Ci.nsITransferable
        );
        trans.init(null);
        trans.addDataFlavor("text/plain");

        Services.clipboard.getData(trans, Ci.nsIClipboard.kGlobalClipboard);

        const data = {};
        const dataLen = {};
        try {
          trans.getTransferData("text/plain", data);
          if (data.value) {
            return data.value.QueryInterface(Ci.nsISupportsString).data;
          }
        } catch {
          // No text data available
        }
        return null;
      },

      write: async text => {
        this.#requirePermission("system", "clipboard", "write");
        const trans = Cc["@mozilla.org/widget/transferable;1"].createInstance(
          Ci.nsITransferable
        );
        trans.init(null);
        trans.addDataFlavor("text/plain");

        const str = Cc["@mozilla.org/supports-string;1"].createInstance(
          Ci.nsISupportsString
        );
        str.data = text;
        trans.setTransferData("text/plain", str);

        Services.clipboard.setData(trans, null, Ci.nsIClipboard.kGlobalClipboard);
      },
    };
  }

  #createNotificationsAPI() {
    return {
      show: async (title, options = {}) => {
        this.#requirePermission("system", "notifications", "show");

        const alertService = Cc[
          "@mozilla.org/alerts-service;1"
        ].getService(Ci.nsIAlertsService);

        const alert = Cc["@mozilla.org/alert-notification;1"].createInstance(
          Ci.nsIAlertNotification
        );

        alert.init(
          `mcp-${this.#serverId}-${Date.now()}`,
          options.icon || "",
          title,
          options.body || "",
          true,
          "",
          null,
          null,
          null,
          null,
          null,
          false,
          false
        );

        alertService.showAlert(alert);
      },
    };
  }

  #validateUrl(url) {
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) {
        throw new Error("Only http/https URLs allowed");
      }
      return parsed.href;
    } catch (e) {
      throw new Error(`Invalid URL: ${e.message}`);
    }
  }

  #getTabList() {
    const tabs = [];
    const windows = Services.wm.getEnumerator("navigator:browser");
    while (windows.hasMoreElements()) {
      const win = windows.getNext();
      if (win.gBrowser) {
        for (const tab of win.gBrowser.tabs) {
          tabs.push(this.#tabToInfo(tab));
        }
      }
    }
    return tabs;
  }

  #tabToInfo(tab) {
    const browser = tab.linkedBrowser;
    return {
      id: tab.linkedPanel,
      url: browser.currentURI?.spec || "",
      title: tab.label || "",
      active: tab.selected,
      pinned: tab.pinned,
      windowId: tab.ownerGlobal.__SSi || 0,
    };
  }

  #getTabById(tabId) {
    const tab = this.#findTabById(tabId);
    if (!tab) {
      return null;
    }
    return this.#tabToInfo(tab);
  }

  #findTabById(tabId) {
    const windows = Services.wm.getEnumerator("navigator:browser");
    while (windows.hasMoreElements()) {
      const win = windows.getNext();
      if (win.gBrowser) {
        for (const tab of win.gBrowser.tabs) {
          if (tab.linkedPanel === tabId) {
            return tab;
          }
        }
      }
    }
    return null;
  }

  async #searchHistory(query, maxResults) {
    const { PlacesUtils } = ChromeUtils.importESModule(
      "resource://gre/modules/PlacesUtils.sys.mjs"
    );

    const options = PlacesUtils.history.getNewQueryOptions();
    options.maxResults = maxResults;
    options.sortingMode =
      Ci.nsINavHistoryQueryOptions.SORT_BY_DATE_DESCENDING;

    const historyQuery = PlacesUtils.history.getNewQuery();
    if (query) {
      historyQuery.searchTerms = query;
    }

    const root = PlacesUtils.history.executeQuery(
      historyQuery,
      options
    ).root;
    root.containerOpen = true;

    const results = [];
    for (let i = 0; i < root.childCount; i++) {
      const node = root.getChild(i);
      results.push({
        url: node.uri,
        title: node.title,
        visitTime: node.time / 1000,
        visitCount: node.accessCount,
      });
    }

    root.containerOpen = false;
    return results;
  }

  async #searchBookmarks(query) {
    const { PlacesUtils } = ChromeUtils.importESModule(
      "resource://gre/modules/PlacesUtils.sys.mjs"
    );

    const results = await PlacesUtils.bookmarks.search({ query });
    return results.map(bm => ({
      guid: bm.guid,
      title: bm.title,
      url: bm.url?.href || "",
      parentGuid: bm.parentGuid,
      dateAdded: bm.dateAdded,
    }));
  }

  async #createBookmark(title, url, parentGuid) {
    const { PlacesUtils } = ChromeUtils.importESModule(
      "resource://gre/modules/PlacesUtils.sys.mjs"
    );

    const bookmark = await PlacesUtils.bookmarks.insert({
      parentGuid: parentGuid || PlacesUtils.bookmarks.unfiledGuid,
      title,
      url,
    });

    return {
      guid: bookmark.guid,
      title: bookmark.title,
      url: bookmark.url?.href || url,
      parentGuid: bookmark.parentGuid,
      dateAdded: bookmark.dateAdded,
    };
  }
}
