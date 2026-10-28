const fs = require("fs"), vm = require("vm"), path = require("path");
const here = __dirname, policy = JSON.parse(fs.readFileSync(path.join(here, "POLICY.json")));
const result = {};
for (const page of Object.keys(policy.tests)) {
  const names = [];
  const register = (_, name) => { if (typeof name !== "string") throw Error("unnamed"); names.push(name); };
  const ctx = vm.createContext({test: register, promise_test: register, lh: {offsetHeight: 0}});
  const html = fs.readFileSync(path.join(here, "capture/testing/web-platform/tests", page), "utf8");
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
    const src = /src=["']([^"']+)["']/.exec(match[1]);
    if (src) {
      if (src[1].startsWith("/resources/")) continue;
      const name = src[1].startsWith("/") ? src[1].slice(1) : path.join(path.dirname(page.slice(1)), src[1]);
      const file = path.join(here, "capture/testing/web-platform/tests", name);
      vm.runInContext(fs.readFileSync(file, "utf8"), ctx, {filename: name});
    } else vm.runInContext(match[2], ctx, {filename: page});
  }
  if (new Set(names).size !== names.length) throw Error("duplicate");
  result[page] = names;
}
fs.writeFileSync(path.join(here, "ENUMERATED-SUBTESTS.json"), JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify(Object.fromEntries(Object.entries(result).map(([p, n]) => [p, n.length]))));
