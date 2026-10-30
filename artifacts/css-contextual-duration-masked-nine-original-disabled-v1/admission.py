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
    assert sha(ROOT / policy["restored_owner"] / "FILES.json") == terminal["owner_sha256"]
    assert terminal["state_and_application_restoration_independently_verified"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    result = read(runtime / "CANDIDATE-RESULT.json")
    assert result["restoration_verified"] and result["runtime_controls_unchanged"]
    assert result["publication_errors"] == [] and result["empty_staging_preserved"]
    assert not result["native_fix_acceptance"]
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
