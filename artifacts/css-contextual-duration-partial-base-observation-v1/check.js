"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const source = fs.readFileSync(path.join(__dirname, "observe.js"), "utf8");
let registered = 0;
const context = vm.createContext({window: {addEventListener(type) {
  assert.equal(type, "load");
  registered++;
}}});
vm.runInContext(source, context);
assert.equal(registered, 1);
const evaluate = expression => JSON.parse(JSON.stringify(vm.runInContext(expression, context)));
assert.equal(evaluate("cases.length"), 4);
function sample(mode, finalFont, duration) {
  const detail = value => ({opacity: 750 / value, font: "32px", cssDuration: `2s, ${value / 1000}s`,
    timings: [{duration: 2000, time: 750, state: "paused"},
      {duration: value, progress: 750 / value, time: 750, state: "paused"}]});
  return {mode, finalFont, error: null, initial: detail(1000),
    samples: ["first-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"].map(
      phase => ({phase, opacity: 750 / duration})),
    beforeMembership: detail(duration), afterMembership: detail(duration),
    membership: {count: 2, held: [{animation: true, effect: true}, {animation: true, effect: true}]}};
}
const checks = observation => {
  context.input = observation;
  return evaluate("referenceChecks(input)");
};
for (const font of [24, 32]) {
  assert.ok(checks(sample("literal", font, font / 16 * 1000)).every(check => check.passed));
}
for (const duration of [1000, 1500, 2000]) {
  assert.ok(checks(sample("contextual", 24, duration)).every(check => check.passed));
}
const unknown = sample("contextual", 24, 1000);
unknown.beforeMembership.timings[1].duration = null;
unknown.beforeMembership.timings[1].progress = null;
unknown.beforeMembership.opacity = null;
assert.ok(checks(unknown).every(check => check.passed));
let negatives = 0;
for (const mutate of [
  value => { value.samples.pop(); },
  value => { value.samples[0].phase = "rescue"; },
  value => { value.membership.held.pop(); },
  value => { value.membership.held[1].effect = false; },
  value => { value.beforeMembership.timings[1].duration = 2000; },
  value => { value.samples[0].opacity = null; },
  value => { value.initial.timings[1].time = 0; },
]) {
  const value = sample("literal", 24, 1500);
  mutate(value);
  assert.ok(checks(value).some(check => !check.passed));
  negatives++;
}
assert.deepEqual(checks({error: {message: "acquisition failed"}}), [{name: "collection", passed: false}]);
const intervention = source.split('target.classList.add("final");')[1].split('result.beforeMembership = details();')[0];
assert.equal((intervention.match(/getComputedStyle\(/g) || []).length, 1);
assert.ok(!/getTiming|getComputedTiming|getAnimations|details\(\)/.test(intervention));
assert.ok(!/fetch\(|XMLHttpRequest|WebSocket|updateTiming\(|assert_/.test(source));
assert.ok(source.includes("result.contextualTimingVerdict = null"));
console.log(JSON.stringify({literal_positives: 2, contextual_policy_variants_retained: 4,
  reference_negatives: negatives, acquisition_error_preserved: true,
  passive_interval_opacity_only: true, DOM_or_browser_executed: false}));
