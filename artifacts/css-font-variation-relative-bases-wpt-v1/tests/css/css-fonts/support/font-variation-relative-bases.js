"use strict";

const variationUnits = ["em", "ex", "ch", "cap", "ic", "lh", "rem", "rex", "rch", "rcap", "ric", "rlh"];
const variationPhases = [
  { name: "initial", parent: 20, child: 40, root: 23, parentLine: 51, childLine: 79, rootLine: 37 },
  { name: "parent-only", parent: 30, child: 40, root: 23, parentLine: 61, childLine: 79, rootLine: 37 },
  { name: "child-only", parent: 30, child: 60, root: 23, parentLine: 61, childLine: 99, rootLine: 37 },
  { name: "root-only", parent: 30, child: 60, root: 31, parentLine: 61, childLine: 99, rootLine: 47 },
];
window.variationBaseObservations = [];

function variationNumber(raw) {
  const match = /^"wdth"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)$/i.exec(raw);
  return match ? Number(match[1]) : NaN;
}

async function variationFrame(t, body, style) {
  const frame = document.createElement("iframe");
  frame.title = "Isolated variation-settings metric bases";
  const loaded = new Promise(resolve => { frame.onload = resolve; });
  frame.srcdoc = `<!doctype html><meta charset="utf-8"><title>Metric bases</title><style>
    html { writing-mode: horizontal-tb; text-orientation: mixed; }
    body { margin: 0; }
    .metric { display: block; height: 0; padding: 0; border: 0; }
    ${style}
  </style>${body}`;
  t.add_cleanup(() => frame.remove());
  document.body.append(frame);
  await loaded;
  await frame.contentDocument.fonts.ready;
  assert_equals(frame.contentDocument.compatMode, "CSS1Compat", "Standards-mode fixture");
  return frame;
}

async function variationSettled(win) {
  await win.document.fonts.ready;
  await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
}

function checkVariationRows(rows, unit, mode) {
  assert_equals(rows.length, 8, "All four first/settled phase pairs retained");
  for (const row of rows) {
    const label = `${mode}/${unit}/${row.phase}/${row.timing}`;
    assert_true(row.supports && row.declaration !== "", `${label}: typed arithmetic admitted`);
    assert_true(Number.isFinite(row.expected) && row.expected > 0, `${label}: metric reference is finite`);
    assert_approx_equals(row.literal, 20, 0.001, `${label}: literal control`);
    assert_approx_equals(row.absolute, 20, 0.001, `${label}: absolute ratio control`);
    assert_approx_equals(row.opacity, row.child / 100, 0.001, `${label}: unrelated numeric property keeps child em`);
    assert_equals(row.parentFont, `${row.parent}px`, `${label}: parent font-size`);
    assert_equals(row.childFont, `${row.child}px`, `${label}: child font-size`);
    assert_equals(row.rootFont, `${row.root}px`, `${label}: root font-size`);
    assert_equals(row.parentLineHeight, row.normalLine ? "normal" : `${row.parentLine}px`, `${label}: parent line-height`);
    assert_equals(row.childLineHeight, `${row.childLine}px`, `${label}: child line-height`);
    assert_equals(row.rootLineHeight, `${row.rootLine}px`, `${label}: root line-height`);
    assert_greater_than(Math.abs(row.expected / row.multiplier - row.childMetric), 0.1,
      `${label}: reference distinguishes parent/root from child`);
    assert_equals(row.parentWritingMode, row.vertical ? "vertical-rl" : "horizontal-tb", `${label}: parent writing mode`);
    assert_equals(row.parentOrientation, row.vertical ? "upright" : "mixed", `${label}: parent orientation`);
    assert_equals(row.childWritingMode, "horizontal-tb", `${label}: child writing mode`);
    assert_equals(row.childOrientation, "mixed", `${label}: child orientation`);
    if (mode === "animation") {
      assert_equals(row.progress, 0.5, `${label}: actual keyframe sampling`);
      assert_equals(row.playState, "paused", `${label}: deterministic sample`);
      assert_equals(row.keyframeCount, 2, `${label}: two keyframes retained`);
    }
    assert_approx_equals(row.actual, row.expected, 0.03,
      `${label}: variation value uses the referred element's required metrics; raw=${row.raw}`);
  }
  for (let i = 0; i < rows.length; i += 2) {
    assert_approx_equals(rows[i].actual, rows[i + 1].actual, 0.001, "First and settled values agree");
  }
}

