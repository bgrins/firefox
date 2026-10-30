import argparse
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
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, digest):
    assert sha(directory / "FILES.json") == digest
    for name, record in read(directory / "FILES.json").items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        path = directory / name
        assert not path.is_symlink() and path.is_file()
        assert sha(path) == (record if isinstance(record, str) else record["sha256"]), name
        if isinstance(record, dict):
            assert path.stat().st_size == record["bytes"]


def phase_policy(settings):
    result = dict(settings, tests={page: "testharness" for page in settings["expected_subtests"]}, held_subtests={})
    result["regression_subtests"] = {page: [name for name in names if name not in settings["target_subtests"].get(page, [])] for page, names in settings["expected_subtests"].items()}
    result["cardinality_description"] = "Exact sealed target and control names; existing control failures retain full signatures."
    return result


def compare_inherited(old, new, signature):
    key = lambda row: (row["action"], row["test"], row.get("subtest"))
    a = {key(row): row for row in old}
    b = {key(row): row for row in new}
    assert len(a) == len(old) and len(b) == len(new) and set(a) <= set(b)
    rows = [{"previous": signature(a[k]), "current": signature(b[k]),
             "full_signature_unchanged": signature(a[k]) == signature(b[k])}
            for k in a]
    return {"inherited_signatures": len(rows), "unchanged": sum(r["full_signature_unchanged"] for r in rows),
            "differences": [r for r in rows if not r["full_signature_unchanged"]],
            "all_rows": rows, "new_signatures": [signature(b[k]) for k in b if k not in a]}


