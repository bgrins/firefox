/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import InfiniteCanvas from "./canvas-engine.mjs";
import SnapManager from "./snap-manager.mjs";
import CanvasToolbar from "./canvas-toolbar.mjs";

// Expose for Playwright tests
window.InfiniteCanvas = InfiniteCanvas;
window.SnapManager = SnapManager;

{
  let container = document.getElementById("canvas-container");
  let canvas = new InfiniteCanvas(container, { gridSize: 8, snapEnabled: true });
  window.__canvas = canvas;

  // Shared toolbar
  let toolbar = new CanvasToolbar(canvas, document.getElementById("toolbar"));

  let nodeCount = 0;
  let colors = [
    { bg: "#16213e", header: "#0f3460" },
    { bg: "#1a3a2e", header: "#0f6040" },
    { bg: "#3e1621", header: "#601030" },
    { bg: "#3e3416", header: "#605010" },
    { bg: "#1e1640", header: "#302060" },
    { bg: "#16303e", header: "#0f4060" },
  ];

  function addMockNode(x, y, title) {
    let id = "node_" + (++nodeCount);
    let c = colors[nodeCount % colors.length];
    let node = canvas.addNode(id, {
      x, y,
      width: 280,
      height: 212,
      title: title || "Tab " + nodeCount,
      color: c.bg,
      headerColor: c.header,
    });
    // Add placeholder content to the body
    let body = node.element.querySelector(".infinite-canvas-node-body");
    if (body) {
      body.style.background = `linear-gradient(135deg, ${c.bg} 0%, ${c.header} 100%)`;
      let placeholder = document.createElement("div");
      placeholder.style.cssText = "padding:12px;color:rgba(255,255,255,0.2);font-size:40px;font-family:system-ui;text-align:center;line-height:140px";
      placeholder.textContent = "\uD83C\uDF10"; // globe emoji as placeholder
      body.appendChild(placeholder);
    }
    return id;
  }

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
