import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_binding = load("expanded_saved_admission", HERE / "admission.py").check_binding


def check(policy):
    check_binding(policy)
    rejected_bindings = []
    for label, mutate in (
        ("wrong current epoch", lambda p: p["controls"].update({"CURRENT-EPOCH.json": "0" * 64})),
        ("changed held provider", lambda p: p["source_role_pins"].update({"servo/components/style/custom_properties.rs": "0" * 64})),
        ("wrong app bytes", lambda p: p["prepared_application_metadata"].update(sha256="0" * 64)),
        ("wrong restored inode", lambda p: p["prepared_application_metadata"].update(identity=[0, 0])),
        ("invented terminal", lambda p: p["restoration_handoff"]["terminal"].update(owner_exit=1)),
        ("changed roster", lambda p: p["wpt"]["expected_subtests"].pop(next(iter(p["wpt"]["expected_subtests"])))),
        ("omitted metadata absence", lambda p: p["wpt"]["metadata"].pop("css/css-variables/animation-taint-direct-attr-context.tentative.html.ini")),
    ):
        altered = copy.deepcopy(policy)
        mutate(altered)
        try:
            check_binding(altered)
        except AssertionError:
            rejected_bindings.append(label)
        else:
            raise AssertionError(label)
    settings = policy["wpt"]
    assert (settings["expected_subtest_count"], settings["expected_control_count"], settings["expected_target_count"], settings["expected_page_count"], settings["expected_regression_signature_count"]) == (120, 120, 0, 16, 136)
    assert len(policy["accepted_current_payloads"]) == 29
    settings = dict(settings, harness_revision="a" * 40, phase_revisions={"original": "b" * 40})
    app = {"browser_build_id": "static-build-id", "revision": "b" * 40,
           "build_revision": "b" * 40, "harness_revision": "a" * 40,
           "source_role": "original", "sha256": "c" * 64, "path": "synthetic/application.ini",
           "resolved": "synthetic/application.ini"}
    configuration = dict(settings, tests={page: "testharness" for page in settings["expected_subtests"]}, held_subtests={}, cardinality_description="synthetic static verification only")
    targets = {(page, name) for page, names in settings["target_subtests"].items() for name in names}
    configuration["regression_subtests"] = {page: [name for name in names if (page, name) not in targets] for page, names in settings["expected_subtests"].items()}
    assessor = load("easing_assessor_check", HERE / "assess.py")
    checks = load("easing_stream_check", ROOT / settings["checks_helper"])
    events = [{"action": "suite_start", "run_info": {"os": "mac", "debug": False, "browser_build_id": app["browser_build_id"], "revision": settings["harness_revision"]}}]
    for page, names in settings["expected_subtests"].items():
        events.append({"action": "test_start", "test": page})
        for name in names:
            events.append({"action": "test_status", "test": page, "subtest": name, "status": "PASS"})
        events.append({"action": "test_end", "test": page, "status": "OK"})
    events.append({"action": "suite_end"})

    def evaluate(stream, code):
        return assessor.assess(stream, code, configuration, checks, run_binding=app)

    assert evaluate(events, 0)["complete"]
    failed = copy.deepcopy(events)
    for event in failed:
        if event.get("action") == "test_status":
            event.update(status="FAIL", expected="PASS", message="synthetic assertion")
    assert evaluate(failed, 1)["complete"]
    mixed = copy.deepcopy(failed)
    next(e for e in mixed if e.get("status") == "FAIL").update(status="PASS")
    assert evaluate(mixed, 1)["complete"]
    rejected = []

    def reject(label, mutate, code=0):
        stream = copy.deepcopy(events)
        mutate(stream)
        assert not evaluate(stream, code)["complete"], label
        rejected.append(label)

    def row(stream):
        return next(e for e in stream if e.get("action") == "test_status")

    reject("missing callback", lambda s: s.remove(row(s)))
    reject("duplicate callback", lambda s: s.insert(2, copy.deepcopy(row(s))))
    reject("renamed callback", lambda s: row(s).update(subtest="unknown"))
    reject("wrong callback page", lambda s: row(s).update(test="/other.html"))
    reject("missing ending", lambda s: s.remove(next(e for e in s if e.get("action") == "test_end")))
    reject("duplicate start", lambda s: s.insert(1, copy.deepcopy(s[1])))
    reject("missing suite end", lambda s: s.pop())
    reject("crash", lambda s: s.append({"action": "crash"}))
    reject("wrong exit", lambda s: None, 1)
    reject("wrong BuildID", lambda s: s[0]["run_info"].update(browser_build_id="wrong"))
    reject("wrong harness revision", lambda s: s[0]["run_info"].update(revision="0" * 40))
    reject("fixture setup exception", lambda s: next(e for e in s if e.get("action") == "test_status" and e["test"] in settings["fixture_target_pages"]).update(status="FAIL", expected="PASS", message="ReferenceError: missing helper"), 1)
    print(json.dumps({"synthetic_positive_checks": 3, "negative_checks": rejected, "references": len(policy["references"]), "binding_negatives": rejected_bindings, "original_outcomes_observed": True, "browser_executed": False}))


if __name__ == "__main__":
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check(json.loads((HERE / "POLICY.json").read_bytes()))
