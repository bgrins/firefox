/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * InfiniteCanvas - A Figma-style infinite canvas engine.
 *
 * Supports pan, zoom, node selection, move, resize, snap-to-grid,
 * frames (grouping containers), and marquee selection.
 *
 * Zero Firefox/browser-chrome dependencies - works in any web page.
 */
class InfiniteCanvas {
  // Interaction states
  static STATE_IDLE = "idle";
  static STATE_PANNING = "panning";
  static STATE_DRAGGING = "dragging";
  static STATE_RESIZING = "resizing";
  static STATE_MARQUEE = "marquee";

  static MIN_NODE_WIDTH = 100;
  static MIN_NODE_HEIGHT = 80;
  static MIN_ZOOM = 0.1;
  static MAX_ZOOM = 5;
  static ZOOM_STEP = 1.15;
  static HANDLE_SIZE = 8;
  static DRAG_THRESHOLD = 3;

  constructor(container, options = {}) {
    this._container = container;
    this._gridSize = options.gridSize ?? 8;
    this._snapEnabled = options.snapEnabled ?? true;

    // View state
    this._panX = 0;
    this._panY = 0;
    this._zoom = 1;

    // Interaction state
    this._state = InfiniteCanvas.STATE_IDLE;
    this._spaceHeld = false;
    this._pointerStartX = 0;
    this._pointerStartY = 0;
    this._panStartX = 0;
    this._panStartY = 0;

    // Drag state
    this._dragTargets = []; // [{id, startX, startY}]
    this._dragPointerId = null;

    // Resize state
    this._resizeTarget = null;
    this._resizeHandle = "";
    this._resizeStartRect = null;

    // Marquee state
    this._marqueeStartX = 0;
    this._marqueeStartY = 0;

    // Data
    this._nodes = new Map();   // id -> {id, x, y, width, height, title, color, frameId, element}
    this._frames = new Map();  // id -> {id, x, y, width, height, label, element}
    this._selection = new Set();
    this._listeners = {};
    this._nextId = 1;

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
        header.innerHTML = "";
        if (typeof node.headerContent === "string") {
          header.innerHTML = node.headerContent;
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
        body.innerHTML = "";
        if (typeof props.bodyContent === "string") {
          body.innerHTML = props.bodyContent;
        } else if (props.bodyContent instanceof Node) {
          body.appendChild(props.bodyContent);
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

  // ---- Public API: Frames ----

  addFrame(id, { x = 0, y = 0, width = 600, height = 400, label = "Frame" } = {}) {
    if (this._snapEnabled) {
      x = this._snap(x);
      y = this._snap(y);
      width = this._snap(width);
      height = this._snap(height);
    }
    let frame = { id, x, y, width, height, label, element: null };
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
    // Unparent children but keep them
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
    this._updateSelectionVisuals();
    this._emit("selection-change", { selection: [...this._selection] });
  }

  deselect(id) {
    this._selection.delete(id);
    this._updateSelectionVisuals();
    this._emit("selection-change", { selection: [...this._selection] });
  }

  deselectAll() {
    this._selection.clear();
    this._updateSelectionVisuals();
    this._emit("selection-change", { selection: [] });
  }

  getSelection() {
    return [...this._selection];
  }

  // ---- Public API: Events ----

  on(eventName, callback) {
    if (!this._listeners[eventName]) {
      this._listeners[eventName] = [];
    }
    this._listeners[eventName].push(callback);
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

  // ---- DOM Construction ----

  _buildDOM() {
    this._container.classList.add("infinite-canvas");
    this._container.setAttribute("tabindex", "0");

    this._viewport = document.createElement("div");
    this._viewport.className = "infinite-canvas-viewport";
    this._container.appendChild(this._viewport);

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
    el.style.left = node.x + "px";
    el.style.top = node.y + "px";
    el.style.width = node.width + "px";
    el.style.height = node.height + "px";
    el.style.setProperty("--node-bg", node.color);
    el.style.setProperty("--node-header-bg", node.headerColor);

    let header = document.createElement("div");
    header.className = "infinite-canvas-node-header";
    if (node.headerContent instanceof Node) {
      header.appendChild(node.headerContent);
    } else if (typeof node.headerContent === "string") {
      header.innerHTML = node.headerContent;
    } else {
      this._buildDefaultHeader(header, node);
    }
    el.appendChild(header);

    let body = document.createElement("div");
    body.className = "infinite-canvas-node-body";
    el.appendChild(body);

    // Resize handles (8: 4 corners + 4 edges)
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
    el.style.left = frame.x + "px";
    el.style.top = frame.y + "px";
    el.style.width = frame.width + "px";
    el.style.height = frame.height + "px";

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
    this._container.addEventListener("pointerdown", this._onPointerDown.bind(this));
    this._container.addEventListener("pointermove", this._onPointerMove.bind(this));
    this._container.addEventListener("pointerup", this._onPointerUp.bind(this));
    this._container.addEventListener("pointercancel", this._onPointerUp.bind(this));
    this._container.addEventListener("wheel", this._onWheel.bind(this), { passive: false });
    this._container.addEventListener("keydown", this._onKeyDown.bind(this));
    this._container.addEventListener("keyup", this._onKeyUp.bind(this));
    this._container.addEventListener("dblclick", this._onDblClick.bind(this));
    this._container.addEventListener("contextmenu", e => e.preventDefault());
  }

  // ---- Pointer Events ----

  _onPointerDown(event) {
    this._container.focus();

    let resizeHandle = event.target.closest(".infinite-canvas-resize-handle");
    if (resizeHandle && this._state === InfiniteCanvas.STATE_IDLE) {
      this._startResize(event, resizeHandle);
      return;
    }

    // Space+click or middle-click = pan
    if (this._spaceHeld && event.button === 0 || event.button === 1) {
      this._startPan(event);
      return;
    }

    let itemEl = this._findItemElement(event.target);

    if (itemEl && event.button === 0) {
      // Click on a node/frame header = start drag
      let header = event.target.closest(".infinite-canvas-node-header, .infinite-canvas-frame-label");
      if (header || itemEl.dataset.isFrame === "true") {
        this._startDrag(event, itemEl);
        return;
      }
      // Click on node body = select only
      this._handleItemClick(event, itemEl);
      return;
    }

    // Click on empty canvas
    if (event.button === 0 && !itemEl) {
      if (!event.shiftKey) {
        this.deselectAll();
      }
      this._startMarquee(event);
    }
  }

  _onPointerMove(event) {
    switch (this._state) {
      case InfiniteCanvas.STATE_PANNING:
        this._doPan(event);
        break;
      case InfiniteCanvas.STATE_DRAGGING:
        this._doDrag(event);
        break;
      case InfiniteCanvas.STATE_RESIZING:
        this._doResize(event);
        break;
      case InfiniteCanvas.STATE_MARQUEE:
        this._doMarquee(event);
        break;
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
    this._container.setPointerCapture(event.pointerId);
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
    this._container.releasePointerCapture(event.pointerId);
    this._emit("view-change", { panX: this._panX, panY: this._panY, zoom: this._zoom });
  }

  // ---- Drag (Move) ----

  _startDrag(event, itemEl) {
    let id = itemEl.dataset.id;
    // If item isn't selected, select it first
    if (!this._selection.has(id)) {
      if (!event.shiftKey) {
        this.deselectAll();
      }
      this.select(id);
    }

    this._state = InfiniteCanvas.STATE_DRAGGING;
    this._pointerStartX = event.clientX;
    this._pointerStartY = event.clientY;
    this._dragPointerId = event.pointerId;

    // Capture start positions for all selected items
    this._dragTargets = [];
    for (let selId of this._selection) {
      let item = this._nodes.get(selId) || this._frames.get(selId);
      if (item) {
        this._dragTargets.push({ id: selId, startX: item.x, startY: item.y });
      }
    }

    this._container.setPointerCapture(event.pointerId);
    event.preventDefault();
  }

  _doDrag(event) {
    let dx = (event.clientX - this._pointerStartX) / this._zoom;
    let dy = (event.clientY - this._pointerStartY) / this._zoom;

    for (let target of this._dragTargets) {
      let item = this._nodes.get(target.id) || this._frames.get(target.id);
      if (!item) {
        continue;
      }
      let newX = target.startX + dx;
      let newY = target.startY + dy;
      if (this._snapEnabled) {
        newX = this._snap(newX);
        newY = this._snap(newY);
      }
      item.x = newX;
      item.y = newY;
      item.element.style.left = newX + "px";
      item.element.style.top = newY + "px";

      // If it's a frame, also move child nodes
      if (this._frames.has(target.id)) {
        this._moveFrameChildren(target.id, newX - target.startX, newY - target.startY);
      }
    }
  }

  _endDrag(event) {
    let wasDrag =
      Math.abs(event.clientX - this._pointerStartX) > InfiniteCanvas.DRAG_THRESHOLD ||
      Math.abs(event.clientY - this._pointerStartY) > InfiniteCanvas.DRAG_THRESHOLD;

    this._state = InfiniteCanvas.STATE_IDLE;
    this._container.releasePointerCapture(event.pointerId);

    if (wasDrag) {
      // Check if any dragged node should be reparented to a frame
      for (let target of this._dragTargets) {
        if (this._nodes.has(target.id)) {
          this._checkFrameContainment(target.id);
        }
      }
      for (let target of this._dragTargets) {
        let item = this._nodes.get(target.id) || this._frames.get(target.id);
        if (item) {
          this._emit("node-move", { id: target.id, x: item.x, y: item.y });
        }
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
    this._container.setPointerCapture(event.pointerId);
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

    r.width = Math.max(r.width, InfiniteCanvas.MIN_NODE_WIDTH);
    r.height = Math.max(r.height, InfiniteCanvas.MIN_NODE_HEIGHT);

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
    item.element.style.left = r.x + "px";
    item.element.style.top = r.y + "px";
    item.element.style.width = r.width + "px";
    item.element.style.height = r.height + "px";
  }

  _endResize(event) {
    this._state = InfiniteCanvas.STATE_IDLE;
    this._container.releasePointerCapture(event.pointerId);
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
    this._container.setPointerCapture(event.pointerId);
    event.preventDefault();
  }

  _doMarquee(event) {
    let canvasPos = this._screenToCanvas(event.clientX, event.clientY);
    let x1 = Math.min(this._marqueeStartX, canvasPos.x);
    let y1 = Math.min(this._marqueeStartY, canvasPos.y);
    let x2 = Math.max(this._marqueeStartX, canvasPos.x);
    let y2 = Math.max(this._marqueeStartY, canvasPos.y);

    // Position marquee in screen space
    let topLeft = this._canvasToScreen(x1, y1);
    let bottomRight = this._canvasToScreen(x2, y2);
    this._marqueeEl.style.left = topLeft.x + "px";
    this._marqueeEl.style.top = topLeft.y + "px";
    this._marqueeEl.style.width = (bottomRight.x - topLeft.x) + "px";
    this._marqueeEl.style.height = (bottomRight.y - topLeft.y) + "px";

    // Select items within marquee
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
    this._container.releasePointerCapture(event.pointerId);
    this._emit("selection-change", { selection: [...this._selection] });
  }

  // ---- Wheel (Pan + Zoom) ----

  _onWheel(event) {
    event.preventDefault();
    let rect = this._container.getBoundingClientRect();
    let mouseX = event.clientX - rect.left;
    let mouseY = event.clientY - rect.top;

    if (event.ctrlKey || event.metaKey) {
      // Ctrl/Cmd + scroll = zoom toward cursor
      let zoomDelta = event.deltaY > 0 ? 1 / InfiniteCanvas.ZOOM_STEP : InfiniteCanvas.ZOOM_STEP;
      this.zoomTo(this._zoom * zoomDelta, mouseX, mouseY);
    } else {
      // Bare scroll = pan
      this._panX -= event.deltaX;
      this._panY -= event.deltaY;
      this._updateTransform();
    }
  }

  // ---- Keyboard ----

  _onKeyDown(event) {
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
      for (let id of selected) {
        if (this._frames.has(id)) {
          this.removeFrame(id);
        } else {
          this.removeNode(id);
        }
        this._emit("node-delete", { id });
      }
      event.preventDefault();
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
          item.element.style.left = item.x + "px";
          item.element.style.top = item.y + "px";
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

    // F = create frame
    if (event.key === "f" && !event.ctrlKey && !event.metaKey) {
      let rect = this._container.getBoundingClientRect();
      let center = this._screenToCanvas(rect.width / 2, rect.height / 2);
      let frameId = "__frame_" + (this._nextId++);
      this.addFrame(frameId, {
        x: center.x - 300,
        y: center.y - 200,
        width: 600,
        height: 400,
        label: "Frame",
      });
      this.deselectAll();
      this.select(frameId);
      this._emit("frame-create", { id: frameId });
      event.preventDefault();
    }
  }

  _onKeyUp(event) {
    if (event.key === " ") {
      this._spaceHeld = false;
      this._container.classList.remove("space-held");
      event.preventDefault();
    }
  }

  // ---- Double Click ----

  _onDblClick(event) {
    let itemEl = this._findItemElement(event.target);
    if (itemEl) {
      this._emit("node-dblclick", { id: itemEl.dataset.id });
    }
  }

  // ---- Helpers ----

  _handleItemClick(event, itemEl) {
    let id = itemEl.dataset.id;
    if (event.shiftKey) {
      if (this._selection.has(id)) {
        this.deselect(id);
      } else {
        this.select(id);
      }
    } else {
      this.deselectAll();
      this.select(id);
    }
    this._emit("node-click", { id });
  }

  _findItemElement(target) {
    return target.closest(".infinite-canvas-node, .infinite-canvas-frame");
  }

  _snap(value) {
    return Math.round(value / this._gridSize) * this._gridSize;
  }

  _screenToCanvas(screenX, screenY) {
    return {
      x: (screenX - this._panX) / this._zoom,
      y: (screenY - this._panY) / this._zoom,
    };
  }

  _canvasToScreen(canvasX, canvasY) {
    return {
      x: canvasX * this._zoom + this._panX,
      y: canvasY * this._zoom + this._panY,
    };
  }

  _rectsOverlap(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2) {
    return ax1 < bx2 && ax2 > bx1 && ay1 < by2 && ay2 > by1;
  }

  _updateTransform() {
    this._viewport.style.transform = `translate(${this._panX}px, ${this._panY}px) scale(${this._zoom})`;
    this._zoomIndicator.textContent = Math.round(this._zoom * 100) + "%";
  }

  _updateSelectionVisuals() {
    for (let [id, node] of this._nodes) {
      node.element.classList.toggle("selected", this._selection.has(id));
    }
    for (let [id, frame] of this._frames) {
      frame.element.classList.toggle("selected", this._selection.has(id));
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
        node.element.style.left = node.x + "px";
        node.element.style.top = node.y + "px";
      }
    }
  }

  _checkFrameContainment(nodeId) {
    let node = this._nodes.get(nodeId);
    if (!node) {
      return;
    }
    node.frameId = null;
    for (let [frameId, frame] of this._frames) {
      if (
        node.x >= frame.x &&
        node.y >= frame.y &&
        node.x + node.width <= frame.x + frame.width &&
        node.y + node.height <= frame.y + frame.height
      ) {
        node.frameId = frameId;
        return;
      }
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
