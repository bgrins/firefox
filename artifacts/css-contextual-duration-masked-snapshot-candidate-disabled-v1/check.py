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
    comparison = load("masked_pair_replay", HERE / "comparison.py")
    original = comparison.source_policy(ROOT, policy)
    assert policy["wpt"] == comparison.expected_wpt(ROOT, policy)
    assert not policy["wpt"]["candidate_required_pass_pages"]
    assert policy["wpt"]["target_subtests"] == {}
    assert (policy["wpt"]["expected_subtest_count"], policy["wpt"]["expected_page_count"]) == (9, 4)
    assert policy["source_context_pins"] == original["source_role_pins"]
    assert policy["accepted_current_payloads"] == original["accepted_current_payloads"] and len(policy["accepted_current_payloads"]) == 29
    roles = read(HERE / "SOURCE-ROLES.json")
    assert set(roles) == set(policy["source_paths"]) == {'layout/style/nsAnimationManager.cpp', 'layout/style/AnimationCollection.h', 'layout/style/ServoTypes.h', 'servo/components/style/context.rs', 'layout/style/GeckoBindings.cpp', 'servo/components/style/matching.rs', 'layout/style/nsAnimationManager.h'}
    proposal = ROOT / policy["proposal"]["directory"]
    assert sha(proposal / "FILES.json") == policy["proposal"]["manifest_sha256"]
    saved = read(proposal / "SOURCE-ROLES.json")
    assert roles == saved
    validate_lineage(policy, roles)
    for name, digest in policy["references"].items():
        assert sha(ROOT / name) == digest, name
    if policy["baseline_binding"] is None:
        assert not policy["execution_enabled"] and not policy["candidate_execution_enabled"]
        assert policy["activation_pending"]
        assert all(policy[key] is None for key in ("head", "controls", "prepared_application_metadata", "prepared_flag_hashes"))
    else:
        validate_actual_bindings(policy)


def validate_lineage(policy, roles, observed=None):
    pin = policy["source_equivalence"]
    assert policy["references"][pin["path"]] == sha(ROOT / pin["path"]) == pin["sha256"]
    receipt = read(ROOT / pin["path"]) if observed is None else observed
    original = read(ROOT / policy["baseline_capsule"]["directory"] / "POLICY.json")
    built = read(ROOT / policy["original_build"]["epoch"])
    assert receipt["head"] == original["head"]
    assert receipt["original_build_revision"] == built["semantic_index"]["head"] == original["wpt"]["phase_revisions"]["original"]
    assert receipt["original_build_epoch_sha256"] == sha(ROOT / policy["original_build"]["epoch"])
    assert receipt["roles_sha256"] == sha(HERE / "SOURCE-ROLES.json")
    unpinned = {name for name in roles if name not in built["pins"]}
    assert set(receipt["sources"]) == unpinned
    assert set(policy["build_unpinned_sources"]) == set(original["build_unpinned_sources"]) | unpinned
    for name, role in roles.items():
        assert name not in built["modified_native_paths"]
        if name not in unpinned:
            assert built["pins"][name] == role["base_sha256"]
            continue
        source = receipt["sources"][name]
        assert source["matches_proposal_base"]
        assert source["sha256"] == role["base_sha256"]
        assert source["bytes"] == (ROOT / role["base_capture"]).stat().st_size
        assert source["committed_versions"] == {revision: role["base_sha256"] for revision in (receipt["head"], receipt["original_build_revision"])}
    assert not receipt["git_mutated"] and not receipt["native_mutated"]


def validate_actual_bindings(policy):
    comparison = load("masked_actual_replay", HERE / "comparison.py")
    original = comparison.source_policy(ROOT, policy)
    assert policy["baseline_binding"] is not None
    assert policy["head"] == original["head"]
    assert policy["controls"] == original["controls"]
    assert policy["prepared_application_metadata"] == {key: value for key, value in original["prepared_application_metadata"].items() if key not in ("build_revision", "harness_revision", "source_role")}
    flag_capture = policy["prepared_flag_capture"]
    assert policy["references"][flag_capture["path"]] == sha(ROOT / flag_capture["path"]) == flag_capture["sha256"]
    assert read(ROOT / flag_capture["path"]) == policy["prepared_flag_hashes"]
    assert set(policy["prepared_flag_hashes"]) == {"root", "nested"}
    assert all(isinstance(value, str) and len(value) == 64 for value in policy["prepared_flag_hashes"].values())
    comparison.replay_all(ROOT, policy)


def check():
    policy = read(HERE / "POLICY.json")
    validate_policy(policy)
    roles = read(HERE / "SOURCE-ROLES.json")
    lineage = read(ROOT / policy["source_equivalence"]["path"])
    for mutate in (
        lambda r: r["sources"].pop(next(iter(r["sources"]))),
        lambda r: r.update(original_build_revision="0" * 40),
        lambda r: r["sources"][next(iter(r["sources"]))].update(committed_versions={}),
    ):
        bad = copy.deepcopy(lineage)
        mutate(bad)
        try:
            validate_lineage(policy, roles, bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("invalid source lineage admitted")
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
    assert observed["complete"] and not observed["comparison_gate_passed"] and len(observed["rows"]) == 9
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
        receipt = {"synthetic": "completed observation with nine FAIL"}
        module.load = lambda *args: SimpleNamespace(save=save, run=lambda *args: receipt)
        configured = dict(policy, baseline_binding={"directory": "original"})
        assert module.run(root, HERE, output, configured, {}, lambda: snapshot, {}, lambda: False) == receipt
        outcomes = read(output / "OUTCOMES.json")
        assert outcomes["callbacks_failed"] == 9 and not outcomes["all_callbacks_passed"] and not outcomes["comparison_gate_passed"] and not outcomes["native_acceptance"]
        assert len(outcomes["rows"]) == 9 and len(outcomes["candidate_endings"]) == 4
    assert not root.exists()


if __name__ == "__main__":
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