async function variationChildCase(t, unit, mode) {
  const vertical = false;
  const normalLine = false;
  const rootUnit = unit.startsWith("r");
  const localUnit = rootUnit ? unit.slice(1) : unit;
  const value = `"wdth" calc(1${unit} / 1px)`;
  const frame = await variationFrame(t, `
    <div id="root-probe"><div class="metric" id="root-metric"></div></div>
    <div id="parent">
      <div class="metric" id="parent-metric"></div>
      <div id="child-probe"><div class="metric" id="child-metric"></div></div>
      <div class="child" id="target"></div>
      <div class="child" id="literal"></div>
      <div class="child" id="absolute"></div>
      <div class="child" id="nonfont"></div>
    </div>`, `
    html { font-family: monospace; font-variation-settings: normal; }
    #parent, #root-probe, #child-probe { font-variation-settings: normal; }
    #parent { writing-mode: ${vertical ? "vertical-rl" : "horizontal-tb"}; text-orientation: ${vertical ? "upright" : "mixed"}; }
    .child, #child-probe { writing-mode: horizontal-tb; text-orientation: mixed; }
    .child, #child-probe { font-size: var(--child-size); line-height: var(--child-line); }
    #target { font-variation-settings: ${value}; }
    #literal { font-variation-settings: "wdth" 20; }
    #absolute { font-variation-settings: "wdth" calc(20px / 1px); }
    #nonfont { opacity: calc(1em / 100px); }
    .metric { width: 100${localUnit}; }
  `);
  const win = frame.contentWindow;
  const doc = frame.contentDocument;
  const target = doc.getElementById("target");
  const parent = doc.getElementById("parent");
  const root = doc.documentElement;
  const rows = [];
  const record = { unit, mode, vertical, normalLine, rows };
  window.variationBaseObservations.push(record);
  let animation;
  for (const phase of variationPhases) {
    root.style.fontSize = `${phase.root}px`;
    root.style.lineHeight = `${phase.rootLine}px`;
    parent.style.fontSize = `${phase.parent}px`;
    parent.style.lineHeight = normalLine ? "normal" : `${phase.parentLine}px`;
    parent.style.setProperty("--child-size", `${phase.child}px`);
    parent.style.setProperty("--child-line", `${phase.childLine}px`);
    if (mode === "animation" && !animation) {
      animation = target.animate([
        { fontVariationSettings: value },
        { fontVariationSettings: `"wdth" calc(3${unit} / 1px)` },
      ], { duration: 1000, fill: "both" });
      animation.pause();
      animation.currentTime = 500;
      t.add_cleanup(() => animation.cancel());
    }
    const take = timing => {
      const raw = win.getComputedStyle(target).fontVariationSettings;
      const css = element => win.getComputedStyle(element);
      const metric = id => doc.getElementById(id).getBoundingClientRect().width / 100;
      const multiplier = mode === "animation" ? 2 : 1;
      const declaration = Array.from(doc.styleSheets[0].cssRules)
        .find(rule => rule.selectorText === "#target").style.fontVariationSettings;
      rows.push({
        ...phase, phase: phase.name, timing, raw, normalLine, actual: variationNumber(raw),
        supports: win.CSS.supports("font-variation-settings", value), declaration,
        expected: multiplier * metric(rootUnit ? "root-metric" : "parent-metric"), multiplier,
        childMetric: metric("child-metric"),
        literal: variationNumber(css(doc.getElementById("literal")).fontVariationSettings),
        absolute: variationNumber(css(doc.getElementById("absolute")).fontVariationSettings),
        opacity: Number(css(doc.getElementById("nonfont")).opacity),
        parentFont: css(parent).fontSize, childFont: css(target).fontSize, rootFont: css(root).fontSize,
        parentLineHeight: css(parent).lineHeight, childLineHeight: css(target).lineHeight,
        parentWritingMode: css(parent).writingMode, parentOrientation: css(parent).textOrientation,
        childWritingMode: css(target).writingMode, childOrientation: css(target).textOrientation, vertical,
        rootLineHeight: css(root).lineHeight,
        progress: animation ? animation.effect.getComputedTiming().progress : null,
        playState: animation ? animation.playState : null,
        keyframeCount: animation ? animation.effect.getKeyframes().length : null,
      });
    };
    take("first");
    await variationSettled(win);
    take("settled");
  }
  checkVariationRows(rows, unit, mode);
}

async function variationRootCase(t, unit) {
  const frame = await variationFrame(t, '<div class="metric" id="initial-metric"></div>', `
    html { font: initial; line-height: initial; font-variation-settings: normal; }
    #initial-metric { width: 100${unit}; }
  `);
  const win = frame.contentWindow;
  const doc = frame.contentDocument;
  const root = doc.documentElement;
  const initial = doc.getElementById("initial-metric").getBoundingClientRect().width / 100;
  const initialFont = win.getComputedStyle(root).fontSize;
  const rows = [];
  window.variationBaseObservations.push({ mode: "root", unit, initial, initialFont, rows });
  for (const size of [40, 60]) {
    root.style.fontFamily = "monospace";
    root.style.fontSize = `${size}px`;
    root.style.lineHeight = `${size + 39}px`;
    const take = timing => {
      const raw = win.getComputedStyle(root).fontVariationSettings;
      rows.push({ size, timing, raw, actual: variationNumber(raw), fontSize: win.getComputedStyle(root).fontSize });
    };
    const value = `"wdth" calc(1${unit} / 1px)`;
    root.style.fontVariationSettings = value;
    const admitted = win.CSS.supports("font-variation-settings", value) && root.style.fontVariationSettings !== "";
    take("first");
    await variationSettled(win);
    take("settled");
    assert_true(admitted, `${unit}: root typed arithmetic admitted`);
  }
  assert_true(Number.isFinite(initial) && initial > 0, "Initial font metric is finite and nonzero");
  for (const row of rows) {
    assert_equals(row.fontSize, `${row.size}px`, "Root own size differs from initial calibration");
    assert_approx_equals(row.actual, initial, 0.03,
      `${unit}/${row.size}/${row.timing}: root self-reference uses initial font/line-height; raw=${row.raw}`);
  }
}

function runVariationBaseTests(mode) {
  for (const unit of variationUnits) {
    promise_test(t => mode === "root" ? variationRootCase(t, unit) : variationChildCase(t, unit, mode),
      `font-variation-settings ${mode}: calc(1${unit} / 1px) metric base`);
  }
}
