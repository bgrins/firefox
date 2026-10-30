"use strict";
const fs = require("fs");
const vm = require("vm");
const source = fs.readFileSync(process.argv[2], "utf8");
const report = JSON.parse(fs.readFileSync(0, "utf8"));
let registered = 0;
const context = vm.createContext({window: {addEventListener(type) {
  if (type !== "load") throw new Error("unexpected registration");
  registered++;
}}});
vm.runInContext(source, context);
if (registered !== 1) throw new Error("unexpected source initialization");
const result = report.observations.map(observation => {
  context.input = observation;
  return {id: observation.id, checks: JSON.parse(JSON.stringify(vm.runInContext("referenceChecks(input)", context)))};
});
process.stdout.write(JSON.stringify(result));
