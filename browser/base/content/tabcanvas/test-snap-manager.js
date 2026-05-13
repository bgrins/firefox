/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const { test, expect } = require("@playwright/test");

const BASE_URL = "http://localhost:9876/test-snap.html";

async function freshPage(page) {
  await page.goto(BASE_URL + "?t=" + Date.now());
  await page.waitForFunction(() => typeof SnapManager !== "undefined");
}

// ---- Point Snapping ----

test.describe("SnapManager: Point Snapping", () => {
  test("snaps to aligned left edges", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const moving = { x: 102, y: 200, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBeCloseTo(-2, 1); // nudge left by 2
    expect(result.nudge.y).toBe(0);
    expect(result.indicators.length).toBeGreaterThan(0);
  });

  test("snaps to center alignment", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      // target center_x = 100 + 50 = 150. moving center_x = 147 + 50 = 197.
      // No snap there. Let's align centers properly:
      // target center = 150. moving at x=148 -> center = 198. Too far.
      // Let me use: target at x=100 w=200 -> center=200. moving at x=147 w=100 -> center=197.
      const moving = { x: 147, y: 200, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 200, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    // moving center_x = 197, target center_x = 200. diff = 3 < threshold(8)
    expect(result.nudge.x).toBeCloseTo(3, 1);
  });

  test("snaps to right edge alignment", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      // target right = 100+100 = 200. moving right = 97+100 = 197. diff = 3
      const moving = { x: 97, y: 200, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBeCloseTo(3, 1);
  });

  test("snaps Y axis independently", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const moving = { x: 500, y: 52, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBe(0); // too far on X
    expect(result.nudge.y).toBeCloseTo(-2, 1); // snaps on Y
  });

  test("no snap when outside threshold", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const moving = { x: 200, y: 200, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBe(0);
    expect(result.nudge.y).toBe(0);
  });

  test("threshold scales with zoom", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      // At zoom=2, threshold becomes 4. A 6px offset should NOT snap.
      const moving = { x: 106, y: 200, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 2);
    });
    expect(result.nudge.x).toBe(0); // 6 > 4, no snap
  });

  test("picks closest snap when multiple candidates", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const moving = { x: 153, y: 200, width: 100, height: 80 };
      const targets = [
        { id: "a", x: 150, y: 50, width: 100, height: 80 },  // left edge diff = 3
        { id: "b", x: 160, y: 50, width: 100, height: 80 },  // left edge diff = 7
      ];
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBeCloseTo(-3, 1); // snaps to closer one
  });

  test("generates line indicators for snaps", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const moving = { x: 100, y: 202, width: 100, height: 80 };
      const targets = [{ id: "a", x: 100, y: 50, width: 100, height: 80 }];
      return sm.snap(moving, targets, 1);
    });
    let lineIndicators = result.indicators.filter(i => i.type === "line");
    expect(lineIndicators.length).toBeGreaterThan(0);
    expect(lineIndicators[0].direction).toBeDefined();
    expect(lineIndicators[0].position).toBeDefined();
  });
});

// ---- Gap Snapping ----

test.describe("SnapManager: Gap Snapping", () => {
  test("detects equal gap to the right", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      // Two shapes with 50px gap between them: A at x=0, B at x=150
      // Moving shape tries to be 50px to the right of B -> x = 300
      const targets = [
        { id: "a", x: 0, y: 100, width: 100, height: 80 },
        { id: "b", x: 150, y: 100, width: 100, height: 80 },
      ];
      // If moving at x=297, should snap to x=300 (50px gap from B's right edge at 250)
      const moving = { x: 297, y: 100, width: 100, height: 80 };
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBeCloseTo(3, 1);
  });

  test("detects equal gap to the left", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const targets = [
        { id: "a", x: 200, y: 100, width: 100, height: 80 },
        { id: "b", x: 350, y: 100, width: 100, height: 80 },
      ];
      // Gap = 350 - 300 = 50. To duplicate left: 200 - 50 = 150. Moving right edge at 150.
      // Moving x + width = 150, so x = 50 for w=100.
      const moving = { x: 47, y: 100, width: 100, height: 80 };
      return sm.snap(moving, targets, 1);
    });
    expect(result.nudge.x).toBeCloseTo(3, 1); // nudge to x=50
  });

  test("generates gap indicators", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager({ threshold: 8 });
      const targets = [
        { id: "a", x: 0, y: 100, width: 100, height: 80 },
        { id: "b", x: 150, y: 100, width: 100, height: 80 },
      ];
      const moving = { x: 298, y: 100, width: 100, height: 80 };
      return sm.snap(moving, targets, 1);
    });
    let gapIndicators = result.indicators.filter(i => i.type === "gap");
    expect(gapIndicators.length).toBeGreaterThan(0);
  });
});

// ---- Alignment Commands ----

test.describe("SnapManager: Alignment", () => {
  test("align-left moves all items to leftmost edge", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager();
      const rects = [
        { id: "a", x: 50, y: 0, width: 100, height: 80 },
        { id: "b", x: 200, y: 50, width: 100, height: 80 },
        { id: "c", x: 100, y: 100, width: 100, height: 80 },
      ];
      return sm.align(rects, "align-left");
    });
    expect(result[0].x).toBe(50);
    expect(result[1].x).toBe(50);
    expect(result[2].x).toBe(50);
  });

  test("align-right moves all items to rightmost edge", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager();
      const rects = [
        { id: "a", x: 50, y: 0, width: 100, height: 80 },
        { id: "b", x: 200, y: 50, width: 100, height: 80 },
      ];
      return sm.align(rects, "align-right");
    });
    // Rightmost edge = 200+100 = 300. a moves to 300-100=200, b stays at 200
    expect(result[0].x).toBe(200);
    expect(result[1].x).toBe(200);
  });

  test("align-center-h centers all horizontally", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager();
      const rects = [
        { id: "a", x: 0, y: 0, width: 100, height: 80 },
        { id: "b", x: 200, y: 50, width: 100, height: 80 },
      ];
      return sm.align(rects, "align-center-h");
    });
    // Bounds: x=0, width=300 -> center=150. a: 150-50=100, b: 150-50=100
    expect(result[0].x).toBe(100);
    expect(result[1].x).toBe(100);
  });

  test("distribute-h spaces items evenly", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager();
      const rects = [
        { id: "a", x: 0, y: 0, width: 100, height: 80 },
        { id: "b", x: 300, y: 0, width: 100, height: 80 },
        { id: "c", x: 50, y: 0, width: 100, height: 80 },  // out of order
      ];
      return sm.align(rects, "distribute-h");
    });
    // Sorted by x: a(0), c(50), b(300)
    // Span = 300+100-0 = 400. Total widths = 300. Gap = (400-300)/2 = 50
    // a: x=0, c: x=150, b: x=300
    expect(result[0].x).toBe(0);
    expect(result[1].x).toBe(150);
    expect(result[2].x).toBe(300);
  });

  test("distribute-v spaces items evenly vertically", async ({ page }) => {
    await freshPage(page);
    const result = await page.evaluate(() => {
      const sm = new SnapManager();
      const rects = [
        { id: "a", x: 0, y: 0, width: 100, height: 80 },
        { id: "b", x: 0, y: 400, width: 100, height: 80 },
        { id: "c", x: 0, y: 100, width: 100, height: 80 },
      ];
      return sm.align(rects, "distribute-v");
    });
    // Sorted by y: a(0), c(100), b(400). Span=480. Sizes=240. Gap=(480-240)/2=120
    expect(result[0].y).toBe(0);
    expect(result[1].y).toBe(200);
    expect(result[2].y).toBe(400);
  });
});
