"use strict";

const absposContinuationDefaults = {
  writingModes: ["horizontal-tb", "vertical-rl"],
  textDirections: ["ltr"],
  flexDirections: ["row", "column"],
  heights: [160, 8000000, 16000000],
  counts: [4, 8, 12],
  blockOffsets: [0],
  kinds: ["single", "span"],
};

function absposContinuationConfigurations(options = {}) {
  const o = {...absposContinuationDefaults, ...options};
  const rows = [];
  for (const writingMode of o.writingModes) {
    for (const textDirection of o.textDirections) {
      for (const flexDirection of o.flexDirections) {
        for (const height of o.heights) {
          for (const count of o.counts) {
            for (const blockOffset of o.blockOffsets) {
              for (const kind of o.kinds) {
                rows.push({writingMode, textDirection, flexDirection,
                           height, count, blockOffset, kind});
              }
            }
          }
        }
      }
    }
  }
  return rows;
}

function measureAbsposContinuation(config) {
  const {writingMode, textDirection, flexDirection, height,
         count, blockOffset, kind} = config;
  const columns = document.createElement("div");
  columns.className = "abs-columns";
  columns.style.writingMode = writingMode;
  columns.style.direction = textDirection;
  columns.style.setProperty("--column-height", `${height}px`);
  columns.style.setProperty("--block-offset", `${blockOffset}px`);
  const logicalRect = (r, c) => {
    if (writingMode === "horizontal-tb") {
      return [textDirection === "rtl" ? c.right - r.right : r.left - c.left,
              r.top - c.top, r.width, r.height];
    }
    return [textDirection === "rtl" ? c.bottom - r.bottom : r.top - c.top,
            writingMode === "vertical-rl" ? c.right - r.right : r.left - c.left,
            r.height, r.width];
  };
  const absoluteCount = kind === "span" ? count : 1;
  const reference = columns.cloneNode();
  reference.classList.add("abs-reference");
  const references = Array.from({length: count}, (_, i) => {
    const item = document.createElement("div");
    item.className = "abs-reference-item";
    item.style.setProperty("--reference-inline", `${i * 100}px`);
    item.style.setProperty("--reference-block", `${i === 0 ? blockOffset : 0}px`);
    reference.append(item);
    return item;
  });
  try {
    document.body.append(reference);
    const refOrigin = reference.getBoundingClientRect();
    const expectedItems = references.slice(0, absoluteCount).map(item =>
      logicalRect(item.getBoundingClientRect(), refOrigin));
    const representable = logicalRect(refOrigin, refOrigin)[3] === height;
    const calibrated = expectedItems.every((rect, i) =>
      Math.abs(rect[0] - i * 100) <= 1 &&
      Math.abs(rect[1] - (i === 0 ? blockOffset : 0)) <= 1 &&
      rect[2] === 100 && rect[3] === height);
    reference.remove();
    const content = document.createElement("div");
    content.className = `abs-flex abs-${flexDirection}`;
    const flowItems = Array.from({length: count}, () => {
      const item = document.createElement("div");
      item.className = "abs-flow-item";
      content.append(item);
      return item;
    });
    const absolute = document.createElement("div");
    absolute.className = "abs-subject";
    const absoluteItems = Array.from({length: absoluteCount}, () => {
      const item = document.createElement("div");
      item.className = "abs-subject-item";
      absolute.append(item);
      return item;
    });
    content.append(absolute);
    const marker = document.createElement("div");
    marker.className = "abs-marker";
    columns.append(content, marker);
    document.body.append(columns);
    const measure = () => {
      const origin = columns.getBoundingClientRect();
      const relative = rect => logicalRect(rect, origin);
      return {
        absoluteItems: absoluteItems.map(item => relative(item.getBoundingClientRect())),
        absoluteItemFragments: absoluteItems.map(item => [...item.getClientRects()].map(relative)),
        absoluteFragments: [...absolute.getClientRects()].map(relative),
        flowItems: flowItems.map(item => relative(item.getBoundingClientRect())),
        flexFragments: [...content.getClientRects()].map(relative),
        marker: relative(marker.getBoundingClientRect()),
        computed: {position: getComputedStyle(absolute).position,
                   insetBlockStart: getComputedStyle(absolute).insetBlockStart,
                   forcedBreaks: absoluteItems.map(item => getComputedStyle(item).breakBefore)},
      };
    };
    const actual = measure();
    columns.remove();
    document.body.append(columns);
    const restored = measure();
    const itemSizesCalibrated = actual.absoluteItems.every(rect => rect[2] === 100 && rect[3] === height);
    const equals = (a, b) => JSON.stringify(a) === JSON.stringify(b);
    return {config, representable, calibrated, itemSizesCalibrated,
            forcedBreakSupported: CSS.supports("break-before", "always"),
            expectedItems, actual, restored,
            checks: {absoluteItemGeometry: equals(actual.absoluteItems, expectedItems),
                     absoluteContinuationCount: actual.absoluteFragments.length === absoluteCount,
                     restoration: equals(actual, restored)}};
  } finally {
    columns.remove();
    reference.remove();
  }
}

window.collectTallAbsposContinuationRows = options =>
  absposContinuationConfigurations(options).map(measureAbsposContinuation);
