import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROL = ROOT / "artifacts/css-registered-number-native-runtime-v1"
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_policy(settings):
    result = dict(settings, tests={page: "testharness" for page in settings["expected_subtests"]}, held_subtests={})
    result["regression_subtests"] = {page: [name for name in names if name not in settings["target_subtests"].get(page, [])] for page, names in settings["expected_subtests"].items()}
    result["cardinality_description"] = "Exact sealed target and control names; existing control failures retain full signatures."
    return result



def validate_build_phase(policy, pre, built, metadata, metadata_after, snapshots, binaries):
    assert metadata == metadata_after
    assert metadata["revision"] == metadata["build_revision"] == policy["head"]
    assert metadata["harness_revision"] == policy["wpt"]["harness_revision"] == policy["head"]
    assert metadata["source_role"] == "candidate"
    assert policy["wpt"]["phase_revisions"]["candidate"] == policy["head"]
    assert all(snapshot == built["snapshot"] for snapshot in snapshots) and len(snapshots) >= 3
    assert binaries == built["binaries"] and set(binaries) == set(policy["rebuilt_binaries"])
    assert built["browser_build_performed"]
    assert built["snapshot"]["working_sources_binaries_research_preserved"]
    assert built["snapshot"]["current_raw_stable_during_check"]
    assert built["snapshot"]["nested_index"] == pre["snapshot"]["nested_index"]
    for key in ("head", "entries", "cached_diff"):
        assert built["snapshot"]["index"][key] == pre["snapshot"]["index"][key]



def summary_counts(observation):
    return {key:(observation.get("outcomes") or {}).get(key) for key in ("callbacks_passed", "callbacks_failed")}


