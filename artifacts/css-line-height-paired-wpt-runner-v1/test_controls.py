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
policy = json.loads((HERE / "POLICY.json").read_text())
parser = load("random_assessor", HERE / "assess.py")
checks = load("random_checks", ROOT / policy["helpers"]["checks"])
binding = {"path": "/synthetic/application.ini", "resolved": "/synthetic/application.ini",
           "sha256": "a" * 64, "browser_build_id": "20261028000000", "revision": policy["frozen_head"]}
def events(target_fail, regression_fail=False):
    result = [{"action": "suite_start", "run_info": {"os": "mac", "debug": False,
               "browser_build_id": binding["browser_build_id"], "revision": binding["revision"]}}]
    for test in policy["tests"]:
        result.append({"action": "test_start", "test": test})
        for name in (policy["target_subtests"] | policy["regression_subtests"])[test]:
            fail = target_fail if test in policy["target_subtests"] else regression_fail
            result.append({"action": "test_status", "test": test, "subtest": name,
                           "status": "FAIL" if fail else "PASS", "expected": "PASS",
                           "message": "fixed original diagnostic" if fail else None})
        result.append({"action": "test_end", "test": test, "status": "OK"})
    result.append({"action": "suite_end"})
    return result
positive = []
rejected = []
for fail in (False, True):
    result = parser.assess(events(fail), int(fail), policy, checks, run_binding=binding)
    assert result["complete"] and result["observed_subtest_count"] == 34
    positive.append("complete original " + str(fail))
original = parser.assess(events(True), 1, policy, checks, run_binding=binding)
candidate = events(False)
assert parser.assess(candidate, 0, policy, checks, original, binding)["comparison_gate_passed"]
positive.append("all targets repaired; regressions unchanged")
old_fail = parser.assess(events(True, True), 1, policy, checks, run_binding=binding)
assert parser.assess(events(False, True), 1, policy, checks, old_fail, binding)["comparison_gate_passed"]
positive.append("unchanged baseline regression failures retained")
def reject(label, rows, code=0, old=original, meta=binding):
    result = parser.assess(rows, code, policy, checks, old, meta)
    assert not result["comparison_gate_passed"], label
    rejected.append(label)
for test in policy["tests"]:
    i = next(i for i, e in enumerate(candidate) if e.get("action") == "test_status" and e["test"] == test)
    reject("missing subtest " + test, candidate[:i] + candidate[i+1:])
    rows = copy.deepcopy(candidate); rows[i]["status"] = "FAIL"; reject("changed outcome " + test, rows, 1)
    rows = copy.deepcopy(candidate); rows[i]["message"] = "new diagnostic"; reject("same status changed message " + test, rows) if test in policy["regression_subtests"] else None
reject("missing suite end", candidate[:-1])
reject("inconsistent exit", candidate, 1)
i = next(i for i, e in enumerate(candidate) if e.get("action") == "test_status")
reject("duplicate identity", candidate[:i] + [candidate[i]] + candidate[i:])
for status in ("TIMEOUT", "NOTRUN", "ERROR"):
    rows = copy.deepcopy(candidate); rows[i]["status"] = status; reject(status, rows, 1)
for field in ("browser_build_id", "revision", "os", "debug"):
    rows = copy.deepcopy(candidate); rows[0]["run_info"][field] = "wrong"; reject("drift " + field, rows)
rows = copy.deepcopy(candidate); rows.insert(-1, {"action": "crash"}); reject("crash", rows, 1)
rows = events(False, True); next(e for e in rows if e.get("test") in policy["regression_subtests"] and e.get("action") == "test_status")["message"] = "different failure"
reject("same FAIL different diagnostic", rows, 1, old_fail)
for test in policy["tests"]:
    rows = copy.deepcopy(candidate)
    next(e for e in rows if e.get("test") == test and e.get("action") == "test_end")["message"] = "changed harness diagnostic"
    reject("changed harness message " + test, rows)
for field in ("expected", "known_intermittent", "message"):
    rows = copy.deepcopy(candidate)
    event = next(e for e in rows if e.get("test") in policy["regression_subtests"] and e.get("action") == "test_status")
    if field in event:
        del event[field]
    else:
        event[field] = []
    reject("regression field presence " + field, rows)
new_binding = dict(binding, browser_build_id="20261029000000", sha256="b" * 64)
rows = copy.deepcopy(candidate); rows[0]["run_info"]["browser_build_id"] = new_binding["browser_build_id"]
assert parser.assess(rows, 0, policy, checks, original, new_binding)["comparison_gate_passed"]
positive.append("independently bound new BuildID")
(HERE / "ASSESSOR-CONTROLS.json").write_text(json.dumps({"positive": positive, "rejected": rejected,
    "browser_executed": False, "runtime_main_executed": False}, indent=2) + "\n")
print(json.dumps({"positive": len(positive), "rejected": len(rejected), "assertions": 34}))
