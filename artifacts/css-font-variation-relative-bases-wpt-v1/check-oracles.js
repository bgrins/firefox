"use strict";
const fs = require("fs");
const vm = require("vm");
const path = require("path");
const fail = message => { throw new Error(message); };
const ctx = vm.createContext({
  window: {},
  assert_true: (v, m) => { if (!v) fail(m); },
  assert_equals: (a, b, m) => { if (a !== b) fail(m); },
  assert_approx_equals: (a, b, epsilon, m) => { if (!(Math.abs(a - b) <= epsilon)) fail(m); },
  assert_greater_than: (a, b, m) => { if (!(a > b)) fail(m); },
});
vm.runInContext(fs.readFileSync(path.join(__dirname, "tests/css/css-fonts/support/font-variation-relative-bases.js"), "utf8"), ctx);
const rows = [
  ["initial", 20, 40, 23, 51, 79, 37],
  ["parent-only", 30, 40, 23, 61, 79, 37],
  ["child-only", 30, 60, 23, 61, 99, 37],
  ["root-only", 30, 60, 31, 61, 99, 47],
].flatMap(([phase, parent, child, root, parentLine, childLine, rootLine]) => ["first", "settled"].map(timing => ({
  phase, parent, child, root, parentLine, childLine, rootLine, timing,
  supports: true, declaration: '"wdth" calc(1em / 1px)', raw: `"wdth" ${parent}`,
  actual: parent, expected: parent, multiplier: 1, childMetric: child,
  literal: 20, absolute: 20, opacity: child / 100,
  parentFont: `${parent}px`, childFont: `${child}px`, rootFont: `${root}px`,
  parentLineHeight: `${parentLine}px`, childLineHeight: `${childLine}px`, rootLineHeight: `${rootLine}px`,
  parentWritingMode: "horizontal-tb", parentOrientation: "mixed", childWritingMode: "horizontal-tb", childOrientation: "mixed", vertical: false,
})));
ctx.checkVariationRows(rows, "em", "ordinary");
const animated = rows.map(r => ({ ...r, actual: 2 * r.parent, expected: 2 * r.parent, multiplier: 2, progress: 0.5, playState: "paused", keyframeCount: 2 }));
ctx.checkVariationRows(animated, "em", "animation");
const negatives = [
  ["observed child-base result", data => { for (const r of data) r.actual = r.child; }, "ordinary"],
  ["stale parent value", data => { for (const r of data) r.actual = 20; }, "ordinary"],
  ["literal control wrong", data => { data[0].literal = 21; }, "ordinary"],
  ["absolute control wrong", data => { data[0].absolute = 21; }, "ordinary"],
  ["unrelated number globally rebased", data => { data[0].opacity = 0.2; }, "ordinary"],
  ["rejected grammar", data => { data[0].supports = false; }, "ordinary"],
  ["omitted phase", data => { data.pop(); }, "ordinary"],
  ["wrong parent orientation", data => { data[0].parentOrientation = "upright"; }, "ordinary"],
  ["animation did not sample", data => { data[0].progress = null; }, "animation"],
];
for (const [name, mutate, mode] of negatives) {
  const data = structuredClone(mode === "animation" ? animated : rows);
  mutate(data);
  let rejected = false;
  try { ctx.checkVariationRows(data, "em", mode); } catch { rejected = true; }
  if (!rejected) fail(`Accepted invalid control: ${name}`);
}
for (const raw of ["normal", '"wght" 20', '"wdth" NaN', '"wdth" 20, "wdth" 30']) {
  if (!Number.isNaN(ctx.variationNumber(raw))) fail(`Parsed unsupported serialization: ${raw}`);
}
process.stdout.write(JSON.stringify({ positives: 2, negativeControls: negatives.map(n => n[0]), serializationRejections: 4, browserExecution: false }) + "\n");
