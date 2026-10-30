import copy
import hashlib
import importlib.util
import json

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(root, policy, original, altered=None):
    binding = policy["restoration_handoff"]
    runtime = root / binding["runtime"]
    owner = root / binding["owner"]["directory"]
    ownership = load("taint_handoff_auth", root / policy["ownership_helper"])
    ownership.authenticate(runtime, binding["manifest_sha256"])
    ownership.authenticate(owner, binding["owner"]["manifest_sha256"])
    assert sha(root / binding["current"]["path"]) == binding["current"]["sha256"]
    saved = {name: read(runtime / name) for name in (
        "ROOT-CURRENT.json", "ROOT-TERMINAL.json", "ROOT-EPOCH-REFRESH.json",
        "ROOT-BACKUP-CLEANUP.json", "RESTORATION.json", "CANDIDATE-RESULT.json",
        "CANDIDATE-PRE.json", "POST.json", "ROOT-FLAGS.json", "BACKUP-CLEANUP.json",
        "RAW-INDEX-OBSERVATION.json", "candidate-build/build-RESULT.json")}
    if altered is not None:
        saved = altered
    current, terminal = saved["ROOT-CURRENT.json"], saved["ROOT-TERMINAL.json"]
    refresh, result = saved["ROOT-EPOCH-REFRESH.json"], saved["CANDIDATE-RESULT.json"]
    assert current["terminal"] == terminal and current["refresh"] == refresh
    assert (terminal["session_id"], terminal["terminal_chunk"], terminal["owner_exit"], terminal["build_exit"]) == (68749, "1404a8", 1, 2)
    assert terminal["browser_executed"] is False and terminal["native_acceptance"] is False
    assert terminal["restoration_independently_verified"] and terminal["owned_process_cleanup_verified"]
    assert terminal["owner_sha256"] == binding["owner"]["manifest_sha256"]
    assert terminal["result_sha256"] == sha(runtime / "CANDIDATE-RESULT.json")
    assert result["success"] is False and result["candidate_phase"] is None
    assert result["error"] == "AssertionError()" and result["publication_errors"] == []
    assert result["restoration_verified"] and result["runtime_controls_unchanged"] and result["empty_staging_preserved"]
    assert result["native_fix_acceptance"] is False and not (runtime / "candidate-wpt").exists()
    build = saved["candidate-build/build-RESULT.json"]
    assert build["exit"] == 2 and build["owned_group_absent"]
    assert build["cleanup_errors"] == [] and build["error"] is None and build["stop_reason"] is None
    restoration = saved["RESTORATION.json"]
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    cleanup = saved["ROOT-BACKUP-CLEANUP.json"]
    assert cleanup["removed"] and cleanup["verified_original_restoration"]
    assert cleanup["owned_backup_bytes"] == terminal["backup_removed_bytes"] == 1008605176
    earlier = saved["BACKUP-CLEANUP.json"]
    assert earlier["verified_original_restoration"] and earlier["retained_after_failure"] and not earlier["removed"]
    assert earlier["owned_backup_bytes"] == cleanup["owned_backup_bytes"]
    pre = saved["CANDIDATE-PRE.json"]
    original_runtime = root / policy["baseline_binding"]["directory"]
    assert pre["snapshot"] == read(original_runtime / "POST.json")
    assert pre["controls"] == original["controls"]
    assert current["head"] == policy["head"] == original["head"]
    assert refresh["before_epoch"] == original["controls"]["CURRENT-EPOCH.json"]
    assert refresh["after_epoch"] == policy["controls"]["CURRENT-EPOCH.json"]
    assert refresh["only_changed_field"] == "raw_index_observation.current"
    assert refresh["full_restored_state_verified"] and refresh["accepted_fix_increment"] == 0
    assert refresh["observation"] == saved["RAW-INDEX-OBSERVATION.json"]
    assert refresh["observation"]["semantic_index_unchanged"] and not refresh["observation"]["canonical_updated"]
    assert refresh["observation"]["before"] == pre["snapshot"]["index"]["raw_index"]
    expected = copy.deepcopy(pre["snapshot"])
    expected["index"]["raw_index"] = refresh["observation"]["after"]
    assert expected == saved["POST.json"] == current["snapshot"]
    assert current["controls"] == policy["controls"]
    for name in ("OWNED.json", "ROLE.json"):
        assert policy["controls"][name] == original["controls"][name]
    assert policy["prepared_application_metadata"] == current["prepared_application_metadata"]
    old_metadata = read(original_runtime / "original-wpt/APPLICATION-METADATA.json")
    omit = {"build_revision", "harness_revision", "source_role", "entry_identity", "identity"}
    assert {k:v for k,v in old_metadata.items() if k not in omit} == {k:v for k,v in current["prepared_application_metadata"].items() if k not in omit}
    assert current["prepared_flag_hashes"] == saved["ROOT-FLAGS.json"] == policy["prepared_flag_hashes"] == read(original_runtime / "ROOT-FLAGS.json")
    roles = read(root / policy["owner_directory"] / "SOURCE-ROLES.json")
    admission = read(root / policy["source_equivalence"]["path"])
    assert set(roles) == set(restoration["sources"]) == set(current["source_role_pins"]) == set(current["source_identities"])
    for name, role in roles.items():
        assert current["source_role_pins"][name] == role["base_sha256"]
        identity = pre["sources"][name]["identity"]
        assert identity == current["source_identities"][name] == admission["sources"][name]["identity"]
        assert restoration["sources"][name] == {"sha256": role["base_sha256"], "identity": identity}
