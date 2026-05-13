/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * SnapManager - snapping engine for InfiniteCanvas.
 *
 * Provides:
 * - Point snapping: align edges, centers, and corners
 * - Gap snapping: detect and enforce equal spacing between shapes
 * - Snap indicators: visual guide data for rendering
 *
 * Operates on plain {x, y, width, height} rects. No DOM dependency.
 */
class SnapManager {
  static DEFAULT_THRESHOLD = 8;

  constructor({ threshold = SnapManager.DEFAULT_THRESHOLD } = {}) {
    this._threshold = threshold;
  }

  /**
   * Given a dragged rect and a set of target rects, compute the snap nudge
   * and visual indicators.
   *
   * @param {Object} movingRect - {x, y, width, height} of the item being dragged
   * @param {Array} targets - [{id, x, y, width, height}, ...] other items to snap to
   * @param {number} zoom - current zoom level (threshold scales with 1/zoom)
   * @returns {{ nudge: {x, y}, indicators: Array }}
   */
  snap(movingRect, targets, zoom = 1) {
    let threshold = this._threshold / zoom;
    let pointResult = this._collectPointSnaps(movingRect, targets, threshold);
    let gapResult = this._collectGapSnaps(movingRect, targets, threshold);

    // Merge: prefer point snaps if they exist, then try gap snaps
    let nudgeX = pointResult.nudgeX;
    let nudgeY = pointResult.nudgeY;
    let indicators = [...pointResult.indicators];

    // Gap snaps only apply on axes where point snaps didn't fire
    if (nudgeX === 0 && gapResult.nudgeX !== 0 && Math.abs(gapResult.nudgeX) <= threshold) {
      nudgeX = gapResult.nudgeX;
    }
    if (nudgeY === 0 && gapResult.nudgeY !== 0 && Math.abs(gapResult.nudgeY) <= threshold) {
      nudgeY = gapResult.nudgeY;
    }
    indicators.push(...gapResult.indicators);

    return {
      nudge: { x: nudgeX, y: nudgeY },
      indicators,
    };
  }

  /**
   * Compute alignment commands for selected rects within a container.
   * @param {Array} rects - [{id, x, y, width, height}, ...]
   * @param {string} command - "align-left"|"align-center-h"|"align-right"|"align-top"|"align-center-v"|"align-bottom"|"distribute-h"|"distribute-v"
   * @param {Object} container - optional {x, y, width, height} bounding container
   * @returns {Array} [{id, x, y}, ...] new positions
   */
  align(rects, command, container = null) {
    if (rects.length === 0) {
      return [];
    }

    let bounds = container || this._boundsOf(rects);
    let results = [];

    switch (command) {
      case "align-left":
        for (let r of rects) {
          results.push({ id: r.id, x: bounds.x, y: r.y });
        }
        break;
      case "align-center-h":
        for (let r of rects) {
          results.push({ id: r.id, x: bounds.x + (bounds.width - r.width) / 2, y: r.y });
        }
        break;
      case "align-right":
        for (let r of rects) {
          results.push({ id: r.id, x: bounds.x + bounds.width - r.width, y: r.y });
        }
        break;
      case "align-top":
        for (let r of rects) {
          results.push({ id: r.id, x: r.x, y: bounds.y });
        }
        break;
      case "align-center-v":
        for (let r of rects) {
          results.push({ id: r.id, x: r.x, y: bounds.y + (bounds.height - r.height) / 2 });
        }
        break;
      case "align-bottom":
        for (let r of rects) {
          results.push({ id: r.id, x: r.x, y: bounds.y + bounds.height - r.height });
        }
        break;
      case "distribute-h":
        results = this._distribute(rects, "horizontal");
        break;
      case "distribute-v":
        results = this._distribute(rects, "vertical");
        break;
    }
    return results;
  }

  // ---- Point Snapping ----

  _collectPointSnaps(movingRect, targets, threshold) {
    let movingSnaps = this._getSnapPoints(movingRect);
    let nudgeX = 0;
    let nudgeY = 0;
    let minDistX = Infinity;
    let minDistY = Infinity;
    let snapPairsX = [];
    let snapPairsY = [];

    for (let target of targets) {
      let targetSnaps = this._getSnapPoints(target);
      for (let ms of movingSnaps) {
        for (let ts of targetSnaps) {
          // X-axis alignment
          let dx = Math.abs(ts.x - ms.x);
          if (dx <= threshold) {
            let rounded = this._round(dx);
            let roundedMin = this._round(minDistX);
            if (rounded < roundedMin) {
              minDistX = dx;
              nudgeX = ts.x - ms.x;
              snapPairsX = [{ moving: ms, target: ts }];
            } else if (rounded === roundedMin) {
              snapPairsX.push({ moving: ms, target: ts });
            }
          }
          // Y-axis alignment
          let dy = Math.abs(ts.y - ms.y);
          if (dy <= threshold) {
            let rounded = this._round(dy);
            let roundedMin = this._round(minDistY);
            if (rounded < roundedMin) {
              minDistY = dy;
              nudgeY = ts.y - ms.y;
              snapPairsY = [{ moving: ms, target: ts }];
            } else if (rounded === roundedMin) {
              snapPairsY.push({ moving: ms, target: ts });
            }
          }
        }
      }
    }

    let indicators = [];
    if (snapPairsX.length > 0) {
      indicators.push(...this._pointSnapIndicators(snapPairsX, "vertical"));
    }
    if (snapPairsY.length > 0) {
      indicators.push(...this._pointSnapIndicators(snapPairsY, "horizontal"));
    }

    return { nudgeX, nudgeY, indicators };
  }

