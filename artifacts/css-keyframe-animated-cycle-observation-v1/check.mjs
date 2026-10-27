import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { spawnSync } from "node:child_process";

const html = fs.readFileSync(new URL("observe.html", import.meta.url), "utf8");
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length, 1);
assert.equal(/<script[^>]+src=|<link/i.test(html), false);
const source = scripts[0][1];
const syntax = spawnSync(process.execPath, ["--check"], { input: source, encoding: "utf8" });
assert.equal(syntax.status, 0, syntax.stderr);
const node = { addEventListener() {} };
const context = vm.createContext({
  document: { querySelector() { return node; } }, window: {},
  Animation() { throw Error("Browser execution forbidden in inert check"); },
  KeyframeEffect() { throw Error("Browser execution forbidden in inert check"); },
});
vm.runInContext(source, context);
const inspect = expression => vm.runInContext(expression, context);
const roster = JSON.parse(inspect("JSON.stringify(roster)"));
assert.equal(roster.length, 52);
assert.equal(new Set(roster.map(item => item.id)).size, 52);
assert.equal(inspect("scenarios.reduce((n, s) => n + s.phases.reduce((m, p) => m + p.times.length, 0), 0) * 4"), 108);
assert.equal(inspect("scenarios.reduce((n, s) => n + s.phases.filter(p => !p.expected).reduce((m, p) => m + p.times.length, 0), 0) * 4"), 32);
assert.equal(inspect("numeric({x: ''}, {x: 0})"), false);
assert.equal(inspect("numeric({x: 'red'}, {x: 10})"), false);
assert.equal(inspect("numeric({x: 'NaN'}, {x: 10})"), false);
assert.equal(inspect("numeric({x: '55'}, {x: 65})"), false);
assert.equal(inspect("numeric({x: '55.0'}, {x: 55})"), true);
const controls = JSON.parse(inspect("JSON.stringify(scenarios)"));
const defaults = new Map([["invalid-red", 10], ["missing-no-fallback", 10],
  ["missing-fallback", 30], ["wrong-type-fallback", 10]]);
for (const [name, endpoint] of defaults) {
  assert.deepEqual(controls.find(s => s.name === name).phases[0].expected,
    [[endpoint + (100 - endpoint) * 0.5, 200]]);
}
assert.deepEqual(controls.find(s => s.name === "acyclic-provider").phases[0].expected,
  [[(300 + 100) / 2, (200 + 400) / 2]]);
assert.deepEqual(controls.find(s => s.name === "literal-unselected").phases[0].expected,
  [[15, 250], [25, 350], [15, 250]]);
vm.runInContext(`
  function inertSample(spec, x, y, z) {
    result = { records: [], all_calibrations_pass: true };
    let reads = 0;
    globalThis.getComputedStyle = () => ({ getPropertyValue(name) {
      reads++;
      return { "--cycle-x": x, "--cycle-y": y, "--cycle-z": z }[name];
    } });
    const expectedFrames = { x: frames("x", spec.x), y: frames("y", spec.y) };
    const animations = Object.fromEntries(["x", "y"].map(key => [key, {
      currentTime: null, playState: "paused", pending: false,
      effect: { composite: "replace", getComputedTiming() {
        if (reads !== 6) throw Error("Timing read before both value reads");
        return { duration: 1000, fill: "both", easing: "linear", currentIteration: 0, progress: 0.5 };
      }, getKeyframes() {
        return expectedFrames[key].map(frame => ({ ...frame, computedOffset: frame.offset }));
      } },
    }]));
    sample({}, animations, expectedFrames, spec, 0,
      { id: "inert-only", creation: ["y", "x"], read_order: ["y", "x"] });
    return result.records[0];
  }
`, context);
for (const [x, y] of [["55", "110"], ["10", "20"], ["red", "999"]]) {
  const record = JSON.parse(inspect(`JSON.stringify(inertSample(mutual(), ${JSON.stringify(x)}, ${JSON.stringify(y)}, "4"))`));
  assert.equal(record.kind, "observation");
  assert.equal(record.calibration_pass, true);
  assert.equal(record.cyclic_numeric_oracle, null);
  assert.equal(record.cyclic_values_judged, false);
  assert.deepEqual(record.expected_calibration, { z: 4 });
}
assert.equal(inspect('inertSample(mutual(), "55", "110", "99").calibration_pass'), false);
assert.equal(inspect('inertSample(acyclic("control"), "125", "300", "4").calibration_pass'), false);
assert.equal(inspect('inertSample(acyclic("control"), "200", "300", "4").calibration_pass'), true);
assert.equal(inspect('retained([{computedOffset: 0, "--cycle-x": "10"}], frames("x", ["10", "20"]))'), false);
fs.writeFileSync(new URL("ROSTER.json", import.meta.url), JSON.stringify(roster, null, 2) + "\n");
console.log(JSON.stringify({ status: "INERT_CHECK_PASS", trials: 52, expected_samples: 108,
  cyclic_observation_samples: 32, numeric_control_samples: 76,
  syntax: "node --check", registration: "source reviewed: three number/non-inherited/fixed initial registrations",
  browser_executed: false, limitations: "VM stubs test record classification and pure controls, not CSS or animation behavior" }, null, 2));
