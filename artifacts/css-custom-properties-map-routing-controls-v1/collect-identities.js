const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[2], "utf8");
const names = [];
const element = {setAttribute() {}, style: {setProperty() {}}};
const CSS = {registerProperty() {}, supports() { throw new Error("test bodies must not execute"); }};
const context = {
  document: {getElementById() { return element; }},
  window: {CSS, getComputedStyle() { return {getPropertyValue() { return ""; }}; }},
  CSS,
  test(body, name) { names.push(name); },
};
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
if (scripts.length !== 1) throw new Error("unexpected inline script count");
vm.runInNewContext(scripts[0][1], context);
process.stdout.write(JSON.stringify({count: names.length, names, scope: "Registration names only; no test body, CSS parser or browser executed"}, null, 2) + "\n");
