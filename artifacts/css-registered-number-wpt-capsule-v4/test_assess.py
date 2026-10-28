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
held = policy["held_subtests"]
fixture = next(iter(targets))
regression = next(t for t, kind in policy["tests"].items() if t in policy["regression_subtests"] and kind == "testharness")
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
            names = {**targets, **held, **policy["regression_subtests"]}[name]
            for subtest in names:
                row = {"action": "test_status", "test": name, "subtest": subtest,
                       "status": candidate_status if name in targets else "PASS"}
                if name in targets and candidate_status == "FAIL":
                    row["expected"] = "PASS"
                if name in held:
                    row.update(status="FAIL", expected="PASS", message='assert_equals: observed=[{"value":"19","fontSize":"20px"},{"value":"19","fontSize":"30px"}] expected "20" but got "19"')
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
assert parser.assess(valid, 1, policy, checks, original, binding)["comparison_gate_passed"]
rejected = []
def reject(label, changed, code=1):
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
row.update(status="FAIL", expected="PASS")
reject("all-types regression status changed", changed, 1)
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
assert parser.assess(new_events, 1, policy, checks, original, new_binding)["comparison_gate_passed"]
build_checks.append("independently bound BuildID difference accepted")
for label, stream, bound, baseline in [
    ("changed BuildID with old metadata", new_events, binding, original),
    ("unbound BuildID", valid, None, original),
    ("metadata digest absent", valid, dict(binding, sha256=None), original),
    ("original binding absent", valid, binding, dict(original, run_binding=None)),
]:
    result = parser.assess(stream, 1, policy, checks, baseline, bound)
    assert not result["comparison_gate_passed"], label
    build_checks.append(label + " rejected")
