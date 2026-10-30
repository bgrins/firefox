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


def partition(original, candidate, signature):
    old = {(row["test"], row["subtest"]): row for row in original}
    new = {(row["test"], row["subtest"]): row for row in candidate}
    assert len(old) == len(original) == 42 and len(new) == len(candidate) == 42
    assert set(old) == set(new)
    assert all(row["status"] in ("PASS", "FAIL") for row in old.values())
    assert all(row["status"] in ("PASS", "FAIL") for row in new.values())
    return {label: [{"original": old[key], "candidate": new[key],
                    "full_signature_unchanged": signature(old[key]) == signature(new[key])}
                   for key in sorted(old) if old[key]["status"] == status]
            for label, status in [("original_pass_controls", "PASS"),
                                  ("original_fail_research_targets", "FAIL")]}


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
    assert type(config["expected_session"]) is int and config["expected_session"] > 1
    assert terminal["session"] == config["expected_session"]
    assert config["expected_launch"] and terminal["launch_chunk"] == config["expected_launch"]
    assert terminal["exit"] in (0, 1) and terminal["terminal_chunk"]
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
    assert policy["runtime_output"] == config["runtime_directory"] and len(roles) == 3
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
    source_admission = read(ROOT / policy["source_equivalence"]["path"])
    for name, role in roles.items():
        assert pre["sources"][name] == dict(role, identity=source_admission["sources"][name]["identity"])
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
    observation = {"browser_executed": False, "observation_complete": False, "build_exit": build["exit"]}
    if (pair / "candidate-wpt/RESULT.json").is_file():
        assert build["exit"] == 0 and build["error"] is None and build["stop_reason"] is None
        built = record("candidate-build/RESULT.json")
        assert built["command_success"] and built["preservation_verified"] and built["error"] is None
        assert built["native_sources"] == command["source_sha256"]
        phase = record("candidate-wpt/RESULT.json")
        metadata = record("candidate-wpt/APPLICATION-METADATA.json")
        comparison = load("terminal_comparison", here / "comparison.py")
        assessor = load("terminal_assessor", here / "assess.py")
        checks = load("terminal_stream_checks", ROOT / policy["wpt"]["checks_helper"])
        original = comparison.replay_all(ROOT, policy)
        settings = record("candidate-wpt/ASSESSMENT-POLICY.json")
        assert settings == comparison.phase_policy(policy["wpt"])
        raw = pair / "candidate-wpt/raw.jsonl"
        inputs["candidate-wpt/raw.jsonl"] = sha(raw)
        replay = assessor.assess([json.loads(line) for line in raw.read_text().splitlines()], phase["exit"], settings, checks, original=original, run_binding=metadata)
        saved_assessment = record("candidate-wpt/ASSESSMENT.json")
        evidence = {"raw_sha256": inputs["candidate-wpt/raw.jsonl"], "browser_exit": phase["exit"],
                    "replay": replay, "saved_assessment_matches": replay == saved_assessment,
                    "complete": replay["complete"], "native_acceptance": False}
        with (HERE / "RAW-REPLAY.json").open("x") as stream:
            json.dump(evidence, stream, indent=2, sort_keys=True)
            stream.write("\n")
        assert replay == saved_assessment and replay["complete"], "Incomplete or changed raw observation; RAW-REPLAY retains evidence"
        assert len(replay["rows"]) == 42 and len(replay["ends"]) == 3
        assert phase["comparison_gate_passed"] == replay["comparison_gate_passed"]
        assert metadata == record("candidate-wpt/APPLICATION-METADATA-POST.json")
        assert metadata["revision"] == metadata["build_revision"] == policy["wpt"]["phase_revisions"]["candidate"] == policy["head"]
        assert metadata["harness_revision"] == policy["wpt"]["harness_revision"] == policy["head"]
        assert metadata["source_role"] == "candidate"
        phase_pre = record("candidate-wpt/PRE.json")
        assert phase_pre == record("candidate-wpt/POST.json") == record("PHASES-PRE.json") == record("PHASES-POST.json")
        assert phase_pre == built["snapshot"]
        assert record("candidate-wpt/BINARY-PINS.json") == built["binaries"]
        assert set(built["binaries"]) == set(policy["rebuilt_binaries"]) and built["browser_build_performed"]
        assert built["snapshot"]["nested_index"] == pre["snapshot"]["nested_index"]
        for key in ("head", "entries", "cached_diff"):
            assert built["snapshot"]["index"][key] == pre["snapshot"]["index"][key]
        assert phase["success"] and phase["preservation_verified"] and phase["execution_error"] is None
        old = {(row["test"], row["subtest"]): row for row in original["rows"]}
        outcomes = {"callbacks_passed": sum(row["status"] == "PASS" for row in replay["rows"]),
                    "callbacks_failed": sum(row["status"] == "FAIL" for row in replay["rows"]),
                    "all_callbacks_passed": all(row["status"] == "PASS" for row in replay["rows"]),
                    "comparison_gate_passed": replay["comparison_gate_passed"],
                    "comparison_errors": replay["comparison_errors"],
                    "rows": [{"original": old[(row["test"], row["subtest"])], "candidate": row} for row in replay["rows"]],
                    "original_endings": original["ends"], "candidate_endings": replay["ends"], "native_acceptance": False}
        assert outcomes == record("OUTCOMES.json")
        assert result["candidate_phase"] == {key: inputs["candidate-wpt/" + name] for key, name in [("assessment_sha256", "ASSESSMENT.json"), ("raw_sha256", "raw.jsonl"), ("result_sha256", "RESULT.json")]}
        assert result["success"]
        cleanup = record("candidate-wpt/CLEANUP.json")
        assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
        process = record("candidate-wpt/PROCESS.json")
        assert process["pid"] == process["pgid"] and process["pgid"] > 1
        ownership.group_absent(process["pgid"])
        wpt_command = record("candidate-wpt/COMMAND.json")
        phase_dir = pair / "candidate-wpt"
        expected_command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--headless", "--processes=1", "--no-manifest-update", "--no-manifest-download",
                            "--binary=" + str(ROOT / policy["wpt"]["binary"]), "--config=" + str(phase_dir / "wptrunner.ini"),
                            "--run-info=" + str(ROOT / "objdir-full.noindex"), "--prefs-root=" + str(ROOT / "testing/profiles"), "--log-raw=" + str(phase_dir / "raw.jsonl")]
        expected_command.extend("--include=" + page for page in policy["wpt"]["expected_subtests"])
        assert wpt_command["command"] == expected_command and wpt_command["timeout_seconds"] == policy["wpt"]["timeout_seconds"]
        temporary = Path(wpt_command["temporary_root"])
        assert temporary.parent == Path("/private/tmp") and temporary.name.startswith("css-easing-paired-")
        assert not temporary.exists() and not temporary.is_symlink()
        for name, pin in policy["wpt"]["resources"].items():
            assert sha(pair / "candidate-wpt/tests" / name) == pin["sha256"]
        assert sha(pair / "candidate-wpt/metadata/MANIFEST.json") == policy["wpt"]["manifest"]["sha256"]
        for name, pin in policy["wpt"]["metadata"].items():
            copied = phase_dir / "metadata" / name
            if pin["sha256"] is None:
                assert not copied.exists() and not copied.is_symlink()
            else:
                assert sha(copied) == pin["sha256"]
        borrowed_tools = phase_dir / "tests/tools"
        assert borrowed_tools.is_symlink() and os.readlink(borrowed_tools) == str(ROOT / "testing/web-platform/tests/tools")
        observation = {"browser_executed": True, "observation_complete": True, "build_exit": build["exit"],
                       "browser_exit": phase["exit"], "outcomes": outcomes,
                       "research_cohorts": partition(original["rows"], replay["rows"], assessor.signature),
                       "cohorts_change_assessor_policy": False}
    else:
        assert not (pair / "candidate-wpt").exists(), "Partial browser observation requires separate recovery review"
        assert build["exit"] != 0 and result["success"] is False and result["candidate_phase"] is None
        assert record("FAILURE-TRACEBACK.json")["error"] == result["error"]
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
              "input_hashes": inputs, "owner_result": result, "observation": observation,
              "restoration_independently_verified": True, "source_identities": restoration["sources"],
              "restored_application_metadata": app, "raw_index_observation": raw_index,
              "snapshot": snapshot, "backup": backup, "backup_deleted_by_reviewer": False,
              "canonical_updated": False, "native_acceptance": False}
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"review_complete": True, "owner_exit": terminal["exit"],
                      "browser_executed": observation["browser_executed"],
                      "comparison_gate_passed": observation.get("outcomes", {}).get("comparison_gate_passed"),
                      "backup_retained": backup["retained_after_failure"], "canonical_updated": False}))


if __name__ == "__main__":
    main()
