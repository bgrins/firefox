import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
parser = load("assessment", here / "assess.py")
policy = json.loads((here / "POLICY.json").read_text())
checks = load("preservation_checks", root / policy["helpers"]["checks"])
fixture = policy["candidate_test"]
regression = next(t for t, kind in policy["tests"].items() if t != fixture and kind == "testharness")
reftest = next(t for t, kind in policy["tests"].items() if kind == "reftest")
binding = {"path": "/probe/application.ini", "resolved": "/probe/build/application.ini",
           "sha256": "0" * 64, "identity": [1, 2],
           "browser_build_id": "20261027145735", "revision": "a" * 40}
def events(candidate_status):
    result = [{"action": "suite_start", "run_info": {"os": "mac", "debug": False,
                                                   "browser_build_id": binding["browser_build_id"],
                                                   "revision": binding["revision"]}}]
    for name, kind in policy["tests"].items():
        result.append({"action": "test_start", "test": name})
        if kind == "testharness":
            names = policy["candidate_subtests"] if name == fixture else ["regression subtest"]
            for subtest in names:
                row = {"action": "test_status", "test": name, "subtest": subtest,
                       "status": candidate_status if name == fixture else "PASS"}
                if name == fixture and candidate_status == "FAIL":
                    row["expected"] = "PASS"
                if name == regression:
                    row.update(status="FAIL", expected="PASS", known_intermittent=["FAIL"])
                result.append(row)
        result.append({"action": "test_end", "test": name,
                       "status": "OK" if kind == "testharness" else "PASS"})
    result.append({"action": "suite_end"})
    return result
original = parser.assess(events("FAIL"), 1, policy, checks, run_binding=binding)
assert original["complete"] and original["unexpected"] and not original["comparison_gate_passed"]
valid = events("PASS")
assert parser.assess(valid, 0, policy, checks, original, binding)["comparison_gate_passed"]
rejected = []
def reject(label, changed, code=0):
    assessment = parser.assess(changed, code, policy, checks, original, binding)
    assert not assessment["comparison_gate_passed"], label
    rejected.append({"case": label, "errors": assessment["errors"],
                     "comparison_errors": assessment["comparison_errors"]})
reject("missing candidate assertion", [e for e in valid if not (e.get("test") == fixture and e.get("subtest") == policy["candidate_subtests"][0])])
reject("missing reftest completion", [e for e in valid if not (e.get("test") == reftest and e.get("action") == "test_end")])
reject("missing suite completion", valid[:-1])
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == regression and e.get("action") == "test_status")
row["status"] = "PASS"
reject("regression status changed despite intermittent allowance", changed)
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == regression and e.get("action") == "test_status")
row["expected"] = "FAIL"
reject("regression expectation changed", changed)
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == regression and e.get("action") == "test_status")
row["known_intermittent"] = ["FAIL", "PASS"]
reject("regression intermittent metadata changed", changed)
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == reftest and e.get("action") == "test_end")
row.update(status="TIMEOUT", expected="PASS")
reject("reftest timeout", changed, 1)
reject("candidate still fails", events("FAIL"), 1)
reject("exit inconsistent with observed statuses", events("FAIL"), 0)
changed = copy.deepcopy(valid)
index = next(i for i,e in enumerate(changed) if e.get("action") == "test_status")
changed.insert(index, copy.deepcopy(changed[index]))
reject("duplicate candidate assertion", changed)
changed = copy.deepcopy(valid)
changed[0]["run_info"]["debug"] = True
reject("run info changed", changed)
changed = copy.deepcopy(valid)
changed.insert(-1, {"action": "crash", "test": fixture})
reject("crash event", changed)
build_checks = []
new_binding = dict(binding, browser_build_id="20261028120000", sha256="1" * 64)
new_events = copy.deepcopy(valid)
new_events[0]["run_info"]["browser_build_id"] = new_binding["browser_build_id"]
assert parser.assess(new_events, 0, policy, checks, original, new_binding)["comparison_gate_passed"]
build_checks.append("independently bound BuildID difference accepted")
for label, stream, bound, baseline in [
    ("changed BuildID with old metadata", new_events, binding, original),
    ("unbound BuildID", valid, None, original),
    ("metadata digest absent", valid, dict(binding, sha256=None), original),
    ("original binding absent", valid, binding, dict(original, run_binding=None)),
]:
    result = parser.assess(stream, 0, policy, checks, baseline, bound)
    assert not result["comparison_gate_passed"], label
    build_checks.append(label + " rejected")
missing_id = copy.deepcopy(valid)
del missing_id[0]["run_info"]["browser_build_id"]
assert not parser.assess(missing_id, 0, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("missing actual BuildID rejected")
wrong_revision = copy.deepcopy(valid)
wrong_revision[0]["run_info"]["revision"] = "b" * 40
assert not parser.assess(wrong_revision, 0, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("actual revision mismatches epoch rejected")
changed_epoch = dict(binding, revision="b" * 40)
assert not parser.assess(wrong_revision, 0, policy, checks, original, changed_epoch)["comparison_gate_passed"]
build_checks.append("individually bound but changed epoch HEAD rejected")
extra_field = copy.deepcopy(valid)
extra_field[0]["run_info"]["unexpected_field"] = True
assert not parser.assess(extra_field, 0, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("new arbitrary run_info field rejected")
changed_changeset = copy.deepcopy(valid)
changed_changeset[0]["run_info"]["browser_changeset"] = "b" * 40
assert not parser.assess(changed_changeset, 0, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("browser_changeset drift rejected")
runner = load("runner_without_execution", here / "run.py")
for epoch, role in [({}, "original"),
                    ({"attribute_fallback_transition": {"role": "original", "compiled": True}}, "original"),
                    ({"attribute_fallback_transition": {"role": "candidate", "compiled": True}}, "candidate")]:
    runner.require_compiled_transition(epoch, role)
phase_rejections = 0
for epoch, role in [({}, "candidate"),
                    ({"attribute_fallback_transition": {"role": "candidate", "compiled": False}}, "candidate"),
                    ({"attribute_fallback_transition": {"role": "original", "compiled": True}}, "candidate"),
                    ({"attribute_fallback_transition": {"role": "original", "compiled": False}}, "original")]:
    try:
        runner.require_compiled_transition(epoch, role)
    except RuntimeError:
        phase_rejections += 1
    else:
        raise AssertionError((epoch, role))
assert phase_rejections == 4
print(json.dumps({"original_expected_failures_retained": True,
                  "matching_original_candidate_passes": True, "rejected_controls": rejected,
                  "phase_transition_positive_controls": 3,
                  "phase_transition_rejected_controls": phase_rejections,
                  "build_identity_controls": build_checks}, indent=2))
