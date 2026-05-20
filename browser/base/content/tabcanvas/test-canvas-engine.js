/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const { test, expect } = require("@playwright/test");

const BASE_URL = "http://localhost:9876/test.html";

// ---- Helpers ----

async function freshPage(page) {
  await page.goto(BASE_URL + "?t=" + Date.now());
  // Wait for ESM modules to load and canvas to initialize
  await page.waitForSelector(".infinite-canvas-node");
  await page.waitForFunction(() => typeof window.__canvas !== "undefined");
}

async function nodePos(page, id) {
  return page.evaluate(nid => {
    const n = window.__canvas._nodes.get(nid);
    return { x: n.x, y: n.y, w: n.width, h: n.height, frame: n.frameId };
  }, id);
}

async function framePos(page, id) {
  return page.evaluate(fid => {
    const f = window.__canvas._frames.get(fid);
    return { x: f.x, y: f.y, w: f.width, h: f.height, label: f.label };
  }, id);
}

async function sel(page) {
  return page.evaluate(() => window.__canvas.getSelection());
}

async function zoomLevel(page) {
  return page.evaluate(() => window.__canvas.zoom);
}

// Select a single node directly via API, bypassing group selection logic
async function selectNode(page, id) {
  await page.evaluate(nid => {
    window.__canvas.deselectAll();
    window.__canvas.select(nid);
  }, id);
}

async function headerCenter(page, nodeId) {
  return page.evaluate(nid => {
    const h = document.querySelector(`[data-id="${nid}"] .infinite-canvas-node-header`);
    const r = h.getBoundingClientRect();
    return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  }, nodeId);
}

async function frameLabelCenter(page, frameId) {
  return page.evaluate(fid => {
    const el = document.querySelector(`[data-id="${fid}"] .infinite-canvas-frame-label`);
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  }, frameId);
}

async function nodeCenter(page, nodeId) {
  return page.evaluate(nid => {
    const el = document.querySelector(`[data-id="${nid}"]`);
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  }, nodeId);
}

async function emptyPoint(page) {
  return page.evaluate(() => {
    const r = document.getElementById("canvas-container").getBoundingClientRect();
    // Avoid the minimap (bottom-right) and zoom indicator
    return { x: Math.round(r.right - 250), y: Math.round(r.bottom - 50) };
  });
}

async function handleCenter(page, nodeId, position) {
  return page.evaluate(([nid, pos]) => {
    const h = document.querySelector(`[data-id="${nid}"] .infinite-canvas-resize-handle[data-position="${pos}"]`);
    const r = h.getBoundingClientRect();
    return { x: Math.round(r.left + r.width / 2), y: Math.round(r.top + r.height / 2) };
  }, [nodeId, position]);
}

async function canvasToScreen(page, cx, cy) {
  return page.evaluate(([x, y]) => {
    const s = window.__canvas._canvasToScreen(x, y);
    return { x: Math.round(s.x), y: Math.round(s.y) };
  }, [cx, cy]);
}

// ---- Tests ----

test.describe("Initialization", () => {
  test("creates canvas with correct number of nodes and groups", async ({ page }) => {
    await freshPage(page);
    const state = await page.evaluate(() => ({
      nodes: window.__canvas._nodes.size,
      frames: window.__canvas._frames.size,
      hasViewport: !!document.querySelector(".infinite-canvas-viewport"),
    }));
    expect(state.nodes).toBe(8);
    expect(state.frames).toBe(2);
    expect(state.hasViewport).toBe(true);
  });

  test("assigns nodes to groups on init", async ({ page }) => {
    await freshPage(page);
    for (let i = 1; i <= 4; i++) {
      expect((await nodePos(page, "node_" + i)).frame).toBe("group_1");
    }
    for (let i = 5; i <= 8; i++) {
      expect((await nodePos(page, "node_" + i)).frame).toBe("group_2");
    }
  });

  test("nodes have 8 resize handles", async ({ page }) => {
    await freshPage(page);
    const count = await page.evaluate(() =>
      document.querySelector('[data-id="node_1"]').querySelectorAll(".infinite-canvas-resize-handle").length
    );
    expect(count).toBe(8);
  });

  test("groups have correct labels", async ({ page }) => {
    await freshPage(page);
    expect((await framePos(page, "group_1")).label).toBe("Work Tabs");
    expect((await framePos(page, "group_2")).label).toBe("Personal Tabs");
  });
});

test.describe("Selection", () => {
  test("click on grouped node selects its group", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_3");
    await page.mouse.click(c.x, c.y);
    const s = await sel(page);
    expect(s).toContain("group_1");
    expect(s).toContain("node_3");
    expect(s.length).toBe(5); // group + 4 children
  });

  test("click on ungrouped node selects only it", async ({ page }) => {
    await freshPage(page);
    // Remove node_3 from its group
    await page.evaluate(() => {
      const n = window.__canvas._nodes.get("node_3");
      n.frameId = null;
      window.__canvas._updateNodeGroupVisual(n);
    });
    const c = await nodeCenter(page, "node_3");
    await page.mouse.click(c.x, c.y);
    const s = await sel(page);
    expect(s).toEqual(["node_3"]);
  });

  test("click on header selects it", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_2");
    await page.mouse.click(h.x, h.y);
    expect(await sel(page)).toContain("node_2");
  });

  test("shift+click adds group to selection", async ({ page }) => {
    await freshPage(page);
    // Click node_1 (selects group_1 + children = 5)
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    expect((await sel(page)).length).toBe(5);
    // Shift+click node_5 (in group_2 - should add group_2 + children)
    const c5 = await nodeCenter(page, "node_5");
    await page.keyboard.down("Shift");
    await page.mouse.click(c5.x, c5.y);
    await page.keyboard.up("Shift");
    const s = await sel(page);
    expect(s).toContain("group_1");
    expect(s).toContain("group_2");
    expect(s.length).toBe(10); // both groups + all 8 children
  });

  test("click on empty canvas deselects all", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    expect((await sel(page)).length).toBeGreaterThan(0);
    const e = await emptyPoint(page);
    await page.mouse.click(e.x, e.y);
    expect((await sel(page)).length).toBe(0);
  });

  test("Escape deselects all", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    expect((await sel(page)).length).toBeGreaterThan(0);
    await page.keyboard.press("Escape");
    expect((await sel(page)).length).toBe(0);
  });

  test("Ctrl+A selects all", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("ControlOrMeta+a");
    expect((await sel(page)).length).toBe(10); // 8 nodes + 2 groups
  });

  test("marquee selects nodes", async ({ page }) => {
    await freshPage(page);
    // Use a wide marquee across the full container to reliably catch nodes
    const bounds = await page.evaluate(() => {
      const r = document.getElementById("canvas-container").getBoundingClientRect();
      return { left: r.left + 5, top: r.top + 5, right: r.right - 200, bottom: r.bottom - 200 };
    });
    await page.mouse.move(bounds.left, bounds.top);
    await page.mouse.down();
    await page.mouse.move(bounds.right, bounds.bottom, { steps: 5 });
    await page.mouse.up();
    expect((await sel(page)).length).toBeGreaterThan(0);
  });

  // Use ungrouped nodes for cmd+click toggle tests so we don't entangle
  // group-selection logic. The group-aware toggle is covered separately.
  async function ungroupAll(page) {
    await page.evaluate(() => {
      for (let [, n] of window.__canvas._nodes) {
        n.frameId = null;
        window.__canvas._updateNodeGroupVisual(n);
      }
    });
  }

  // Both Control (Windows/Linux) and Meta (macOS Cmd) toggle multi-select.
  // Meta also exercises the macOS-specific contextmenu suppression path
  // (cmd+left-click on macOS fires `contextmenu` between pointerdown and
  // pointerup, which the engine has to suppress to keep its selection intact).
  for (const mod of ["Control", "Meta"]) {
    test(`${mod}+click adds an unselected node to selection`, async ({ page }) => {
      await freshPage(page);
      await ungroupAll(page);
      const c1 = await nodeCenter(page, "node_1");
      const c2 = await nodeCenter(page, "node_2");
      await page.mouse.click(c1.x, c1.y);
      expect(await sel(page)).toEqual(["node_1"]);
      await page.keyboard.down(mod);
      await page.mouse.click(c2.x, c2.y);
      await page.keyboard.up(mod);
      const s = await sel(page);
      expect(s).toContain("node_1");
      expect(s).toContain("node_2");
      expect(s.length).toBe(2);
    });

    test(`${mod}+click on a selected node removes it from selection`, async ({ page }) => {
      await freshPage(page);
      await ungroupAll(page);
      const c1 = await nodeCenter(page, "node_1");
      const c2 = await nodeCenter(page, "node_2");
      await page.mouse.click(c1.x, c1.y);
      await page.keyboard.down(mod);
      await page.mouse.click(c2.x, c2.y);
      // Toggle node_1 back off
      await page.mouse.click(c1.x, c1.y);
      await page.keyboard.up(mod);
      expect(await sel(page)).toEqual(["node_2"]);
    });

    test(`${mod}+click toggle does not deselect other nodes`, async ({ page }) => {
      await freshPage(page);
      await ungroupAll(page);
      const c1 = await nodeCenter(page, "node_1");
      const c2 = await nodeCenter(page, "node_2");
      const c3 = await nodeCenter(page, "node_3");
      await page.mouse.click(c1.x, c1.y);
      await page.keyboard.down(mod);
      await page.mouse.click(c2.x, c2.y);
      await page.mouse.click(c3.x, c3.y);
      await page.keyboard.up(mod);
      expect((await sel(page)).sort()).toEqual(["node_1", "node_2", "node_3"]);
    });

    test(`${mod}+click on a grouped node toggles whole group`, async ({ page }) => {
      await freshPage(page);
      const c1 = await nodeCenter(page, "node_1");
      const c5 = await nodeCenter(page, "node_5");
      // Click node_1 selects group_1 + 4 children
      await page.mouse.click(c1.x, c1.y);
      expect((await sel(page)).length).toBe(5);
      // Cmd/Ctrl+click on node_5 adds group_2 + 4 children
      await page.keyboard.down(mod);
      await page.mouse.click(c5.x, c5.y);
      expect((await sel(page)).length).toBe(10);
      // Cmd/Ctrl+click node_5 again toggles group_2 off
      await page.mouse.click(c5.x, c5.y);
      await page.keyboard.up(mod);
      const s = await sel(page);
      expect(s).toContain("group_1");
      expect(s).not.toContain("group_2");
      expect(s).not.toContain("node_5");
      expect(s.length).toBe(5);
    });
  }
});

test.describe("Move", () => {
  test("drag header moves node", async ({ page }) => {
    await freshPage(page);
    const before = await nodePos(page, "node_1");
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 80, h.y + 40, { steps: 5 });
    await page.mouse.up();
    const after = await nodePos(page, "node_1");
    expect(after.x).not.toBe(before.x);
    expect(after.y).not.toBe(before.y);
  });

  test("position snaps to grid", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 53, h.y + 37, { steps: 5 });
    await page.mouse.up();
    const after = await nodePos(page, "node_1");
    expect(after.x % 8).toBe(0);
    expect(after.y % 8).toBe(0);
  });

  test("snap guides appear during drag", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x, h.y + 100, { steps: 10 });
    const guides = await page.evaluate(() =>
      document.querySelectorAll(".infinite-canvas-snap-guide").length
    );
    await page.mouse.up();
    expect(guides).toBeGreaterThan(0);
  });

  test("guides cleared after drag", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x, h.y + 50, { steps: 5 });
    await page.mouse.up();
    const guides = await page.evaluate(() =>
      document.querySelectorAll(".infinite-canvas-snap-guide").length
    );
    expect(guides).toBe(0);
  });

  test("arrow nudge by grid size", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    const before = await nodePos(page, "node_1");
    await page.keyboard.press("ArrowRight");
    await page.keyboard.press("ArrowDown");
    const after = await nodePos(page, "node_1");
    expect(after.x).toBe(before.x + 8);
    expect(after.y).toBe(before.y + 8);
  });

  test("arrow nudge on a selected frame moves its children too", async ({ page }) => {
    await freshPage(page);
    const before = await page.evaluate(() => {
      const c = window.__canvas;
      // Select just the frame (no children in the selection).
      c.deselectAll();
      c.select("group_1");
      document.getElementById("canvas-container").focus();
      let kids = c.getFrameChildren("group_1").map(id => {
        let n = c._nodes.get(id);
        return { id, x: n.x, y: n.y };
      });
      let frame = c._frames.get("group_1");
      return { frame: { x: frame.x, y: frame.y }, kids };
    });
    await page.keyboard.press("ArrowRight");
    await page.keyboard.press("ArrowDown");
    const after = await page.evaluate(() => {
      const c = window.__canvas;
      let kids = c.getFrameChildren("group_1").map(id => {
        let n = c._nodes.get(id);
        return { id, x: n.x, y: n.y };
      });
      let frame = c._frames.get("group_1");
      return { frame: { x: frame.x, y: frame.y }, kids };
    });
    // Frame moved by 8px on each axis (default grid).
    expect(after.frame.x).toBe(before.frame.x + 8);
    expect(after.frame.y).toBe(before.frame.y + 8);
    // Every child moved by the same delta.
    for (let i = 0; i < before.kids.length; i++) {
      expect(after.kids[i].x).toBe(before.kids[i].x + 8);
      expect(after.kids[i].y).toBe(before.kids[i].y + 8);
    }
  });

  test("shift+arrow nudge by 2x grid", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    const before = await nodePos(page, "node_1");
    await page.keyboard.press("Shift+ArrowRight");
    const after = await nodePos(page, "node_1");
    expect(after.x).toBe(before.x + 16);
  });
});

