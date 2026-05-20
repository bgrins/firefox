/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import SnapManager from "./snap-manager.mjs";

/**
 * InfiniteCanvas - A Figma-style infinite canvas engine.
 *
 * Supports pan, zoom, node selection, move, resize, snap-to-grid,
 * frames (grouping containers), marquee selection, and snap guides.
 *
 * Zero Firefox/browser-chrome dependencies - works in any web page.
 */
class InfiniteCanvas {
  static STATE_IDLE = "idle";
  static STATE_PANNING = "panning";
  static STATE_DRAGGING = "dragging";
  static STATE_RESIZING = "resizing";
  static STATE_MARQUEE = "marquee";
  static STATE_DRAWING = "drawing";

  static MIN_NODE_WIDTH = 104;
  static MIN_NODE_HEIGHT = 80;
  static MIN_ZOOM = 0.1;
  static MAX_ZOOM = 5;
  static ZOOM_STEP = 1.15;
  static HANDLE_SIZE = 8;
  static DRAG_THRESHOLD = 3;
  static SNAP_GUIDE_THRESHOLD = 6;

  constructor(container, options = {}) {
    this._container = container;
    this._gridSize = options.gridSize ?? 8;
    this._snapEnabled = options.snapEnabled ?? true;
    this._snapGuidesEnabled = options.snapGuidesEnabled ?? true;
    this._snapManager = new SnapManager({ threshold: 8 });

    this._panX = 0;
    this._panY = 0;
    this._zoom = 1;

    this._state = InfiniteCanvas.STATE_IDLE;
    this._spaceHeld = false;
    this._pointerStartX = 0;
    this._pointerStartY = 0;
    this._panStartX = 0;
    this._panStartY = 0;

    this._dragTargets = [];
    this._dragPointerId = null;
    this._dragDidMove = false;

    this._resizeTarget = null;
    this._resizeHandle = "";
    this._resizeStartRect = null;

    this._marqueeStartX = 0;
    this._marqueeStartY = 0;

    this._nodes = new Map();
    this._frames = new Map();
    this._selection = new Set();
    this._listeners = {};
    this._nextId = 1;
    // Saved view state per node ID for the zoom-to-node toggle.
    this._savedViews = new Map();
    // Adapter-customizable default options for toggleZoomToNode (used by
    // keyboard shortcut Alt+Enter and other implicit zoom invocations).
    // The chrome adapter sets tighter padding/maxZoom; standalone uses
    // the engine defaults from fitNode.
    this._defaultFitOptions = {};

    this._activeSnapGuides = [];
    this._lastClickId = null;
    this._lastClickTime = 0;
    this._undoStack = [];
    this._redoStack = [];
    // Transaction state for coalescing pushes inside a gesture.
    this._transactionDepth = 0;
    this._transactionBuffer = null;
    this._transactionLabel = null;
    this._transactionCoalesceKey = null;
    this._transactionCoalesceWindowMs = 0;
    // Debug log ring buffer (most recent N entries).
    this._debugLogBuffer = [];
    this._debugLogMax = 200;
    this._rafPending = false;
    this._pendingMoveEvent = null;
    this._guidePool = [];
    this._activeTool = "move"; // "move" or "hand"

    this._buildDOM();
    this._attachEvents();
  }

  // ---- Public API: Nodes ----

  addNode(id, { x = 0, y = 0, width = 280, height = 212, title = "", color = "#16213e", headerColor = "#0f3460", headerContent = null } = {}) {
    if (this._snapEnabled) {
      x = this._snap(x);
      y = this._snap(y);
      width = this._snap(width);
      height = this._snap(height);
    }
    let node = { id, x, y, width, height, title, color, headerColor, headerContent, frameId: null, element: null };
    this._nodes.set(id, node);
    node.element = this._createNodeElement(node);
    this._viewport.appendChild(node.element);
    return node;
  }

  removeNode(id) {
    let node = this._nodes.get(id);
    if (!node) {
      return;
    }
    let frameId = node.frameId;
    node.element.remove();
    this._nodes.delete(id);
    this._selection.delete(id);
    this._savedViews.delete(id);
    if (frameId && this._frames.has(frameId)) {
      this._autoShrinkFrame(frameId);
    }
  }

  getNode(id) {
    return this._nodes.get(id) || null;
  }

  updateNode(id, props) {
    let node = this._nodes.get(id);
    if (!node) {
      return;
    }
    if (props.title !== undefined) {
      node.title = props.title;
      let titleEl = node.element.querySelector(".infinite-canvas-node-title");
      if (titleEl) {
        titleEl.textContent = node.title;
      }
    }
    if (props.headerContent !== undefined) {
      node.headerContent = props.headerContent;
      let header = node.element.querySelector(".infinite-canvas-node-header");
      if (header) {
        header.textContent = "";
        if (typeof node.headerContent === "string") {
          header.textContent = node.headerContent;
        } else if (node.headerContent instanceof Node) {
          header.appendChild(node.headerContent);
        } else {
          this._buildDefaultHeader(header, node);
        }
      }
    }
    if (props.bodyContent !== undefined) {
      let body = node.element.querySelector(".infinite-canvas-node-body");
      if (body) {
        body.textContent = "";
        if (props.bodyContent instanceof Node) {
          body.appendChild(props.bodyContent);
        } else if (typeof props.bodyContent === "string") {
          body.textContent = props.bodyContent;
        }
      }
    }
  }

  getNodePosition(id) {
    let node = this._nodes.get(id);
    if (!node) {
      return null;
    }
    return { x: node.x, y: node.y, width: node.width, height: node.height };
  }

  // Find a position next to an existing node that doesn't overlap any
  // others. Returns {x, y} suitable for passing to addNode. If no source
  // node is found, returns a position below the current bounds.
  //
  // Strategy: try the four cardinal positions adjacent to the source
  // (right, below, left, above). If all are occupied, slide further out
  // in each direction until we find a clear slot. As a final fallback,
  // return a position below all existing content so we never sit on top
  // of an existing node.
  findPositionNearNode(sourceId, { newWidth = null, newHeight = null, gap = 24 } = {}) {
    let source = this._nodes.get(sourceId);
    if (!source) {
      return this._positionBelowBounds();
    }
    let w = newWidth ?? source.width;
    let h = newHeight ?? source.height;

    let directions = [
      // Right: shift further right on each retry
      step => ({ x: source.x + source.width + gap + step * (w + gap), y: source.y }),
      // Below: shift further down
      step => ({ x: source.x, y: source.y + source.height + gap + step * (h + gap) }),
      // Left: shift further left
      step => ({ x: source.x - w - gap - step * (w + gap), y: source.y }),
      // Above: shift further up
      step => ({ x: source.x, y: source.y - h - gap - step * (h + gap) }),
    ];

    // Try each direction at increasing distances. First pass: adjacent
    // slots. Subsequent passes: keep sliding outward in each direction
    // until a slot is clear.
    const MAX_STEPS = 8;
    for (let step = 0; step < MAX_STEPS; step++) {
      for (let dir of directions) {
        let c = dir(step);
        if (!this._rectOverlapsAnyNode(c.x, c.y, w, h)) {
          return c;
        }
      }
    }

    // Couldn't find a non-overlapping slot near the source — drop below
    // the entire current layout so we never fully cover an old node.
    return this._positionBelowBounds();
  }

  _positionBelowBounds() {
    let bounds = this._getAllBounds();
    return bounds
      ? { x: bounds.x, y: bounds.y + bounds.height + 40 }
      : { x: 0, y: 0 };
  }

  _rectOverlapsAnyNode(x, y, w, h) {
    for (let [, n] of this._nodes) {
      if (x < n.x + n.width && x + w > n.x && y < n.y + n.height && y + h > n.y) {
        return true;
      }
    }
    return false;
  }

  canvasToScreen(canvasX, canvasY) {
    return this._canvasToScreen(canvasX, canvasY);
  }

  getViewState() {
    return { panX: this._panX, panY: this._panY, zoom: this._zoom };
  }

  // ---- Public API: Frames ----

  static GROUP_COLORS = ["#0a84ff", "#00cc66", "#ff6633", "#cc66ff", "#ffcc00", "#00cccc", "#ff3366", "#66aaff"];

  addFrame(id, { x = 0, y = 0, width = 600, height = 400, label = "Frame", color = null } = {}) {
    if (this._snapEnabled) {
      x = this._snap(x);
      y = this._snap(y);
      width = this._snap(width);
      height = this._snap(height);
    }
    if (!color) {
      color = InfiniteCanvas.GROUP_COLORS[this._frames.size % InfiniteCanvas.GROUP_COLORS.length];
    }
    let frame = { id, x, y, width, height, label, color, element: null };
    this._frames.set(id, frame);
    frame.element = this._createFrameElement(frame);
    this._viewport.insertBefore(frame.element, this._viewport.firstChild);
    return frame;
  }

  removeFrame(id) {
    let frame = this._frames.get(id);
    if (!frame) {
      return;
    }
    for (let [, node] of this._nodes) {
      if (node.frameId === id) {
        this._setNodeFrame(node, null);
      }
    }
    frame.element.remove();
    this._frames.delete(id);
    this._selection.delete(id);
    this._emit("frame-remove", { id });
  }

  // Same effect as removeFrame: keeps the child nodes ungrouped. The name
  // makes intent explicit for adapters that want to map this to the
  // underlying "ungroup tabs" operation (vs. removeFrame which they may
  // also reach via other paths).
  ungroupFrame(id) {
    this.removeFrame(id);
  }

  // Programmatically assign a node to a frame (or null to clear) and
  // grow the target frame to include the node visually. Use this when
  // the assignment isn't driven by a user drag (e.g. an external system
  // tells us a node should be in a particular group).
  assignNodeToFrame(nodeId, frameId) {
    let node = this._nodes.get(nodeId);
    if (!node) {
      return;
    }
    let changed = this._setNodeFrame(node, frameId);
    if (frameId && this._frames.has(frameId)) {
      this._autoExpandFrame(frameId);
    }
    return changed;
  }

  updateFrame(id, props) {
    let frame = this._frames.get(id);
    if (!frame) {
      return;
    }
    if (props.label !== undefined) {
      frame.label = props.label;
      let labelEl = frame.element.querySelector(".infinite-canvas-frame-label");
      if (labelEl) {
        labelEl.textContent = frame.label;
      }
    }
  }

  // ---- Public API: View ----

  panTo(x, y) {
    this._panX = x;
    this._panY = y;
    this._updateTransform();
  }

  zoomTo(level, centerX, centerY) {
    let newZoom = Math.min(Math.max(level, InfiniteCanvas.MIN_ZOOM), InfiniteCanvas.MAX_ZOOM);
    if (centerX !== undefined && centerY !== undefined) {
      let scale = newZoom / this._zoom;
      this._panX = centerX - scale * (centerX - this._panX);
      this._panY = centerY - scale * (centerY - this._panY);
    }
    this._zoom = newZoom;
    this._updateTransform();
  }

  fitAll(animate = false) {
    let bounds = this._getAllBounds();
    if (!bounds) {
      return;
    }
    let containerRect = this._container.getBoundingClientRect();
    let padding = 60;
    let scaleX = (containerRect.width - padding * 2) / bounds.width;
    let scaleY = (containerRect.height - padding * 2) / bounds.height;
    let targetZoom = Math.min(scaleX, scaleY, 1);
    let targetPanX = (containerRect.width - bounds.width * targetZoom) / 2 - bounds.x * targetZoom;
    let targetPanY = (containerRect.height - bounds.height * targetZoom) / 2 - bounds.y * targetZoom;
    if (animate) {
      this._animateToView(targetPanX, targetPanY, targetZoom);
    } else {
      this._panX = targetPanX;
      this._panY = targetPanY;
      this._zoom = targetZoom;
      this._updateTransform();
    }
  }

  // ---- Public API: Selection ----

  select(id) {
    this._selection.add(id);
    let item = this._nodes.get(id) || this._frames.get(id);
    if (item) {
      item.element.classList.add("selected");
    }
    this._emit("selection-change", { selection: [...this._selection] });
  }

  deselect(id) {
    this._selection.delete(id);
    let item = this._nodes.get(id) || this._frames.get(id);
    if (item) {
      item.element.classList.remove("selected");
    }
    this._emit("selection-change", { selection: [...this._selection] });
  }

  deselectAll() {
    if (this._selection.size === 0) {
      return;
    }
    this._clearGroupChildSelected();
    for (let id of this._selection) {
      let item = this._nodes.get(id) || this._frames.get(id);
      if (item) {
        item.element.classList.remove("selected");
      }
    }
    this._selection.clear();
    this._emit("selection-change", { selection: [] });
  }

  getSelection() {
    return [...this._selection];
  }

  // Compare two selection arrays (order-insensitive).
  _sameSelection(a, b) {
    if (a.length !== b.length) return false;
    let sa = new Set(a);
    for (let id of b) if (!sa.has(id)) return false;
    return true;
  }

  // Record a user-driven selection change as an undoable command. The
  // command body is empty — the engine's selection-restore on undo/redo
  // does the work via selectionBefore/selectionAfter. Rapid changes
  // coalesce (e.g. shift+click adding several nodes in succession).
  _recordSelectionChange(prevSelection, label = "Select") {
    let cur = [...this._selection];
    if (this._sameSelection(cur, prevSelection)) {
      return;
    }
    let cmd = {
      type: "selection",
      label,
      selectionBefore: prevSelection,
      selectionAfter: cur,
      undo: () => {},
      redo: () => {},
      sideEffects: [],
      coalesceKey: "selection",
      attach(effect) { this.sideEffects.push(effect); },
      _pushedAt: Date.now(),
    };
    if (this._transactionDepth > 0) {
      this._transactionBuffer.push(cmd);
      return;
    }
    this._commitCommand(cmd, 400);
  }

  // ---- Public API: Serialization ----

  toJSON() {
    let nodes = [];
    for (let [, n] of this._nodes) {
      nodes.push({ id: n.id, x: n.x, y: n.y, width: n.width, height: n.height, title: n.title, color: n.color, headerColor: n.headerColor, frameId: n.frameId });
    }
    let frames = [];
    for (let [, f] of this._frames) {
      frames.push({ id: f.id, x: f.x, y: f.y, width: f.width, height: f.height, label: f.label, color: f.color });
    }
    return {
      nodes,
      frames,
      viewState: { panX: this._panX, panY: this._panY, zoom: this._zoom },
    };
  }

  fromJSON(data) {
    // Clear existing
    for (let [id] of this._nodes) {
      this.removeNode(id);
    }
    for (let [id] of this._frames) {
      this.removeFrame(id);
    }
    this._selection.clear();
    this._undoStack = [];
    this._redoStack = [];

    // Restore frames first (they go behind nodes)
    for (let f of data.frames) {
      this.addFrame(f.id, { x: f.x, y: f.y, width: f.width, height: f.height, label: f.label, color: f.color });
    }
    // Restore nodes
    for (let n of data.nodes) {
      let node = this.addNode(n.id, { x: n.x, y: n.y, width: n.width, height: n.height, title: n.title, color: n.color, headerColor: n.headerColor });
      node.frameId = n.frameId;
      this._updateNodeGroupVisual(node);
    }
    // Restore view
    if (data.viewState) {
      this._panX = data.viewState.panX;
      this._panY = data.viewState.panY;
      this._zoom = data.viewState.zoom;
      this._updateTransform();
    }
  }

  // ---- Public API: Undo/Redo ----

  // Build a command object. All commands go through this factory so they
  // share a single shape (selection capture, optional coalesce key, label
  // for UI/telemetry).
  _makeCommand({ type, label, undo, redo, coalesceKey = null, sideEffects = [] }) {
    return {
      type,
      label: label || type,
      // Selection state at command-creation time (i.e. the "before" state
      // for an undo, "after" state for a redo).
      selectionBefore: [...this._selection],
      selectionAfter: null, // filled in by _pushCommand right before stack push
      undo,
      redo,
      coalesceKey,
      sideEffects,
      // Attach a chrome-side side-effect; runs in addition to the
      // engine's own undo/redo. Adapters use this to mirror state to
      // browser systems (e.g. tab close ↔ SessionStore.undoCloseTab).
      attach(effect) { this.sideEffects.push(effect); },
    };
  }

  // Open a transaction. Subsequent _pushCommand calls coalesce into a
  // single batch command pushed at endTransaction().
  beginTransaction(label, { coalesceKey = null, coalesceWindowMs = 250 } = {}) {
    if (this._transactionDepth === 0) {
      this._transactionBuffer = [];
      this._transactionLabel = label;
      this._transactionCoalesceKey = coalesceKey;
      this._transactionCoalesceWindowMs = coalesceWindowMs;
    }
    this._transactionDepth++;
  }

