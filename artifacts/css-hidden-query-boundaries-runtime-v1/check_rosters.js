"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const here = __dirname;
const config = JSON.parse(fs.readFileSync(path.join(here, "CONFIG.json"), "utf8"));
const rows = [];
for (const [target, source] of Object.entries(config.install)) {
  const names = [];
  const context = vm.createContext({test: (_, name) => names.push(name), promise_test: (_, name) => names.push(name), window: {}});
  const html = fs.readFileSync(path.join(here, source), "utf8");
  for (const match of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) {
    if (match[1].trim()) vm.runInContext(match[1], context, {timeout: 1000});
  }
  const key = "/" + target.replace("testing/web-platform/tests/", "");
  if (JSON.stringify(names) !== JSON.stringify(config.expected_subtests[key])) throw new Error("Roster mismatch " + key);
  rows.push({test: key, names});
}
console.log(JSON.stringify({status: "PASS_REGISTRATION_ONLY", files: rows.length, subtests: rows.reduce((sum, row) => sum + row.names.length, 0), rows}, null, 2));
