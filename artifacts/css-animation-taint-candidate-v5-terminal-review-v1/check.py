import ast
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / "review.py").read_text()
module = ast.parse(source)
node = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "partition")
namespace = {}
exec(compile(ast.Module(body=[node], type_ignores=[]), "partition", "exec"), namespace)
partition = namespace["partition"]
original = [{"test": "/page", "subtest": str(i), "status": "PASS" if i < 103 else "FAIL", "message": str(i)} for i in range(120)]
unchanged = partition(original, original, dict)
assert len(unchanged["original_pass_controls"]) == 103 and len(unchanged["original_fail_research_targets"]) == 17
assert all(row["full_signature_unchanged"] for rows in unchanged.values() for row in rows)
improved = copy.deepcopy(original)
for row in improved[103:]:
    row["status"] = "PASS"
result = partition(original, improved, dict)
assert all(row["full_signature_unchanged"] for row in result["original_pass_controls"])
assert all(not row["full_signature_unchanged"] for row in result["original_fail_research_targets"])
regressed = copy.deepcopy(improved)
regressed[0]["status"] = "FAIL"
assert not partition(original, regressed, dict)["original_pass_controls"][0]["full_signature_unchanged"]
negatives = [original[:-1], original + [original[0]], [dict(row, subtest="unknown") if i == 0 else row for i,row in enumerate(original)]]
for rows in negatives:
    try:
        partition(original, rows, dict)
    except AssertionError:
        pass
    else:
        raise AssertionError("Malformed roster accepted")
assert json.loads((HERE / "POLICY.json").read_text())["execution_enabled"] is False
assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"unlink", "rmtree", "write_owned"} for node in ast.walk(module))
print(json.dumps({"cohort_positives": 3, "roster_negatives": 3, "syntax": True, "execution_disabled": True, "live_checks_executed": False}))
