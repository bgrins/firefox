"use strict";
const fs = require("fs");
const vm = require("vm");
const path = require("path");
const assert = require("assert/strict");
const source = fs.readFileSync(path.join(__dirname, "probe.js"), "utf8");
const context = vm.createContext({});
vm.runInContext(source, context);
const evaluate = expression => JSON.parse(JSON.stringify(vm.runInContext(expression, context)));
assert.equal(evaluate("summarize([])"), null);
assert.deepEqual(evaluate("summarize([3])"), {count: 1, min: 3, p10: 3, median: 3,
  p90: 3, p95: 3, max: 3, mean: 3});
const distribution = evaluate("summarize([9, 1, 7, 3])");
assert.equal(distribution.median, 5);
assert.equal(distribution.mean, 5);
assert.equal(distribution.p90, 8.4);
const input = {label: "original", count: "200", iterations: "50", warmup: "10",
  rounds: "3", order: "outline", mask: "yes"};
context.input = input;
assert.equal(evaluate("readConfig(input)").count, 200);
let negatives = 0;
for (const change of [{count: 0}, {count: 3001}, {iterations: 1.5}, {warmup: -1},
  {rounds: 11}, {count: "NaN"}, {order: "bad"}, {mask: "bad"},
  {count: 3000, iterations: 500, warmup: 100, rounds: 10}]) {
  context.input = {...input, ...change};
  assert.throws(() => vm.runInContext("readConfig(input)", context));
  negatives++;
}
const timed = source.split("const start = performance.now();")[1].split("const flushed = performance.now();")[0];
assert.equal((timed.match(/getComputedStyle\(/g) || []).length, 1);
assert.equal((timed.match(/classList.toggle\(/g) || []).length, 1);
assert.ok(!/getTiming|getAnimations|offsetWidth|requestAnimationFrame|await/.test(timed));
assert.ok(!/fetch\(|XMLHttpRequest|WebSocket/.test(source));
console.log(JSON.stringify({statistics_cases: 3, valid_config: 1, invalid_configs: negatives,
  explicit_timed_style_reads: 1, explicit_timed_mutations: 1,
  browser_or_DOM_execution: false, automatic_run: false}));
