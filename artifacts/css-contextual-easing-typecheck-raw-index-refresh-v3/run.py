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
    evidence = ROOT / policy["typecheck_runtime"]
    pre, post = read(evidence / "PRE.json"), read(evidence / "POST.json")
    result, restored = read(evidence / "RESULT.json"), read(evidence / "RESTORATION.json")
    inner = read(evidence / "build-RESULT.json")
    terminal = read(HERE / "ROOT-REPORTED-TERMINAL.json")
    assert terminal["session"] == 95159 and terminal["launch_receipt"] == "e0410b" and terminal["terminal_receipt"] == "eba90a/0" and terminal["exit"] == 0
    assert result["success"] is True and result["actual_cargo_success"] is True
    assert result["error"] is None and result["preservation_error"] is None
    assert result["source_restored"] and result["preservation_verified"] and result["runtime_controls_unchanged"]
    assert result["owned_processes"] == {} and result["publication_errors"] == []
    assert inner["exit"] == 0 and inner["owned_group_absent"] and inner["cleanup_errors"] == []
    assert inner["error"] is None and inner["stop_reason"] is None
    assert restored["errors"] == [] and restored["owned_processes"] == {}
    assert pre["epoch_sha256"] == post["epoch_sha256"] == policy["controls"]["CURRENT-EPOCH.json"]
    assert epoch["semantic_index"]["head"] == policy["head"]
    assert {k: v for k, v in pre["index"].items() if k != "raw_index"} == epoch["semantic_index"]
    assert pre["index"]["raw_index"] == epoch["raw_index_observation"]["current"]
    raw = read(evidence / "RAW-INDEX-OBSERVATION.json")
    assert raw["before"] == pre["index"]["raw_index"] and raw["after"] == post["index"]["raw_index"]
    assert raw["semantic_index_unchanged"] and raw["canonical_updated"] is False
    projected = copy.deepcopy(pre)
    projected["index"]["raw_index"] = post["index"]["raw_index"]
    projected["snapshot_sha256"] = post["snapshot_sha256"]
    assert projected == post
    updated = copy.deepcopy(epoch)
    updated["raw_index_observation"]["current"] = post["index"]["raw_index"]
    encoded = json.dumps(updated, indent=2, sort_keys=True).encode() + b"\n"
    assert digest(encoded) == policy["updated_epoch_sha256"]
    for snapshot in (pre, post):
        full = {"index": snapshot["index"], "nested_index": snapshot["nested_index"], "current_raw_stable_during_check": True, "working_sources_binaries_research_preserved": True}
        assert digest(json.dumps(full, sort_keys=True).encode()) == snapshot["snapshot_sha256"]
    if sys.argv[1] == "--check":
        print("Authenticated successful Cargo/restored source evidence; only canonical raw observation changes", policy["updated_epoch_sha256"])
        return
    assert policy["execution_enabled"] is True
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    state = load("refresh_state", policy["state_helper"])
    owned = load("refresh_ownership", policy["ownership_helper"])
    before = state.a.verify_current(state.h, ROOT, ENV, updated)
    assert before["index"] == post["index"] and before["nested_index"] == post["nested_index"]
    assert digest(json.dumps(before, sort_keys=True).encode()) == post["snapshot_sha256"]
    for label, path in (("root", ROOT), ("nested", ROOT / "artifacts/css-spec-lean")):
        assert digest(state.h.git(path, ENV, "ls-files", "-v", "-z")) == post["index_flag_hashes"][label]
    sources = read(evidence / "SOURCES.json")
    assert set(sources) == set(restored["sources"]) == set(policy["source_paths"])
    for name, record in sources.items():
        assert restored["sources"][name] == {"sha256": record["base_sha256"], "identity": record["identity"], "mode": record["mode"]}
        owned.claim(ROOT, name, record["base_sha256"], record["identity"])
        assert stat.S_IMODE((ROOT / name).lstat().st_mode) == record["mode"]
    for prefix in ("build", "wake"):
        cleanup = read(evidence / (prefix + "-GROUP-CLEANUP.json"))
        assert cleanup["owned_group_absent"]
    for name in ("build-PROCESS.json", "WAKE-PROCESS.json"):
        owned.group_absent(read(evidence / name)["pgid"])
    owned.quiescent(RUNTIME)
    lock = RUNTIME / "SOURCE-TRANSITION.lock"
    assert not lock.exists() and not lock.is_symlink()
    output = ROOT / policy["output"]
    assert output.parent == ROOT / "artifacts" and not output.exists() and not output.is_symlink()
    claims = {n: owned.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    output.mkdir()
    state.save(output / "PRE.json", {"head": policy["head"], "controls": policy["controls"], "verified_post_snapshot_sha256": post["snapshot_sha256"], "old_raw": pre["index"]["raw_index"], "new_raw": post["index"]["raw_index"]})
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
        state.save(output / "RESULT.json", {"success": True, "preservation_verified": True, "updated_only": "raw_index_observation.current", "epoch_sha256": digest(encoded), "before": pre["index"]["raw_index"], "after": post["index"]["raw_index"], "head": policy["head"], "cargo_result_reclassified": False, "cargo_exit": 0, "full_epoch_copies_saved": 0})
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
    print("Canonical raw-index observation refreshed; successful Cargo evidence unchanged", flush=True)


if __name__ == "__main__":
    main()
