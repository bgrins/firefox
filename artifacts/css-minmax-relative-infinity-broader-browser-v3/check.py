import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = json.loads((HERE / "POLICY.json").read_bytes())
if (HERE / "FILES.json").exists():
    for name, pin in json.loads((HERE / "FILES.json").read_bytes()).items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == pin, name
assert policy["execution_enabled"] is True and policy["activation_pending"] == []
assert policy["head"] and policy["controls"] and policy["prepared_application_metadata"]
owner = load("broader_enabled_owner", HERE / "run.py")
owner.verify_entry(policy)
activation_negative_checks = []
for label, mutate in [
    ("wrong HEAD", lambda p: p.__setitem__("head", "0" * 40)),
    ("wrong epoch", lambda p: p["controls"].__setitem__("CURRENT-EPOCH.json", "0" * 64)),
    ("wrong application identity", lambda p: p["prepared_application_metadata"].__setitem__("identity", [0, 0])),
    ("wrong build lineage", lambda p: p["wpt"]["phase_revisions"].__setitem__("original", "0" * 40)),
    ("wrong park terminal", lambda p: p["entry_authority"]["terminal_record"].__setitem__("exit", 1)),
    ("wrong entry authority", lambda p: p["entry_authority"].__setitem__("kind", "unverified")),
]:
    altered = copy.deepcopy(policy)
    mutate(altered)
    try:
        owner.verify_entry(altered)
    except AssertionError:
        activation_negative_checks.append(label)
    else:
        raise AssertionError("Accepted activation mutation: " + label)
for name in ("run.py", "wpt.py", "assess.py", "assess-base.py", "check.py"):
    compile((HERE / name).read_bytes(), name, "exec")
for name, pin in policy["references"].items():
    if name.startswith("artifacts/"):
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
assert (HERE / "assess-base.py").read_bytes() == (ROOT / "artifacts/css-minmax-relative-infinity-browser-v2/assess.py").read_bytes()
settings = copy.deepcopy(policy["wpt"])
capture = ROOT / "artifacts/css-minmax-relative-infinity-broader-plan-v3"
for name, record in json.loads((capture / "FILES.json").read_bytes()).items():
    assert hashlib.sha256((capture / name).read_bytes()).hexdigest() == record["sha256"], name
captured_roster = json.loads((capture / "ROSTER.json").read_bytes())["pages"]
assert settings["known_subtests"] == {page: row["names"] for page, row in captured_roster.items() if row["complete"]}
assert settings["discovery_pages"] == [page for page, row in captured_roster.items() if not row["complete"]]
extension = "/css/css-values/minmax-relative-infinity-ordering.html"
cases = json.loads((ROOT / "artifacts/css-minmax-relative-infinity-regression-selection-v3/CASES.json").read_bytes())["cases"]
assert settings["target_subtests"][extension] == [case["expression"] + " preserves n-ary contextual and NaN behavior"
                                                  for case in cases if case["group"] == "nary_relative_infinity"]
settings.update(tests={page: "testharness" for page in settings["expected_subtests"]},
                held_subtests={}, regression_subtests={}, cardinality_description="synthetic discovery checks",
                harness_revision="a" * 40, phase_revisions={"original": "b" * 40})
binding = {"sha256": "c" * 64, "path": "synthetic/application.ini", "resolved": "/synthetic/application.ini",
           "browser_build_id": "synthetic-build", "revision": "b" * 40, "build_revision": "b" * 40,
           "harness_revision": "a" * 40, "source_role": "original"}
events = [{"action": "suite_start", "run_info": {"os": "synthetic", "debug": False,
           "revision": "a" * 40, "browser_build_id": "synthetic-build"}}]
for page in settings["tests"]:
    events.append({"action": "test_start", "test": page})
    names = settings["known_subtests"].get(page, ["synthetic unknown callback A", "synthetic unknown callback B"])
    events.extend({"action": "test_status", "test": page, "subtest": name, "status": "PASS"} for name in names)
    events.append({"action": "test_end", "test": page, "status": "OK"})
events.append({"action": "suite_end"})
assessor = load("broader_discovery", HERE / "assess.py")
checks = load("broader_checks", ROOT / settings["checks_helper"])
positive = []
negative = []


def assess(stream=events, code=0, configuration=settings, metadata=binding, original=None):
    return assessor.assess(stream, code, configuration, checks, original=original, run_binding=metadata)


def valid(label, stream=events, code=0):
    result = assess(stream, code)
    assert result["complete"] and result["discovered_subtests"] is not None, result["errors"]
    assert result["comparison_gate_passed"] is False and result["roster_requires_seal_before_candidate"]
    positive.append(label)
    return result


