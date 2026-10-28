const fs = require("fs");
const path = require("path");
const vm = require("vm");
const here = __dirname;
const root = path.resolve(here, "../..");
const read = name => JSON.parse(fs.readFileSync(path.join(here, name), "utf8"));
function check(value, message) { if (!value) throw new Error(message); }
function enumerate(file, extra = {}) {
  const html = fs.readFileSync(file, "utf8");
  const names = [];
  const context = vm.createContext({test:(callback,name) => names.push(name), ...extra});
  for (const match of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) {
    new vm.Script(match[1]);
    vm.runInContext(match[1], context);
  }
  check(names.length === new Set(names).size, "unique names");
  return {names,context};
}
const original = enumerate(path.join(here, "historical/prior58.html"));
const aPath = fs.readFileSync(path.join(here, "NEW-BREADTH-WPT-PATH.txt"), "utf8").trim();
const bPath = fs.readFileSync(path.join(here, "HELD-WPT-PATH.txt"), "utf8").trim();
const a = enumerate(path.join(here, "candidate", aPath));
const b = enumerate(path.join(here, "held", bPath));
check(original.names.length === 58 && a.names.length === 104 && b.names.length === 16, "partition counts");
for (const name of original.names) check(Number(a.names.includes(name)) + Number(b.names.includes(name)) === 1, "preserved old identity " + name);
check(!a.names.some(name => b.names.includes(name)), "disjoint A/B identities");
check(JSON.stringify(JSON.parse(vm.runInContext("JSON.stringify(breadthCases)",a.context))) === JSON.stringify(read("A-BREADTH-CASES.json")), "A breadth data");
check(JSON.stringify(JSON.parse(vm.runInContext("JSON.stringify(breadthCases)",b.context))) === JSON.stringify(read("B-BREADTH-CASES.json")), "B breadth data");
const pending = enumerate(path.join(here,"context/registered-numeric-relative-units.html"));
check(pending.names.length === 76, "historical pending76");
const regressions = {};
for (const name of read("ADDED-REGRESSION-PAGES.json")) {
  const style = {};
  const extra = {CSS:{registerProperty:()=>{}}, add_result_callback:()=>{},ref:{style},target:{style,parentElement:{}},document:{documentElement:{style}},getComputedStyle:()=>({marginBottom:"0px"})};
  regressions[name] = enumerate(path.join(here,"capture/testing/web-platform/tests",name),extra).names;
}
const url = value => "/" + value.replace("testing/web-platform/tests/", "");
console.log(JSON.stringify({target_pages:{[url(aPath)]:a.names}, held_pages:{[url(bPath)]:b.names},
  original58_names:original.names, original58_names_retained_once:true,
  target_count:104,held_count:16,total_partition_count:120,
  added_regression_names:regressions,added_regression_count:Object.values(regressions).reduce((n,x)=>n+x.length,0),
  pending76_names:pending.names,enumeration_only:true,callbacks_executed:false,browser_executed:false},null,2));