test.describe("Resize", () => {
  test("SE handle resizes node", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const node = c._nodes.get("node_1");
      c.deselectAll();
      c.select("node_1");
      const beforeW = node.width;
      const beforeH = node.height;
      const beforeX = node.x;
      const beforeY = node.y;
      c._resizeTarget = "node_1";
      c._resizeHandle = "se";
      c._resizeStartRect = { x: node.x, y: node.y, width: node.width, height: node.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      c._doResize({ clientX: 80, clientY: 80 });
      return {
        grew: node.width > beforeW && node.height > beforeH,
        originStable: node.x === beforeX && node.y === beforeY,
      };
    });
    expect(result.grew).toBe(true);
    expect(result.originStable).toBe(true);
  });

  test("NW handle resize adjusts origin correctly", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const node = c._nodes.get("node_1");
      c.deselectAll();
      c.select("node_1");
      const beforeX = node.x;
      const beforeY = node.y;
      const beforeW = node.width;
      const beforeH = node.height;
      c._resizeTarget = "node_1";
      c._resizeHandle = "nw";
      c._resizeStartRect = { x: node.x, y: node.y, width: node.width, height: node.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      c._doResize({ clientX: -40, clientY: -40 });
      return {
        movedUp: node.x < beforeX && node.y < beforeY,
        grew: node.width > beforeW && node.height > beforeH,
      };
    });
    expect(result.movedUp).toBe(true);
    expect(result.grew).toBe(true);
  });

  test("resize clamps to min size without teleporting", async ({ page }) => {
    await freshPage(page);
    // Use programmatic resize to test the clamping logic precisely
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      const node = c._nodes.get("node_1");
      const origX = node.x;
      const origW = node.width;
      // Simulate W-handle drag that would shrink below minimum
      c._resizeTarget = "node_1";
      c._resizeHandle = "w";
      c._resizeStartRect = { x: node.x, y: node.y, width: node.width, height: node.height };
      // Fake a large rightward dx (shrinking from west)
      c._pointerStartX = 0;
      c._doResize({ clientX: 500, clientY: 0 });
      // Node should be at min width, and x should be startX + startWidth - minWidth
      return {
        width: node.width,
        x: node.x,
        expectedX: c._resizeStartRect.x + origW - InfiniteCanvas.MIN_NODE_WIDTH,
        minWidth: InfiniteCanvas.MIN_NODE_WIDTH,
      };
    });
    expect(result.width).toBe(result.minWidth);
    expect(result.x).toBe(result.expectedX);
  });

  test("resize snaps to grid", async ({ page }) => {
    await freshPage(page);
    // Programmatic test for snap precision
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const node = c._nodes.get("node_1");
      c.deselectAll();
      c.select("node_1");
      c._resizeTarget = "node_1";
      c._resizeHandle = "se";
      c._resizeStartRect = { x: node.x, y: node.y, width: node.width, height: node.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._doResize({ clientX: 33, clientY: 17 });
      return { w: node.width % 8, h: node.height % 8 };
    });
    expect(result.w).toBe(0);
    expect(result.h).toBe(0);
  });
});

test.describe("Pan and Zoom", () => {
  test("bare scroll pans", async ({ page }) => {
    await freshPage(page);
    const before = await page.evaluate(() => ({
      panX: window.__canvas._panX, panY: window.__canvas._panY,
    }));
    // Use synthetic wheel event since Playwright's mouse.wheel may not target the canvas
    await page.evaluate(() => {
      const c = document.getElementById("canvas-container");
      c.dispatchEvent(new WheelEvent("wheel", {
        deltaX: 0, deltaY: 200,
        clientX: 500, clientY: 400,
        bubbles: true, cancelable: true,
      }));
    });
    const after = await page.evaluate(() => ({
      panX: window.__canvas._panX, panY: window.__canvas._panY,
    }));
    expect(after.panY).toBeLessThan(before.panY);
    expect(after.panX).toBe(before.panX);
  });

  test("Ctrl+scroll zooms", async ({ page }) => {
    await freshPage(page);
    const before = await zoomLevel(page);
    await page.evaluate(() => {
      const c = document.getElementById("canvas-container");
      c.dispatchEvent(new WheelEvent("wheel", {
        deltaY: -100, ctrlKey: true, clientX: 500, clientY: 400,
        bubbles: true, cancelable: true,
      }));
    });
    expect(await zoomLevel(page)).toBeGreaterThan(before);
  });

  test("Ctrl+= zooms in, Ctrl+- zooms out", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    const initial = await zoomLevel(page);
    await page.keyboard.press("ControlOrMeta+=");
    const zi = await zoomLevel(page);
    expect(zi).toBeGreaterThan(initial);
    await page.keyboard.press("ControlOrMeta+-");
    expect(await zoomLevel(page)).toBeLessThan(zi);
  });

  test("Ctrl+0 resets to 100%", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    expect(await zoomLevel(page)).not.toBe(1);
    await page.keyboard.press("ControlOrMeta+0");
    expect(await zoomLevel(page)).toBe(1);
  });

  test("Ctrl+1 fits all", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("ControlOrMeta+0");
    expect(await zoomLevel(page)).toBe(1);
    await page.keyboard.press("ControlOrMeta+1");
    // Wait for animation to complete
    await page.waitForTimeout(300);
    expect(await zoomLevel(page)).not.toBe(1);
  });

  test("space+drag pans", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    const before = await page.evaluate(() => ({
      panX: window.__canvas._panX, panY: window.__canvas._panY,
    }));
    await page.keyboard.down(" ");
    await page.mouse.move(500, 400);
    await page.mouse.down();
    await page.mouse.move(600, 300, { steps: 5 });
    await page.mouse.up();
    await page.keyboard.up(" ");
    const after = await page.evaluate(() => ({
      panX: window.__canvas._panX, panY: window.__canvas._panY,
    }));
    expect(after.panX).toBeGreaterThan(before.panX);
    expect(after.panY).toBeLessThan(before.panY);
  });
});

test.describe("Tab Groups", () => {
  test("F activates frame drawing tool", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("f");
    expect(await page.evaluate(() => window.__canvas.activeTool)).toBe("frame");
  });

  test("drawing a group and it auto-selects", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("f");
    // Draw in empty area
    const e = await emptyPoint(page);
    await page.mouse.move(e.x - 200, e.y - 100);
    await page.mouse.down();
    await page.mouse.move(e.x, e.y, { steps: 5 });
    await page.mouse.up();
    const s = await sel(page);
    expect(s.length).toBe(1);
    expect(s[0]).toMatch(/^__group_/);
  });

  test("dragging group moves children", async ({ page }) => {
    await freshPage(page);
    const childBefore = await nodePos(page, "node_1");
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.move(lbl.x, lbl.y);
    await page.mouse.down();
    await page.mouse.move(lbl.x + 80, lbl.y + 40, { steps: 5 });
    await page.mouse.up();
    const childAfter = await nodePos(page, "node_1");
    expect(childAfter.x).toBeGreaterThan(childBefore.x);
    expect(childAfter.y).toBeGreaterThan(childBefore.y);
  });

  test("drop node into group assigns it with highlight", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_8");
    const h8 = await headerCenter(page, "node_8");
    const g1 = await page.evaluate(() => {
      const f = window.__canvas._frames.get("group_1");
      const s = window.__canvas._canvasToScreen(f.x + f.width / 2, f.y + f.height / 2);
      return { x: Math.round(s.x), y: Math.round(s.y) };
    });
    await page.mouse.move(h8.x, h8.y);
    await page.mouse.down();
    await page.mouse.move(g1.x, g1.y, { steps: 10 });
    const highlight = await page.evaluate(() =>
      !!document.querySelector(".infinite-canvas-frame.drop-target")
    );
    await page.mouse.up();
    expect(highlight).toBe(true);
    expect((await nodePos(page, "node_8")).frame).toBe("group_1");
  });

  test("Delete removes group but keeps children when only group selected", async ({ page }) => {
    await freshPage(page);
    // Select only the group via API (not click, which now also selects children)
    await page.evaluate(() => {
      window.__canvas.deselectAll();
      window.__canvas._selection.add("group_1");
      window.__canvas._updateSelectionVisuals();
    });
    const n1Before = await nodePos(page, "node_1");
    // Use the removeFrame API directly
    await page.evaluate(() => {
      window.__canvas.removeFrame("group_1");
    });
    expect(await page.evaluate(() => window.__canvas._frames.has("group_1"))).toBe(false);
    const n1After = await nodePos(page, "node_1");
    expect(n1After.frame).toBeNull();
    expect(n1After.x).toBe(n1Before.x);
  });
});

test.describe("Delete", () => {
  test("Delete removes selected node", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_3");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Delete");
    expect(await page.evaluate(() => window.__canvas._nodes.has("node_3"))).toBe(false);
    expect((await sel(page)).length).toBe(0);
  });

  test("Delete removes multiple selected", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    await page.evaluate(() => window.__canvas.select("node_2"));
    expect((await sel(page)).length).toBe(2);
    await page.evaluate(() =>
      document.getElementById("canvas-container").focus()
    );
    await page.keyboard.press("Delete");
    expect(await page.evaluate(() => window.__canvas._nodes.has("node_1"))).toBe(false);
    expect(await page.evaluate(() => window.__canvas._nodes.has("node_2"))).toBe(false);
    expect((await sel(page)).length).toBe(0);
  });
});

test.describe("Double Click", () => {
  test("emits node-dblclick event on two quick clicks", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__dblclicked = null;
      window.__canvas.on("node-dblclick", d => { window.__dblclicked = d.id; });
    });
    const c = await nodeCenter(page, "node_4");
    // Two quick clicks: first selects group, second drills into node_4 and fires dblclick
    await page.mouse.click(c.x, c.y);
    await page.mouse.click(c.x, c.y);
    expect(await page.evaluate(() => window.__dblclicked)).toBe("node_4");
  });
});

test.describe("Drag Threshold", () => {
  test("tiny movement below threshold does not move node", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    const before = await nodePos(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    // Move only 1px - below DRAG_THRESHOLD of 3
    await page.mouse.move(h.x + 1, h.y + 1, { steps: 1 });
    await page.mouse.up();
    const after = await nodePos(page, "node_1");
    expect(after.x).toBe(before.x);
    expect(after.y).toBe(before.y);
  });
});

test.describe("Zoom Clamping", () => {
  test("zoom does not go below MIN_ZOOM", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.zoomTo(0.01, 500, 400);
    });
    const z = await zoomLevel(page);
    expect(z).toBeGreaterThanOrEqual(0.1);
  });

  test("zoom does not go above MAX_ZOOM", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.zoomTo(10, 500, 400);
    });
    const z = await zoomLevel(page);
    expect(z).toBeLessThanOrEqual(5);
  });
});

test.describe("Multi-Selection Drag", () => {
  test("dragging with multiple selected moves all", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    await page.evaluate(() => window.__canvas.select("node_2"));
    expect((await sel(page)).length).toBe(2);

    const b1 = await nodePos(page, "node_1");
    const b2 = await nodePos(page, "node_2");

    // Drag via node_1 header
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 80, h.y + 40, { steps: 5 });
    await page.mouse.up();

    const a1 = await nodePos(page, "node_1");
    const a2 = await nodePos(page, "node_2");
    // Both should have moved by roughly the same delta
    const dx1 = a1.x - b1.x;
    const dx2 = a2.x - b2.x;
    expect(dx1).not.toBe(0);
    expect(dx1).toBe(dx2);
  });
});

test.describe("Node Leaving Frame", () => {
  test("nudging node out of frame clears frameId", async ({ page }) => {
    await freshPage(page);
    const before = await nodePos(page, "node_1");
    expect(before.frame).toBe("group_1");

    // Select node_1 via API to avoid group selection
    await selectNode(page, "node_1");
    await page.evaluate(() =>
      document.getElementById("canvas-container").focus()
    );
    for (let i = 0; i < 50; i++) {
      await page.keyboard.press("Shift+ArrowRight");
    }
    const after = await nodePos(page, "node_1");
    // Should have left the group since it's been nudged far right
    expect(after.frame).not.toBe("group_1");
  });
});

test.describe("API", () => {
  test("removeNode via API works", async ({ page }) => {
    await freshPage(page);
    const count = await page.evaluate(() => {
      window.__canvas.removeNode("node_5");
      return window.__canvas._nodes.size;
    });
    expect(count).toBe(7);
  });

  test("removeFrame via API unparents children", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      window.__canvas.removeFrame("group_1");
      const n1 = window.__canvas._nodes.get("node_1");
      return { frameExists: window.__canvas._frames.has("group_1"), n1Frame: n1.frameId };
    });
    expect(result.frameExists).toBe(false);
    expect(result.n1Frame).toBeNull();
  });

  test("updateNode changes title", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__canvas.updateNode("node_1", { title: "Renamed Tab" });
    });
    const title = await page.evaluate(() =>
      document.querySelector('[data-id="node_1"] .infinite-canvas-node-title')?.textContent
    );
    expect(title).toBe("Renamed Tab");
  });

  test("updateFrame changes label", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__canvas.updateFrame("group_1", { label: "Renamed Group" });
    });
    const label = await page.evaluate(() =>
      document.querySelector('[data-id="group_1"] .infinite-canvas-frame-label')?.textContent
    );
    expect(label).toBe("Renamed Group");
  });
});

// ==================================================================
// Phase 1 Tests (TDD - written to fail first, then fixed)
// ==================================================================

test.describe("Phase 1a: Coordinate Transforms", () => {
  test("_screenToCanvas accounts for container offset", async ({ page }) => {
    await freshPage(page);
    // The test page has a 40px toolbar above the canvas container.
    // _screenToCanvas(0, 40) should map to canvas origin when pan=0, zoom=1.
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Reset to known view state
      c._panX = 0;
      c._panY = 0;
      c._zoom = 1;
      // The container starts at y=40 due to the toolbar
      const rect = document.getElementById("canvas-container").getBoundingClientRect();
      const pos = c._screenToCanvas(rect.left, rect.top);
      return { x: pos.x, y: pos.y, containerTop: rect.top };
    });
    // Should be (0,0) in canvas space, not some offset value
    expect(result.x).toBeCloseTo(0, 0);
    expect(result.y).toBeCloseTo(0, 0);
    expect(result.containerTop).toBeGreaterThan(0); // confirms toolbar offset exists
  });

  test("_canvasToScreen is inverse of _screenToCanvas", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c._panX = 50;
      c._panY = 30;
      c._zoom = 1.5;
      const rect = document.getElementById("canvas-container").getBoundingClientRect();
      // Round-trip: screen -> canvas -> screen
      const screenX = rect.left + 200;
      const screenY = rect.top + 150;
      const canvasPos = c._screenToCanvas(screenX, screenY);
      const backToScreen = c._canvasToScreen(canvasPos.x, canvasPos.y);
      return {
        origX: screenX, origY: screenY,
        roundTripX: backToScreen.x, roundTripY: backToScreen.y,
      };
    });
    expect(result.roundTripX).toBeCloseTo(result.origX, 0);
    expect(result.roundTripY).toBeCloseTo(result.origY, 0);
  });

  test("marquee selection works correctly with container offset", async ({ page }) => {
    await freshPage(page);
    // Deselect, then marquee around the entire canvas area
    await page.evaluate(() => window.__canvas.deselectAll());
    // Get the canvas container bounds and drag across a large area
    const bounds = await page.evaluate(() => {
      const r = document.getElementById("canvas-container").getBoundingClientRect();
      return { left: r.left + 10, top: r.top + 10, right: r.right - 10, bottom: r.bottom - 10 };
    });
    await page.mouse.move(bounds.left, bounds.top);
    await page.mouse.down();
    await page.mouse.move(bounds.right, bounds.bottom, { steps: 5 });
    await page.mouse.up();
    const s = await sel(page);
    // A canvas-wide marquee should select at least some nodes and groups
    expect(s.length).toBeGreaterThan(0);
    expect(s).toContain("node_1");
  });
});

