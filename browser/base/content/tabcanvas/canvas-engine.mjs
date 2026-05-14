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

    this._activeSnapGuides = [];
    this._lastClickId = null;
    this._lastClickTime = 0;
    this._undoStack = [];
    this._redoStack = [];
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
    node.element.remove();
    this._nodes.delete(id);
    this._selection.delete(id);
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
        node.frameId = null;
      }
    }
    frame.element.remove();
    this._frames.delete(id);
    this._selection.delete(id);
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

  fitAll() {
    let bounds = this._getAllBounds();
    if (!bounds) {
      return;
    }
    let containerRect = this._container.getBoundingClientRect();
    let padding = 60;
    let scaleX = (containerRect.width - padding * 2) / bounds.width;
    let scaleY = (containerRect.height - padding * 2) / bounds.height;
    this._zoom = Math.min(scaleX, scaleY, 1);
    this._panX = (containerRect.width - bounds.width * this._zoom) / 2 - bounds.x * this._zoom;
    this._panY = (containerRect.height - bounds.height * this._zoom) / 2 - bounds.y * this._zoom;
    this._updateTransform();
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

  // ---- Public API: Serialization ----

  toJSON() {
    let nodes = [];
    for (let [, n] of this._nodes) {
      nodes.push({ id: n.id, x: n.x, y: n.y, width: n.width, height: n.height, title: n.title, color: n.color, headerColor: n.headerColor, frameId: n.frameId });
    }
    let frames = [];
    for (let [, f] of this._frames) {
      frames.push({ id: f.id, x: f.x, y: f.y, width: f.width, height: f.height, label: f.label });
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
      this.addFrame(f.id, { x: f.x, y: f.y, width: f.width, height: f.height, label: f.label });
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

  undo() {
    if (this._undoStack.length === 0) {
      return;
    }
    let cmd = this._undoStack.pop();
    cmd.undo();
    this._redoStack.push(cmd);
  }

  redo() {
    if (this._redoStack.length === 0) {
      return;
    }
    let cmd = this._redoStack.pop();
    cmd.redo();
    this._undoStack.push(cmd);
  }

  _pushCommand(cmd) {
    this._undoStack.push(cmd);
    this._redoStack = [];
  }

  // ---- Public API: Extended ----

  fitSelection() {
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
    this._zoom = Math.min(scaleX, scaleY, 3);
    this._panX = (containerRect.width - w * this._zoom) / 2 - minX * this._zoom;
    this._panY = (containerRect.height - h * this._zoom) / 2 - minY * this._zoom;
    this._updateTransform();
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
    for (let id of ids) {
      let item = this._nodes.get(id) || this._frames.get(id);
      if (item) {
        rects.push({ id, x: item.x, y: item.y, width: item.width, height: item.height });
      }
    }
    let results = this._snapManager.align(rects, command);
    for (let r of results) {
      let item = this._nodes.get(r.id) || this._frames.get(r.id);
      if (item) {
        item.x = this._snapEnabled ? this._snap(r.x) : r.x;
        item.y = this._snapEnabled ? this._snap(r.y) : r.y;
        this._applyRect(item.element, item);
      }
    }
    this._emit("align", { command, ids });
  }

  // ---- Public API: Z-Index ----

  bringToFront(id) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }
    this._maxZIndex = (this._maxZIndex || 0) + 1;
    item.element.style.zIndex = this._maxZIndex;
  }

  sendToBack(id) {
    let item = this._nodes.get(id) || this._frames.get(id);
    if (!item) {
      return;
    }
    this._minZIndex = (this._minZIndex || 0) - 1;
    item.element.style.zIndex = this._minZIndex;
  }

  // ---- Public API: Node Color ----

  setNodeColor(id, bgColor, headerColor) {
    let node = this._nodes.get(id);
    if (!node) {
      return;
    }
    if (bgColor) {
      node.color = bgColor;
      node.element.style.setProperty("--node-bg", bgColor);
    }
    if (headerColor) {
      node.headerColor = headerColor;
      node.element.style.setProperty("--node-header-bg", headerColor);
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
    let commit = () => {
      let newLabel = input.value.trim() || frame.label;
      frame.label = newLabel;
      labelEl.textContent = newLabel;
      labelEl.style.display = "";
      input.remove();
      this._emit("frame-label-change", { id: frameId, label: newLabel });
    };
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") {
        e.preventDefault();
        commit();
      }
      if (e.key === "Escape") {
        e.preventDefault();
        labelEl.style.display = "";
        input.remove();
      }
      e.stopPropagation();
    });
    input.addEventListener("blur", commit);
    labelEl.style.display = "none";
    frame.element.appendChild(input);
    input.focus();
    input.select();
  }

  // ---- Public API: Auto-Layout ----

  autoLayout(frameId, { gap = 20, cols = null } = {}) {
    let frame = this._frames.get(frameId);
    if (!frame) {
      return;
    }
    let children = this.getFrameChildren(frameId);
    if (children.length === 0) {
      return;
    }

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

    this._marqueeEl = document.createElement("div");
    this._marqueeEl.className = "infinite-canvas-marquee";
    this._marqueeEl.style.display = "none";
    this._container.appendChild(this._marqueeEl);

    this._zoomIndicator = document.createElement("div");
    this._zoomIndicator.className = "infinite-canvas-zoom-indicator";
    this._zoomIndicator.textContent = "100%";
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
    let rect = this._container.getBoundingClientRect();
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    let itemEl = this._findItemElement(event.target);
    console.log("[canvas pointerdown]",
      "clientX:", event.clientX, "clientY:", event.clientY,
      "rect.top:", rect.top, "rect.left:", rect.left,
      "offsetInContainer:", { x: event.clientX - rect.left, y: event.clientY - rect.top },
      "canvasPos:", canvasPos,
      "target:", event.target.className,
      "itemEl:", itemEl?.className,
      "zoom:", this._zoom, "panX:", this._panX, "panY:", this._panY
    );
    this._container.focus();

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
    if (!this._selection.has(id)) {
      if (!event.shiftKey) {
        this.deselectAll();
      }
      this.select(id);
      // Selecting a frame also selects all its children
      if (this._frames.has(id)) {
        for (let [childId, child] of this._nodes) {
          if (child.frameId === id) {
            this.select(childId);
          }
        }
      }
    }

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
        this._dragTargets.push({ id: selId, startX: item.x, startY: item.y });
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
      for (let g of this._cloneGhosts) {
        let newX = g.startX + rawDx;
        let newY = g.startY + rawDy;
        if (this._snapEnabled) {
          newX = this._snap(newX);
          newY = this._snap(newY);
        }
        g.ghost.style.transform = `translate(${newX}px, ${newY}px)`;
        g.finalX = newX;
        g.finalY = newY;
      }
      // Move child ghosts relative to their parent ghost
      for (let cg of this._cloneChildGhosts) {
        let parent = this._cloneGhosts[cg.parentIdx];
        if (parent) {
          let cx = parent.finalX + cg.offsetX;
          let cy = parent.finalY + cg.offsetY;
          cg.ghost.style.transform = `translate(${cx}px, ${cy}px)`;
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
    }

    // Frame drop highlight
    if (this._dragTargets.length > 0) {
      let primary = this._nodes.get(this._dragTargets[0].id) || this._frames.get(this._dragTargets[0].id);
      if (primary) {
        this._highlightDropFrame(primary);
      }
    }
  }

  _endDrag(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.remove("is-dragging");
    this._container.classList.remove("is-interacting");
    this._container.classList.remove("is-cloning");
    this._clearSnapGuides();
    this._clearDropFrameHighlight();

    if (this._dragDidMove && this._isCloning) {
      // Clone mode: create real clones at ghost positions, remove ghosts
      let cloneIds = [];
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
          // Clone all children of the frame
          let dx = ghost.finalX - item.x;
          let dy = ghost.finalY - item.y;
          for (let [childId, child] of this._nodes) {
            if (child.frameId === target.id) {
              let childCloneId = "__clone_" + (this._nextId++);
              let childClone = this.addNode(childCloneId, {
                x: child.x + dx, y: child.y + dy,
                width: child.width, height: child.height,
                title: child.title,
                color: child.color, headerColor: child.headerColor,
              });
              childClone.frameId = cloneId;
              this._updateNodeGroupVisual(childClone);
              cloneIds.push(childCloneId);
            }
          }
        }
        cloneIds.push(cloneId);
      }
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
      // Push undo command for the move
      let moves = this._dragTargets.map(t => ({
        id: t.id,
        fromX: t.startX, fromY: t.startY,
        toX: (this._nodes.get(t.id) || this._frames.get(t.id))?.x ?? t.startX,
        toY: (this._nodes.get(t.id) || this._frames.get(t.id))?.y ?? t.startY,
      }));
      this._pushCommand({
        undo: () => {
          for (let m of moves) {
            let item = this._nodes.get(m.id) || this._frames.get(m.id);
            if (item) {
              item.x = m.fromX;
              item.y = m.fromY;
              this._applyRect(item.element, item);
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
            }
          }
        },
      });
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
      let id = this._dragTargets[0].id;
      let now = Date.now();
      if (this._lastClickId === id && now - this._lastClickTime < 400) {
        this._emit("node-dblclick", { id });
        // Auto-start label editing for frames on double-click
        if (this._frames.has(id)) {
          this.startEditingFrameLabel(id);
        }
        this._lastClickId = null;
      } else {
        this._emit("node-click", { id });
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
  }

  _endResize(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    try { this._container.releasePointerCapture(event.pointerId); } catch (e) {}
    this._container.classList.remove("is-interacting");
    let item = this._nodes.get(this._resizeTarget) || this._frames.get(this._resizeTarget);
    if (item) {
      this._emit("node-resize", {
        id: this._resizeTarget,
        x: item.x, y: item.y, width: item.width, height: item.height,
      });
    }
    this._resizeTarget = null;
  }

  // ---- Marquee Selection ----

  _startMarquee(event) {
    this._state = InfiniteCanvas.STATE_MARQUEE;
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    this._marqueeStartX = canvasPos.x;
    this._marqueeStartY = canvasPos.y;
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
      this.addFrame(id, { x: x1, y: y1, width: w, height: h, label: "Tab Group" });
      // Auto-include ungrouped nodes whose center is inside the drawn rect
      for (let [nodeId, node] of this._nodes) {
        if (node.frameId) {
          continue;
        }
        let cx = node.x + node.width / 2;
        let cy = node.y + node.height / 2;
        if (cx >= x1 && cy >= y1 && cx <= x2 && cy <= y2) {
          node.frameId = id;
          this._updateNodeGroupVisual(node);
        }
      }
      this._autoExpandFrame(id);
      this.deselectAll();
      this.select(id);
      this._emit("frame-create", { id });
    } else if (this._drawTool === "node") {
      let id = "__node_" + (this._nextId++);
      this.addNode(id, { x: x1, y: y1, width: w, height: h, title: "New Tab" });
      this.deselectAll();
      this.select(id);
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

    if (event.ctrlKey || event.metaKey) {
      // Scale zoom factor by deltaY magnitude. Trackpad pinch sends small
      // deltas (1-5), mouse wheel sends large ones (50-150). Using deltaY
      // directly gives smooth trackpad zoom and snappy mouse wheel zoom.
      let sensitivity = 0.008;
      let zoomDelta = Math.exp(-event.deltaY * sensitivity);
      this.zoomTo(this._zoom * zoomDelta, mouseX, mouseY);
    } else {
      this._panX -= event.deltaX;
      this._panY -= event.deltaY;
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
      this._pushCommand({
        undo: () => {
          for (let s of snapshot) {
            if (s.type === "node") {
              let n = this.addNode(s.id, s.data);
              n.frameId = s.data.frameId;
            } else {
              this.addFrame(s.id, s.data);
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
      });
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
      return;
    }

    // Ctrl+G = group selected nodes into a new tab group
    if ((event.ctrlKey || event.metaKey) && event.key === "g") {
      event.preventDefault();
      let nodeIds = [...this._selection].filter(id => this._nodes.has(id));
      if (nodeIds.length === 0) {
        return;
      }
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
      this.addFrame(frameId, {
        x: minX - padding, y: minY - padding,
        width: maxX - minX + padding * 2, height: maxY - minY + padding * 2,
        label: "Tab Group",
      });
      for (let id of nodeIds) {
        let n = this._nodes.get(id);
        n.frameId = frameId;
        this._updateNodeGroupVisual(n);
      }
      this.select(frameId);
      this._emit("frame-create", { id: frameId });
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
      for (let id of this._selection) {
        let item = this._nodes.get(id) || this._frames.get(id);
        if (item) {
          item.x += dx;
          item.y += dy;
          this._applyRect(item.element, item);
          if (this._nodes.has(id)) {
            this._checkFrameContainment(id, { autoResize: false });
          }
          this._emit("node-move", { id, x: item.x, y: item.y });
        }
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
      this.fitAll();
      event.preventDefault();
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
    for (let [, frame] of this._frames) {
      if (this._selection.has(frame.id)) {
        continue;
      }
      if (
        cx >= frame.x && cy >= frame.y &&
        cx <= frame.x + frame.width && cy <= frame.y + frame.height
      ) {
        frame.element.classList.add("drop-target");
        return;
      }
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
          { label: "Delete Group", action: "delete" },
        ];
      } else {
        items = [
          { label: "Bring to Front", action: "bring-to-front" },
          { label: "Send to Back", action: "send-to-back" },
          { label: "---" },
          { label: "Delete", action: "delete" },
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
    let rect = this._container.getBoundingClientRect();
    menu.style.left = (screenX - rect.left) + "px";
    menu.style.top = (screenY - rect.top) + "px";

    for (let item of items) {
      if (item.label === "---") {
        let sep = document.createElement("div");
        sep.className = "infinite-canvas-context-menu-separator";
        menu.appendChild(sep);
        continue;
      }
      let el = document.createElement("div");
      el.className = "infinite-canvas-context-menu-item";
      el.textContent = item.label;
      el.dataset.action = item.action;
      el.addEventListener("click", e => {
        e.stopPropagation();
        this._executeContextAction(item.action, targetId, item);
        this._closeContextMenu();
      });
      menu.appendChild(el);
    }

    this._contextMenu = menu;
    this._container.appendChild(menu);

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
            this.removeFrame(id);
          } else {
            this.removeNode(id);
          }
          this._emit("node-delete", { id });
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
        this.fitAll();
        break;
    }
  }

  // ---- Helpers ----

  _updateNodeGroupVisual(node) {
    if (node.frameId) {
      let frame = this._frames.get(node.frameId);
      node.element.dataset.frameId = node.frameId;
      node.element.style.setProperty("--group-color", frame ? frame.color : "");
    } else {
      delete node.element.dataset.frameId;
      node.element.style.removeProperty("--group-color");
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
    this._emit("view-change", { panX: this._panX, panY: this._panY, zoom: this._zoom });
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

  _checkFrameContainment(nodeId, { autoResize = true } = {}) {
    let node = this._nodes.get(nodeId);
    if (!node) {
      return;
    }
    let oldFrameId = node.frameId;
    node.frameId = null;

    let cx = node.x + node.width / 2;
    let cy = node.y + node.height / 2;
    for (let [frameId, frame] of this._frames) {
      if (
        cx >= frame.x &&
        cy >= frame.y &&
        cx <= frame.x + frame.width &&
        cy <= frame.y + frame.height
      ) {
        node.frameId = frameId;
        this._updateNodeGroupVisual(node);
        if (autoResize) {
          this._autoExpandFrame(frameId);
        }
        return;
      }
    }

    this._updateNodeGroupVisual(node);
    if (autoResize && oldFrameId && this._frames.has(oldFrameId)) {
      this._autoShrinkFrame(oldFrameId);
    }
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