missing_id = copy.deepcopy(valid)
del missing_id[0]["run_info"]["browser_build_id"]
assert not parser.assess(missing_id, 1, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("missing actual BuildID rejected")
wrong_revision = copy.deepcopy(valid)
wrong_revision[0]["run_info"]["revision"] = "b" * 40
assert not parser.assess(wrong_revision, 1, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("actual revision mismatches epoch rejected")
changed_epoch = dict(binding, revision="b" * 40)
assert not parser.assess(wrong_revision, 1, policy, checks, original, changed_epoch)["comparison_gate_passed"]
build_checks.append("individually bound but changed epoch HEAD rejected")
extra_field = copy.deepcopy(valid)
extra_field[0]["run_info"]["unexpected_field"] = True
assert not parser.assess(extra_field, 1, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("new arbitrary run_info field rejected")
changed_changeset = copy.deepcopy(valid)
changed_changeset[0]["run_info"]["browser_changeset"] = "b" * 40
assert not parser.assess(changed_changeset, 1, policy, checks, original, binding)["comparison_gate_passed"]
build_checks.append("browser_changeset drift rejected")
runner = load("runner_without_execution", here / "run.py")
for role in ("original", "candidate"):
    runner.require_compiled_transition({"registered_number_transition": {
        "role": role, "variant": "committed-head", "compiled": True}}, role)
phase_rejections = []
for role in ("original", "candidate"):
    for label, epoch in [
        ("missing transition", {}),
        ("raw transition only", {"raw_attribute_transition": {"role": "candidate", "compiled": True, "accepted": True}}),
        ("missing variant", {"registered_number_transition": {"role": role, "compiled": True}}),
        ("live variant", {"registered_number_transition": {"role": role, "variant": "live", "compiled": True}}),
        ("not compiled", {"registered_number_transition": {"role": role, "variant": "committed-head", "compiled": False}}),
        ("integer compiled", {"registered_number_transition": {"role": role, "variant": "committed-head", "compiled": 1}}),
        ("opposite role", {"registered_number_transition": {"role": "candidate" if role == "original" else "original", "variant": "committed-head", "compiled": True}}),
    ]:
        try:
            runner.require_compiled_transition(epoch, role)
        except RuntimeError:
            phase_rejections.append(role + ": " + label)
        else:
            raise AssertionError((epoch, role))
for name in targets[fixture]:
    reject("missing registered-number assertion: " + name, [e for e in valid if not (e.get("test") == fixture and e.get("subtest") == name)])
    changed = copy.deepcopy(valid)
    row = next(e for e in changed if e.get("test") == fixture and e.get("subtest") == name)
    row.update(status="FAIL", expected="PASS")
    reject("failing registered-number assertion: " + name, changed, 1)


for test, names in held.items():
    reject("missing held page", [e for e in valid if e.get("test") != test])
    for name in names:
        reject("missing held assertion: " + name, [e for e in valid if not (e.get("test") == test and e.get("subtest") == name)])
        for label, mutate in [
            ("changed first value same FAIL", lambda row: row.update(message=row["message"].replace('"value":"19"', '"value":"18"', 1))),
            ("changed second snapshot same FAIL", lambda row: row.update(message=row["message"].replace('"fontSize":"30px"', '"fontSize":"31px"'))),
            ("missing observation message", lambda row: row.pop("message")),
            ("truncated observations", lambda row: row.update(message='observed=[{"value":"19"}]')),
            ("malformed observations", lambda row: row.update(message='observed=broken')),
            ("changed FAIL to PASS", lambda row: row.update(status="PASS")),
        ]:
            changed = copy.deepcopy(valid)
            row = next(e for e in changed if e.get("test") == test and e.get("subtest") == name)
            mutate(row)
            reject(label + ": " + name, changed)
    incomplete = parser.assess([e for e in events("FAIL") if e.get("test") != test], 1, policy, checks, run_binding=binding)
    assert not incomplete["complete"]

import hashlib
import tempfile
saved_argv = sys.argv
saved_authenticate = runner.authenticate
saved_metadata = runner.application_metadata
stale_epoch_rejections = []
def forbid_metadata(*args):
    raise AssertionError("stale epoch reached live application metadata")
try:
    runner.authenticate = lambda *args: None
    runner.application_metadata = forbid_metadata
    with tempfile.TemporaryDirectory(prefix="registered-number-epoch-negative-") as temporary:
        epoch_path = Path(temporary) / "EPOCH.json"
        for role in ("original", "candidate"):
            epoch_path.write_text(json.dumps({"registered_number_transition": {
                "role": role, "variant": "committed-head", "compiled": True}}))
            previous = hashlib.sha256(epoch_path.read_bytes()).hexdigest()
            epoch_path.write_text(json.dumps({"registered_number_transition": {
                "role": role, "variant": "committed-head", "compiled": False}}))
            sys.argv = ["run.py", "0" * 64, role + "-1", str(epoch_path), previous,
                        str(Path(temporary) / "absent-output")]
            if role == "candidate":
                sys.argv += [str(Path(temporary) / "absent-original"), "0" * 64]
            try:
                runner.main()
            except RuntimeError as error:
                assert str(error) == "externally supplied epoch digest", str(error)
                stale_epoch_rejections.append(role)
            else:
                raise AssertionError("stale epoch accepted")
finally:
    sys.argv = saved_argv
    runner.authenticate = saved_authenticate
    runner.application_metadata = saved_metadata
fresh_baseline_rejections = []
try:
    runner.authenticate = lambda *args: None
    runner.application_metadata = lambda *args: binding
    with tempfile.TemporaryDirectory(prefix="registered-number-baseline-negative-") as temporary:
        temporary = Path(temporary)
        epoch_path = temporary / "EPOCH.json"
        baseline_path = temporary / "ASSESSMENT.json"
        for label, head, capsule in [
            ("frozen HEAD drift", "f" * 40, "0" * 64),
            ("prior capsule baseline", policy["frozen_head"], "9" * 64),
        ]:
            epoch_path.write_text(json.dumps({"registered_number_transition": {
                "role": "candidate", "variant": "committed-head", "compiled": True},
                "semantic_index": {"head": head}}))
            baseline_path.write_text(json.dumps({"complete": True, "execution_preserved": True,
                "phase": "original-1", "capsule_manifest_sha256": capsule,
                "native_sources": policy["source_roles"]["original"],
                "run_binding": {"revision": policy["frozen_head"]}}))
            sys.argv = ["run.py", "0" * 64, "candidate-2", str(epoch_path),
                        hashlib.sha256(epoch_path.read_bytes()).hexdigest(), str(temporary / "absent-output"),
                        str(baseline_path), hashlib.sha256(baseline_path.read_bytes()).hexdigest()]
            try:
                runner.main()
            except RuntimeError as error:
                assert str(error) == ("epoch HEAD differs from frozen comparison HEAD" if label == "frozen HEAD drift" else "only the exact adopted original assessment is permitted"), str(error)
                fresh_baseline_rejections.append(label)
            else:
                raise AssertionError(label)
finally:
    sys.argv = saved_argv
    runner.authenticate = saved_authenticate
    runner.application_metadata = saved_metadata

assert len(phase_rejections) == 14 and len(stale_epoch_rejections) == 2
print(json.dumps({"original_expected_failures_retained": True,
                  "matching_original_candidate_passes": True, "rejected_controls": rejected,
                  "phase_transition_positive_controls": 2,
                  "phase_transition_rejected_controls": phase_rejections,
                  "stale_epoch_main_preflight_rejected": stale_epoch_rejections,
                  "stale_epoch_test_scope": "Capsule authentication stubbed; real epoch digest check executed before live metadata or process launch",
                  "fresh_baseline_rejected_controls": fresh_baseline_rejections,
                  "build_identity_controls": build_checks}, indent=2))
