import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def package(directory, expected):
    directory = ROOT / directory
    assert sha(directory / "FILES.json") == expected
    for name, pin in read(directory / "FILES.json").items():
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        path = directory / relative
        assert not path.is_symlink() and path.is_file()
        assert sha(path) == (pin if isinstance(pin, str) else pin["sha256"]), name


def pinned(policy, record):
    assert policy["references"][record["path"]] == sha(ROOT / record["path"]) == record["sha256"]
    return read(ROOT / record["path"])


def validate(policy):
    if "preserved_disabled" in policy:
        saved = policy["preserved_disabled"]
        package(saved["directory"], saved["manifest_sha256"])
        for name in ("run.py", "assess.py", "check.py"):
            assert sha(ROOT / saved["directory"] / name) == sha(Path(__file__).resolve().parent / name)
    predecessor = policy["predecessor"]
    package(predecessor["directory"], predecessor["manifest_sha256"])
    previous = read(ROOT / predecessor["directory"] / "POLICY.json")
    for key in ("source_role_pins", "accepted_current_payloads", "build_epoch", "rebuilt_binaries", "build_unpinned_sources", "deferred_nonartifact_references"):
        assert policy[key] == previous[key], key
    assert policy["original_only"] and not policy["candidate_execution_enabled"]
    if policy["fresh_admission"] is None:
        assert not policy["execution_enabled"] and policy["activation_pending"]
        assert all(policy[key] is None for key in ("head", "controls", "prepared_application_metadata", "restored_runtime", "restored_runtime_manifest", "restoration_binding", "restored_owner"))
        assert policy["wpt"]["harness_revision"] is None
        assert policy["wpt"]["phase_revisions"] == {"original": None}
        return
    fresh = pinned(policy, policy["fresh_admission"])
    assert fresh["full_current_state_verified"] and fresh["source_transition_lock_absent"]
    assert fresh["owned_processes_absent"] and fresh["native_acceptance_increment"] == 0
    assert fresh["source_role_pins"] == policy["source_role_pins"]
    assert fresh["accepted_current_payloads"] == policy["accepted_current_payloads"]
    for key in ("head", "controls", "prepared_application_metadata", "restored_runtime_manifest"):
        assert policy[key] == fresh[key]
    assert set(fresh["controls"]) == {"CURRENT-EPOCH.json", "OWNED.json", "ROLE.json"}
    assert fresh["snapshot"]["index"]["head"] == fresh["head"] == policy["wpt"]["harness_revision"]
    assert fresh["snapshot"]["index"]["raw_index"] == fresh["raw_index"]
    package(policy["restored_runtime"], policy["restored_runtime_manifest"])
    runtime = ROOT / policy["restored_runtime"]
    terminal = pinned(policy, policy["restoration_binding"]["terminal"])
    assert terminal == read(runtime / "ROOT-TERMINAL.json")
    package(policy["restored_owner"], terminal["owner_sha256"])
    assert (terminal["session_id"], terminal["terminal_chunk"], terminal["exit"], terminal["browser_exit"]) == (44603, "98abc4", 0, 1)
    assert terminal["build_success"] and terminal["observation_complete"] and terminal["raw_replay_verified"]
    assert not terminal["all_callbacks_passed"] and not terminal["comparison_gate_passed"] and not terminal["native_acceptance"]
    assert (terminal["callbacks_passed"], terminal["callbacks_failed"], terminal["page_endings_ok"]) == (5, 2, 2)
    assert terminal["state_and_application_restoration_independently_verified"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    result = read(runtime / "CANDIDATE-RESULT.json")
    assert result["success"] and result["error"] is None
    assert result["success_scope"] == terminal["success_scope"] == "build, complete observation and restoration; callback PASS is separate"
    assert result["restoration_verified"] and result["runtime_controls_unchanged"]
    assert result["publication_errors"] == [] and result["empty_staging_preserved"]
    assert not result["native_fix_acceptance"]
    for key, filename in (("raw_sha256", "raw.jsonl"), ("assessment_sha256", "ASSESSMENT.json"), ("result_sha256", "RESULT.json")):
        assert result["candidate_phase"][key] == sha(runtime / "candidate-wpt" / filename)
    phase = read(runtime / "candidate-wpt/RESULT.json")
    assert phase["exit"] == 1 and phase["success"] and phase["preservation_verified"]
    assert not phase["comparison_gate_passed"] and phase["execution_error"] is None
    assessment = read(runtime / "candidate-wpt/ASSESSMENT.json")
    assert assessment["complete"] and assessment["observed_subtest_count"] == 7
    assert sum(row["status"] == "PASS" for row in assessment["rows"]) == 5
    assert {row["subtest"] for row in assessment["rows"] if row["status"] == "FAIL"} == {
        "Masked font element: outline preserves timing and output",
        "Masked font ::before: outline preserves timing and output",
    }
    assert len(assessment["ends"]) == 2 and all(row["status"] == "OK" for row in assessment["ends"])
    outcomes = read(runtime / "OUTCOMES.json")
    assert (outcomes["callbacks_passed"], outcomes["callbacks_failed"]) == (5, 2)
    assert not outcomes["all_callbacks_passed"] and not outcomes["comparison_gate_passed"]
    assert outcomes["comparison_errors"] == assessment["comparison_errors"]
    cleanup = read(runtime / "BACKUP-CLEANUP.json")
    assert cleanup["removed"] and cleanup["verified_original_restoration"] and not cleanup["retained_after_failure"]
    assert cleanup["owned_backup_bytes"] == terminal["backup_removed_bytes"] == 1008605176
    restored = read(runtime / "RESTORATION.json")
    assert restored["errors"] == [] and restored["owned_processes"] == {}
    before = read(runtime / "CANDIDATE-PRE.json")
    assert set(restored["sources"]) == {"servo/components/style/matching.rs"}
    for name, record in restored["sources"].items():
        assert record["sha256"] == policy["source_role_pins"][name]
        assert record["identity"] == before["sources"][name]["identity"]
    refresh = pinned(policy, policy["restoration_binding"]["refresh"])
    assert refresh["runtime_manifest_sha256"] == policy["restored_runtime_manifest"]
    assert refresh["full_restored_state_verified"] and refresh["accepted_fix_increment"] == 0
    assert refresh["only_changed_field"] == "raw_index_observation.current"
    assert refresh["observation"] == terminal["raw_index_observation"]
    assert refresh["after_epoch"] == fresh["controls"]["CURRENT-EPOCH.json"]
    assert refresh["observation"]["after"] == fresh["raw_index"]
    verification = fresh["full_state_verification"]
    assert (verification["session_id"], verification["terminal_chunk"], verification["exit"]) == (56092, "4312c9", 0)
    assert policy["references"][verification["log"]] == sha(ROOT / verification["log"]) == verification["log_sha256"]
    post = read(runtime / "POST.json")
    assert fresh["snapshot"] == post
    app = policy["prepared_application_metadata"]
    historical = previous["prepared_application_metadata"]
    identities = ("entry_identity", "identity", "harness_revision")
    assert {k: v for k, v in app.items() if k not in identities} == {k: v for k, v in historical.items() if k not in identities}
    assert app["entry_identity"] == terminal["restored_application_entry"]["identity"]
    assert app["identity"] == terminal["restored_application_target"]["identity"]
    assert app["sha256"] == terminal["restored_application_target"]["sha256"]
    assert app["harness_revision"] == fresh["head"]
    assert policy["wpt"]["phase_revisions"] == {"original": app["revision"]}
    assert policy["activation_pending"] == ([] if policy["execution_enabled"] else ["root review and activation"])
