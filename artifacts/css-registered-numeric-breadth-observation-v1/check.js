const fs = require("fs");
const vm = require("vm");
const path = require("path");
const here = __dirname;
const html = fs.readFileSync(path.join(here, "observation-only.html"), "utf8");
for (const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
new vm.Script(fs.readFileSync(path.join(here, "report.js"), "utf8"));
const cases = JSON.parse(fs.readFileSync(path.join(here, "CASES.json"), "utf8"));
const embedded = JSON.parse(html.match(/const cases = (.*);\nconst rows = \[\];/)[1]);
if (JSON.stringify(cases) !== JSON.stringify(embedded)) throw new Error("Embedded case data drift");
if (cases.length !== 60 || new Set(cases.map(item => item.id)).size !== 60) throw new Error("Case identities");
const names = cases.flatMap(item => item.registrations.map(registration => registration.name));
if (names.length !== new Set(names).size) throw new Error("Registration identity collision");
for (const item of cases) {
  if (!item.requiresCalibration.every(id => cases.some(other => other.id === id))) throw new Error("Missing calibration");
  if (item.kind.startsWith("provider") && item.registrations[1].initialValue !== "7") throw new Error("Consumer initial calibration");
  if (item.mode === "math" && (item.fontSize !== "20px" || JSON.stringify(item.snapshots.map(step => step.set["font-size"])) !== '["20px","30px"]')) throw new Error("Noncyclic math setup");
}
console.log(JSON.stringify({javascript_syntax:true, embedded_cases_exact:true, cases:cases.length,
  snapshots:cases.reduce((sum,item) => sum+item.snapshots.length,0), registrations:names.length,
  browser_executed:false, probe_script_executed:false}, null, 2));