  endTransaction() {
    if (this._transactionDepth === 0) {
      return;
    }
    this._transactionDepth--;
    if (this._transactionDepth > 0) {
      return;
    }
    let buf = this._transactionBuffer;
    let label = this._transactionLabel;
    let coalesceKey = this._transactionCoalesceKey;
    let windowMs = this._transactionCoalesceWindowMs;
    this._transactionBuffer = null;
    this._transactionLabel = null;
    this._transactionCoalesceKey = null;
    this._transactionCoalesceWindowMs = 0;
    if (!buf || !buf.length) {
      return;
    }
    let batch;
    if (buf.length === 1) {
      batch = buf[0];
      batch.label = label || batch.label;
    } else {
      batch = this._makeCommand({
        type: "batch",
        label: label || "Batch",
        undo: () => { for (let i = buf.length - 1; i >= 0; i--) buf[i].undo(); },
        redo: () => { for (let c of buf) c.redo(); },
      });
      batch.children = buf;
      batch.selectionBefore = buf[0].selectionBefore;
    }
    batch.coalesceKey = coalesceKey || batch.coalesceKey;
    batch._pushedAt = Date.now();
    this._commitCommand(batch, windowMs);
  }

  undo() {
    if (this._undoStack.length === 0) {
      return;
    }
    let cmd = this._undoStack.pop();
    try {
      cmd.undo();
      for (let i = (cmd.sideEffects || []).length - 1; i >= 0; i--) {
        try { cmd.sideEffects[i].undo?.(); }
        catch (e) { this.debugLog("warn", "side-effect undo failed", { type: cmd.type, error: String(e) }); }
      }
      if (cmd.selectionBefore) {
        this._restoreSelection(cmd.selectionBefore);
      }
      this._redoStack.push(cmd);
      this._emit("command-undone", { type: cmd.type, label: cmd.label });
    } catch (e) {
      // Silent drop: command can't be reverted (state moved on). Log
      // and continue without pushing to redo.
      this.debugLog("warn", "undo dropped (revert threw)", { type: cmd.type, error: String(e) });
    }
    this._emitStackChange();
  }

  redo() {
    if (this._redoStack.length === 0) {
      return;
    }
    let cmd = this._redoStack.pop();
    try {
      cmd.redo();
      for (let eff of (cmd.sideEffects || [])) {
        try { eff.redo?.(); }
        catch (e) { this.debugLog("warn", "side-effect redo failed", { type: cmd.type, error: String(e) }); }
      }
      if (cmd.selectionAfter) {
        this._restoreSelection(cmd.selectionAfter);
      }
      this._undoStack.push(cmd);
      this._emit("command-redone", { type: cmd.type, label: cmd.label });
    } catch (e) {
      this.debugLog("warn", "redo dropped (apply threw)", { type: cmd.type, error: String(e) });
    }
    this._emitStackChange();
  }

  // Restore a recorded selection. Items that no longer exist are skipped.
  _restoreSelection(ids) {
    this.deselectAll();
    for (let id of ids) {
      if (this._nodes.has(id) || this._frames.has(id)) {
        this.select(id);
      }
    }
  }

  // Push a command. Routes through the transaction buffer when one is
  // open; otherwise commits immediately (with optional coalescing).
  _pushCommand(cmd) {
    // Existing callers pass a plain {undo, redo} object — wrap it so the
    // factory's bookkeeping is consistent. New callers should use
    // _makeCommand directly.
    if (!cmd.type) {
      cmd = this._makeCommand({
        type: cmd.type || "anonymous",
        label: cmd.label || "Action",
        undo: cmd.undo,
        redo: cmd.redo,
      });
    }
    cmd.selectionAfter = [...this._selection];
    if (this._transactionDepth > 0) {
      this._transactionBuffer.push(cmd);
      return;
    }
    cmd._pushedAt = Date.now();
    this._commitCommand(cmd, 0);
  }

  _commitCommand(cmd, coalesceWindowMs) {
    // Try to coalesce with the previous command if both opted in and
    // we're within the window.
    if (cmd.coalesceKey && this._undoStack.length) {
      let top = this._undoStack[this._undoStack.length - 1];
      let dt = cmd._pushedAt - (top._pushedAt || 0);
      if (top.coalesceKey === cmd.coalesceKey && dt <= coalesceWindowMs) {
        // Merge: keep top's selectionBefore, take new selectionAfter,
        // chain undo (new first when undoing, top last) and redo
        // (top first when redoing, new last).
        let prevUndo = top.undo;
        let prevRedo = top.redo;
        let newUndo = cmd.undo;
        let newRedo = cmd.redo;
        top.undo = () => { newUndo(); prevUndo(); };
        top.redo = () => { prevRedo(); newRedo(); };
        top.selectionAfter = cmd.selectionAfter;
        top._pushedAt = cmd._pushedAt;
        top.sideEffects = [...(top.sideEffects || []), ...(cmd.sideEffects || [])];
        this._redoStack = [];
        this._emit("command-pushed", { type: top.type, label: top.label, coalesced: true });
        this._emitStackChange();
        return;
      }
    }
    this._undoStack.push(cmd);
    this._redoStack = [];
    this._emit("command-pushed", { type: cmd.type, label: cmd.label, coalesced: false });
    this._emitStackChange();
  }

  _emitStackChange() {
    let top = this._undoStack[this._undoStack.length - 1];
    let redoTop = this._redoStack[this._redoStack.length - 1];
    this._emit("stack-change", {
      canUndo: this._undoStack.length > 0,
      canRedo: this._redoStack.length > 0,
      undoLabel: top ? `Undo ${top.label}` : null,
      redoLabel: redoTop ? `Redo ${redoTop.label}` : null,
    });
  }

  // ---- Debug Log ----

  debugLog(level, message, data) {
    let entry = { ts: Date.now(), level, message, data };
    this._debugLogBuffer.push(entry);
    if (this._debugLogBuffer.length > this._debugLogMax) {
      this._debugLogBuffer.shift();
    }
    this._emit("debug-log", entry);
  }

  getDebugLog() {
    return [...this._debugLogBuffer];
  }

  // ---- Public API: Extended ----

  fitSelection(animate = true) {
    let ids = [...this._selection];
    if (ids.length === 0) {
      return;
    }
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (let id of ids) {
      let item = this._nodes.get(id) || this._frames.get(id);
      if (item) {
        minX = Math.min(minX, item.x);
        minY = Math.min(minY, item.y);
        maxX = Math.max(maxX, item.x + item.width);
        maxY = Math.max(maxY, item.y + item.height);
      }
    }
    if (minX === Infinity) {
      return;
    }
    let containerRect = this._container.getBoundingClientRect();
    let padding = 60;
    let w = maxX - minX;
    let h = maxY - minY;
    let scaleX = (containerRect.width - padding * 2) / w;
    let scaleY = (containerRect.height - padding * 2) / h;
    let targetZoom = Math.min(scaleX, scaleY, 3);
    let targetPanX = (containerRect.width - w * targetZoom) / 2 - minX * targetZoom;
    let targetPanY = (containerRect.height - h * targetZoom) / 2 - minY * targetZoom;
    if (animate) {
      this._animateToView(targetPanX, targetPanY, targetZoom);
    } else {
      this._panX = targetPanX;
      this._panY = targetPanY;
      this._zoom = targetZoom;
      this._updateTransform();
    }
  }

