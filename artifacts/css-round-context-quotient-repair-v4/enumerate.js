const fs = require("fs");
const vm = require("vm");
const names = [];
const html = fs.readFileSync(process.argv[2], "utf8");
const context = vm.createContext({test: (callback, name) => names.push(name)});
for (const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
  vm.runInContext(match[1], context);
}
process.stdout.write(JSON.stringify(names));
