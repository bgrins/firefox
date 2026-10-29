const fs = require("fs");
const vm = require("vm");
const path = require("path");
const input = JSON.parse(fs.readFileSync(process.argv[2]));
const result = {};
for (const page of Object.keys(input.expected)) {
  const names = [];
  const iframe = {};
  const element = {};
  Object.defineProperty(element, "style", {
    get() { return this._style || (this._style = {}); },
    set(value) { this._style = {}; },
  });
  const document = {getElementById: () => element, querySelector: () => element};
  const context = vm.createContext({
    document, window: {}, iframe,
    promise_test: (_, name) => names.push(name),
    test: (_, name) => {
      if (typeof name !== "string") throw new Error("unnamed test");
      names.push(name);
    },
  });
  const html = fs.readFileSync(path.join(input.root, page), "utf8");
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
    const source = /src=["']([^"']+)["']/.exec(match[1]);
    if (!source) {
      vm.runInContext(match[2], context, {filename: page});
      continue;
    }
    if (source[1].startsWith("/resources/")) continue;
    const relative = source[1].startsWith("/") ? source[1] :
      path.posix.join(path.posix.dirname(page), source[1]);
    const file = path.join(input.root, relative);
    if (fs.existsSync(file)) {
      vm.runInContext(fs.readFileSync(file, "utf8"), context, {filename: relative});
    } else if (relative !== "/css/css-easing/support/util.js") {
      throw new Error("Missing resource " + relative);
    }
  }
  if (iframe.onload) iframe.onload();
  if (new Set(names).size !== names.length) throw new Error("Duplicate " + page);
  if (JSON.stringify(names) !== JSON.stringify(input.expected[page])) {
    throw new Error("Registration differs for " + page);
  }
  result[page] = names;
}
process.stdout.write(JSON.stringify(result));
