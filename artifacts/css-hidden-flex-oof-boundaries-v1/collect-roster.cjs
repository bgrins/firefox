const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const names = [];
const file = "hidden-oof-provider-boundaries.html";
const context = vm.createContext({test: (callback, name) => names.push(name)});
for (const match of fs.readFileSync(path.join(__dirname, file), "utf8").matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
  if (match[1].trim()) new vm.Script(match[1]).runInContext(context);
}
if (names.length !== 16 || new Set(names).size !== 16) throw new Error("roster mismatch");
fs.writeFileSync(path.join(__dirname, "EXPECTED-ROSTER.json"), JSON.stringify(names, null, 2) + "\n");
console.log(JSON.stringify({registrations: names.length, callbacksExecuted: false}));