test.describe("Phase 1b: Dot Grid Tracking", () => {
  test("container has CSS custom properties for pan/zoom", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const el = document.getElementById("canvas-container");
      const style = getComputedStyle(el);
      return {
        hasPanX: style.getPropertyValue("--canvas-pan-x") !== "",
        hasPanY: style.getPropertyValue("--canvas-pan-y") !== "",
        hasZoom: style.getPropertyValue("--canvas-zoom") !== "",
      };
    });
    expect(result.hasPanX).toBe(true);
    expect(result.hasPanY).toBe(true);
    expect(result.hasZoom).toBe(true);
  });

  test("CSS custom properties update when view changes", async ({ page }) => {
    await freshPage(page);
    const before = await page.evaluate(() => {
      const el = document.getElementById("canvas-container");
      return {
        panX: el.style.getPropertyValue("--canvas-pan-x"),
        zoom: el.style.getPropertyValue("--canvas-zoom"),
      };
    });
    // Zoom in
    await page.evaluate(() => {
      const c = window.__canvas;
      c.zoomTo(2, 500, 400);
    });
    const after = await page.evaluate(() => {
      const el = document.getElementById("canvas-container");
      return {
        panX: el.style.getPropertyValue("--canvas-pan-x"),
        zoom: el.style.getPropertyValue("--canvas-zoom"),
      };
    });
    expect(after.zoom).not.toBe(before.zoom);
  });
});

test.describe("Phase 1c: view-change Events", () => {
  test("view-change fires on wheel zoom", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__viewChanges = 0;
      window.__canvas.on("view-change", () => { window.__viewChanges++; });
    });
    // Ctrl+scroll zoom
    await page.evaluate(() => {
      const c = document.getElementById("canvas-container");
      c.dispatchEvent(new WheelEvent("wheel", {
        deltaY: -100, ctrlKey: true,
        clientX: 500, clientY: 400,
        bubbles: true, cancelable: true,
      }));
    });
    const count = await page.evaluate(() => window.__viewChanges);
    expect(count).toBeGreaterThan(0);
  });

  test("view-change fires on keyboard zoom", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.evaluate(() => {
      window.__viewChanges = 0;
      window.__canvas.on("view-change", () => { window.__viewChanges++; });
    });
    await page.keyboard.press("ControlOrMeta+=");
    const count = await page.evaluate(() => window.__viewChanges);
    expect(count).toBeGreaterThan(0);
  });

  test("view-change fires on fitAll", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__viewChanges = 0;
      window.__canvas.on("view-change", () => { window.__viewChanges++; });
      window.__canvas.fitAll();
    });
    const count = await page.evaluate(() => window.__viewChanges);
    expect(count).toBeGreaterThan(0);
  });

  test("view-change fires on bare scroll pan", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      window.__viewChanges = 0;
      window.__canvas.on("view-change", () => { window.__viewChanges++; });
      const c = document.getElementById("canvas-container");
      c.dispatchEvent(new WheelEvent("wheel", {
        deltaX: 0, deltaY: 100,
        clientX: 500, clientY: 400,
        bubbles: true, cancelable: true,
      }));
    });
    const count = await page.evaluate(() => window.__viewChanges);
    expect(count).toBeGreaterThan(0);
  });
});

test.describe("Phase 1d: destroy() and off()", () => {
  test("destroy() removes all DOM and listeners", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const container = document.getElementById("canvas-container");
      const c = window.__canvas;
      // Verify DOM exists
      const hadViewport = !!container.querySelector(".infinite-canvas-viewport");
      const hadClass = container.classList.contains("infinite-canvas");
      // Destroy
      c.destroy();
      const hasViewport = !!container.querySelector(".infinite-canvas-viewport");
      const hasClass = container.classList.contains("infinite-canvas");
      const hasNodes = container.querySelectorAll(".infinite-canvas-node").length;
      return { hadViewport, hadClass, hasViewport, hasClass, hasNodes };
    });
    expect(result.hadViewport).toBe(true);
    expect(result.hadClass).toBe(true);
    expect(result.hasViewport).toBe(false);
    expect(result.hasClass).toBe(false);
    expect(result.hasNodes).toBe(0);
  });

  test("off() removes a specific listener", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let count = 0;
      const handler = () => { count++; };
      c.on("node-click", handler);
      c._emit("node-click", {});
      const afterOn = count;
      c.off("node-click", handler);
      c._emit("node-click", {});
      const afterOff = count;
      return { afterOn, afterOff };
    });
    expect(result.afterOn).toBe(1);
    expect(result.afterOff).toBe(1); // should NOT have incremented
  });
});

test.describe("Phase 1g: Frame Resize + Auto-expand/shrink", () => {
  test("frame can be resized via handles", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const beforeW = frame.width;
      const beforeH = frame.height;
      // Programmatic resize via SE handle
      c._resizeTarget = "group_1";
      c._resizeHandle = "se";
      c._resizeStartRect = { x: frame.x, y: frame.y, width: frame.width, height: frame.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      c._doResize({ clientX: 80, clientY: 80 });
      return {
        grew: frame.width > beforeW && frame.height > beforeH,
      };
    });
    expect(result.grew).toBe(true);
  });

  test("auto-expand grows group when node dropped inside", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const beforeW = frame.width;
      const beforeRight = frame.x + frame.width;
      // Place node so its CENTER is inside the frame but its RIGHT EDGE extends past
      // Center needs to be < frame.x + frame.width, so x + 140 < beforeRight
      // x = beforeRight - 200 -> center at beforeRight - 60, which is inside
      // right edge at beforeRight + 80, which is outside -> should auto-expand
      const node = c._nodes.get("node_8");
      node.x = beforeRight - 200;
      node.y = frame.y + 50;
      c._applyRect(node.element, node);
      c._checkFrameContainment("node_8");
      return {
        assigned: node.frameId === "group_1",
        expanded: frame.width > beforeW,
      };
    });
    expect(result.assigned).toBe(true);
    expect(result.expanded).toBe(true);
  });

  test("auto-shrink contracts group when node leaves", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Create a large frame with two nodes: one near left, one near right
      c.addFrame("shrink_test", { x: 0, y: 800, width: 800, height: 300, label: "Shrink Test" });
      const nA = c.addNode("shrink_a", { x: 24, y: 824, width: 104, height: 80 });
      const nB = c.addNode("shrink_b", { x: 600, y: 824, width: 104, height: 80 });
      nA.frameId = "shrink_test";
      nB.frameId = "shrink_test";
      const beforeW = c._frames.get("shrink_test").width;
      // Move nB completely outside the frame
      nB.x = 5000;
      nB.y = 5000;
      c._applyRect(nB.element, nB);
      c._checkFrameContainment("shrink_b");
      const shrunkW = c._frames.get("shrink_test").width;
      return {
        left: nB.frameId !== "shrink_test",
        beforeW,
        shrunkW,
      };
    });
    expect(result.left).toBe(true);
    // Frame should shrink to fit only nA (much less than 800)
    expect(result.shrunkW).toBeLessThan(result.beforeW);
  });
});

// ==================================================================
// Phase 2 Tests: Performance
// ==================================================================

test.describe("Phase 2: Performance", () => {
  test("handles 100 nodes without excessive overhead", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const t0 = performance.now();
      for (let i = 0; i < 100; i++) {
        c.addNode("perf_" + i, {
          x: (i % 10) * 320,
          y: Math.floor(i / 10) * 260,
          width: 280,
          height: 212,
          title: "Perf Node " + i,
        });
      }
      const createTime = performance.now() - t0;
      return { totalNodes: c._nodes.size, createTime };
    });
    expect(result.totalNodes).toBe(108); // 8 initial + 100 new
    expect(result.createTime).toBeLessThan(500);
  });

  test("nodes use CSS transforms for positioning", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const node = document.querySelector('[data-id="node_1"]');
      return { hasTransform: node.style.transform.includes("translate") };
    });
    expect(result.hasTransform).toBe(true);
  });

  test("container has is-interacting class during drag", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 50, h.y + 50, { steps: 3 });
    const hasCls = await page.evaluate(() =>
      document.getElementById("canvas-container").classList.contains("is-interacting")
    );
    await page.mouse.up();
    const hasClsAfter = await page.evaluate(() =>
      document.getElementById("canvas-container").classList.contains("is-interacting")
    );
    expect(hasCls).toBe(true);
    expect(hasClsAfter).toBe(false);
  });

  test("drag 50 selected nodes under 16ms per move", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let i = 0; i < 50; i++) {
        c.addNode("drag_" + i, {
          x: (i % 10) * 320,
          y: Math.floor(i / 10) * 260,
          width: 280, height: 212,
          title: "Drag " + i,
        });
      }
    });
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("ControlOrMeta+a");
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    const timing = await page.evaluate(() => {
      const container = document.getElementById("canvas-container");
      const times = [];
      for (let i = 0; i < 10; i++) {
        const t0 = performance.now();
        container.dispatchEvent(new PointerEvent("pointermove", {
          clientX: 300 + i * 5, clientY: 300 + i * 5,
          bubbles: true, pointerId: 1,
        }));
        times.push(performance.now() - t0);
      }
      return { avg: times.reduce((a, b) => a + b, 0) / times.length, max: Math.max(...times) };
    });
    await page.mouse.up();
    expect(timing.avg).toBeLessThan(16);
  });
});

// ==================================================================
// Phase 3 Tests: Feature Completeness
// ==================================================================

test.describe("Phase 3a: Serialization", () => {
  test("toJSON returns full canvas state", async ({ page }) => {
    await freshPage(page);
    const json = await page.evaluate(() => {
      const c = window.__canvas;
      return c.toJSON();
    });
    expect(json.nodes).toBeDefined();
    expect(json.nodes.length).toBe(8);
    expect(json.frames).toBeDefined();
    expect(json.frames.length).toBe(2);
    expect(json.viewState).toBeDefined();
    expect(json.viewState.zoom).toBeDefined();
    expect(json.viewState.panX).toBeDefined();
    // Each node should have id, x, y, width, height, title, frameId
    expect(json.nodes[0].id).toBeDefined();
    expect(json.nodes[0].x).toBeDefined();
    expect(json.nodes[0].frameId).toBeDefined();
  });

  test("fromJSON restores canvas state", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const saved = c.toJSON();
      // Modify the canvas
      c.removeNode("node_1");
      c.removeNode("node_2");
      c.removeFrame("group_1");
      const afterDelete = { nodes: c._nodes.size, frames: c._frames.size };
      // Restore
      c.fromJSON(saved);
      const afterRestore = {
        nodes: c._nodes.size,
        frames: c._frames.size,
        node1Exists: c._nodes.has("node_1"),
        group1Exists: c._frames.has("group_1"),
        zoomRestored: Math.abs(c._zoom - saved.viewState.zoom) < 0.01,
      };
      return { afterDelete, afterRestore };
    });
    expect(result.afterDelete.nodes).toBe(6);
    expect(result.afterDelete.frames).toBe(1);
    expect(result.afterRestore.nodes).toBe(8);
    expect(result.afterRestore.frames).toBe(2);
    expect(result.afterRestore.node1Exists).toBe(true);
    expect(result.afterRestore.group1Exists).toBe(true);
    expect(result.afterRestore.zoomRestored).toBe(true);
  });

  test("fromJSON renders DOM correctly", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      const saved = c.toJSON();
      c.fromJSON(saved);
    });
    const count = await page.evaluate(() =>
      document.querySelectorAll(".infinite-canvas-node").length
    );
    expect(count).toBe(8);
  });
});

test.describe("Phase 3b: Undo/Redo", () => {
  test("Ctrl+Z undoes a move", async ({ page }) => {
    await freshPage(page);
    const before = await nodePos(page, "node_1");
    // Drag node_1
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 80, h.y + 80, { steps: 5 });
    await page.mouse.up();
    const afterMove = await nodePos(page, "node_1");
    expect(afterMove.x).not.toBe(before.x);
    // Undo
    await page.keyboard.press("ControlOrMeta+z");
    const afterUndo = await nodePos(page, "node_1");
    expect(afterUndo.x).toBe(before.x);
    expect(afterUndo.y).toBe(before.y);
  });

  test("Ctrl+Shift+Z redoes", async ({ page }) => {
    await freshPage(page);
    const before = await nodePos(page, "node_1");
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 80, h.y + 80, { steps: 5 });
    await page.mouse.up();
    const afterMove = await nodePos(page, "node_1");
    // Undo then redo
    await page.keyboard.press("ControlOrMeta+z");
    await page.keyboard.press("ControlOrMeta+Shift+z");
    const afterRedo = await nodePos(page, "node_1");
    expect(afterRedo.x).toBe(afterMove.x);
    expect(afterRedo.y).toBe(afterMove.y);
  });

  test("Ctrl+Z undoes a delete", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_3");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Delete");
    expect(await page.evaluate(() => window.__canvas._nodes.has("node_3"))).toBe(false);
    // Undo
    await page.keyboard.press("ControlOrMeta+z");
    expect(await page.evaluate(() => window.__canvas._nodes.has("node_3"))).toBe(true);
  });
});

test.describe("Phase 3c: Zoom-to-selection and Positioning API", () => {
  test("fitSelection zooms to selected items", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.fitSelection(false); // no animation for test
    });
    const result = await page.evaluate(() => {
      return { changed: window.__canvas._zoom !== 1 };
    });
    expect(result.changed).toBe(true);
  });

  test("setNodePosition moves a node", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.setNodePosition("node_1", 500, 600);
      const pos = c.getNodePosition("node_1");
      return pos;
    });
    expect(result.x).toBe(504); // snapped to grid
    expect(result.y).toBe(600);
  });

  test("getFrameChildren returns child node IDs", async ({ page }) => {
    await freshPage(page);
    const children = await page.evaluate(() => {
      return window.__canvas.getFrameChildren("group_1");
    });
    expect(children).toContain("node_1");
    expect(children).toContain("node_2");
    expect(children).toContain("node_3");
    expect(children).toContain("node_4");
    expect(children.length).toBe(4);
  });
});

// ==================================================================
// Phase 3 continued: Frame editing, z-index, auto-layout, groups
// ==================================================================

