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
original = [{"test": "/page", "subtest": str(i), "status": "PASS" if i < 30 else "FAIL", "message": str(i)} for i in range(45)]
unchanged = partition(original, original, dict)
assert len(unchanged["original_pass_controls"]) == 30 and len(unchanged["original_fail_research_targets"]) == 15
assert all(row["full_signature_unchanged"] for rows in unchanged.values() for row in rows)
improved = copy.deepcopy(original)
for row in improved[30:]:
    row["status"] = "PASS"
result = partition(original, improved, dict)
assert all(row["full_signature_unchanged"] for row in result["original_pass_controls"])
assert all(not row["full_signature_unchanged"] for row in result["original_fail_research_targets"])
regressed = copy.deepcopy(improved)
regressed[0]["status"] = "FAIL"
assert not partition(original, regressed, dict)["original_pass_controls"][0]["full_signature_unchanged"]
all_failed = [dict(row, status="FAIL") for row in original]
assert len(partition(original, all_failed, dict)["original_pass_controls"]) == 30
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
assert policy["expected_session"] == 16539 and policy["expected_launch"] == "335776"
import hashlib
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for name, expected in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert sha(ROOT / name) == expected
owner = ROOT / policy['owner_directory']
assert sha(owner / 'FILES.json') == policy['owner_manifest_sha256']
for name, pin in json.loads((owner / 'FILES.json').read_text()).items():
    assert sha(owner / name) == pin['sha256']
old_source = (ROOT / 'artifacts/css-registered-selected-color-narrow-combined-terminal-review-v1/review.py').read_text()
anchor = '    assert {name: sha(CONTROL / name) for name in policy["controls"]}'
assert source[source.index(anchor):source.index("    report = {")] == old_source[old_source.index(anchor):old_source.index("    report = {")]
assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"unlink", "rmtree", "write_owned"} for node in ast.walk(module))


import re
import importlib.util
helpers = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in {"preservation", "warning_summary"}]
space = {"re": re}
exec(compile(ast.Module(body=helpers, type_ignores=[]), "common_pure_helpers", "exec"), space)
spec = importlib.util.spec_from_file_location("strict_signature", ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py")
assessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessor)
old = {"complete": True, "rows": [dict(row, action="test_status") for row in original], "ends": [{"action": "test_end", "test": "/page" + str(i), "status": "OK"} for i in range(4)]}
check_preservation = lambda value: space["preservation"](old, value, assessor.signature)["full_original_signature_equality"]
assert check_preservation(copy.deepcopy(old))
timed = copy.deepcopy(old)
for row in timed["rows"] + timed["ends"]: row["time"] = 12345
assert check_preservation(timed)
for field, index, changes in [("rows", 30, {"status": "PASS"}), ("rows", 0, {"message": "changed"}), ("rows", 30, {"expected": "FAIL"}), ("ends", 0, {"message": "changed"})]:
    changed = copy.deepcopy(old)
    changed[field][index].update(changes)
    assert not check_preservation(changed)
malformed = []
for field in ("rows", "ends"):
    missing = copy.deepcopy(old); missing[field].pop(); malformed.append(missing)
    duplicate = copy.deepcopy(old); duplicate[field][-1] = duplicate[field][0]; malformed.append(duplicate)
partial = copy.deepcopy(old); partial["complete"] = False; malformed.append(partial)
for bad in malformed:
    try: check_preservation(bad)
    except AssertionError: pass
    else: raise AssertionError("Malformed equality evidence accepted")
warnings = space["warning_summary"](b"\x1b[33mwarning: dead code\x1b[0m\n  location\nwarning[unused]: unused function\nx.rs:4: warning: note\nwarning: 2 warnings emitted\n")
assert warnings["matched_line_count"] == 4 and warnings["matching_warning_lines"][0]["following_context"][0] == "  location"
assert space["warning_summary"](b"warning_count=0\n") ["matched_line_count"] == 0
assert space["warning_summary"](b"\xffwarning: bad encoding")["decoding_replacement_present"]
assert not warnings["complete_warning_inventory_claimed"] and warnings["human_log_review_required"]
print(json.dumps({"cohort_positives": 4, "roster_negatives": 3, "preservation_equal_cases": 2, "preservation_mismatches": 4, "preservation_malformed": 5, "warning_cases": 3, "execution_disabled": True, "live_checks_executed": False}))
