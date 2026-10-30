"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const source = fs.readFileSync(path.join(__dirname, "observe.js"), "utf8");
const context = {window: {}, navigator: {userAgent: "synthetic"}};
vm.createContext(context);
vm.runInContext(source.slice(0, source.lastIndexOf("(async () => {")), context);
const row = {
  mode: "waapi", error: null, stage: "complete",
  before: {variable: "vertical-rl", sink: "arbitrary"},
  active: {variable: "horizontal-tb", sink: "arbitrary", effectSame: true,
    timing: {duration: 2000, computedDuration: 2000, time: 750, progress: .375, state: "paused"}},
  activeMembership: {count: 1, sameAnimation: true, sameEffect: true},
  cancelled: {variable: "vertical-rl", sink: "arbitrary", effectSame: true,
    timing: {time: null, state: "idle"}},
  cancelMembership: {count: 0},
  activeSamples: Array(4).fill({sink: "arbitrary"}),
  cancelSamples: Array(4).fill({sink: "arbitrary"}),
};
const passed = value => context.calibration(value).every(check => check.passed);
for (const mode of ["waapi", "css"]) {
  for (const sink of ["horizontal-tb", "vertical-lr", "vertical-rl", "unexpected"]) {
    const value = structuredClone(row);
    value.mode = mode;
    value.before.sink = value.active.sink = value.cancelled.sink = sink;
    assert.ok(passed(value));
  }
}
for (const mutate of [
  value => value.active.timing.time = 751,
  value => value.active.timing.progress = null,
  value => value.activeMembership.sameEffect = false,
  value => value.cancelMembership.count = 1,
  value => value.cancelled.variable = "horizontal-tb",
  value => value.error = {name: "Error", message: "setup", stack: ""},
]) {
  const value = structuredClone(row);
  mutate(value);
  assert.equal(passed(value), false);
}
const literal = structuredClone(row);
literal.mode = "literal";
literal.before.sink = literal.active.sink = literal.cancelled.sink = "vertical-lr";
literal.activeSamples = literal.cancelSamples = Array(4).fill({sink: "vertical-lr"});
assert.ok(passed(literal));
literal.active.sink = "horizontal-tb";
assert.equal(passed(literal), false);
console.log("Eight policy-neutral sink cases, literal calibration, and seven calibration negatives passed; no browser.");