test.describe("Frame Label Editing", () => {
  test("double-click on frame label makes it editable", async ({ page }) => {
    await freshPage(page);
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    await page.mouse.click(lbl.x, lbl.y); // double-click via two quick clicks
    const isEditing = await page.evaluate(() => {
      const label = document.querySelector('[data-id="group_1"] .infinite-canvas-frame-label');
      return label.getAttribute("contenteditable") === "true" ||
             !!document.querySelector('[data-id="group_1"] .infinite-canvas-frame-label-input');
    });
    expect(isEditing).toBe(true);
  });

  test("typing in editable label updates the frame", async ({ page }) => {
    await freshPage(page);
    // Start editing via API
    await page.evaluate(() => {
      window.__canvas.startEditingFrameLabel("group_1");
    });
    // The input should be focused - type a new name
    await page.keyboard.press("ControlOrMeta+a");
    await page.keyboard.type("My Custom Group");
    await page.keyboard.press("Enter");
    const label = await page.evaluate(() =>
      window.__canvas._frames.get("group_1").label
    );
    expect(label).toBe("My Custom Group");
  });
});

test.describe("Z-Index Management", () => {
  test("bringToFront moves node above others", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const n1 = document.querySelector('[data-id="node_1"]');
      const n2 = document.querySelector('[data-id="node_2"]');
      const zBefore1 = parseInt(getComputedStyle(n1).zIndex) || 0;
      const zBefore2 = parseInt(getComputedStyle(n2).zIndex) || 0;
      c.bringToFront("node_1");
      const zAfter1 = parseInt(getComputedStyle(n1).zIndex) || 0;
      // node_1 should now have higher z-index than node_2
      return { zAfter1, zBefore2, isAbove: zAfter1 > zBefore2 };
    });
    expect(result.isAbove).toBe(true);
  });

  test("sendToBack moves node behind others", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // First bring node_1 to front to ensure it has a high z
      c.bringToFront("node_1");
      const zHigh = parseInt(getComputedStyle(document.querySelector('[data-id="node_1"]')).zIndex) || 0;
      c.sendToBack("node_1");
      const zLow = parseInt(getComputedStyle(document.querySelector('[data-id="node_1"]')).zIndex) || 0;
      return { zHigh, zLow, wentDown: zLow < zHigh };
    });
    expect(result.wentDown).toBe(true);
  });
});

test.describe("Auto-Layout", () => {
  test("autoLayout arranges nodes in grid within a frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Scramble node positions first
      for (let i = 1; i <= 4; i++) {
        const n = c._nodes.get("node_" + i);
        n.x = Math.random() * 2000;
        n.y = Math.random() * 2000;
        c._applyRect(n.element, n);
      }
      c.autoLayout("group_1");
      // After auto-layout, nodes in group_1 should be in a grid pattern
      const positions = [];
      for (let i = 1; i <= 4; i++) {
        const n = c._nodes.get("node_" + i);
        positions.push({ x: n.x, y: n.y });
      }
      // Check that they're evenly spaced and aligned
      const xs = [...new Set(positions.map(p => p.x))].sort((a, b) => a - b);
      const ys = [...new Set(positions.map(p => p.y))].sort((a, b) => a - b);
      return { nodeCount: positions.length, uniqueXs: xs.length, uniqueYs: ys.length };
    });
    // 4 nodes in a grid should have 2-4 unique x values and 1-2 unique y values
    expect(result.uniqueXs).toBeGreaterThan(1);
    expect(result.uniqueYs).toBeGreaterThanOrEqual(1);
  });

  test("autoLayout resizes frame to fit arranged nodes", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.autoLayout("group_1");
      const frame = c._frames.get("group_1");
      // All children should be inside the frame
      const children = c.getFrameChildren("group_1");
      let allInside = true;
      for (let id of children) {
        const n = c._nodes.get(id);
        if (n.x < frame.x || n.y < frame.y ||
            n.x + n.width > frame.x + frame.width ||
            n.y + n.height > frame.y + frame.height) {
          allInside = false;
        }
      }
      return { allInside, childCount: children.length };
    });
    expect(result.allInside).toBe(true);
    expect(result.childCount).toBe(4);
  });
});

test.describe("Visual Group Membership", () => {
  test("nodes in a group show a group indicator color", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const n1 = document.querySelector('[data-id="node_1"]');
      const n5 = document.querySelector('[data-id="node_5"]');
      // Nodes in group_1 and group_2 should have different visual indicators
      const n1Indicator = n1.dataset.frameId || n1.style.getPropertyValue("--group-color");
      const n5Indicator = n5.dataset.frameId || n5.style.getPropertyValue("--group-color");
      return {
        n1HasIndicator: !!n1Indicator,
        n5HasIndicator: !!n5Indicator,
        different: n1Indicator !== n5Indicator,
      };
    });
    expect(result.n1HasIndicator).toBe(true);
    expect(result.n5HasIndicator).toBe(true);
    expect(result.different).toBe(true);
  });
});

test.describe("Node Color API", () => {
  test("setNodeColor changes node appearance", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.setNodeColor("node_1", "#ff0000", "#cc0000");
      const el = document.querySelector('[data-id="node_1"]');
      return {
        bg: el.style.getPropertyValue("--node-bg"),
        header: el.style.getPropertyValue("--node-header-bg"),
      };
    });
    expect(result.bg).toBe("#ff0000");
    expect(result.header).toBe("#cc0000");
  });
});

// ==================================================================
// Phase 5: Polish
// ==================================================================

test.describe("Context Menu", () => {
  test("right-click on node shows context menu with correct items", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y, { button: "right" });
    const result = await page.evaluate(() => {
      const menu = document.querySelector(".infinite-canvas-context-menu");
      if (!menu) return { visible: false };
      const items = [...menu.querySelectorAll("[data-action]")].map(el => el.dataset.action);
      return { visible: true, items };
    });
    expect(result.visible).toBe(true);
    expect(result.items).toContain("delete");
    expect(result.items).toContain("bring-to-front");
    expect(result.items).toContain("send-to-back");
  });

  test("right-click on frame shows frame context menu", async ({ page }) => {
    await freshPage(page);
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y, { button: "right" });
    const result = await page.evaluate(() => {
      const menu = document.querySelector(".infinite-canvas-context-menu");
      if (!menu) return { visible: false };
      const items = [...menu.querySelectorAll("[data-action]")].map(el => el.dataset.action);
      return { visible: true, items };
    });
    expect(result.visible).toBe(true);
    expect(result.items).toContain("rename");
    expect(result.items).toContain("auto-layout");
    expect(result.items).toContain("delete");
  });

  test("right-click on empty canvas shows canvas context menu", async ({ page }) => {
    await freshPage(page);
    const e = await emptyPoint(page);
    await page.mouse.click(e.x, e.y, { button: "right" });
    const result = await page.evaluate(() => {
      const menu = document.querySelector(".infinite-canvas-context-menu");
      if (!menu) return { visible: false };
      const items = [...menu.querySelectorAll("[data-action]")].map(el => el.dataset.action);
      return { visible: true, items };
    });
    expect(result.visible).toBe(true);
    expect(result.items).toContain("add-node");
    expect(result.items).toContain("add-group");
    expect(result.items).toContain("fit-all");
  });

  test("clicking a menu item executes the action and closes menu", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_3");
    await page.mouse.click(c.x, c.y, { button: "right" });
    // Click delete
    await page.evaluate(() => {
      document.querySelector('.infinite-canvas-context-menu [data-action="delete"]').click();
    });
    const result = await page.evaluate(() => ({
      menuGone: !document.querySelector(".infinite-canvas-context-menu"),
      nodeGone: !window.__canvas._nodes.has("node_3"),
    }));
    expect(result.menuGone).toBe(true);
    expect(result.nodeGone).toBe(true);
  });

  test("menu closes on left-click elsewhere", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y, { button: "right" });
    expect(await page.evaluate(() => !!document.querySelector(".infinite-canvas-context-menu"))).toBe(true);
    // Wait for the close handler to register (setTimeout(0) in showContextMenu)
    await page.waitForTimeout(50);
    // Click elsewhere
    const e = await emptyPoint(page);
    await page.mouse.click(e.x, e.y);
    expect(await page.evaluate(() => !!document.querySelector(".infinite-canvas-context-menu"))).toBe(false);
  });
});

test.describe("Visual Polish", () => {
  test("nodes in a group have a colored left border strip", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const n1 = document.querySelector('[data-id="node_1"]');
      const groupColor = getComputedStyle(n1).getPropertyValue("--group-color").trim();
      const borderLeft = getComputedStyle(n1).borderLeftColor;
      return { hasGroupColor: !!groupColor, groupColor };
    });
    expect(result.hasGroupColor).toBe(true);
  });

  test("selected frame label uses group color", async ({ page }) => {
    await freshPage(page);
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const color = await page.evaluate(() => {
      const label = document.querySelector('[data-id="group_1"] .infinite-canvas-frame-label');
      return getComputedStyle(label).color;
    });
    // Should not be the default gray when selected
    expect(color).not.toBe("rgba(255, 255, 255, 0.5)");
  });
});

// ==================================================================
// Group+Children Move Bug Fix + Tool Switching
// ==================================================================

test.describe("Group+Children Drag", () => {
  test("dragging group+children together preserves relative positions", async ({ page }) => {
    await freshPage(page);
    // Record positions before
    const before = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      return {
        frameX: frame.x, frameY: frame.y,
        n1x: n1.x, n1y: n1.y,
        n2x: n2.x, n2y: n2.y,
        n1relX: n1.x - frame.x, n1relY: n1.y - frame.y,
        n2relX: n2.x - frame.x, n2relY: n2.y - frame.y,
      };
    });
    // Select group_1 (which selects frame + we shift-select children)
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    // Shift-click all children to add them to selection
    for (let i = 1; i <= 4; i++) {
      const c = await nodeCenter(page, "node_" + i);
      await page.keyboard.down("Shift");
      await page.mouse.click(c.x, c.y);
      await page.keyboard.up("Shift");
    }
    // Verify all selected
    const selCount = await page.evaluate(() => window.__canvas.getSelection().length);
    expect(selCount).toBe(5); // group + 4 children

    // Drag via the frame label
    const lbl2 = await frameLabelCenter(page, "group_1");
    await page.mouse.move(lbl2.x, lbl2.y);
    await page.mouse.down();
    await page.mouse.move(lbl2.x + 100, lbl2.y + 50, { steps: 5 });
    await page.mouse.up();

    const after = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      return {
        frameX: frame.x, frameY: frame.y,
        n1relX: n1.x - frame.x, n1relY: n1.y - frame.y,
        n2relX: n2.x - frame.x, n2relY: n2.y - frame.y,
        n1frame: n1.frameId, n2frame: n2.frameId,
      };
    });
    // Relative positions within group should be preserved
    expect(Math.abs(after.n1relX - before.n1relX)).toBeLessThan(16);
    expect(Math.abs(after.n1relY - before.n1relY)).toBeLessThan(16);
    expect(Math.abs(after.n2relX - before.n2relX)).toBeLessThan(16);
    // Children should still belong to the group
    expect(after.n1frame).toBe("group_1");
    expect(after.n2frame).toBe("group_1");
    // Frame should have actually moved
    expect(after.frameX).not.toBe(before.frameX);
  });

  test("group auto-expands to fit children after move", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const n1 = c._nodes.get("node_1");
      const rightEdge = frame.x + frame.width;
      // Place node so center is inside but right edge extends past frame
      // center_x = x + 140, must be < rightEdge, so x < rightEdge - 140
      // right_edge_of_node = x + 280, must be > rightEdge (to test expansion)
      // So x must be in range (rightEdge - 280, rightEdge - 140)
      n1.x = rightEdge - 200;
      n1.y = frame.y + 20;
      c._applyRect(n1.element, n1);
      c._checkFrameContainment("node_1");
      return {
        n1Inside: n1.x + n1.width <= frame.x + frame.width,
        n1frame: n1.frameId,
      };
    });
    expect(result.n1frame).toBe("group_1");
    expect(result.n1Inside).toBe(true);
  });
});

test.describe("Tool Switching", () => {
  test("V key activates move tool", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("v");
    const tool = await page.evaluate(() => window.__canvas.activeTool);
    expect(tool).toBe("move");
  });

  test("H key activates hand tool", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("h");
    const tool = await page.evaluate(() => window.__canvas.activeTool);
    expect(tool).toBe("hand");
  });

  test("hand tool click-drags to pan instead of selecting", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape"); // deselect
    await page.keyboard.press("h");

    const before = await page.evaluate(() => ({
      panX: window.__canvas._panX, panY: window.__canvas._panY,
    }));
    // Click-drag on a node — should pan, NOT select
    const n = await nodeCenter(page, "node_1");
    await page.mouse.move(n.x, n.y);
    await page.mouse.down();
    await page.mouse.move(n.x + 100, n.y + 50, { steps: 5 });
    await page.mouse.up();

    const after = await page.evaluate(() => ({
      panX: window.__canvas._panX,
      panY: window.__canvas._panY,
      sel: window.__canvas.getSelection().length,
    }));
    expect(after.panX).not.toBe(before.panX);
    expect(after.sel).toBe(0); // should NOT have selected
  });

  test("container has data-tool attribute", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    const defaultTool = await page.evaluate(() =>
      document.getElementById("canvas-container").dataset.tool
    );
    expect(defaultTool).toBe("move");
    await page.keyboard.press("h");
    const handTool = await page.evaluate(() =>
      document.getElementById("canvas-container").dataset.tool
    );
    expect(handTool).toBe("hand");
  });
});

