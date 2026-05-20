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
var { CanvasDebugConsole } = ChromeUtils.importESModule(
  "chrome://browser/content/tabcanvas/canvas-debug-console.mjs",
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

  // Verbose logging for the lazy-tab wakeup path, gated behind the
  // browser.tabcanvas.debug pref. Read once in init() so per-event
  // checks don't hit the pref service. Off by default.
  _tabcanvasDebug: false,

  // Tab <-> canvas node ID mappings
  _tabToId: new WeakMap(),
  _idToTab: new Map(),

  // Browsers currently in preserveLayers(true) state because we're holding
  // the previous selection alive across a canvas-initiated tab switch.
  // Tracked so rapid switches (alt+arrow, Ctrl+Tab cycling) don't leak.
  _preservedLayerBrowsers: new Set(),

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
      this._tabKeys.set(key, "tab_" + this._nextKeyId++);
    }
    return this._tabKeys.get(key);
  },

  init() {
    this._tabcanvasDebug = Services.prefs.getBoolPref(
      "browser.tabcanvas.debug",
      false
    );

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
    // Debug console mounted inside the canvas overlay. Toggleable via
    // its own button, plus an Alt+Shift+D shortcut handled in keydown.
    this._debugConsole = new CanvasDebugConsole(
      this._canvas,
      document.getElementById("tab-canvas-inner")
    );

    // Track canvas .on() subscriptions so uninit can pair them with .off().
    this._canvasSubs = [];
    let onCanvas = (eventName, cb) => {
      this._canvas.on(eventName, cb);
      this._canvasSubs.push([eventName, cb]);
    };

    // Tabbrowser tabContainer events all route through handleEvent; collect
    // the names so uninit can remove them in one loop.
    this._tabContainerEvents = [
      "TabOpen",
      "TabClose",
      "TabAttrModified",
      "TabSelect",
      "TabPinned",
      "TabUnpinned",
      "TabGroupCreate",
      "TabGroupRemoved",
      "TabGroupUpdate",
      "TabGrouped",
      "TabUngrouped",
    ];

    // --- Canvas event handlers ---

    onCanvas("node-dblclick", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (tab) {
        gBrowser.selectedTab = tab;
        this.hide();
      }
    });

    onCanvas("node-click", ({ id, altKey }) => {
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
        this._canvas.toggleZoomToNode(zoomTargetId, {
          padding: 56,
          maxZoom: 3,
        });
      }
      this._selectTabFromCanvas(id);
    });

    onCanvas("node-zoom-toggle", ({ id }) => {
      // Clicking the zoom button on a tab card should also focus that
      // tab — both on the canvas (visual selection) and in the browser
      // (live overlay target). For frame zoom buttons the canvas
      // selection still moves to the frame.
      if (this._canvas.getNode(id) || this._canvas._frames.has(id)) {
        this._canvas.deselectAll();
        if (this._canvas._frames.has(id)) {
          this._canvas._selectFrameWithChildren(id);
        } else {
          this._canvas.select(id);
        }
      }
      this._selectTabFromCanvas(id);
    });

    onCanvas("node-delete", ({ id }) => {
      let tab = this._idToTab.get(id);
      if (!tab) {
        return;
      }
      this._closeTabFromCanvas(tab, id);
    });

    onCanvas("escape", () => {
      if (this._canvas.getSelection().length === 0) {
        this.hide();
      }
    });

    onCanvas("selection-change", ({ selection }) => {
      this._scheduleSelectionSync(selection);
    });

    onCanvas("view-change", () => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
    });

    onCanvas("node-move", () => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
      this._scheduleSave();
    });

    // node-drag fires on every rAF tick during a drag (vs node-move
    // which only fires once at drag end). We need this so the live
    // browser overlay tracks the selected tab while it's being moved.
    onCanvas("node-drag", ({ id }) => {
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

    onCanvas("node-resize", () => {
      if (this._active) {
        this._scheduleOverlayUpdate();
      }
      this._scheduleSave();
    });

    onCanvas("frame-create", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameCreate(id);
    });

    onCanvas("frame-remove", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameRemove(id);
    });

    onCanvas("frame-label-change", ({ id }) => {
      this._scheduleSave();
      this._onCanvasFrameLabelChange(id);
    });

    onCanvas("node-frame-change", ({ id, frameId, prevFrameId }) => {
      this._scheduleSave();
      this._onCanvasNodeFrameChange(id, frameId, prevFrameId);
    });

    // --- Undo command side-effects ---
    // For each engine command pushed to the undo stack, attach a chrome
    // side-effect so that undoing also reverts the corresponding browser
    // operation (e.g. tab close, group create/remove). The side-effect
    // captures snapshots at push time so it can replay them later even
    // if external state has changed.
    onCanvas("command-pushed", ({ type }) => {
      let top = this._canvas._undoStack[this._canvas._undoStack.length - 1];
      if (!top) {
        return;
      }
      this._attachAdapterSideEffects(top, type);
    });

    // --- Tab event handlers ---

    for (let name of this._tabContainerEvents) {
      gBrowser.tabContainer.addEventListener(name, this);
    }

    // Capture phase to intercept before XUL key handlers
    document.addEventListener("keydown", this, true);
    window.addEventListener("resize", this);
    window.addEventListener("unload", () => this.uninit(), { once: true });
  },

  uninit() {
    for (let name of this._tabContainerEvents || []) {
      gBrowser.tabContainer.removeEventListener(name, this);
    }
    document.removeEventListener("keydown", this, true);
    window.removeEventListener("resize", this);
    if (this._canvas && this._canvasSubs) {
      for (let [name, cb] of this._canvasSubs) {
        this._canvas.off(name, cb);
      }
    }
    this._canvasSubs = [];
    clearTimeout(this._saveTimer);
    this._saveTimer = null;
  },

  handleEvent(event) {
    // Trace every browser → canvas event so bug reports can show exactly
    // which external signal triggered a downstream canvas mutation. Skip
    // keydown / resize: they fire constantly and the interesting ones are
    // already traced via canvas-level events.
    if (event.type !== "keydown" && event.type !== "resize") {
      let detail = this._describeBrowserEvent(event);
      this._canvas?.debugLog("info", "browser event", detail);
    }
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

  _describeBrowserEvent(event) {
    let detail = { type: event.type };
    let tab = event.target;
    if (tab && tab.tagName === "tab") {
      detail.tab = {
        label: tab.label,
        pinned: !!tab.pinned,
        groupId: tab.group?.id || null,
        permanentKey: this._tabKeys?.get(tab.permanentKey) || null,
      };
    }
    let group = event.detail?.group || event.target;
    if (group && group.tagName === "tab-group") {
      detail.group = { id: group.id, label: group.label, color: group.color };
    }
    if (event.detail && typeof event.detail === "object") {
      // Surface a small subset of detail fields without dumping the whole DOM tree.
      let { changed } = event.detail;
      if (changed) {
        detail.changed = changed;
      }
    }
    return detail;
  },

  // --- Show / Hide ---

  toggle() {
    this._canvas?.debugLog("info", "toggle", { from: this._active ? "shown" : "hidden" });
    if (this._active) {
      this.hide();
    } else {
      this.show();
    }
  },

  show() {
    this._canvas?.debugLog("info", "show", {
      tabCount: gBrowser.tabs.length,
      selectedTab: gBrowser.selectedTab?.label,
      initialized: !!this._initialized,
    });
    this._active = true;
    // Reset placement cursor on each show so a new session starts from
    // current canvas bounds rather than wherever the last one left off.
    this._nextPlacementX = 0;
    this._nextPlacementY = null;

    // Capture native browser dimensions before we apply fixed positioning
    let selectedStack = gBrowser.selectedBrowser?.closest(".browserStack");
    if (selectedStack) {
      this._browserNativeWidth = selectedStack.clientWidth || 1;
      this._browserNativeHeight = selectedStack.clientHeight || 1;
    }

    this._overlay.setAttribute("active", "true");
    document
      .getElementById("tabbrowser-tabpanels")
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
    this._canvas?.debugLog("info", "hide");
    this._active = false;
    this._overlay.removeAttribute("active");
    document
      .getElementById("tabbrowser-tabpanels")
      .removeAttribute("tabcanvas-active");
    this._clearAllBrowserOverlays();
    // Release any browsers we were keeping alive via preserveLayers(true)
    // for canvas-driven switches.
    for (let preserved of this._preservedLayerBrowsers) {
      try {
        preserved.preserveLayers(false);
      } catch (e) {}
    }
    this._preservedLayerBrowsers.clear();
    this._save();
  },

  // --- Persistence ---

  _scheduleSave() {
    clearTimeout(this._saveTimer);
    this._saveTimer = setTimeout(() => this._save(), 500);
  },

  _SCHEMA_VERSION: 1,

  _save() {
    if (!this._initialized) {
      return;
    }
    let data = this._canvas.toJSON();
    data.schemaVersion = this._SCHEMA_VERSION;
    data.tabMap = {};
    let tabs = Array.from(gBrowser.tabs);
    for (let [id, tab] of this._idToTab) {
      data.tabMap[id] = {
        url: tab.linkedBrowser?.currentURI?.spec || "",
        title: tab.label || "",
        userContextId: tab.userContextId || 0,
        pinned: !!tab.pinned,
        tabIndex: tabs.indexOf(tab),
      };
    }
    data.groupMap = {};
    for (let [canvasId, groupId] of this._canvasToTabGroup) {
      data.groupMap[canvasId] = groupId;
    }
    try {
      SessionStore.setCustomWindowValue(
        window,
        "tabCanvasLayout",
        JSON.stringify(data)
      );
    } catch (e) {
      console.error("TabCanvas: failed to persist layout", e);
    }
  },

  _backupBrokenLayout(raw, err) {
    try {
      SessionStore.setCustomWindowValue(window, "tabCanvasLayout.broken", raw);
    } catch (e) {
      // Best effort.
    }
    console.error(
      "TabCanvas: failed to restore layout, backed up at tabCanvasLayout.broken",
      err
    );
  },

  _loadSavedLayout() {
    let saved;
    try {
      saved = SessionStore.getCustomWindowValue(window, "tabCanvasLayout");
    } catch (e) {
      // SessionStore not ready yet.
      return null;
    }
    if (!saved) {
      return null;
    }
    let parsed;
    try {
      parsed = JSON.parse(saved);
    } catch (e) {
      this._backupBrokenLayout(saved, e);
      return null;
    }
    if (parsed?.schemaVersion !== this._SCHEMA_VERSION) {
      this._backupBrokenLayout(
        saved,
        new Error(
          `schemaVersion mismatch: got ${parsed?.schemaVersion}, expected ${this._SCHEMA_VERSION}`
        )
      );
      return null;
    }
    return parsed;
  },

  _restoreLayout(data) {
    this._canvas.fromJSON(data);

    let currentTabs = Array.from(gBrowser.tabs);
    let unmatched = new Set(currentTabs);
    let tabMap = data.tabMap || {};

    // Lazy/pending tabs expose their would-be url/title via SessionStore's
    // lazy-tab values; fall back to those when currentURI/label are stubs.
    let tabUrl = tab => {
      let url = tab.linkedBrowser?.currentURI?.spec || "";
      if (url && url !== "about:blank") {
        return url;
      }
      try {
        return SessionStore.getLazyTabValue(tab, "url") || url;
      } catch (e) {
        return url;
      }
    };
    let tabTitle = tab => {
      if (tab.label) {
        return tab.label;
      }
      try {
        return SessionStore.getLazyTabValue(tab, "title") || "";
      } catch (e) {
        return "";
      }
    };

    for (let savedNode of data.nodes) {
      let saved = tabMap[savedNode.id];
      if (!saved) {
        continue;
      }
      let bestTab = null;
      let bestScore = 0;
      let bestIndexDelta = Infinity;
      for (let tab of unmatched) {
        let url = tabUrl(tab);
        let title = tabTitle(tab);
        let score = 0;
        if (saved.url && url === saved.url && url !== "about:blank") {
          score += 10;
        }
        if (saved.title && title === saved.title && title !== "New Tab") {
          score += 5;
        }
        if ((tab.userContextId || 0) === (saved.userContextId || 0)) {
          score += 3;
        }
        if (!!tab.pinned === !!saved.pinned) {
          score += 1;
        }
        if (score < bestScore) {
          continue;
        }
        let indexDelta = Math.abs(
          currentTabs.indexOf(tab) - (saved.tabIndex ?? 0)
        );
        if (
          score > bestScore ||
          (score === bestScore && indexDelta < bestIndexDelta)
        ) {
          bestScore = score;
          bestTab = tab;
          bestIndexDelta = indexDelta;
        }
      }
      // Require at least a title or URL hit (5+) so the userContextId/pinned
      // bonuses can't false-match two unrelated default-context tabs.
      if (bestTab && bestScore >= 5) {
        let id = this._getTabId(bestTab);
        // Remap if the saved ID doesn't match the new stable ID
        if (id !== savedNode.id) {
          let nodeObj = this._canvas.getNode(savedNode.id);
          if (nodeObj) {
            this._canvas.removeNode(savedNode.id);
            this._canvas.addNode(id, {
              x: savedNode.x,
              y: savedNode.y,
              width: savedNode.width,
              height: savedNode.height,
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

    // Keep orphan nodes (saved layout with no current matching tab) so
    // users don't silently lose layout. Mark with data-orphan so we can
    // style them and so other handlers (which lookup via _idToTab) skip
    // them naturally.
    for (let savedNode of data.nodes) {
      if (!this._idToTab.has(savedNode.id)) {
        let nodeEl = this._canvas.getNode(savedNode.id)?.element;
        if (nodeEl) {
          nodeEl.setAttribute("data-orphan", "true");
        }
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

    // Make sure every restored frame still contains all of its children
    // (saved-state padding/positions may not match the engine's current
    // auto-expand padding, especially if children were nudged after the
    // last save).
    for (let savedFrame of data.frames || []) {
      this._canvas.autoExpandFrame(savedFrame.id);
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
      x,
      y,
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
          blue: "#0a84ff",
          turquoise: "#00c8d7",
          green: "#44b700",
          yellow: "#ffbd4f",
          orange: "#ff9400",
          red: "#ff0039",
          pink: "#ff2a8a",
          purple: "#9400ff",
        };
        let c = colorMap[identity.color] || "#666";
        this._canvas.setNodeColor(id, null, c);
      }
    }

    if (tab === gBrowser.selectedTab) {
      this._canvas.select(id);
    }
  },

  _findEmptyPosition(height = 212) {
    // Seed the cursor lazily from current canvas bounds so concurrent
    // TabOpen events (session restore, "Open all in tabs") don't stack
    // every new tab at the same coordinate. The cursor advances per
    // call; show() resets it.
    if (this._nextPlacementY === null) {
      let bounds = this._canvas._getAllBounds();
      this._nextPlacementX = bounds ? bounds.x : 0;
      this._nextPlacementY = bounds ? bounds.y + bounds.height + 40 : 0;
    }
    let pos = { x: this._nextPlacementX, y: this._nextPlacementY };
    this._nextPlacementY += height + 40;
    return pos;
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
    let header = document.createElementNS(
      "http://www.w3.org/1999/xhtml",
      "div"
    );
    header.style.cssText = "display:flex;align-items:center;gap:8px;width:100%";

    let pinEl = null;
    if (tab.pinned) {
      pinEl = document.createElementNS("http://www.w3.org/1999/xhtml", "img");
      pinEl.style.cssText = "width:12px;height:12px;flex-shrink:0";
      pinEl.src = "chrome://global/skin/icons/pin-12.svg";
      pinEl.draggable = false;
      header.appendChild(pinEl);
    }

    let favicon = document.createElementNS(
      "http://www.w3.org/1999/xhtml",
      "img"
    );
    favicon.style.cssText = "width:16px;height:16px;flex-shrink:0";
    favicon.src =
      tab.getAttribute("image") ||
      "chrome://global/skin/icons/defaultFavicon.svg";
    favicon.draggable = false;
    header.appendChild(favicon);

    let title = document.createElementNS(
      "http://www.w3.org/1999/xhtml",
      "span"
    );
    // min-width:0 is required so flex shrinking can truncate the text below
    // its intrinsic content width; otherwise a long title pushes the zoom
    // button past the node's overflow:hidden boundary.
    title.style.cssText =
      "color:#e0e0e0;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0";
    title.textContent = tab.label || "New Tab";
    header.appendChild(title);

    // Prefer the explicit nodeId argument over the map lookup. Some call
    // sites (e.g. _restoreLayout) build the header before populating
    // _tabToId; in that case we still need the zoom button.
    let id = nodeId || this._tabToId.get(tab);
    if (id) {
      // Fit options for the integration: a bit of breathing room around
      // the zoomed tab while still filling most of the canvas.
      header.appendChild(
        this._canvas.createZoomButton(id, {
          padding: 56,
          maxZoom: 3,
        })
      );
      // The shared close button removes the node and emits node-delete;
      // our node-delete handler turns that into gBrowser.removeTab.
      header.appendChild(this._canvas.createCloseButton(id));
    }

    // Stash refs on the header itself so _updateTabHeader can mutate the
    // mutable bits (title/favicon/pin) in-place without rebuilding the
    // whole subtree (which would orphan the close/zoom buttons' listeners
    // and force an engine re-layout on every TabAttrModified event).
    header._titleEl = title;
    header._faviconEl = favicon;
    header._pinEl = pinEl;
    header._pinned = !!tab.pinned;

    return header;
  },

  // Shared close logic used by both the X button and the node-delete
  // event (Delete key / context menu). Restores any saved zoom-in view
  // for the closing tab, then removes the tab. If the tab is currently
  // selected, suppresses the auto-hide that would normally follow.
  // Attach chrome side-effects to a freshly-pushed engine command.
  // Each engine command type has a different policy:
  //   - "delete": if the user just closed a tab through the canvas, the
  //     side-effect calls SessionStore.undoCloseTab on undo so the tab
  //     comes back. Multiple tabs in one batch get multiple restores.
  //     We deliberately do NOT attach a side-effect for tab closes that
  //     originated outside the canvas (tab strip, Ctrl+W) — those have
  //     their own browser-level undo.
  //   - "group" / "draw-frame": adapter created a browser tab group as
  //     a side effect; undo should ungroup it, redo should recreate.
  //   - "ungroup": adapter ungrouped a browser tab group; undo restores
  //     the group (via savedGroup or by re-creating from member tabs).
  // Other engine command types are pure canvas (z-order, color, rename,
  // layout, etc.) — no browser-side mirror.
  _attachAdapterSideEffects(cmd, type) {
    if (type === "delete") {
      let pending = this._pendingCanvasCloses || 0;
      this._pendingCanvasCloses = 0;
      if (pending <= 0) {
        // The delete batch didn't include any canvas-initiated tab
        // closes (e.g. it was a frame-only delete). Nothing to attach.
        return;
      }
      cmd.attach({
        undo: () => {
          for (let i = 0; i < pending; i++) {
            try {
              SessionStore.undoCloseTab(window);
            } catch (e) {
              this._canvas.debugLog("warn", "undoCloseTab failed", { error: String(e) });
            }
          }
        },
        redo: () => {
          // Best-effort: redo re-closes tabs that were just restored.
          // We don't track which restored tabs correspond to which
          // engine nodes, so close the most-recently-restored ones.
          this._canvas.debugLog("info", "redo of canvas tab close: not yet implemented");
        },
      });
    }
  },

  _closeTabFromCanvas(tab, nodeId) {
    this._canvas.debugLog("info", "side-effect → removeTab", {
      nodeId, label: tab.label, wasSelected: tab === gBrowser.selectedTab,
    });
    // If the user had zoomed in on this tab, animate back to the
    // previous view before the node disappears. The engine's removeNode
    // also auto-shrinks the containing frame to fit the remaining nodes.
    if (nodeId) {
      this._canvas.restoreSavedView(nodeId);
    }
    // Track canvas-initiated closes so the upcoming engine "delete"
    // command can be enriched with a SessionStore.undoCloseTab
    // side-effect. External tab closes (via tab strip, Ctrl+W) shouldn't
    // be tagged.
    this._pendingCanvasCloses = (this._pendingCanvasCloses || 0) + 1;
    let wasSelected = tab === gBrowser.selectedTab;
    this._canvasInitiatedClose = true;
    if (wasSelected) {
      this._internalTabSelect = true;
      // gBrowser.removeTab can dispatch TabSelect deferred via
      // AsyncTabSwitcher; use the refcount so a late event doesn't
      // trigger hide().
      this._suppressHideRefCount++;
    }
    try {
      gBrowser.removeTab(tab);
    } finally {
      this._canvasInitiatedClose = false;
      if (wasSelected) {
        this._internalTabSelect = false;
        setTimeout(() => this._suppressHideRefCount--, 0);
        // gBrowser auto-selected an adjacent tab on close. Mirror that
        // into the canvas selection so the new active tab is visually
        // highlighted, and apply the live overlay to it.
        let newId = this._tabToId.get(gBrowser.selectedTab);
        if (newId) {
          this._canvas.deselectAll();
          this._canvas.select(newId);
        }
        this._applyOverlayToTab(gBrowser.selectedTab);
        this._captureAllThumbnails();
        // Keep canvas keyboard focus after the close so subsequent
        // arrow / Enter keys keep navigating the canvas.
        document.getElementById("tab-canvas-inner")?.focus();
      }
    }
  },

  _updateTabHeader(tab, id) {
    let node = this._canvas.getNode(id);
    let label = tab.label || "New Tab";
    // Fast path: if the existing header DOM is still attached and its
    // structural attributes (pinned) match the tab, mutate the
    // title/favicon in place. updateNode() rebuilds the engine's DOM and
    // re-triggers layout; we want to avoid that for label/icon churn.
    let header = node?.element?.querySelector(".infinite-canvas-node-header");
    let existing = header?.firstElementChild;
    if (
      existing &&
      existing._titleEl &&
      existing._faviconEl &&
      existing._pinned === !!tab.pinned
    ) {
      if (existing._titleEl.textContent !== label) {
        existing._titleEl.textContent = label;
      }
      let src =
        tab.getAttribute("image") ||
        "chrome://global/skin/icons/defaultFavicon.svg";
      if (existing._faviconEl.src !== src) {
        existing._faviconEl.src = src;
      }
      if (node.title !== label) {
        node.title = label;
      }
      return;
    }
    // Structural change (pinned/crashed toggled, or first-time build):
    // fall back to a full header rebuild via updateNode.
    this._canvas.updateNode(id, {
      title: label,
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
  //
  // Engine paths that emit one selection-change per tab toggle (Ctrl+A,
  // marquee select, etc.) can cascade into N events in the same task,
  // each clearing the tab strip selection and re-adding tabs one by one.
  // Coalesce via microtask so we only sync the latest selection once.
  _scheduleSelectionSync(selection) {
    this._pendingSelectionSync = selection;
    if (this._selectionSyncPending) {
      return;
    }
    this._selectionSyncPending = true;
    Promise.resolve().then(() => {
      this._selectionSyncPending = false;
      let latest = this._pendingSelectionSync;
      this._pendingSelectionSync = null;
      if (latest) {
        this._syncSelectionToTabbrowser(latest);
      }
    });
  },

  _syncSelectionToTabbrowser(selection) {
    if (this._internalTabSelect) {
      // Already in the middle of a single-tab select; selection-change will
      // fire again after the dust settles.
      return;
    }
    // Collect both the tabs and their canvas ids in the same order as
    // they appear in the selection set.
    let tabs = [];
    let desiredTabSet = new Set();
    let firstTabNodeId = null;
    for (let id of selection) {
      let tab = this._idToTab.get(id);
      if (tab) {
        tabs.push(tab);
        desiredTabSet.add(tab);
        if (firstTabNodeId === null) {
          firstTabNodeId = id;
        }
      }
    }

    // If exactly one tab is selected (e.g. via alt+arrow navigation,
    // Enter to drill into a frame, etc.) make it the active browser tab
    // so the live overlay renders that tab's content. Skip if it's
    // already selected.
    if (tabs.length === 1 && tabs[0] !== gBrowser.selectedTab) {
      this._ensureTabLoaded(tabs[0]);
      this._selectTabFromCanvas(firstTabNodeId);
    }

    // Diff against the existing multi-selection and apply only the delta
    // so we avoid one TabSelectMultiple dispatch (and tab strip repaint)
    // per tab on big selections. Uses the private _multiSelectedTabsSet
    // for O(1) membership checks; the public selectedTabs getter would
    // include the current selectedTab even when not multi-selected.
    let currentSet = gBrowser._multiSelectedTabsSet;
    // _withSync bumps _suppressHideRefCount so any TabSelect dispatched as
    // a side effect of these multi-select changes won't exit the canvas.
    this._withSync(() => {
      if (tabs.length < 2) {
        // Single (or zero) tab selection on the canvas should leave the
        // tab strip in a non-multi-selected state.
        gBrowser.clearMultiSelectedTabs();
        return;
      }
      // Remove tabs that are no longer selected.
      let multiselected = gBrowser.visibleTabs.filter(t => t.multiselected);
      for (let tab of multiselected) {
        if (!desiredTabSet.has(tab)) {
          gBrowser.removeFromMultiSelectedTabs(tab);
        }
      }
      // Add tabs that newly entered the selection. Only newly-added tabs
      // need _ensureTabLoaded — already-selected tabs were woken on a
      // prior event.
      for (let tab of tabs) {
        if (!currentSet.has(tab)) {
          gBrowser.addToMultiSelectedTabs(tab);
          this._ensureTabLoaded(tab);
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
      // Tab labels and URIs are PII; log only non-identifying state.
      console.warn("[tabcanvas] _ensureTabLoaded", {
        pending: hasPending,
        discarded: hasDiscarded,
        linkedPanel: !!tab.linkedPanel,
        docShellIsActive: browser?.docShellIsActive,
        needsLoad,
        alreadyLoading: this._loadingTabs?.has(tab),
      });
    }

    // Activate the docshell unconditionally for any non-selected tab in
    // canvas mode. Most tabs in a browser are loaded-but-inactive
    // (docShellIsActive=false) — they need this flip to actually paint
    // so PageThumbs can capture real content. This is an explicit
    // deviation from the general "don't activate non-selected docshells"
    // rule, accepted here because the canvas IS the user-facing reason
    // those tabs need to render. AsyncTabSwitcher / audio focus get
    // their normal signals back when the canvas closes and the deck
    // resumes ownership.
    if (browser && !browser.docShellIsActive) {
      try {
        browser.docShellIsActive = true;
      } catch (e) {}
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
      // After insertBrowser the browser may be brand new and still
      // inactive; flip again so the just-materialized docshell paints.
      if (browser && !browser.docShellIsActive) {
        try {
          browser.docShellIsActive = true;
        } catch (e) {}
      }
      // Three complementary wake-up triggers — whichever applies fires:
      //   - TabShow → SessionStore.onTabShow → queues restore via
      //     restoreNextTab(). This is the path Firefox uses when a
      //     hidden tab becomes visible. SessionStore enforces a restore
      //     concurrency limit, so on a session with many pending tabs
      //     this alone is not enough to wake them all promptly.
      //   - browser.reload() → for pending/discarded tabs, kicks off the
      //     URI load directly. For lazy browsers the `reload` getter
      //     chains _insertBrowser + SSTabRestoring + the real reload.
      //     This bypasses the SessionStore concurrency limit and is
      //     the primary reason all canvas previews render after a
      //     session restore.
      //   - docShellIsActive activation (above) — makes the browser paint
      //     once content arrives.
      try {
        tab.dispatchEvent(new CustomEvent("TabShow", { bubbles: true }));
      } catch (e) {}
      if ((hasPending || hasDiscarded) && browser?.reload) {
        try {
          browser.reload();
        } catch (e) {}
      }
      // Once the tab actually finishes loading, re-capture its thumbnail
      // so the canvas body shows real content instead of the placeholder
      // that may have been captured while the tab was still discarded.
      // pageshow / SSTabRestored both fire before the page has had time
      // to actually paint, so we schedule two delayed captures: a quick
      // one for fast-painting pages and a later one to catch async
      // content (web fonts, lazy images, hydration). Each one replaces
      // the previous bodyContent in the canvas node.
      let scheduleDelayedCapture = (delay, key) => {
        this._thumbCaptureTimers ??= new WeakMap();
        let timers = this._thumbCaptureTimers.get(tab) || {};
        clearTimeout(timers[key]);
        timers[key] = setTimeout(() => {
          let nodeId = this._tabToId.get(tab);
          if (nodeId && this._active) {
            this._captureThumbnail(tab, nodeId);
          }
        }, delay);
        this._thumbCaptureTimers.set(tab, timers);
      };
      let onLoad = () => {
        tab.removeEventListener("SSTabRestored", onLoad);
        tab.linkedBrowser?.removeEventListener("pageshow", onLoad, true);
        // Clear from _loadingTabs so a re-discarded tab can be re-loaded
        // (memory pressure can discard a tab again later in the session).
        this._loadingTabs?.delete(tab);
        scheduleDelayedCapture(600, "fast");
        scheduleDelayedCapture(2500, "slow");
      };
      tab.addEventListener("SSTabRestored", onLoad, { once: true });
      try {
        tab.linkedBrowser?.addEventListener("pageshow", onLoad, {
          once: true,
          capture: true,
        });
      } catch (e) {}
      if (this._tabcanvasDebug) {
        console.warn("[tabcanvas] _ensureTabLoaded -> dispatched", {
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
    this._canvas.debugLog("info", "side-effect → selectedTab", {
      nodeId, label: tab.label, prev: gBrowser.selectedTab?.label,
    });

    let oldTab = gBrowser.selectedTab;
    let newBrowser = tab.linkedBrowser;
    let oldBrowser = oldTab.linkedBrowser;

    // Release any previously-preserved browsers from prior canvas switches
    // before adding a new one. If the user clicks tabs rapidly (alt+arrow,
    // Ctrl+Tab), stale preserveLayers(true) entries would otherwise leak.
    for (let preserved of this._preservedLayerBrowsers) {
      try {
        preserved.preserveLayers(false);
      } catch (e) {}
    }
    this._preservedLayerBrowsers.clear();

    // Preserve the OLD selected tab's layers so its overlay content
    // doesn't get torn down during the switch (we still want it to show
    // a live preview-ish state until a thumbnail captures).
    if (oldBrowser) {
      try {
        oldBrowser.preserveLayers(true);
        this._preservedLayerBrowsers.add(oldBrowser);
      } catch (e) {}
    }

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

    // gBrowser.selectedTab = tab may dispatch TabSelect on a deferred tick
    // (AsyncTabSwitcher can wait for layers). The deferred event would
    // arrive after _internalTabSelect was cleared in finally and trigger
    // _onTabSelect -> hide(). Bump _suppressHideRefCount and decrement on
    // the next event-loop tick so the deferred dispatch is still
    // suppressed.
    this._internalTabSelect = true;
    this._suppressHideRefCount = (this._suppressHideRefCount || 0) + 1;
    try {
      gBrowser.selectedTab = tab;
    } finally {
      this._internalTabSelect = false;
      setTimeout(() => {
        this._suppressHideRefCount--;
      }, 0);
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
    // focus after the synchronous selection change. The OLD browser's
    // preserveLayers(true) is intentionally NOT released here: the overlay
    // move keeps the layers alive, and the entry is released on the next
    // canvas switch or in hide().
    requestAnimationFrame(() => {
      this._captureAllThumbnails();
      document.getElementById("tab-canvas-inner")?.focus();
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
    if (!stack || !stack.parentNode) {
      return;
    }

    // Compute the position-fixed origin offset every call rather than
    // caching it. The cache was only invalidated on hide()/window-resize,
    // missing devtools dock/undock, fullscreen toggles, sidebar/megabar
    // expansion, and DPR changes from monitor moves. A single layout
    // probe per overlay update is cheap. try/finally guarantees the
    // probe is removed if getBoundingClientRect (or anything else)
    // throws.
    let fixedOffset;
    let probe = document.createElementNS("http://www.w3.org/1999/xhtml", "div");
    probe.style.cssText =
      "position:fixed;left:0;top:0;width:1px;height:1px;pointer-events:none;z-index:-1";
    stack.parentNode.appendChild(probe);
    try {
      let probeRect = probe.getBoundingClientRect();
      fixedOffset = { x: probeRect.left, y: probeRect.top };
    } finally {
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
    stack.style.left = bodyRect.left - fixedOffset.x + "px";
    stack.style.top = bodyRect.top - fixedOffset.y + "px";
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

      let thumbCanvas = document.createElementNS(
        "http://www.w3.org/1999/xhtml",
        "canvas"
      );
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
    // already cleared. Refcounted so nested / overlapping _withSync (or
    // _selectTabFromCanvas) windows don't clear early.
    this._suppressHideRefCount = (this._suppressHideRefCount || 0) + 1;
    try {
      fn();
    } finally {
      this._syncing = false;
      setTimeout(() => {
        this._suppressHideRefCount--;
      }, 0);
    }
  },

  _syncTabGroups() {
    for (let group of gBrowser.tabGroups) {
      this._importBrowserTabGroup(group);
    }
  },

  _groupColorMap: {
    blue: "#0a84ff",
    purple: "#9400ff",
    cyan: "#00c8d7",
    orange: "#ff9400",
    yellow: "#ffbd4f",
    pink: "#ff2a8a",
    green: "#44b700",
    gray: "#666",
    red: "#ff0039",
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
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity;
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

    // Belt-and-suspenders: make sure the frame actually contains all of
    // its children. The bbox calculation above should already cover this,
    // but if any child was placed with a slightly different padding (or
    // got off-grid) the auto-expand pass fixes it on first render.
    this._canvas.autoExpandFrame(frameId);

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
    this._canvas.debugLog("info", "side-effect ← frame-create", { frameId });
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
    this._canvas.debugLog("info", "side-effect → ungroupTabs", { frameId, groupId });
    let group = gBrowser.getTabGroupById(groupId);
    // Only forget the mapping after the browser-side ungroup succeeds.
    // If group.ungroupTabs() throws, the browser group still exists and
    // we want the mapping to stay so a subsequent retry / sync can pair
    // them again.
    try {
      if (group) {
        this._withSync(() => group.ungroupTabs());
      }
      this._canvasToTabGroup.delete(frameId);
      this._tabGroupToCanvas.delete(groupId);
    } catch (e) {
      console.error("[tabcanvas] _onCanvasFrameRemove failed", e);
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
    this._canvas.debugLog("info", "side-effect → tab group membership", {
      nodeId, label: tab.label, frameId, prevFrameId,
    });

    let prevGroupId = prevFrameId
      ? this._canvasToTabGroup.get(prevFrameId)
      : null;
    let newGroupId = frameId ? this._canvasToTabGroup.get(frameId) : null;

    if (frameId && !newGroupId) {
      // No browser group exists yet for this frame: create one now with
      // this tab (and any other tabs the canvas has already assigned to
      // this frame). _maybeCreateBrowserGroup → gBrowser.addTabGroup
      // moves the tab into the new group atomically, which implicitly
      // removes it from any previous group it belonged to. No explicit
      // ungroup needed here.
      this._maybeCreateBrowserGroup(frameId);
    } else if (frameId && newGroupId) {
      // Move tab into existing group. addTabs auto-removes from the
      // previous group if any.
      let group = gBrowser.getTabGroupById(newGroupId);
      if (group && tab.group !== group) {
        this._withSync(() => group.addTabs([tab]));
      }
    } else if (!frameId && prevGroupId) {
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
      this._canvas.debugLog("info", "side-effect → group label", {
        frameId, groupId, label: frame.label,
      });
      this._withSync(() => {
        group.label = frame.label;
      });
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
    // Only forget the mapping after the canvas-side frame is gone. If
    // removeFrame() throws (e.g. mid-render), the canvas frame is still
    // around and the map entries must stay so we can retry.
    try {
      this._withSync(() => this._canvas.removeFrame(frameId));
      this._canvasToTabGroup.delete(frameId);
      this._tabGroupToCanvas.delete(group.id);
    } catch (e) {
      console.error("[tabcanvas] _onBrowserTabGroupRemoved failed", e);
    }
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
    // Cmd/Ctrl+I toggles the tab canvas. Claimed globally (not gated on
    // _active) so the canvas can be opened from any chrome focus state.
    // stopPropagation only fires when we consume — this intentionally
    // overrides View:PageInfo (key_viewInfo) which is the same chord.
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

    // Alt+Shift+D toggles the debug console while canvas is active.
    if (this._active && event.altKey && event.shiftKey && event.key === "D") {
      event.preventDefault();
      event.stopPropagation();
      this._debugConsole?.toggle();
      return;
    }

    if (this._active) {
      // Only claim keys when keyboard focus is actually inside the canvas
      // (not on the live <browser> overlay or the URL bar). Otherwise the
      // user clicking into a tab preview can't use arrow keys / Enter in
      // the page itself.
      let canvasInner = document.getElementById("tab-canvas-inner");
      let focusInCanvas =
        canvasInner &&
        (document.activeElement === canvasInner ||
          canvasInner.contains(document.activeElement));
      if (!focusInCanvas) {
        return;
      }

      // Only prevent default for keys the canvas engine handles,
      // so F5, F12, url bar typing, etc. still work.
      let canvasKeys = [
        "h",
        "v",
        "f",
        "t",
        " ",
        "Delete",
        "Backspace",
        "ArrowUp",
        "ArrowDown",
        "ArrowLeft",
        "ArrowRight",
        "Escape",
        "Enter",
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
      if (
        (event.ctrlKey || event.metaKey) &&
        ["g", "d", "a", "z", "0", "1", "=", "-"].includes(event.key)
      ) {
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
    let pos = opener
      ? this._findPositionNearOpener(opener)
      : this._findEmptyPosition();
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
    let browser = tab.linkedBrowser;
    // Drop the closing tab from the preserved-layer set so we don't
    // call preserveLayers(false) on a destroyed browser in hide().
    if (browser) {
      this._preservedLayerBrowsers.delete(browser);
    }
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
    if (this._active && !this._canvasInitiatedClose) {
      // Only clear the closing tab's overlay; leaving every other tab's
      // overlay alone avoids a visible flash on the selected tab when an
      // unrelated tab closes. _closeTabFromCanvas already manages the
      // selected-tab overlay itself, so skip when it initiated the close.
      let stack = browser?.closest(".browserStack");
      if (stack && browser) {
        this._clearBrowserOverlay(stack, browser);
      }
      if (tab === gBrowser.selectedTab) {
        this._updateAllBrowserOverlays();
      }
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
    if (
      !changed ||
      changed.some(
        a =>
          a === "label" ||
          a === "image" ||
          a === "iconLoadingPrincipal" ||
          a === "pinned" ||
          a === "muted" ||
          a === "crashed"
      )
    ) {
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
    // (_syncing/_suppressHideRefCount). Stay in canvas mode.
    if (
      this._internalTabSelect ||
      this._syncing ||
      this._suppressHideRefCount > 0
    ) {
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
    // Measure native browser dimensions from the tabbox (a stable
    // ancestor whose layout doesn't depend on the position:fixed
    // overlay we may be applying to the selected stack). The earlier
    // implementation cleared the selected stack's overlay synchronously
    // to measure it, then re-applied via rAF, producing a visible
    // flicker mid-resize.
    let tabbox = gBrowser.tabbox;
    if (tabbox) {
      this._browserNativeWidth = tabbox.clientWidth || 1;
      this._browserNativeHeight = tabbox.clientHeight || 1;
    }
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
