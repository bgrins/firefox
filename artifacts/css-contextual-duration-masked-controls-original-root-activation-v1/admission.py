import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def validate(policy):
    predecessor = ROOT / policy["predecessor"]["directory"]
    assert sha(predecessor / "FILES.json") == policy["predecessor"]["manifest_sha256"]
    for name, pin in read(predecessor / "FILES.json").items():
        assert sha(predecessor / name) == (pin if isinstance(pin, str) else pin["sha256"]), name
    previous = read(predecessor / "POLICY.json")
    for key in ("source_role_pins", "accepted_current_payloads", "build_epoch", "rebuilt_binaries", "build_unpinned_sources", "deferred_nonartifact_references"):
        assert policy[key] == previous[key], key
    runtime = ROOT / policy["restored_runtime"]
    assert sha(runtime / "FILES.json") == policy["restored_runtime_manifest"]
    for name, pin in read(runtime / "FILES.json").items():
        assert sha(runtime / name) == (pin if isinstance(pin, str) else pin["sha256"]), name
    terminal = read(runtime / "ROOT-TERMINAL.json")
    assert (terminal["session_id"], terminal["terminal_chunk"], terminal["exit"]) == (29079, "6c7cd1", 1)
    assert terminal["state_and_application_restoration_independently_verified"] and not terminal["native_acceptance"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    result = read(runtime / "CANDIDATE-RESULT.json")
    assert not result["success"] and result["restoration_verified"] and result["runtime_controls_unchanged"]
    assert result["publication_errors"] == [] and result["empty_staging_preserved"]
    restored = read(runtime / "RESTORATION.json")
    assert restored["errors"] == [] and restored["owned_processes"] == {}
    assert set(restored["sources"]) == {"servo/components/style/matching.rs", "dom/animation/EffectCompositor.cpp", "dom/animation/EffectCompositor.h", "layout/style/nsAnimationManager.cpp"}
    before = read(runtime / "CANDIDATE-PRE.json")
    for name, record in restored["sources"].items():
        assert record["sha256"] == policy["source_role_pins"][name]
        assert record["identity"] == before["sources"][name]["identity"]
    cleanup = read(runtime / "ROOT-BACKUP-CLEANUP.json")
    assert cleanup["removed"] and cleanup["verified_original_restoration"]
    assert cleanup["inventory_verified_before_removal"] and cleanup["owner_failure_receipt_preserved"]
    assert cleanup["owned_backup_bytes"] == terminal["backup_removed_bytes"] == 1008605176
    for record in policy["restoration_binding"].values():
        assert policy["references"][record["path"]] == sha(ROOT / record["path"]) == record["sha256"]
    refresh = read(ROOT / policy["restoration_binding"]["refresh"]["path"])
    assert refresh["runtime_manifest_sha256"] == policy["restored_runtime_manifest"]
    assert refresh["full_restored_state_verified"] and refresh["accepted_fix_increment"] == 0
    assert refresh["only_changed_field"] == "raw_index_observation.current"
    assert refresh["observation"] == terminal["raw_index_observation"]
    if policy["fresh_admission"] is None:
        assert not policy["execution_enabled"] and policy["activation_pending"]
        assert all(policy[key] is None for key in ("head", "controls", "prepared_application_metadata"))
        assert policy["wpt"]["harness_revision"] is None
        return
    pin = policy["fresh_admission"]
    assert policy["references"][pin["path"]] == sha(ROOT / pin["path"]) == pin["sha256"]
    fresh = read(ROOT / pin["path"])
    assert fresh["full_current_state_verified"] and fresh["source_transition_lock_absent"]
    assert fresh["owned_processes_absent"] and fresh["native_acceptance_increment"] == 0
    assert fresh["source_role_pins"] == policy["source_role_pins"]
    assert fresh["accepted_current_payloads"] == policy["accepted_current_payloads"]
    assert fresh["restored_runtime_manifest"] == policy["restored_runtime_manifest"]
    for key in ("head", "controls", "prepared_application_metadata"):
        assert policy[key] == fresh[key]
    assert set(fresh["controls"]) == {"CURRENT-EPOCH.json", "OWNED.json", "ROLE.json"}
    assert fresh["snapshot"]["index"]["head"] == fresh["head"] == policy["wpt"]["harness_revision"]
    assert fresh["snapshot"]["index"]["raw_index"] == fresh["raw_index"]
    signing = fresh["signer_terminal"]
    assert policy["references"][signing["path"]] == sha(ROOT / signing["path"]) == signing["sha256"]
    app = policy["prepared_application_metadata"]
    historical = previous["prepared_application_metadata"]
    assert {k: v for k, v in app.items() if k not in ("entry_identity", "identity", "harness_revision")} == {k: v for k, v in historical.items() if k not in ("entry_identity", "identity", "harness_revision")}
    assert app["entry_identity"] == terminal["restored_application_entry"]["identity"]
    assert app["identity"] == terminal["restored_application_target"]["identity"]
    assert app["sha256"] == terminal["restored_application_target"]["sha256"]
    assert app["harness_revision"] == fresh["head"]
    assert policy["wpt"]["phase_revisions"] == {"original": app["revision"]}
    assert policy["activation_pending"] == ([] if policy["execution_enabled"] else ["root review and activation"])
