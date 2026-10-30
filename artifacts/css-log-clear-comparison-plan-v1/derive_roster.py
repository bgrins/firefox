import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
CAPTURE = HERE / "capture/tests"
helper = (CAPTURE / "css/support/numeric-testcommon.js").read_text()
assert "`${testString} should be ${stage}-value-equivalent to ${expectedString}`" in helper
serialize = (CAPTURE / "css/support/serialize-testcommon.js").read_text()
for stage in ("specified", "computed"):
    assert "`'${t}' as a " + stage + " value should serialize as '${e}'.`" in serialize
pages = {}
for name in ("exp-log-compute.html", "exp-log-serialize.html", "log-clear-special-values.html"):
    body = (CAPTURE / "css/css-values" / name).read_text()
    scripts = re.findall(r"<script>(.*?)</script>", body, re.S)
    assert len(scripts) == 1
    request = {"helper": helper, "page": scripts[0]}
    result = subprocess.run(["node", "-e", r"""
const vm = require("vm");
let input = "";
process.stdin.on("data", data => input += data);
process.stdin.on("end", () => {
  const request = JSON.parse(input);
  const rows = [];
  const context = vm.createContext({
    test: (callback, name) => rows.push({name, kind: "authored"}),
    test_specified_serialization: (prop, expression, expected) => rows.push({
      name: `'${expression}' as a specified value should serialize as '${expected}'.`,
      kind: "serialization", prop, expression, expected}),
    test_computed_serialization: (prop, expression, expected) => rows.push({
      name: `'${expression}' as a computed value should serialize as '${expected}'.`,
      kind: "serialization", prop, expression, expected})
  });
  vm.runInContext(request.helper, context);
  context._test_math = ({stage, testString, expectedString, msg, msgExtra}) => {
    let name = msg || `${testString} should be ${stage}-value-equivalent to ${expectedString}`;
    if (!msg && msgExtra) name += `; ${msgExtra}`;
    rows.push({name, kind: "numeric", stage, expression: testString, expected: expectedString});
  };
  vm.runInContext(request.page, context);
  process.stdout.write(JSON.stringify(rows));
});
"""], input=json.dumps(request), text=True, capture_output=True, check=True)
    rows = json.loads(result.stdout)
    assert len({row["name"] for row in rows}) == len(rows)
    pages["/css/css-values/" + name] = rows
metadata = (HERE / "capture/meta/css/css-values/exp-log-compute.html.ini").read_text()
known_failures = re.findall(r"^  \[(.*)\]\n    expected: FAIL$", metadata, re.M)
assert len(known_failures) == 5
compute = pages["/css/css-values/exp-log-compute.html"]
assert set(known_failures) <= {row["name"] for row in compute}
new_targets = [
    "base one above one", "base one below one", "base one at positive zero",
    "base one at generated negative zero", "base one at positive infinity",
    "argument one at base one half", "argument one at base one quarter",
    "deferred base reaches one", "deferred valid base crosses one",
    "deferred argument reaches one",
]
assert set(new_targets) <= {row["name"] for row in pages["/css/css-values/log-clear-special-values.html"]}
for path, rows in pages.items():
    for row in rows:
        row["classification"] = "control"
        if path.endswith("exp-log-compute.html") and row["name"] in known_failures:
            row["classification"] = "clear_target"
        if path.endswith("log-clear-special-values.html") and row["name"] in new_targets:
            row["classification"] = "clear_target"
        if row.get("expression") in ["log(2, 0)", "calc(-1 * log(2, 0))", "log(2, -0)", "calc(-1 * log(2, -0))"]:
            row["classification"] = "unresolved_boundary_control"
result = {"provenance": "Source-derived helper-call expansion, not real DOM registration or browser callback execution. Numeric helper runs with _test_math collecting requests; serialization calls record their source name template. No document or DOM mock is supplied.", "pages": pages, "known_metadata_failures": known_failures,
          "page_counts": {path: len(rows) for path, rows in pages.items()},
          "total": sum(len(rows) for rows in pages.values()),
          "targets": sum(row["classification"] == "clear_target" for rows in pages.values() for row in rows),
          "unresolved_boundary_controls": sum(row["classification"] == "unresolved_boundary_control" for rows in pages.values() for row in rows),
          "browser_confirmation_required": True}
output = HERE / "ROSTER.json"
if output.exists():
    assert json.loads(output.read_text()) == result
else:
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({key: result[key] for key in ["page_counts", "total", "targets", "unresolved_boundary_controls", "browser_confirmation_required"]}))