  _getSnapPoints(rect) {
    return [
      // Edges
      { x: rect.x, y: rect.y + rect.height / 2, type: "left" },
      { x: rect.x + rect.width, y: rect.y + rect.height / 2, type: "right" },
      { x: rect.x + rect.width / 2, y: rect.y, type: "top" },
      { x: rect.x + rect.width / 2, y: rect.y + rect.height, type: "bottom" },
      // Center
      { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2, type: "center" },
      // Corners
      { x: rect.x, y: rect.y, type: "tl" },
      { x: rect.x + rect.width, y: rect.y, type: "tr" },
      { x: rect.x, y: rect.y + rect.height, type: "bl" },
      { x: rect.x + rect.width, y: rect.y + rect.height, type: "br" },
    ];
  }

  _pointSnapIndicators(pairs, lineDirection) {
    // Group pairs by their target coordinate to form lines
    let groups = new Map();
    for (let pair of pairs) {
      let key = lineDirection === "vertical"
        ? this._round(pair.target.x)
        : this._round(pair.target.y);
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key).push(pair);
    }

    let indicators = [];
    for (let [coord, group] of groups) {
      let points = [];
      for (let p of group) {
        points.push(p.moving, p.target);
      }
      // Compute line extent
      let minP, maxP;
      if (lineDirection === "vertical") {
        points.sort((a, b) => a.y - b.y);
        minP = points[0].y;
        maxP = points[points.length - 1].y;
        indicators.push({
          type: "line",
          direction: lineDirection,
          position: coord,
          start: minP - 20,
          end: maxP + 20,
        });
      } else {
        points.sort((a, b) => a.x - b.x);
        minP = points[0].x;
        maxP = points[points.length - 1].x;
        indicators.push({
          type: "line",
          direction: lineDirection,
          position: coord,
          start: minP - 20,
          end: maxP + 20,
        });
      }
    }
    return indicators;
  }

  // ---- Gap Snapping ----

  _collectGapSnaps(movingRect, targets, threshold) {
    let hGaps = this._detectGaps(targets, "horizontal");
    let vGaps = this._detectGaps(targets, "vertical");

    let nudgeX = 0;
    let nudgeY = 0;
    let minDistX = Infinity;
    let minDistY = Infinity;
    let indicators = [];

    let mx1 = movingRect.x;
    let mx2 = movingRect.x + movingRect.width;
    let my1 = movingRect.y;
    let my2 = movingRect.y + movingRect.height;
    let mcx = movingRect.x + movingRect.width / 2;
    let mcy = movingRect.y + movingRect.height / 2;

    // For each horizontal gap, check if the moving rect can match the gap
    for (let gap of hGaps) {
      // Duplicate gap to the left
      let leftTarget = gap.startRect.x - gap.length;
      let dx = Math.abs(leftTarget - mx2);
      if (dx < minDistX && dx <= threshold) {
        minDistX = dx;
        nudgeX = leftTarget - mx2;
        indicators = indicators.filter(i => i.gapAxis !== "horizontal");
        indicators.push({
          type: "gap",
          gapAxis: "horizontal",
          direction: "horizontal",
          gaps: [
            { start: mx2 + (leftTarget - mx2), end: gap.startRect.x, y: gap.midY },
            { start: gap.endX, end: gap.endRect.x, y: gap.midY },
          ],
        });
      }

      // Duplicate gap to the right
      let rightTarget = gap.endRect.x + gap.endRect.width + gap.length;
      dx = Math.abs(rightTarget - (mx1 + movingRect.width));
      let rightNudge = (gap.endRect.x + gap.endRect.width + gap.length) - mx2;
      let rightDx = Math.abs(gap.endRect.x + gap.endRect.width - mx1 + gap.length);
      // Simpler: check if moving.minX can sit at endRect.maxX + gap.length
      let targetMinX = gap.endRect.x + gap.endRect.width + gap.length;
      dx = Math.abs(targetMinX - mx1);
      if (dx < minDistX && dx <= threshold) {
        minDistX = dx;
        nudgeX = targetMinX - mx1;
        indicators = indicators.filter(i => i.gapAxis !== "horizontal");
        indicators.push({
          type: "gap",
          gapAxis: "horizontal",
          direction: "horizontal",
          gaps: [
            { start: gap.startRect.x + gap.startRect.width, end: gap.endRect.x, y: gap.midY },
            { start: gap.endRect.x + gap.endRect.width, end: targetMinX, y: gap.midY },
          ],
        });
      }
    }

    // Same for vertical gaps
    for (let gap of vGaps) {
      let topTarget = gap.startRect.y - gap.length;
      let dy = Math.abs(topTarget - my2);
      if (dy < minDistY && dy <= threshold) {
        minDistY = dy;
        nudgeY = topTarget - my2;
        indicators = indicators.filter(i => i.gapAxis !== "vertical");
        indicators.push({
          type: "gap",
          gapAxis: "vertical",
          direction: "vertical",
          gaps: [
            { start: my2 + (topTarget - my2), end: gap.startRect.y, x: gap.midX },
            { start: gap.endY, end: gap.endRect.y, x: gap.midX },
          ],
        });
      }

      let targetMinY = gap.endRect.y + gap.endRect.height + gap.length;
      dy = Math.abs(targetMinY - my1);
      if (dy < minDistY && dy <= threshold) {
        minDistY = dy;
        nudgeY = targetMinY - my1;
        indicators = indicators.filter(i => i.gapAxis !== "vertical");
        indicators.push({
          type: "gap",
          gapAxis: "vertical",
          direction: "vertical",
          gaps: [
            { start: gap.startRect.y + gap.startRect.height, end: gap.endRect.y, x: gap.midX },
            { start: gap.endRect.y + gap.endRect.height, end: targetMinY, x: gap.midX },
          ],
        });
      }
    }

    return { nudgeX, nudgeY, indicators };
  }

  _detectGaps(rects, direction) {
    if (rects.length < 2) {
      return [];
    }
    let gaps = [];
    let sorted;

    if (direction === "horizontal") {
      sorted = [...rects].sort((a, b) => a.x - b.x);
      for (let i = 0; i < sorted.length - 1; i++) {
        let a = sorted[i];
        let b = sorted[i + 1];
        let aRight = a.x + a.width;
        if (aRight < b.x) {
          // Check vertical overlap
          let overlapStart = Math.max(a.y, b.y);
          let overlapEnd = Math.min(a.y + a.height, b.y + b.height);
          if (overlapEnd > overlapStart) {
            gaps.push({
              startRect: a,
              endRect: b,
              endX: aRight,
              length: b.x - aRight,
              midY: (overlapStart + overlapEnd) / 2,
            });
          }
        }
      }
    } else {
      sorted = [...rects].sort((a, b) => a.y - b.y);
      for (let i = 0; i < sorted.length - 1; i++) {
        let a = sorted[i];
        let b = sorted[i + 1];
        let aBottom = a.y + a.height;
        if (aBottom < b.y) {
          let overlapStart = Math.max(a.x, b.x);
          let overlapEnd = Math.min(a.x + a.width, b.x + b.width);
          if (overlapEnd > overlapStart) {
            gaps.push({
              startRect: a,
              endRect: b,
              endY: aBottom,
              length: b.y - aBottom,
              midX: (overlapStart + overlapEnd) / 2,
            });
          }
        }
      }
    }
    return gaps;
  }

  // ---- Distribution ----

  _distribute(rects, direction) {
    if (rects.length < 3) {
      return rects.map(r => ({ id: r.id, x: r.x, y: r.y }));
    }

    let sorted, totalSize, totalSpan;
    if (direction === "horizontal") {
      sorted = [...rects].sort((a, b) => a.x - b.x);
      totalSize = sorted.reduce((sum, r) => sum + r.width, 0);
      let minX = sorted[0].x;
      let maxX = sorted[sorted.length - 1].x + sorted[sorted.length - 1].width;
      totalSpan = maxX - minX;
      let gap = (totalSpan - totalSize) / (sorted.length - 1);
      let x = minX;
      return sorted.map(r => {
        let result = { id: r.id, x, y: r.y };
        x += r.width + gap;
        return result;
      });
    } else {
      sorted = [...rects].sort((a, b) => a.y - b.y);
      totalSize = sorted.reduce((sum, r) => sum + r.height, 0);
      let minY = sorted[0].y;
      let maxY = sorted[sorted.length - 1].y + sorted[sorted.length - 1].height;
      totalSpan = maxY - minY;
      let gap = (totalSpan - totalSize) / (sorted.length - 1);
      let y = minY;
      return sorted.map(r => {
        let result = { id: r.id, x: r.x, y };
        y += r.height + gap;
        return result;
      });
    }
  }

  // ---- Helpers ----

  _boundsOf(rects) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (let r of rects) {
      minX = Math.min(minX, r.x);
      minY = Math.min(minY, r.y);
      maxX = Math.max(maxX, r.x + r.width);
      maxY = Math.max(maxY, r.y + r.height);
    }
    return { x: minX, y: minY, width: maxX - minX, height: maxY - minY };
  }

  _round(n) {
    return Math.round(n * 1e8) / 1e8;
  }
}

export default SnapManager;
export { SnapManager };