def authenticate():
    config = read(HERE / "POLICY.json")
    for name, expected in read(HERE / "REFERENCES.json").items():
        assert sha(ROOT / name) == expected, name
    owner = ROOT / config["owner_directory"]
    assert sha(owner / "FILES.json") == config["owner_manifest_sha256"]
    for name, pin in read(owner / "FILES.json").items():
        assert sha(owner / name) == (pin["sha256"] if isinstance(pin, dict) else pin)
    return config, owner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    config, here = authenticate()
    if not args.verify:
        print("Saved owner payloads authenticated; no runtime or live state read")
        return
    assert config["execution_enabled"] and config["actual_terminal"] is not None
    terminal = config["actual_terminal"]
    assert terminal["session"] == config["expected_session"] == 72027
    assert terminal["exit"] in (0, 1) and terminal["terminal_chunk"]
    assert terminal["launch_chunk"] == config["expected_launch"] == "67e6f7"
    assert not config["mutations_allowed"] and not config["epoch_publication_allowed"]
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    pair = ROOT / config["runtime_directory"]
    inputs = {}
    def record(name):
        path = pair / name
        assert path.is_file() and not path.is_symlink()
        inputs[name] = sha(path)
        return read(path)
    result = record("CANDIDATE-RESULT.json")
    assert inputs["CANDIDATE-RESULT.json"] == terminal["result_sha256"]
    assert result["success"] == (terminal["exit"] == 0)
    assert result["restoration_verified"] and result["runtime_controls_unchanged"] and result["empty_staging_preserved"]
    assert result["native_fix_acceptance"] is False and result["publication_errors"] == []
    assert (result["error"] is None) == result["success"]
    baseline = load("terminal_baseline", here / "baseline.py")
    policy, ownership, roles = baseline.prepare(config["owner_manifest_sha256"])
    assert policy["runtime_output"] == config["runtime_directory"] and set(roles) == {"servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs"}
    assert roles["servo/components/style/custom_properties.rs"]["candidate_sha256"] == policy["committed_source_preimages"]["servo/components/style/custom_properties.rs"]
    state = load("terminal_state", ROOT / policy["state_helper"])
    bundle = load("terminal_bundle", ROOT / policy["bundle_helper"])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    pre = record("CANDIDATE-PRE.json")
    restoration = record("RESTORATION.json")
    backup = record("BACKUP-CLEANUP.json")
    inventory = record("BACKUPS.json")
    assert pre["controls"] == policy["controls"]
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    assert set(restoration["sources"]) == set(roles) == set(pre["sources"])
    admission = read(ROOT / policy["source_equivalence"]["path"])
    for name, role in roles.items():
        assert pre["sources"][name] == dict(role, identity=admission["sources"][name]["identity"])
    build = record("candidate-build/build-RESULT.json")
    command = record("candidate-build/COMMAND.json")
    assert command["owner_manifest"] == config["owner_manifest_sha256"]
    assert command["source_sha256"] == {name: role["candidate_sha256"] for name, role in roles.items()}
    assert command["command"] == ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "build", "binaries", "-j2"]
    assert build["owned_group_absent"] and build["cleanup_errors"] == []
    for name in ("build", "wake"):
        assert record("candidate-build/" + name + "-GROUP-CLEANUP.json")["owned_group_absent"]
    assert record("candidate-build/WAKE-RESULT.json")["owned_group_absent"]
    for name in ("build-PROCESS.json", "WAKE-PROCESS.json"):
        ownership.group_absent(record("candidate-build/" + name)["pgid"])
    lane_review = load("candidate74_observation_review", HERE / "observations.py")
    observation = lane_review.review(ROOT, HERE, pair, policy, pre, result, build, record, inputs, ownership, validate_build_phase)
    with (HERE / "RAW-REPLAY.json").open("x") as stream:
        json.dump(observation, stream, indent=2, sort_keys=True)
        stream.write("\n")
    baseline.metadata_guard(policy)
    assert {name: sha(CONTROL / name) for name in policy["controls"]} == policy["controls"]
    for name in policy["preserved_absent_metadata"] + policy["preserved_absent_resources"]:
        assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
    assert not (CONTROL / "SOURCE-TRANSITION.lock").exists() and not (CONTROL / "SOURCE-TRANSITION.lock").is_symlink()
    for name, role in roles.items():
        claim = restoration["sources"][name]
        assert claim == {"sha256": role["base_sha256"], "identity": pre["sources"][name]["identity"]}
        ownership.claim(ROOT, name, role["base_sha256"], claim["identity"])
    for name, pin in policy["accepted_current_payloads"].items():
        ownership.claim(ROOT, name, pin["sha256"], pin["identity"])
    for name, pin in policy["source_context_pins"].items():
        assert sha(ROOT / name) == pin
    assert bundle.semantic(bundle.scan(ROOT / policy["bundle_path"])) == bundle.semantic(record("APP-PRE.json"))
    assert bundle.semantic({name: bundle.entry(ROOT / name) for name in policy["extra_backup_paths"]}) == bundle.semantic(record("EXTRA-PRE.json"))
    metadata_helper = load("terminal_metadata", ROOT / policy["wpt"]["metadata_helper"])
    app = metadata_helper.application_metadata(ROOT / policy["wpt"]["application_ini"], policy["restored_application_revision"])
    omit = {"identity", "entry_identity"}
    assert {k:v for k,v in app.items() if k not in omit} == {k:v for k,v in policy["prepared_application_metadata"].items() if k not in omit}
    for name, path in [("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")]:
        assert hashlib.sha256(state.h.git(path, env, "ls-files", "-v", "-z")).hexdigest() == policy["prepared_flag_hashes"][name]
    epoch = read(CONTROL / "CURRENT-EPOCH.json")
    raw_index = record("RAW-INDEX-OBSERVATION.json")
    assert raw_index["semantic_index_unchanged"] and not raw_index["canonical_updated"]
    assert raw_index["before"] == epoch["raw_index_observation"]["current"] == pre["snapshot"]["index"]["raw_index"]
    adjusted = copy.deepcopy(epoch)
    adjusted["raw_index_observation"]["current"] = raw_index["after"]
    snapshot = state.a.verify_current(state.h, ROOT, env, adjusted)
    expected = copy.deepcopy(pre["snapshot"])
    expected["index"]["raw_index"] = raw_index["after"]
    assert snapshot == expected == record("POST.json")
    assert backup["verified_original_restoration"]
    assert backup["owned_backup_bytes"] == pre["owned_backup_bytes"] == inventory["bytes"]
    backups = pair / "backups"
    assert Path(restoration["backup_directory"]) == backups
    if result["success"]:
        assert backup["removed"] and not backup["retained_after_failure"]
        assert not backups.exists() and not backups.is_symlink()
    else:
        assert not backup["removed"] and backup["retained_after_failure"]
        assert backups.is_dir() and not backups.is_symlink()
        assert bundle.scan(backups) == inventory["owned_inventory"]
    for name, digest in inputs.items():
        assert sha(pair / name) == digest, name
    output = HERE / config["output"]
    assert output.parent == HERE and not output.exists()
    report = {"actual_terminal": terminal, "owner_manifest_sha256": config["owner_manifest_sha256"],
              "input_hashes": inputs, "owner_result": result, "observation": observation, "observation_complete": observation["observation_complete"],
              "restoration_independently_verified": True, "source_identities": restoration["sources"],
              "restored_application_metadata": app, "raw_index_observation": raw_index,
              "snapshot": snapshot, "backup": backup, "backup_deleted_by_reviewer": False,
              "canonical_updated": False, "native_acceptance": False}
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    assert not result["success"] or observation["observation_complete"], "Owner success lacks independently complete observation; REVIEW retains restoration/evidence"
    print(json.dumps({"review_complete": True, "owner_exit": terminal["exit"],
                      "browser_executed": observation["browser_executed"],
                      "callback_counts": summary_counts(observation),
                      "backup_retained": backup["retained_after_failure"], "canonical_updated": False}))


if __name__ == "__main__":
    main()
