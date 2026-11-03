"use strict";

const minimumMode = document.body.dataset.minimum;
const observations = window.minimumFontSizeObservations = [];
const text = "0000000000000000";
const forms = {omitted: "", explicit: "font-size:16px", inherit: "font-size:inherit",
  percentage: "font-size:100%", calc: "font-size:calc(100% + 0px)"};
const phases = [
  {family: "monospace", lang: "en", zoom: 1},
  {family: "serif", lang: "en", zoom: 1},
  {family: "monospace", lang: "ja", zoom: 1.25},
  {family: "monospace", lang: "en", zoom: 1}
];

function retain(row) {
  observations.push(row);
  document.getElementById("observations").textContent = JSON.stringify(observations);
}

async function fixture(t) {
  const frame = document.createElement("iframe");
  frame.srcdoc = '<!doctype html><meta charset="utf-8"><style></style><div id="parent"><span id="target" data-length="var(--len)"></span><span id="ordinary"></span><span id="pixels"></span><span id="large"></span></div>';
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  t.add_cleanup(() => frame.remove());
  await loaded;
  const doc = frame.contentDocument;
  for (const node of doc.querySelectorAll("span")) node.textContent = text;
  return {win: frame.contentWindow, doc};
}

function sheet(form, phase, extra = "") {
  return `#parent { font: medium serif; }
    span { display:inline-block; white-space:pre; padding:0; border:0;
      font-family:${phase.family}; ${form}; zoom:${phase.zoom};
      font-weight:400; font-style:normal; font-stretch:normal;
      font-size-adjust:none; font-kerning:none; font-optical-sizing:none;
      font-variant-ligatures:none; letter-spacing:0; line-height:normal; --metric:1ch; }
    #target { --len:1em; appearance:attr(data-length type(<length>),auto); }
    #ordinary { appearance:none; }
    #pixels { appearance:none; }
    #large { font-size:48px; appearance:none; } ${extra}`;
}

function measure(win, node) {
  const style = win.getComputedStyle(node);
  const rect = node.getBoundingClientRect();
  return {fontSize:style.fontSize, family:style.fontFamily, appearance:style.appearance,
    width:rect.width, height:rect.height, zoom:style.zoom,
    len:style.getPropertyValue("--len").trim(), metric:style.getPropertyValue("--metric").trim()};
}

for (const lang of ["en", "ja"]) {
  promise_test(async t => {
    const {win, doc} = await fixture(t);
    doc.getElementById("parent").lang = lang;
    const expected = minimumMode === "on" ? (lang === "ja" ? 32 : 24) : 8;
    doc.querySelector("style").textContent = sheet("font-size:8px", {family:"monospace", zoom:1},
      `#target {--len:initial;--metric:initial;appearance:none} #pixels {font-size:${expected}px}`);
    const small = measure(win, doc.getElementById("ordinary"));
    const expectedSize = measure(win, doc.getElementById("pixels"));
    const large = measure(win, doc.getElementById("large"));
    const row = {minimumMode, calibration:lang, expected, small, expectedSize, large};
    retain(row);
    const details = JSON.stringify(row);
    assert_equals(small.fontSize, "8px", details);
    assert_approx_equals(small.width, expectedSize.width, 0.1, details);
    assert_greater_than(large.width, small.width * 1.25, details);
    if (minimumMode === "off") assert_greater_than(large.width, small.width * 4, details);
  }, `Minimum preference geometry calibration ${lang} (${minimumMode})`);
}

for (const [name, form] of Object.entries(forms)) {
  promise_test(async t => {
    const {win, doc} = await fixture(t);
    assert_true(win.CSS.supports("appearance", "attr(data-length type(<length>),auto)"));
    win.CSS.registerProperty({name:"--len", syntax:"<length>", inherits:false, initialValue:"0px"});
    win.CSS.registerProperty({name:"--metric", syntax:"<length>", inherits:false, initialValue:"0px"});
    const row = {minimumMode, name, phases:[]};
    for (const phase of phases) {
      doc.getElementById("parent").lang = phase.lang;
      const style = doc.querySelector("style");
      style.textContent = sheet(form, phase);
      const firstLen = win.getComputedStyle(doc.getElementById("target")).getPropertyValue("--len").trim();
      const first = measure(win, doc.getElementById("target"));
      const ordinary = measure(win, doc.getElementById("ordinary"));
      style.textContent += `#pixels {font-size:${ordinary.fontSize};}`;
      const pixels = measure(win, doc.getElementById("pixels"));
      const samples = [];
      for (let i = 0; i < 3; ++i) {
        await new Promise(resolve => win.requestAnimationFrame(resolve));
        samples.push(measure(win, doc.getElementById("target")));
      }
      row.phases.push({...phase, firstLen, first, ordinary, pixels, samples,
        large:measure(win, doc.getElementById("large"))});
    }
    retain(row);
    const details = JSON.stringify(row);
    for (const phase of row.phases) {
      assert_greater_than(phase.ordinary.width, 0, details);
      assert_equals(phase.firstLen, phase.ordinary.fontSize, details);
      assert_approx_equals(phase.ordinary.width, phase.pixels.width, 0.1, details);
      for (const sample of [phase.first, ...phase.samples]) {
        assert_equals(sample.fontSize, phase.ordinary.fontSize, details);
        assert_equals(sample.appearance, "none", details);
        assert_approx_equals(sample.width, phase.ordinary.width, 0.1, details);
        assert_approx_equals(sample.height, phase.ordinary.height, 0.1, details);
        assert_equals(sample.metric, phase.ordinary.metric, details);
        assert_equals(sample.metric, phase.pixels.metric, details);
      }
    }
  }, `Used-size preservation with ${name} font size (${minimumMode})`);
}

