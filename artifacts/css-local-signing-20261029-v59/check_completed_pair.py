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


owner = load("checkpoint_pair_checker", HERE / "run.py")
assessor = load("checkpoint_pair_signatures", ROOT / "artifacts/css-hypot-finite-scale-browser-v4/assess.py")
policy = json.loads((ROOT / "artifacts/css-hypot-finite-scale-browser-v4/POLICY.json").read_bytes())["wpt"]
original = json.loads((ROOT / "artifacts/css-hypot-finite-scale-browser-runtime-1/original-wpt/ASSESSMENT.json").read_bytes())
candidate = copy.deepcopy(original)
targets = {(test, name) for test, names in policy["target_subtests"].items() for name in names}
for row in candidate["rows"]:
    if (row["test"], row["subtest"]) in targets:
        row["status"] = "PASS"
candidate["comparison_gate_passed"] = True
candidate["comparison_errors"] = []
check = lambda old, new: owner.validate_completed_assessments(old, new, policy, assessor.signature)
check(original, candidate)
assert any(row["status"] == "FAIL" for row in candidate["rows"])
print("PASS: synthetic 16 target improvements preserve all existing control failures")
mutations = {}
mutations["missing row"] = lambda c: c["rows"].pop()
mutations["duplicate row"] = lambda c: c["rows"].__setitem__(0, copy.deepcopy(c["rows"][1]))
mutations["missing ending"] = lambda c: c["ends"].pop()
mutations["ending message"] = lambda c: c["ends"][0].__setitem__("message", "changed")
mutations["signature changed"] = lambda c: c["regression_signature"].pop()
mutations["gate false"] = lambda c: c.__setitem__("comparison_gate_passed", False)
mutations["comparison error"] = lambda c: c.__setitem__("comparison_errors", ["changed"])
mutations["setup error"] = lambda c: c.__setitem__("fixture_setup_errors", ["changed"])
mutations["control improvement"] = lambda c: next(r for r in c["rows"] if r["status"] == "FAIL").__setitem__("status", "PASS")
mutations["control message"] = lambda c: next(r for r in c["rows"] if (r["test"], r["subtest"]) not in targets).__setitem__("message", "changed")
mutations["target failed"] = lambda c: next(r for r in c["rows"] if (r["test"], r["subtest"]) in targets).__setitem__("status", "FAIL")
for name, mutate in mutations.items():
    changed = copy.deepcopy(candidate)
    mutate(changed)
    try:
        check(original, changed)
    except AssertionError:
        print("PASS: rejected " + name)
    else:
        raise AssertionError("Accepted mutation: " + name)
passing_original = copy.deepcopy(original)
passing_target = next(r for r in passing_original["rows"] if (r["test"], r["subtest"]) in targets)
passing_target["status"] = "PASS"
changed = copy.deepcopy(candidate)
key = (passing_target["test"], passing_target["subtest"])
next(r for r in changed["rows"] if (r["test"], r["subtest"]) == key)["message"] = "changed"
try:
    check(passing_original, changed)
except AssertionError:
    print("PASS: rejected original-PASS target signature change")
else:
    raise AssertionError("Accepted original-PASS target mutation")
print("Synthetic only; no candidate observation is fabricated or bound.")

actual = json.loads((ROOT / "artifacts/css-hypot-finite-scale-browser-runtime-1/candidate-wpt/ASSESSMENT.json").read_bytes())
check(original, actual)
print("PASS: actual saved hypot227 baseline/candidate assessments satisfy the completed-pair gate")
