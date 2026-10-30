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


def check(policy):
    settings = policy["wpt"]
    roles = json.loads((ROOT / "artifacts/css-contextual-easing-activation-prototype-v2/SOURCE-ROLES.json").read_bytes())
    assert len(roles) == 8 and "servo/components/style/values/generics/calc.rs" not in roles
    assert policy["source_role_pins"] == dict(
        {name: row["base_sha256"] for name, row in roles.items()},
        **{"servo/components/style/custom_properties.rs": "2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774"})
    assert policy["build_unpinned_sources"] == ["servo/components/style/stylesheets/keyframes_rule.rs"]
    assert policy["original_only"] and set(settings["phase_revisions"]) == {"original"}
    assert (settings["expected_subtest_count"], settings["expected_target_count"],
            settings["expected_control_count"], settings["expected_page_count"],
            settings["expected_regression_signature_count"]) == (1, 1, 0, 1, 1)
    assert len(policy["accepted_current_payloads"]) == 29
    roster = json.loads((ROOT / policy["source_roster"]).read_bytes())
    assert settings["expected_subtests"] == {page: [r["name"] for r in rows] for page, rows in roster["pages"].items()}
    assert settings["target_subtests"] == {page: [r["name"] for r in rows if r["classification"] == "clear_target"] for page, rows in roster["pages"].items()}
    manifest = json.loads((ROOT / settings["manifest"]["path"]).read_bytes())
    assert set(manifest["items"]["testharness"]["css"]["css-animations"]) == {Path(page).name for page in settings["expected_subtests"]}
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
        if (event.get("test"), event.get("subtest")) in targets:
            event.update(status="FAIL", expected="PASS", message="synthetic assertion")
    assert evaluate(failed, 1)["complete"]
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
    print(json.dumps({"synthetic_positive_checks": 2, "negative_checks": rejected,
                      "original_statuses_measured_without_required_failure_count": True,
                      "fresh_application_metadata_required_at_activation": True, "browser_executed": False}))
