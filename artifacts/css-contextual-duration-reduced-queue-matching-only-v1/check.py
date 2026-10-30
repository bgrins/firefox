import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = read(HERE / "POLICY.json")
comparison = load("reduced_comparison", HERE / "comparison.py")
assessor = load("reduced_assessor", HERE / "assess.py")
checks = load("reduced_checks", ROOT / policy["wpt"]["checks_helper"])
actual = comparison.replay_original(ROOT, policy, assessor, checks)
assert len(actual["rows"]) == 2 and all(r["status"] == "PASS" for r in actual["rows"])
assert len(actual["regression_signature"]) == 3
settings = comparison.phase_policy(copy.deepcopy(policy["wpt"]))
settings["phase_revisions"]["candidate"] = "f" * 40
app = dict(actual["run_binding"], browser_build_id="synthetic-new-build",
           revision="f" * 40, build_revision="f" * 40, source_role="candidate")
events = [{"action": "suite_start", "run_info": dict(actual["run_info"], browser_build_id=app["browser_build_id"])}]
events += copy.deepcopy(actual["starts"] + actual["rows"] + actual["ends"])
events.append({"action": "suite_end"})


def evaluate(stream, code=0):
    return assessor.assess(stream, code, settings, checks, original=actual, run_binding=app)


assert evaluate(events)["comparison_gate_passed"]
failed = copy.deepcopy(events)
for event in failed:
    if event.get("action") == "test_status":
        event.update(status="FAIL", expected="PASS", message="assert_approx_equals: Composed font: expected 22 but got 22.85")
negative_observation = evaluate(failed, 1)
assert negative_observation["complete"] and not negative_observation["comparison_gate_passed"]
assert negative_observation["errors"] == [] and negative_observation["comparison_errors"]
assert len(negative_observation["rows"]) == 2
negative = []


def row(stream):
    return next(e for e in stream if e.get("action") == "test_status")


def reject(label, change, code=0):
    stream = copy.deepcopy(events)
    change(stream)
    assert not evaluate(stream, code)["comparison_gate_passed"], label
    negative.append(label)


reject("changed PASS message", lambda s: row(s).update(message="changed"))
reject("changed expected presence", lambda s: row(s).update(expected="PASS"))
reject("changed intermittent presence", lambda s: row(s).update(known_intermittent=["FAIL"]))
reject("missing callback", lambda s: s.remove(row(s)))
reject("duplicate callback", lambda s: s.insert(2, copy.deepcopy(row(s))))
reject("unknown callback", lambda s: row(s).update(subtest="unknown"))
reject("missing ending", lambda s: s.remove(next(e for e in s if e.get("action") == "test_end")))
reject("changed ending", lambda s: next(e for e in s if e.get("action") == "test_end").update(message="changed"))
reject("missing suite end", lambda s: s.pop())
reject("wrong exit", lambda s: None, 1)
reject("crash", lambda s: s.append({"action": "crash"}))
reject("wrong BuildID", lambda s: s[0]["run_info"].update(browser_build_id="wrong"))
reject("wrong harness revision", lambda s: s[0]["run_info"].update(revision="0" * 40))
reject("setup exception", lambda s: row(s).update(status="FAIL", expected="PASS", message="ReferenceError: missing helper"), 1)
print(json.dumps({"actual_original_replay": "2 PASS / 1 OK", "strict_signatures": 3,
                  "synthetic_equal_candidate_passes": True,
                  "synthetic_regression_is_complete_but_comparison_fails": True,
                  "negative_checks": negative, "live_guard_or_browser_executed": False}, indent=2))
