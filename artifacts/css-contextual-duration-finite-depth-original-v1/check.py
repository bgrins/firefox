import copy
import ast
import importlib.util
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_binding(policy):
    return load("same_element_actual_admission", HERE / "admission.py").validate(policy)


def check(policy):
    settings = policy["wpt"]
    runtime_assertions = [node for node in ast.walk(ast.parse((HERE / "run.py").read_text())) if isinstance(node, ast.Assert)]
    assert any(ast.dump(node.test) == ast.dump(ast.parse('len(policy["accepted_current_payloads"]) == 29', mode='eval').body) for node in runtime_assertions)
    fixture = ROOT / policy["probe_packages"][0]
    roster = json.loads((fixture / "ROSTER.json").read_text())
    assert policy["probe_packages"] == ["artifacts/css-contextual-duration-finite-depth-probe-v1"]
    inputs = json.loads((fixture / "INPUTS.json").read_text())
    assert settings["expected_subtests"] == roster["tests"] == inputs["source_roster"]["tests"]
    assert len(roster["tests"]) == 1 and sum(map(len, roster["tests"].values())) == 4
    assert settings["resources"] == inputs["resources"] and settings["metadata"] == inputs["metadata"]
    assert settings["manifest"] == inputs["manifest"]
    assert sorted(policy["record_kinds"]) == sorted(inputs["transport"]["expected_files"])
    assert (settings["expected_subtest_count"], settings["expected_control_count"], settings["expected_target_count"], settings["expected_page_count"], settings["expected_regression_signature_count"]) == (4, 4, 0, 1, 5)
    roles = json.loads((ROOT / "artifacts/css-contextual-easing-activation-prototype-v2/SOURCE-ROLES.json").read_bytes())
    assert len(roles) == 8 and "servo/components/style/values/generics/calc.rs" not in roles
    assert policy["source_role_pins"] == dict(
        {name: row["base_sha256"] for name, row in roles.items()},
        **{"servo/components/style/custom_properties.rs": "2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774",
           "dom/animation/EffectCompositor.cpp": "6ec3a0ca45789b3089e8d2abcfb3ff37b881b0ee9084e09d0d396d73491249ed",
           "dom/animation/EffectCompositor.h": "5ee054432f5105515def6f1eba9e2875226d6a59b6a0dc4d1e05b9617a12dc19"})
    assert policy["build_unpinned_sources"] == ["servo/components/style/stylesheets/keyframes_rule.rs"]
    assert policy["original_only"] and set(settings["phase_revisions"]) == {"original"}
    roster = json.loads((ROOT / policy["source_roster"]).read_bytes())
    assert settings["expected_subtests"] == roster["tests"]
    assert settings["target_subtests"] == {}
    assert policy["candidate_execution_enabled"] is False
    check_binding(policy)
    if not policy["execution_enabled"]:
        assert policy["activation_pending"]
    else:
        assert not policy["activation_pending"]
        assert policy["head"] == settings["harness_revision"]
        assert policy["prepared_application_metadata"]["harness_revision"] == policy["head"]
        assert policy["prepared_application_metadata"]["build_revision"] == settings["phase_revisions"]["original"]
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
    for name, digest in policy["references"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    check_records(policy)
    print(json.dumps({"synthetic_positive_checks": 3, "negative_checks": rejected,
                      "original_statuses_measured_without_required_failure_count": True,
                      "fresh_application_metadata_required_at_activation": True, "browser_executed": False}))


def check_records(policy):
    import os
    import tempfile
    collector = load("progress_collection_check", HERE / "records.py")
    samples = {}
    for filename, rule in policy["record_kinds"].items():
        depth = int(rule["kind"].removeprefix("depth-"))
        timing = {"duration": None, "progress": None, "time": None, "state": "synthetic"}
        snapshot = {"rootFont": None, "opacity": None, "leafDuration": None, "leaf": timing,
                    "nodes": [{"font": None, "lineHeight": None, "duration": None, "timing": timing} for _ in range(depth)]}
        observations = {mode: {"depth": depth, "mode": mode, "literalInitial": snapshot, "initial": snapshot,
            "samples": [{"phase": phase, "opacity": None} for phase in ("first-leaf-read", "passive-frame-1", "passive-frame-2", "passive-frame-3")],
            "beforeMembership": snapshot, "afterMembership": snapshot,
            "membership": [{"animation": False, "effect": False} for _ in range(depth + 1)]} for mode in ("literal", "contextual")}
        samples[filename] = {"run_id": "synthetic_progress_run_123456", "kind": rule["kind"], "observations": observations}
    with tempfile.TemporaryDirectory(prefix="css-progress-record-check-", dir="/private/tmp") as temporary:
        directory = Path(temporary)
        directory.chmod(0o700)
        binding = dict(directory=str(directory), identity=[directory.stat().st_dev, directory.stat().st_ino], run_id="synthetic_progress_run_123456")
        rows = [{"test": rule["page"], "subtest": rule["subtest"], "status": "PASS"} for rule in policy["record_kinds"].values()]
        def put(name, value):
            (directory / name).write_text(json.dumps(value))
            (directory / name).chmod(0o600)
        for name, value in samples.items():
            put(name, value)
        def collect(current=rows, bound=binding):
            return collector.collect(ROOT, directory, bound, policy, {"rows": current})
        assert collect()["complete"]
        failed = copy.deepcopy(rows)
        for row in failed:
            row["status"] = "FAIL"
        assert collect(failed)["complete"]
        first = next(iter(samples))
        (directory / first).unlink()
        partial = collect(failed)
        assert not partial["complete"] and len(partial["missing"]) == 1 and not partial["errors"] and len(partial["records"]) == 3
        assert collect()["errors"]
        put(first, samples[first])
        negatives = []
        for label, mutate in [
            ("wrong run", lambda v: v.update(run_id="wrong")),
            ("extra envelope field", lambda v: v.update(extra=1)),
            ("wrong kind", lambda v: v.update(kind="unknown")),
            ("missing first sample", lambda v: v["observations"]["contextual"]["samples"].pop(0)),
            ("out of order samples", lambda v: v["observations"]["contextual"]["samples"].reverse()),
            ("nonfinite numeric sample", lambda v: v["observations"]["contextual"]["samples"][0].update(opacity=float("inf"))),
        ]:
            value = copy.deepcopy(samples[first]); mutate(value); put(first, value)
            result = collect(); assert result["errors"] and first in result["records"] and not result["records"][first]["schema_valid"], label
            negatives.append(label)
        put(first, samples[first]); (directory / first).chmod(0o644)
        assert collect()["errors"]; negatives.append("nonprivate file")
        (directory / first).chmod(0o600)
        (directory / "unknown.json").write_text("{}")
        assert collect()["errors"]; (directory / "unknown.json").unlink(); negatives.append("unknown file")
        (directory / first).unlink(); (directory / first).symlink_to(directory / list(samples)[1])
        assert collect()["errors"]; (directory / first).unlink(); put(first, samples[first]); negatives.append("symlink")
        wrong = dict(binding, identity=[0, 0])
        try:
            collect(bound=wrong)
        except AssertionError:
            negatives.append("directory identity")
        else:
            raise AssertionError("wrong directory identity accepted")
        assert collect()["complete"]
    assert not directory.exists()
    print(json.dumps({"record_positive_checks": 3, "record_negative_checks": ["missing PASS record", *negatives], "ordinary_FAIL_missing_collection_retained": True, "temporary_removed": True}))

if __name__ == "__main__":
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check(json.loads((HERE / "POLICY.json").read_text()))
