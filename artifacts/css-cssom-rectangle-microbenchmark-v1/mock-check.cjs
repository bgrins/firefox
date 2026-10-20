const fs = require("fs");
const vm = require("vm");
let calls = 0;
class Element {
  constructor() { this.children = []; this.className = ""; }
  append(child) { this.children.push(child); child.parent = this; }
  getBoundingClientRect() {
    calls++;
    let x = 0, y = 0;
    for (let node = this; node; node = node.parent) {
      if (node.className.includes("link")) { x++; y++; }
      if (node.className.includes("transformed")) { x += 3; y += 5; }
    }
    return {x, y, width: 20, height: 10};
  }
}
const output = new Element();
const context = {
  URLSearchParams, location: {hash: ""},
  document: {body: new Element(), visibilityState: "visible",
    createElement: () => new Element(), getElementById: () => output},
  navigator: {userAgent: "MOCK: not a browser"},
  devicePixelRatio: 1, innerWidth: 800, innerHeight: 600,
  performance: {timeOrigin: 0, now: () => calls * 0.005},
  setTimeout: fn => fn(), requestAnimationFrame: fn => fn(), window: {},
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[2], "utf8"), context);
context.window.rectangleBenchmarkPromise.then(result => {
  if (!result.valid || result.cases.length !== 6 || result.order.length !== 42 ||
      result.totalMeasuredCalls !== 840000 || calls !== 858012 ||
      result.cases.some(entry => entry.batches.length !== 7)) {
    throw new Error(JSON.stringify({calls, result}));
  }
  console.log(JSON.stringify({role: "control-flow mock only; no native or browser evidence",
    cases: result.cases.length, batches: result.order.length,
    measuredCalls: result.totalMeasuredCalls, allCalls: calls, valid: result.valid}));
});
