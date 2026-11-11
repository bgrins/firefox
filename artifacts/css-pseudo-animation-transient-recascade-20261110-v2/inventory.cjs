const fs = require("fs");
const path = require("path");
const acorn = require(path.resolve("node_modules/acorn"));
const html = fs.readFileSync(path.join(__dirname, "test_missing_pseudo_animation_recascade.html"), "utf8");
const script = html.split("<script>")[1].split("</script>")[0];
const tree = acorn.parse(script, {ecmaVersion: "latest"});
const rows = [], tasks = [];
function walk(node, task) {
  if (!node || typeof node !== "object") return;
  if (node.type === "CallExpression" && node.callee.name === "add_task") {
    const name = node.arguments[0].id.name;
    tasks.push(name); walk(node.arguments[0].body, name); return;
  }
  if (task && node.type === "CallExpression" && ["ok", "is", "accepted"].includes(node.callee.name)) {
    const arg = node.arguments.at(-1);
    if (arg.type !== "Literal" || typeof arg.value !== "string") throw Error("Nonliteral assertion label");
    const labels = node.callee.name === "accepted" ? ["admitted", "exact pseudo identity", "origin style not replaced", "no generated pseudo created"].map(s => `${arg.value}: ${s}`) : [arg.value];
    for (const label of labels) rows.push({task, label, kind: label.startsWith("Setup:") ? "setup" : node.callee.name === "accepted" ? "admission_preservation" : "result_or_rejection"});
    return;
  }
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) value.forEach(n => walk(n, task));
    else if (value && typeof value === "object") walk(value, task);
  }
}
walk(tree, null);
if (new Set(rows.map(r => r.label)).size !== rows.length) throw Error("Duplicate assertion labels");
console.log(JSON.stringify({tasks, assertion_count: rows.length, rows}, null, 2));