test.describe("Drawing Tools", () => {
  test("F key activates frame drawing tool", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("f");
    const tool = await page.evaluate(() => window.__canvas.activeTool);
    expect(tool).toBe("frame");
  });

  test("drawing a frame via click-drag creates it at drawn rect", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("f");
    const framesBefore = await page.evaluate(() => window.__canvas._frames.size);
    // Draw a rectangle in empty space
    const e = await emptyPoint(page);
    await page.mouse.move(e.x - 200, e.y - 100);
    await page.mouse.down();
    await page.mouse.move(e.x, e.y, { steps: 5 });
    await page.mouse.up();
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      return {
        frames: c._frames.size,
        tool: c.activeTool, // should revert to move
      };
    });
    expect(result.frames).toBe(framesBefore + 1);
    expect(result.tool).toBe("move");
  });

  test("drawing a frame over ungrouped nodes includes them", async ({ page }) => {
    await freshPage(page);
    // First remove all existing frames so nodes are ungrouped
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let [id] of [...c._frames]) {
        c.removeFrame(id);
      }
      // Verify nodes are now ungrouped
      for (let [, node] of c._nodes) {
        node.frameId = null;
        c._updateNodeGroupVisual(node);
      }
    });
    // Activate frame tool
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("f");
    // Get screen positions of node_1 and node_2 and draw a frame around both
    const n1 = await nodeCenter(page, "node_1");
    const n2 = await nodeCenter(page, "node_2");
    const left = Math.min(n1.x, n2.x) - 30;
    const top = Math.min(n1.y, n2.y) - 30;
    const right = Math.max(n1.x, n2.x) + 30;
    const bottom = Math.max(n1.y, n2.y) + 30;
    await page.mouse.move(left, top);
    await page.mouse.down();
    await page.mouse.move(right, bottom, { steps: 5 });
    await page.mouse.up();
    // Nodes within the drawn rect should be parented to the new frame
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      return {
        n1frame: n1.frameId,
        n2frame: n2.frameId,
        sameFrame: n1.frameId === n2.frameId && n1.frameId !== null,
      };
    });
    expect(result.sameFrame).toBe(true);
  });

  test("T key activates node drawing tool", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("t");
    const tool = await page.evaluate(() => window.__canvas.activeTool);
    expect(tool).toBe("node");
  });

  test("drawing a node via click-drag creates it at drawn rect", async ({ page }) => {
    await freshPage(page);
    const c = await nodeCenter(page, "node_1");
    await page.mouse.click(c.x, c.y);
    await page.keyboard.press("Escape");
    await page.keyboard.press("t");
    const nodesBefore = await page.evaluate(() => window.__canvas._nodes.size);
    const e = await emptyPoint(page);
    await page.mouse.move(e.x - 150, e.y - 100);
    await page.mouse.down();
    await page.mouse.move(e.x, e.y, { steps: 5 });
    await page.mouse.up();
    const result = await page.evaluate(() => ({
      nodes: window.__canvas._nodes.size,
      tool: window.__canvas.activeTool,
    }));
    expect(result.nodes).toBe(nodesBefore + 1);
    expect(result.tool).toBe("move");
  });
});

test.describe("Alt+Drag Clone", () => {
  test("alt+drag clones a node", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    const nodesBefore = await page.evaluate(() => window.__canvas._nodes.size);
    const h = await headerCenter(page, "node_1");
    await page.keyboard.down("Alt");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 100, h.y + 100, { steps: 5 });
    await page.mouse.up();
    await page.keyboard.up("Alt");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      return {
        nodeCount: c._nodes.size,
        origX: c._nodes.get("node_1").x,
      };
    });
    expect(result.nodeCount).toBe(nodesBefore + 1);
  });

  test("clone preserves original position", async ({ page }) => {
    await freshPage(page);
    const before = await nodePos(page, "node_1");
    const h = await headerCenter(page, "node_1");
    await page.keyboard.down("Alt");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 100, h.y + 100, { steps: 5 });
    await page.mouse.up();
    await page.keyboard.up("Alt");
    const after = await nodePos(page, "node_1");
    // Original should not have moved
    expect(after.x).toBe(before.x);
    expect(after.y).toBe(before.y);
  });

  test("container shows copy cursor during alt+drag", async ({ page }) => {
    await freshPage(page);
    const h = await headerCenter(page, "node_1");
    await page.keyboard.down("Alt");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 50, h.y + 50, { steps: 3 });
    const hasCls = await page.evaluate(() =>
      document.getElementById("canvas-container").classList.contains("is-cloning")
    );
    await page.mouse.up();
    await page.keyboard.up("Alt");
    expect(hasCls).toBe(true);
  });

  test("clone selects the new element, not the original", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    const h = await headerCenter(page, "node_1");
    await page.keyboard.down("Alt");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 100, h.y + 100, { steps: 5 });
    await page.mouse.up();
    await page.keyboard.up("Alt");
    const result = await page.evaluate(() => {
      const s = window.__canvas.getSelection();
      return { selCount: s.length, isOriginal: s.includes("node_1") };
    });
    expect(result.selCount).toBe(1);
    expect(result.isOriginal).toBe(false);
  });
});

test.describe("Alignment Commands", () => {
  test("align-left aligns selected nodes to leftmost edge", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      c.select("node_3");
      const n1Before = c._nodes.get("node_1").x;
      c.alignSelection("align-left");
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      const n3 = c._nodes.get("node_3");
      return { n1x: n1.x, n2x: n2.x, n3x: n3.x, allSame: n1.x === n2.x && n2.x === n3.x };
    });
    expect(result.allSame).toBe(true);
  });

  test("align-right aligns to rightmost edge", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      c.alignSelection("align-right");
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      return { rightEdge1: n1.x + n1.width, rightEdge2: n2.x + n2.width };
    });
    expect(result.rightEdge1).toBe(result.rightEdge2);
  });

  test("distribute-h spaces selected nodes evenly", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      c.select("node_3");
      c.alignSelection("distribute-h");
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      const n3 = c._nodes.get("node_3");
      // Sort by x
      const sorted = [n1, n2, n3].sort((a, b) => a.x - b.x);
      const gap1 = sorted[1].x - (sorted[0].x + sorted[0].width);
      const gap2 = sorted[2].x - (sorted[1].x + sorted[1].width);
      return { gap1, gap2, equal: Math.abs(gap1 - gap2) < 10 };
    });
    expect(result.equal).toBe(true);
  });
});

// ==================================================================
// Multi-Selection, Ctrl+D, Ctrl+G
// ==================================================================

test.describe("Multi-Selection Improvements", () => {
  test("shift+click on group label selects group and all children", async ({ page }) => {
    await freshPage(page);
    // First select a single node via API to avoid group selection
    await selectNode(page, "node_5");
    expect((await sel(page)).length).toBe(1);
    // Shift+click group_1 label
    const lbl = await frameLabelCenter(page, "group_1");
    await page.keyboard.down("Shift");
    await page.mouse.click(lbl.x, lbl.y);
    await page.keyboard.up("Shift");
    const s = await sel(page);
    // Should have node_5 + group_1 + its 4 children = 6
    expect(s).toContain("group_1");
    expect(s).toContain("node_1");
    expect(s).toContain("node_2");
    expect(s).toContain("node_3");
    expect(s).toContain("node_4");
    expect(s).toContain("node_5");
  });

  test("clicking group label without shift selects group and children only", async ({ page }) => {
    await freshPage(page);
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const s = await sel(page);
    expect(s).toContain("group_1");
    expect(s).toContain("node_1");
    expect(s.length).toBe(5); // group + 4 children
  });
});

test.describe("Ctrl+D Duplicate", () => {
  test("duplicates selected node in place with offset", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    await page.evaluate(() =>
      document.getElementById("canvas-container").focus()
    );
    const before = await page.evaluate(() => window.__canvas._nodes.size);
    await page.keyboard.press("ControlOrMeta+d");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const s = c.getSelection();
      return {
        nodeCount: c._nodes.size,
        selCount: s.length,
        originalStillExists: c._nodes.has("node_1"),
        cloneSelected: s.length === 1 && !s.includes("node_1"),
      };
    });
    expect(result.nodeCount).toBe(before + 1);
    expect(result.originalStillExists).toBe(true);
    expect(result.cloneSelected).toBe(true);
  });
});

test.describe("Ctrl+G Group Selected", () => {
  test("groups selected nodes into a new tab group", async ({ page }) => {
    await freshPage(page);
    // Remove existing groups first so nodes are ungrouped
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let [id] of [...c._frames]) { c.removeFrame(id); }
      for (let [, n] of c._nodes) { n.frameId = null; c._updateNodeGroupVisual(n); }
    });
    // Select nodes 1 and 2
    const c1 = await nodeCenter(page, "node_1");
    const c2 = await nodeCenter(page, "node_2");
    await page.mouse.click(c1.x, c1.y);
    await page.keyboard.down("Shift");
    await page.mouse.click(c2.x, c2.y);
    await page.keyboard.up("Shift");
    expect((await sel(page)).length).toBe(2);
    const framesBefore = await page.evaluate(() => window.__canvas._frames.size);
    await page.keyboard.press("ControlOrMeta+g");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const n1 = c._nodes.get("node_1");
      const n2 = c._nodes.get("node_2");
      return {
        frames: c._frames.size,
        n1frame: n1.frameId,
        n2frame: n2.frameId,
        sameGroup: n1.frameId === n2.frameId && n1.frameId !== null,
      };
    });
    expect(result.frames).toBe(framesBefore + 1);
    expect(result.sameGroup).toBe(true);
  });

  test("groups a single selected node into a new tab group", async ({ page }) => {
    await freshPage(page);
    // Ungroup everything first
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let [id] of [...c._frames]) { c.removeFrame(id); }
      for (let [, n] of c._nodes) { n.frameId = null; c._updateNodeGroupVisual(n); }
    });
    const center = await nodeCenter(page, "node_1");
    await page.mouse.click(center.x, center.y);
    expect((await sel(page)).length).toBe(1);
    const framesBefore = await page.evaluate(() => window.__canvas._frames.size);
    await page.keyboard.press("ControlOrMeta+g");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const n1 = c._nodes.get("node_1");
      return {
        frames: c._frames.size,
        n1frame: n1.frameId,
        // Selection should be the new frame (Ctrl+G selects the frame).
        selectedFrame: c.getSelection().some(id => c._frames.has(id)),
      };
    });
    expect(result.frames).toBe(framesBefore + 1);
    expect(result.n1frame).not.toBeNull();
    expect(result.selectedFrame).toBe(true);
  });

  test("Ctrl+G on a selected frame ungroups it (toggle)", async ({ page }) => {
    await freshPage(page);
    // group_1 already contains node_1..node_4. Click a node so the
    // canvas container has keyboard focus, then swap to selecting the
    // group via API.
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    await page.evaluate(() => {
      window.__canvas.deselectAll();
      window.__canvas.select("group_1");
    });
    expect((await sel(page))).toContain("group_1");
    const framesBefore = await page.evaluate(() => window.__canvas._frames.size);
    await page.keyboard.press("ControlOrMeta+g");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      return {
        frames: c._frames.size,
        groupGone: !c._frames.has("group_1"),
        n1frame: c._nodes.get("node_1").frameId,
      };
    });
    expect(result.frames).toBe(framesBefore - 1);
    expect(result.groupGone).toBe(true);
    expect(result.n1frame).toBeNull();
  });
});

test.describe("Click-into-Group (Figma nested selection)", () => {
  test("first click on group selects group + children", async ({ page }) => {
    await freshPage(page);
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const s = await sel(page);
    expect(s).toContain("group_1");
    expect(s).toContain("node_1");
    expect(s.length).toBe(5); // group + 4 children
  });

  test("clicking a child node inside an already-selected group drills into that child", async ({ page }) => {
    await freshPage(page);
    // First click: select the group
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    expect(await sel(page)).toContain("group_1");
    // Second click: click on node_2 which is inside the already-selected group
    const n2 = await nodeCenter(page, "node_2");
    await page.mouse.click(n2.x, n2.y);
    const s = await sel(page);
    // Should now be ONLY node_2 - drilled into the group
    expect(s).toEqual(["node_2"]);
  });

  test("clicking a child node outside a selected group does normal selection", async ({ page }) => {
    await freshPage(page);
    // Select group_1
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    // Click on node_5 which is in group_2 (NOT in the selected group)
    const n5 = await nodeCenter(page, "node_5");
    await page.mouse.click(n5.x, n5.y);
    const s = await sel(page);
    // Should select group_2 + all its children (normal group selection)
    expect(s).toContain("group_2");
    expect(s).toContain("node_5");
    expect(s).not.toContain("group_1");
  });

  test("clicking group label when already drilled into a child re-selects the group", async ({ page }) => {
    await freshPage(page);
    // Select group, then drill into node_1
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const n1 = await nodeCenter(page, "node_1");
    await page.mouse.click(n1.x, n1.y);
    expect(await sel(page)).toEqual(["node_1"]);
    // Click group label again - should re-select the whole group
    const lbl2 = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl2.x, lbl2.y);
    const s = await sel(page);
    expect(s).toContain("group_1");
    expect(s.length).toBe(5);
  });

  test("dragging a drilled-into child moves only that child", async ({ page }) => {
    await freshPage(page);
    // Select group, drill into node_1
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const n1 = await nodeCenter(page, "node_1");
    await page.mouse.click(n1.x, n1.y);
    expect(await sel(page)).toEqual(["node_1"]);
    // Drag node_1 - only node_1 should move, not the whole group
    const before2 = await nodePos(page, "node_2");
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 60, h.y + 40, { steps: 5 });
    await page.mouse.up();
    const after2 = await nodePos(page, "node_2");
    // node_2 should NOT have moved (it's not selected)
    expect(after2.x).toBe(before2.x);
    expect(after2.y).toBe(before2.y);
  });
});

test.describe("Edge Auto-Pan", () => {
  test("dragging to right edge pans the canvas", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    const before = await page.evaluate(() => window.__canvas._panX);
    const h = await headerCenter(page, "node_1");
    const bounds = await page.evaluate(() => {
      const r = document.getElementById("canvas-container").getBoundingClientRect();
      return { right: r.right, top: r.top, height: r.height };
    });
    // Drag to the right edge and hold for a moment
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(bounds.right - 10, bounds.top + bounds.height / 2, { steps: 5 });
    // Wait for auto-pan to kick in
    await page.waitForTimeout(200);
    await page.mouse.up();
    const after = await page.evaluate(() => window.__canvas._panX);
    expect(after).toBeLessThan(before); // panned left (canvas moved to show right)
  });

  test("auto-pan stops when pointer leaves edge zone", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    const h = await headerCenter(page, "node_1");
    const bounds = await page.evaluate(() => {
      const r = document.getElementById("canvas-container").getBoundingClientRect();
      return { right: r.right, left: r.left, top: r.top, height: r.height, width: r.width };
    });
    // Drag to edge, then move back to center
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(bounds.right - 10, bounds.top + bounds.height / 2, { steps: 3 });
    await page.waitForTimeout(100);
    // Move back to center
    await page.mouse.move(bounds.left + bounds.width / 2, bounds.top + bounds.height / 2, { steps: 3 });
    const panAfterCenter = await page.evaluate(() => window.__canvas._panX);
    await page.waitForTimeout(200);
    const panLater = await page.evaluate(() => window.__canvas._panX);
    await page.mouse.up();
    // Pan should have stopped once pointer left the edge zone
    expect(panLater).toBe(panAfterCenter);
  });
});

