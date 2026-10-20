"use strict";

window.collectOverflowContainerRows = (options = {}) => {
  const o = {writingModes: ["horizontal-tb", "vertical-rl"],
             flexDirections: ["row", "column"], heights: [160, 16000000],
             counts: [4, 8], ...options};
  const rows = [];
  for (const writingMode of o.writingModes) {
    for (const flexDirection of o.flexDirections) {
      for (const height of o.heights) {
        for (const count of o.counts) {
          const columns = document.createElement("div");
          columns.className = "oc-columns";
          columns.style.writingMode = writingMode;
          columns.style.setProperty("--height", `${height}px`);
          const logicalRect = (r, c) => writingMode === "horizontal-tb"
            ? [r.left - c.left, r.top - c.top, r.width, r.height]
            : [r.top - c.top, c.right - r.right, r.height, r.width];
          const reference = columns.cloneNode();
          reference.classList.add("oc-reference");
          const refs = Array.from({length: count}, (_, i) => {
            const div = document.createElement("div");
            div.style.setProperty("--inline", `${i * 100}px`);
            reference.append(div);
            return div;
          });
          try {
            document.body.append(reference);
            const refOrigin = reference.getBoundingClientRect();
            const expected = refs.map(div => logicalRect(div.getBoundingClientRect(), refOrigin));
            const representable = logicalRect(refOrigin, refOrigin)[3] === height;
            const calibrated = expected.every((r, i) =>
              r[0] === i * 100 && r[1] === 0 && r[2] === 100 && r[3] === 20);
            reference.remove();
            const flex = document.createElement("div");
            flex.className = `oc-flex oc-${flexDirection}`;
            const items = Array.from({length: count}, () => {
              const div = document.createElement("div");
              div.className = "oc-item";
              flex.append(div);
              return div;
            });
            const descendants = Array.from({length: count}, () => {
              const div = document.createElement("div");
              div.className = "oc-descendant";
              items[0].append(div);
              return div;
            });
            columns.append(flex);
            document.body.append(columns);
            const measure = () => {
              const origin = columns.getBoundingClientRect();
              const rel = r => logicalRect(r, origin);
              return {descendants: descendants.map(div => rel(div.getBoundingClientRect())),
                      itemFragments: items.map(div => [...div.getClientRects()].map(rel)),
                      flexFragments: [...flex.getClientRects()].map(rel),
                      computedBreaks: descendants.map(div => getComputedStyle(div).breakBefore)};
            };
            const actual = measure();
            columns.remove();
            document.body.append(columns);
            const restored = measure();
            rows.push({config: {writingMode, flexDirection, height, count},
                       representable, calibrated, expected, actual, restored,
                       descendantGeometryMatches: JSON.stringify(actual.descendants) === JSON.stringify(expected),
                       restorationMatches: JSON.stringify(actual) === JSON.stringify(restored)});
          } finally {
            columns.remove();
            reference.remove();
          }
        }
      }
    }
  }
  return rows;
};
