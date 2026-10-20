"use strict";

const relativeOffsetDefaults = {
  writingModes: ["horizontal-tb", "vertical-lr", "vertical-rl"],
  textDirections: ["ltr", "rtl"],
  flexDirections: ["row", "column"],
  heights: [160, 4000000, 8000000, 16000000],
  counts: [4, 8, 12],
  offsets: [[0, 0], [11, 17], [-11, -17]],
};

function relativeOffsetConfigurations(options = {}) {
  const o = {...relativeOffsetDefaults, ...options};
  const result = [];
  for (const writingMode of o.writingModes) {
    for (const textDirection of o.textDirections) {
      for (const flexDirection of o.flexDirections) {
        for (const height of o.heights) {
          for (const count of o.counts) {
            for (const [inlineOffset, blockOffset] of o.offsets) {
              result.push({writingMode, textDirection, flexDirection, height,
                           count, inlineOffset, blockOffset});
            }
          }
        }
      }
    }
  }
  return result;
}

function measureRelativeOffsetFixture(config) {
  const {writingMode, textDirection, flexDirection, height, count,
         inlineOffset, blockOffset} = config;
  const columns = document.createElement("div");
  columns.className = "offset-columns";
  columns.style.writingMode = writingMode;
  columns.style.direction = textDirection;
  columns.style.setProperty("--column-height", `${height}px`);
  columns.style.setProperty("--inline-offset", `${inlineOffset}px`);
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
  const reference = columns.cloneNode();
  reference.classList.add("offset-reference");
  const referenceItems = Array.from({length: count}, (_, i) => {
    const item = document.createElement("div");
    item.className = "offset-reference-item";
    item.style.setProperty("--reference-inline", `${i * 100 + inlineOffset}px`);
    reference.append(item);
    return item;
  });
  const referenceFragment = document.createElement("div");
  referenceFragment.className = "offset-reference-fragment";
  const referenceMarker = document.createElement("div");
  referenceMarker.className = "offset-reference-marker";
  for (const node of [referenceFragment, referenceMarker]) {
    node.style.setProperty("--reference-inline", `${(count - 1) * 100}px`);
    reference.append(node);
  }
  try {
    document.body.append(reference);
    const referenceOrigin = reference.getBoundingClientRect();
    const expected = {
      items: referenceItems.map(item => logicalRect(item.getBoundingClientRect(), referenceOrigin)),
      finalFragment: logicalRect(referenceFragment.getBoundingClientRect(), referenceOrigin),
      marker: logicalRect(referenceMarker.getBoundingClientRect(), referenceOrigin),
    };
    const representable = logicalRect(referenceOrigin, referenceOrigin)[3] === height;
    const calibrated = expected.items.every((rect, i) =>
      Math.abs(rect[0] - (i * 100 + inlineOffset)) <= 1 &&
      Math.abs(rect[1] - blockOffset) <= 1 && rect[2] === 100 && rect[3] === 80) &&
      Math.abs(expected.finalFragment[0] - (count - 1) * 100) <= 1 &&
      expected.finalFragment[1] === 0 && expected.finalFragment[2] === 100 &&
      expected.finalFragment[3] === 80 &&
      Math.abs(expected.marker[0] - (count - 1) * 100) <= 1 &&
      Math.abs(expected.marker[1] - 80) <= 1 &&
      expected.marker[2] === 100 && expected.marker[3] === 20;
    reference.remove();
    const content = document.createElement("div");
    content.className = `offset-content offset-${flexDirection}`;
    const items = Array.from({length: count}, () => {
      const item = document.createElement("div");
      item.className = "offset-item";
      content.append(item);
      return item;
    });
    const marker = document.createElement("div");
    marker.className = "offset-marker";
    columns.append(content, marker);
    document.body.append(columns);
    const measure = () => {
      const origin = columns.getBoundingClientRect();
      return {
        items: items.map(item => logicalRect(item.getBoundingClientRect(), origin)),
        fragments: [...content.getClientRects()].map(rect => logicalRect(rect, origin)),
        marker: logicalRect(marker.getBoundingClientRect(), origin),
      };
    };
    const actual = measure();
    columns.remove();
    document.body.append(columns);
    const restored = measure();
    return {config, representable, calibrated,
            forcedBreakSupported: CSS.supports("break-before", "always"),
            expected, actual, restored};
  } finally {
    columns.remove();
    reference.remove();
  }
}

window.collectRelativeOffsetRows = options =>
  relativeOffsetConfigurations(options).map(measureRelativeOffsetFixture);

if (typeof test === "function") {
  for (const config of relativeOffsetConfigurations()) {
    const label = `${config.writingMode}, ${config.textDirection}, ${config.flexDirection}, ` +
      `${config.count} items, ${config.height}px columns, ` +
      `relative (${config.inlineOffset}, ${config.blockOffset})`;
    for (const observation of ["items", "flow", "restoration"]) {
      test(() => {
        const row = measureRelativeOffsetFixture(config);
        assert_implements_optional(row.representable, "The column height is representable");
        assert_implements_optional(row.forcedBreakSupported, "Forced breaks are supported");
        assert_true(row.calibrated, "Independent absolute reference geometry is calibrated");
        if (observation === "items") {
          for (let i = 0; i < config.count; ++i) {
            assert_array_equals(row.actual.items[i], row.expected.items[i],
                                `Item ${i} has its relative offset from the normal column position`);
          }
        } else if (observation === "flow") {
          assert_equals(row.actual.fragments.length, config.count, "One fragment per item");
          assert_array_equals(row.actual.fragments[config.count - 1], row.expected.finalFragment,
                              "Relative offsets preserve the final flow fragment");
          assert_array_equals(row.actual.marker, row.expected.marker,
                              "Relative offsets preserve following-sibling flow position");
        } else {
          assert_equals(JSON.stringify(row.actual), JSON.stringify(row.restored),
                        "Removal and restoration preserve all observations");
        }
      }, `${observation}: ${label}`);
    }
  }
}