def replay(directory, owner, policy):
    phase = directory / "original-wpt"
    result = read(directory / "RESULT.json")
    assert result["lifecycle_complete"] and result["observation_complete"] and result["preservation_verified"]
    assert result["source_or_canonical_mutation"] is False and result["native_fix_accepted"] is False
    assert result["phase"] == {k:sha(phase / n) for k,n in [("assessment_sha256", "ASSESSMENT.json"), ("raw_sha256", "raw.jsonl"), ("result_sha256", "RESULT.json")]}
    settings = read(phase / "ASSESSMENT-POLICY.json")
    assert settings == phase_policy(policy["wpt"])
    outcome = read(phase / "RESULT.json")
    assert outcome["success"] and outcome["preservation_verified"] and outcome["execution_error"] is None
    assert outcome["native_fix_acceptance"] is False
    metadata = read(phase / "APPLICATION-METADATA.json")
    assert metadata == read(phase / "APPLICATION-METADATA-POST.json") == policy["prepared_application_metadata"]
    assessor = load("original_replay_assessor", owner / "assess.py")
    checks = load("original_replay_checks", ROOT / policy["wpt"]["checks_helper"])
    events = [json.loads(line) for line in (phase / "raw.jsonl").read_text().splitlines()]
    assessment = assessor.assess(events, outcome["exit"], settings, checks, run_binding=metadata)
    assert assessment == read(phase / "ASSESSMENT.json") and assessment["complete"] and assessment["errors"] == []
    assert len(assessment["rows"]) == policy["wpt"]["expected_subtest_count"]
    assert len(assessment["ends"]) == policy["wpt"]["expected_page_count"]
    assert all(row["status"] in ("PASS", "FAIL") for row in assessment["rows"])
    assert all(row["status"] == "OK" for row in assessment["ends"])
    assert result["callbacks_passed"] == sum(row["status"] == "PASS" for row in assessment["rows"])
    assert result["callbacks_failed"] == sum(row["status"] == "FAIL" for row in assessment["rows"])
    assert result["all_callbacks_passed"] == (result["callbacks_failed"] == 0)
    assert read(directory / "PRE.json") == read(directory / "POST.json") == read(phase / "PRE.json") == read(phase / "POST.json")
    roster = read(directory / "OBSERVED-ROSTER.json")
    assert roster["expected_subtests"] == policy["wpt"]["expected_subtests"]
    assert roster["observed_subtest_count"] == policy["wpt"]["expected_subtest_count"]
    assert roster["owner_sha256"] == sha(owner / "FILES.json") and roster["phase"] == result["phase"]
    assert roster["source_roster_sha256"] == sha(ROOT / policy["source_roster"]) and not roster["candidate_authorized"]
    built = read(ROOT / policy["build_epoch"])
    assert read(phase / "BINARY-PINS.json") == {name:built["pins"][name] for name in policy["rebuilt_binaries"]}
    bound = [name for name in built["pins"] if name.startswith(("servo/", "layout/", "dom/")) or name in policy["rebuilt_binaries"]]
    assert result["build_native_and_binary_pin_count"] == len(bound)
    for name, record in policy["wpt"]["resources"].items():
        assert sha(phase / "tests" / name) == record["sha256"]
    assert sha(phase / "metadata/MANIFEST.json") == policy["wpt"]["manifest"]["sha256"]
    for name, record in policy["wpt"]["metadata"].items():
        copied = phase / "metadata" / name
        if record["sha256"] is None:
            assert not copied.exists() and not copied.is_symlink()
        else:
            assert sha(copied) == record["sha256"]
    cleanup = read(phase / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
    return result, outcome, assessment, assessor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    config = read(HERE / "POLICY.json")
    for name, digest in read(HERE / "REFERENCES.json").items():
        assert sha(ROOT / name) == digest
    owner = ROOT / config["owner_directory"]
    authenticate(owner, config["owner_manifest_sha256"])
    if not args.verify:
        print("Saved owner authenticated; no observation or live state read")
        return
    assert config["execution_enabled"] and config["actual_terminal"] is not None
    assert config["source_or_canonical_mutations_allowed"] is False
    terminal = config["actual_terminal"]
    assert terminal["session_id"] == 91618 and terminal["exit"] == 0 and terminal["terminal_chunk"]
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    policy = read(owner / "POLICY.json")
    load("expanded_owner_check", owner / "check.py").check_binding(policy)
    pair = ROOT / config["runtime_directory"]
    assert policy["output"] == config["runtime_directory"]
    assert sha(pair / "RESULT.json") == terminal["result_sha256"]
    owner_terminal = read(pair / "ROOT-OWNER-TERMINAL.json")
    assert {k:owner_terminal[k] for k in terminal} == terminal
    assert owner_terminal["owner_sha256"] == config["owner_manifest_sha256"]
    assert owner_terminal["native_acceptance"] is False
    previous_owner = ROOT / config["previous_owner"]
    previous_runtime = ROOT / config["previous_runtime"]
    authenticate(previous_owner, config["previous_owner_manifest_sha256"])
    authenticate(previous_runtime, config["previous_runtime_manifest_sha256"])
    result, outcome, assessment, assessor = replay(pair, owner, policy)
    old_policy = read(previous_owner / "POLICY.json")
    _, _, old, _ = replay(previous_runtime, previous_owner, old_policy)
    inherited = compare_inherited(old["rows"] + old["ends"], assessment["rows"] + assessment["ends"], assessor.signature)
    assert inherited["inherited_signatures"] == 118 and len(inherited["new_signatures"]) == 18
    phase = pair / "original-wpt"
    command = read(phase / "COMMAND.json")
    expected_command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--headless", "--processes=1", "--no-manifest-update", "--no-manifest-download", "--binary=" + str(ROOT / policy["wpt"]["binary"]), "--config=" + str(phase / "wptrunner.ini"), "--run-info=" + str(ROOT / "objdir-full.noindex"), "--prefs-root=" + str(ROOT / "testing/profiles"), "--log-raw=" + str(phase / "raw.jsonl")]
    expected_command.extend("--include=" + page for page in policy["wpt"]["expected_subtests"])
    assert command["command"] == expected_command and command["timeout_seconds"] == policy["wpt"]["timeout_seconds"]
    temporary = Path(command["temporary_root"])
    assert temporary.parent == Path("/private/tmp") and temporary.name.startswith("css-easing-paired-")
    assert not temporary.exists() and not temporary.is_symlink()
    ownership = load("expanded_ownership", ROOT / "artifacts/css-registered-number-source-transition-v4/transition.py")
    process = read(phase / "PROCESS.json")
    assert process["pid"] == process["pgid"] and process["pgid"] > 1
    ownership.group_absent(process["pgid"])
    assert {name:sha(CONTROL / name) for name in policy["controls"]} == policy["controls"]
    assert not (CONTROL / "SOURCE-TRANSITION.lock").exists() and not (CONTROL / "SOURCE-TRANSITION.lock").is_symlink()
    for name, digest in policy["deferred_nonartifact_references"].items():
        assert sha(ROOT / name) == digest
    for record in policy["wpt"]["metadata"].values():
        if record["sha256"] is None:
            assert not (ROOT / record["path"]).exists() and not (ROOT / record["path"]).is_symlink()
        else:
            assert sha(ROOT / record["path"]) == record["sha256"]
    for name, pin in policy["source_role_pins"].items():
        assert sha(ROOT / name) == pin
    for name, claim in policy["accepted_current_payloads"].items():
        ownership.claim(ROOT, name, claim["sha256"], claim["identity"])
    state = load("expanded_state", ROOT / policy["state_helper"])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    epoch = read(CONTROL / "CURRENT-EPOCH.json")
    snapshot = state.a.verify_current(state.h, ROOT, env, epoch)
    assert snapshot == read(pair / "PRE.json") == read(pair / "POST.json")
    for name, pin in read(phase / "BINARY-PINS.json").items():
        assert sha(ROOT / name) == epoch["pins"][name] == pin
    restoration_owner = ROOT / config["restoration_owner"]
    restoration_runtime = ROOT / config["restoration_runtime"]
    authenticate(restoration_owner, config["restoration_owner_manifest_sha256"])
    authenticate(restoration_runtime, config["restoration_runtime_manifest_sha256"])
    restoration_policy = read(restoration_owner / "POLICY.json")
    bundle = load("expanded_bundle", ROOT / restoration_policy["bundle_helper"])
    assert bundle.semantic(bundle.scan(ROOT / restoration_policy["bundle_path"])) == bundle.semantic(read(restoration_runtime / "APP-PRE.json"))
    assert bundle.semantic({name:bundle.entry(ROOT / name) for name in restoration_policy["extra_backup_paths"]}) == bundle.semantic(read(restoration_runtime / "EXTRA-PRE.json"))
    for name, claim in read(restoration_runtime / "ROOT-REVIEW.json")["source_identities"].items():
        ownership.claim(ROOT, name, claim["sha256"], claim["identity"])
    metadata = load("expanded_metadata", ROOT / policy["wpt"]["metadata_helper"])
    app = metadata.application_metadata(ROOT / policy["wpt"]["application_ini"], policy["wpt"]["phase_revisions"]["original"])
    app.update(build_revision=app["revision"], harness_revision=policy["head"], source_role="original")
    assert app == policy["prepared_application_metadata"]
    flags = {name:hashlib.sha256(state.h.git(path, env, "ls-files", "-v", "-z")).hexdigest() for name,path in [("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")]}
    assert flags == restoration_policy["prepared_flag_hashes"]
    assert {name:sha(CONTROL / name) for name in policy["controls"]} == policy["controls"]
    report = {"actual_terminal": terminal, "owner_sha256": config["owner_manifest_sha256"], "result": result,
              "browser_exit": outcome["exit"], "callbacks_passed": result["callbacks_passed"], "callbacks_failed": result["callbacks_failed"],
              "page_endings_ok": len(assessment["ends"]), "inherited_signature_comparison": inherited,
              "raw_replay_verified": True, "pre_post_equality_verified": True, "current_state_verified": True,
              "current_source_binary_control_pins_verified": True, "resource_bodies_verified": True,
              "owned_process_cleanup_verified": True, "owned_profile_root_absent": str(temporary),
              "snapshot": snapshot, "controls": policy["controls"], "flags": flags, "application_metadata": app,
              "native_acceptance": False, "source_or_canonical_mutated_by_reviewer": False}
    output = HERE / config["output"]
    assert output.parent == HERE
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"review_complete": True, "callbacks_passed": result["callbacks_passed"], "callbacks_failed": result["callbacks_failed"], "inherited_signatures_unchanged": inherited["unchanged"], "report_sha256": sha(output)}))


if __name__ == "__main__":
    main()
