/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * CanvasToolbar - Reusable toolbar for InfiniteCanvas.
 * Provides tool switching, alignment, zoom controls.
 * Works in both standalone test page and browser chrome overlay.
 */
export default class CanvasToolbar {
  constructor(canvas, container) {
    this._canvas = canvas;
    this._container = container;
    this._build();
    this._attachEvents();
  }

  _build() {
    this._container.classList.add("canvas-toolbar");

    // Tool buttons
    this._tools = this._group([
      this._button("move", "\u{1F446}", "Move (V)", true),
      this._button("hand", "\u270B", "Hand (H)"),
      this._button("frame", "\u25A1", "Group (F)"),
      this._button("tab", "\u25A0", "Tab (T)"),
    ]);

    this._sep();

    // Actions
    this._actions = this._group([
      this._actionButton("snap", "Snap: ON", () => {
        this._canvas.snapEnabled = !this._canvas.snapEnabled;
        this._updateSnap();
      }),
      this._actionButton("fit", "Fit All", () => this._canvas.fitAll()),
    ]);

    this._sep();

    // Alignment (shown when 2+ items selected)
    this._alignGroup = this._group([
      this._actionButton("al", "\u2190", () => this._canvas.alignSelection("align-left"), "Align left"),
      this._actionButton("ac", "\u2194", () => this._canvas.alignSelection("align-center-h"), "Align center"),
      this._actionButton("ar", "\u2192", () => this._canvas.alignSelection("align-right"), "Align right"),
      this._actionButton("dh", "\u2261", () => this._canvas.alignSelection("distribute-h"), "Distribute horizontally"),
    ]);
    this._alignGroup.style.display = "none";

    this._sep();

    // Info
    this._zoomDisplay = document.createElement("span");
    this._zoomDisplay.className = "canvas-toolbar-info";
    this._zoomDisplay.textContent = "100%";
    this._container.appendChild(this._zoomDisplay);

    this._selDisplay = document.createElement("span");
    this._selDisplay.className = "canvas-toolbar-info canvas-toolbar-selection";
    this._selDisplay.textContent = "";
    this._container.appendChild(this._selDisplay);
  }

  _button(tool, icon, title, active = false) {
    let btn = document.createElement("button");
    btn.className = "canvas-toolbar-btn" + (active ? " active" : "");
    btn.textContent = icon;
    btn.title = title;
    btn.dataset.tool = tool;
    btn.addEventListener("click", () => {
      this._canvas.activeTool = tool;
    });
    return btn;
  }

  _actionButton(id, label, handler, title = "") {
    let btn = document.createElement("button");
    btn.className = "canvas-toolbar-btn";
    btn.textContent = label;
    btn.dataset.action = id;
    if (title) {
      btn.title = title;
    }
    btn.addEventListener("click", handler);
    return btn;
  }

  _group(buttons) {
    let g = document.createElement("div");
    g.className = "canvas-toolbar-group";
    for (let b of buttons) {
      g.appendChild(b);
    }
    this._container.appendChild(g);
    return g;
  }

  _sep() {
    let s = document.createElement("div");
    s.className = "canvas-toolbar-sep";
    this._container.appendChild(s);
  }

  _attachEvents() {
    this._canvas.on("tool-change", () => this._updateTools());
    this._canvas.on("view-change", () => this._updateZoom());
    this._canvas.on("selection-change", (data) => this._updateSelection(data));
  }

  _updateTools() {
    let tool = this._canvas.activeTool;
    for (let btn of this._tools.querySelectorAll("[data-tool]")) {
      btn.classList.toggle("active", btn.dataset.tool === tool);
    }
  }

  _updateSnap() {
    let btn = this._container.querySelector('[data-action="snap"]');
    if (btn) {
      btn.textContent = "Snap: " + (this._canvas.snapEnabled ? "ON" : "OFF");
      btn.classList.toggle("active", this._canvas.snapEnabled);
    }
  }

  _updateZoom() {
    this._zoomDisplay.textContent = Math.round(this._canvas.zoom * 100) + "%";
  }

  _updateSelection(data) {
    let count = data.selection.length;
    this._selDisplay.textContent = count > 0 ? count + " selected" : "";
    this._alignGroup.style.display = count >= 2 ? "" : "none";
  }

  destroy() {
    this._container.innerHTML = "";
  }
}

export { CanvasToolbar };
