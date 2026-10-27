const fs = require("fs");
const path = require("path");
const vm = require("vm");
const here = __dirname;
const root = path.resolve(here, "../..");
function check(value, message) { if (!value) throw new Error(message); }
function enumerate(file, extra = {}) {
  const html = fs.readFileSync(file, "utf8");
  const names = [];
  const context = vm.createContext({test: (callback, name) => names.push(name), ...extra});
  for (const match of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) {
    new vm.Script(match[1]);
    vm.runInContext(match[1], context);
  }
  check(names.length === new Set(names).size && names.every(name => typeof name === "string"), "unique named tests");
  return {names, context};
}
const targetPath = fs.readFileSync(path.join(here, "NEW-WPT-PATH.txt"), "utf8").trim();
const target = enumerate(path.join(here, "candidate", targetPath));
check(target.names.length === 58, "58 target tests");
const data = JSON.parse(vm.runInContext("JSON.stringify(cases)", target.context));
const prior = JSON.parse(fs.readFileSync(path.join(root, "artifacts/css-registered-number-fallback-branch-v1/probe/CASES.json")));
for (const item of prior) {
  const current = data.find(row => row.id === "probe: " + item.id);
  check(current.css === item.css && current.parent === (item.parent || "") && current.expected["font-size"] === item.expected, "exact prior row " + item.id);
}
const normative = JSON.parse(fs.readFileSync(path.join(root, "artifacts/css-registered-number-cycle-normative-trace-v1/ORACLES.json")));
for (const item of normative.assertion_cases) {
  const current = data.find(row => row.id === "normative: " + item.id);
  check(JSON.stringify(current.expected) === JSON.stringify(item.expected), "normative expected " + item.id);
  check(JSON.stringify(current.mutation) === JSON.stringify(item.mutation), "normative mutation " + item.id);
  if (item.mutation) check(current.fontSize === "20px", "initial fixed font " + item.id);
  check(current.css === Object.entries(item.declarations).map(([name, value]) => name + ":" + value).join(";"), "normative declarations " + item.id);
}
const regressions = {};
const added = JSON.parse(fs.readFileSync(path.join(here, "ADDED-REGRESSION-PAGES.json")));
for (const name of added) {
  const style = {};
  const extra = {CSS: {registerProperty: () => {}}, add_result_callback: () => {},
    ref: {style}, target: {style, parentElement: {}},
    document: {documentElement: {style}}, getComputedStyle: () => ({marginBottom: "0px"})};
  regressions[name] = enumerate(path.join(here, "capture/testing/web-platform/tests", name), extra).names;
}
for (const match of fs.readFileSync(path.join(here, "observation-only.html"), "utf8").matchAll(/<script>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
console.log(JSON.stringify({target_names:target.names, added_regression_names:regressions,
  target_count:target.names.length, added_regression_count:Object.values(regressions).reduce((n,x) => n+x.length,0),
  prior14_exact:true, normative8_exact:true, observation_only_not_executed:true,
  enumeration_only:true, callbacks_executed:false, browser_executed:false}, null, 2));
