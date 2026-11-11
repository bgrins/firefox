"use strict";

const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = process.argv[2];
const mode = process.argv[3];
const corpus = JSON.parse(fs.readFileSync(path.join(root, "corpus.json"), "utf8"));
const oracle = new Set(JSON.parse(fs.readFileSync(path.join(root, "inputs/oracle.json"), "utf8")).map(words => words.join(" ")));
corpus.inputSha256 = require("node:crypto").createHash("sha256").update(fs.readFileSync(path.join(root, "corpus.json"))).digest("hex");
const admitted = value => oracle.has(value) || (mode === "overaccept" && value === "none full-width");
class Declaration {
  constructor() { this.value = ""; }
  setProperty(property, value) {
    if (property !== "text-transform") { throw new Error("wrong property"); }
    if (value === "") {
      if (mode !== "broken-removal") { this.value = ""; }
    } else if (admitted(value)) {
      this.value = value.split(" ").reverse().join(" ");
    }
  }
  getPropertyValue() { return this.value; }
  getPropertyPriority() { return ""; }
  get length() { return this.value === "" ? 0 : 1; }
  item() { return this.value === "" ? "" : "text-transform"; }
  get cssText() { return this.value === "" ? "" : `text-transform: ${this.value};`; }
}
const elements = new Map();
const element = id => {
  if (!elements.has(id)) {
    elements.set(id, { textContent: "", value: "mock-only", disabled: true, addEventListener() {} });
  }
  return elements.get(id);
};
element("probe-input").textContent = JSON.stringify(corpus);
const context = {
  document: { getElementById: element, createElement: () => ({ style: new Declaration() }) },
  CSS: { supports: (property, value) => {
    if (property !== "text-transform") { throw new Error("wrong property"); }
    return admitted(value);
  } },
  navigator: { userAgent: "MOCK_ONLY_NO_BROWSER", platform: "mock", appVersion: "mock" },
  location: { href: "mock://source-only" },
  window: {},
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root, "probe.js"), "utf8"), context);
process.stdout.write(JSON.stringify(context.window.textTransformProbe.run()) + "\n");
