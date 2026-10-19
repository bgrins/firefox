const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = process.argv[2];
const result = {};
for (const [file, realm] of [
  ["fontface-loaded-size-adjust-update.html", "window"],
  ["fontface-loaded-size-adjust-canvas.any.js", "window"],
  ["fontface-loaded-size-adjust-canvas.any.js", "dedicatedworker"],
]) {
  let source = fs.readFileSync(path.join(root, "proposal", file), "utf8");
  if (file.endsWith(".html")) {
    const scripts = [...source.matchAll(/<script>([\s\S]*?)<\/script>/g)];
    if (scripts.length !== 1) throw new Error("Unexpected inline scripts");
    source = scripts[0][1];
  }
  const names = [];
  let setupCount = 0;
  vm.runInNewContext(source, {
    GLOBAL: {isWindow: () => realm === "window"},
    document: {fonts: {}},
    self: {fonts: {}},
    promise_setup: () => { setupCount++; },
    promise_test: (callback, name) => { names.push(name); },
  }, {filename: file, timeout: 1000});
  if (setupCount !== 1 || names.length !== new Set(names).size) {
    throw new Error("Setup or duplicate test name");
  }
  result[`${file}:${realm}`] = names;
}
process.stdout.write(JSON.stringify(result, null, 2) + "\n");