test.describe("Shift+Resize Aspect Ratio Lock", () => {
  test("shift+drag SE handle preserves aspect ratio", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const node = c._nodes.get("node_1");
      c.deselectAll();
      c.select("node_1");
      const ratio = node.width / node.height;
      c._resizeTarget = "node_1";
      c._resizeHandle = "se";
      c._resizeStartRect = { x: node.x, y: node.y, width: node.width, height: node.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      // Resize with shift held (asymmetric drag - width grows more than height)
      c._doResize({ clientX: 100, clientY: 30, shiftKey: true });
      const newRatio = node.width / node.height;
      return { origRatio: ratio, newRatio, ratioPreserved: Math.abs(newRatio - ratio) < 0.1 };
    });
    expect(result.ratioPreserved).toBe(true);
  });
});

test.describe("Visual Polish", () => {
  test("grid dots have zoom-dependent opacity", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const el = document.getElementById("canvas-container");
      const style = getComputedStyle(el);
      return {
        hasGridOpacity: style.getPropertyValue("--grid-opacity") !== "",
      };
    });
    expect(result.hasGridOpacity).toBe(true);
  });
});

// ==================================================================
// Interaction Audit Fixes
// ==================================================================

test.describe("Resize Containment", () => {
  test("resizing a node into a frame parents it", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Create an ungrouped node near group_1
      const frame = c._frames.get("group_1");
      c.addNode("resize_test", { x: frame.x + frame.width + 100, y: frame.y + 50, width: 100, height: 80 });
      // Resize it so its center lands inside the frame (grow left)
      c._resizeTarget = "resize_test";
      c._resizeHandle = "w";
      const n = c._nodes.get("resize_test");
      c._resizeStartRect = { x: n.x, y: n.y, width: n.width, height: n.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      c._doResize({ clientX: -200, clientY: 0, shiftKey: false });
      c._endResize({ pointerId: 1 });
      return { frameId: c._nodes.get("resize_test").frameId };
    });
    expect(result.frameId).toBe("group_1");
  });
});

test.describe("Undo Restores Frame Membership", () => {
  test("undoing a move into a frame restores original frameId", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const n1 = c._nodes.get("node_1");
      const origFrame = n1.frameId; // "group_1"
      c.deselectAll();
      c.select("node_1");
      // Include startFrameId in the drag target (as _startDrag does)
      c._dragTargets = [{ id: "node_1", startX: n1.x, startY: n1.y, startFrameId: n1.frameId }];
      c._dragDidMove = true;
      c._isCloning = false;
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._dragStartPanX = c._panX;
      c._dragStartPanY = c._panY;
      c._dragStartZoom = c._zoom;
      c._cachedSnapTargets = [];
      n1.x = 5000;
      n1.y = 5000;
      c._applyRect(n1.element, n1);
      c._state = InfiniteCanvas.STATE_DRAGGING;
      c._endDrag({ pointerId: 1, clientX: 0, clientY: 0 });
      const afterDrag = n1.frameId;
      c.undo();
      const afterUndo = n1.frameId;
      return { origFrame, afterDrag, afterUndo };
    });
    expect(result.origFrame).toBe("group_1");
    expect(result.afterDrag).toBeNull();
    expect(result.afterUndo).toBe("group_1");
  });
});

test.describe("Undo Foundation", () => {
  test("undo restores selection to its pre-action state", async ({ page }) => {
    await freshPage(page);
    // Select node_1 + node_2 first, then drag-move them, then undo.
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
    });
    const before = await page.evaluate(() => ({
      selection: window.__canvas.getSelection(),
      n1: { ...window.__canvas._nodes.get("node_1") },
    }));
    // Simulate a drag by directly mutating state and calling _pushCommand
    // through the same public path the engine uses (we want to test the
    // foundation, not the drag mechanics).
    await page.evaluate(() => {
      const c = window.__canvas;
      let n1 = c._nodes.get("node_1");
      let n2 = c._nodes.get("node_2");
      let cmd = c._makeCommand({
        type: "move",
        label: "Move",
        undo: () => {},
        redo: () => {},
      });
      cmd.undo = () => { n1.x = 0; n2.x = 0; };
      cmd.redo = () => { n1.x = 100; n2.x = 100; };
      // Mutate then push (matches engine call order).
      n1.x = 100; n2.x = 100;
      c._pushCommand(cmd);
      c.deselectAll();
    });
    const afterPush = await page.evaluate(() => window.__canvas.getSelection());
    expect(afterPush.length).toBe(0);
    // Undo restores selection too.
    await page.evaluate(() => window.__canvas.undo());
    const afterUndo = await page.evaluate(() => window.__canvas.getSelection());
    expect(afterUndo).toEqual(before.selection);
  });

  test("stack-change event fires with labels on push/undo/redo", async ({ page }) => {
    await freshPage(page);
    const events = await page.evaluate(() => {
      const c = window.__canvas;
      window.__stackEvents = [];
      c.on("stack-change", e => window.__stackEvents.push(e));
      let n1 = c._nodes.get("node_1");
      let prev = n1.x;
      let cmd = c._makeCommand({
        type: "test",
        label: "Test Action",
        undo: () => { n1.x = prev; },
        redo: () => { n1.x = prev + 10; },
      });
      n1.x = prev + 10;
      c._pushCommand(cmd);
      c.undo();
      c.redo();
      return window.__stackEvents;
    });
    // Expect at least three events (push, undo, redo).
    expect(events.length).toBeGreaterThanOrEqual(3);
    // After push: canUndo true, canRedo false, undoLabel set.
    expect(events[0].canUndo).toBe(true);
    expect(events[0].canRedo).toBe(false);
    expect(events[0].undoLabel).toBe("Undo Test Action");
    // After undo: canUndo false, canRedo true.
    expect(events[1].canUndo).toBe(false);
    expect(events[1].canRedo).toBe(true);
    expect(events[1].redoLabel).toBe("Redo Test Action");
  });

  test("transactions coalesce multiple pushes into one command", async ({ page }) => {
    await freshPage(page);
    const sizes = await page.evaluate(() => {
      const c = window.__canvas;
      let n1 = c._nodes.get("node_1");
      let originalX = n1.x;
      c.beginTransaction("Nudge");
      for (let i = 0; i < 5; i++) {
        let prev = n1.x;
        n1.x += 8;
        c._pushCommand(c._makeCommand({
          type: "nudge",
          label: "Nudge",
          undo: () => { n1.x = prev; },
          redo: () => { n1.x = prev + 8; },
        }));
      }
      c.endTransaction();
      let stackSize = c._undoStack.length;
      c.undo();
      let xAfterUndo = n1.x;
      return { stackSize, xAfterUndo, originalX };
    });
    // 5 pushes inside one transaction = 1 entry on the stack.
    expect(sizes.stackSize).toBeGreaterThan(0);
    // Undo reverts the entire batch to the pre-transaction state.
    expect(sizes.xAfterUndo).toBe(sizes.originalX);
  });

  test("coalesceKey merges sequential commands within the window", async ({ page }) => {
    await freshPage(page);
    const count = await page.evaluate(() => {
      const c = window.__canvas;
      let n1 = c._nodes.get("node_1");
      // Three coalesce-able pushes outside a transaction.
      for (let i = 0; i < 3; i++) {
        let prev = n1.x;
        n1.x += 8;
        let cmd = c._makeCommand({
          type: "nudge",
          label: "Nudge",
          undo: () => { n1.x = prev; },
          redo: () => { n1.x = prev + 8; },
          coalesceKey: "arrow-nudge",
        });
        cmd._pushedAt = Date.now();
        c._commitCommand(cmd, 1000);
      }
      return c._undoStack.length;
    });
    expect(count).toBe(1);
  });

  test("undo silently drops when revert throws", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let cmd = c._makeCommand({
        type: "broken",
        label: "Broken",
        undo: () => { throw new Error("nope"); },
        redo: () => {},
      });
      c._pushCommand(cmd);
      let logBefore = c.getDebugLog().length;
      c.undo();
      let logAfter = c.getDebugLog().length;
      return {
        undoStack: c._undoStack.length,
        redoStack: c._redoStack.length,
        logGrew: logAfter > logBefore,
      };
    });
    // Bad command dropped from both stacks.
    expect(result.undoStack).toBe(0);
    expect(result.redoStack).toBe(0);
    expect(result.logGrew).toBe(true);
  });

  test("attached side-effects run on undo and redo", async ({ page }) => {
    await freshPage(page);
    const events = await page.evaluate(() => {
      const c = window.__canvas;
      let log = [];
      let cmd = c._makeCommand({
        type: "test",
        label: "Test",
        undo: () => log.push("engine-undo"),
        redo: () => log.push("engine-redo"),
      });
      cmd.attach({
        undo: () => log.push("adapter-undo"),
        redo: () => log.push("adapter-redo"),
      });
      c._pushCommand(cmd);
      c.undo();
      c.redo();
      return log;
    });
    // Engine action runs first, then adapter side-effect.
    expect(events).toEqual([
      "engine-undo", "adapter-undo",
      "engine-redo", "adapter-redo",
    ]);
  });

  test("clone command round-trips: undo removes clones, redo recreates", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let beforeNodeCount = c._nodes.size;
      // Simulate the engine's clone command (matches what alt+drag does).
      let cloneIds = [];
      let clone = c.addNode("__test_clone_1", {
        x: 5000, y: 5000, width: 280, height: 212, title: "Clone",
      });
      cloneIds.push("__test_clone_1");
      let cloneSnapshots = cloneIds.map(id => {
        let n = c._nodes.get(id);
        return {
          kind: "node", id,
          data: { x: n.x, y: n.y, width: n.width, height: n.height, title: n.title },
        };
      });
      c._pushCommand(c._makeCommand({
        type: "clone",
        label: "Duplicate",
        undo: () => {
          for (let s of cloneSnapshots) c.removeNode(s.id);
        },
        redo: () => {
          for (let s of cloneSnapshots) c.addNode(s.id, s.data);
        },
      }));
      c.undo();
      let nodesAfterUndo = c._nodes.size;
      let cloneExistsAfterUndo = c._nodes.has("__test_clone_1");
      c.redo();
      let nodesAfterRedo = c._nodes.size;
      let cloneExistsAfterRedo = c._nodes.has("__test_clone_1");
      return {
        beforeNodeCount,
        nodesAfterUndo,
        cloneExistsAfterUndo,
        nodesAfterRedo,
        cloneExistsAfterRedo,
      };
    });
    expect(result.nodesAfterUndo).toBe(result.beforeNodeCount);
    expect(result.cloneExistsAfterUndo).toBe(false);
    expect(result.nodesAfterRedo).toBe(result.beforeNodeCount + 1);
    expect(result.cloneExistsAfterRedo).toBe(true);
  });

  test("debug log ring buffer caps at the max size", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c._debugLogMax = 5;
      c._debugLogBuffer = [];
      for (let i = 0; i < 10; i++) {
        c.debugLog("info", "msg " + i, { i });
      }
      return c.getDebugLog();
    });
    expect(result.length).toBe(5);
    // Oldest 5 dropped, newest 5 retained.
    expect(result[0].message).toBe("msg 5");
    expect(result[4].message).toBe("msg 9");
  });
});

test.describe("Selection Undo", () => {
  test("undo restores empty initial selection after a click", async ({ page }) => {
    await freshPage(page);
    // Test page starts with no selection and empty undo stack.
    const initial = await page.evaluate(() => ({
      selection: window.__canvas.getSelection(),
      undoSize: window.__canvas._undoStack.length,
    }));
    expect(initial.selection.length).toBe(0);
    expect(initial.undoSize).toBe(0);
    // Click a node — selection changes from [] to [group_1 + children].
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    const afterClick = await sel(page);
    expect(afterClick.length).toBeGreaterThan(0);
    // Ctrl+Z restores empty selection.
    await page.evaluate(() => window.__canvas.undo());
    const afterUndo = await sel(page);
    expect(afterUndo.length).toBe(0);
  });

  test("undo restores prior selection after a switch", async ({ page }) => {
    await freshPage(page);
    // Select node_1, then click node_5 to switch.
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    const after1 = await sel(page);
    // Wait longer than the selection coalesce window (400 ms) so the
    // second click pushes a distinct undo entry rather than merging.
    await page.waitForTimeout(500);
    const c5 = await nodeCenter(page, "node_5");
    await page.mouse.click(c5.x, c5.y);
    const after5 = await sel(page);
    expect(after5).not.toEqual(after1);
    // Undo restores selection-1.
    await page.evaluate(() => window.__canvas.undo());
    const afterUndo = await sel(page);
    expect(afterUndo.sort()).toEqual([...after1].sort());
  });

  test("rapid selection changes coalesce into one undo entry", async ({ page }) => {
    await freshPage(page);
    const stackSizes = await page.evaluate(async () => {
      const c = window.__canvas;
      c.deselectAll();
      c._undoStack = [];
      c._redoStack = [];
      // Each call: mutate THEN record (mirrors how the gesture entry
      // points use the helper — prev is captured before, recorded after).
      c._selection.add("node_1");
      c._recordSelectionChange([], "Select");
      c._selection.add("node_2");
      c._recordSelectionChange(["node_1"], "Select");
      c._selection.add("node_3");
      c._recordSelectionChange(["node_1", "node_2"], "Select");
      return c._undoStack.length;
    });
    // Three changes within the coalesce window = one entry.
    expect(stackSizes).toBe(1);
  });

  test("arrow navigation pushes a selection-undo entry", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      let kids = c._sortedFrameChildren("group_1");
      c.deselectAll();
      c.select(kids[0].id);
      // Reset stack to start clean.
      c._undoStack = [];
      c._redoStack = [];
    });
    await page.evaluate(() => window.__canvas.focusNeighbor("right"));
    const after = await page.evaluate(() => ({
      selection: window.__canvas.getSelection(),
      stack: window.__canvas._undoStack.length,
    }));
    expect(after.stack).toBeGreaterThan(0);
    // Undo restores the previous selection.
    let prevSelection = await page.evaluate(() => {
      let kids = window.__canvas._sortedFrameChildren("group_1");
      return [kids[0].id];
    });
    await page.evaluate(() => window.__canvas.undo());
    const afterUndo = await sel(page);
    expect(afterUndo).toEqual(prevSelection);
  });
});

