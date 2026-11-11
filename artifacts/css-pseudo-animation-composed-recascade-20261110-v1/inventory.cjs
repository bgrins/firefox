const fs = require("fs"), path = require("path");
const acorn = require(path.resolve("node_modules/acorn"));
const html = fs.readFileSync(path.join(__dirname, "test_missing_pseudo_animation_composed.html"), "utf8");
const ast = acorn.parse(html.split("<script>")[1].split("</script>")[0], {ecmaVersion: "latest"});
const helpers = Object.fromEntries(ast.body.filter(n => n.type === "FunctionDeclaration" && ["makeTarget", "transition", "query"].includes(n.id.name)).map(n => [n.id.name, n.body]));
const tasks = [];
function label(node, prefix) {
  if (node.type === "Literal" && typeof node.value === "string") return node.value;
  if (node.type === "TemplateLiteral" && node.expressions.length === 1 && node.expressions[0].name === "label" && prefix !== null) return node.quasis[0].value.cooked + prefix + node.quasis[1].value.cooked;
  throw Error("Unexpected label expression");
}
function walk(node, rows, prefix = null) {
  if (!node || typeof node !== "object") return;
  if (node.type === "CallExpression") {
    const name = node.callee.name;
    if (["ok", "is"].includes(name)) {
      const text = label(node.arguments.at(-1), prefix);
      rows.push({name: text, classification: text.startsWith("Probe:") ? "probe" : text.startsWith("Setup:") || text.includes(": setup ") ? "setup" : name === "query" ? "diagnostic" : "result"}); return;
    }
    if (helpers[name]) { walk(helpers[name], rows, label(node.arguments[0], prefix)); return; }
  }
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) value.forEach(n => walk(n, rows, prefix));
    else if (value && typeof value === "object") walk(value, rows, prefix);
  }
}
for (const node of ast.body) {
  if (node.type === "ExpressionStatement" && node.expression.callee?.name === "add_task") {
    const fn = node.expression.arguments[0], rows = [];
    walk(fn.body, rows); tasks.push({name: fn.id.name, assertions: rows});
  }
}
const rows = tasks.flatMap(t => t.assertions);
if (new Set(rows.map(r => r.name)).size !== rows.length) throw Error("Duplicate assertion");
console.log(JSON.stringify({assertion_count: rows.length, tasks}, null, 2));
