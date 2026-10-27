const fs = require("fs");
const vm = require("vm");
const path = require("path");
const here = __dirname;
const old = path.join(here, "../css-attr-raw-nested-repair-v1");
const newPath = fs.readFileSync(path.join(here, "NEW-WPT-PATH.txt"), "utf8").trim();
function check(condition, message) { if (!condition) throw new Error(message); }
function enumerate(directory) {
  const source = fs.readFileSync(path.join(directory, "candidate", newPath), "utf8");
  const script = [...source.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join("\n");
  new vm.Script(script);
  const names = [];
  const context = vm.createContext({test: (callback, name) => names.push(name)});
  vm.runInContext(script, context);
  return {source, names, cases: JSON.parse(vm.runInContext("JSON.stringify(cases)", context))};
}
const before = enumerate(old), after = enumerate(here);
check(after.names.length === 36 && new Set(after.names).size === 36, "36 unique names");
check(JSON.stringify(before.cases) === JSON.stringify(after.cases.slice(0, 26)), "original26 data unchanged");
check(before.names.every(n => after.names.includes(n)), "original29 names preserved");
check(before.source.split("function makeTarget")[1] === after.source.split("function makeTarget")[1], "helper and mutations unchanged");
const cyclePath = "testing/web-platform/tests/css/css-values/attr-cycle.html";
const cycleBefore = fs.readFileSync(path.join(old, "candidate", cyclePath), "utf8");
const cycleAfter = fs.readFileSync(path.join(here, "candidate", cyclePath), "utf8");
for (const match of cycleAfter.matchAll(/<script>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
const calls = value => value.match(/^  test_attr_(?:no_cycle|cycle)\(.*$/gm);
const priorCalls = calls(cycleBefore), nextCalls = calls(cycleAfter);
check(priorCalls.length === 37 && nextCalls.length === 37, "37 original helper calls");
const changes = nextCalls.flatMap((line, i) => line === priorCalls[i] ? [] : [{before:priorCalls[i],after:line}]);
check(changes.length === 1 && changes[0].before.includes("'attr(data-foo', 'abc'"), "only EOF oracle changed versus v1");
console.log(JSON.stringify({javascript_syntax:true, new_test_count:36, fixed_case_count:33,
  original29_names_preserved:true, original26_data_unchanged:true, helpers_and_mutations_unchanged:true,
  new_test_names:after.names, existing_test_call_count:37, additional_explicit_oracle_changes:changes,
  browser_executed:false}, null, 2));
