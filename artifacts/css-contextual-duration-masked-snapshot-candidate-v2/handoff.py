import copy
import hashlib
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(directory, digest):
    assert sha(directory / "FILES.json") == digest
    records = read(directory / "FILES.json")
    for name, record in records.items():
        path = directory / name
        assert not path.is_symlink() and path.is_file(), name
        assert sha(path) == (record["sha256"] if isinstance(record, dict) else record), name
        if isinstance(record, dict):
            assert path.stat().st_size == record["bytes"]
    return records


def validate(root, policy, original, overrides=None):
    binding = policy["restoration_handoff"]
    def pinned(key):
        pin = binding[key]
        assert policy["references"][pin["path"]] == sha(root / pin["path"]) == pin["sha256"]
        return read(root / pin["path"])
    admission = pinned("admission")
    terminal = pinned("terminal")
    refresh = pinned("refresh")
    header = pinned("new_header_provenance")
    runtime = root / binding["runtime"]
    records = authenticate(runtime, binding["runtime_manifest_sha256"])
    authenticate(root / binding["owner"]["directory"], binding["owner"]["manifest_sha256"])
    saved = {name: read(runtime / name) for name in (
        "CANDIDATE-PRE.json", "POST.json", "RESTORATION.json", "CANDIDATE-RESULT.json",
        "BACKUP-CLEANUP.json", "ROOT-BACKUP-CLEANUP.json", "candidate-build/build-RESULT.json")}
    if overrides is not None:
        admission = overrides.get("admission", admission)
        terminal = overrides.get("terminal", terminal)
        refresh = overrides.get("refresh", refresh)
        saved.update(overrides.get("saved", {}))
    roles = read(root / policy["owner_directory"] / "SOURCE-ROLES.json")
    assert admission["head"] == policy["head"] == original["head"]
    assert admission["controls"] == policy["controls"]
    assert admission["prepared_flag_hashes"] == policy["prepared_flag_hashes"]
    assert admission["accepted_current_payloads"] == policy["accepted_current_payloads"] == original["accepted_current_payloads"]
    assert len(admission["accepted_current_payloads"]) == 29
    assert admission["source_role_pins"] == {name: role["base_sha256"] for name, role in roles.items()}
    assert all(admission[key] for key in ("full_current_state_verified", "source_transition_lock_absent", "owned_processes_absent"))
    assert admission["native_acceptance_increment"] == 0
    assert admission["restored_runtime"] == binding["runtime"]
    assert admission["restored_runtime_manifest"] == binding["runtime_manifest_sha256"]
    assert admission["restoration_binding"] == {key: binding[key] for key in ("terminal", "refresh")}
    verified = admission["full_state_verification"]
    assert (verified["session_id"], verified["terminal_chunk"], verified["exit"]) == (79160, "326118", 0)
    assert policy["references"][verified["log"]] == sha(root / verified["log"]) == verified["log_sha256"]
    current_app = admission["prepared_application_metadata"]
    expected_app = copy.deepcopy(original["prepared_application_metadata"])
    for key in ("entry_identity", "identity"):
        expected_app[key] = current_app[key]
    assert expected_app == current_app
    assert {key: value for key, value in current_app.items() if key not in ("build_revision", "harness_revision", "source_role")} == policy["prepared_application_metadata"]
    assert terminal["restored_application_entry"]["identity"] == current_app["entry_identity"]
    assert terminal["restored_application_entry"]["target"] == current_app["symlink_target"]
    assert terminal["restored_application_target"]["identity"] == current_app["identity"]
    assert terminal["restored_application_target"]["sha256"] == current_app["sha256"]
    assert (terminal["session_id"], terminal["terminal_chunk"], terminal["exit"]) == (33133, "e369a3", 1)
    assert terminal["owner_sha256"] == binding["owner"]["manifest_sha256"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    assert terminal["build_exit"] == 2 and terminal["comparison_gate_passed"] is None
    assert not any(terminal[key] for key in ("build_success", "browser_executed", "observation_complete", "native_acceptance"))
    assert terminal["owner_failure_preserved"] and terminal["state_and_application_restoration_independently_verified"]
    result = saved["CANDIDATE-RESULT.json"]
    assert not result["success"] and result["error"] == "AssertionError()" and result["candidate_phase"] is None
    assert result["restoration_verified"] and result["runtime_controls_unchanged"] and result["empty_staging_preserved"]
    assert result["publication_errors"] == [] and not result["native_fix_acceptance"]
    build = saved["candidate-build/build-RESULT.json"]
    assert build["exit"] == 2 and build["owned_group_absent"] and build["cleanup_errors"] == []
    assert build["error"] is None and build["stop_reason"] is None
    assert not any(name.startswith("candidate-wpt/") for name in records)
    pre, post = saved["CANDIDATE-PRE.json"], saved["POST.json"]
    historical = read(root / policy["baseline_binding"]["directory"] / "POST.json")
    assert pre["controls"] == original["controls"] and pre["snapshot"] == historical
    projected = copy.deepcopy(historical)
    projected["index"]["raw_index"] = post["index"]["raw_index"]
    assert projected == post == admission["snapshot"]
    assert admission["raw_index"] == post["index"]["raw_index"]
    restoration = saved["RESTORATION.json"]
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    assert set(restoration["sources"]) == set(pre["sources"]) == set(roles) - {"layout/style/GeckoBindings.h"}
    for name, restored in restoration["sources"].items():
        assert restored == {"identity": pre["sources"][name]["identity"], "sha256": roles[name]["base_sha256"]}
        assert pre["sources"][name]["base_sha256"] == roles[name]["base_sha256"]
    retained, removed = saved["BACKUP-CLEANUP.json"], saved["ROOT-BACKUP-CLEANUP.json"]
    assert not retained["removed"] and retained["retained_after_failure"] and retained["verified_original_restoration"]
    assert all(removed[key] for key in ("inventory_verified_before_removal", "owner_failure_receipt_preserved", "removed", "verified_original_restoration"))
    assert retained["owned_backup_bytes"] == removed["owned_backup_bytes"] == terminal["backup_removed_bytes"] == pre["owned_backup_bytes"] == 1008605176
    assert refresh["before_epoch"] == original["controls"]["CURRENT-EPOCH.json"]
    assert refresh["after_epoch"] == policy["controls"]["CURRENT-EPOCH.json"]
    assert refresh["full_restored_state_verified"] and refresh["accepted_fix_increment"] == 0
    assert refresh["only_changed_field"] == "raw_index_observation.current"
    assert refresh["runtime_manifest_sha256"] == binding["runtime_manifest_sha256"]
    assert refresh["observation"] == terminal["raw_index_observation"] == {
        "before": historical["index"]["raw_index"], "after": admission["raw_index"],
        "canonical_updated": False, "semantic_index_unchanged": True}
    assert all(policy["controls"][name] == original["controls"][name] for name in ("OWNED.json", "ROLE.json"))
    name = "layout/style/GeckoBindings.h"
    assert header["path"] == name and header["sha256"] == header["original_build_pin"] == roles[name]["base_sha256"]
    assert header["committed_versions"] == {revision: header["sha256"] for revision in (policy["head"], current_app["build_revision"])}
    assert header["bytes"] == (root / roles[name]["base_capture"]).stat().st_size
    assert not header["native_mutated"] and not header["git_mutated"]
