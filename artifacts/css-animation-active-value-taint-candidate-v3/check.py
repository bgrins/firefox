import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    roles = read(HERE / "SOURCE-ROLES.json")
    assert set(roles) == set(policy["source_paths"]) == {
        "servo/components/style/custom_properties.rs",
        "servo/components/style/custom_properties_map.rs",
        "servo/components/style/properties/cascade.rs",
        "servo/components/style/properties_and_values/value.rs",
    }
    proposal = ROOT / policy["proposal"]["directory"]
    assert sha(proposal / "FILES.json") == policy["proposal"]["manifest_sha256"]
    assert roles == read(proposal / "SOURCE-ROLES.json")
    built = read(ROOT / policy["original_build"]["epoch"])
    for name, record in roles.items():
        for kind in ("base", "candidate"):
            assert sha(ROOT / record[kind + "_capture"]) == record[kind + "_sha256"]
        if name in built["pins"]:
            assert built["pins"][name] == record["base_sha256"]
        else:
            assert name == "servo/components/style/custom_properties_map.rs"
        assert (name in built["modified_native_paths"]) == (name == "servo/components/style/custom_properties.rs")
        expected = "8a4adc903e7d88e218ee087cbe44cc3548df70fac9353dd923d5c32de2c458f9" if name.endswith("/custom_properties.rs") else record["base_sha256"]
        assert policy["committed_source_preimages"][name] == expected
    validate_lineage(policy, roles)
    for name, digest in policy["references"].items():
        assert sha(ROOT / name) == digest, name
    if policy["baseline_capsule"] is None:
        assert policy["wpt"] is None and policy["baseline_binding"] is None
        assert not policy["execution_enabled"] and not policy["candidate_execution_enabled"]
        return
    comparison = load("taint_pair_replay", HERE / "comparison.py")
    original = comparison.source_policy(ROOT, policy)
    assert policy["wpt"] == comparison.expected_wpt(ROOT, policy)
    assert not policy["wpt"]["candidate_required_pass_pages"] and policy["wpt"]["target_subtests"] == {}
    assert policy["source_context_pins"] == original["source_role_pins"]
    assert policy["accepted_current_payloads"] == original["accepted_current_payloads"]
    assert len(policy["accepted_current_payloads"]) == 29
    if policy["baseline_binding"] is None:
        assert not policy["execution_enabled"] and not policy["candidate_execution_enabled"]
        assert policy["activation_pending"]
        assert all(policy[key] is None for key in ("head", "controls", "prepared_application_metadata", "prepared_flag_hashes"))
    else:
        validate_actual_bindings(policy)


def validate_lineage(policy, roles, receipt=None):
    binding = policy["source_equivalence"]
    assert policy["references"][binding["path"]] == sha(ROOT / binding["path"]) == binding["sha256"]
    observed = read(ROOT / binding["path"]) if receipt is None else receipt
    built = read(ROOT / policy["original_build"]["epoch"])
    assert observed["original_build_revision"] == built["semantic_index"]["head"]
    assert observed["head"] == read(ROOT / policy["native_checkpoint"]["path"])["head"]
    assert set(observed["sources"]) == set(roles)
    for name, role in roles.items():
        row = observed["sources"][name]
        assert row["working_sha256"] == role["base_sha256"]
        assert row["head_sha256"] == row["original_build_revision_sha256"] == policy["committed_source_preimages"][name]
        assert len(row["identity"]) == 2 and all(isinstance(v, int) and v > 0 for v in row["identity"])


def validate_actual_bindings(policy):
    comparison = load("taint_actual_replay", HERE / "comparison.py")
    original = comparison.source_policy(ROOT, policy)
    assert policy["baseline_binding"] is not None
    load("taint_failed_restore", HERE / "handoff.py").validate(ROOT, policy, original)
    flag = policy["prepared_flag_capture"]
    assert policy["references"][flag["path"]] == sha(ROOT / flag["path"]) == flag["sha256"]
    assert read(ROOT / flag["path"]) == policy["prepared_flag_hashes"]
    assert set(policy["prepared_flag_hashes"]) == {"root", "nested"}
    assert policy["source_equivalence"] is not None
    comparison.replay_all(ROOT, policy)