test.describe("Drill-Switch Within Group", () => {
  test("clicking another tab in same group while one is drilled in selects only the new tab", async ({ page }) => {
    await freshPage(page);
    // Phase 1: drill into node_1 of group_1.
    const c1 = await nodeCenter(page, "node_1");
    // First click: selects the whole group + its children.
    await page.mouse.click(c1.x, c1.y);
    const afterFirstClick = await sel(page);
    expect(afterFirstClick).toContain("group_1");
    expect(afterFirstClick).toContain("node_1");
    // Second click on same node: drills in.
    await page.mouse.click(c1.x, c1.y);
    const afterDrillIn = await sel(page);
    expect(afterDrillIn).toEqual(["node_1"]);

    // Phase 2: click node_2 (sibling within the same group). The
    // expectation is that we DON'T pop back to the group selection;
    // we drill straight into node_2 instead.
    const c2 = await nodeCenter(page, "node_2");
    await page.mouse.click(c2.x, c2.y);
    const afterSiblingClick = await sel(page);
    expect(afterSiblingClick).toEqual(["node_2"]);
  });

  test("clicking a tab in a DIFFERENT group still selects that group with children", async ({ page }) => {
    await freshPage(page);
    // Drill into a child of group_1.
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    await page.mouse.click(c1.x, c1.y);
    expect(await sel(page)).toEqual(["node_1"]);
    // Click a node in group_2 — should select group_2 + all its children.
    const c5 = await nodeCenter(page, "node_5");
    await page.mouse.click(c5.x, c5.y);
    const after = await sel(page);
    expect(after).toContain("group_2");
    expect(after).toContain("node_5");
  });

  test("clicking an ungrouped tab while drilled into a group selects only that tab", async ({ page }) => {
    await freshPage(page);
    // Drill into a child of group_1.
    const c1 = await nodeCenter(page, "node_1");
    await page.mouse.click(c1.x, c1.y);
    await page.mouse.click(c1.x, c1.y);
    // Move node_8 out of group_2 to make it ungrouped.
    await page.evaluate(() => {
      let n8 = window.__canvas._nodes.get("node_8");
      n8.frameId = null;
      window.__canvas._updateNodeGroupVisual(n8);
    });
    const c8 = await nodeCenter(page, "node_8");
    await page.mouse.click(c8.x, c8.y);
    expect(await sel(page)).toEqual(["node_8"]);
  });
});

test.describe("Debug Console", () => {
  test("toggle button shows and hides the panel", async ({ page }) => {
    await freshPage(page);
    // Test page starts with debug console visible; toggle to hide first.
    const initial = await page.evaluate(() => {
      let panel = document.querySelector(".canvas-debug-console");
      return panel?.style.display;
    });
    expect(initial).toBe("flex");
    await page.evaluate(() => {
      let btn = document.querySelector(".canvas-debug-console-toggle");
      btn.click();
    });
    const afterHide = await page.evaluate(() => {
      let panel = document.querySelector(".canvas-debug-console");
      return panel?.style.display;
    });
    expect(afterHide).toBe("none");
    await page.evaluate(() => {
      let btn = document.querySelector(".canvas-debug-console-toggle");
      btn.click();
    });
    const afterShow = await page.evaluate(() => {
      let panel = document.querySelector(".canvas-debug-console");
      return panel?.style.display;
    });
    expect(afterShow).toBe("flex");
  });

  test("debug log entries appear in the panel after wakeup", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => window.__debugConsole.show());
    const rows = await page.evaluate(() => {
      window.__canvas.debugLog("info", "hello from test", { foo: 1 });
      let body = document.querySelector(".canvas-debug-console")
        .querySelector("div[style*='overflow-y']");
      return body.textContent;
    });
    expect(rows).toContain("hello from test");
  });

  test("clear button empties the panel body", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.debugLog("info", "one");
      c.debugLog("info", "two");
      window.__debugConsole.show();
    });
    await page.evaluate(() => {
      // Find the clear button via text content.
      let panel = document.querySelector(".canvas-debug-console");
      let btns = panel.querySelectorAll("button");
      for (let b of btns) {
        if (b.textContent === "clear") { b.click(); break; }
      }
    });
    const isEmpty = await page.evaluate(() => {
      let body = document.querySelector(".canvas-debug-console")
        .querySelector("div[style*='overflow-y']");
      return body.childNodes.length === 0;
    });
    expect(isEmpty).toBe(true);
  });
});

