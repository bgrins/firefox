const fs = require("fs"), vm = require("vm"), path = require("path");
const html = fs.readFileSync(path.join(__dirname, "random-typed-parse-rollback.html"), "utf8");
const names = []; const context = vm.createContext({test: (_, name) => names.push(name)});
for (const m of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) vm.runInContext(m[1], context);
if(names.length !== 19 || new Set(names).size !== 19) throw Error("cardinality");
fs.writeFileSync(path.join(__dirname,"ENUMERATION.json"),JSON.stringify({test_callbacks_executed:false,names},null,2)+"\n");
console.log("19 unique names; callbacks not executed");
