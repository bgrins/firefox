"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const source = fs.readFileSync(path.join(__dirname, "report.js"), "utf8");
let callback;
const sent = [];
const context = {
  URLSearchParams, location: {search: "?run=example&nonce=secret"},
  window: {partialBaseObservations: {status: "running"}},
  setInterval(fn, ms) { assert.equal(ms, 50); callback = fn; return 1; },
  clearInterval(id) { assert.equal(id, 1); },
  async fetch(url, options) { sent.push({url, options}); return {ok: true}; },
};
vm.runInNewContext(source, context);
(async () => {
  await callback();
  assert.equal(sent.length, 0);
  context.window.partialBaseObservations = {status: "complete", value: NaN};
  await callback();
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, "/report/secret");
  assert.deepEqual(JSON.parse(sent[0].options.body), {run_id: "example", report: {status: "complete", value: {nonfinite: "NaN"}}});
  assert.ok(!/getComputedStyle|getAnimations|getTiming|currentTime|updateTiming/.test(source));
  console.log("Completion-only bridge and nonfinite roundtrip passed; no browser.");
})().catch(error => { console.error(error); process.exitCode = 1; });
