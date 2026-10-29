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
assessor = load("move_assessor_check", HERE / "assess.py")
policy = json.loads((HERE / "POLICY.json").read_bytes())
settings = policy["wpt"]
checks = load("move_checks", ROOT / settings["checks_helper"])
phase = dict(settings, tests={p: "testharness" for p in settings["expected_subtests"]}, held_subtests={}, cardinality_description="Synthetic exact70 control")
selector = "/dom/nodes/moveBefore/moveBefore-child-list-selector-invalidation.html"
improvements = {(selector, name) for name in settings["target_subtests"][selector]}
def sample(role):
    binding = dict(policy["application_metadata"], source_role=role, revision=settings["phase_revisions"][role], build_revision=settings["phase_revisions"][role], harness_revision=settings["harness_revision"])
    if role == "candidate":
        binding["browser_build_id"] = "synthetic-new-build"
    events = [{"action": "suite_start", "run_info": {"os": "mac", "debug": False, "revision": settings["harness_revision"], "browser_build_id": binding["browser_build_id"]}}]
    for test, names in settings["expected_subtests"].items():
        events.append({"action": "test_start", "test": test})
        for name in names:
            status = "FAIL" if role == "original" and (test, name) in improvements else "PASS"
            row = {"action": "test_status", "test": test, "subtest": name, "status": status}
            if role == "candidate" and (test, name) in improvements:
                row["expected"] = "FAIL"
            events.append(row)
        events.append({"action": "test_end", "test": test, "status": "OK"})
    events.append({"action": "suite_end"})
    return events, binding
old_events, old_binding = sample("original")
old = assessor.assess(old_events, 0, phase, checks, run_binding=old_binding)
assert old["complete"] and len(old["regression_signature"]) == 31
events, binding = sample("candidate")
result = assessor.assess(events, 1, phase, checks, original=old, run_binding=binding)
assert result["comparison_gate_passed"] and len(result["unexpected"]) == 7
assert "MoveBefore" in result["oracle_caveat"]
bad = copy.deepcopy(events)
target = next(r for r in bad if (r.get("test"), r.get("subtest")) in improvements)
target["status"] = "FAIL"
assert not assessor.assess(bad, 1, phase, checks, original=old, run_binding=binding)["comparison_gate_passed"]
bad = copy.deepcopy(events)
control = next(r for r in bad if r.get("action") == "test_status" and r["subtest"] not in settings["target_subtests"].get(r["test"], []))
control["message"] = "changed control signature"
assert not assessor.assess(bad, 1, phase, checks, original=old, run_binding=binding)["comparison_gate_passed"]
bad_binding = dict(binding, revision=old_binding["revision"], build_revision=old_binding["revision"])
assert not assessor.assess(events, 1, phase, checks, original=old, run_binding=bad_binding)["comparison_gate_passed"]
bad = [e for e in events if not (e.get("action") == "test_end" and e.get("test") == selector)]
assert not assessor.assess(bad, 1, phase, checks, original=old, run_binding=binding)["comparison_gate_passed"]
print(json.dumps({"synthetic_accepts": 1, "rejected_mutations": 4, "candidate_expected_fail_to_pass_exit1_supported": True, "observed_browser_results": False}))
