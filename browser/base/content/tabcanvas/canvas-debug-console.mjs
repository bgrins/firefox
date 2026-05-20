/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * CanvasDebugConsole - in-canvas log panel.
 *
 * Subscribes to the engine's `debug-log` events (and seeds itself with
 * `getDebugLog()` on mount). Renders a floating, scroll-anchored panel
 * inside the supplied container, with a tiny toggle button.
 *
 * Public API:
 *   - new CanvasDebugConsole(canvas, container, opts?)
 *   - .show() / .hide() / .toggle()
 *   - .log(level, message, data?)  — proxies to canvas.debugLog so the
 *     console captures adapter-level events too.
 *   - .destroy() — removes the DOM and listeners.
 */
export default class CanvasDebugConsole {
  constructor(canvas, container, { maxRows = 200, startVisible = false } = {}) {
    this._canvas = canvas;
    this._container = container;
    this._maxRows = maxRows;
    this._build();
    this._wire();
    this._seedFromBuffer();
    if (startVisible) {
      this.show();
    }
  }

  _build() {
    const HTML_NS = "http://www.w3.org/1999/xhtml";
    let doc = this._container.ownerDocument;

    this._toggleBtn = doc.createElementNS(HTML_NS, "button");
    this._toggleBtn.className = "canvas-debug-console-toggle";
    this._toggleBtn.title = "Toggle debug console";
    this._toggleBtn.textContent = "debug";
    this._toggleBtn.style.cssText = [
      "position:absolute", "left:10px", "bottom:10px", "z-index:9998",
      "background:rgba(20,20,30,0.85)", "color:#cccccc",
      "border:1px solid rgba(255,255,255,0.15)", "border-radius:3px",
      "padding:3px 8px", "font:11px system-ui,sans-serif", "cursor:pointer",
      "opacity:0.5",
    ].join(";");
    this._toggleBtn.addEventListener("mouseenter", () => {
      this._toggleBtn.style.opacity = "1";
    });
    this._toggleBtn.addEventListener("mouseleave", () => {
      this._toggleBtn.style.opacity = "0.5";
    });
    // Stop pointerdown so the canvas engine doesn't start a marquee
    // selection when the button is clicked.
    this._toggleBtn.addEventListener("pointerdown", e => e.stopPropagation());
    this._toggleBtn.addEventListener("click", e => {
      e.stopPropagation();
      this.toggle();
    });
    this._container.appendChild(this._toggleBtn);

    this._panel = doc.createElementNS(HTML_NS, "div");
    this._panel.className = "canvas-debug-console";
    this._panel.style.cssText = [
      "position:absolute", "left:10px", "bottom:40px", "width:480px",
      "max-height:320px", "display:none", "flex-direction:column",
      "background:rgba(15,15,25,0.95)", "color:#cccccc",
      "border:1px solid rgba(255,255,255,0.15)", "border-radius:4px",
      "font:11px ui-monospace,monospace", "z-index:9999",
      "box-shadow:0 4px 12px rgba(0,0,0,0.5)",
    ].join(";");

    let header = doc.createElementNS(HTML_NS, "div");
    header.style.cssText = [
      "display:flex", "align-items:center", "justify-content:space-between",
      "padding:6px 10px", "border-bottom:1px solid rgba(255,255,255,0.1)",
      "color:#999", "user-select:none", "flex-shrink:0",
    ].join(";");
    header.textContent = "Debug Console";

    let actions = doc.createElementNS(HTML_NS, "div");
    actions.style.cssText = "display:flex;gap:8px";
    let clearBtn = doc.createElementNS(HTML_NS, "button");
    clearBtn.textContent = "clear";
    clearBtn.style.cssText = "background:transparent;border:none;color:#888;font:inherit;cursor:pointer";
    clearBtn.addEventListener("pointerdown", e => e.stopPropagation());
    clearBtn.addEventListener("click", () => this._clear());
    let closeBtn = doc.createElementNS(HTML_NS, "button");
    closeBtn.textContent = "×";
    closeBtn.style.cssText = "background:transparent;border:none;color:#888;font:14px sans-serif;cursor:pointer;line-height:1";
    closeBtn.addEventListener("pointerdown", e => e.stopPropagation());
    closeBtn.addEventListener("click", () => this.hide());
    actions.appendChild(clearBtn);
    actions.appendChild(closeBtn);
    header.appendChild(actions);
    this._panel.appendChild(header);

    this._body = doc.createElementNS(HTML_NS, "div");
    this._body.style.cssText = "overflow-y:auto;padding:6px 10px;flex:1;min-height:0";
    this._panel.appendChild(this._body);

    // Stop pointerdown anywhere inside the panel so interacting with
    // the console (scrolling, selecting text) never starts a canvas
    // marquee gesture or drags a node behind it.
    this._panel.addEventListener("pointerdown", e => e.stopPropagation());

    this._container.appendChild(this._panel);
  }