def check():
    policy = read(HERE / "POLICY.json")
    validate_policy(policy)
    handoff = load("taint_handoff_negative_checks", HERE / "handoff.py")
    runtime = ROOT / policy["restoration_handoff"]["runtime"]
    original_policy = read(ROOT / policy["baseline_capsule"]["directory"] / "POLICY.json")
    saved = {name: read(runtime / name) for name in (
        "ROOT-CURRENT.json", "ROOT-TERMINAL.json", "ROOT-EPOCH-REFRESH.json",
        "ROOT-BACKUP-CLEANUP.json", "RESTORATION.json", "CANDIDATE-RESULT.json",
        "CANDIDATE-PRE.json", "POST.json", "ROOT-FLAGS.json", "BACKUP-CLEANUP.json",
        "RAW-INDEX-OBSERVATION.json", "candidate-build/build-RESULT.json")}
    mutations = (
        lambda x: x["ROOT-CURRENT.json"]["prepared_application_metadata"].update(sha256="0" * 64),
        lambda x: x["ROOT-CURRENT.json"]["prepared_application_metadata"].update(identity=[0, 0]),
        lambda x: x["ROOT-CURRENT.json"]["snapshot"]["nested_index"].update(raw_index="0" * 64),
        lambda x: x["ROOT-CURRENT.json"]["source_role_pins"].update({"servo/components/style/custom_properties.rs": "0" * 64}),
        lambda x: x["RESTORATION.json"].update(errors=["unrestored"]),
        lambda x: x["candidate-build/build-RESULT.json"].update(exit=0),
        lambda x: x["ROOT-BACKUP-CLEANUP.json"].update(removed=False),
        lambda x: x["ROOT-CURRENT.json"]["controls"].update({"ROLE.json": "0" * 64}),
        lambda x: x["ROOT-FLAGS.json"].update(root="0" * 64),
        lambda x: x["CANDIDATE-RESULT.json"].update(success=True),
    )
    for mutate in mutations:
        bad = copy.deepcopy(saved)
        mutate(bad)
        try:
            handoff.validate(ROOT, policy, original_policy, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("invalid failed-restoration handoff admitted")
    lineage = read(ROOT / policy["source_equivalence"]["path"])
    roles = read(HERE / "SOURCE-ROLES.json")
    for mutate in (
        lambda r: r["sources"].pop("servo/components/style/custom_properties_map.rs"),
        lambda r: r["sources"]["servo/components/style/custom_properties.rs"].update(head_sha256=roles["servo/components/style/custom_properties.rs"]["base_sha256"]),
        lambda r: r["sources"]["servo/components/style/properties_and_values/value.rs"].update(working_sha256="0" * 64),
    ):
        bad = copy.deepcopy(lineage)
        mutate(bad)
        try:
            validate_lineage(policy, roles, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("invalid source lineage admitted")
    if policy["baseline_capsule"] is None:
        print("Disabled source recipe checked; exact original roster pending")
        return
    original = load("masked_original_checks", ROOT / policy["baseline_capsule"]["directory"] / "check.py")
    original.check(read(ROOT / policy["baseline_capsule"]["directory"] / "POLICY.json"))
    checks = load("masked_base_stream_checks", ROOT / policy["wpt"]["checks_helper"])
    assessor = load("masked_observation_assessor", HERE / "assess.py")
    comparison = load("masked_test_projection", HERE / "comparison.py")
    settings = copy.deepcopy(policy["wpt"])
    settings.update(harness_revision="a" * 40, phase_revisions={"original": "b" * 40, "candidate": "a" * 40})
    app = {"browser_build_id": "synthetic", "revision": "b" * 40, "build_revision": "b" * 40, "harness_revision": "a" * 40, "source_role": "original", "sha256": "c" * 64, "path": "synthetic/application.ini", "resolved": "synthetic/application.ini"}
    events = [{"action": "suite_start", "run_info": {"os": "mac", "debug": False, "browser_build_id": "synthetic", "revision": "a" * 40}}]
    for page, names in settings["expected_subtests"].items():
        events.append({"action": "test_start", "test": page})
        events.extend({"action": "test_status", "test": page, "subtest": name, "status": "PASS"} for name in names)
        events.append({"action": "test_end", "test": page, "status": "OK"})
    events.append({"action": "suite_end"})
    config = comparison.phase_policy(settings)
    baseline = assessor.assess(events, 0, config, checks, run_binding=app)
    assert baseline["complete"]
    candidate_app = dict(app, revision="a" * 40, build_revision="a" * 40, source_role="candidate")
    failed = copy.deepcopy(events)
    rows = [row for row in failed if row.get("action") == "test_status"]
    for row in rows:
        row.update(status="FAIL", expected="PASS", message="synthetic ordinary assertion")
    observed = assessor.assess(failed, 1, config, checks, original=baseline, run_binding=candidate_app)
    assert observed["complete"] and not observed["comparison_gate_passed"] and len(observed["rows"]) == policy["wpt"]["expected_subtest_count"]
    assert all(row["status"] == "FAIL" for row in observed["rows"])
    phases_check(policy, baseline, observed)
    print(json.dumps({"references": len(policy["references"]), "all_failed_comparison_preserved": True, "actual_baseline_pending": policy["baseline_binding"] is None, "browser_or_build_executed": False}))


def phases_check(policy, baseline, observed):
    import tempfile
    from types import SimpleNamespace
    module = load("masked_phase_test", HERE / "phases.py")
    with tempfile.TemporaryDirectory(prefix="css-masked-phase-", dir="/private/tmp") as temporary:
        root = Path(temporary)
        output = root / "candidate"
        phase = output / "candidate-wpt"
        phase.mkdir(parents=True)
        (output / "candidate-build").mkdir()
        original = root / "original/original-wpt"
        original.mkdir(parents=True)
        def save(path, value):
            path.write_text(json.dumps(value))
        save(original / "ASSESSMENT.json", baseline)
        snapshot = {"synthetic": True}
        for name in ("PRE.json", "POST.json"):
            save(phase / name, snapshot)
        for name in ("APPLICATION-METADATA.json", "APPLICATION-METADATA-POST.json"):
            save(phase / name, {"synthetic": "app"})
        save(phase / "BINARY-PINS.json", {"synthetic": "binary"})
        save(output / "candidate-build/RESULT.json", {"binaries": {"synthetic": "binary"}})
        save(phase / "ASSESSMENT.json", observed)
        receipt = {"synthetic": "completed observation with all FAIL"}
        module.load = lambda *args: SimpleNamespace(save=save, run=lambda *args: receipt)
        configured = dict(policy, baseline_binding={"directory": "original"})
        assert module.run(root, HERE, output, configured, {}, lambda: snapshot, {}, lambda: False) == receipt
        outcomes = read(output / "OUTCOMES.json")
        assert outcomes["callbacks_failed"] == policy["wpt"]["expected_subtest_count"] and not outcomes["all_callbacks_passed"] and not outcomes["comparison_gate_passed"] and not outcomes["native_acceptance"]
        assert len(outcomes["rows"]) == policy["wpt"]["expected_subtest_count"] and len(outcomes["candidate_endings"]) == policy["wpt"]["expected_page_count"]
    assert not root.exists()


if __name__ == "__main__":
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
