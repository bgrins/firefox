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
targets = policy["target_subtests"]
fixture = next(iter(targets))
regression = next(t for t, kind in policy["tests"].items() if t not in targets and kind == "testharness")
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
            names = targets[name] if name in targets else policy["regression_subtests"][name]
            for subtest in names:
                row = {"action": "test_status", "test": name, "subtest": subtest,
                       "status": candidate_status if name in targets else "PASS"}
                if name in targets and candidate_status == "FAIL":
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
for target, names in targets.items():
    reject("missing target assertion: " + target, [e for e in valid if not (e.get("test") == target and e.get("subtest") == names[0])])
    reject("missing complete target page: " + target, [e for e in valid if e.get("test") != target])
    changed = copy.deepcopy(valid)
    row = next(e for e in changed if e.get("test") == target and e.get("action") == "test_status")
    row.update(status="FAIL", expected="PASS")
    reject("target assertion still fails: " + target, changed, 1)
    incomplete_original = parser.assess([e for e in events("FAIL") if e.get("test") != target], 1, policy, checks, run_binding=binding)
    assert not incomplete_original["complete"], target
for test in policy["regression_subtests"]:
    changed = copy.deepcopy(valid)
    row = next(e for e in changed if e.get("test") == test and e.get("action") == "test_status")
    row["subtest"] += " altered"
    reject("untouched regression identity changed: " + test, changed)
used = "/css/css-values/attr-non-type-used-fallback-cycle.html"
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == used and e.get("action") == "test_status")
row.update(status="FAIL", expected="PASS")
reject("used-fallback regression changes", changed, 1)
all_types = "/css/css-values/attr-all-types.html"
changed = copy.deepcopy(valid)
row = next(e for e in changed if e.get("test") == all_types and e.get("action") == "test_status")
row.update(status="PASS")
reject("all-types regression status changed", changed)
reject("all-types page missing", [e for e in valid if e.get("test") != all_types])

eof_names = [item["id"] for item in json.loads((root / "artifacts/css-attr-raw-nested-repair-v2/EOF-CONTROLS.json").read_text())]
raw_target = "/css/css-values/attr-raw-nested-cycle.html"
for name in eof_names:
    reject("missing EOF/control assertion: " + name, [e for e in valid if not (e.get("test") == raw_target and e.get("subtest") == name)])
    changed = copy.deepcopy(valid)
    row = next(e for e in changed if e.get("test") == raw_target and e.get("subtest") == name)
    row.update(status="FAIL", expected="PASS")
    reject("failing EOF/control assertion: " + name, changed, 1)
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
prior = {"attribute_fallback_transition": {"role": "candidate", "compiled": True, "accepted": True}}
for epoch, role in [(prior, "original"),
                    ({"raw_attribute_transition": {"role": "original", "compiled": True}}, "original"),
                    ({"raw_attribute_transition": {"role": "candidate", "compiled": True}}, "candidate")]:
    runner.require_compiled_transition(epoch, role)
phase_rejections = 0
for epoch, role in [({}, "original"), ({}, "candidate"), (prior, "candidate"),
                    ({"attribute_fallback_transition": {"role": "candidate", "compiled": True}}, "original"),
                    ({"attribute_fallback_transition": {"role": "candidate", "compiled": False, "accepted": True}}, "original"),
                    ({"attribute_fallback_transition": {"role": "original", "compiled": True, "accepted": True}}, "original"),
                    ({"raw_attribute_transition": {"role": "candidate", "compiled": False}}, "candidate"),
                    ({"raw_attribute_transition": {"role": "original", "compiled": True}}, "candidate"),
                    ({"raw_attribute_transition": {"role": "original", "compiled": False}}, "original"),
                    ({"raw_attribute_transition": {"role": "candidate", "compiled": True}}, "original")]:
    try:
        runner.require_compiled_transition(epoch, role)
    except RuntimeError:
        phase_rejections += 1
    else:
        raise AssertionError((epoch, role))
assert phase_rejections == 10
print(json.dumps({"original_expected_failures_retained": True,
                  "matching_original_candidate_passes": True, "rejected_controls": rejected,
                  "phase_transition_positive_controls": 3,
                  "phase_transition_rejected_controls": phase_rejections,
                  "build_identity_controls": build_checks}, indent=2))
