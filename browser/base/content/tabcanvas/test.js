/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function () {
  "use strict";

  let container = document.getElementById("canvas-container");
  let canvas = new InfiniteCanvas(container, { gridSize: 8, snapEnabled: true });

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

  // Pre-populate mock nodes in a grid
  let cols = 4;
  for (let i = 0; i < 8; i++) {
    let col = i % cols;
    let row = Math.floor(i / cols);
    addMockNode(col * 320, row * 252, "Tab " + (i + 1));
  }

  // Pre-populate a frame
  canvas.addFrame("frame_1", {
    x: -40,
    y: -40,
    width: 680,
    height: 290,
    label: "Row 1 Tabs",
  });

  canvas.addFrame("frame_2", {
    x: -40,
    y: 216,
    width: 680,
    height: 290,
    label: "Row 2 Tabs",
  });

  // Fit all into view
  canvas.fitAll();

  // ---- Toolbar wiring ----
  let btnAddNode = document.getElementById("btn-add-node");
  let btnAddFrame = document.getElementById("btn-add-frame");
  let btnSnap = document.getElementById("btn-snap");
  let btnFit = document.getElementById("btn-fit");
  let btnLog = document.getElementById("btn-log");
  let zoomDisplay = document.getElementById("zoom-display");
  let selectionDisplay = document.getElementById("selection-display");
  let eventLog = document.getElementById("event-log");

  btnAddNode.addEventListener("click", () => {
    let rect = container.getBoundingClientRect();
    addMockNode(
      Math.round(rect.width / 2 - 140),
      Math.round(rect.height / 2 - 106),
    );
  });

  btnAddFrame.addEventListener("click", () => {
    // Simulate F key press
    let rect = container.getBoundingClientRect();
    let frameId = "__frame_toolbar_" + Date.now();
    canvas.addFrame(frameId, {
      x: Math.round(rect.width / 2 - 300),
      y: Math.round(rect.height / 2 - 200),
      width: 600,
      height: 400,
      label: "New Frame",
    });
    canvas.deselectAll();
    canvas.select(frameId);
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

  // ---- Canvas events ----
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
  canvas.on("frame-create", data => log("frame-create", data));
  canvas.on("escape", () => log("escape", {}));

  // Keep zoom display in sync with wheel zoom
  let observer = new MutationObserver(() => {
    zoomDisplay.textContent = Math.round(canvas.zoom * 100) + "%";
  });
  observer.observe(container.querySelector(".infinite-canvas-zoom-indicator"), { childList: true });
})();