  _wire() {
    this._onDebugLog = entry => this._appendRow(entry);
    this._canvas.on("debug-log", this._onDebugLog);

    // Mirror notable engine events into the log so the console is
    // useful out of the box, not silent until something explicitly
    // calls debugLog(). Each subscription is recorded in
    // this._mirrorSubs so destroy() can unwire them in one loop.
    this._mirror = (label, data, level = "info") => this._appendRow({
      ts: Date.now(), level, message: label, data,
    });

    this._mirrorSubs = [];
    let on = (event, fn) => {
      this._canvas.on(event, fn);
      this._mirrorSubs.push([event, fn]);
    };

    on("command-pushed", ({ type, label, coalesced }) =>
      this._mirror(coalesced ? "command coalesced" : "command pushed", { type, label }));
    on("command-undone", ({ type, label }) => this._mirror("undo", { type, label }));
    on("command-redone", ({ type, label }) => this._mirror("redo", { type, label }));
    on("selection-change", ({ selection }) =>
      this._mirror("selection", { size: selection.length, ids: selection }));
    on("tool-change", ({ tool }) => this._mirror("tool", { tool }));
    on("node-click", data => this._mirror("node-click", data));
    on("node-dblclick", data => this._mirror("node-dblclick", data));
    on("node-move", ({ id, x, y }) => this._mirror("node-move", { id, x, y }));
    on("node-resize", data => this._mirror("node-resize", data));
    on("node-delete", ({ id }) => this._mirror("node-delete", { id }));
    on("node-clone", data => this._mirror("node-clone", data));
    on("node-zoom-toggle", ({ id }) => this._mirror("node-zoom-toggle", { id }));
    on("frame-create", ({ id }) => this._mirror("frame-create", { id }));
    on("frame-remove", ({ id }) => this._mirror("frame-remove", { id }));
    on("frame-label-change", ({ id, label }) => this._mirror("frame-label", { id, label }));
    on("escape", () => this._mirror("escape"));
    on("align", ({ command, ids }) => this._mirror("align", { command, count: ids?.length }));
  }

  _seedFromBuffer() {
    let buf = this._canvas.getDebugLog?.() || [];
    for (let entry of buf) {
      this._appendRow(entry);
    }
  }

  _appendRow(entry) {
    const HTML_NS = "http://www.w3.org/1999/xhtml";
    let doc = this._container.ownerDocument;
    let row = doc.createElementNS(HTML_NS, "div");
    let color = "#ccc";
    if (entry.level === "warn") color = "#ffb74d";
    else if (entry.level === "error") color = "#ef5350";
    else if (entry.level === "info") color = "#90caf9";
    row.style.cssText = `color:${color};padding:1px 0;white-space:pre-wrap;word-break:break-all`;
    let time = new Date(entry.ts).toLocaleTimeString("en-US", { hour12: false });
    let dataStr = "";
    if (entry.data !== undefined) {
      try {
        dataStr = " " + JSON.stringify(entry.data);
      } catch (e) {
        dataStr = " [unserializable]";
      }
    }
    row.textContent = `[${time}] [${entry.level}] ${entry.message}${dataStr}`;
    this._body.appendChild(row);
    while (this._body.childNodes.length > this._maxRows) {
      this._body.removeChild(this._body.firstChild);
    }
    // Auto-scroll to the bottom only if we were already near it.
    let nearBottom = this._body.scrollHeight - this._body.scrollTop - this._body.clientHeight < 60;
    if (nearBottom) {
      this._body.scrollTop = this._body.scrollHeight;
    }
  }

  _clear() {
    this._body.textContent = "";
  }

  show() {
    this._panel.style.display = "flex";
    this._visible = true;
    this._body.scrollTop = this._body.scrollHeight;
  }

  hide() {
    this._panel.style.display = "none";
    this._visible = false;
  }

  toggle() {
    if (this._visible) {
      this.hide();
    } else {
      this.show();
    }
  }

  log(level, message, data) {
    this._canvas.debugLog?.(level, message, data);
  }

  destroy() {
    this._canvas.off?.("debug-log", this._onDebugLog);
    for (let [event, fn] of this._mirrorSubs || []) {
      this._canvas.off?.(event, fn);
    }
    this._toggleBtn?.remove();
    this._panel?.remove();
  }
}

export { CanvasDebugConsole };
