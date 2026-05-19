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

  // Temporary: enable verbose logging for the lazy-tab wakeup path.
  // Toggle off (or via TabCanvas._tabcanvasDebug = false) once the
  // behavior is confirmed working.
  _tabcanvasDebug: true,

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
    // Match the zoom-button fit options for keyboard shortcuts (Alt+Enter
    // and friends) so chrome-side UX is consistent.
    this._canvas.setDefaultFitOptions({ padding: 56, maxZoom: 3 });

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

    this._canvas.on("node-click", ({ id, altKey }) => {
      if (altKey) {
        // Alt+click matches the zoom button: smart toggle. If the user
        // is still at the saved zoom-in target, restore the previous
        // view; otherwise (first click, or view has been moved) save
        // the current view and zoom in.
        //
        // If the clicked node is part of a group, treat the whole group
        // as the zoom target — the user is acting on the group, not on
        // a single child inside it.
        let zoomTargetId = id;
        let node = this._canvas.getNode(id);
        if (node && node.frameId) {
          zoomTargetId = node.frameId;
        }
        this._canvas.toggleZoomToNode(zoomTargetId, { padding: 56, maxZoom: 3 });
      }
      this._selectTabFromCanvas(id);
    });

    this._canvas.on("node-zoom-toggle", ({ id }) => {
      this._selectTabFromCanvas(id);
    });

    this._canvas.on("node-delete", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (!tab) {
        return;
      }
      this._closeTabFromCanvas(tab, id);
    });

    this._canvas.on("escape", () => {
      if (this._canvas.getSelection().length === 0) {
        this.hide();
      }
    });

    this._canvas.on("selection-change", ({ selection }) => {
      this._syncSelectionToTabbrowser(selection);
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

    // node-drag fires on every rAF tick during a drag (vs node-move
    // which only fires once at drag end). We need this so the live
    // browser overlay tracks the selected tab while it's being moved.
    this._canvas.on("node-drag", ({ id }) => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
      // Wake the dragged tab in the background so live content shows
      // up by the time the drag completes. _ensureTabLoaded guards
      // against repeated work via _loadingTabs.
      let tab = this._idToTab.get(id);
      if (tab) {
        this._ensureTabLoaded(tab);
      }
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
      }
      this._initialized = true;
    } else {
      this._syncNodes();
    }
    // Always fit-all when entering the canvas view so the user sees
    // everything (whether this is the first show, a restored layout,
    // or a re-open with new/closed tabs).
    this._canvas.fitAll(true);

    // Ensure the canvas selection reflects the current selected tab so
    // keyboard shortcuts (alt+arrow, Enter, etc.) act on it. Then focus
    // the canvas container so it receives keyboard events.
    let currentId = this._tabToId.get(gBrowser.selectedTab);
    if (currentId) {
      this._canvas.deselectAll();
      this._canvas.select(currentId);
    }
    document.getElementById("tab-canvas-inner")?.focus();

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
              headerContent: this._buildHeader(bestTab, id),
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
      headerContent: this._buildHeader(tab, id),
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

  // Place a new tab next to its opener if we know one.
  _findPositionNearOpener(openerTab) {
    let openerId = openerTab && this._tabToId.get(openerTab);
    if (!openerId) {
      return this._findEmptyPosition();
    }
    return this._canvas.findPositionNearNode(openerId);
  },

  _buildHeader(tab, nodeId = null) {
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
    // min-width:0 is required so flex shrinking can truncate the text below
    // its intrinsic content width; otherwise a long title pushes the zoom
    // button past the node's overflow:hidden boundary.
    title.style.cssText = "color:#e0e0e0;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0";
    title.textContent = tab.label || "New Tab";
    header.appendChild(title);

    // Prefer the explicit nodeId argument over the map lookup. Some call
    // sites (e.g. _restoreLayout) build the header before populating
    // _tabToId; in that case we still need the zoom button.
    let id = nodeId || this._tabToId.get(tab);
    if (id) {
      // Fit options for the integration: a bit of breathing room around
      // the zoomed tab while still filling most of the canvas.
      header.appendChild(this._canvas.createZoomButton(id, {
        padding: 56,
        maxZoom: 3,
      }));
      // The shared close button removes the node and emits node-delete;
      // our node-delete handler turns that into gBrowser.removeTab.
      header.appendChild(this._canvas.createCloseButton(id));
    }

    return header;
  },

  // Shared close logic used by both the X button and the node-delete
  // event (Delete key / context menu). Restores any saved zoom-in view
  // for the closing tab, then removes the tab. If the tab is currently
  // selected, suppresses the auto-hide that would normally follow.
  _closeTabFromCanvas(tab, nodeId) {
    // If the user had zoomed in on this tab, animate back to the
    // previous view before the node disappears. The engine's removeNode
    // also auto-shrinks the containing frame to fit the remaining nodes.
    if (nodeId) {
      this._canvas.restoreSavedView(nodeId);
    }
    let wasSelected = tab === gBrowser.selectedTab;
    if (wasSelected) {
      this._internalTabSelect = true;
    }
    try {
      gBrowser.removeTab(tab);
    } finally {
      if (wasSelected) {
        this._internalTabSelect = false;
        this._applyOverlayToTab(gBrowser.selectedTab);
        this._captureAllThumbnails();
      }
    }
  },

  _updateTabHeader(tab, id) {
    this._canvas.updateNode(id, {
      title: tab.label || "New Tab",
      headerContent: this._buildHeader(tab, id),
    });
  },

  // --- Browser Overlays (live content for selected tab) ---

  _captureAllThumbnails() {
    for (let [id, tab] of this._idToTab) {
      if (tab !== gBrowser.selectedTab) {
        // If the tab is unloaded, wake it up so a real thumbnail can
        // be captured shortly. (Without this, the captured image is
        // the "discarded" placeholder.)
        this._ensureTabLoaded(tab);
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
  // Mirror canvas selection into tabbrowser multi-selection. Frames and
  // canvas-only items are skipped (they're not real tabs).
  _syncSelectionToTabbrowser(selection) {
    if (this._internalTabSelect) {
      // Already in the middle of a single-tab select; selection-change will
      // fire again after the dust settles.
      return;
    }
    // Collect both the tabs and their canvas ids in the same order as
    // they appear in the selection set.
    let tabs = [];
    let firstTabNodeId = null;
    for (let id of selection) {
      let tab = this._idToTab.get(id);
      if (tab) {
        tabs.push(tab);
        if (firstTabNodeId === null) {
          firstTabNodeId = id;
        }
      }
    }
    // Any tab the user pulls into the selection (single click, marquee,
    // shift-click, ctrl+a, drag, arrow keys, ...) should wake up its
    // content so thumbnails / live previews become real.
    for (let tab of tabs) {
      this._ensureTabLoaded(tab);
    }

    // If exactly one tab is selected (e.g. via alt+arrow navigation,
    // Enter to drill into a frame, etc.) make it the active browser tab
    // so the live overlay renders that tab's content. Skip if it's
    // already selected.
    if (tabs.length === 1 && tabs[0] !== gBrowser.selectedTab) {
      this._selectTabFromCanvas(firstTabNodeId);
    }

    // _withSync sets _suppressHide so any TabSelect dispatched as a side
    // effect of these multi-select changes won't exit the canvas.
    this._withSync(() => {
      gBrowser.clearMultiSelectedTabs();
      if (tabs.length >= 2) {
        for (let tab of tabs) {
          gBrowser.addToMultiSelectedTabs(tab);
        }
      }
    });
  },

  // For a tab that's lazy (session-restored but not yet loaded) or
  // discarded (was loaded, then unloaded for memory), materialize its
  // browser and kick off a load in the background. Combines several
  // signals because the "lazy" vs "discarded" vs "fully-loaded but
  // hidden" cases each need slightly different handling.
  _ensureTabLoaded(tab) {
    if (!tab) {
      return;
    }
    let hasPending = tab.hasAttribute("pending");
    let hasDiscarded = tab.hasAttribute("discarded");
    let browser = tab.linkedBrowser;
    let needsLoad = hasPending || hasDiscarded || !tab.linkedPanel;
    if (this._tabcanvasDebug) {
      console.log("[tabcanvas] _ensureTabLoaded", {
        label: tab.label,
        pending: hasPending,
        discarded: hasDiscarded,
        linkedPanel: !!tab.linkedPanel,
        docShellIsActive: browser?.docShellIsActive,
        currentURI: browser?.currentURI?.spec,
        needsLoad,
        alreadyLoading: this._loadingTabs?.has(tab),
      });
    }
    if (!needsLoad) {
      return;
    }
    if (this._loadingTabs?.has(tab)) {
      return;
    }
    (this._loadingTabs ??= new WeakSet()).add(tab);
    try {
      // Materialize the lazy browser (idempotent — no-op if already in
      // the DOM). For session-restored tabs, this attaches the docshell
      // and registers SessionStore state for the browser.
      if (!tab.linkedPanel) {
        gBrowser._insertBrowser(tab);
      }
      browser = tab.linkedBrowser;
      // Activate the docshell so layers/processes spin up.
      if (browser && !browser.docShellIsActive) {
        try { browser.docShellIsActive = true; } catch (e) {}
      }
      // Three complementary triggers — whichever applies will fire:
      //   - TabShow → SessionStore.onTabShow → queues restore.
      //   - browser.reload() → for pending or discarded tabs, kicks
      //     off the URI load directly. For lazy browsers, the lazy
      //     `reload` getter chains _insertBrowser + SSTabRestoring +
      //     real reload.
      tab.dispatchEvent(new CustomEvent("TabShow", { bubbles: true }));
      if ((hasPending || hasDiscarded) && browser?.reload) {
        try { browser.reload(); } catch (e) {}
      }
      // Once the tab actually finishes loading, re-capture its thumbnail
      // so the canvas body shows real content instead of the placeholder
      // that may have been captured while the tab was still discarded.
      let onLoad = () => {
        tab.removeEventListener("SSTabRestored", onLoad);
        tab.linkedBrowser?.removeEventListener("pageshow", onLoad, true);
        let nodeId = this._tabToId.get(tab);
        if (nodeId && this._active) {
          this._captureThumbnail(tab, nodeId);
        }
      };
      tab.addEventListener("SSTabRestored", onLoad, { once: true });
      try {
        tab.linkedBrowser?.addEventListener("pageshow", onLoad, { once: true, capture: true });
      } catch (e) {}
      if (this._tabcanvasDebug) {
        console.log("[tabcanvas] _ensureTabLoaded -> dispatched", {
          label: tab.label,
          linkedPanel: !!tab.linkedPanel,
          docShellIsActive: browser?.docShellIsActive,
        });
      }
    } catch (e) {
      if (this._tabcanvasDebug) {
        console.error("[tabcanvas] _ensureTabLoaded failed", e);
      }
    }
  },

  _selectTabFromCanvas(nodeId) {
    let tab = this._idToTab.get(nodeId);
    if (!tab) {
      return;
    }

    // If the tab is unloaded/lazy/discarded, kick off the load so the
    // live overlay can show real content. This works whether or not
    // we'll go on to actually change selectedTab.
    this._ensureTabLoaded(tab);

    if (tab === gBrowser.selectedTab) {
      return;
    }

    let oldTab = gBrowser.selectedTab;
    let newBrowser = tab.linkedBrowser;
    let oldBrowser = oldTab.linkedBrowser;

    // Preserve the OLD selected tab's layers so its overlay content
    // doesn't get torn down during the switch (we still want it to show
    // a live preview-ish state until a thumbnail captures).
    try {
      oldBrowser?.preserveLayers(true);
    } catch (e) {}

    // Activate the NEW tab's docshell synchronously and ensure its layers
    // are ready, so AsyncTabSwitcher doesn't need to spin up the
    // compositor during the actual selectedTab assignment.
    if (newBrowser) {
      try {
        if (!newBrowser.docShellIsActive) {
          newBrowser.docShellIsActive = true;
        }
        newBrowser.preserveLayers(false);
      } catch (e) {}
    }

    // Pre-apply overlay styles so the new stack is already positioned at
    // its small node-body location before the deck transition runs.
    this._applyOverlayToTab(tab);

    this._internalTabSelect = true;
    try {
      gBrowser.selectedTab = tab;
    } finally {
      this._internalTabSelect = false;
    }

    // Selecting a tab triggers Firefox's _adjustFocusAfterTabSwitch which
    // moves keyboard focus to the new browser's content. While in canvas
    // mode that would steal keyboard focus from the canvas — arrow keys,
    // Enter, etc. would all start going to the page instead of doing
    // canvas navigation. Pull focus back to the canvas container.
    document.getElementById("tab-canvas-inner")?.focus();

    // Re-apply (the selectedTab assignment may have synchronously emitted
    // events that touched layout) and re-sync overlays.
    this._applyOverlayToTab(tab);
    this._updateAllBrowserOverlays();
    // Capture thumbnail for the previously-selected tab after a tick so
    // its layers have settled in their new (non-selected) state. The
    // focus refocus is also re-applied here in case any async chrome
    // logic (e.g. the AsyncTabSwitcher's finish step) reasserts content
    // focus after the synchronous selection change.
    requestAnimationFrame(() => {
      this._captureAllThumbnails();
      document.getElementById("tab-canvas-inner")?.focus();
      try {
        oldBrowser?.preserveLayers(false);
      } catch (e) {}
    });
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
    // Use "cover" scaling so the browser fills the body in both
    // dimensions (clipping excess on the wider axis). "Contain" scaling
    // by width alone leaves a vertical gap when the browser is wider
    // than the node body, exposing the thumbnail behind the overlay.
    let scaleFactor = Math.max(
      bodyRect.width / browserW,
      bodyRect.height / browserH
    );

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
    // Only the selected tab gets a live browser overlay. Non-selected
    // tabs are hidden by the deck's default visibility behavior, so we
    // don't need to clear their inline overlay styles here — that would
    // cause a brief flash where the old selected tab's stack reverts to
    // full-size deck layout before the deck-selected class moves. hide()
    // clears all stacks when canvas closes.
    let selectedTab = gBrowser.selectedTab;
    if (selectedTab) {
      this._applyOverlayToTab(selectedTab);
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
    // Also suppress canvas-exit-on-TabSelect across the next event tick,
    // in case a browser API we called (addTabGroup, addTabs, ungroupTab,
    // etc.) queues a TabSelect on a later turn after _syncing has
    // already cleared.
    this._suppressHide = true;
    try {
      fn();
    } finally {
      this._syncing = false;
      setTimeout(() => { this._suppressHide = false; }, 0);
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
      // Tab moved out of a frame on the canvas: remove it from the
      // corresponding browser tab group.
      if (tab.group && tab.group.id === prevGroupId) {
        this._withSync(() => gBrowser.ungroupTab(tab));
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
      this._withSync(() => this._canvas.assignNodeToFrame(nodeId, frameId));
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
      // Only claim keys when keyboard focus is actually inside the canvas
      // (not on the live <browser> overlay or the URL bar). Otherwise the
      // user clicking into a tab preview can't use arrow keys / Enter in
      // the page itself.
      let canvasInner = document.getElementById("tab-canvas-inner");
      let focusInCanvas = canvasInner &&
        (document.activeElement === canvasInner ||
         canvasInner.contains(document.activeElement));
      if (!focusInCanvas) {
        return;
      }

      // Only prevent default for keys the canvas engine handles,
      // so F5, F12, url bar typing, etc. still work.
      let canvasKeys = [
        "h", "v", "f", "t", " ",
        "Delete", "Backspace",
        "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
        "Escape", "Enter",
      ];
      if (!event.ctrlKey && !event.metaKey && canvasKeys.includes(event.key)) {
        event.preventDefault();
      }
      // For Ctrl/Cmd shortcuts the canvas claims, swallow the chrome
      // default (Cmd+G = Find Again, Cmd+D = Bookmark, etc.) via
      // preventDefault. We deliberately do NOT stopPropagation here:
      // the capture phase is descending toward the canvas container's
      // own keydown listener, and stopping propagation would prevent
      // the engine from ever seeing the key (which would break the
      // actual grouping/duplicate/etc. behavior).
      if ((event.ctrlKey || event.metaKey) &&
          ["g", "d", "a", "z", "0", "1", "=", "-"].includes(event.key)) {
        event.preventDefault();
      }
    }
  },

  _onTabOpen(event) {
    if (!this._active) {
      return;
    }
    let tab = event.target;
    // Place the new node next to its opener tab (set when middle-clicking
    // a link, ctrl-clicking, window.open, etc.). Falls back to empty space.
    let opener = tab.openerTab || tab.owner;
    let pos = opener ? this._findPositionNearOpener(opener) : this._findEmptyPosition();
    this._addTabNode(tab, 0, 4, pos.x, pos.y);

    // If the new tab joins a tab group via opener, sync into the canvas
    // frame as well so it's visually inside the frame (auto-expand grows
    // the frame to contain the new node).
    if (tab.group) {
      let frameId = this._tabGroupToCanvas.get(tab.group.id);
      if (frameId) {
        let nodeId = this._tabToId.get(tab);
        if (nodeId) {
          this._withSync(() => this._canvas.assignNodeToFrame(nodeId, frameId));
        }
      }
    }

    this._updateAllBrowserOverlays();
    this._scheduleSave();
  },

  _onTabClose(event) {
    let tab = event.target;
    let id = this._tabToId.get(tab);
    if (id) {
      // If the tab was zoomed in, restore the previously-saved view
      // before removing the node so the canvas returns to where it was.
      // (Engine's removeNode auto-shrinks the containing frame too.)
      if (this._active) {
        this._canvas.restoreSavedView(id);
      }
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
    // Tab selection initiated by something the canvas did — either a
    // direct canvas click (_internalTabSelect) or as a side effect of a
    // canvas → browser sync call like addTabGroup/ungroupTabs/ungroupTab
    // (_syncing/_suppressHide). Stay in canvas mode.
    if (this._internalTabSelect || this._syncing || this._suppressHide) {
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
