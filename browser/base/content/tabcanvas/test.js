/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import InfiniteCanvas from "./canvas-engine.js";
import SnapManager from "./snap-manager.js";

// Expose for Playwright tests
window.InfiniteCanvas = InfiniteCanvas;
window.SnapManager = SnapManager;

{

  let container = document.getElementById("canvas-container");
  let canvas = new InfiniteCanvas(container, { gridSize: 8, snapEnabled: true });
  window.__canvas = canvas; // Expose for testing

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
    canvas.addNode(id, {
      x, y,
      width: 280,
      height: 212,
      title: title || "Tab " + nodeCount,
      color: c.bg,
      headerColor: c.header,
    });
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
  // Position group_2 below group_1 with breathing room
  let g1 = canvas._frames.get("group_1");
  let g2 = canvas._frames.get("group_2");
  g2.x = g1.x;
  g2.y = g1.y + g1.height + 40;
  canvas._applyRect(g2.element, g2);
  canvas.autoLayout("group_2");

  canvas.fitAll();

  // ---- Toolbar wiring ----
  let btnMove = document.getElementById("btn-move");
  let btnHand = document.getElementById("btn-hand");
  let btnAddNode = document.getElementById("btn-add-node");
  let btnAddFrame = document.getElementById("btn-add-frame");
  let btnSnap = document.getElementById("btn-snap");
  let btnFit = document.getElementById("btn-fit");
  let btnLog = document.getElementById("btn-log");
  let zoomDisplay = document.getElementById("zoom-display");
  let selectionDisplay = document.getElementById("selection-display");
  let eventLog = document.getElementById("event-log");

  function updateToolButtons() {
    btnMove.classList.toggle("active", canvas.activeTool === "move");
    btnHand.classList.toggle("active", canvas.activeTool === "hand");
    btnAddNode.classList.toggle("active", canvas.activeTool === "node");
    btnAddFrame.classList.toggle("active", canvas.activeTool === "frame");
  }
  btnMove.addEventListener("click", () => { canvas.activeTool = "move"; updateToolButtons(); });
  btnHand.addEventListener("click", () => { canvas.activeTool = "hand"; updateToolButtons(); });
  canvas.on("tool-change", updateToolButtons);

  btnAddNode.addEventListener("click", () => {
    canvas.activeTool = "node";
    updateToolButtons();
  });

  btnAddFrame.addEventListener("click", () => {
    canvas.activeTool = "frame";
    updateToolButtons();
  });

  btnSnap.addEventListener("click", () => {
    canvas.snapEnabled = !canvas.snapEnabled;
    btnSnap.textContent = "Snap: " + (canvas.snapEnabled ? "ON" : "OFF");
    btnSnap.classList.toggle("active", canvas.snapEnabled);
  });

  btnFit.addEventListener("click", () => {
    canvas.fitAll();
  });

  btnLog.addEventListener("click", () => {
    eventLog.classList.toggle("visible");
  });

  function log(eventName, data) {
    let entry = document.createElement("div");
    entry.className = "log-entry";
    entry.innerHTML = `<span class="event-name">${eventName}</span> ${JSON.stringify(data)}`;
    eventLog.appendChild(entry);
    eventLog.scrollTop = eventLog.scrollHeight;
  }

  canvas.on("selection-change", data => {
    selectionDisplay.textContent = data.selection.length ? data.selection.join(", ") : "none";
    log("selection-change", data);
  });

  canvas.on("view-change", () => {
    zoomDisplay.textContent = Math.round(canvas.zoom * 100) + "%";
    log("view-change", { zoom: canvas.zoom });
  });

  canvas.on("node-click", data => log("node-click", data));
  canvas.on("node-dblclick", data => log("node-dblclick", data));
  canvas.on("node-move", data => log("node-move", data));
  canvas.on("node-resize", data => log("node-resize", data));
  canvas.on("node-delete", data => log("node-delete", data));
  canvas.on("frame-create", data => log("group-create", data));
  canvas.on("escape", () => log("escape", {}));

  // Keep zoom display in sync with wheel zoom
  let observer = new MutationObserver(() => {
    zoomDisplay.textContent = Math.round(canvas.zoom * 100) + "%";
  });
  observer.observe(container.querySelector(".infinite-canvas-zoom-indicator"), { childList: true });
}
