"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const source = fs.readFileSync(path.join(__dirname, "observe.js"), "utf8");
const context = {window: {}, navigator: {userAgent: "synthetic"}};
vm.createContext(context);
vm.runInContext(source.slice(0, source.lastIndexOf("(async () => {")), context);
const modes = ["tainted-attr", "untainted-attr", "literal-attr", "direct-var"];
function row(mode) {
  const ordinary = mode === "untainted-attr" ? "horizontal-tb" : "vertical-rl";
  const sink = mode === "untainted-attr" ? "horizontal-tb" : "vertical-lr";
  return {mode, error: null, stage: "complete",
    before: {variable: ordinary, sink},
    active: {variable: mode === "literal-attr" ? ordinary : "horizontal-tb", sink, effectSame: true,
      timing: {duration: 2000, computedDuration: 2000, time: 750, progress: .375, state: "paused"}},
    activeMembership: {count: 1, sameAnimation: true, sameEffect: true},
    cancelled: {variable: ordinary, sink, effectSame: true, timing: {time: null, state: "idle"}},
    cancelMembership: {count: 0},
    activeSamples: Array.from({length: 4}, () => ({sink})),
    cancelSamples: Array.from({length: 4}, () => ({sink}))};
}
const calibrated = value => context.calibration(value).every(check => check.passed);
for (const mode of modes) {
  assert.ok(calibrated(row(mode)));
  assert.ok(context.activeExpectation(row(mode)).matches);
}
for (const mode of ["tainted-attr", "direct-var"]) {
  const value = row(mode);
  value.before.sink = value.cancelled.sink = "arbitrary";
  value.cancelSamples.forEach(v => v.sink = "arbitrary");
  assert.ok(calibrated(value));
  assert.ok(context.activeExpectation(value).matches);
  for (const sink of ["horizontal-tb", "vertical-rl"]) {
    value.active.sink = sink;
    assert.ok(calibrated(value));
    assert.equal(context.activeExpectation(value).matches, false);
  }
}
for (const mutate of [
  v => v.active.timing.time = 751,
  v => v.active.timing.progress = null,
  v => v.activeMembership.sameAnimation = false,
  v => v.cancelMembership.count = 1,
  v => v.active.variable = "vertical-rl",
  v => v.error = {name: "Error", message: "setup", stack: ""},
]) {
  const value = row("tainted-attr"); mutate(value); assert.equal(calibrated(value), false);
}
const unsupported = row("literal-attr");
unsupported.active.sink = "vertical-rl";
assert.equal(calibrated(unsupported), false);
const unparsed = row("untainted-attr");
unparsed.active.sink = "vertical-rl";
assert.ok(calibrated(unparsed));
assert.equal(context.activeExpectation(unparsed).matches, false);
assert.equal(context.activeExpectation({active: null}), null);
assert.ok(source.indexOf("await animation.ready") < source.indexOf("animation.currentTime = 750"));
assert.ok(source.indexOf("await sample(row.activeSamples)") < source.indexOf("row.active = details()"));
assert.ok(source.indexOf("await sample(row.cancelSamples)") < source.indexOf("row.cancelled = details()"));
console.log("Four positives; outside-active policy neutrality; four wrong active expectations retained; eight calibration/control negatives and partial expectation checked; no browser.");
