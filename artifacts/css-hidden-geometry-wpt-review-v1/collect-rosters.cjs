const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const counts = {
  "hidden-flex-item-measuring-reflow.html": 48,
  "hidden-flex-fixed-size-query.html": 32,
  "hidden-flex-skipped-positions.html": 44,
};
const rosters = {};
for (const [file, count] of Object.entries(counts)) {
  const names = [];
  const html = fs.readFileSync(path.join(__dirname, file), "utf8");
  const context = vm.createContext({
    test: (callback, name) => names.push(name),
    promise_test: (callback, name) => names.push(name),
  });
  for (const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) {
    if (match[1].trim()) new vm.Script(match[1], {filename: file}).runInContext(context);
  }
  if (names.length !== count || new Set(names).size !== count) throw new Error(file);
  rosters[file] = names;
}
fs.writeFileSync(path.join(__dirname, "EXPECTED-ROSTERS.json"), JSON.stringify(rosters, null, 2) + "\n");
for (const [file, names] of Object.entries(rosters)) {
  fs.writeFileSync(path.join(__dirname, file + ".roster.json"), JSON.stringify(names, null, 2) + "\n");
}
console.log(JSON.stringify(counts));
