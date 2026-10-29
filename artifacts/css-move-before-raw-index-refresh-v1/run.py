import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
digest = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    assert digest((HERE / "FILES.json").read_bytes()) == sys.argv[2]
    for name, pin in read(HERE / "FILES.json").items():
        assert not Path(name).is_absolute() and ".." not in Path(name).parts
        assert digest((HERE / name).read_bytes()) == pin
    policy = read(HERE / "POLICY.json")
    for name, pin in policy["references"].items():
        assert digest((ROOT / name).read_bytes()) == pin, name
    controls = {n: (RUNTIME / n).read_bytes() for n in ("CURRENT-EPOCH.json", "ROLE.json", "OWNED.json")}
    assert {n: digest(body) for n, body in controls.items()} == policy["controls"]
    epoch = json.loads(controls["CURRENT-EPOCH.json"])
    evidence = ROOT / policy["pair_runtime"]
    initial = read(evidence / "BASELINE-PRE.json")
    pre, post = initial["snapshot"], read(evidence / "POST.json")
    result, restored = read(evidence / "RESULT.json"), read(evidence / "RESTORATION.json")
    inner = read(evidence / "candidate-build/build-RESULT.json")
    terminal = read(evidence / "CANDIDATE-ROOT-REPORTED-TERMINAL.json")
    assert terminal["session"] == 81773 and terminal["launch_receipt"] == "5c540d" and terminal["terminal_receipt"] == "7ef7a6/0" and terminal["exit"] == 0
    assert result["success"] is True and result["restoration_verified"] and result["runtime_controls_unchanged"] and result["empty_staging_preserved"]
    assert result["error"] is None
    assert result["candidate_phase"] == {"assessment_sha256": digest((evidence / "candidate-wpt/ASSESSMENT.json").read_bytes()), "raw_sha256": digest((evidence / "candidate-wpt/raw.jsonl").read_bytes()), "result_sha256": digest((evidence / "candidate-wpt/RESULT.json").read_bytes())}
    assert result["publication_errors"] == [] and result["native_fix_acceptance"] is False
    assert inner["exit"] == 0 and inner["owned_group_absent"] and inner["cleanup_errors"] == []
    assert inner["error"] is None and inner["stop_reason"] is None
    assert restored["errors"] == [] and restored["owned_processes"] == {}
    assert initial["controls"] == policy["controls"] == read(evidence / "CANDIDATE-PRE.json")["controls"]
    assert read(evidence / "CANDIDATE-PRE.json")["snapshot"] == pre
    assessments = {}
    for role in ("original", "candidate"):
        phase = evidence / (role + "-wpt")
        record, assessment = read(phase / "RESULT.json"), read(phase / "ASSESSMENT.json")
        assert record["success"] is True
        assert record["preservation_verified"] and record["execution_error"] is None
        assert assessment["complete"] and assessment["errors"] == [] and assessment["fixture_setup_errors"] == []
        assert read(phase / "PRE.json") == read(phase / "POST.json")
        assert read(phase / "CLEANUP.json")["owned_group_absent"] and read(phase / "CLEANUP.json")["temporary_root_removed"]
        assessments[role] = assessment
    assert assessments["candidate"]["comparison_gate_passed"] is True
    assert assessments["candidate"]["comparison_errors"] == []
    assert len(assessments["candidate"]["rows"]) == 70
    assert all(row["status"] == "PASS" for row in assessments["candidate"]["rows"])
    assert len(assessments["candidate"]["regression_signature"]) == 31
    targets = {tuple(row) for row in policy["target_ids"]}
    original_targets = [row for row in assessments["original"]["rows"] if (row["test"], row["subtest"]) in targets]
    candidate_targets = [row for row in assessments["candidate"]["rows"] if (row["test"], row["subtest"]) in targets]
    assert len(original_targets) == len(candidate_targets) == 51
    assert sum(row["status"] == "FAIL" for row in original_targets) == 21
    assert all(row["status"] in ("PASS", "FAIL") for row in original_targets)
    assert all(row["status"] == "PASS" for row in candidate_targets)
    unexpected = assessments["candidate"]["unexpected"]
    assert len(unexpected) == 7
    assert all(row["status"] == "PASS" and row["expected"] == "FAIL" for row in unexpected)
    assert {(row["test"], row["subtest"]) for row in unexpected} == {tuple(row) for row in policy["expected_unexpected_pass_ids"]}
    assert assessments["original"]["regression_signature"] == assessments["candidate"]["regression_signature"]
    cleanup = read(evidence / "BACKUP-CLEANUP.json")
    assert cleanup["removed"] and cleanup["verified_original_restoration"] and cleanup["retained_after_failure"] is False
    assert not (evidence / "backups").exists()
    assert epoch["semantic_index"]["head"] == policy["head"]
    assert {k: v for k, v in pre["index"].items() if k != "raw_index"} == epoch["semantic_index"]
    assert pre["index"]["raw_index"] == epoch["raw_index_observation"]["current"]
    raw = read(evidence / "RAW-INDEX-OBSERVATION.json")
    assert raw["before"] == pre["index"]["raw_index"] and raw["after"] == post["index"]["raw_index"]
    assert raw["semantic_index_unchanged"] and raw["canonical_updated"] is False
    projected = copy.deepcopy(pre)
    projected["index"]["raw_index"] = post["index"]["raw_index"]
    assert projected == post
    flag_reference = read(ROOT / policy["flag_reference"])
    assert flag_reference["index_sha256"] == digest(json.dumps(pre["index"], sort_keys=True).encode())
    assert flag_reference["nested_index_sha256"] == digest(json.dumps(pre["nested_index"], sort_keys=True).encode())
    updated = copy.deepcopy(epoch)
    updated["raw_index_observation"]["current"] = post["index"]["raw_index"]
    encoded = json.dumps(updated, indent=2, sort_keys=True).encode() + b"\n"
    assert digest(encoded) == policy["updated_epoch_sha256"]
    if sys.argv[1] == "--check":
        print("Authenticated successful moveBefore70 pair with verified restoration; only canonical raw observation changes", policy["updated_epoch_sha256"])
        return
    assert policy["execution_enabled"] is True
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    state = load("refresh_state", policy["state_helper"])
    owned = load("refresh_ownership", policy["ownership_helper"])
    before = state.a.verify_current(state.h, ROOT, ENV, updated)
    assert before["index"] == post["index"] and before["nested_index"] == post["nested_index"]
    assert before == post
    for label, path in (("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")):
        assert digest(state.h.git(path, ENV, "ls-files", "-v", "-z")) == flag_reference["index_flag_hashes"][label]
    sources = read(evidence / "CANDIDATE-PRE.json")["sources"]
    source_reference = read(ROOT / policy["source_reference"])
    assert set(sources) == set(restored["sources"]) == set(source_reference) == set(policy["source_paths"])
    for name, record in sources.items():
        expected = source_reference[name]
        assert expected["base_sha256"] == record["base_sha256"] and expected["identity"] == record["identity"]
        assert restored["sources"][name] == {"sha256": record["base_sha256"], "identity": record["identity"]}
        owned.claim(ROOT, name, record["base_sha256"], record["identity"])
        assert stat.S_IMODE((ROOT / name).lstat().st_mode) == expected["mode"]
    for name in ("candidate-build/build-GROUP-CLEANUP.json", "candidate-build/wake-GROUP-CLEANUP.json"):
        assert read(evidence / name)["owned_group_absent"]
    for name in ("candidate-build/build-PROCESS.json", "candidate-build/WAKE-PROCESS.json", "original-wpt/PROCESS.json", "candidate-wpt/PROCESS.json"):
        owned.group_absent(read(evidence / name)["pgid"])
    owned.quiescent(RUNTIME)
    lock = RUNTIME / "SOURCE-TRANSITION.lock"
    assert not lock.exists() and not lock.is_symlink()
    output = ROOT / policy["output"]
    assert output.parent == ROOT / "artifacts" and not output.exists() and not output.is_symlink()
    claims = {n: owned.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    output.mkdir()
    state.save(output / "PRE.json", {"head": policy["head"], "controls": policy["controls"], "verified_post_snapshot_sha256": digest(json.dumps(post, sort_keys=True).encode()), "old_raw": pre["index"]["raw_index"], "new_raw": post["index"]["raw_index"]})
    with lock.open("x") as stream:
        stream.write(json.dumps({"pid": os.getpid(), "runtime": policy["output"]}) + "\n")
    identity = (lock.stat().st_dev, lock.stat().st_ino)
    published = False
    try:
        assert state.a.verify_current(state.h, ROOT, ENV, updated) == before
        for name, pin in policy["references"].items():
            assert digest((ROOT / name).read_bytes()) == pin
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        owned.write_owned(ROOT, claims["CURRENT-EPOCH.json"], encoded)
        assert state.a.verify_current(state.h, ROOT, ENV, updated) == before
        assert all((RUNTIME / n).read_bytes() == controls[n] for n in ("ROLE.json", "OWNED.json"))
        state.save(output / "RESULT.json", {"success": True, "preservation_verified": True, "updated_only": "raw_index_observation.current", "epoch_sha256": digest(encoded), "before": pre["index"]["raw_index"], "after": post["index"]["raw_index"], "head": policy["head"], "paired_result_reclassified": False, "build_exit": 0, "full_epoch_copies_saved": 0})
        published = True
        assert (lock.stat().st_dev, lock.stat().st_ino) == identity
        lock.unlink()
    except BaseException as error:
        rollback_errors = []
        if not published:
            try:
                owned.write_owned(ROOT, claims["CURRENT-EPOCH.json"], controls["CURRENT-EPOCH.json"])
                assert state.a.verify_current(state.h, ROOT, ENV, updated) == before
                assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
            except BaseException as rollback:
                rollback_errors.append(repr(rollback))
        state.save(output / "FAILURE.json", {"error": repr(error), "rollback_errors": rollback_errors, "published_refresh_preserved": published, "manual_recovery_required": published or bool(rollback_errors)})
        if not published and not rollback_errors:
            assert (lock.stat().st_dev, lock.stat().st_ino) == identity
            lock.unlink()
        raise
    print("Canonical raw-index observation refreshed; successful paired evidence unchanged", flush=True)


if __name__ == "__main__":
    main()
