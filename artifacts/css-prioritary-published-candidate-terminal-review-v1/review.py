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



def validate_build_phase(policy, pre, built, metadata, metadata_after, snapshots, binaries, *, consumed_inputs):
    assert metadata == metadata_after
    assert metadata["revision"] == metadata["build_revision"] == policy["head"]
    assert metadata["harness_revision"] == policy["wpt"]["harness_revision"] == policy["head"]
    assert metadata["source_role"] == "candidate"
    assert policy["wpt"]["phase_revisions"]["candidate"] == policy["head"]
    assert all(snapshot == built["snapshot"] for snapshot in snapshots) and len(snapshots) >= 3
    assert binaries == built["binaries"] and set(binaries) == set(policy["rebuilt_binaries"])
    assert built["browser_build_performed"]
    scope = load("intermediate_review_scope", HERE / "review_scope.py")
    scope.require_intermediate(built["snapshot"], consumed_inputs)
    scope.require_full(pre["snapshot"])
    assert built["snapshot"]["current_raw_stable_during_check"]
    assert built["snapshot"]["nested_index"] == pre["snapshot"]["nested_index"]
    for key in ("head", "entries", "cached_diff"):
        assert built["snapshot"]["index"][key] == pre["snapshot"]["index"][key]



def summary_counts(observation):
    return {key:(observation.get("outcomes") or {}).get(key) for key in ("callbacks_passed", "callbacks_failed")}


def consumed_map(here, policy, roles, manifest_sha256):
    closure = load("review_consumed_closure", HERE / "closure.py")
    binding = load("review_input_binding", HERE / "inputs.py")
    external = closure.external_inputs(ROOT, policy, roles)
    assert external == policy["intermediate_consumed_inputs"]
    return binding.bind_inputs(str(here.relative_to(ROOT)), (here / "FILES.json").read_bytes(), manifest_sha256, external)


def authenticate(manifest=None):
    config = read(HERE / "POLICY.json")
    for name, expected in read(HERE / "REFERENCES.json").items():
        assert sha(ROOT / name) == expected, name
    owner = ROOT / config["owner_directory"]
    for name, expected in read(HERE / "OWNER-CORE.json").items():
        assert sha(owner / name) == expected, name
    assert sha(HERE / "OWNER-PREPARED-FILES.json") == config["prepared_owner_manifest_sha256"]
    manifest = manifest or config["owner_manifest_sha256"]
    if manifest is not None:
        assert sha(owner / "FILES.json") == manifest
        for name, pin in read(owner / "FILES.json").items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            assert sha(owner / name) == pin["sha256"]
    return config, owner


def validate_mismatch(value, result):
    if value is None:
        return
    assert result["success"] is False
    assert value["repository"] in ("root", "nested")
    assert type(value["verification_call"]) is int and value["verification_call"] > 0
    before, after = value["before"], value["after"]
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    assert changed and value["changed_fields"] == changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--owner-manifest")
    parser.add_argument("--terminal")
    parser.add_argument("--terminal-sha256")
    args = parser.parse_args()
    config, here = authenticate(args.owner_manifest if args.verify else None)
    if not args.verify:
        print("Saved owner payloads authenticated; no runtime or live state read")
        return
    assert config["execution_enabled"]
    assert args.owner_manifest == config["owner_manifest_sha256"] and args.terminal and args.terminal_sha256
    terminal_path = ROOT / args.terminal
    assert args.terminal.startswith('artifacts/') and '..' not in Path(args.terminal).parts
    assert terminal_path.is_file() and not terminal_path.is_symlink()
    assert sha(terminal_path) == args.terminal_sha256
    terminal = read(terminal_path)
    assert type(terminal["session"]) is int and terminal["session"] == config["expected_session"]
    assert terminal["launch_chunk"] == config["expected_launch"]
    assert terminal["exit"] in (0, 1) and terminal["terminal_chunk"] and terminal["launch_chunk"]
    config["owner_manifest_sha256"] = args.owner_manifest
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
    assert result["provider_source_role"] == "published-baseline-prioritary-candidate"
    assert (result["error"] is None) == result["success"]
    baseline = load("terminal_baseline", here / "baseline.py")
    policy, ownership, roles = baseline.prepare(config["owner_manifest_sha256"])
    consumed_inputs = consumed_map(here, policy, roles, config["owner_manifest_sha256"])
    assert policy["runtime_output"] == config["runtime_directory"]
    assert policy["owner_directory"] == config["owner_directory"]
    assert policy["current_binding"] == config["current_binding"]
    capture = baseline.current_capture(policy)
    assert capture["full_current_state_verified"] and capture["sources_match_head"]
    assert result["build_revision"] == policy["head"] == capture["checkpoint"]["head"]
    assert set(roles) == set(capture["sources"]) == set(read(here / "SOURCE-ROLES.json"))
    for name, role in roles.items():
        assert role["base_sha256"] == capture["sources"][name]["owned_sha256"]
    assert {name for name, role in roles.items() if role["base_sha256"] != role["candidate_sha256"]} == {"servo/components/style/properties/cascade.rs"}
    assert policy["source_context_pins"]["servo/components/style/values/generics/calc.rs"] == capture["epoch_payload_pins"]["servo/components/style/values/generics/calc.rs"]
    state = load("terminal_state", ROOT / policy["state_helper"])
    bundle = load("terminal_bundle", ROOT / policy["bundle_helper"])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    pre = record("CANDIDATE-PRE.json")
    restoration = record("RESTORATION.json")
    backup = record("BACKUP-CLEANUP.json")
    inventory = record("BACKUPS.json")
    assert pre["controls"] == policy["controls"] == capture["controls"]
    assert pre["snapshot"] == capture["snapshot"]
    assert restoration["errors"] == [] and restoration["owned_processes"] == {}
    assert set(restoration["sources"]) == set(roles) == set(pre["sources"])
    admission = capture
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
    mismatch = record("INTERMEDIATE-INDEX-MISMATCH.json") if (pair / "INTERMEDIATE-INDEX-MISMATCH.json").exists() else None
    validate_mismatch(mismatch, result)
    lane_review = load("published_observation_review", HERE / "observations.py")
    validate = lambda *args: validate_build_phase(*args, consumed_inputs=consumed_inputs)
    observation = lane_review.review(ROOT, HERE, pair, policy, pre, result, build, record, inputs, ownership, validate)
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
    assert {k:v for k,v in app.items() if k not in omit} == {k:v for k,v in capture["application_metadata"].items() if k not in omit}
    for name, path in [("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")]:
        assert hashlib.sha256(state.h.git(path, env, "ls-files", "-v", "-z")).hexdigest() == capture["flag_hashes"][name]
    baseline.require_app_inventory(policy, record("APP-PRE.json"), record("EXTRA-PRE.json"))
    epoch = read(CONTROL / "CURRENT-EPOCH.json")
    baseline.require_role(policy, read(CONTROL / "ROLE.json"), epoch)
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
              "canonical_updated": False, "native_acceptance": False,
              "intermediate_index_mismatch": mismatch, "current_capture": config["current_binding"],
              "terminal_receipt": {"path": args.terminal, "sha256": args.terminal_sha256}}
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