def invalid(label, stream=events, code=0, configuration=settings, metadata=binding, original=None):
    try:
        result = assess(stream, code, configuration, metadata, original)
    except AssertionError:
        negative.append(label)
        return
    assert not result["complete"] and result["discovered_subtests"] is None, label
    negative.append(label)


valid("twelve synthetic complete pages with five exact authored rosters")
unknown = settings["discovery_pages"][0]
known = next(iter(settings["known_subtests"]))
row_index = next(i for i, e in enumerate(events) if e.get("action") == "test_status" and e["test"] == unknown)
known_index = next(i for i, e in enumerate(events) if e.get("action") == "test_status" and e["test"] == known)
for label, fields, code in [
    ("existing expected FAIL retained", {"status": "FAIL", "expected": "FAIL", "message": "synthetic existing failure"}, 0),
    ("existing intermittent FAIL retained", {"status": "FAIL", "expected": "PASS", "known_intermittent": ["FAIL"]}, 0),
    ("original unexpected FAIL observed", {"status": "FAIL", "expected": "PASS", "message": "synthetic original failure"}, 1),
]:
    stream = copy.deepcopy(events)
    stream[row_index].update(fields)
    result = valid(label, stream, code)
    assert assessor.signature(stream[row_index]) in result["regression_signature"]
stream = copy.deepcopy(events)
stream.pop(row_index)
valid("one unknown callback cannot be detected as missing before independent discovery", stream)
stream = copy.deepcopy(events)
stream.insert(row_index, dict(stream[row_index], subtest="synthetic additional unknown callback"))
valid("unknown roster has no invented upper callback count", stream)

for action in ("suite_start", "suite_end", "test_start", "test_end"):
    stream = copy.deepcopy(events)
    stream.pop(next(i for i, e in enumerate(stream) if e["action"] == action))
    invalid("missing " + action, stream)
for action in ("suite_start", "suite_end", "test_start", "test_end", "test_status"):
    stream = copy.deepcopy(events)
    index = next(i for i, e in enumerate(stream) if e["action"] == action)
    stream.insert(index, copy.deepcopy(stream[index]))
    invalid("duplicate " + action, stream)
invalid("entire selected page omitted", [e for e in events if e.get("test") != unknown])
invalid("unknown page has no callbacks", [e for e in events if not (e.get("test") == unknown and e["action"] == "test_status")])
stream = copy.deepcopy(events)
stream.pop(known_index)
invalid("missing known callback", stream)
stream = copy.deepcopy(events)
stream[known_index]["subtest"] = "renamed known callback"
invalid("renamed known callback", stream)
stream = copy.deepcopy(events)
stream[row_index]["test"] = "/unselected.html"
invalid("callback from unselected page", stream)
stream = copy.deepcopy(events)
stream[row_index]["status"] = "TIMEOUT"
invalid("non-completed callback", stream)
stream = copy.deepcopy(events)
next(e for e in stream if e["action"] == "test_end")["status"] = "ERROR"
invalid("non-OK page ending", stream, 1)
stream = copy.deepcopy(events)
target = next(e for e in stream if e.get("action") == "test_status" and e["test"] in settings["fixture_target_pages"])
target.update(status="FAIL", expected="PASS", message="ReferenceError: synthetic setup exception")
invalid("new fixture setup exception", stream, 1)
for fault in [{"action": "crash"}, {"action": "log", "level": "ERROR", "message": "synthetic"},
              {"action": "process_exit", "exitcode": 9}]:
    invalid("infrastructure " + fault["action"], [*events, fault])
invalid("wrong exit", events, 1)
stream = copy.deepcopy(events)
stream[0]["run_info"]["browser_build_id"] = "other-build"
invalid("wrong BuildID", stream)
stream = copy.deepcopy(events)
stream[0]["run_info"]["revision"] = "d" * 40
invalid("wrong harness revision", stream)
invalid("candidate source role", metadata=dict(binding, source_role="candidate"))
invalid("candidate comparison prohibited", original={"complete": True})
invalid("reordered lifecycle", [events[1], events[0], *events[2:]])
bad = copy.deepcopy(settings)
bad["known_subtests"].pop(known)
invalid("known roster partition weakened", configuration=bad)
bad = copy.deepcopy(settings)
bad["expected_subtest_count"] = 999
invalid("invented aggregate count", configuration=bad)
print(json.dumps({"positive_checks": positive, "negative_checks": negative,
                  "activation_negative_checks": activation_negative_checks,
                  "synthetic_only": True, "unknown_page_names_are_synthetic": True,
                  "actual_broader_callback_count": None, "browser_executed": False,
                  "external_runtime_pins_deferred": [name for name in policy["references"] if not name.startswith("artifacts/")]}))
