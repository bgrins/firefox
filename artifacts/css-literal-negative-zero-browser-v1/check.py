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
    assert policy["original_only"] and set(settings["phase_revisions"]) == {"original"}
    roster = json.loads((ROOT / policy["source_roster"]).read_bytes())
    assert settings["expected_subtests"] == {page: [r["name"] for r in rows] for page, rows in roster["pages"].items()}
    assert settings["target_subtests"] == {page: [r["name"] for r in rows if r["classification"] == "literal_target"] for page, rows in roster["pages"].items()}
    assert sum(r["classification"] == "unresolved_boundary_control" for rows in roster["pages"].values() for r in rows) == 0
    manifest = json.loads((ROOT / settings["manifest"]["path"]).read_bytes())
    assert set(manifest["items"]["testharness"]["css"]["css-values"]) == {Path(page).name for page in settings["expected_subtests"]}
    metadata = load("static_metadata", ROOT / settings["metadata_helper"])
    app = metadata.application_metadata(ROOT / settings["application_ini"], settings["phase_revisions"]["original"])
    app.update(build_revision=app["revision"], harness_revision=settings["harness_revision"], source_role="original")
    assert app == policy["prepared_application_metadata"]
    configuration = dict(settings, tests={page: "testharness" for page in settings["expected_subtests"]}, held_subtests={}, cardinality_description="synthetic static verification only")
    targets = {(page, name) for page, names in settings["target_subtests"].items() for name in names}
    configuration["regression_subtests"] = {page: [name for name in names if (page, name) not in targets] for page, names in settings["expected_subtests"].items()}
    assessor = load("zero_assessor_check", HERE / "assess.py")
    checks = load("zero_stream_check", ROOT / settings["checks_helper"])
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
    mixed = copy.deepcopy(failed)
    next(e for e in mixed if e.get("status") == "FAIL").update(status="PASS")
    assert evaluate(mixed, 1)["complete"]
    controls_failed = copy.deepcopy(mixed)
    next(e for e in controls_failed if e.get("action") == "test_status" and (e["test"], e["subtest"]) not in targets).update(status="FAIL", expected="PASS")
    assert evaluate(controls_failed, 1)["complete"]
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
    print(json.dumps({"synthetic_positive_checks": 4, "negative_checks": rejected,
                      "original_statuses_measured_without_required_failure_count": True,
                      "fresh_application_metadata_matches": True, "browser_executed": False}))
