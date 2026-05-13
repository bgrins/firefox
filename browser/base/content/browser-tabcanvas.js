/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

var { InfiniteCanvas } = ChromeUtils.importESModule(
  "chrome://browser/content/tabcanvas/canvas-engine.mjs",
  { global: "current" }
);
var { CanvasToolbar } = ChromeUtils.importESModule(
  "chrome://browser/content/tabcanvas/canvas-toolbar.mjs",
  { global: "current" }
);

/**
 * TabCanvas - Browser chrome adapter for InfiniteCanvas.
 * Connects gBrowser tabs to canvas nodes with live browser content overlays.
 */
var TabCanvas = {
  _overlay: null,
  _canvas: null,
  _active: false,
  _initialized: false,

  // Map tab -> canvas node id
  _tabToId: new WeakMap(),
  _idToTab: new Map(),

  // Header height in canvas-space pixels (padding 8+8 + 16 min-height)
  _HEADER_HEIGHT: 32,

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

    // Shared toolbar
    this._toolbar = new CanvasToolbar(
      this._canvas,
      document.getElementById("tab-canvas-toolbar")
    );

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

    this._canvas.on("view-change", () => {
      if (this._active) {
        this._updateAllBrowserOverlays();
      }
    });

    this._canvas.on("node-move", () => {
      if (this._active) {
        this._updateAllBrowserOverlays();
      }
    });

    this._canvas.on("node-resize", () => {
      if (this._active) {
        this._updateAllBrowserOverlays();
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

    // Capture native browser dimensions before we apply fixed positioning
    let selectedStack = gBrowser.selectedBrowser?.closest(".browserStack");
    if (selectedStack) {
      this._browserNativeWidth = selectedStack.clientWidth || 1;
      this._browserNativeHeight = selectedStack.clientHeight || 1;
    }

    this._overlay.setAttribute("active", "true");
    document.getElementById("tabbrowser-tabpanels")
      .setAttribute("tabcanvas-active", "true");

    if (!this._initialized) {
      this._buildNodes();
      this._canvas.fitAll();
      this._initialized = true;
    } else {
      this._syncNodes();
    }

    this._updateAllBrowserOverlays();
  },

  hide() {
    this._active = false;
    this._overlay.removeAttribute("active");
    document.getElementById("tabbrowser-tabpanels")
      .removeAttribute("tabcanvas-active");
    this._clearAllBrowserOverlays();
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

    for (let [id, tab] of this._idToTab) {
      if (!currentTabs.has(tab)) {
        this._canvas.removeNode(id);
        this._idToTab.delete(id);
      } else {
        knownTabs.add(tab);
      }
    }

    let cols = 4;
    let existingCount = this._idToTab.size;
    for (let tab of currentTabs) {
      if (!knownTabs.has(tab)) {
        this._addTabNode(tab, existingCount, cols);
        existingCount++;
      }
    }

    for (let [id, tab] of this._idToTab) {
      this._updateTabHeader(tab, id);
    }

    this._canvas.deselectAll();
    let selId = this._tabToId.get(gBrowser.selectedTab);
    if (selId) {
      this._canvas.select(selId);
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

  _updateAllBrowserOverlays() {
    let { zoom } = this._canvas.getViewState();
    let browserW = this._browserNativeWidth;
    let browserH = this._browserNativeHeight;

    for (let [id, tab] of this._idToTab) {
      let pos = this._canvas.getNodePosition(id);
      if (!pos) {
        continue;
      }

      // Measure actual header height from the node's DOM element
      let node = this._canvas.getNode(id);
      let headerEl = node?.element?.querySelector(".infinite-canvas-node-header");
      let headerH = headerEl ? headerEl.getBoundingClientRect().height / zoom : this._HEADER_HEIGHT;

      let bodyTop = pos.y + headerH;
      let bodyHeight = pos.height - headerH;
      if (bodyHeight <= 0) {
        continue;
      }

      let screenPos = this._canvas.canvasToScreen(pos.x, bodyTop);
      let screenW = pos.width * zoom;
      let screenH = bodyHeight * zoom;

      let browser = tab.linkedBrowser;
      if (!browser) {
        continue;
      }

      let stack = browser.closest(".browserStack");
      if (!stack) {
        continue;
      }

      let scaleFactor = screenW / browserW;

      // Size the stack to the small screen-space node body dimensions
      // so its hit area matches the visual bounds.
      stack.style.position = "fixed";
      stack.style.left = screenPos.x + "px";
      stack.style.top = screenPos.y + "px";
      stack.style.width = screenW + "px";
      stack.style.height = screenH + "px";
      stack.style.overflow = "hidden";
      stack.style.zIndex = "1001";
      stack.style.transform = "";
      stack.style.transformOrigin = "";

      // Scale the browser element inside to fit the small container
      browser.style.width = browserW + "px";
      browser.style.height = browserH + "px";
      browser.style.transform = `scale(${scaleFactor})`;
      browser.style.transformOrigin = "0 0";
    }
  },

  _clearAllBrowserOverlays() {
    for (let [, tab] of this._idToTab) {
      let browser = tab.linkedBrowser;
      if (!browser) {
        continue;
      }
      let stack = browser.closest(".browserStack");
      if (!stack) {
        continue;
      }
      stack.style.position = "";
      stack.style.left = "";
      stack.style.top = "";
      stack.style.width = "";
      stack.style.height = "";
      stack.style.transform = "";
      stack.style.transformOrigin = "";
      stack.style.overflow = "";
      stack.style.zIndex = "";

      browser.style.width = "";
      browser.style.height = "";
      browser.style.transform = "";
      browser.style.transformOrigin = "";
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
    this._updateAllBrowserOverlays();
  },

  _onTabClose(event) {
    let tab = event.target;
    let id = this._tabToId.get(tab);
    if (id) {
      this._canvas.removeNode(id);
      this._idToTab.delete(id);
    }
    if (this._active) {
      this._clearAllBrowserOverlays();
      this._updateAllBrowserOverlays();
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
