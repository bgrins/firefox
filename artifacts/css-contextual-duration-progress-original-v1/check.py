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
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    runtime = ROOT / policy["restored_runtime"]
    terminal = read(ROOT / policy["restoration_binding"]["terminal"]["path"])
    refresh = read(ROOT / policy["restoration_binding"]["refresh"]["path"])
    owner = ROOT / policy["restored_owner"]
    assert terminal["owner_sha256"] == sha(owner / "FILES.json")
    assert terminal["exit"] == 1 and terminal["callbacks_failed"] == 2 and terminal["comparison_gate_passed"] is False and terminal["state_and_application_restoration_independently_verified"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    result = read(runtime / "CANDIDATE-RESULT.json")
    assert result["restoration_verified"] and result["runtime_controls_unchanged"]
    assert result["publication_errors"] == []
    restored = read(runtime / "RESTORATION.json")
    assert restored["errors"] == [] and restored["owned_processes"] == {}
    assert all(policy["source_role_pins"][n] == r["sha256"] for n, r in restored["sources"].items())
    cleanup = read(runtime / "ROOT-BACKUP-CLEANUP.json")
    assert cleanup["removed"] and cleanup["verified_original_restoration"]
    assert refresh["full_restored_state_verified"] and refresh["accepted_fix_increment"] == 0
    assert refresh["only_changed_field"] == "raw_index_observation.current"
    assert refresh["runtime_manifest_sha256"] == sha(runtime / "FILES.json")
    assert refresh["observation"] == terminal["raw_index_observation"]
    before = read(owner / "POLICY.json")
    assert refresh["before_epoch"] == before["controls"]["CURRENT-EPOCH.json"]
    assert policy["head"] == before["head"] == policy["wpt"]["harness_revision"]
    assert policy["controls"] == dict(before["controls"], **{"CURRENT-EPOCH.json": refresh["after_epoch"]})
    expected = dict(before["prepared_application_metadata"])
    expected.update(entry_identity=terminal["restored_application_entry"]["identity"],
                    identity=terminal["restored_application_target"]["identity"],
                    sha256=terminal["restored_application_target"]["sha256"])
    expected.update(build_revision=expected["revision"], harness_revision=policy["head"], source_role="original")
    assert policy["prepared_application_metadata"] == expected
    assert policy["wpt"]["phase_revisions"] == {"original": expected["revision"]}
    assert policy["accepted_current_payloads"] == before["accepted_current_payloads"] and len(policy["accepted_current_payloads"]) == 29
    audit = read(ROOT / policy["postfailure_audit"])
    signing = read(ROOT / policy["failed_signing_result"])
    assert audit["head"] == policy["head"] and audit["index_and_epoch_unchanged"] and audit["transition_lock_absent"]
    assert (audit["signing_session"], audit["signing_terminal_chunk"], audit["owner_exit"]) == (61015, "7c997c", 1)
    assert audit["signing_result"] == signing == {"committed": False, "exit": 128, "real_index_and_canonical_state_unchanged": True}
    assert audit["untracked_count"] == 563 and audit["prototype_hashes_and_committed_recoveries_verified"] == 68 and audit["unrelated_metadata_verified"] == 495
    assert not audit["unexpected_paths"] and not audit["missing_paths"]


def check(policy):
    settings = policy["wpt"]
    runtime_assertions = [node for node in ast.walk(ast.parse((HERE / "run.py").read_text())) if isinstance(node, ast.Assert)]
    assert any(ast.dump(node.test) == ast.dump(ast.parse('len(policy["accepted_current_payloads"]) == 29', mode='eval').body) for node in runtime_assertions)
    expected_names, expected_resources, expected_metadata, expected_records = {}, {}, {}, {}
    merged_manifest = None
    def merge(left, right):
        for name, value in right.items():
            if name not in left:
                left[name] = copy.deepcopy(value)
            elif isinstance(value, dict):
                merge(left[name], value)
            else:
                assert left[name] == value, name
    for package in policy["probe_packages"]:
        inputs = json.loads((ROOT / package / "INPUTS.json").read_bytes())
        expected_names.update(inputs["source_roster"]["tests"])
        merge(expected_resources, inputs["resources"])
        merge(expected_metadata, {key: value for key, value in inputs["metadata"].items() if value["sha256"] is not None})
        manifest = json.loads((ROOT / inputs["manifest"]["path"]).read_bytes())
        if merged_manifest is None:
            merged_manifest = manifest
        else:
            merge(merged_manifest, manifest)
        page, names = next(iter(inputs["source_roster"]["tests"].items()))
        schema = inputs["transport"].get("handler", {"path": "artifacts/css-contextual-duration-progress-transport-v1/duration-progress-record.py"})["path"]
        for kind, name in zip(inputs["transport"]["expected_kinds"], names):
            expected_records[kind + ".json"] = dict(kind=kind, page=page, subtest=name, schema=schema)
        relative = page.lstrip("/") + ".ini"
        expected_metadata[relative] = dict(path="testing/web-platform/meta/" + relative, sha256=None, status="proposed fixture metadata must be absent at admission")
    assert settings["expected_subtests"] == expected_names and len(expected_names) == 3
    assert sum(map(len, expected_names.values())) == 9
    assert settings["resources"] == expected_resources and settings["metadata"] == expected_metadata
    assert policy["record_kinds"] == expected_records and len(expected_records) == 9
    assert json.loads((ROOT / settings["manifest"]["path"]).read_bytes()) == merged_manifest
    assert (settings["expected_subtest_count"], settings["expected_control_count"], settings["expected_target_count"], settings["expected_page_count"], settings["expected_regression_signature_count"]) == (9, 9, 0, 3, 12)
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
    assert settings["expected_subtests"] == {page: [r["name"] for r in rows] for page, rows in roster["pages"].items()}
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
        kind = rule["kind"]
        mode = kind.rsplit("-", 1)[1]
        timing = dict(duration=2000, progress=.375, time=750, state="paused")
        flags = {"membership": dict(middle=True, child=True, middleEffect=True, childEffect=True)}
        driver = timing.copy()
        if kind.startswith("two-hop-"):
            snapshot = dict(childOpacity=.5, childDuration=1500, child=timing.copy(), middleFont=24, middleDuration=2000, middle=timing.copy(), rootFont=32)
        elif kind.startswith("lh-chain-"):
            snapshot = dict(childOpacity=.5, childDuration=1500, childLineHeight=24, child=timing.copy(), middleLineHeight=24, middleDuration=2000, middle=timing.copy(), parentFont=32)
        else:
            snapshot = dict(width=56, cssDuration=2000, parentFont=32, **timing)
            flags = {"same": True}
            driver = dict(time=1000, state="paused")
        dimension = "width" if kind.startswith("property-only-") else "opacity"
        observation = dict(mode=mode, samples=[dict(phase=phase, **{dimension: index}) for index, phase in enumerate(("first-child-read", "passive-frame-1", "passive-frame-2", "passive-frame-3"))], beforeMembership=copy.deepcopy(snapshot), driverTiming=driver if mode == "animated" else None, afterMembership=copy.deepcopy(snapshot), seek751=copy.deepcopy(snapshot), afterSeek=copy.deepcopy(snapshot), **flags)
        samples[filename] = dict(run_id="synthetic_progress_run_123456", kind=kind, observation=observation)
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
        assert not partial["complete"] and len(partial["missing"]) == 1 and not partial["errors"] and len(partial["records"]) == 8
        assert collect()["errors"]
        put(first, samples[first])
        negatives = []
        for label, mutate in [
            ("wrong run", lambda v: v.update(run_id="wrong")),
            ("extra envelope field", lambda v: v.update(extra=1)),
            ("wrong kind", lambda v: v.update(kind="unknown")),
            ("missing first sample", lambda v: v["observation"]["samples"].pop(0)),
            ("out of order samples", lambda v: v["observation"]["samples"].reverse()),
            ("nonfinite numeric sample", lambda v: v["observation"]["samples"][0].update(opacity=float("inf"))),
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
