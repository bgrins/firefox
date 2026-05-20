/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import InfiniteCanvas from "./canvas-engine.mjs";
import SnapManager from "./snap-manager.mjs";
import CanvasToolbar from "./canvas-toolbar.mjs";
import CanvasDebugConsole from "./canvas-debug-console.mjs";

// Expose for Playwright tests
window.InfiniteCanvas = InfiniteCanvas;
window.SnapManager = SnapManager;

{
  let container = document.getElementById("canvas-container");
  let canvas = new InfiniteCanvas(container, { gridSize: 8, snapEnabled: true });
  window.__canvas = canvas;

  // Shared toolbar
  let toolbar = new CanvasToolbar(canvas, document.getElementById("toolbar"));
  let debugConsole = new CanvasDebugConsole(canvas, document.getElementById("canvas-container"), { startVisible: true });
  window.__debugConsole = debugConsole;

  let nodeCount = 0;
  let colors = [
    { bg: "#16213e", header: "#0f3460" },
    { bg: "#1a3a2e", header: "#0f6040" },
    { bg: "#3e1621", header: "#601030" },
    { bg: "#3e3416", header: "#605010" },
    { bg: "#1e1640", header: "#302060" },
    { bg: "#16303e", header: "#0f4060" },
  ];

  // Decorate the body of a freshly-created node with the mock-tab visual
  // (gradient, globe icon, + opener). Extracted so the `node-clone` event
  // can re-apply it to cloned nodes too \u2014 without this, alt+drag clones
  // come up as bare black rectangles because the engine's clone only
  // copies geometry/title, not test-page body content.
  function decorateMockBody(nodeId, colorPalette) {
    let n = canvas.getNode(nodeId);
    if (!n) {
      return;
    }
    let body = n.element.querySelector(".infinite-canvas-node-body");
    if (!body) {
      return;
    }
    body.style.background = `linear-gradient(135deg, ${colorPalette.bg} 0%, ${colorPalette.header} 100%)`;
    let placeholder = document.createElement("div");
    placeholder.style.cssText = "padding:12px;color:rgba(255,255,255,0.2);font-size:40px;font-family:system-ui;text-align:center;line-height:140px";
    placeholder.textContent = "\uD83C\uDF10";
    body.appendChild(placeholder);

    // Opener-like demo: clicking this "+" inside the body creates a new
    // child node next to this one, inheriting frame membership. Lives
    // inside the tab itself so it doesn't collide with engine modifier
    // keys (shift = multi-select / drill, alt = clone).
    let opener = document.createElement("button");
    opener.className = "demo-open-child";
    opener.title = "Open child tab";
    opener.textContent = "+";
    opener.style.cssText = "position:absolute;right:8px;bottom:8px;width:24px;height:24px;border-radius:4px;border:1px solid rgba(255,255,255,0.2);background:rgba(0,0,0,0.4);color:#fff;font-size:14px;font-family:system-ui;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0";
    opener.addEventListener("pointerdown", e => e.stopPropagation());
    opener.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      openChildTab(nodeId);
    });
    body.appendChild(opener);
    // Stash the palette so a later clone can re-decorate without having
    // to reverse-engineer the colors back out of the gradient.
    n.__mockColors = colorPalette;
  }

  function addMockNode(x, y, title) {
    let id = "node_" + (++nodeCount);
    let c = colors[nodeCount % colors.length];
    canvas.addNode(id, {
      x, y,
      width: 280,
      height: 212,
      title: title || "Tab " + nodeCount,
      color: c.bg,
      headerColor: c.header,
    });
    decorateMockBody(id, c);
    return id;
  }

  // Click "+" on a tab \u2192 create a sibling tab and push a single
  // undoable command so Ctrl+Z removes the new tab (and Ctrl+Shift+Z
  // re-creates it).
  function openChildTab(sourceId) {
    let source = canvas.getNode(sourceId);
    if (!source) {
      return;
    }
    let pos = canvas.findPositionNearNode(sourceId);
    let prevSelection = [...canvas._selection];
    let newId = "node_" + (++nodeCount);
    let palette = colors[nodeCount % colors.length];
    let nodeData = {
      x: pos.x, y: pos.y, width: 280, height: 212,
      title: "New Tab " + nodeCount,
      color: palette.bg, headerColor: palette.header,
    };
    let frameId = source.frameId || null;

    let apply = () => {
      canvas.addNode(newId, nodeData);
      decorateMockBody(newId, palette);
      if (frameId) {
        canvas.assignNodeToFrame(newId, frameId);
      }
      canvas.deselectAll();
      canvas.select(newId);
    };
    apply();

    canvas._pushCommand(canvas._makeCommand({
      type: "add-tab",
      label: "Open Child Tab",
      undo: () => {
        canvas.removeNode(newId);
        canvas._restoreSelection(prevSelection);
      },
      redo: () => {
        apply();
      },
    }));
    log("open-child", { sourceId, newId, frameId });
  }

  // Re-decorate clones of mock tabs so they don't render as bare black
  // bodies. The engine clone copies geometry + colors but doesn't know
  // about the placeholder/opener content the test page injects.
  canvas.on("node-clone", ({ sourceId, cloneId }) => {
    let source = canvas.getNode(sourceId);
    if (!source) {
      return;
    }
    let palette = source.__mockColors || { bg: source.color, header: source.headerColor };
    decorateMockBody(cloneId, palette);
  });

  // Pre-populate nodes (positions will be set by autoLayout)
  for (let i = 0; i < 8; i++) {
    addMockNode(0, 0, "Tab " + (i + 1));
  }

  // Create tab groups
  canvas.addFrame("group_1", { x: 0, y: 0, width: 100, height: 100, label: "Work Tabs" });
  canvas.addFrame("group_2", { x: 0, y: 0, width: 100, height: 100, label: "Personal Tabs" });

  // Assign membership
  for (let i = 1; i <= 4; i++) {
    let node = canvas.getNode("node_" + i);
    if (node) {
      node.frameId = "group_1";
      canvas._updateNodeGroupVisual(node);
    }
  }
  for (let i = 5; i <= 8; i++) {
    let node = canvas.getNode("node_" + i);
    if (node) {
      node.frameId = "group_2";
      canvas._updateNodeGroupVisual(node);
    }
  }

  // Layout nodes within their groups
  canvas.autoLayout("group_1");
  let g1 = canvas._frames.get("group_1");
  let g2 = canvas._frames.get("group_2");
  g2.x = g1.x;
  g2.y = g1.y + g1.height + 40;
  canvas._applyRect(g2.element, g2);
  canvas.autoLayout("group_2");

  canvas.fitAll();

  // Clear undo/redo stacks built up during initial test-page setup so
  // tests start from a clean slate. (autoLayout etc. now push undo
  // entries; we don't want test setup to pollute them.)
  canvas._undoStack = [];
  canvas._redoStack = [];

  // Event log (test page only - not part of shared toolbar)
  let eventLog = document.getElementById("event-log");
  function log(eventName, data) {
    let entry = document.createElement("div");
    entry.className = "log-entry";
    let nameSpan = document.createElement("span");
    nameSpan.className = "event-name";
    nameSpan.textContent = eventName;
    entry.appendChild(nameSpan);
    entry.appendChild(document.createTextNode(" " + JSON.stringify(data)));
    eventLog.appendChild(entry);
    eventLog.scrollTop = eventLog.scrollHeight;
  }

  canvas.on("node-click", data => log("node-click", data));
  canvas.on("node-dblclick", data => log("node-dblclick", data));
  canvas.on("node-move", data => log("node-move", data));
  canvas.on("node-resize", data => log("node-resize", data));
  canvas.on("node-delete", data => log("node-delete", data));
  canvas.on("frame-create", data => log("group-create", data));
  canvas.on("escape", () => log("escape", {}));

}