  // Compute the target view for fitting an item into the canvas, without
  // applying it. Returns null if the item doesn't exist.
  _computeFitView(id, { padding = 60, maxZoom = 3 } = {}) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return null;
    }
    let containerRect = this._container.getBoundingClientRect();
    let scaleX = (containerRect.width - padding * 2) / item.width;
    let scaleY = (containerRect.height - padding * 2) / item.height;
    let zoom = Math.min(scaleX, scaleY, maxZoom);
    let panX = (containerRect.width - item.width * zoom) / 2 - item.x * zoom;
    let panY = (containerRect.height - item.height * zoom) / 2 - item.y * zoom;
    return { panX, panY, zoom };
  }

  fitNode(id, animate = true, fitOptions = {}) {
    let target = this._computeFitView(id, fitOptions);
    if (!target) {
      return;
    }
    if (animate) {
      this._animateToView(target.panX, target.panY, target.zoom);
    } else {
      this._panX = target.panX;
      this._panY = target.panY;
      this._zoom = target.zoom;
      this._updateTransform();
    }
  }

  animateToView({ panX, panY, zoom }, duration = 250) {
    this._animateToView(panX, panY, zoom, duration);
  }

  // Drill down the hierarchy (Figma's Enter): top-level → frame → first
  // child. When repeatedly invoked on a node inside a frame, cycles
  // through the siblings. Animates the view to center the new selection.
  // Returns the id of the new selection, or null if nothing changed.
  focusDescend() {
    let prevSelection = [...this._selection];
    let result = this._focusDescendInternal();
    if (result !== null) {
      this._recordSelectionChange(prevSelection, "Navigate Into");
    }
    return result;
  }

  _focusDescendInternal() {
    // Top-level (no useful single selection): pick the first frame, or
    // the first ungrouped node if there are no frames.
    let solo = this._selection.size === 1 ? [...this._selection][0] : null;
    if (!solo) {
      let firstFrame = this._sortedTopLevelItems()[0];
      if (!firstFrame) {
        return null;
      }
      this.deselectAll();
      this.select(firstFrame.id);
      this._centerOnItem(firstFrame);
      return firstFrame.id;
    }
    // A frame is selected: descend to its first child.
    if (this._frames.has(solo)) {
      let children = this._sortedFrameChildren(solo);
      if (!children.length) {
        return null;
      }
      let target = children[0];
      this.deselectAll();
      this.select(target.id);
      this._centerOnItem(target);
      return target.id;
    }
    // A node inside a frame is selected: cycle to next sibling.
    let node = this._nodes.get(solo);
    if (node && node.frameId && this._frames.has(node.frameId)) {
      let siblings = this._sortedFrameChildren(node.frameId);
      let idx = siblings.findIndex(s => s.id === solo);
      if (idx < 0 || siblings.length < 2) {
        return null;
      }
      let next = siblings[(idx + 1) % siblings.length];
      this.deselectAll();
      this.select(next.id);
      this._centerOnItem(next);
      return next.id;
    }
    // Ungrouped node: nothing deeper to go into.
    return null;
  }

  // Move up the hierarchy (Figma's Shift+Enter): node → its parent frame
  // → top-level (fitAll, no selection). Returns the id of the new
  // selection, or null if we popped to top level (or nothing to do).
  focusAscend() {
    let prevSelection = [...this._selection];
    let result = this._focusAscendInternal();
    this._recordSelectionChange(prevSelection, "Navigate Out");
    return result;
  }

  _focusAscendInternal() {
    let solo = this._selection.size === 1 ? [...this._selection][0] : null;
    if (!solo) {
      // Already at top level.
      return null;
    }
    // A node inside a frame: go up to the frame.
    let node = this._nodes.get(solo);
    if (node && node.frameId && this._frames.has(node.frameId)) {
      let frame = this._frames.get(node.frameId);
      this.deselectAll();
      this.select(frame.id);
      this._centerOnItem(frame);
      return frame.id;
    }
    // A frame, or an ungrouped node: pop to top-level (deselect + fitAll).
    this.deselectAll();
    this.fitAll(true);
    return null;
  }

  // Top-level items, sorted in reading order (top-to-bottom, then
  // left-to-right). Includes frames and ungrouped nodes.
  _sortedTopLevelItems() {
    let items = [];
    for (let [, f] of this._frames) items.push(f);
    for (let [, n] of this._nodes) {
      if (!n.frameId || !this._frames.has(n.frameId)) {
        items.push(n);
      }
    }
    return items.sort((a, b) => a.y - b.y || a.x - b.x);
  }

  // Children of a frame, sorted in reading order.
  _sortedFrameChildren(frameId) {
    let kids = this.getFrameChildren(frameId).map(id => this._nodes.get(id));
    return kids.sort((a, b) => a.y - b.y || a.x - b.x);
  }

  // Animate the view so the item is centered. Preserves the current zoom
  // when the item already fits in the viewport; otherwise zooms out just
  // enough to fit (so navigating up to a large frame still shows the
  // whole thing).
  _centerOnItem(item, { padding = 60 } = {}) {
    let containerRect = this._container.getBoundingClientRect();
    let scaleX = (containerRect.width - padding * 2) / item.width;
    let scaleY = (containerRect.height - padding * 2) / item.height;
    let fitZoom = Math.min(scaleX, scaleY);
    let targetZoom = Math.min(this._zoom, fitZoom);
    // Don't go below the canvas's minimum zoom.
    targetZoom = Math.max(targetZoom, InfiniteCanvas.MIN_ZOOM);
    let cx = item.x + item.width / 2;
    let cy = item.y + item.height / 2;
    let targetPanX = containerRect.width / 2 - cx * targetZoom;
    let targetPanY = containerRect.height / 2 - cy * targetZoom;
    this._animateToView(targetPanX, targetPanY, targetZoom);
  }

  // Spatial navigation: from the currently-selected single item, find the
  // nearest peer in the given direction and select + center it
  // (preserving the current zoom level). Candidate set is determined by
  // the source's hierarchy level:
  //   - A node inside a frame → other nodes in the same frame.
  //   - A frame OR an ungrouped node → other top-level items (frames
  //     and ungrouped nodes).
  // Returns the id of the new selection, or null if no neighbor was found.
  focusNeighbor(direction) {
    if (this._selection.size !== 1) {
      return null;
    }
    let prevSelection = [...this._selection];
    let sourceId = [...this._selection][0];
    let sourceNode = this._nodes.get(sourceId);
    let sourceFrame = this._frames.get(sourceId);
    let source = sourceNode || sourceFrame;
    if (!source) {
      return null;
    }

    // Build the candidate set based on hierarchy level.
    let candidates;
    if (sourceNode && sourceNode.frameId && this._frames.has(sourceNode.frameId)) {
      // Node inside a frame: peers are siblings within that frame.
      candidates = [];
      for (let [, n] of this._nodes) {
        if (n.frameId === sourceNode.frameId && n.id !== sourceId) {
          candidates.push(n);
        }
      }
    } else {
      // Frame or ungrouped node: peers are other top-level items.
      candidates = this._sortedTopLevelItems().filter(it => it.id !== sourceId);
    }

    let sx = source.x + source.width / 2;
    let sy = source.y + source.height / 2;

    let best = null;
    let bestCost = Infinity;
    for (let n of candidates) {
      let cx = n.x + n.width / 2;
      let cy = n.y + n.height / 2;
      let dx = cx - sx;
      let dy = cy - sy;
      let primary, perp;
      switch (direction) {
        case "right":
          if (dx <= 0) continue;
          primary = dx; perp = Math.abs(dy);
          break;
        case "left":
          if (dx >= 0) continue;
          primary = -dx; perp = Math.abs(dy);
          break;
        case "down":
          if (dy <= 0) continue;
          primary = dy; perp = Math.abs(dx);
          break;
        case "up":
          if (dy >= 0) continue;
          primary = -dy; perp = Math.abs(dx);
          break;
        default:
          return null;
      }
      // Reject candidates outside a ~45° cone: if the perpendicular
      // distance exceeds the primary distance, treat it as not in the
      // requested direction.
      if (perp > primary) continue;
      let cost = primary + perp * 2;
      if (cost < bestCost) {
        bestCost = cost;
        best = n;
      }
    }
    if (!best) {
      return null;
    }

    // Swap selection and center the new item at the current zoom.
    this.deselectAll();
    this.select(best.id);
    this._centerOnItem(best);
    this._recordSelectionChange(prevSelection, "Navigate");

    return best.id;
  }

  // Set the default fit options used by Alt+Enter and other implicit
  // zoom invocations. Adapters that want tighter zoom for their UX
  // (e.g. the chrome integration's zoom button) can override the
  // engine-wide defaults here.
  setDefaultFitOptions(opts) {
    this._defaultFitOptions = { ...opts };
  }

  // Does this node have a saved "previous view" from a zoom-in toggle?
  // Pick the most meaningful target for "zoom to current selection"
  // operations (Alt+Enter, etc.):
  //   - If a frame is in the selection, return it (selecting a frame
  //     often also selects its children — the user thinks of the group
  //     as one unit).
  //   - Else if exactly one node is selected, return it.
  //   - Else null.
  _primaryZoomTargetId() {
    for (let id of this._selection) {
      if (this._frames.has(id)) {
        return id;
      }
    }
    if (this._selection.size === 1) {
      return [...this._selection][0];
    }
    return null;
  }

  hasSavedView(id) {
    return this._savedViews.has(id);
  }

  // Restore (and clear) the saved view for a node, if any. Returns true
  // if a saved view was applied. Use this before deleting a node so the
  // canvas returns to where it was before the zoom-in.
  restoreSavedView(id) {
    let saved = this._savedViews.get(id);
    if (!saved) {
      return false;
    }
    this._savedViews.delete(id);
    this._animateToView(saved.panX, saved.panY, saved.zoom);
    return true;
  }

  // Toggle between "fit this node into view" and "restore previous view".
  // Only restores the previous view if the current view is still the
  // zoomed-in target — if the user scrolled/zoomed away after zooming in,
  // clicking the button re-zooms to the node (and updates the restore
  // target to whatever view they had).
  toggleZoomToNode(id, fitOptions = {}) {
    let target = this._computeFitView(id, fitOptions);
    if (!target) {
      return;
    }

    let saved = this._savedViews.get(id);
    let stillAtTarget = saved &&
      Math.abs(this._panX - target.panX) < 1 &&
      Math.abs(this._panY - target.panY) < 1 &&
      Math.abs(this._zoom - target.zoom) < 0.005;

    if (saved && stillAtTarget) {
      // Restore the previously-saved view.
      this._savedViews.delete(id);
      this._animateToView(saved.panX, saved.panY, saved.zoom);
    } else {
      // User has moved away from the previous zoom target (or this is
      // the first click). Save current view and zoom in.
      this._savedViews.set(id, { panX: this._panX, panY: this._panY, zoom: this._zoom });
      this._animateToView(target.panX, target.panY, target.zoom);
    }
  }

  setNodePosition(id, x, y) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }
    if (this._snapEnabled) {
      x = this._snap(x);
      y = this._snap(y);
    }
    item.x = x;
    item.y = y;
    this._applyRect(item.element, item);
  }

  getFrameChildren(frameId) {
    let children = [];
    for (let [id, node] of this._nodes) {
      if (node.frameId === frameId) {
        children.push(id);
      }
    }
    return children;
  }

  alignSelection(command) {
    let ids = [...this._selection];
    if (ids.length < 2 && !command.startsWith("distribute")) {
      return;
    }
    let rects = [];
    let before = [];
    for (let id of ids) {
      let item = this._nodes.get(id) || this._frames.get(id);
      if (item) {
        rects.push({ id, x: item.x, y: item.y, width: item.width, height: item.height });
        before.push({ id, x: item.x, y: item.y });
      }
    }
    let results = this._snapManager.align(rects, command);
    let after = [];
    for (let r of results) {
      let item = this._nodes.get(r.id) || this._frames.get(r.id);
      if (item) {
        item.x = this._snapEnabled ? this._snap(r.x) : r.x;
        item.y = this._snapEnabled ? this._snap(r.y) : r.y;
        this._applyRect(item.element, item);
        after.push({ id: r.id, x: item.x, y: item.y });
      }
    }
    this._emit("align", { command, ids });
    if (after.length) {
      this._pushCommand(this._makeCommand({
        type: "align",
        label: "Align",
        undo: () => {
          for (let b of before) {
            let item = this._nodes.get(b.id) || this._frames.get(b.id);
            if (item) { item.x = b.x; item.y = b.y; this._applyRect(item.element, item); }
          }
        },
        redo: () => {
          for (let a of after) {
            let item = this._nodes.get(a.id) || this._frames.get(a.id);
            if (item) { item.x = a.x; item.y = a.y; this._applyRect(item.element, item); }
          }
        },
      }));
    }
  }

  // ---- Public API: Z-Index ----

  bringToFront(id) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }
    let prevZ = item.element.style.zIndex;
    this._maxZIndex = (this._maxZIndex || 0) + 1;
    let newZ = String(this._maxZIndex);
    item.element.style.zIndex = newZ;
    this._pushCommand(this._makeCommand({
      type: "z-order",
      label: "Bring to Front",
      undo: () => {
        let it = this._nodes.get(id) || this._frames.get(id);
        if (it) it.element.style.zIndex = prevZ;
      },
      redo: () => {
        let it = this._nodes.get(id) || this._frames.get(id);
        if (it) it.element.style.zIndex = newZ;
      },
    }));
  }

  sendToBack(id) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }
    let prevZ = item.element.style.zIndex;
    this._minZIndex = (this._minZIndex || 0) - 1;
    let newZ = String(this._minZIndex);
    item.element.style.zIndex = newZ;
    this._pushCommand(this._makeCommand({
      type: "z-order",
      label: "Send to Back",
      undo: () => {
        let it = this._nodes.get(id) || this._frames.get(id);
        if (it) it.element.style.zIndex = prevZ;
      },
      redo: () => {
        let it = this._nodes.get(id) || this._frames.get(id);
        if (it) it.element.style.zIndex = newZ;
      },
    }));
  }

  // ---- Public API: Node Color ----

  setNodeColor(id, bgColor, headerColor) {
    let node = this._nodes.get(id);
    if (!node) {
      return;
    }
    let prevBg = node.color;
    let prevHeader = node.headerColor;
    if (bgColor) {
      node.color = bgColor;
      node.element.style.setProperty("--node-bg", bgColor);
    }
    if (headerColor) {
      node.headerColor = headerColor;
      node.element.style.setProperty("--node-header-bg", headerColor);
    }
    let nextBg = node.color;
    let nextHeader = node.headerColor;
    if (prevBg !== nextBg || prevHeader !== nextHeader) {
      this._pushCommand(this._makeCommand({
        type: "color",
        label: "Set Color",
        undo: () => {
          let n = this._nodes.get(id);
          if (!n) return;
          n.color = prevBg; n.headerColor = prevHeader;
          n.element.style.setProperty("--node-bg", prevBg);
          n.element.style.setProperty("--node-header-bg", prevHeader);
        },
        redo: () => {
          let n = this._nodes.get(id);
          if (!n) return;
          n.color = nextBg; n.headerColor = nextHeader;
          n.element.style.setProperty("--node-bg", nextBg);
          n.element.style.setProperty("--node-header-bg", nextHeader);
        },
      }));
    }
  }

  // ---- Public API: Frame Label Editing ----

  startEditingFrameLabel(frameId) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let labelEl = frame.element.querySelector(".infinite-canvas-frame-label");
    if (!labelEl) {
      return;
    }
    // Create an input overlay
    let input = document.createElement("input");
    input.className = "infinite-canvas-frame-label-input";
    input.value = frame.label;
    input.style.cssText = `
      position: absolute; top: -26px; left: -2px;
      font-size: 12px; font-family: system-ui, sans-serif;
      background: #1a1a2e; color: #e0e0e0; border: 1px solid #0a84ff;
      border-radius: 4px; padding: 2px 6px; outline: none;
      min-width: 80px;
    `;
    let oldLabel = frame.label;
    let commit = () => {
      let newLabel = input.value.trim() || frame.label;
      frame.label = newLabel;
      labelEl.textContent = newLabel;
      labelEl.style.display = "";
      input.remove();
      this._emit("frame-label-change", { id: frameId, label: newLabel });
      if (newLabel !== oldLabel) {
        this._pushCommand(this._makeCommand({
          type: "rename",
          label: "Rename Group",
          undo: () => {
            let f = this._frames.get(frameId);
            if (!f) return;
            f.label = oldLabel;
            let lbl = f.element.querySelector(".infinite-canvas-frame-label");
            if (lbl) lbl.textContent = oldLabel;
            this._emit("frame-label-change", { id: frameId, label: oldLabel });
          },
          redo: () => {
            let f = this._frames.get(frameId);
            if (!f) return;
            f.label = newLabel;
            let lbl = f.element.querySelector(".infinite-canvas-frame-label");
            if (lbl) lbl.textContent = newLabel;
            this._emit("frame-label-change", { id: frameId, label: newLabel });
          },
        }));
      }
    };
    input.addEventListener("keydown", e => {
      // Stop propagation first so engine shortcuts (Enter → focusDescend,
      // Escape → deselectAll, etc.) don't run after commit/cancel modifies
      // the DOM — once the input is removed, propagation flags can be
      // unreliable depending on the browser's event flow.
      e.stopPropagation();
      if (e.key === "Enter") {
        e.preventDefault();
        commit();
      }
      if (e.key === "Escape") {
        e.preventDefault();
        labelEl.style.display = "";
        input.remove();
      }
    });
    input.addEventListener("blur", commit);
    labelEl.style.display = "none";
    frame.element.appendChild(input);
    input.focus();
    input.select();
  }

  // ---- Public API: Auto-Layout ----

  // Compact a set of nodes into a tidy grid that minimizes whitespace,
  // grouping by frame membership. Nodes without a frame are arranged
  // into a single grid below the frames. Frames are auto-sized to fit
  // their children. Pass `ids` to compact only those nodes (default:
  // current selection; if empty selection, all nodes).
  compactLayout({ ids = null, gap = 20, frameGap = 60 } = {}) {
    let geomBefore = this._snapshotGeometry();
    let targetIds;
    if (ids) {
      targetIds = ids;
    } else if (this._selection.size) {
      targetIds = [...this._selection];
    } else {
      targetIds = [...this._nodes.keys(), ...this._frames.keys()];
    }
    // Bucket: frames and their participating children; loose nodes
    let frameSet = new Set();
    let looseNodes = [];
    for (let id of targetIds) {
      if (this._frames.has(id)) {
        frameSet.add(id);
      } else if (this._nodes.has(id)) {
        let n = this._nodes.get(id);
        if (n.frameId && this._frames.has(n.frameId)) {
          frameSet.add(n.frameId);
        } else {
          looseNodes.push(id);
        }
      }
    }

    // Anchor the layout at the top-left of the current bounds, so
    // compacting doesn't tear the layout away from where the user is
    // looking.
    let anchor = this._getAllBounds();
    let cursorX = anchor ? anchor.x : 0;
    let cursorY = anchor ? anchor.y : 0;
    let rowMaxH = 0;
    let containerRect = this._container.getBoundingClientRect();
    // Wrap rows to a reasonable width based on the viewport.
    let wrapWidth = Math.max(800, containerRect.width / Math.max(this._zoom, 0.3));

    let placeBlock = (blockW, blockH, placer) => {
      if (cursorX > anchor?.x && cursorX + blockW > (anchor?.x ?? 0) + wrapWidth) {
        cursorX = anchor ? anchor.x : 0;
        cursorY += rowMaxH + frameGap;
        rowMaxH = 0;
      }
      placer(cursorX, cursorY);
      cursorX += blockW + frameGap;
      rowMaxH = Math.max(rowMaxH, blockH);
    };

    // Layout each participating frame as a compact block.
    for (let frameId of frameSet) {
      let block = this._compactFrameBlock(frameId, { gap });
      placeBlock(block.width, block.height, (x, y) => {
        this._placeFrameBlock(frameId, x, y, block);
      });
    }

    // Loose nodes: pack into a single grid block.
    if (looseNodes.length) {
      let nodeWidth = 0, nodeHeight = 0;
      for (let id of looseNodes) {
        let n = this._nodes.get(id);
        nodeWidth = Math.max(nodeWidth, n.width);
        nodeHeight = Math.max(nodeHeight, n.height);
      }
      let cols = Math.ceil(Math.sqrt(looseNodes.length));
      let rows = Math.ceil(looseNodes.length / cols);
      let blockW = cols * nodeWidth + (cols - 1) * gap;
      let blockH = rows * nodeHeight + (rows - 1) * gap;
      placeBlock(blockW, blockH, (x, y) => {
        for (let i = 0; i < looseNodes.length; i++) {
          let n = this._nodes.get(looseNodes[i]);
          let c = i % cols;
          let r = Math.floor(i / cols);
          n.x = this._snap(x + c * (nodeWidth + gap));
          n.y = this._snap(y + r * (nodeHeight + gap));
          this._applyRect(n.element, n);
          this._emit("node-move", { id: looseNodes[i], x: n.x, y: n.y });
        }
      });
    }
    this._pushGeometryDiff("Tidy Layout", geomBefore);
  }

  // Snapshot every node + frame geometry into a Map<id, {x,y,w,h}>.
  _snapshotGeometry() {
    let snap = new Map();
    for (let [id, n] of this._nodes) {
      snap.set(id, { x: n.x, y: n.y, width: n.width, height: n.height });
    }
    for (let [id, f] of this._frames) {
      snap.set(id, { x: f.x, y: f.y, width: f.width, height: f.height });
    }
    return snap;
  }

  // Diff the current geometry against a snapshot and return a command
  // representing the change. Returns null if nothing changed.
  _makeGeometryDiffCommand(label, snapBefore) {
    let diff = [];
    let current = this._snapshotGeometry();
    for (let [id, after] of current) {
      let before = snapBefore.get(id);
      if (!before) continue;
      if (before.x !== after.x || before.y !== after.y ||
          before.width !== after.width || before.height !== after.height) {
        diff.push({ id, before, after });
      }
    }
    if (!diff.length) return null;
    return this._makeCommand({
      type: "layout",
      label,
      undo: () => {
        for (let d of diff) {
          let item = this._nodes.get(d.id) || this._frames.get(d.id);
          if (item) {
            item.x = d.before.x; item.y = d.before.y;
            item.width = d.before.width; item.height = d.before.height;
            this._applyRect(item.element, item);
          }
        }
      },
      redo: () => {
        for (let d of diff) {
          let item = this._nodes.get(d.id) || this._frames.get(d.id);
          if (item) {
            item.x = d.after.x; item.y = d.after.y;
            item.width = d.after.width; item.height = d.after.height;
            this._applyRect(item.element, item);
          }
        }
      },
    });
  }

  // Push a geometry-diff command, no coalescing.
  _pushGeometryDiff(label, snapBefore) {
    let cmd = this._makeGeometryDiffCommand(label, snapBefore);
    if (cmd) this._pushCommand(cmd);
  }

  _compactFrameBlock(frameId, { gap = 20 } = {}) {
    let children = this.getFrameChildren(frameId);
    let nodeWidth = 280, nodeHeight = 212;
    for (let id of children) {
      let n = this._nodes.get(id);
      nodeWidth = Math.max(nodeWidth, n.width);
      nodeHeight = Math.max(nodeHeight, n.height);
    }
    let count = Math.max(children.length, 1);
    let cols = Math.ceil(Math.sqrt(count));
    let rows = Math.ceil(count / cols);
    let labelH = 28;
    let padding = 20;
    let innerW = cols * nodeWidth + (cols - 1) * gap;
    let innerH = rows * nodeHeight + (rows - 1) * gap;
    return {
      width: innerW + padding * 2,
      height: innerH + padding * 2 + labelH,
      cols,
      rows,
      nodeWidth,
      nodeHeight,
      padding,
      labelH,
      children,
    };
  }

  _placeFrameBlock(frameId, x, y, block) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    frame.x = this._snap(x);
    frame.y = this._snap(y);
    frame.width = this._snap(block.width);
    frame.height = this._snap(block.height);
    this._applyRect(frame.element, frame);

    let { children, cols, nodeWidth, nodeHeight, padding, labelH } = block;
    let gap = (block.width - padding * 2 - cols * nodeWidth) / Math.max(cols - 1, 1);
    if (!isFinite(gap) || gap < 0) {
      gap = 20;
    }
    let startX = frame.x + padding;
    let startY = frame.y + padding + labelH;
    for (let i = 0; i < children.length; i++) {
      let n = this._nodes.get(children[i]);
      let c = i % cols;
      let r = Math.floor(i / cols);
      n.x = this._snap(startX + c * (nodeWidth + gap));
      n.y = this._snap(startY + r * (nodeHeight + gap));
      this._applyRect(n.element, n);
      this._emit("node-move", { id: children[i], x: n.x, y: n.y });
    }
  }

  autoLayout(frameId, { gap = 20, cols = null } = {}) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let children = this.getFrameChildren(frameId);
    if (children.length === 0) {
      return;
    }
    let geomBefore = this._snapshotGeometry();

    // Determine grid dimensions
    let nodeWidth = 0, nodeHeight = 0;
    for (let id of children) {
      let n = this._nodes.get(id);
      nodeWidth = Math.max(nodeWidth, n.width);
      nodeHeight = Math.max(nodeHeight, n.height);
    }

    if (!cols) {
      cols = Math.ceil(Math.sqrt(children.length));
    }
    let rows = Math.ceil(children.length / cols);

    let padding = 20;
    let startX = frame.x + padding;
    let startY = frame.y + padding;

    for (let i = 0; i < children.length; i++) {
      let n = this._nodes.get(children[i]);
      let col = i % cols;
      let row = Math.floor(i / cols);
      n.x = this._snap(startX + col * (nodeWidth + gap));
      n.y = this._snap(startY + row * (nodeHeight + gap));
      this._applyRect(n.element, n);
    }

    // Resize frame to fit
    let totalW = cols * nodeWidth + (cols - 1) * gap + padding * 2;
    let totalH = rows * nodeHeight + (rows - 1) * gap + padding * 2;
    frame.width = this._snap(Math.max(totalW, frame.width));
    frame.height = this._snap(Math.max(totalH, frame.height));
    // Ensure minimum size
    frame.width = Math.max(frame.width, totalW);
    frame.height = Math.max(frame.height, totalH);
    this._applyRect(frame.element, frame);
    this._pushGeometryDiff("Auto-Layout", geomBefore);
  }

  // ---- Public API: Events ----

  on(eventName, callback) {
    if (!this._listeners[eventName]) {
      this._listeners[eventName] = [];
    }
    this._listeners[eventName].push(callback);
  }

  off(eventName, callback) {
    let list = this._listeners[eventName];
    if (list) {
      let idx = list.indexOf(callback);
      if (idx !== -1) {
        list.splice(idx, 1);
      }
    }
  }

  destroy() {
    // Remove DOM event listeners
    for (let [event, handler, options] of this._boundListeners) {
      this._container.removeEventListener(event, handler, options);
    }
    this._boundListeners = [];

    // Remove all DOM children we created
    while (this._container.firstChild) {
      this._container.firstChild.remove();
    }
    this._container.classList.remove("infinite-canvas");
    this._container.removeAttribute("tabindex");
    this._container.style.removeProperty("--canvas-pan-x");
    this._container.style.removeProperty("--canvas-pan-y");
    this._container.style.removeProperty("--canvas-zoom");

    // Clear data
    this._nodes.clear();
    this._frames.clear();
    this._selection.clear();
    this._listeners = {};
    this._viewport = null;
    this._marqueeEl = null;
    this._zoomIndicator = null;
    this._guidesContainer = null;
  }

  // ---- Public API: Getters ----

  get zoom() {
    return this._zoom;
  }

  get snapEnabled() {
    return this._snapEnabled;
  }

  set snapEnabled(val) {
    this._snapEnabled = !!val;
  }

  get activeTool() {
    return this._activeTool;
  }

  set activeTool(tool) {
    this._activeTool = tool;
    this._container.dataset.tool = tool;
    this._emit("tool-change", { tool });
  }

  // ---- DOM Construction ----

  _buildDOM() {
    this._container.classList.add("infinite-canvas");
    this._container.setAttribute("tabindex", "0");
    this._container.dataset.tool = this._activeTool;

    this._viewport = document.createElement("div");
    this._viewport.className = "infinite-canvas-viewport";
    this._container.appendChild(this._viewport);

    this._guidesContainer = document.createElement("div");
    this._guidesContainer.className = "infinite-canvas-guides";
    this._viewport.appendChild(this._guidesContainer);

    this._tooltip = document.createElement("div");
    this._tooltip.className = "infinite-canvas-tooltip";
    this._tooltip.style.display = "none";
    this._container.appendChild(this._tooltip);

    this._marqueeEl = document.createElement("div");
    this._marqueeEl.className = "infinite-canvas-marquee";
    this._marqueeEl.style.display = "none";
    this._container.appendChild(this._marqueeEl);

    this._zoomIndicator = document.createElement("div");
    this._zoomIndicator.className = "infinite-canvas-zoom-indicator";
    this._zoomIndicator.textContent = "100%";
    this._zoomIndicator.addEventListener("click", () => {
      let rect = this._container.getBoundingClientRect();
      this.zoomTo(1, rect.width / 2, rect.height / 2);
    });
    this._container.appendChild(this._zoomIndicator);

    this._updateTransform();
  }

  _createNodeElement(node) {
    let el = document.createElement("div");
    el.className = "infinite-canvas-node";
    el.dataset.id = node.id;
    this._applyRect(el, node);
    el.style.setProperty("--node-bg", node.color);
    el.style.setProperty("--node-header-bg", node.headerColor);

    let header = document.createElement("div");
    header.className = "infinite-canvas-node-header";
    if (node.headerContent instanceof Node) {
      header.appendChild(node.headerContent);
    } else if (typeof node.headerContent === "string") {
      header.textContent = node.headerContent;
    } else {
      this._buildDefaultHeader(header, node);
    }
    el.appendChild(header);

    let body = document.createElement("div");
    body.className = "infinite-canvas-node-body";
    el.appendChild(body);

    for (let pos of ["nw", "n", "ne", "e", "se", "s", "sw", "w"]) {
      let handle = document.createElement("div");
      handle.className = "infinite-canvas-resize-handle";
      handle.dataset.position = pos;
      el.appendChild(handle);
    }

    return el;
  }

  _buildDefaultHeader(header, node) {
    let title = document.createElement("span");
    title.className = "infinite-canvas-node-title";
    title.textContent = node.title;
    header.appendChild(title);
    header.appendChild(this.createZoomButton(node.id));
    header.appendChild(this.createCloseButton(node.id));
  }

  // Build a close (X) button for a node. On click: restores any saved
  // zoom-in view, removes the node, and emits node-delete so consumers
  // can react (the chrome adapter uses node-delete to close the
  // underlying tab; the standalone page just relies on removeNode).
  createCloseButton(nodeId) {
    const SVG_NS = "http://www.w3.org/2000/svg";
    const HTML_NS = "http://www.w3.org/1999/xhtml";
    let btn = document.createElementNS(HTML_NS, "button");
    btn.className = "infinite-canvas-close-btn";
    btn.title = "Close";
    let svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("width", "12");
    svg.setAttribute("height", "12");
    svg.setAttribute("aria-hidden", "true");
    let path = document.createElementNS(SVG_NS, "path");
    // Simple X glyph
    path.setAttribute("d",
      "M4 4 L12 12 M12 4 L4 12"
    );
    path.setAttribute("stroke", "currentColor");
    path.setAttribute("stroke-width", "1.5");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("fill", "none");
    svg.appendChild(path);
    btn.appendChild(svg);
    btn.addEventListener("pointerdown", e => e.stopPropagation());
    btn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      this.restoreSavedView(nodeId);
      this.removeNode(nodeId);
      this._emit("node-delete", { id: nodeId });
    });
    return btn;
  }

  createZoomButton(nodeId, fitOptions = {}) {
    const SVG_NS = "http://www.w3.org/2000/svg";
    const HTML_NS = "http://www.w3.org/1999/xhtml";
    // Must use createElementNS — in a XUL document (browser chrome),
    // plain createElement("button") creates a XUL <button>, which renders
    // and styles entirely differently.
    let btn = document.createElementNS(HTML_NS, "button");
    btn.className = "infinite-canvas-zoom-btn";
    btn.title = "Zoom to fit";
    let svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("width", "12");
    svg.setAttribute("height", "12");
    svg.setAttribute("aria-hidden", "true");
    let path = document.createElementNS(SVG_NS, "path");
    // Four-corner expand arrows
    path.setAttribute("d",
      "M2 2 h4 v1.5 H4.5 L7 6 5.9 7.1 3.5 4.5 V6 H2 z " +
      "M14 2 h-4 v1.5 H11.5 L9 6 10.1 7.1 12.5 4.5 V6 H14 z " +
      "M2 14 h4 v-1.5 H4.5 L7 10 5.9 8.9 3.5 11.5 V10 H2 z " +
      "M14 14 h-4 v-1.5 H11.5 L9 10 10.1 8.9 12.5 11.5 V10 H14 z"
    );
    path.setAttribute("fill", "currentColor");
    svg.appendChild(path);
    btn.appendChild(svg);
    btn.addEventListener("pointerdown", e => e.stopPropagation());
    btn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      this.toggleZoomToNode(nodeId, fitOptions);
      this._emit("node-zoom-toggle", { id: nodeId });
    });
    return btn;
  }

  _createFrameElement(frame) {
    let el = document.createElement("div");
    el.className = "infinite-canvas-frame";
    el.dataset.id = frame.id;
    el.dataset.isFrame = "true";
    this._applyRect(el, frame);

    let label = document.createElement("div");
    label.className = "infinite-canvas-frame-label";
    label.textContent = frame.label;
    el.appendChild(label);

    for (let pos of ["nw", "n", "ne", "e", "se", "s", "sw", "w"]) {
      let handle = document.createElement("div");
      handle.className = "infinite-canvas-resize-handle";
      handle.dataset.position = pos;
      el.appendChild(handle);
    }

    return el;
  }

  // ---- Event Wiring ----

  _attachEvents() {
    this._boundListeners = [];
    let bind = (event, method, options) => {
      let handler = method.bind(this);
      this._container.addEventListener(event, handler, options);
      this._boundListeners.push([event, handler, options]);
    };
    bind("pointerdown", this._onPointerDown);
    bind("pointermove", this._onPointerMove);
    bind("pointerup", this._onPointerUp);
    bind("pointercancel", this._onPointerUp);
    bind("wheel", this._onWheel, { passive: false });
    bind("keydown", this._onKeyDown);
    bind("keyup", this._onKeyUp);
    bind("contextmenu", this._onContextMenu);
  }

  // ---- Pointer Events ----

  _onPointerDown(event) {
    this._container.focus();
    let itemEl = this._findItemElement(event.target);

    let resizeHandle = event.target.closest(".infinite-canvas-resize-handle");
    if (resizeHandle && this._state === InfiniteCanvas.STATE_IDLE) {
      this._startResize(event, resizeHandle);
      return;
    }

    if ((this._spaceHeld && event.button === 0) || event.button === 1 ||
        (this._activeTool === "hand" && event.button === 0)) {
      this._startPan(event);
      return;
    }

    // Drawing tools: frame or node
    if ((this._activeTool === "frame" || this._activeTool === "node") && event.button === 0) {
      this._startDrawing(event);
      return;
    }

    if (itemEl && event.button === 0) {
      // Any click on a node or frame starts a drag (Figma behavior).
      // If the user releases without moving past the threshold, it becomes
      // a click-to-select instead (handled in _endDrag).
      this._startDrag(event, itemEl);
      return;
    }

    if (event.button === 0 && !itemEl) {
      // Capture the pre-click selection so the eventual marquee command
      // records the right "before" state. _onPointerDown is the
      // gesture's earliest hook; once we deselectAll() the selection is
      // gone, so capture first.
      this._marqueeSelectionBefore = [...this._selection];
      if (!event.shiftKey) {
        this.deselectAll();
      }
      this._startMarquee(event);
    }
  }

  _onPointerMove(event) {
    if (this._state === InfiniteCanvas.STATE_IDLE) {
      return;
    }
    // Throttle via rAF: store latest event, process on next frame
    this._pendingMoveEvent = event;
    if (!this._rafPending) {
      this._rafPending = true;
      requestAnimationFrame(() => {
        this._rafPending = false;
        let e = this._pendingMoveEvent;
        if (!e) {
          return;
        }
        this._pendingMoveEvent = null;
        switch (this._state) {
          case InfiniteCanvas.STATE_PANNING:
            this._doPan(e);
            break;
          case InfiniteCanvas.STATE_DRAGGING:
            this._doDrag(e);
            break;
          case InfiniteCanvas.STATE_RESIZING:
            this._doResize(e);
            break;
          case InfiniteCanvas.STATE_MARQUEE:
            this._doMarquee(e);
            break;
          case InfiniteCanvas.STATE_DRAWING:
            this._doDrawing(e);
            break;
        }
      });
    }
  }

  _onPointerUp(event) {
    switch (this._state) {
      case InfiniteCanvas.STATE_PANNING:
        this._endPan(event);
        break;
      case InfiniteCanvas.STATE_DRAGGING:
        this._endDrag(event);
        break;
      case InfiniteCanvas.STATE_RESIZING:
        this._endResize(event);
        break;
      case InfiniteCanvas.STATE_MARQUEE:
        this._endMarquee(event);
        break;
      case InfiniteCanvas.STATE_DRAWING:
        this._endDrawing(event);
        break;
    }
  }

  // ---- Pan ----

  _startPan(event) {
    this._state = InfiniteCanvas.STATE_PANNING;
    this._pointerStartX = event.clientX;
    this._pointerStartY = event.clientY;
    this._panStartX = this._panX;
    this._panStartY = this._panY;
    this._container.classList.add("is-panning");
    try { this._container.setPointerCapture(event.pointerId); } catch (e) {}
    event.preventDefault();
  }

  _doPan(event) {
    this._panX = this._panStartX + (event.clientX - this._pointerStartX);
    this._panY = this._panStartY + (event.clientY - this._pointerStartY);
    this._updateTransform();
  }

  _endPan(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    this._container.classList.remove("is-panning");
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
  }

  // ---- Drag (Move) ----

  _startDrag(event, itemEl) {
    let id = itemEl.dataset.id;
    this._dragClickedId = id; // Track what was actually clicked for dblclick detection
    // Shift is the multi-select / drill modifier (Figma uses shift; we used
    // to use cmd/ctrl but that conflicted with the macOS context menu and
    // wasn't discoverable).
    let isAddToSelection = event.shiftKey;
    let selectionBeforeClick = [...this._selection];

    let newNode = this._nodes.get(id);
    // Drill into a child of a currently-selected frame (works for both
    // plain click and shift+click). Lets the user explore a group and then
    // jump directly into one of its tabs without first deselecting.
    let isDrillIntoSelectedFrame = newNode && newNode.frameId &&
        this._selection.has(newNode.frameId);

    let path = "unknown";

    // Shift+click on an already-selected item toggles it off. Skip when
    // we're drilling into a child of a selected frame (handled below).
    //
    // We reach this branch with the frame NOT in selection (the
    // isDrillIntoSelectedFrame check filtered that case out), so the
    // user can only be in one of two states:
    //   - the literal clicked item is selected individually → deselect it
    //   - the clicked item IS a frame element → deselect frame + children
    // We deliberately do NOT deselect the frame's other children when the
    // user clicks one of them; that would silently unselect siblings.
    if (isAddToSelection && this._selection.has(id) && !isDrillIntoSelectedFrame) {
      if (this._frames.has(id)) {
        this._deselectFrameWithChildren(id);
        path = "shift-toggle-off (frame)";
      } else {
        this.deselect(id);
        path = "shift-toggle-off (item)";
      }
      this.debugLog("info", "click selection", {
        id, shift: isAddToSelection, path,
        before: selectionBeforeClick, after: [...this._selection],
      });
      this._recordSelectionChange(selectionBeforeClick, "Deselect");
      this._state = InfiniteCanvas.STATE_IDLE;
      this._dragTargets = [];
      return;
    }

    if (isDrillIntoSelectedFrame) {
      // Replace the group selection with just this child.
      this.deselectAll();
      this.select(id);
      path = "drill-into-selected-frame";
    } else if (!this._selection.has(id)) {
      // If the user is currently "drilled in" to a group — i.e. one or
      // more of the group's children are individually selected without
      // the parent frame itself — clicking another child of the SAME
      // group should drill straight into that sibling, not pop back to
      // the whole-group selection.
      let isDrillSwitch = false;
      if (newNode && newNode.frameId && this._frames.has(newNode.frameId) &&
          this._selection.size > 0 && !this._selection.has(newNode.frameId) &&
          !isAddToSelection) {
        // Are all current selected items children of newNode.frameId?
        let allSiblings = [...this._selection].every(sid => {
          let sn = this._nodes.get(sid);
          return sn && sn.frameId === newNode.frameId;
        });
        if (allSiblings) {
          isDrillSwitch = true;
        }
      }

      if (!isAddToSelection) {
        this.deselectAll();
      }

      if (isDrillSwitch) {
        // Drill straight into the new sibling, skipping the group.
        this.select(id);
        path = "drill-switch (sibling)";
      } else if (isAddToSelection && newNode) {
        // Shift+click on a tab bypasses the "auto-promote to frame"
        // behavior — the user is explicitly editing the selection, so
        // add the literal item they clicked, not its containing group.
        this.select(id);
        path = "shift-add (tab only)";
      } else if (newNode && newNode.frameId && this._frames.has(newNode.frameId)) {
        // Fresh click into a group: select group + children (first-level).
        this._selectFrameWithChildren(newNode.frameId);
        path = "plain-click-on-tab → select frame+children";
      } else if (this._frames.has(id)) {
        // Click on a frame label or border: select group + children.
        this._selectFrameWithChildren(id);
        path = isAddToSelection ? "shift-add (frame+children)" : "plain-click-on-frame";
      } else {
        this.select(id);
        path = "plain-add (loose item)";
      }
    } else {
      path = "no-op (already selected, plain click)";
    }
    this.debugLog("info", "click selection", {
      id, shift: isAddToSelection, path,
      before: selectionBeforeClick, after: [...this._selection],
    });
    // Record the selection change for undo. If the user later drags
    // (move command), that pushes a separate command — undo will revert
    // the move first, then the selection.
    this._recordSelectionChange(selectionBeforeClick, "Select");

    this._state = InfiniteCanvas.STATE_DRAGGING;
    this._pointerStartX = event.clientX;
    this._pointerStartY = event.clientY;
    this._dragPointerId = event.pointerId;
    this._dragDidMove = false;
    // Capture view state at drag start to compensate for mid-drag scroll/zoom
    this._dragStartPanX = this._panX;
    this._dragStartPanY = this._panY;
    this._dragStartZoom = this._zoom;

    this._dragTargets = [];
    for (let selId of this._selection) {
      let item = this._nodes.get(selId) || this._frames.get(selId);
      if (item) {
        let node = this._nodes.get(selId);
        this._dragTargets.push({ id: selId, startX: item.x, startY: item.y, startFrameId: node?.frameId ?? null });
      }
    }

    // Alt+drag = clone mode
    this._isCloning = event.altKey && this._activeTool === "move";

    // Cache snap targets at drag start (non-dragged items as rects)
    this._cachedSnapTargets = this._collectSnapTargets();

    try { this._container.setPointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.add("is-dragging");
    this._container.classList.add("is-interacting");
    if (this._isCloning) {
      this._container.classList.add("is-cloning");
    }
  }

  _doDrag(event) {
    // Compute canvas-space delta, compensating for any mid-drag pan/zoom changes.
    // Convert both pointer positions to canvas space using current view state.
    let rect = this._container.getBoundingClientRect();
    let startCanvasX = (this._pointerStartX - rect.left - this._dragStartPanX) / this._dragStartZoom;
    let startCanvasY = (this._pointerStartY - rect.top - this._dragStartPanY) / this._dragStartZoom;
    let currentCanvasX = (event.clientX - rect.left - this._panX) / this._zoom;
    let currentCanvasY = (event.clientY - rect.top - this._panY) / this._zoom;
    let rawDx = currentCanvasX - startCanvasX;
    let rawDy = currentCanvasY - startCanvasY;

    if (!this._dragDidMove) {
      if (Math.abs(rawDx) < InfiniteCanvas.DRAG_THRESHOLD / this._zoom &&
          Math.abs(rawDy) < InfiniteCanvas.DRAG_THRESHOLD / this._zoom) {
        return;
      }
      this._dragDidMove = true;
      // Create ghost elements for clone mode on first real move
      if (this._isCloning) {
        this._cloneGhosts = [];
        this._cloneChildGhosts = [];
        for (let target of this._dragTargets) {
          let item = this._nodes.get(target.id) || this._frames.get(target.id);
          if (!item) {
            continue;
          }
          let ghost = item.element.cloneNode(true);
          ghost.classList.add("infinite-canvas-ghost");
          ghost.style.opacity = "0.6";
          ghost.style.pointerEvents = "none";
          this._viewport.appendChild(ghost);
          this._cloneGhosts.push({ ghost, startX: target.startX, startY: target.startY, width: item.width, height: item.height });

          // For frames, also ghost all children
          if (this._frames.has(target.id)) {
            for (let [, child] of this._nodes) {
              if (child.frameId === target.id) {
                let childGhost = child.element.cloneNode(true);
                childGhost.classList.add("infinite-canvas-ghost");
                childGhost.style.opacity = "0.6";
                childGhost.style.pointerEvents = "none";
                this._viewport.appendChild(childGhost);
                this._cloneChildGhosts.push({
                  ghost: childGhost,
                  offsetX: child.x - item.x,
                  offsetY: child.y - item.y,
                  parentIdx: this._cloneGhosts.length - 1,
                });
              }
            }
          }
        }
      }
    }

    if (this._isCloning) {
      // Clone mode: move ghosts, leave originals in place
      let snapNudgeX = 0, snapNudgeY = 0;

      // Compute snap for the primary ghost
      if (this._snapGuidesEnabled && this._snapManager && this._cloneGhosts.length > 0) {
        let g0 = this._cloneGhosts[0];
        let candidateRect = {
          x: this._snapEnabled ? this._snap(g0.startX + rawDx) : g0.startX + rawDx,
          y: this._snapEnabled ? this._snap(g0.startY + rawDy) : g0.startY + rawDy,
          width: g0.width, height: g0.height,
        };
        let snapResult = this._snapManager.snap(candidateRect, this._cachedSnapTargets, this._zoom);
        snapNudgeX = snapResult.nudge.x;
        snapNudgeY = snapResult.nudge.y;
        this._renderSnapIndicators(snapResult.indicators);
      }

      for (let g of this._cloneGhosts) {
        let newX = g.startX + rawDx;
        let newY = g.startY + rawDy;
        if (this._snapEnabled) {
          newX = this._snap(newX);
          newY = this._snap(newY);
        }
        newX += snapNudgeX;
        newY += snapNudgeY;
        g.ghost.style.transform = `translate(${newX}px, ${newY}px)`;
        g.finalX = newX;
        g.finalY = newY;
      }
      for (let cg of this._cloneChildGhosts) {
        let parent = this._cloneGhosts[cg.parentIdx];
        if (parent) {
          cg.ghost.style.transform = `translate(${parent.finalX + cg.offsetX}px, ${parent.finalY + cg.offsetY}px)`;
        }
      }
      return;
    }

    // Compute snap-to-grid positions for all targets
    let snapNudgeX = 0;
    let snapNudgeY = 0;

    // Use SnapManager for smart snapping (point + gap) on the primary target
    if (this._snapGuidesEnabled && this._snapManager && this._dragTargets.length > 0) {
      let primary = this._dragTargets[0];
      let primaryItem = this._nodes.get(primary.id) || this._frames.get(primary.id);
      if (primaryItem) {
        let candidateRect = {
          x: primary.startX + rawDx,
          y: primary.startY + rawDy,
          width: primaryItem.width,
          height: primaryItem.height,
        };
        if (this._snapEnabled) {
          candidateRect.x = this._snap(candidateRect.x);
          candidateRect.y = this._snap(candidateRect.y);
        }
        let snapResult = this._snapManager.snap(candidateRect, this._cachedSnapTargets, this._zoom);
        snapNudgeX = snapResult.nudge.x;
        snapNudgeY = snapResult.nudge.y;
        this._renderSnapIndicators(snapResult.indicators);
      }
    }

    for (let target of this._dragTargets) {
      let item = this._nodes.get(target.id) || this._frames.get(target.id);
      if (!item) {
        continue;
      }
      let newX = target.startX + rawDx;
      let newY = target.startY + rawDy;
      if (this._snapEnabled) {
        newX = this._snap(newX);
        newY = this._snap(newY);
      }
      newX += snapNudgeX;
      newY += snapNudgeY;

      let prevX = item.x;
      let prevY = item.y;
      item.x = newX;
      item.y = newY;
      this._applyRect(item.element, item);

      if (this._frames.has(target.id)) {
        this._moveFrameChildren(target.id, newX - prevX, newY - prevY);
      }
      // Emit per-frame drag events so consumers (e.g. the browser
      // adapter's live overlay) can track the position continuously
      // instead of only at drag end.
      this._emit("node-drag", { id: target.id, x: newX, y: newY });
    }

    // Frame drop highlight
    if (this._dragTargets.length > 0) {
      let primary = this._nodes.get(this._dragTargets[0].id) || this._frames.get(this._dragTargets[0].id);
      if (primary) {
        this._highlightDropFrame(primary);
      }
    }

    // Edge auto-pan: start/stop based on pointer position
    this._lastDragEvent = event;
    this._updateEdgeAutoPan(event);
  }

  _updateEdgeAutoPan(event) {
    let rect = this._container.getBoundingClientRect();
    let edgeZone = 40;
    let relX = event.clientX - rect.left;
    let relY = event.clientY - rect.top;
    let needsPan = relX < edgeZone || relX > rect.width - edgeZone ||
                   relY < edgeZone || relY > rect.height - edgeZone;

    if (needsPan && !this._autoPanRAF) {
      this._autoPanRAF = requestAnimationFrame(() => this._doEdgeAutoPan());
    } else if (!needsPan && this._autoPanRAF) {
      cancelAnimationFrame(this._autoPanRAF);
      this._autoPanRAF = null;
    }
  }

  _doEdgeAutoPan() {
    this._autoPanRAF = null;
    if (this._state !== InfiniteCanvas.STATE_DRAGGING || !this._lastDragEvent) {
      return;
    }
    let rect = this._container.getBoundingClientRect();
    let edgeZone = 40;
    let speed = 6;
    let e = this._lastDragEvent;
    let relX = e.clientX - rect.left;
    let relY = e.clientY - rect.top;
    let dx = 0, dy = 0;

    if (relX < edgeZone) {
      dx = speed * (1 - relX / edgeZone);
    } else if (relX > rect.width - edgeZone) {
      dx = -speed * (1 - (rect.width - relX) / edgeZone);
    }
    if (relY < edgeZone) {
      dy = speed * (1 - relY / edgeZone);
    } else if (relY > rect.height - edgeZone) {
      dy = -speed * (1 - (rect.height - relY) / edgeZone);
    }

    if (dx || dy) {
      this._panX += dx;
      this._panY += dy;
      this._updateTransform();
      // Continue the loop
      this._autoPanRAF = requestAnimationFrame(() => this._doEdgeAutoPan());
    }
  }

  _endDrag(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.remove("is-dragging");
    this._container.classList.remove("is-interacting");
    if (this._autoPanRAF) {
      cancelAnimationFrame(this._autoPanRAF);
      this._autoPanRAF = null;
    }
    this._lastDragEvent = null;
    this._container.classList.remove("is-cloning");
    this._clearSnapGuides();
    this._clearDropFrameHighlight();

    if (this._dragDidMove && this._isCloning) {
      // Clone mode: create real clones at ghost positions, remove ghosts
      let cloneIds = [];
      let explicitlyParented = new Set(); // children already assigned to a cloned frame
      for (let i = 0; i < this._dragTargets.length; i++) {
        let target = this._dragTargets[i];
        let item = this._nodes.get(target.id) || this._frames.get(target.id);
        let ghost = this._cloneGhosts?.[i];
        if (!item || !ghost) {
          continue;
        }
        ghost.ghost.remove();
        let cloneId = "__clone_" + (this._nextId++);
        if (this._nodes.has(target.id)) {
          this.addNode(cloneId, {
            x: ghost.finalX, y: ghost.finalY,
            width: item.width, height: item.height,
            title: item.title,
            color: item.color, headerColor: item.headerColor,
          });
          this._emit("node-clone", { sourceId: target.id, cloneId });
        } else if (this._frames.has(target.id)) {
          this.addFrame(cloneId, {
            x: ghost.finalX, y: ghost.finalY,
            width: item.width, height: item.height,
            label: item.label,
          });
          // Clone all children - snapshot IDs first to avoid iterator issues
          let dx = ghost.finalX - item.x;
          let dy = ghost.finalY - item.y;
          let childrenToClone = [];
          for (let [childId, child] of this._nodes) {
            if (child.frameId === target.id) {
              childrenToClone.push({ childId, child });
            }
          }
          for (let { child } of childrenToClone) {
            let childCloneId = "__clone_" + (this._nextId++);
            let childClone = this.addNode(childCloneId, {
              x: child.x + dx, y: child.y + dy,
              width: child.width, height: child.height,
              title: child.title,
              color: child.color, headerColor: child.headerColor,
            });
            childClone.frameId = cloneId;
            this._updateNodeGroupVisual(childClone);
            explicitlyParented.add(childCloneId);
            cloneIds.push(childCloneId);
          }
        }
        cloneIds.push(cloneId);
      }
      // Check containment only for standalone clones (not children of cloned frames)
      for (let id of cloneIds) {
        if (this._nodes.has(id) && !explicitlyParented.has(id)) {
          this._checkFrameContainment(id);
        }
      }
      // Snapshot each clone so redo can re-create them after an undo.
      let cloneSnapshots = cloneIds.map(id => {
        if (this._frames.has(id)) {
          let f = this._frames.get(id);
          return {
            kind: "frame", id,
            data: { x: f.x, y: f.y, width: f.width, height: f.height, label: f.label, color: f.color },
          };
        }
        let n = this._nodes.get(id);
        return {
          kind: "node", id,
          data: {
            x: n.x, y: n.y, width: n.width, height: n.height,
            title: n.title, color: n.color, headerColor: n.headerColor,
            frameId: n.frameId,
          },
        };
      });
      this._pushCommand(this._makeCommand({
        type: "clone",
        label: cloneSnapshots.length > 1 ? "Duplicate" : "Duplicate",
        undo: () => {
          for (let snap of cloneSnapshots) {
            if (snap.kind === "frame") {
              if (this._frames.has(snap.id)) this.removeFrame(snap.id);
            } else if (this._nodes.has(snap.id)) {
              this.removeNode(snap.id);
            }
          }
        },
        redo: () => {
          // Recreate frames first so child nodes can be reparented.
          for (let snap of cloneSnapshots) {
            if (snap.kind === "frame") {
              this.addFrame(snap.id, snap.data);
            }
          }
          for (let snap of cloneSnapshots) {
            if (snap.kind === "node") {
              let n = this.addNode(snap.id, snap.data);
              if (snap.data.frameId) {
                n.frameId = snap.data.frameId;
                this._updateNodeGroupVisual(n);
              }
            }
          }
        },
      }));
      this.deselectAll();
      for (let id of cloneIds) {
        this.select(id);
      }
      this._isCloning = false;
      this._cloneGhosts = [];
      for (let cg of (this._cloneChildGhosts || [])) {
        cg.ghost.remove();
      }
      this._cloneChildGhosts = [];
      this._dragTargets = [];
      return;
    }

    this._isCloning = false;
    if (this._cloneGhosts) {
      for (let g of this._cloneGhosts) {
        g.ghost.remove();
      }
      this._cloneGhosts = [];
    }
    if (this._cloneChildGhosts) {
      for (let cg of this._cloneChildGhosts) {
        cg.ghost.remove();
      }
      this._cloneChildGhosts = [];
    }

    if (this._dragDidMove) {
      // Push undo command for the move (captures position + frameId)
      let moves = this._dragTargets.map(t => {
        let item = this._nodes.get(t.id) || this._frames.get(t.id);
        let node = this._nodes.get(t.id);
        return {
          id: t.id,
          fromX: t.startX, fromY: t.startY,
          fromFrameId: t.startFrameId ?? null,
          toX: item?.x ?? t.startX,
          toY: item?.y ?? t.startY,
          toFrameId: node?.frameId ?? null,
        };
      });
      this._pushCommand(this._makeCommand({
        type: "move",
        label: moves.length > 1 ? "Move" : "Move",
        undo: () => {
          for (let m of moves) {
            let item = this._nodes.get(m.id) || this._frames.get(m.id);
            if (item) {
              item.x = m.fromX;
              item.y = m.fromY;
              this._applyRect(item.element, item);
              if (this._nodes.has(m.id)) {
                this._nodes.get(m.id).frameId = m.fromFrameId;
                this._updateNodeGroupVisual(this._nodes.get(m.id));
              }
            }
          }
        },
        redo: () => {
          for (let m of moves) {
            let item = this._nodes.get(m.id) || this._frames.get(m.id);
            if (item) {
              item.x = m.toX;
              item.y = m.toY;
              this._applyRect(item.element, item);
              if (this._nodes.has(m.id)) {
                this._nodes.get(m.id).frameId = m.toFrameId;
                this._updateNodeGroupVisual(this._nodes.get(m.id));
              }
            }
          }
        },
      }));
      let draggedFrameIds = new Set(
        this._dragTargets.filter(t => this._frames.has(t.id)).map(t => t.id)
      );
      for (let target of this._dragTargets) {
        if (this._nodes.has(target.id)) {
          let node = this._nodes.get(target.id);
          // Skip containment check if the node's frame was also being dragged
          // (they moved together, so the relationship should be preserved)
          if (node.frameId && draggedFrameIds.has(node.frameId)) {
            continue;
          }
          this._checkFrameContainment(target.id);
        }
      }
      // Auto-expand any dragged frames to ensure they encompass all children
      for (let frameId of draggedFrameIds) {
        this._autoExpandFrame(frameId);
      }
      for (let target of this._dragTargets) {
        let item = this._nodes.get(target.id) || this._frames.get(target.id);
        if (item) {
          this._emit("node-move", { id: target.id, x: item.x, y: item.y });
        }
      }
    } else if (this._dragTargets.length > 0) {
      // Was a click, not a drag. Emit node-click, and check for double-click.
      // Use _dragClickedId (what was actually clicked) for dblclick detection,
      // since drill-into-group may have changed the drag target.
      let id = this._dragClickedId || this._dragTargets[0].id;
      let now = Date.now();
      let modifiers = {
        altKey: !!event?.altKey,
        shiftKey: !!event?.shiftKey,
        ctrlKey: !!event?.ctrlKey,
        metaKey: !!event?.metaKey,
      };
      if (this._lastClickId === id && now - this._lastClickTime < 400) {
        this._emit("node-dblclick", { id, ...modifiers });
        if (this._frames.has(id)) {
          this.startEditingFrameLabel(id);
        }
        this._lastClickId = null;
      } else {
        this._emit("node-click", { id, ...modifiers });
        this._lastClickId = id;
        this._lastClickTime = now;
      }
    }
    this._dragTargets = [];
  }

  // ---- Resize ----

  _startResize(event, handleEl) {
    let itemEl = handleEl.closest(".infinite-canvas-node, .infinite-canvas-frame");
    if (!itemEl) {
      return;
    }
    let id = itemEl.dataset.id;
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }

    this._state = InfiniteCanvas.STATE_RESIZING;
    this._resizeTarget = id;
    this._resizeHandle = handleEl.dataset.position;
    this._resizeStartRect = { x: item.x, y: item.y, width: item.width, height: item.height };
    this._pointerStartX = event.clientX;
    this._pointerStartY = event.clientY;
    try { this._container.setPointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.add("is-interacting");
    event.preventDefault();
  }

  _doResize(event) {
    let item = this._nodes.get(this._resizeTarget) || this._frames.get(this._resizeTarget);
    if (!item) {
      return;
    }
    let dx = (event.clientX - this._pointerStartX) / this._zoom;
    let dy = (event.clientY - this._pointerStartY) / this._zoom;
    let r = { ...this._resizeStartRect };
    let h = this._resizeHandle;

    if (h.includes("e")) {
      r.width += dx;
    }
    if (h.includes("s")) {
      r.height += dy;
    }
    if (h.includes("w")) {
      r.x += dx;
      r.width -= dx;
    }
    if (h.includes("n")) {
      r.y += dy;
      r.height -= dy;
    }

    // Shift = lock aspect ratio
    if (event.shiftKey) {
      let origRatio = this._resizeStartRect.width / this._resizeStartRect.height;
      let currentRatio = r.width / r.height;
      if (currentRatio > origRatio) {
        // Width grew more - constrain width to match height
        r.width = r.height * origRatio;
        if (h.includes("w")) {
          r.x = this._resizeStartRect.x + this._resizeStartRect.width - r.width;
        }
      } else {
        // Height grew more - constrain height to match width
        r.height = r.width / origRatio;
        if (h.includes("n")) {
          r.y = this._resizeStartRect.y + this._resizeStartRect.height - r.height;
        }
      }
    }

    // Clamp to minimum size, adjusting origin for NW/W/N handles so node
    // does not teleport when clamped.
    if (r.width < InfiniteCanvas.MIN_NODE_WIDTH) {
      if (h.includes("w")) {
        r.x = this._resizeStartRect.x + this._resizeStartRect.width - InfiniteCanvas.MIN_NODE_WIDTH;
      }
      r.width = InfiniteCanvas.MIN_NODE_WIDTH;
    }
    if (r.height < InfiniteCanvas.MIN_NODE_HEIGHT) {
      if (h.includes("n")) {
        r.y = this._resizeStartRect.y + this._resizeStartRect.height - InfiniteCanvas.MIN_NODE_HEIGHT;
      }
      r.height = InfiniteCanvas.MIN_NODE_HEIGHT;
    }

    if (this._snapEnabled) {
      r.x = this._snap(r.x);
      r.y = this._snap(r.y);
      r.width = this._snap(r.width);
      r.height = this._snap(r.height);
    }

    item.x = r.x;
    item.y = r.y;
    item.width = r.width;
    item.height = r.height;
    this._applyRect(item.element, item);

    // Show dimensions tooltip near cursor
    let rect = this._container.getBoundingClientRect();
    this._tooltip.textContent = `${Math.round(r.width)} x ${Math.round(r.height)}`;
    this._tooltip.style.display = "block";
    this._tooltip.style.left = (event.clientX - rect.left + 12) + "px";
    this._tooltip.style.top = (event.clientY - rect.top + 12) + "px";
  }

  _endResize(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.remove("is-interacting");
    this._tooltip.style.display = "none";
    let id = this._resizeTarget;
    let item = this._nodes.get(id) || this._frames.get(id);
    let startRect = this._resizeStartRect;
    if (item && startRect) {
      let from = { x: startRect.x, y: startRect.y, width: startRect.width, height: startRect.height };
      let to = { x: item.x, y: item.y, width: item.width, height: item.height };
      // Snapshot children whose membership may flip as a result of the
      // resize (frame resize can evict children whose centers fall
      // outside the new bounds).
      let evictedChildren = [];
      if (this._nodes.has(id)) {
        this._checkFrameContainment(id);
      }
      if (this._frames.has(id)) {
        for (let [, child] of this._nodes) {
          if (child.frameId === id) {
            let cx = child.x + child.width / 2;
            let cy = child.y + child.height / 2;
            if (cx < item.x || cy < item.y ||
                cx > item.x + item.width || cy > item.y + item.height) {
              evictedChildren.push({ id: child.id, fromFrameId: id });
              this._setNodeFrame(child, null);
            }
          }
        }
      }
      // Only push an undo entry if anything actually changed.
      let resized = from.x !== to.x || from.y !== to.y ||
                    from.width !== to.width || from.height !== to.height;
      if (resized || evictedChildren.length) {
        this._pushCommand(this._makeCommand({
          type: "resize",
          label: "Resize",
          undo: () => {
            let it = this._nodes.get(id) || this._frames.get(id);
            if (it) {
              it.x = from.x; it.y = from.y;
              it.width = from.width; it.height = from.height;
              this._applyRect(it.element, it);
            }
            for (let e of evictedChildren) {
              let child = this._nodes.get(e.id);
              if (child) {
                this._setNodeFrame(child, e.fromFrameId);
              }
            }
          },
          redo: () => {
            let it = this._nodes.get(id) || this._frames.get(id);
            if (it) {
              it.x = to.x; it.y = to.y;
              it.width = to.width; it.height = to.height;
              this._applyRect(it.element, it);
            }
            for (let e of evictedChildren) {
              let child = this._nodes.get(e.id);
              if (child) {
                this._setNodeFrame(child, null);
              }
            }
          },
        }));
      }
      this._emit("node-resize", {
        id, x: item.x, y: item.y, width: item.width, height: item.height,
      });
    }
    this._resizeTarget = null;
    this._resizeStartRect = null;
  }

  // ---- Marquee Selection ----

  _startMarquee(event) {
    this._state = InfiniteCanvas.STATE_MARQUEE;
    // _marqueeSelectionBefore was captured in _onPointerDown (before
    // we ran deselectAll), so we have the genuine pre-gesture
    // selection to record at _endMarquee.
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    this._marqueeStartX = canvasPos.x;
    this._marqueeStartY = canvasPos.y;
    // Collapse the marquee to a 0x0 rect at the start point BEFORE
    // making it visible, so the previous marquee's last dimensions
    // don't flash on screen.
    let containerRect = this._container.getBoundingClientRect();
    let startScreen = this._canvasToScreen(canvasPos.x, canvasPos.y);
    this._marqueeEl.style.left = (startScreen.x - containerRect.left) + "px";
    this._marqueeEl.style.top = (startScreen.y - containerRect.top) + "px";
    this._marqueeEl.style.width = "0px";
    this._marqueeEl.style.height = "0px";
    this._marqueeEl.style.display = "block";
    try { this._container.setPointerCapture(event.pointerId); } catch (e) {}
    event.preventDefault();
  }

  _doMarquee(event) {
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    let x1 = Math.min(this._marqueeStartX, canvasPos.x);
    let y1 = Math.min(this._marqueeStartY, canvasPos.y);
    let x2 = Math.max(this._marqueeStartX, canvasPos.x);
    let y2 = Math.max(this._marqueeStartY, canvasPos.y);

    let topLeft = this._canvasToScreen(x1, y1);
    let bottomRight = this._canvasToScreen(x2, y2);
    let rect = this._container.getBoundingClientRect();
    this._marqueeEl.style.left = (topLeft.x - rect.left) + "px";
    this._marqueeEl.style.top = (topLeft.y - rect.top) + "px";
    this._marqueeEl.style.width = (bottomRight.x - topLeft.x) + "px";
    this._marqueeEl.style.height = (bottomRight.y - topLeft.y) + "px";

    this._selection.clear();
    for (let [id, node] of this._nodes) {
      if (this._rectsOverlap(x1, y1, x2, y2, node.x, node.y, node.x + node.width, node.y + node.height)) {
        this._selection.add(id);
      }
    }
    for (let [id, frame] of this._frames) {
      if (this._rectsOverlap(x1, y1, x2, y2, frame.x, frame.y, frame.x + frame.width, frame.y + frame.height)) {
        this._selection.add(id);
      }
    }
    this._updateSelectionVisuals();
  }

  _endMarquee(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    this._marqueeEl.style.display = "none";
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
    this._emit("selection-change", { selection: [...this._selection] });
    let prev = this._marqueeSelectionBefore;
    this._marqueeSelectionBefore = null;
    if (prev) {
      this._recordSelectionChange(prev, "Marquee Select");
    }
  }

  // ---- Drawing Tool (Frame/Node) ----

  _startDrawing(event) {
    this._state = InfiniteCanvas.STATE_DRAWING;
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    this._drawStartX = canvasPos.x;
    this._drawStartY = canvasPos.y;
    this._drawTool = this._activeTool; // "frame" or "node"
    this._marqueeEl.style.display = "block";
    try { this._container.setPointerCapture(event.pointerId); } catch (e) {}
    event.preventDefault();
  }

  _doDrawing(event) {
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    let x1 = Math.min(this._drawStartX, canvasPos.x);
    let y1 = Math.min(this._drawStartY, canvasPos.y);
    let x2 = Math.max(this._drawStartX, canvasPos.x);
    let y2 = Math.max(this._drawStartY, canvasPos.y);

    let topLeft = this._canvasToScreen(x1, y1);
    let bottomRight = this._canvasToScreen(x2, y2);
    let rect = this._container.getBoundingClientRect();
    this._marqueeEl.style.left = (topLeft.x - rect.left) + "px";
    this._marqueeEl.style.top = (topLeft.y - rect.top) + "px";
    this._marqueeEl.style.width = (bottomRight.x - topLeft.x) + "px";
    this._marqueeEl.style.height = (bottomRight.y - topLeft.y) + "px";
  }

  _endDrawing(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    this._marqueeEl.style.display = "none";
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}

    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    let x1 = Math.min(this._drawStartX, canvasPos.x);
    let y1 = Math.min(this._drawStartY, canvasPos.y);
    let x2 = Math.max(this._drawStartX, canvasPos.x);
    let y2 = Math.max(this._drawStartY, canvasPos.y);
    let w = x2 - x1;
    let h = y2 - y1;

    // Minimum size to avoid accidental tiny objects
    if (w < 20 || h < 20) {
      this.activeTool = "move";
      return;
    }

    if (this._drawTool === "frame") {
      let id = "__group_" + (this._nextId++);
      let frameData = { x: x1, y: y1, width: w, height: h, label: "Tab Group" };
      this.addFrame(id, frameData);
      // Auto-include ungrouped nodes whose center is inside the drawn rect
      let claimedChildren = [];
      for (let [, node] of this._nodes) {
        if (node.frameId) {
          continue;
        }
        let cx = node.x + node.width / 2;
        let cy = node.y + node.height / 2;
        if (cx >= x1 && cy >= y1 && cx <= x2 && cy <= y2) {
          claimedChildren.push(node.id);
          this._setNodeFrame(node, id);
        }
      }
      this._autoExpandFrame(id);
      let frameAfter = this._frames.get(id);
      let frameAfterData = {
        x: frameAfter.x, y: frameAfter.y,
        width: frameAfter.width, height: frameAfter.height,
        label: frameAfter.label, color: frameAfter.color,
      };
      this.deselectAll();
      this.select(id);
      this._emit("frame-create", { id });
      this._pushCommand(this._makeCommand({
        type: "draw-frame",
        label: "New Group",
        undo: () => {
          for (let cid of claimedChildren) {
            let n = this._nodes.get(cid);
            if (n) this._setNodeFrame(n, null);
          }
          if (this._frames.has(id)) {
            this.removeFrame(id);
          }
        },
        redo: () => {
          if (!this._frames.has(id)) {
            this.addFrame(id, frameAfterData);
          }
          for (let cid of claimedChildren) {
            let n = this._nodes.get(cid);
            if (n) this._setNodeFrame(n, id);
          }
        },
      }));
    } else if (this._drawTool === "node") {
      let id = "__node_" + (this._nextId++);
      let nodeData = { x: x1, y: y1, width: w, height: h, title: "New Tab" };
      this.addNode(id, nodeData);
      this._checkFrameContainment(id);
      let createdNode = this._nodes.get(id);
      let assignedFrameId = createdNode?.frameId ?? null;
      this.deselectAll();
      this.select(id);
      this._pushCommand(this._makeCommand({
        type: "draw-node",
        label: "New Tab",
        undo: () => {
          if (this._nodes.has(id)) this.removeNode(id);
        },
        redo: () => {
          if (!this._nodes.has(id)) {
            let n = this.addNode(id, nodeData);
            if (assignedFrameId && this._frames.has(assignedFrameId)) {
              this._setNodeFrame(n, assignedFrameId);
            }
          }
        },
      }));
    }

    // Revert to move tool after drawing
    this.activeTool = "move";
  }

  // ---- Wheel (Pan + Zoom) ----

  _onWheel(event) {
    event.preventDefault();
    let rect = this._container.getBoundingClientRect();
    let mouseX = event.clientX - rect.left;
    let mouseY = event.clientY - rect.top;

    // Suppress expensive effects (shadows) during a wheel burst.
    this._container.classList.add("is-interacting");
    clearTimeout(this._wheelIdleTimer);
    this._wheelIdleTimer = setTimeout(() => {
      this._container.classList.remove("is-interacting");
    }, 120);

    // Normalize deltas across deltaMode. Some mouse wheels report in
    // lines (deltaMode=1) with tiny values (~3); without normalizing,
    // each click only pans/zooms by a few px which feels unresponsive.
    let deltaX = event.deltaX;
    let deltaY = event.deltaY;
    if (event.deltaMode === 1) {
      deltaX *= 16;
      deltaY *= 16;
    } else if (event.deltaMode === 2) {
      deltaX *= rect.width;
      deltaY *= rect.height;
    }

    // Distinguish discrete mouse-wheel ticks from continuous trackpad
    // gestures so we can be snappier for the former without overshooting
    // on the latter.
    let isMouseWheel = event.deltaMode === 1 ||
                       Math.abs(deltaY) >= 40 || Math.abs(deltaX) >= 40;

    if (event.ctrlKey || event.metaKey) {
      // Zoom: gentler sensitivity for mouse-wheel ticks so a single
      // click doesn't snap too far; trackpads keep a smoother feel.
      let sensitivity = isMouseWheel ? 0.005 : 0.0075;
      let zoomDelta = Math.exp(-deltaY * sensitivity);
      this.zoomTo(this._zoom * zoomDelta, mouseX, mouseY);
    } else {
      // Pan: boost mouse-wheel ticks so each click feels like a real
      // step. Shift+wheel (vertical wheel only) maps to horizontal pan.
      let panBoost = isMouseWheel ? 1.5 : 1;
      let dx = deltaX * panBoost;
      let dy = deltaY * panBoost;
      if (event.shiftKey && !event.deltaX) {
        dx = dy;
        dy = 0;
      }
      this._panX -= dx;
      this._panY -= dy;
      this._updateTransform();
    }
  }

  // ---- Keyboard ----

  _onKeyDown(event) {
    if (event.key === "Alt" && this._activeTool === "move") {
      this._container.classList.add("alt-held");
    }

    if (event.key === " " && !this._spaceHeld) {
      this._spaceHeld = true;
      this._container.classList.add("space-held");
      event.preventDefault();
      return;
    }

    if (event.key === "Escape") {
      // Cancel active drag/resize by reverting positions
      if (this._state === InfiniteCanvas.STATE_DRAGGING && this._dragTargets) {
        for (let target of this._dragTargets) {
          let item = this._nodes.get(target.id) || this._frames.get(target.id);
          if (item) {
            item.x = target.startX;
            item.y = target.startY;
            this._applyRect(item.element, item);
          }
        }
        // Also revert frame children if a frame was being dragged
        // (they were moved incrementally during _doDrag)
        this._state = InfiniteCanvas.STATE_IDLE;
        this._container.classList.remove("is-dragging", "is-interacting", "is-cloning");
        this._clearSnapGuides();
        this._clearDropFrameHighlight();
        if (this._cloneGhosts) {
          for (let g of this._cloneGhosts) { g.ghost.remove(); }
          this._cloneGhosts = [];
        }
        if (this._cloneChildGhosts) {
          for (let cg of this._cloneChildGhosts) { cg.ghost.remove(); }
          this._cloneChildGhosts = [];
        }
        if (this._autoPanRAF) {
          cancelAnimationFrame(this._autoPanRAF);
          this._autoPanRAF = null;
        }
        this._dragTargets = [];
        event.preventDefault();
        return;
      }
      if (this._state === InfiniteCanvas.STATE_RESIZING && this._resizeStartRect) {
        let item = this._nodes.get(this._resizeTarget) || this._frames.get(this._resizeTarget);
        if (item) {
          item.x = this._resizeStartRect.x;
          item.y = this._resizeStartRect.y;
          item.width = this._resizeStartRect.width;
          item.height = this._resizeStartRect.height;
          this._applyRect(item.element, item);
        }
        this._state = InfiniteCanvas.STATE_IDLE;
        this._container.classList.remove("is-interacting");
        this._tooltip.style.display = "none";
        this._resizeTarget = null;
        event.preventDefault();
        return;
      }
      if (this._selection.size > 0) {
        this.deselectAll();
      }
      this._emit("escape");
      event.preventDefault();
      return;
    }

    if (event.key === "Delete" || event.key === "Backspace") {
      let selected = [...this._selection];
      // Snapshot items for undo
      let snapshot = selected.map(id => {
        let node = this._nodes.get(id);
        if (node) {
          return { type: "node", id, data: { x: node.x, y: node.y, width: node.width, height: node.height, title: node.title, color: node.color, headerColor: node.headerColor, frameId: node.frameId } };
        }
        let frame = this._frames.get(id);
        if (frame) {
          return { type: "frame", id, data: { x: frame.x, y: frame.y, width: frame.width, height: frame.height, label: frame.label } };
        }
        return null;
      }).filter(Boolean);
      for (let id of selected) {
        if (this._frames.has(id)) {
          this.removeFrame(id);
        } else {
          this.removeNode(id);
        }
        this._emit("node-delete", { id });
      }
      this._pushCommand(this._makeCommand({
        type: "delete",
        label: snapshot.length > 1 ? "Delete" : "Delete",
        undo: () => {
          // Restore frames first so child nodes can be parented to them.
          for (let s of snapshot) {
            if (s.type === "frame") {
              this.addFrame(s.id, s.data);
            }
          }
          for (let s of snapshot) {
            if (s.type === "node") {
              let n = this.addNode(s.id, s.data);
              n.frameId = s.data.frameId;
              this._updateNodeGroupVisual(n);
            }
          }
        },
        redo: () => {
          for (let s of snapshot) {
            if (s.type === "node") {
              this.removeNode(s.id);
            } else {
              this.removeFrame(s.id);
            }
          }
        },
      }));
      this._emit("selection-change", { selection: [...this._selection] });
      event.preventDefault();
      return;
    }

    if ((event.ctrlKey || event.metaKey) && event.key === "z" && !event.shiftKey) {
      this.undo();
      event.preventDefault();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "z" && event.shiftKey) {
      this.redo();
      event.preventDefault();
      return;
    }

    // Ctrl+D = duplicate selection in place
    if ((event.ctrlKey || event.metaKey) && event.key === "d") {
      event.preventDefault();
      let ids = [...this._selection];
      if (ids.length === 0) {
        return;
      }
      let offset = this._gridSize * 2;
      let cloneIds = [];
      for (let id of ids) {
        let item = this._nodes.get(id) || this._frames.get(id);
        if (!item) {
          continue;
        }
        let cloneId = "__dup_" + (this._nextId++);
        if (this._nodes.has(id)) {
          this.addNode(cloneId, {
            x: item.x + offset, y: item.y + offset,
            width: item.width, height: item.height,
            title: item.title, color: item.color, headerColor: item.headerColor,
          });
          this._checkFrameContainment(cloneId);
        } else if (this._frames.has(id)) {
          this.addFrame(cloneId, {
            x: item.x + offset, y: item.y + offset,
            width: item.width, height: item.height,
            label: item.label,
          });
          // Also duplicate children
          for (let [childId, child] of this._nodes) {
            if (child.frameId === id) {
              let childCloneId = "__dup_" + (this._nextId++);
              let cc = this.addNode(childCloneId, {
                x: child.x + offset, y: child.y + offset,
                width: child.width, height: child.height,
                title: child.title, color: child.color, headerColor: child.headerColor,
              });
              cc.frameId = cloneId;
              this._updateNodeGroupVisual(cc);
              cloneIds.push(childCloneId);
            }
          }
        }
        cloneIds.push(cloneId);
      }
      this.deselectAll();
      for (let cid of cloneIds) {
        this.select(cid);
      }
      // Snapshot every created clone so redo can rebuild them.
      let dupSnapshots = cloneIds.map(id => {
        if (this._frames.has(id)) {
          let f = this._frames.get(id);
          return {
            kind: "frame", id,
            data: { x: f.x, y: f.y, width: f.width, height: f.height, label: f.label, color: f.color },
          };
        }
        let n = this._nodes.get(id);
        return {
          kind: "node", id,
          data: {
            x: n.x, y: n.y, width: n.width, height: n.height,
            title: n.title, color: n.color, headerColor: n.headerColor,
            frameId: n.frameId,
          },
        };
      });
      this._pushCommand(this._makeCommand({
        type: "duplicate",
        label: "Duplicate",
        undo: () => {
          for (let s of dupSnapshots) {
            if (s.kind === "frame") {
              if (this._frames.has(s.id)) this.removeFrame(s.id);
            } else if (this._nodes.has(s.id)) {
              this.removeNode(s.id);
            }
          }
        },
        redo: () => {
          for (let s of dupSnapshots) {
            if (s.kind === "frame" && !this._frames.has(s.id)) {
              this.addFrame(s.id, s.data);
            }
          }
          for (let s of dupSnapshots) {
            if (s.kind === "node" && !this._nodes.has(s.id)) {
              let n = this.addNode(s.id, s.data);
              if (s.data.frameId) {
                n.frameId = s.data.frameId;
                this._updateNodeGroupVisual(n);
              }
            }
          }
        },
      }));
      return;
    }

    // Ctrl+G / Cmd+G: toggle group/ungroup based on current selection.
    // - If any frames are selected: ungroup them (children stay).
    // - Otherwise group selected nodes into a new frame.
    if ((event.ctrlKey || event.metaKey) && event.key === "g") {
      event.preventDefault();
      event.stopPropagation();
      let selectedFrameIds = [...this._selection].filter(id => this._frames.has(id));
      if (selectedFrameIds.length) {
        // Ungroup: snapshot frames + their members so undo can recreate.
        let removed = selectedFrameIds.map(fid => {
          let f = this._frames.get(fid);
          let childIds = [];
          for (let [, n] of this._nodes) {
            if (n.frameId === fid) childIds.push(n.id);
          }
          return {
            id: fid,
            data: { x: f.x, y: f.y, width: f.width, height: f.height, label: f.label, color: f.color },
            childIds,
          };
        });
        for (let frameId of selectedFrameIds) {
          this.removeFrame(frameId);
        }
        this._pushCommand(this._makeCommand({
          type: "ungroup",
          label: "Ungroup",
          undo: () => {
            for (let snap of removed) {
              if (!this._frames.has(snap.id)) {
                this.addFrame(snap.id, snap.data);
              }
              for (let cid of snap.childIds) {
                let n = this._nodes.get(cid);
                if (n) this._setNodeFrame(n, snap.id);
              }
            }
          },
          redo: () => {
            for (let snap of removed) {
              if (this._frames.has(snap.id)) {
                this.removeFrame(snap.id);
              }
            }
          },
        }));
        this._emit("selection-change", { selection: [...this._selection] });
        return;
      }

      let nodeIds = [...this._selection].filter(id => this._nodes.has(id));
      if (nodeIds.length === 0) {
        return;
      }
      // Snapshot each node's prior frameId so undo restores prior state.
      let priorFrames = nodeIds.map(id => ({ id, prevFrameId: this._nodes.get(id).frameId }));
      // Compute bounding box of selected nodes
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (let id of nodeIds) {
        let n = this._nodes.get(id);
        minX = Math.min(minX, n.x);
        minY = Math.min(minY, n.y);
        maxX = Math.max(maxX, n.x + n.width);
        maxY = Math.max(maxY, n.y + n.height);
      }
      let padding = 20;
      let frameId = "__group_" + (this._nextId++);
      let frameData = {
        x: minX - padding, y: minY - padding,
        width: maxX - minX + padding * 2, height: maxY - minY + padding * 2,
        label: "Tab Group",
      };
      this.addFrame(frameId, frameData);
      for (let id of nodeIds) {
        let n = this._nodes.get(id);
        this._setNodeFrame(n, frameId);
      }
      let createdFrame = this._frames.get(frameId);
      let createdFrameData = {
        x: createdFrame.x, y: createdFrame.y,
        width: createdFrame.width, height: createdFrame.height,
        label: createdFrame.label, color: createdFrame.color,
      };
      this.select(frameId);
      this._emit("frame-create", { id: frameId });
      this._pushCommand(this._makeCommand({
        type: "group",
        label: "Group",
        undo: () => {
          for (let p of priorFrames) {
            let n = this._nodes.get(p.id);
            if (n) this._setNodeFrame(n, p.prevFrameId);
          }
          if (this._frames.has(frameId)) {
            this.removeFrame(frameId);
          }
        },
        redo: () => {
          if (!this._frames.has(frameId)) {
            this.addFrame(frameId, createdFrameData);
          }
          for (let p of priorFrames) {
            let n = this._nodes.get(p.id);
            if (n) this._setNodeFrame(n, frameId);
          }
        },
      }));
      return;
    }

    if ((event.ctrlKey || event.metaKey) && event.key === "a") {
      this._selection.clear();
      for (let [id] of this._nodes) {
        this._selection.add(id);
      }
      for (let [id] of this._frames) {
        this._selection.add(id);
      }
      this._updateSelectionVisuals();
      this._emit("selection-change", { selection: [...this._selection] });
      event.preventDefault();
      return;
    }

    // Enter / Shift+Enter / Alt+Enter shortcuts (no Ctrl/Cmd modifiers):
    //   Enter      → focusDescend (Figma drill down)
    //   Shift+Enter → focusAscend (Figma pop up)
    //   Alt+Enter   → toggleZoomToNode on the current single selection
    //                (same effect as clicking the header zoom button)
    if (event.key === "Enter" && !event.ctrlKey && !event.metaKey) {
      if (event.altKey) {
        let id = this._primaryZoomTargetId();
        if (id) {
          this.toggleZoomToNode(id, this._defaultFitOptions);
          this._emit("node-zoom-toggle", { id });
        }
      } else if (event.shiftKey) {
        this.focusAscend();
      } else {
        this.focusDescend();
      }
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    // Alt+arrow: spatial navigation to neighboring item (preserves zoom).
    // Alt is a navigation modifier — never fall through to nudge from here,
    // even when no neighbor is found.
    if (event.altKey &&
        ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
      let dir = {
        ArrowLeft: "left", ArrowRight: "right",
        ArrowUp: "up", ArrowDown: "down",
      }[event.key];
      this.focusNeighbor(dir);
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    // Arrow key nudge
    let nudge = event.shiftKey ? 10 : 1;
    if (this._snapEnabled) {
      nudge = event.shiftKey ? this._gridSize * 2 : this._gridSize;
    }
    let dx = 0, dy = 0;
    if (event.key === "ArrowLeft") {
      dx = -nudge;
    }
    if (event.key === "ArrowRight") {
      dx = nudge;
    }
    if (event.key === "ArrowUp") {
      dy = -nudge;
    }
    if (event.key === "ArrowDown") {
      dy = nudge;
    }
    if (dx || dy) {
      let geomBefore = this._snapshotGeometry();
      for (let id of this._selection) {
        let item = this._nodes.get(id) || this._frames.get(id);
        if (item) {
          item.x += dx;
          item.y += dy;
          this._applyRect(item.element, item);
          if (this._nodes.has(id)) {
            this._checkFrameContainment(id, { autoResize: false });
          } else if (this._frames.has(id)) {
            // Moving a frame should drag its children with it (matches
            // mouse-drag behavior). Skip children that are also in the
            // selection so we don't move them twice.
            this._moveFrameChildren(id, dx, dy);
          }
          this._emit("node-move", { id, x: item.x, y: item.y });
        }
      }
      // Push a coalescing command so rapid arrow taps within ~400ms
      // merge into one undo entry.
      let diffCmd = this._makeGeometryDiffCommand("Nudge", geomBefore);
      if (diffCmd) {
        diffCmd.coalesceKey = "arrow-nudge";
        diffCmd._pushedAt = Date.now();
        this._commitCommand(diffCmd, 400);
      }
      event.preventDefault();
      return;
    }

    // Zoom shortcuts
    if ((event.ctrlKey || event.metaKey) && (event.key === "=" || event.key === "+")) {
      let rect = this._container.getBoundingClientRect();
      this.zoomTo(this._zoom * InfiniteCanvas.ZOOM_STEP, rect.width / 2, rect.height / 2);
      event.preventDefault();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "-") {
      let rect = this._container.getBoundingClientRect();
      this.zoomTo(this._zoom / InfiniteCanvas.ZOOM_STEP, rect.width / 2, rect.height / 2);
      event.preventDefault();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "0") {
      let rect = this._container.getBoundingClientRect();
      this.zoomTo(1, rect.width / 2, rect.height / 2);
      event.preventDefault();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "1") {
      this.fitAll(true);
      event.preventDefault();
      return;
    }

    // Tab = cycle selection through nodes
    if (event.key === "Tab") {
      event.preventDefault();
      let nodeIds = [...this._nodes.keys()];
      if (nodeIds.length === 0) {
        return;
      }
      let currentSel = [...this._selection];
      let currentIdx = -1;
      if (currentSel.length === 1 && this._nodes.has(currentSel[0])) {
        currentIdx = nodeIds.indexOf(currentSel[0]);
      }
      let nextIdx = event.shiftKey
        ? (currentIdx <= 0 ? nodeIds.length - 1 : currentIdx - 1)
        : (currentIdx + 1) % nodeIds.length;
      this.deselectAll();
      this.select(nodeIds[nextIdx]);
      return;
    }

    // V = move tool, H = hand tool
    if (event.key === "v" && !event.ctrlKey && !event.metaKey) {
      this.activeTool = "move";
      event.preventDefault();
      return;
    }
    if (event.key === "h" && !event.ctrlKey && !event.metaKey) {
      this.activeTool = "hand";
      event.preventDefault();
      return;
    }

    // F = frame drawing tool, N = node drawing tool
    if (event.key === "f" && !event.ctrlKey && !event.metaKey) {
      this.activeTool = "frame";
      event.preventDefault();
      return;
    }
    if (event.key === "t" && !event.ctrlKey && !event.metaKey) {
      this.activeTool = "node";
      event.preventDefault();
      return;
    }
  }

  _onKeyUp(event) {
    if (event.key === " ") {
      this._spaceHeld = false;
      this._container.classList.remove("space-held");
      event.preventDefault();
    }
    if (event.key === "Alt") {
      this._container.classList.remove("alt-held");
    }
  }

  // ---- Snap Guides (SnapManager-based) ----

  _collectSnapTargets() {
    let dragIds = new Set(this._dragTargets.map(t => t.id));
    let targets = [];
    for (let [id, node] of this._nodes) {
      if (!dragIds.has(id)) {
        targets.push({ id, x: node.x, y: node.y, width: node.width, height: node.height });
      }
    }
    for (let [id, frame] of this._frames) {
      if (!dragIds.has(id)) {
        targets.push({ id, x: frame.x, y: frame.y, width: frame.width, height: frame.height });
      }
    }
    return targets;
  }

  _renderSnapIndicators(indicators) {
    this._clearSnapGuides();
    for (let ind of indicators) {
      if (ind.type === "line") {
        let el = this._guidePool.pop() || document.createElement("div");
        el.className = "infinite-canvas-snap-guide";
        if (ind.direction === "vertical") {
          el.style.cssText = `position:absolute;left:${ind.position}px;top:${ind.start}px;width:1px;height:${ind.end - ind.start}px;background:#ff3366;opacity:0.7`;
        } else {
          el.style.cssText = `position:absolute;left:${ind.start}px;top:${ind.position}px;width:${ind.end - ind.start}px;height:1px;background:#ff3366;opacity:0.7`;
        }
        this._guidesContainer.appendChild(el);
        this._activeSnapGuides.push(el);
      } else if (ind.type === "gap") {
        for (let gap of ind.gaps) {
          let el = this._guidePool.pop() || document.createElement("div");
          el.className = "infinite-canvas-snap-guide infinite-canvas-snap-gap";
          if (ind.direction === "horizontal") {
            el.style.cssText = `position:absolute;left:${gap.start}px;top:${gap.y - 0.5}px;width:${gap.end - gap.start}px;height:1px;background:#ff3366;opacity:0.5;border-top:1px dashed #ff3366`;
          } else {
            el.style.cssText = `position:absolute;left:${gap.x - 0.5}px;top:${gap.start}px;width:1px;height:${gap.end - gap.start}px;background:#ff3366;opacity:0.5;border-left:1px dashed #ff3366`;
          }
          this._guidesContainer.appendChild(el);
          this._activeSnapGuides.push(el);
        }
      }
    }
  }

  _clearSnapGuides() {
    for (let el of this._activeSnapGuides) {
      el.remove();
      this._guidePool.push(el);
    }
    this._activeSnapGuides = [];
  }

  // ---- Frame Drop Highlight ----

  _highlightDropFrame(item) {
    this._clearDropFrameHighlight();
    if (!this._nodes.has(item.id)) {
      return;
    }
    let cx = item.x + item.width / 2;
    let cy = item.y + item.height / 2;
    let bestFrame = null;
    let bestArea = Infinity;
    for (let [, frame] of this._frames) {
      if (this._selection.has(frame.id)) {
        continue;
      }
      if (
        cx >= frame.x && cy >= frame.y &&
        cx <= frame.x + frame.width && cy <= frame.y + frame.height
      ) {
        let area = frame.width * frame.height;
        if (area < bestArea) {
          bestArea = area;
          bestFrame = frame;
        }
      }
    }
    if (bestFrame) {
      bestFrame.element.classList.add("drop-target");
    }
  }

  _clearDropFrameHighlight() {
    for (let [, frame] of this._frames) {
      frame.element.classList.remove("drop-target");
    }
  }

  // ---- Context Menu ----

  _onContextMenu(event) {
    event.preventDefault();
    this._closeContextMenu();

    let itemEl = this._findItemElement(event.target);
    let items = [];

    if (itemEl) {
      let id = itemEl.dataset.id;
      let isFrame = this._frames.has(id);
      if (!this._selection.has(id)) {
        this.deselectAll();
        this.select(id);
      }
      if (isFrame) {
        items = [
          { label: "Rename", action: "rename" },
          { label: "Auto-Layout", action: "auto-layout" },
          { label: "---" },
          { label: "Bring to Front", action: "bring-to-front" },
          { label: "Send to Back", action: "send-to-back" },
          { label: "---" },
          { label: "Ungroup", action: "ungroup" },
          { label: "Delete Group", action: "delete" },
        ];
      } else {
        items = [
          { label: "Duplicate", action: "duplicate", shortcut: "Ctrl+D" },
          { label: "Group Selection", action: "group", shortcut: "Ctrl+G" },
          { label: "---" },
          { label: "Bring to Front", action: "bring-to-front" },
          { label: "Send to Back", action: "send-to-back" },
          { label: "---" },
          { label: "Delete", action: "delete", shortcut: "Del" },
        ];
      }
    } else {
      let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
      items = [
        { label: "Add Tab", action: "add-node", x: canvasPos.x, y: canvasPos.y },
        { label: "Add Tab Group", action: "add-group", x: canvasPos.x, y: canvasPos.y },
        { label: "---" },
        { label: "Fit All", action: "fit-all" },
      ];
    }

    this._showContextMenu(event.clientX, event.clientY, items, itemEl?.dataset.id);
  }

  _showContextMenu(screenX, screenY, items, targetId) {
    let menu = document.createElement("div");
    menu.className = "infinite-canvas-context-menu";
    // Position relative to viewport and append to the document root so the
    // menu escapes any local stacking context (the canvas overlay sits
    // below live browser overlays in chrome integration; if the menu lived
    // inside the overlay, browser stacks at higher z-index would swallow
    // its clicks).
    menu.style.position = "fixed";
    menu.style.left = screenX + "px";
    menu.style.top = screenY + "px";

    for (let item of items) {
      if (item.label === "---") {
        let sep = document.createElement("div");
        sep.className = "infinite-canvas-context-menu-separator";
        menu.appendChild(sep);
        continue;
      }
      let el = document.createElement("div");
      el.className = "infinite-canvas-context-menu-item";
      el.dataset.action = item.action;
      let labelSpan = document.createElement("span");
      labelSpan.textContent = item.label;
      el.appendChild(labelSpan);
      if (item.shortcut) {
        let shortcutSpan = document.createElement("span");
        shortcutSpan.className = "infinite-canvas-context-menu-shortcut";
        shortcutSpan.textContent = item.shortcut;
        el.appendChild(shortcutSpan);
      }
      el.addEventListener("click", e => {
        e.stopPropagation();
        this._executeContextAction(item.action, targetId, item);
        this._closeContextMenu();
      });
      menu.appendChild(el);
    }

    this._contextMenu = menu;
    document.documentElement.appendChild(menu);

    setTimeout(() => {
      this._contextMenuCloseHandler = e => {
        if (!menu.contains(e.target)) {
          this._closeContextMenu();
        }
      };
      document.addEventListener("pointerdown", this._contextMenuCloseHandler);
    }, 0);
  }

  _closeContextMenu() {
    if (this._contextMenu) {
      this._contextMenu.remove();
      this._contextMenu = null;
    }
    if (this._contextMenuCloseHandler) {
      document.removeEventListener("pointerdown", this._contextMenuCloseHandler);
      this._contextMenuCloseHandler = null;
    }
  }

  _executeContextAction(action, targetId, item) {
    switch (action) {
      case "delete":
        for (let id of [...this._selection]) {
          if (this._frames.has(id)) {
            // Delete a frame: remove all child nodes (each emits
            // node-delete so adapters can close the underlying tabs),
            // then remove the frame itself.
            let childIds = this.getFrameChildren(id);
            for (let childId of childIds) {
              this.removeNode(childId);
              this._emit("node-delete", { id: childId });
            }
            this.removeFrame(id);
          } else {
            this.removeNode(id);
            this._emit("node-delete", { id });
          }
        }
        this._emit("selection-change", { selection: [] });
        break;
      case "ungroup":
        // Remove the frame but keep its child nodes as ungrouped items.
        // The frame-remove event lets adapters break apart the underlying
        // browser tab group without closing any tabs.
        for (let id of [...this._selection]) {
          if (this._frames.has(id)) {
            this.removeFrame(id);
          }
        }
        this._emit("selection-change", { selection: [] });
        break;
      case "bring-to-front":
        if (targetId) {
          this.bringToFront(targetId);
        }
        break;
      case "send-to-back":
        if (targetId) {
          this.sendToBack(targetId);
        }
        break;
      case "rename":
        if (targetId) {
          this.startEditingFrameLabel(targetId);
        }
        break;
      case "auto-layout":
        if (targetId) {
          this.autoLayout(targetId);
        }
        break;
      case "add-node":
        this.activeTool = "node";
        break;
      case "add-group":
        this.activeTool = "frame";
        break;
      case "fit-all":
        this.fitAll(true);
        break;
      case "duplicate":
        // Simulate Ctrl+D
        this._onKeyDown({ key: "d", ctrlKey: true, metaKey: false, shiftKey: false, preventDefault() {}, stopPropagation() {} });
        break;
      case "group":
        // Simulate Ctrl+G
        this._onKeyDown({ key: "g", ctrlKey: true, metaKey: false, shiftKey: false, preventDefault() {}, stopPropagation() {} });
        break;
    }
  }

  // ---- Helpers ----

  _updateNodeGroupVisual(node) {
    if (node.frameId) {
      let frame = this._frames.get(node.frameId);
      node.element.dataset.frameId = node.frameId;
      node.element.style.setProperty("--group-color", frame ? frame.color : "");
      this._updateFrameLabelCount(node.frameId);
    } else {
      delete node.element.dataset.frameId;
      node.element.style.removeProperty("--group-color");
    }
  }

  _updateFrameLabelCount(frameId) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let count = this.getFrameChildren(frameId).length;
    let labelEl = frame.element.querySelector(".infinite-canvas-frame-label");
    if (labelEl) {
      let countSpan = labelEl.querySelector(".infinite-canvas-frame-count");
      if (!countSpan) {
        countSpan = document.createElement("span");
        countSpan.className = "infinite-canvas-frame-count";
        labelEl.appendChild(countSpan);
      }
      countSpan.textContent = count > 0 ? ` (${count})` : "";
    }
  }

  // Update the selection set and DOM classes for the frame and all its
  // children, then emit a single selection-change. Calling select/deselect
  // N+1 times would emit N+1 events; listeners (e.g. the chrome adapter
  // that syncs to gBrowser multi-selection) only need the final state.
  _selectFrameWithChildren(frameId) {
    let frame = this._frames.get(frameId);
    if (frame) {
      this._selection.add(frameId);
      frame.element.classList.add("selected");
    }
    for (let [childId, child] of this._nodes) {
      if (child.frameId === frameId) {
        this._selection.add(childId);
        child.element.classList.add("selected");
        child.element.classList.add("group-child-selected");
      }
    }
    this._emit("selection-change", { selection: [...this._selection] });
  }

  _deselectFrameWithChildren(frameId) {
    let frame = this._frames.get(frameId);
    if (frame) {
      this._selection.delete(frameId);
      frame.element.classList.remove("selected");
    }
    for (let [childId, child] of this._nodes) {
      if (child.frameId === frameId) {
        this._selection.delete(childId);
        child.element.classList.remove("selected");
        child.element.classList.remove("group-child-selected");
      }
    }
    this._emit("selection-change", { selection: [...this._selection] });
  }

  _clearGroupChildSelected() {
    for (let el of this._container.querySelectorAll(".group-child-selected")) {
      el.classList.remove("group-child-selected");
    }
  }

  _findItemElement(target) {
    return target.closest(".infinite-canvas-node, .infinite-canvas-frame");
  }

  _snap(value) {
    return Math.round(value / this._gridSize) * this._gridSize;
  }

  _screenToCanvas(screenX, screenY) {
    let rect = this._container.getBoundingClientRect();
    return {
      x: (screenX - rect.left - this._panX) / this._zoom,
      y: (screenY - rect.top - this._panY) / this._zoom,
    };
  }

  _canvasToScreen(canvasX, canvasY) {
    let rect = this._container.getBoundingClientRect();
    return {
      x: canvasX * this._zoom + this._panX + rect.left,
      y: canvasY * this._zoom + this._panY + rect.top,
    };
  }

  _rectsOverlap(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2) {
    return ax1 < bx2 && ax2 > bx1 && ay1 < by2 && ay2 > by1;
  }

  _applyRect(el, item) {
    el.style.transform = `translate(${item.x}px, ${item.y}px)`;
    el.style.width = item.width + "px";
    el.style.height = item.height + "px";
  }

  _updateTransform() {
    this._viewport.style.transform = `translate(${this._panX}px, ${this._panY}px) scale(${this._zoom})`;
    this._zoomIndicator.textContent = Math.round(this._zoom * 100) + "%";
    this._container.style.setProperty("--canvas-pan-x", this._panX);
    this._container.style.setProperty("--canvas-pan-y", this._panY);
    this._container.style.setProperty("--canvas-zoom", this._zoom);
    // Grid opacity: dim at low zoom, normal at 1x, intensify at high zoom
    let gridOpacity = Math.min(Math.max(this._zoom * 0.6, 0.03), 0.15);
    this._container.style.setProperty("--grid-opacity", gridOpacity);
    this._emit("view-change", { panX: this._panX, panY: this._panY, zoom: this._zoom });
  }

  _animateToView(targetPanX, targetPanY, targetZoom, duration = 250) {
    if (this._viewAnimation) {
      cancelAnimationFrame(this._viewAnimation);
    }
    let startPanX = this._panX;
    let startPanY = this._panY;
    let startZoom = this._zoom;
    let startTime = performance.now();

    // Mark as interacting so heavy effects (shadows, transitions) are
    // suppressed during the animation.
    this._container.classList.add("is-interacting");

    let step = (now) => {
      let t = Math.min((now - startTime) / duration, 1);
      // Ease-out cubic
      let ease = 1 - Math.pow(1 - t, 3);
      this._panX = startPanX + (targetPanX - startPanX) * ease;
      this._panY = startPanY + (targetPanY - startPanY) * ease;
      this._zoom = startZoom + (targetZoom - startZoom) * ease;
      this._updateTransform();
      if (t < 1) {
        this._viewAnimation = requestAnimationFrame(step);
      } else {
        this._viewAnimation = null;
        this._container.classList.remove("is-interacting");
      }
    };
    this._viewAnimation = requestAnimationFrame(step);
  }

  _updateSelectionVisuals() {
    // Used only by marquee selection which changes many items at once
    for (let [id, node] of this._nodes) {
      let shouldSelect = this._selection.has(id);
      if (node.element.classList.contains("selected") !== shouldSelect) {
        node.element.classList.toggle("selected", shouldSelect);
      }
    }
    for (let [id, frame] of this._frames) {
      let shouldSelect = this._selection.has(id);
      if (frame.element.classList.contains("selected") !== shouldSelect) {
        frame.element.classList.toggle("selected", shouldSelect);
      }
    }
  }

  _getAllBounds() {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    let hasItems = false;
    for (let [, node] of this._nodes) {
      hasItems = true;
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + node.width);
      maxY = Math.max(maxY, node.y + node.height);
    }
    for (let [, frame] of this._frames) {
      hasItems = true;
      minX = Math.min(minX, frame.x);
      minY = Math.min(minY, frame.y);
      maxX = Math.max(maxX, frame.x + frame.width);
      maxY = Math.max(maxY, frame.y + frame.height);
    }
    if (!hasItems) {
      return null;
    }
    return { x: minX, y: minY, width: maxX - minX, height: maxY - minY };
  }

  _moveFrameChildren(frameId, dx, dy) {
    for (let [, node] of this._nodes) {
      if (node.frameId === frameId && !this._selection.has(node.id)) {
        node.x += dx;
        node.y += dy;
        this._applyRect(node.element, node);
      }
    }
  }

  _setNodeFrame(node, newFrameId) {
    let prev = node.frameId;
    if (prev === newFrameId) {
      return false;
    }
    node.frameId = newFrameId;
    this._updateNodeGroupVisual(node);
    this._emit("node-frame-change", { id: node.id, frameId: newFrameId, prevFrameId: prev });
    return true;
  }

  _checkFrameContainment(nodeId, { autoResize = true } = {}) {
    let node = this._nodes.get(nodeId);
    if (!node) {
      return;
    }
    let oldFrameId = node.frameId;

    let cx = node.x + node.width / 2;
    let cy = node.y + node.height / 2;
    let bestFrameId = null;
    let bestArea = Infinity;
    for (let [frameId, frame] of this._frames) {
      if (
        cx >= frame.x &&
        cy >= frame.y &&
        cx <= frame.x + frame.width &&
        cy <= frame.y + frame.height
      ) {
        let area = frame.width * frame.height;
        if (area < bestArea) {
          bestArea = area;
          bestFrameId = frameId;
        }
      }
    }

    this._setNodeFrame(node, bestFrameId);

    if (bestFrameId && autoResize) {
      this._autoExpandFrame(bestFrameId);
    } else if (!bestFrameId && autoResize && oldFrameId && this._frames.has(oldFrameId)) {
      this._autoShrinkFrame(oldFrameId);
    }
  }

  // Public: grow a frame so it visually contains all of its children
  // (with the engine's standard padding). Adapters that assign children
  // to frames via programmatic paths (e.g. mirroring external state)
  // should call this to ensure the frame is sized correctly on first
  // render.
  autoExpandFrame(frameId) {
    this._autoExpandFrame(frameId);
  }

  _autoExpandFrame(frameId) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let padding = 20;
    let changed = false;

    for (let [, node] of this._nodes) {
      if (node.frameId !== frameId) {
        continue;
      }
      // Expand group to contain the node with padding
      if (node.x - padding < frame.x) {
        let diff = frame.x - (node.x - padding);
        frame.x -= diff;
        frame.width += diff;
        changed = true;
      }
      if (node.y - padding < frame.y) {
        let diff = frame.y - (node.y - padding);
        frame.y -= diff;
        frame.height += diff;
        changed = true;
      }
      if (node.x + node.width + padding > frame.x + frame.width) {
        frame.width = (node.x + node.width + padding) - frame.x;
        changed = true;
      }
      if (node.y + node.height + padding > frame.y + frame.height) {
        frame.height = (node.y + node.height + padding) - frame.y;
        changed = true;
      }
    }

    if (changed) {
      if (this._snapEnabled) {
        frame.x = this._snap(frame.x);
        frame.y = this._snap(frame.y);
        frame.width = this._snap(frame.width);
        frame.height = this._snap(frame.height);
      }
      this._applyRect(frame.element, frame);
    }
  }

  _autoShrinkFrame(frameId) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let padding = 20;
    let hasChildren = false;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    for (let [, node] of this._nodes) {
      if (node.frameId !== frameId) {
        continue;
      }
      hasChildren = true;
      minX = Math.min(minX, node.x);
      minY = Math.min(minY, node.y);
      maxX = Math.max(maxX, node.x + node.width);
      maxY = Math.max(maxY, node.y + node.height);
    }

    if (hasChildren) {
      frame.x = minX - padding;
      frame.y = minY - padding;
      frame.width = maxX - minX + padding * 2;
      frame.height = maxY - minY + padding * 2;
      if (this._snapEnabled) {
        frame.x = this._snap(frame.x);
        frame.y = this._snap(frame.y);
        frame.width = this._snap(frame.width);
        frame.height = this._snap(frame.height);
      }
      this._applyRect(frame.element, frame);
    }
  }

  _emit(eventName, data = {}) {
    let callbacks = this._listeners[eventName];
    if (callbacks) {
      for (let cb of callbacks) {
        cb(data);
      }
    }
  }
}

export default InfiniteCanvas;
export { InfiniteCanvas };
