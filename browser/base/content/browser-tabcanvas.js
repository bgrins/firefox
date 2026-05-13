/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

var { InfiniteCanvas } = ChromeUtils.importESModule(
  "chrome://browser/content/tabcanvas/canvas-engine.mjs",
  { global: "current" }
);

/**
 * TabCanvas - Browser chrome adapter for InfiniteCanvas.
 * Connects gBrowser tabs to canvas nodes with thumbnails.
 */
var TabCanvas = {
  _overlay: null,
  _canvas: null,
  _active: false,
  _initialized: false,

  // Map tab -> canvas node id
  _tabToId: new WeakMap(),
  _idToTab: new Map(),

  get active() {
    return this._active;
  },

  init() {
    this._overlay = document.getElementById("tab-canvas-overlay");
    let container = document.getElementById("tab-canvas-inner");

    this._canvas = new InfiniteCanvas(container, {
      gridSize: 8,
      snapEnabled: true,
    });

    this._canvas.on("node-dblclick", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (tab) {
        gBrowser.selectedTab = tab;
        this.hide();
      }
    });

    this._canvas.on("node-click", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (tab) {
        gBrowser.selectedTab = tab;
      }
    });

    this._canvas.on("node-delete", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (tab) {
        gBrowser.removeTab(tab);
      }
    });

    this._canvas.on("escape", () => {
      if (this._canvas.getSelection().length === 0) {
        this.hide();
      }
    });

    gBrowser.tabContainer.addEventListener("TabOpen", this);
    gBrowser.tabContainer.addEventListener("TabClose", this);
    gBrowser.tabContainer.addEventListener("TabAttrModified", this);
    gBrowser.tabContainer.addEventListener("TabSelect", this);

    // Capture phase to intercept before XUL key handlers
    document.addEventListener("keydown", this, true);
  },

  handleEvent(event) {
    switch (event.type) {
      case "keydown":
        this._onKeyDown(event);
        break;
      case "TabOpen":
        this._onTabOpen(event);
        break;
      case "TabClose":
        this._onTabClose(event);
        break;
      case "TabAttrModified":
        this._onTabAttrModified(event);
        break;
      case "TabSelect":
        this._onTabSelect(event);
        break;
    }
  },

  toggle() {
    if (this._active) {
      this.hide();
    } else {
      this.show();
    }
  },

  show() {
    this._active = true;
    this._overlay.setAttribute("active", "true");

    if (!this._initialized) {
      // First show: build everything from scratch
      this._buildNodes();
      this._canvas.fitAll();
      this._initialized = true;
    } else {
      // Subsequent shows: sync tabs (add new, remove closed) and refresh thumbnails
      this._syncNodes();
      this._refreshAllThumbnails();
    }
  },

  hide() {
    this._active = false;
    this._overlay.removeAttribute("active");
  },

  _buildNodes() {
    for (let [id] of this._idToTab) {
      this._canvas.removeNode(id);
    }
    this._idToTab.clear();

    let tabs = gBrowser.tabs;
    let cols = 4;
    for (let i = 0; i < tabs.length; i++) {
      this._addTabNode(tabs[i], i, cols);
    }
  },

  _syncNodes() {
    let currentTabs = new Set(gBrowser.tabs);
    let knownTabs = new Set();

    // Remove nodes for tabs that no longer exist
    for (let [id, tab] of this._idToTab) {
      if (!currentTabs.has(tab)) {
        this._canvas.removeNode(id);
        this._idToTab.delete(id);
      } else {
        knownTabs.add(tab);
      }
    }

    // Add nodes for new tabs
    let cols = 4;
    let existingCount = this._idToTab.size;
    for (let tab of currentTabs) {
      if (!knownTabs.has(tab)) {
        this._addTabNode(tab, existingCount, cols);
        existingCount++;
      }
    }

    // Update headers for all existing nodes (title/favicon may have changed)
    for (let [id, tab] of this._idToTab) {
      this._updateTabHeader(tab, id);
    }

    // Update selection to match current tab
    this._canvas.deselectAll();
    let selId = this._tabToId.get(gBrowser.selectedTab);
    if (selId) {
      this._canvas.select(selId);
    }
  },

  _refreshAllThumbnails() {
    for (let [id, tab] of this._idToTab) {
      this._captureThumbnail(tab, id);
    }
  },

  _addTabNode(tab, index, cols = 4) {
    let id = "tab_" + (tab.linkedPanel || index);
    let col = index % cols;
    let row = Math.floor(index / cols);

    this._tabToId.set(tab, id);
    this._idToTab.set(id, tab);

    this._canvas.addNode(id, {
      x: col * 320,
      y: row * 252,
      width: 280,
      height: 212,
      title: tab.label || "New Tab",
      headerContent: this._buildHeader(tab),
    });

    this._captureThumbnail(tab, id);

    if (tab === gBrowser.selectedTab) {
      this._canvas.select(id);
    }
  },

  _buildHeader(tab) {
    let header = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
    header.style.cssText = "display:flex;align-items:center;gap:8px;width:100%";

    let favicon = document.createElementNS("http://www.w3.org/1999/xhtml", "img");
    favicon.style.cssText = "width:16px;height:16px;flex-shrink:0";
    favicon.src = tab.iconImage || "chrome://global/skin/icons/defaultFavicon.svg";
    favicon.draggable = false;
    header.appendChild(favicon);

    let title = document.createElementNS("http://www.w3.org/1999/xhtml", "span");
    title.style.cssText = "color:#e0e0e0;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1";
    title.textContent = tab.label || "New Tab";
    header.appendChild(title);

    return header;
  },

  _updateTabHeader(tab, id) {
    this._canvas.updateNode(id, {
      title: tab.label || "New Tab",
      headerContent: this._buildHeader(tab),
    });
  },

  async _captureThumbnail(tab, nodeId) {
    try {
      let browser = tab.linkedBrowser;
      if (!browser?.browsingContext?.currentWindowGlobal) {
        return;
      }

      let thumbCanvas = document.createElementNS("http://www.w3.org/1999/xhtml", "canvas");
      thumbCanvas.width = 280 * 2;
      thumbCanvas.height = 180 * 2;
      thumbCanvas.style.cssText = "width:100%;height:100%;display:block";

      let { PageThumbs } = ChromeUtils.importESModule(
        "resource://gre/modules/PageThumbs.sys.mjs"
      );
      await PageThumbs.captureTabPreviewThumbnail(browser, thumbCanvas);
      this._canvas.updateNode(nodeId, { bodyContent: thumbCanvas });
    } catch (e) {
      // Tab not ready
    }
  },

  _onKeyDown(event) {
    // Ctrl/Cmd+I to toggle (takes over Page Info shortcut)
    if (
      event.key === "i" &&
      !event.shiftKey &&
      (event.ctrlKey || event.metaKey)
    ) {
      event.preventDefault();
      event.stopPropagation();
      this.toggle();
      return;
    }

    if (this._active) {
      if (!event.ctrlKey && !event.metaKey) {
        event.stopPropagation();
      }
    }
  },

  _onTabOpen(event) {
    if (!this._active) {
      return;
    }
    let tab = event.target;
    let index = Array.from(gBrowser.tabs).indexOf(tab);
    this._addTabNode(tab, index);
  },

  _onTabClose(event) {
    let tab = event.target;
    let id = this._tabToId.get(tab);
    if (id) {
      this._canvas.removeNode(id);
      this._idToTab.delete(id);
    }
  },

  _onTabAttrModified(event) {
    if (!this._active) {
      return;
    }
    let tab = event.target;
    let id = this._tabToId.get(tab);
    if (!id) {
      return;
    }
    this._updateTabHeader(tab, id);
  },

  _onTabSelect() {
    if (!this._active) {
      return;
    }
    this._canvas.deselectAll();
    let id = this._tabToId.get(gBrowser.selectedTab);
    if (id) {
      this._canvas.select(id);
    }
  },
};

// gBrowser isn't available until after onLoad, so wait for delayed startup.
Services.obs.addObserver(function observer(subject, topic) {
  if (subject === window) {
    Services.obs.removeObserver(observer, topic);
    TabCanvas.init();
  }
}, "browser-delayed-startup-finished");
