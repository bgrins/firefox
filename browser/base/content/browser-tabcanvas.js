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
 * Connects gBrowser tabs to canvas nodes with live browser content overlays,
 * SessionStore persistence, and bidirectional tab group mapping.
 */
var TabCanvas = {
  _overlay: null,
  _canvas: null,
  _active: false,
  _initialized: false,

  // Tab <-> canvas node ID mappings
  _tabToId: new WeakMap(),
  _idToTab: new Map(),

  // Stable ID generation via permanentKey
  _tabKeys: new WeakMap(),
  _nextKeyId: 0,

  // Tab group <-> canvas frame bidirectional mapping
  _canvasToTabGroup: new Map(),
  _tabGroupToCanvas: new Map(),

  // Re-entrancy guard for bidirectional sync
  _syncing: false,

  // Header height in canvas-space pixels
  _HEADER_HEIGHT: 32,

  // Persistence
  _saveTimer: null,

  get active() {
    return this._active;
  },

  _getTabId(tab) {
    let key = tab.permanentKey;
    if (!this._tabKeys.has(key)) {
      this._tabKeys.set(key, "tab_" + (this._nextKeyId++));
    }
    return this._tabKeys.get(key);
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

    // --- Canvas event handlers ---

    this._canvas.on("node-dblclick", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (tab) {
        gBrowser.selectedTab = tab;
        this.hide();
      }
    });

    this._canvas.on("node-click", ({ id }) => {
      this._selectTabFromCanvas(id);
    });

    this._canvas.on("node-zoom-toggle", ({ id }) => {
      this._selectTabFromCanvas(id);
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
        this._scheduleOverlayUpdate();
      }
    });

    this._canvas.on("node-move", () => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
      this._scheduleSave();
    });

    this._canvas.on("node-resize", () => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
      this._scheduleSave();
    });

    this._canvas.on("frame-create", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameCreate(id);
    });

    this._canvas.on("frame-remove", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameRemove(id);
    });

    this._canvas.on("frame-label-change", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameLabelChange(id);
    });

    this._canvas.on("node-frame-change", ({ id, frameId, prevFrameId }) => {
      this._scheduleSave();
      this._onCanvasNodeFrameChange(id, frameId, prevFrameId);
    });

    // --- Tab event handlers ---

    gBrowser.tabContainer.addEventListener("TabOpen", this);
    gBrowser.tabContainer.addEventListener("TabClose", this);
    gBrowser.tabContainer.addEventListener("TabAttrModified", this);
    gBrowser.tabContainer.addEventListener("TabSelect", this);
    gBrowser.tabContainer.addEventListener("TabPinned", this);
    gBrowser.tabContainer.addEventListener("TabUnpinned", this);
    gBrowser.tabContainer.addEventListener("TabGroupCreate", this);
    gBrowser.tabContainer.addEventListener("TabGroupRemoved", this);
    gBrowser.tabContainer.addEventListener("TabGroupUpdate", this);
    gBrowser.tabContainer.addEventListener("TabGrouped", this);
    gBrowser.tabContainer.addEventListener("TabUngrouped", this);

    // Capture phase to intercept before XUL key handlers
    document.addEventListener("keydown", this, true);
    window.addEventListener("resize", this);
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
      case "TabPinned":
      case "TabUnpinned":
        this._onTabPinChange(event);
        break;
      case "TabGroupCreate":
        this._onBrowserTabGroupCreate(event);
        break;
      case "TabGroupRemoved":
        this._onBrowserTabGroupRemoved(event);
        break;
      case "TabGroupUpdate":
        this._onBrowserTabGroupUpdate(event);
        break;
      case "TabGrouped":
        this._onBrowserTabGrouped(event);
        break;
      case "TabUngrouped":
        this._onBrowserTabUngrouped(event);
        break;
      case "resize":
        this._onWindowResize();
        break;
    }
  },

  // --- Show / Hide ---

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
      let saved = this._loadSavedLayout();
      if (saved) {
        this._restoreLayout(saved);
      } else {
        this._buildNodes();
        this._syncTabGroups();
        this._canvas.fitAll();
      }
      this._initialized = true;
    } else {
      this._syncNodes();
    }

    this._captureAllThumbnails();
    this._updateAllBrowserOverlays();
  },

  hide() {
    this._active = false;
    this._overlay.removeAttribute("active");
    document.getElementById("tabbrowser-tabpanels")
      .removeAttribute("tabcanvas-active");
    this._clearAllBrowserOverlays();
    this._fixedOffset = null;
    this._save();
  },

  // --- Persistence ---

  _scheduleSave() {
    clearTimeout(this._saveTimer);
    this._saveTimer = setTimeout(() => this._save(), 500);
  },

  _save() {
    if (!this._initialized) {
      return;
    }
    let data = this._canvas.toJSON();
    data.tabMap = {};
    for (let [id, tab] of this._idToTab) {
      data.tabMap[id] = {
        url: tab.linkedBrowser?.currentURI?.spec || "",
        title: tab.label || "",
      };
    }
    data.groupMap = {};
    for (let [canvasId, groupId] of this._canvasToTabGroup) {
      data.groupMap[canvasId] = groupId;
    }
    try {
      SessionStore.setCustomWindowValue(
        window, "tabCanvasLayout", JSON.stringify(data)
      );
    } catch (e) {
      // SessionStore not ready yet
    }
  },

  _loadSavedLayout() {
    try {
      let saved = SessionStore.getCustomWindowValue(window, "tabCanvasLayout");
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      // SessionStore not ready or parse error
    }
    return null;
  },

  _restoreLayout(data) {
    this._canvas.fromJSON(data);

    // Match saved nodes to current tabs by URL/title
    let currentTabs = Array.from(gBrowser.tabs);
    let unmatched = new Set(currentTabs);
    let tabMap = data.tabMap || {};

    for (let savedNode of data.nodes) {
      let saved = tabMap[savedNode.id];
      if (!saved) {
        continue;
      }
      // Find best matching tab
      let bestTab = null;
      let bestScore = 0;
      for (let tab of unmatched) {
        let url = tab.linkedBrowser?.currentURI?.spec || "";
        let title = tab.label || "";
        let score = 0;
        if (url === saved.url && url !== "about:blank") {
          score += 10;
        }
        if (title === saved.title && title !== "New Tab") {
          score += 5;
        }
        if (score > bestScore) {
          bestScore = score;
          bestTab = tab;
        }
      }
      if (bestTab && bestScore > 0) {
        let id = this._getTabId(bestTab);
        // Remap if the saved ID doesn't match the new stable ID
        if (id !== savedNode.id) {
          let nodeObj = this._canvas.getNode(savedNode.id);
          if (nodeObj) {
            this._canvas.removeNode(savedNode.id);
            this._canvas.addNode(id, {
              x: savedNode.x, y: savedNode.y,
              width: savedNode.width, height: savedNode.height,
              title: bestTab.label || "New Tab",
              headerContent: this._buildHeader(bestTab),
            });
            let newNode = this._canvas.getNode(id);
            if (newNode && savedNode.frameId) {
              newNode.frameId = savedNode.frameId;
              this._canvas._updateNodeGroupVisual(newNode);
            }
          }
        } else {
          this._updateTabHeader(bestTab, id);
        }
        this._tabToId.set(bestTab, id);
        this._idToTab.set(id, bestTab);
        unmatched.delete(bestTab);
      }
    }

    // Remove orphaned canvas nodes (no matching tab)
    for (let savedNode of data.nodes) {
      if (!this._idToTab.has(savedNode.id)) {
        this._canvas.removeNode(savedNode.id);
      }
    }

    // Add unmatched tabs as new nodes
    for (let tab of unmatched) {
      let pos = this._findEmptyPosition();
      this._addTabNode(tab, 0, 4, pos.x, pos.y);
    }

    // Restore group mappings
    if (data.groupMap) {
      for (let [canvasId, groupId] of Object.entries(data.groupMap)) {
        this._canvasToTabGroup.set(canvasId, groupId);
        this._tabGroupToCanvas.set(groupId, canvasId);
      }
    }
  },

  // --- Node Management ---

  _buildNodes() {
    for (let [id] of this._idToTab) {
      this._canvas.removeNode(id);
    }
    this._idToTab.clear();

    let tabs = gBrowser.tabs;
    let cols = 4;
    for (let i = 0; i < tabs.length; i++) {
      let col = i % cols;
      let row = Math.floor(i / cols);
      this._addTabNode(tabs[i], i, cols, col * 320, row * 252);
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

    for (let tab of currentTabs) {
      if (!knownTabs.has(tab)) {
        let pos = this._findEmptyPosition();
        this._addTabNode(tab, 0, 4, pos.x, pos.y);
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

  _addTabNode(tab, index, cols = 4, x = null, y = null) {
    let id = this._getTabId(tab);
    if (x === null) {
      let col = index % cols;
      let row = Math.floor(index / cols);
      x = col * 320;
      y = row * 252;
    }

    this._tabToId.set(tab, id);
    this._idToTab.set(id, tab);

    let nodeOpts = {
      x, y,
      width: tab.pinned ? 160 : 280,
      height: tab.pinned ? 120 : 212,
      title: tab.label || "New Tab",
      headerContent: this._buildHeader(tab),
    };

    this._canvas.addNode(id, nodeOpts);

    // Apply container tab color
    if (tab.userContextId) {
      let identity = ContextualIdentityService.getPublicIdentityFromId(
        tab.userContextId
      );
      if (identity?.color) {
        let colorMap = {
          blue: "#0a84ff", turquoise: "#00c8d7", green: "#44b700",
          yellow: "#ffbd4f", orange: "#ff9400", red: "#ff0039",
          pink: "#ff2a8a", purple: "#9400ff",
        };
        let c = colorMap[identity.color] || "#666";
        this._canvas.setNodeColor(id, null, c);
      }
    }

    if (tab === gBrowser.selectedTab) {
      this._canvas.select(id);
    }
  },

  _findEmptyPosition() {
    let bounds = this._canvas._getAllBounds();
    if (!bounds) {
      return { x: 0, y: 0 };
    }
    return { x: bounds.x, y: bounds.y + bounds.height + 40 };
  },

  _buildHeader(tab) {
    let header = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
    header.style.cssText = "display:flex;align-items:center;gap:8px;width:100%";

    if (tab.pinned) {
      let pin = document.createElementNS("http://www.w3.org/1999/xhtml", "img");
      pin.style.cssText = "width:12px;height:12px;flex-shrink:0";
      pin.src = "chrome://global/skin/icons/pin-12.svg";
      pin.draggable = false;
      header.appendChild(pin);
    }

    let favicon = document.createElementNS("http://www.w3.org/1999/xhtml", "img");
    favicon.style.cssText = "width:16px;height:16px;flex-shrink:0";
    favicon.src = tab.getAttribute("image") || "chrome://global/skin/icons/defaultFavicon.svg";
    favicon.draggable = false;
    header.appendChild(favicon);

    let title = document.createElementNS("http://www.w3.org/1999/xhtml", "span");
    title.style.cssText = "color:#e0e0e0;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1";
    title.textContent = tab.label || "New Tab";
    header.appendChild(title);

    let nodeId = this._tabToId.get(tab);
    if (nodeId) {
      header.appendChild(this._canvas.createZoomButton(nodeId));
    }

    return header;
  },

  _updateTabHeader(tab, id) {
    this._canvas.updateNode(id, {
      title: tab.label || "New Tab",
      headerContent: this._buildHeader(tab),
    });
  },

  // --- Browser Overlays (live content for selected tab) ---

  _captureAllThumbnails() {
    for (let [id, tab] of this._idToTab) {
      if (tab !== gBrowser.selectedTab) {
        this._captureThumbnail(tab, id);
      }
    }
  },

  _scheduleOverlayUpdate() {
    if (this._overlayUpdatePending) {
      return;
    }
    this._overlayUpdatePending = true;
    requestAnimationFrame(() => {
      this._overlayUpdatePending = false;
      if (this._active) {
        this._updateAllBrowserOverlays();
      }
    });
  },

  // Select a tab from a canvas action (click or zoom button) without
  // exiting the canvas. Pre-applies overlay styles to the incoming tab's
  // browserStack so the new browser never flashes at full size.
  _selectTabFromCanvas(nodeId) {
    let tab = this._idToTab.get(nodeId);
    if (!tab || tab === gBrowser.selectedTab) {
      return;
    }
    this._applyOverlayToTab(tab);
    this._internalTabSelect = true;
    try {
      gBrowser.selectedTab = tab;
    } finally {
      this._internalTabSelect = false;
    }
    this._captureAllThumbnails();
    this._updateAllBrowserOverlays();
  },

  _applyOverlayToTab(tab) {
    let id = this._tabToId.get(tab);
    if (!id) {
      return;
    }
    let node = this._canvas.getNode(id);
    if (!node) {
      return;
    }
    let bodyEl = node.element?.querySelector(".infinite-canvas-node-body");
    if (!bodyEl) {
      return;
    }
    let bodyRect = bodyEl.getBoundingClientRect();
    if (bodyRect.width <= 0 || bodyRect.height <= 0) {
      return;
    }
    let browser = tab.linkedBrowser;
    let stack = browser?.closest(".browserStack");
    if (!stack) {
      return;
    }

    if (!this._fixedOffset) {
      let probe = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
      probe.style.cssText = "position:fixed;left:0;top:0;width:1px;height:1px;pointer-events:none;z-index:-1";
      stack.parentNode.appendChild(probe);
      let probeRect = probe.getBoundingClientRect();
      this._fixedOffset = { x: probeRect.left, y: probeRect.top };
      probe.remove();
    }

    let browserW = this._browserNativeWidth;
    let browserH = this._browserNativeHeight;
    let scaleFactor = bodyRect.width / browserW;

    stack.style.position = "fixed";
    stack.style.left = (bodyRect.left - this._fixedOffset.x) + "px";
    stack.style.top = (bodyRect.top - this._fixedOffset.y) + "px";
    stack.style.width = bodyRect.width + "px";
    stack.style.height = bodyRect.height + "px";
    stack.style.overflow = "hidden";
    stack.style.zIndex = "1001";
    stack.style.pointerEvents = "auto";

    browser.style.width = browserW + "px";
    browser.style.height = browserH + "px";
    browser.style.transform = `scale(${scaleFactor})`;
    browser.style.transformOrigin = "0 0";
  },

  _updateAllBrowserOverlays() {
    let selectedTab = gBrowser.selectedTab;

    for (let [, tab] of this._idToTab) {
      let browser = tab.linkedBrowser;
      let stack = browser?.closest(".browserStack");
      if (tab === selectedTab) {
        this._applyOverlayToTab(tab);
      } else if (stack) {
        this._clearBrowserOverlay(stack, browser);
      }
    }
  },

  async _captureThumbnail(tab, nodeId) {
    try {
      let browser = tab.linkedBrowser;
      if (!browser?.browsingContext?.currentWindowGlobal) {
        return;
      }
      if (tab.getAttribute("pending")) {
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

  _clearBrowserOverlay(stack, browser) {
    stack.style.position = "";
    stack.style.left = "";
    stack.style.top = "";
    stack.style.width = "";
    stack.style.height = "";
    stack.style.transform = "";
    stack.style.transformOrigin = "";
    stack.style.overflow = "";
    stack.style.zIndex = "";
    stack.style.pointerEvents = "";

    browser.style.width = "";
    browser.style.height = "";
    browser.style.transform = "";
    browser.style.transformOrigin = "";
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
      this._clearBrowserOverlay(stack, browser);
    }
  },

  // --- Tab Group Bidirectional Sync ---

  _withSync(fn) {
    if (this._syncing) {
      return;
    }
    this._syncing = true;
    try {
      fn();
    } finally {
      this._syncing = false;
    }
  },

  _syncTabGroups() {
    for (let group of gBrowser.tabGroups) {
      this._importBrowserTabGroup(group);
    }
  },

  _groupColorMap: {
    blue: "#0a84ff", purple: "#9400ff", cyan: "#00c8d7",
    orange: "#ff9400", yellow: "#ffbd4f", pink: "#ff2a8a",
    green: "#44b700", gray: "#666", red: "#ff0039",
  },

  _importBrowserTabGroup(group) {
    if (this._tabGroupToCanvas.has(group.id)) {
      return;
    }
    let groupTabs = group.tabs;
    if (!groupTabs.length) {
      return;
    }

    // Find bounding box of member tabs on canvas
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (let tab of groupTabs) {
      let id = this._tabToId.get(tab);
      if (!id) {
        continue;
      }
      let pos = this._canvas.getNodePosition(id);
      if (!pos) {
        continue;
      }
      minX = Math.min(minX, pos.x);
      minY = Math.min(minY, pos.y);
      maxX = Math.max(maxX, pos.x + pos.width);
      maxY = Math.max(maxY, pos.y + pos.height);
    }

    if (!isFinite(minX)) {
      return;
    }

    let pad = 24;
    let frameId = "__group_" + group.id;

    this._canvas.addFrame(frameId, {
      x: minX - pad,
      y: minY - pad - 24,
      width: maxX - minX + pad * 2,
      height: maxY - minY + pad * 2 + 24,
      label: group.label || "Group",
      color: this._groupColorMap[group.color] || null,
    });

    // Assign tabs to frame (use private setter via canvas; no event needed
    // since we are mirroring an external state, not creating a change to sync back)
    this._withSync(() => {
      for (let tab of groupTabs) {
        let id = this._tabToId.get(tab);
        if (!id) {
          continue;
        }
        let node = this._canvas.getNode(id);
        if (node) {
          this._canvas._setNodeFrame(node, frameId);
        }
      }
    });

    this._canvasToTabGroup.set(frameId, group.id);
    this._tabGroupToCanvas.set(group.id, frameId);
  },

  // Create a browser group from a canvas frame and link the mapping.
  // No-op if the frame has no eligible (non-pinned) tabs.
  _maybeCreateBrowserGroup(frameId) {
    if (this._canvasToTabGroup.has(frameId)) {
      return null;
    }
    let children = this._canvas.getFrameChildren(frameId);
    let tabs = children
      .map(id => this._idToTab.get(id))
      .filter(t => t && !t.pinned);
    if (!tabs.length) {
      return null;
    }
    let frame = this._canvas._frames.get(frameId);
    let group;
    this._withSync(() => {
      group = gBrowser.addTabGroup(tabs, {
        label: frame?.label || "Group",
      });
    });
    if (group) {
      this._canvasToTabGroup.set(frameId, group.id);
      this._tabGroupToCanvas.set(group.id, frameId);
    }
    return group;
  },

  // Canvas frame created -> create browser tab group (if frame has tabs).
  // Empty frames defer group creation until first tab joins.
  _onCanvasFrameCreate(frameId) {
    if (this._syncing) {
      return;
    }
    this._maybeCreateBrowserGroup(frameId);
  },

  // Canvas frame removed -> ungroup browser tabs.
  _onCanvasFrameRemove(frameId) {
    if (this._syncing) {
      return;
    }
    let groupId = this._canvasToTabGroup.get(frameId);
    if (!groupId) {
      return;
    }
    this._canvasToTabGroup.delete(frameId);
    this._tabGroupToCanvas.delete(groupId);
    let group = gBrowser.getTabGroupById(groupId);
    if (group) {
      this._withSync(() => group.ungroupTabs());
    }
  },

  // Canvas node moved into/out of frame -> sync to browser group membership.
  _onCanvasNodeFrameChange(nodeId, frameId, prevFrameId) {
    if (this._syncing) {
      return;
    }
    let tab = this._idToTab.get(nodeId);
    if (!tab || tab.pinned) {
      return;
    }

    let prevGroupId = prevFrameId ? this._canvasToTabGroup.get(prevFrameId) : null;
    let newGroupId = frameId ? this._canvasToTabGroup.get(frameId) : null;

    if (frameId && !newGroupId) {
      // No browser group exists yet for this frame: create one now with this tab
      // (and any other tabs the canvas has already assigned to this frame).
      let group = this._maybeCreateBrowserGroup(frameId);
      if (!group) {
        // No eligible tabs (this tab is pinned). Nothing to do.
      }
      // If we needed to remove from prev group, fall through.
    } else if (frameId && newGroupId) {
      // Move tab into existing group.
      let group = gBrowser.getTabGroupById(newGroupId);
      if (group && tab.group !== group) {
        this._withSync(() => group.addTabs([tab]));
      }
    }

    if (!frameId && prevGroupId) {
      // Tab moved out of a frame: remove from browser group.
      if (tab.group && tab.group.id === prevGroupId) {
        this._withSync(() => {
          // Moving tab to the end of the tab strip removes it from its group.
          gBrowser.moveTabTo(tab, { tabIndex: gBrowser.tabs.length - 1 });
        });
      }
    }
  },

  // Canvas frame label changed -> update browser tab group label.
  _onCanvasFrameLabelChange(frameId) {
    if (this._syncing) {
      return;
    }
    let groupId = this._canvasToTabGroup.get(frameId);
    if (!groupId) {
      return;
    }
    let group = gBrowser.getTabGroupById(groupId);
    if (!group) {
      return;
    }
    let frame = this._canvas._frames.get(frameId);
    if (frame) {
      this._withSync(() => { group.label = frame.label; });
    }
  },

  // Browser tab group created -> create canvas frame.
  _onBrowserTabGroupCreate(event) {
    if (this._syncing) {
      return;
    }
    let group = event.target;
    if (this._tabGroupToCanvas.has(group.id)) {
      return;
    }
    if (!this._initialized) {
      return;
    }
    this._importBrowserTabGroup(group);
    this._scheduleSave();
  },

  // Browser tab group removed -> remove canvas frame.
  _onBrowserTabGroupRemoved(event) {
    if (this._syncing) {
      return;
    }
    let group = event.target;
    let frameId = this._tabGroupToCanvas.get(group.id);
    if (!frameId) {
      return;
    }
    this._canvasToTabGroup.delete(frameId);
    this._tabGroupToCanvas.delete(group.id);
    this._withSync(() => this._canvas.removeFrame(frameId));
    this._scheduleSave();
  },

  // Browser tab group label/color changed -> update canvas frame.
  _onBrowserTabGroupUpdate(event) {
    if (this._syncing) {
      return;
    }
    let group = event.target;
    let frameId = this._tabGroupToCanvas.get(group.id);
    if (!frameId) {
      return;
    }
    this._withSync(() => {
      this._canvas.updateFrame(frameId, {
        label: group.label,
        color: this._groupColorMap[group.color] || null,
      });
    });
    this._scheduleSave();
  },

  // Browser tab added to group -> assign canvas node to corresponding frame.
  _onBrowserTabGrouped(event) {
    if (this._syncing) {
      return;
    }
    let group = event.target;
    let tab = event.detail;
    let nodeId = this._tabToId.get(tab);
    if (!nodeId) {
      return;
    }
    let frameId = this._tabGroupToCanvas.get(group.id);
    if (!frameId) {
      // Browser group not yet mirrored. Import it.
      if (this._initialized) {
        this._importBrowserTabGroup(group);
        frameId = this._tabGroupToCanvas.get(group.id);
      }
      if (!frameId) {
        return;
      }
    }
    let node = this._canvas.getNode(nodeId);
    if (node && node.frameId !== frameId) {
      this._withSync(() => this._canvas._setNodeFrame(node, frameId));
    }
    this._scheduleSave();
  },

  // Browser tab removed from group -> clear canvas node's frame.
  _onBrowserTabUngrouped(event) {
    if (this._syncing) {
      return;
    }
    let tab = event.detail;
    let nodeId = this._tabToId.get(tab);
    if (!nodeId) {
      return;
    }
    let node = this._canvas.getNode(nodeId);
    if (node && node.frameId !== null) {
      this._withSync(() => this._canvas._setNodeFrame(node, null));
    }
    this._scheduleSave();
  },

  // --- Tab Event Handlers ---

  _onKeyDown(event) {
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
      // Only prevent default for keys the canvas engine handles,
      // so F5, F12, url bar typing, etc. still work
      let canvasKeys = [
        "h", "v", "f", "t", " ",
        "Delete", "Backspace",
        "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
        "Escape",
      ];
      if (!event.ctrlKey && !event.metaKey && canvasKeys.includes(event.key)) {
        event.preventDefault();
      }
    }
  },

  _onTabOpen(event) {
    if (!this._active) {
      return;
    }
    let tab = event.target;
    let pos = this._findEmptyPosition();
    this._addTabNode(tab, 0, 4, pos.x, pos.y);
    this._updateAllBrowserOverlays();
    this._scheduleSave();
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
    this._scheduleSave();
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
    // Only refresh the header when label/icon-related attributes change.
    // Tab events fire frequently during loads for unrelated attributes
    // (busy, progress, soundplaying, etc.) and rebuilding the header on
    // every one causes flicker.
    let changed = event.detail?.changed;
    if (!changed || changed.some(a =>
      a === "label" || a === "image" || a === "iconLoadingPrincipal" ||
      a === "pinned" || a === "muted" || a === "crashed"
    )) {
      this._updateTabHeader(tab, id);
    }
  },

  _onTabSelect() {
    if (!this._active) {
      return;
    }
    // Tab selection initiated by a canvas click: stay in canvas mode.
    if (this._internalTabSelect) {
      return;
    }
    this.hide();
  },

  _onTabPinChange(event) {
    let tab = event.target;
    let id = this._tabToId.get(tab);
    if (!id) {
      return;
    }
    this._updateTabHeader(tab, id);
    // Resize node for pinned/unpinned state
    let pos = this._canvas.getNodePosition(id);
    if (pos) {
      let newW = tab.pinned ? 160 : 280;
      let newH = tab.pinned ? 120 : 212;
      if (pos.width !== newW || pos.height !== newH) {
        let node = this._canvas.getNode(id);
        if (node) {
          node.width = newW;
          node.height = newH;
          this._canvas._applyRect(node.element, node);
        }
      }
    }
    this._scheduleSave();
  },

  _onWindowResize() {
    if (!this._active) {
      return;
    }
    let selectedStack = gBrowser.selectedBrowser?.closest(".browserStack");
    if (selectedStack) {
      // Clear overlay first so we measure native dimensions
      let browser = gBrowser.selectedBrowser;
      this._clearBrowserOverlay(selectedStack, browser);
      this._browserNativeWidth = selectedStack.clientWidth || 1;
      this._browserNativeHeight = selectedStack.clientHeight || 1;
    }
    this._fixedOffset = null;
    this._scheduleOverlayUpdate();
  },
};

// gBrowser isn't available until after onLoad, so wait for delayed startup.
Services.obs.addObserver(function observer(subject, topic) {
  if (subject === window) {
    Services.obs.removeObserver(observer, topic);
    TabCanvas.init();
  }
}, "browser-delayed-startup-finished");
