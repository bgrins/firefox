import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = load("draft_runner", HERE / "run.py")
policy = helper.read(HERE / "POLICY.json")
parser = load("saved_assessor", ROOT / policy["base_assessor"])
checks = load("saved_checks", ROOT / policy["helpers"]["checks"])
baseline = load("baseline_auth", HERE / "baseline.py")
comparison = load("compare", HERE / "compare.py")
original = baseline.validate(ROOT, HERE, policy, helper, parser, checks)
assert comparison.compare(original, original, policy)["counts"] == {"repaired":0,"new_failures":0,"unchanged_pass":6,"unchanged_fail":50,"changed_fail":0}
changed = copy.deepcopy(original)
for row in changed["rows"]:
    row["status"] = "PASS"
assert comparison.compare(original, changed, policy)["counts"]["repaired"] == 50
changed = copy.deepcopy(original)
for row in changed["rows"]:
    row["status"] = "FAIL"
assert comparison.compare(original, changed, policy)["counts"]["new_failures"] == 6
changed = copy.deepcopy(original)
for row in changed["rows"]:
    if row["status"] == "FAIL": row["message"] = "different failure"
assert comparison.compare(original, changed, policy)["counts"]["changed_fail"] == 50
changed = copy.deepcopy(original)
changed["run_info"]["browser_build_id"] = "different-bound-build"
changed["run_binding"]["browser_build_id"] = "different-bound-build"
comparison.compare(original, changed, policy)
negative = []
for i in range(56):
    changed = copy.deepcopy(original); changed["rows"].pop(i); negative.append(changed)
    changed = copy.deepcopy(original); changed["rows"][i]["subtest"] = "unknown"; negative.append(changed)
    changed = copy.deepcopy(original); changed["rows"][i]["status"] = "TIMEOUT"; negative.append(changed)
for key in ["complete", "execution_preserved"]:
    changed = copy.deepcopy(original); changed[key] = False; negative.append(changed)
changed = copy.deepcopy(original); changed["rows"].append(changed["rows"][0]); negative.append(changed)
changed = copy.deepcopy(original); changed["run_binding"]["revision"] = "wrong"; negative.append(changed)
changed = copy.deepcopy(original); changed["run_info"]["browser_build_id"] = "unbound"; negative.append(changed)
changed = copy.deepcopy(original); changed["run_info"]["unexpected_drift"] = True; negative.append(changed)
for changed in negative:
    try: comparison.compare(original, changed, policy)
    except (ValueError, KeyError): continue
    raise AssertionError("corrupt comparison accepted")
for path in HERE.glob("*.py"): ast.parse(path.read_text())
print(json.dumps({"baseline_replayed":True,"baseline_counts":{"FAIL":50,"PASS":6},"positive_comparisons":5,
                  "negative_comparisons_rejected":len(negative),"browser_executed":False,"runner_main_executed":False},indent=2))
