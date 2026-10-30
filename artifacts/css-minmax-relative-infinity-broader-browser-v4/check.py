import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, pin):
    assert sha(directory / "FILES.json") == pin
    for name, record in read(directory / "FILES.json").items():
        expected = record["sha256"] if isinstance(record, dict) else record
        assert sha(directory / name) == expected, name


policy = read(HERE / "POLICY.json")
assert policy["execution_enabled"] is False and policy["candidate_execution_enabled"] is False
assert policy["activation_pending"]
if (HERE / "FILES.json").exists():
    authenticate(HERE, sha(HERE / "FILES.json"))
for name in ("candidate.py", "baseline.py", "wpt.py", "assess.py", "comparison.py", "check.py"):
    compile((HERE / name).read_bytes(), name, "exec")
for name, pin in policy["references"].items():
    if name.startswith("artifacts/"):
        assert sha(ROOT / name) == pin, name
binding = policy["baseline_binding"]
directory = ROOT / binding["directory"]
authenticate(directory, binding["manifest_sha256"])
authenticate(ROOT / policy["baseline_capsule"]["directory"], policy["baseline_capsule"]["sha256"])
assert read(directory / binding["terminal_path"]) == binding["terminal"]
assert binding["terminal"]["session_id"] == 42876 and binding["terminal"]["terminal_chunk"] == "ea6fe2" and binding["terminal"]["exit"] == 0
assert sha(directory / "RESULT.json") == binding["result_sha256"] == binding["terminal"]["result_sha256"]
assert sha(directory / "DISCOVERED-ROSTER.json") == binding["roster_sha256"]
outer = read(directory / "RESULT.json")
for key, name in (("assessment_sha256", "ASSESSMENT.json"), ("raw_sha256", "raw.jsonl"), ("result_sha256", "RESULT.json")):
    assert sha(directory / "original-wpt" / name) == outer["phase"][key]
assert read(directory / "DISCOVERED-ROSTER.json")["phase"] == outer["phase"]
roles = read(HERE / "SOURCE-ROLES.json")
assert set(roles) == {"servo/components/style/values/generics/calc.rs"}
for record in roles.values():
    for kind in ("base", "candidate"):
        assert sha(ROOT / record[kind + "_capture"]) == record[kind + "_sha256"]
    assert record["candidate_sha256"] == "065c05d8c9fee140c07a7ef68841c95a6339ca66021c72122fc8832b136e0103"
assessor = load("strict_assessor", HERE / "assess.py")
checks = load("stream_checks", ROOT / policy["wpt"]["checks_helper"])
comparison = load("strict_comparison", HERE / "comparison.py")
original = comparison.replay_original(ROOT, policy, assessor, checks)
settings = comparison.phase_policy(policy["wpt"])
assert (settings["expected_subtest_count"], settings["expected_target_count"], settings["expected_control_count"],
        settings["expected_page_count"], settings["expected_regression_signature_count"]) == (472, 14, 458, 12, 470)
targets = {(page, name) for page, names in settings["target_subtests"].items() for name in names}
assert sum(row["status"] == "FAIL" for row in original["rows"]) == 16
assert all(row["status"] == "FAIL" for row in original["rows"] if (row["test"], row["subtest"]) in targets)
events = [json.loads(line) for line in (directory / "original-wpt/raw.jsonl").read_text().splitlines()]
events = copy.deepcopy(events)
metadata = copy.deepcopy(original["run_binding"])
metadata.update(revision=policy["head"], build_revision=policy["head"], source_role="candidate", browser_build_id="synthetic-candidate-build")
for event in events:
    if event.get("action") == "suite_start":
        event["run_info"]["browser_build_id"] = metadata["browser_build_id"]
    if event.get("action") == "test_status" and (event["test"], event["subtest"]) in targets:
        event["status"] = "PASS"
        for key in ("expected", "known_intermittent", "message", "stack"):
            event.pop(key, None)


def evaluate(stream=events, code=0, configuration=settings, old=original, app=metadata):
    return assessor.assess(stream, code, configuration, checks, original=old, run_binding=app)


