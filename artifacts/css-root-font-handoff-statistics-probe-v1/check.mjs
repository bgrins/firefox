import fs from "node:fs";
import vm from "node:vm";
import assert from "node:assert/strict";
const dir = new URL(".", import.meta.url);
const sources = Object.fromEntries(["setup", "action", "cleanup"].map(name =>
  [name, fs.readFileSync(new URL(`${name}.js`, dir), "utf8")]));
for (const source of Object.values(sources)) new vm.Script(`(${source})`);
const original = fs.readFileSync(new URL("../css-root-font-handoff-cost-probe-v1/probe.js", dir), "utf8");
const body = original.slice(original.indexOf("      const loaded = "),
  original.indexOf("      for (let index = ")).trimEnd().split("\n").map(line => line.slice(2)).join("\n");
assert.ok(sources.setup.includes(body));
const events = [];
const target = {};
const state = { ready: true, acted: false, target,
  rootAnimation: { set currentTime(value) { events.push(["seek", value]); } },
  win: {
    performance: { now() { events.push("clock"); return events.length; } },
    getComputedStyle(element) { assert.equal(element, target); events.push("target getter"); return { fontSize: "64px" }; },
  },
};
const window = { __cssFontHandoffStatisticsV1: state };
const action = vm.runInNewContext(`(${sources.action})`, { window });
const result = action();
assert.deepEqual(events, ["clock", ["seek", 1000], "target getter", "clock"]);
assert.equal(result.valid, true);
assert.equal(result.value, "64px");
assert.equal(state.result, result);
assert.throws(() => action(), /unused ready setup/);
assert.equal(events.length, 4);
delete window.__cssFontHandoffStatisticsV1;
assert.throws(() => action(), /unused ready setup/);
const staleEvents = [];
window.__cssFontHandoffStatisticsV1 = { ...state, acted: false,
  win: { performance: { now() { return 0; } },
    getComputedStyle() { staleEvents.push("getter"); return { fontSize: "32px" }; } } };
assert.equal(action().valid, false);
assert.equal(staleEvents.length, 1);
console.log(JSON.stringify({ syntax: 3, setupBodyEqualsOriginal: true,
  exactActionOrder: true, resultRetained: true,
  rejectingControls: ["repeat action", "missing setup", "stale computed value"],
  browserRun: false, scope: "VM action ordering with explicit DOM/animation doubles; setup grammar and original body correspondence only" }, null, 2));