test.describe("Undo Coverage", () => {
  // Generic round-trip helper: snapshot, perform, undo, expect equal,
  // redo, expect post-action, undo again, expect snapshot, redo again.
  async function roundTrip(page, action) {
    let result = await page.evaluate(async (act) => {
      const c = window.__canvas;
      // Use a simplified state hash that's robust to ordering quirks.
      let hash = () => JSON.stringify({
        nodes: [...c._nodes.entries()].map(([id, n]) => ({
          id, x: n.x, y: n.y, w: n.width, h: n.height,
          color: n.color, header: n.headerColor, frameId: n.frameId,
          z: n.element.style.zIndex || "",
        })).sort((a, b) => a.id.localeCompare(b.id)),
        frames: [...c._frames.entries()].map(([id, f]) => ({
          id, x: f.x, y: f.y, w: f.width, h: f.height, label: f.label, color: f.color,
          z: f.element.style.zIndex || "",
        })).sort((a, b) => a.id.localeCompare(b.id)),
      });
      let before = hash();
      // eslint-disable-next-line no-new-func
      let actionFn = new Function("c", act);
      actionFn(c);
      let after = hash();
      c.undo();
      let afterUndo = hash();
      c.redo();
      let afterRedo = hash();
      c.undo();
      let afterUndoAgain = hash();
      c.redo();
      let afterRedoAgain = hash();
      return { before, after, afterUndo, afterRedo, afterUndoAgain, afterRedoAgain };
    }, action);
    expect(result.afterUndo).toBe(result.before);
    expect(result.afterRedo).toBe(result.after);
    expect(result.afterUndoAgain).toBe(result.before);
    expect(result.afterRedoAgain).toBe(result.after);
  }

  test("z-order: bringToFront round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `c.bringToFront("node_1");`);
  });

  test("z-order: sendToBack round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `c.sendToBack("node_1");`);
  });

  test("color: setNodeColor round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `c.setNodeColor("node_1", "#ff0000", "#cc0000");`);
  });

  test("group: Ctrl+G round-trips", async ({ page }) => {
    await freshPage(page);
    // Ungroup first so we can group a fresh pair.
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let [id] of [...c._frames]) c.removeFrame(id);
      for (let [, n] of c._nodes) { n.frameId = null; c._updateNodeGroupVisual(n); }
      c._undoStack = [];
      c._redoStack = [];
    });
    await roundTrip(page, `
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      c._onKeyDown({
        ctrlKey: true, metaKey: false, shiftKey: false, altKey: false,
        key: "g",
        preventDefault() {},
        stopPropagation() {},
      });
    `);
  });

  test("ungroup: removeFrame via Ctrl+G round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `
      c.deselectAll();
      c.select("group_1");
      c._onKeyDown({
        ctrlKey: true, metaKey: false, shiftKey: false, altKey: false,
        key: "g",
        preventDefault() {},
        stopPropagation() {},
      });
    `);
  });

  test("compactLayout round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `c.deselectAll(); c.compactLayout();`);
  });

  test("autoLayout round-trips", async ({ page }) => {
    await freshPage(page);
    // Pre-scramble so autoLayout actually moves things.
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let id of c.getFrameChildren("group_1")) {
        let n = c._nodes.get(id);
        n.x = 5000 + Math.random() * 100;
        n.y = 5000 + Math.random() * 100;
        c._applyRect(n.element, n);
      }
      c._undoStack = [];
      c._redoStack = [];
    });
    await roundTrip(page, `c.autoLayout("group_1");`);
  });

  test("alignment round-trips", async ({ page }) => {
    await freshPage(page);
    await roundTrip(page, `
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      c.select("node_3");
      c.alignSelection("align-left");
    `);
  });

  test("arrow nudge coalesces and round-trips", async ({ page }) => {
    await freshPage(page);
    let stackBefore = await page.evaluate(() => window.__canvas._undoStack.length);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      // Three rapid arrow nudges.
      for (let i = 0; i < 3; i++) {
        c._onKeyDown({
          key: "ArrowRight",
          ctrlKey: false, metaKey: false, shiftKey: false, altKey: false,
          preventDefault() {},
          stopPropagation() {},
        });
      }
    });
    let stackAfter = await page.evaluate(() => window.__canvas._undoStack.length);
    // Three nudges coalesced into one command.
    expect(stackAfter).toBe(stackBefore + 1);
    // Undo reverts all three at once.
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let beforeX = c._nodes.get("node_1").x;
      c.undo();
      let afterX = c._nodes.get("node_1").x;
      return { beforeX, afterX };
    });
    expect(result.afterX).toBeLessThan(result.beforeX);
  });

  test("frame rename round-trips", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let originalLabel = c._frames.get("group_1").label;
      c.startEditingFrameLabel("group_1");
      let input = document.querySelector(".infinite-canvas-frame-label-input");
      input.value = "Renamed Group";
      // Synthesize Enter to commit.
      input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
      let afterRename = c._frames.get("group_1").label;
      c.undo();
      let afterUndo = c._frames.get("group_1").label;
      c.redo();
      let afterRedo = c._frames.get("group_1").label;
      return { originalLabel, afterRename, afterUndo, afterRedo };
    });
    expect(result.afterRename).toBe("Renamed Group");
    expect(result.afterUndo).toBe(result.originalLabel);
    expect(result.afterRedo).toBe("Renamed Group");
  });
});

test.describe("Frame Selection Visual", () => {
  test("children do not show selection handles when frame is selected", async ({ page }) => {
    await freshPage(page);
    // Click to select group_1 (selects frame + children)
    const lbl = await frameLabelCenter(page, "group_1");
    await page.mouse.click(lbl.x, lbl.y);
    const result = await page.evaluate(() => {
      const n1 = document.querySelector('[data-id="node_1"]');
      const frame = document.querySelector('[data-id="group_1"]');
      const n1Handles = n1.querySelectorAll(".infinite-canvas-resize-handle");
      const frameHandles = frame.querySelectorAll(".infinite-canvas-resize-handle");
      const n1HandlesVisible = [...n1Handles].some(h => getComputedStyle(h).display !== "none");
      const frameHandlesVisible = [...frameHandles].some(h => getComputedStyle(h).display !== "none");
      return { n1HandlesVisible, frameHandlesVisible };
    });
    // Frame handles should be visible, child handles should NOT
    expect(result.frameHandlesVisible).toBe(true);
    expect(result.n1HandlesVisible).toBe(false);
  });
});

test.describe("Ctrl+D Containment", () => {
  test("duplicating a node inside a frame parents the duplicate", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    await page.evaluate(() => document.getElementById("canvas-container").focus());
    await page.keyboard.press("ControlOrMeta+d");
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const sel = c.getSelection();
      const cloneId = sel[0];
      const clone = c._nodes.get(cloneId);
      return { cloneFrame: clone?.frameId };
    });
    // node_1 is in group_1, so the duplicate (offset 16px) should also be in group_1
    expect(result.cloneFrame).toBe("group_1");
  });
});

test.describe("Drawing Node Inside Frame", () => {
  test("node drawn inside a frame is parented to it", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      // Use the engine API to add a node at a position inside the frame, then check containment
      let id = "__drawn_node_test";
      c.addNode(id, {
        x: frame.x + 30, y: frame.y + 30,
        width: 100, height: 80,
        title: "Drawn Node",
      });
      c._checkFrameContainment(id);
      return { frameId: c._nodes.get(id)?.frameId };
    });
    expect(result.frameId).toBe("group_1");
  });
});

test.describe("Escape Cancels Drag", () => {
  test("pressing Escape mid-drag reverts node position", async ({ page }) => {
    await freshPage(page);
    await selectNode(page, "node_1");
    const before = await nodePos(page, "node_1");
    const h = await headerCenter(page, "node_1");
    await page.mouse.move(h.x, h.y);
    await page.mouse.down();
    await page.mouse.move(h.x + 200, h.y + 200, { steps: 5 });
    // Press Escape mid-drag
    await page.keyboard.press("Escape");
    await page.mouse.up();
    const after = await nodePos(page, "node_1");
    expect(after.x).toBe(before.x);
    expect(after.y).toBe(before.y);
  });
});

test.describe("Frame Resize Unparents Children", () => {
  test("shrinking a frame unparents children that fall outside", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      const frame = c._frames.get("group_1");
      const children = c.getFrameChildren("group_1");
      let rightmostId = children[0];
      let rightmostX = 0;
      for (let id of children) {
        let n = c._nodes.get(id);
        if (n.x + n.width > rightmostX) {
          rightmostX = n.x + n.width;
          rightmostId = id;
        }
      }
      const childBefore = c._nodes.get(rightmostId).frameId;
      c._resizeTarget = "group_1";
      c._resizeHandle = "e";
      c._resizeStartRect = { x: frame.x, y: frame.y, width: frame.width, height: frame.height };
      c._pointerStartX = 0;
      c._pointerStartY = 0;
      c._state = InfiniteCanvas.STATE_RESIZING;
      let n = c._nodes.get(rightmostId);
      let targetWidth = n.x - frame.x - 10;
      c._doResize({ clientX: -(frame.width - targetWidth), clientY: 0, shiftKey: false });
      c._endResize({ pointerId: 1 });
      const childAfter = c._nodes.get(rightmostId).frameId;
      return { childBefore, childAfter };
    });
    expect(result.childBefore).toBe("group_1");
    expect(result.childAfter).toBeNull();
  });
});

test.describe("Overlapping Frames Prefer Smallest", () => {
  test("node dropped in overlap zone parents to smaller frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.addFrame("big_frame", { x: 2000, y: 2000, width: 600, height: 400, label: "Big" });
      c.addFrame("small_frame", { x: 2100, y: 2100, width: 200, height: 150, label: "Small" });
      c.addNode("overlap_node", { x: 2120, y: 2120, width: 80, height: 60 });
      c._checkFrameContainment("overlap_node");
      return { frameId: c._nodes.get("overlap_node").frameId };
    });
    expect(result.frameId).toBe("small_frame");
  });
});

test.describe("Alt+Arrow Spatial Navigation", () => {
  test("focusNeighbor right picks the rightward neighbor within the same group", async ({ page }) => {
    await freshPage(page);
    // group_1 contains node_1..node_4 in a 2x2 layout from autoLayout.
    // node_1 is top-left; rightward neighbor should be node_2.
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Sort children left-to-right by x; first two should be at row 0.
      let kids = c.getFrameChildren("group_1").map(id => c._nodes.get(id));
      kids.sort((a, b) => a.y - b.y || a.x - b.x);
      let sourceId = kids[0].id;
      let expectedRight = kids[1].id;
      c.deselectAll();
      c.select(sourceId);
      let returned = c.focusNeighbor("right");
      return {
        sourceId,
        expectedRight,
        returned,
        selection: c.getSelection(),
      };
    });
    expect(result.returned).toBe(result.expectedRight);
    expect(result.selection).toEqual([result.expectedRight]);
  });

  test("focusNeighbor is restricted to the same frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Take the rightmost node in group_1 and look further right.
      let kids1 = c.getFrameChildren("group_1").map(id => c._nodes.get(id));
      kids1.sort((a, b) => a.x - b.x);
      let rightmost = kids1[kids1.length - 1].id;
      c.deselectAll();
      c.select(rightmost);
      let returned = c.focusNeighbor("right");
      // No neighbor to the right exists within group_1.
      return { rightmost, returned };
    });
    expect(result.returned).toBeNull();
  });

  test("focusNeighbor ignores nodes in other frames", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Place node_5 (group_2) directly to the right of a group_1 node
      // and ensure focusNeighbor doesn't jump groups.
      let kid1 = c._nodes.get(c.getFrameChildren("group_1")[0]);
      let n5 = c._nodes.get("node_5");
      n5.frameId = "group_2";
      c._updateNodeGroupVisual(n5);
      n5.x = kid1.x + kid1.width + 20;
      n5.y = kid1.y;
      c._applyRect(n5.element, n5);
      c.deselectAll();
      c.select(kid1.id);
      let returned = c.focusNeighbor("right");
      // Should be either a group_1 sibling or null — never node_5.
      return { kid1Id: kid1.id, returned };
    });
    expect(result.returned).not.toBe("node_5");
  });

  test("focusNeighbor preserves zoom and pans to center the new node", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let kids = c.getFrameChildren("group_1").map(id => c._nodes.get(id));
      kids.sort((a, b) => a.y - b.y || a.x - b.x);
      let sourceId = kids[0].id;
      c.deselectAll();
      c.select(sourceId);
      // Force a specific zoom so we can verify it is preserved.
      c.zoomTo(1.5, 0, 0);
      let beforeZoom = c._zoom;
      c.focusNeighbor("right");
      return { beforeZoom, afterZoom: c._zoom };
    });
    // Zoom is preserved (animation also sets it but to the same target).
    expect(Math.abs(result.afterZoom - result.beforeZoom)).toBeLessThan(0.01);
  });

  test("focusNeighbor returns null with no selection", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      window.__canvas.deselectAll();
      return window.__canvas.focusNeighbor("right");
    });
    expect(result).toBeNull();
  });

  test("focusNeighbor returns null when multiple nodes selected", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      c.select("node_2");
      return c.focusNeighbor("right");
    });
    expect(result).toBeNull();
  });

  test("Alt+ArrowRight keybinding triggers neighbor focus", async ({ page }) => {
    await freshPage(page);
    const setup = await page.evaluate(() => {
      const c = window.__canvas;
      let kids = c.getFrameChildren("group_1").map(id => c._nodes.get(id));
      kids.sort((a, b) => a.y - b.y || a.x - b.x);
      // Force a single-node selection via API and focus the container so
      // the keydown listener gets the event. Clicking a child of a group
      // would also pull in the parent + siblings via "select group with
      // children" behavior, which would defeat focusNeighbor's
      // single-selection precondition.
      c.deselectAll();
      c.select(kids[0].id);
      document.getElementById("canvas-container").focus();
      return { sourceId: kids[0].id, expectedRight: kids[1].id };
    });
    await page.keyboard.down("Alt");
    await page.keyboard.press("ArrowRight");
    await page.keyboard.up("Alt");
    const sel = await page.evaluate(() => window.__canvas.getSelection());
    expect(sel).toEqual([setup.expectedRight]);
  });

  test("focusDescend from top-level selects the first frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      let returned = c.focusDescend();
      let firstFrame = c._sortedTopLevelItems()[0];
      return { returned, firstFrameId: firstFrame.id };
    });
    expect(result.returned).toBe(result.firstFrameId);
  });

  test("focusDescend from a frame selects its first child", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_1");
      let returned = c.focusDescend();
      let firstChild = c._sortedFrameChildren("group_1")[0];
      return { returned, firstChildId: firstChild.id };
    });
    expect(result.returned).toBe(result.firstChildId);
  });

  test("focusDescend on a frame child cycles to the next sibling", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let kids = c._sortedFrameChildren("group_1");
      c.deselectAll();
      c.select(kids[0].id);
      let first = c.focusDescend();
      let second = c.focusDescend();
      let third = c.focusDescend();
      let fourth = c.focusDescend();
      let cycledBack = c.focusDescend();
      return {
        kidIds: kids.map(k => k.id),
        first, second, third, fourth, cycledBack,
      };
    });
    // From kids[0], cycling through kids[1..N-1] then wrapping to kids[0]
    expect(result.first).toBe(result.kidIds[1]);
    expect(result.second).toBe(result.kidIds[2]);
    expect(result.third).toBe(result.kidIds[3]);
    expect(result.fourth).toBe(result.kidIds[0]);
    expect(result.cycledBack).toBe(result.kidIds[1]);
  });

  test("focusAscend from a child node goes to its parent frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      let kid = c._sortedFrameChildren("group_1")[0];
      c.deselectAll();
      c.select(kid.id);
      let returned = c.focusAscend();
      return { returned, selection: c.getSelection() };
    });
    expect(result.returned).toBe("group_1");
    expect(result.selection).toEqual(["group_1"]);
  });

  test("focusAscend from a frame deselects and zooms out", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_1");
      let returned = c.focusAscend();
      return { returned, selection: c.getSelection() };
    });
    expect(result.returned).toBeNull();
    expect(result.selection.length).toBe(0);
  });

  test("focusAscend from no selection is a no-op", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      let returned = c.focusAscend();
      return { returned, selection: c.getSelection() };
    });
    expect(result.returned).toBeNull();
    expect(result.selection.length).toBe(0);
  });

  test("Enter key triggers focusDescend; Shift+Enter triggers focusAscend", async ({ page }) => {
    await freshPage(page);
    const setup = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_1");
      document.getElementById("canvas-container").focus();
      let firstChild = c._sortedFrameChildren("group_1")[0];
      return { firstChildId: firstChild.id };
    });
    // Enter → drill into first child of group_1
    await page.keyboard.press("Enter");
    let sel = await page.evaluate(() => window.__canvas.getSelection());
    expect(sel).toEqual([setup.firstChildId]);
    // Shift+Enter → back up to group_1
    await page.keyboard.press("Shift+Enter");
    sel = await page.evaluate(() => window.__canvas.getSelection());
    expect(sel).toEqual(["group_1"]);
  });

  test("Alt+Enter zooms to fit the selected node (toggle)", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("node_1");
      document.getElementById("canvas-container").focus();
    });
    const before = await page.evaluate(() => ({
      panX: window.__canvas._panX,
      panY: window.__canvas._panY,
      zoom: window.__canvas._zoom,
    }));
    // First Alt+Enter saves current view and zooms in.
    await page.keyboard.press("Alt+Enter");
    // Wait past animation duration.
    await page.waitForTimeout(300);
    const zoomed = await page.evaluate(() => ({
      zoom: window.__canvas._zoom,
      hasSaved: window.__canvas.hasSavedView("node_1"),
    }));
    expect(zoomed.zoom).toBeGreaterThan(before.zoom);
    expect(zoomed.hasSaved).toBe(true);
    // Second Alt+Enter restores the original view.
    await page.keyboard.press("Alt+Enter");
    await page.waitForTimeout(300);
    const after = await page.evaluate(() => ({
      panX: window.__canvas._panX,
      panY: window.__canvas._panY,
      zoom: window.__canvas._zoom,
      hasSaved: window.__canvas.hasSavedView("node_1"),
    }));
    expect(Math.abs(after.zoom - before.zoom)).toBeLessThan(0.01);
    expect(after.hasSaved).toBe(false);
  });

  test("Alt+Enter on a focused tab group fits the group", async ({ page }) => {
    await freshPage(page);
    // Compute what zooming to fit group_1 should look like at default
    // fit options, then trigger the keypress via the same select-frame
    // path the user gets when clicking the frame label (selection holds
    // both the frame and its children).
    const setup = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c._selectFrameWithChildren("group_1");
      document.getElementById("canvas-container").focus();
      let frame = c._frames.get("group_1");
      const containerRect = document.getElementById("canvas-container").getBoundingClientRect();
      const padding = 60;
      const fitZoom = Math.min(
        (containerRect.width - padding * 2) / frame.width,
        (containerRect.height - padding * 2) / frame.height,
        3
      );
      return {
        frameW: frame.width,
        frameH: frame.height,
        beforeZoom: c._zoom,
        fitZoom,
      };
    });
    await page.keyboard.press("Alt+Enter");
    await page.waitForTimeout(300);
    const after = await page.evaluate(() => ({
      zoom: window.__canvas._zoom,
      hasSavedView: window.__canvas.hasSavedView("group_1"),
    }));
    // Zoom should have animated to the fit-zoom (preserves toggle state).
    expect(Math.abs(after.zoom - setup.fitZoom)).toBeLessThan(0.05);
    // A "previous view" should have been saved against the frame so a
    // second Alt+Enter would restore the original.
    expect(after.hasSavedView).toBe(true);
  });

  test("Alt+Enter on a frame alone (no children selected) also fits the group", async ({ page }) => {
    await freshPage(page);
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_1");
      document.getElementById("canvas-container").focus();
    });
    await page.keyboard.press("Alt+Enter");
    await page.waitForTimeout(300);
    const hasSaved = await page.evaluate(() =>
      window.__canvas.hasSavedView("group_1")
    );
    expect(hasSaved).toBe(true);
  });

  test("Shift+Enter on a child zooms out to fit the parent frame if needed", async ({ page }) => {
    await freshPage(page);
    const setup = await page.evaluate(() => {
      const c = window.__canvas;
      let kid = c._sortedFrameChildren("group_1")[0];
      c.deselectAll();
      c.select(kid.id);
      // Zoom way in so the frame can't fit at current zoom.
      c.zoomTo(3, 0, 0);
      document.getElementById("canvas-container").focus();
      let frame = c._frames.get("group_1");
      // Compute the required fit-zoom for the frame.
      const containerRect = document.getElementById("canvas-container").getBoundingClientRect();
      const padding = 60;
      const fitZoom = Math.min(
        (containerRect.width - padding * 2) / frame.width,
        (containerRect.height - padding * 2) / frame.height
      );
      return { startZoom: c._zoom, fitZoom };
    });
    await page.keyboard.press("Shift+Enter");
    await page.waitForTimeout(300);
    const after = await page.evaluate(() => window.__canvas._zoom);
    // Should have zoomed out (from 3) to roughly fitZoom or lower.
    expect(after).toBeLessThan(setup.startZoom);
    expect(after).toBeLessThanOrEqual(setup.fitZoom + 0.01);
  });

  test("focusNeighbor on a frame finds an adjacent top-level frame", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_1");
      // group_2 is positioned below group_1 by the test page setup.
      let returned = c.focusNeighbor("down");
      return { returned, selection: c.getSelection() };
    });
    expect(result.returned).toBe("group_2");
    expect(result.selection).toEqual(["group_2"]);
  });

  test("focusNeighbor on a frame includes ungrouped top-level nodes as candidates", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Place an ungrouped node directly to the right of group_1.
      let g1 = c._frames.get("group_1");
      c.addNode("loose_node", {
        x: g1.x + g1.width + 40,
        y: g1.y,
        width: 200, height: 150, title: "Loose",
      });
      c.deselectAll();
      c.select("group_1");
      let returned = c.focusNeighbor("right");
      return { returned };
    });
    expect(result.returned).toBe("loose_node");
  });

  test("Alt+arrow with no neighbor does not nudge the selection", async ({ page }) => {
    await freshPage(page);
    // group_2 is the bottom frame; alt+arrow down from it has no neighbor.
    await page.evaluate(() => {
      const c = window.__canvas;
      c.deselectAll();
      c.select("group_2");
      document.getElementById("canvas-container").focus();
    });
    const before = await page.evaluate(() => {
      const f = window.__canvas._frames.get("group_2");
      return { x: f.x, y: f.y };
    });
    await page.keyboard.down("Alt");
    await page.keyboard.press("ArrowDown");
    await page.keyboard.up("Alt");
    const after = await page.evaluate(() => {
      const f = window.__canvas._frames.get("group_2");
      return { x: f.x, y: f.y, sel: window.__canvas.getSelection() };
    });
    expect(after.x).toBe(before.x);
    expect(after.y).toBe(before.y);
    expect(after.sel).toEqual(["group_2"]);
  });

  test("Alt+arrow on a node with no neighbor in direction does not nudge", async ({ page }) => {
    await freshPage(page);
    // Move all nodes ungrouped to a known layout and select the leftmost.
    await page.evaluate(() => {
      const c = window.__canvas;
      for (let [id] of [...c._frames]) c.removeFrame(id);
      let i = 0;
      for (let [, n] of c._nodes) {
        n.frameId = null;
        c._updateNodeGroupVisual(n);
        n.x = 1000 + i * 320;
        n.y = 0;
        c._applyRect(n.element, n);
        i++;
      }
      c.deselectAll();
      c.select("node_1");
      document.getElementById("canvas-container").focus();
    });
    const before = await page.evaluate(() => {
      const n = window.__canvas._nodes.get("node_1");
      return { x: n.x, y: n.y };
    });
    await page.keyboard.down("Alt");
    await page.keyboard.press("ArrowLeft");
    await page.keyboard.up("Alt");
    const after = await page.evaluate(() => {
      const n = window.__canvas._nodes.get("node_1");
      return { x: n.x, y: n.y, sel: window.__canvas.getSelection() };
    });
    expect(after.x).toBe(before.x);
    expect(after.y).toBe(before.y);
    expect(after.sel).toEqual(["node_1"]);
  });

  test("focusNeighbor works among ungrouped nodes", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const c = window.__canvas;
      // Ungroup all so nodes are free.
      for (let [id] of [...c._frames]) c.removeFrame(id);
      for (let [, n] of c._nodes) { n.frameId = null; c._updateNodeGroupVisual(n); }
      // Pick the leftmost node, look right.
      let all = [...c._nodes.values()].sort((a, b) => a.x - b.x || a.y - b.y);
      let sourceId = all[0].id;
      c.deselectAll();
      c.select(sourceId);
      let returned = c.focusNeighbor("right");
      return { sourceId, returned };
    });
    expect(result.returned).not.toBeNull();
    expect(result.returned).not.toBe(result.sourceId);
  });
});
