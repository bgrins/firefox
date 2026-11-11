const fs = require("fs");
const path = require("path");
const espree = require(path.join(process.cwd(), "node_modules/espree"));
const html = fs.readFileSync(path.join(__dirname, "test.html"), "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
const tree = espree.parse(script, { ecmaVersion: "latest" });
const setup = new Set([
  "Known raw base", "Real CSSAnimation source", "CSS generation path reached",
  "Pause is pending before query", "Play is pending before query",
  "Null-hold non-null-start wallclock branch reached",
  "Unresolved CSSAnimation exists", "Native unresolved timeline reached",
  "Held unresolved effect remains registered", "Finite timeline geometry",
  "Interior scroll position", "Resolved interior progress",
  "Resolved boundary progress", "Two genuine CSS transitions created",
  "Retargeted effects retain native transition level", "No animation-level effect yet",
  "Transition levels preserved after animation addition", "Animation-level effect present",
  "Narrow attachment interior progress", "Expanded attachment quarter progress",
]);
const preservation = new Set([
  "Query does not complete pending pause", "Query does not complete pending play",
]);
const suffixes = ["diagnostic schema", "aliased outputs rejected",
  "occupied outputs rejected", "captured native state unchanged", "owned output maps"];
const tasks = [];
for (const statement of tree.body) {
  const call = statement.expression;
  if (call?.callee?.name !== "add_task") {
    continue;
  }
  const callback = call.arguments[0];
  const assertions = [];
  const visit = node => {
    if (!node || typeof node !== "object") {
      return;
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) {
        value.forEach(visit);
      } else if (value && typeof value === "object") {
        visit(value);
      }
    }
    if (node.type !== "CallExpression") {
      return;
    }
    if (node.callee.name === "query") {
      const label = node.arguments[2];
      if (label.type !== "Literal" || typeof label.value !== "string") {
        throw Error("Nonliteral query label");
      }
      suffixes.forEach(suffix => assertions.push({
        name: `${label.value}: ${suffix}`, classification: "diagnostic",
      }));
    } else if (["is", "ok"].includes(node.callee.name)) {
      const label = node.arguments.at(-1);
      if (label.type !== "Literal" || typeof label.value !== "string") {
        throw Error("Nonliteral direct assertion");
      }
      assertions.push({ name: label.value,
        classification: setup.has(label.value) ? "setup" :
          preservation.has(label.value) ? "preservation" : "result" });
    }
  };
  visit(callback.body);
  tasks.push({ name: callback.id.name, assertions });
}
const names = tasks.flatMap(task => task.assertions.map(assertion => assertion.name));
if (new Set(names).size !== names.length) {
  throw Error("Duplicate assertion name");
}
const totals = {};
tasks.flatMap(task => task.assertions).forEach(assertion => {
  totals[assertion.classification] = (totals[assertion.classification] || 0) + 1;
});
process.stdout.write(JSON.stringify({ task_count: tasks.length,
  assertion_count: names.length, totals,
  runtime_policy: "A setup failure invalidates that task's semantic interpretation; all categories must pass. Missing, duplicate, unexpected and failed assertions reject the run.",
  tasks }, null, 2) + "\n");