positive = evaluate()
assert positive["complete"] and positive["comparison_gate_passed"], positive
assert positive["regression_signature"] == original["regression_signature"]
assert sum(row["status"] == "FAIL" for row in positive["rows"]) == 2
assert sum(row["test"] in settings["candidate_required_pass_pages"] and row["status"] == "PASS" for row in positive["rows"]) == 32
negative = []


def reject(label, mutate, code=0):
    stream = copy.deepcopy(events)
    mutate(stream)
    result = evaluate(stream, code)
    assert not result["comparison_gate_passed"], label
    negative.append(label)


def row(stream, predicate):
    return next(event for event in stream if event.get("action") == "test_status" and predicate(event))


reject("missing callback", lambda stream: stream.pop(next(i for i, event in enumerate(stream) if event.get("action") == "test_status")))
reject("duplicate callback", lambda stream: stream.insert(2, copy.deepcopy(row(stream, lambda event: True))))
reject("renamed callback", lambda stream: row(stream, lambda event: True).__setitem__("subtest", "synthetic rename"))
reject("target remains failed", lambda stream: row(stream, lambda event: (event["test"], event["subtest"]) in targets).update(status="FAIL", expected="PASS"), 1)
reject("original PASS changed", lambda stream: row(stream, lambda event: (event["test"], event["subtest"]) not in targets and event["status"] == "PASS").update(status="FAIL", expected="PASS"), 1)
reject("original PASS message changed", lambda stream: row(stream, lambda event: (event["test"], event["subtest"]) not in targets and event["status"] == "PASS").__setitem__("message", "synthetic change"))
reject("legacy expected FAIL became PASS", lambda stream: row(stream, lambda event: event["status"] == "FAIL").__setitem__("status", "PASS"))
reject("legacy failure message changed", lambda stream: row(stream, lambda event: event["status"] == "FAIL").__setitem__("message", "synthetic change"))
reject("legacy expectation field presence changed", lambda stream: row(stream, lambda event: event["status"] == "FAIL").__setitem__("expected", "FAIL"))
reject("intermittent field presence changed", lambda stream: row(stream, lambda event: (event["test"], event["subtest"]) not in targets).pop("known_intermittent"))
for token in ("preserves singleton", "preserves duplicate-only", "min(NaN", "max(NaN"):
    reject("authored control changed: " + token, lambda stream, token=token: row(stream, lambda event: token in event["subtest"]).update(status="FAIL", expected="PASS"), 1)
reject("missing page ending", lambda stream: stream.pop(next(i for i, event in enumerate(stream) if event.get("action") == "test_end")))
reject("ending message changed", lambda stream: next(event for event in stream if event.get("action") == "test_end").__setitem__("message", "synthetic change"))
reject("duplicate page start", lambda stream: stream.insert(1, copy.deepcopy(next(event for event in stream if event.get("action") == "test_start"))))
reject("unknown callback page", lambda stream: row(stream, lambda event: True).__setitem__("test", "/unselected.html"))
reject("missing suite end", lambda stream: stream.pop(next(i for i, event in enumerate(stream) if event.get("action") == "suite_end")))
reject("infrastructure crash", lambda stream: stream.append({"action": "crash"}))
reject("wrong exit", lambda stream: None, 1)
reject("wrong browser BuildID", lambda stream: next(event for event in stream if event.get("action") == "suite_start")["run_info"].__setitem__("browser_build_id", "wrong"))
reject("changed platform run_info", lambda stream: next(event for event in stream if event.get("action") == "suite_start")["run_info"].__setitem__("os", "other"))
print(json.dumps({"actual_baseline_replayed_exactly": True, "strict_transformation_preserves_observations": True,
                  "synthetic_candidate_only": True, "synthetic_repaired_targets": 14,
                  "synthetic_authored_passes": 32, "unchanged_full_control_ending_signatures": 470,
                  "negative_checks": negative, "owner_or_browser_executed": False,
                  "external_runtime_pins_deferred": [name for name in policy["references"] if not name.startswith("artifacts/")]}))
