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


def check_binding(policy):
    for name, expected in policy["references"].items():
        assert name.startswith("artifacts/") and ".." not in Path(name).parts
        assert not (ROOT / name).is_symlink() and sha(ROOT / name) == expected, name
    previous = read(ROOT / policy["predecessor"]["directory"] / "POLICY.json")
    for key in ("accepted_calc_sha256", "accepted_current_payloads", "build_epoch", "build_unpinned_sources", "deferred_nonartifact_references", "head", "original_only", "candidate_execution_enabled", "rebuilt_binaries", "source_role_pins", "state_helper", "wpt_helper"):
        assert policy[key] == previous[key], key
    mutable = {"expected_control_count", "expected_page_count", "expected_regression_signature_count", "expected_subtest_count", "expected_subtests", "fixture_target_pages", "manifest", "metadata", "resources"}
    assert {k:v for k,v in policy["wpt"].items() if k not in mutable} == {k:v for k,v in previous["wpt"].items() if k not in mutable}
    assert policy["original_only"] and policy["candidate_execution_enabled"] is False
    assert policy["activation_pending"] == ([] if policy["execution_enabled"] else ["root saved review and activation"])
    current = read(ROOT / policy["fresh_admission"]["path"])
    assert policy["references"][policy["fresh_admission"]["path"]] == policy["fresh_admission"]["sha256"]
    assert policy["head"] == current["head"] and policy["controls"] == current["controls"]
    assert current["source_transition_lock_absent"] and current["native_acceptance_increment"] == 0
    assert sha(ROOT / current["final_state_audit"]) == current["final_state_audit_sha256"]
    snapshot = read(ROOT / current["final_state_audit"])
    assert snapshot["index"]["head"] == policy["head"] and snapshot["index"]["raw_index"] == current["raw_index"]
    assert sha(ROOT / current["fresh_application_capture"]) == current["fresh_application_capture_sha256"]
    app = read(ROOT / current["fresh_application_capture"])
    app.update(build_revision=app["revision"], harness_revision=policy["head"], source_role="original")
    assert policy["prepared_application_metadata"] == app
    assert app["revision"] == policy["wpt"]["phase_revisions"]["original"]
    failed = read(ROOT / policy["failed_signing_receipt"]["path"])
    assert policy["references"][policy["failed_signing_receipt"]["path"]] == policy["failed_signing_receipt"]["sha256"]
    assert failed["head"] == policy["head"] and failed["committed"] is False and failed["git_exit"] == 128
    assert all(failed[k] for k in ("head_unchanged", "controls_unchanged", "raw_index_unchanged", "native_working_diff_preserved", "untracked_paths_unchanged", "source_transition_lock_absent", "owned_temporary_index_removed"))
    attempt = ROOT / "artifacts/css-research-checkpoint-20261030-v82"
    assert sha(attempt / "result.json") == failed["result_sha256"] and sha(attempt / "signing.log") == failed["signing_log_sha256"]
    assert read(attempt / "result.json") == {"committed": False, "exit": 128, "real_index_and_canonical_state_unchanged": True}


def check(policy):
    check_binding(policy)
    settings = policy["wpt"]
    roster = {}
    expected_resources = {}
    combined = None
    for directory in policy["probe_packages"]:
        source = ROOT / directory
        for name, record in read(source / "FILES.json").items():
            assert sha(source / name) == (record if isinstance(record, str) else record["sha256"])
        roster.update(read(source / "ROSTER.json"))
        for name, record in read(source / "INPUTS.json")["resources"].items():
            digest = record if isinstance(record, str) else record["sha256"]
            assert sha(source / "tests" / name) == digest
            if name in expected_resources:
                assert expected_resources[name]["sha256"] == digest
            else:
                expected_resources[name] = {"path": str((source / "tests" / name).relative_to(ROOT)), "sha256": digest}
        manifest = read(source / "MANIFEST.json")
        if combined is None:
            combined = manifest
        else:
            assert combined["version"] == manifest["version"] and combined["url_base"] == manifest["url_base"] and combined["items"]["support"] == manifest["items"]["support"]
            combined["items"]["testharness"]["css"]["css-animations"].update(manifest["items"]["testharness"]["css"]["css-animations"])
    assert roster == settings["expected_subtests"] == read(ROOT / policy["source_roster"])
    assert read(ROOT / settings["manifest"]["path"]) == combined
    assert sha(ROOT / settings["manifest"]["path"]) == settings["manifest"]["sha256"]
    for name, record in expected_resources.items():
        assert settings["resources"][name] == record
    assert set(settings["resources"]) == set(expected_resources) | {"resources/testharness.js.headers", "resources/testharnessreport.js.headers"}
    assert (settings["expected_subtest_count"], settings["expected_control_count"], settings["expected_target_count"], settings["expected_page_count"], settings["expected_regression_signature_count"]) == (6, 6, 0, 2, 8)
    assert settings["target_subtests"] == {} and set(settings["fixture_target_pages"]) == set(roster)
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
    print(json.dumps({"synthetic_positive_checks": 3, "negative_checks": rejected, "references": len(policy["references"]), "original_outcomes_observed": True, "browser_executed": False}))


if __name__ == "__main__":
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check(json.loads((HERE / "POLICY.json").read_bytes()))
