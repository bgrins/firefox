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
original = [{"test": "/page", "subtest": str(i), "status": "PASS" if i < 29 else "FAIL", "message": str(i)} for i in range(42)]
unchanged = partition(original, original, dict)
assert len(unchanged["original_pass_controls"]) == 29 and len(unchanged["original_fail_research_targets"]) == 13
assert all(row["full_signature_unchanged"] for rows in unchanged.values() for row in rows)
improved = copy.deepcopy(original)
for row in improved[29:]:
    row["status"] = "PASS"
result = partition(original, improved, dict)
assert all(row["full_signature_unchanged"] for row in result["original_pass_controls"])
assert all(not row["full_signature_unchanged"] for row in result["original_fail_research_targets"])
regressed = copy.deepcopy(improved)
regressed[0]["status"] = "FAIL"
assert not partition(original, regressed, dict)["original_pass_controls"][0]["full_signature_unchanged"]
all_failed = [dict(row, status="FAIL") for row in original]
assert len(partition(original, all_failed, dict)["original_pass_controls"]) == 29
negatives = [original[:-1], original + [original[0]], [dict(row, subtest="unknown") if i == 0 else row for i,row in enumerate(original)]]
for rows in negatives:
    try:
        partition(original, rows, dict)
    except AssertionError:
        pass
    else:
        raise AssertionError("Malformed roster accepted")
policy = json.loads((HERE / "POLICY.json").read_text())
assert policy["execution_enabled"] is False and policy["actual_terminal"] is None
assert policy["expected_session"] == 50372 and policy["expected_launch"] == "cbc269"
import hashlib
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for name, expected in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert sha(ROOT / name) == expected
owner = ROOT / policy['owner_directory']
assert sha(owner / 'FILES.json') == policy['owner_manifest_sha256']
for name, pin in json.loads((owner / 'FILES.json').read_text()).items():
    assert sha(owner / name) == pin['sha256']
old_source = (ROOT / 'artifacts/css-registered-selected-color-candidate-terminal-review-v1/review.py').read_text()
assert source == old_source
anchor = '    assert {name: sha(CONTROL / name) for name in policy["controls"]}'
assert source[source.index(anchor):] == old_source[old_source.index(anchor):]
assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"unlink", "rmtree", "write_owned"} for node in ast.walk(module))
print(json.dumps({"cohort_positives": 4, "roster_negatives": 3, "syntax": True, "execution_disabled": True, "live_checks_executed": False}))
