import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import sys
import time
import traceback

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
read = lambda p: json.loads(p.read_bytes())
digest = lambda b: hashlib.sha256(b).hexdigest()
sha = lambda p: digest(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compact(snapshot, flags, epoch_bytes):
    return {"epoch_sha256": digest(epoch_bytes), "snapshot_sha256": digest(json.dumps(snapshot, sort_keys=True).encode()), "index": snapshot["index"], "nested_index": snapshot["nested_index"], "index_flag_hashes": {n: digest(body) for n, body in flags.items()}}


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    assert sha(HERE / "FILES.json") == sys.argv[2]
    for name, pin in read(HERE / "FILES.json").items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert not (HERE / path).is_symlink() and sha(HERE / path) == pin
    policy = read(HERE / "POLICY.json")
    for name, pin in policy["references"].items():
        assert sha(ROOT / name) == pin, name
    if sys.argv[1] == "--check" and policy["candidate"] is None:
        print("Disabled preparation: candidate source roster and manifest remain unbound")
        return
    owned_helper = load("typecheck_ownership", policy["ownership_helper"])
    allowed_captures = {}
    for package in [policy["candidate"]] + policy["capture_packages"]:
        directory = ROOT / package["directory"]
        owned_helper.authenticate(directory, package["sha256"])
        for name, entry in read(directory / "FILES.json").items():
            pin = entry["sha256"] if isinstance(entry, dict) else entry
            capture_name = str(Path(package["directory"]) / name)
            assert capture_name not in allowed_captures or allowed_captures[capture_name] == pin
            allowed_captures[capture_name] = pin
    assert (HERE / "SOURCE-ROLES.json").read_bytes() == (ROOT / policy["candidate"]["directory"] / "SOURCE-ROLES.json").read_bytes()
    roles = read(HERE / "SOURCE-ROLES.json")
    assert set(roles) == set(policy["source_paths"]) and roles
    assert set(roles) & set(policy["accepted_current_payloads"]) == {"servo/components/style/values/specified/easing.rs"}
    assert "servo/components/style/values/generics/calc.rs" not in roles
    assert "servo/components/style/custom_properties.rs" not in roles
    base, candidate = {}, {}
    for name, record in roles.items():
        assert name.startswith("servo/") and ".." not in Path(name).parts
        for kind, target in (("base", base), ("candidate", candidate)):
            capture = Path(record[kind + "_capture"])
            assert allowed_captures.get(str(capture)) == record[kind + "_sha256"]
            assert not capture.is_absolute() and ".." not in capture.parts
            assert not (ROOT / capture).is_symlink()
            target[name] = (ROOT / capture).read_bytes()
            assert digest(target[name]) == record[kind + "_sha256"]
        assert base[name] != candidate[name]
    if sys.argv[1] == "--check":
        print("Authenticated disabled/enabled preparation; source paths:", len(roles), "enabled:", policy["execution_enabled"])
        return
    assert policy["execution_enabled"] is True
    assert policy["start_free_bytes"] == 30 * 1024**3 and policy["running_stop_bytes"] == 15 * 1024**3
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "CC", "CXX", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_TARGET_DIR", "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER"))
    state = load("typecheck_state", policy["state_helper"])
    builder = load("typecheck_builder", policy["phase_helper"])
    control = load("typecheck_process", policy["process_helper"])
    controls = {n: (RUNTIME / n).read_bytes() for n in ("CURRENT-EPOCH.json", "ROLE.json", "OWNED.json")}
    assert {n: digest(body) for n, body in controls.items()} == policy["controls"]
    epoch = json.loads(controls["CURRENT-EPOCH.json"])
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    assert epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"]
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    roots = {"root": ROOT, "nested": ROOT / "artifacts/css-spec-lean"}
    flags = {n: state.h.git(path, ENV, "ls-files", "-v", "-z") for n, path in roots.items()}
    claims = {n: owned_helper.claim(ROOT, n, r["base_sha256"]) for n, r in roles.items()}
    modes = {n: stat.S_IMODE((ROOT / n).lstat().st_mode) for n in roles}
    accepted = {n: owned_helper.claim(ROOT, n, r["sha256"], r["identity"]) for n, r in policy["accepted_current_payloads"].items()}
    for name in roles:
        assert state.h.git(ROOT, ENV, "show", policy["head"] + ":" + name) == base[name]
        if name in accepted:
            assert accepted[name] == claims[name]
            claims[name] = accepted[name]
    for name, record in policy["accepted_current_payloads"].items():
        assert digest(state.h.git(ROOT, ENV, "show", policy["head"] + ":" + name)) == record["sha256"]
    control_claims = {n: owned_helper.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    outside_args = ["diff", "--binary", "--", "."] + [":(exclude)" + n for n in roles]
    outside = state.h.git(ROOT, ENV, *outside_args)
    output = ROOT / policy["output"]
    assert output.parent == ROOT / "artifacts" and not output.exists() and not output.is_symlink()
    lock = RUNTIME / "SOURCE-TRANSITION.lock"
    assert not lock.exists() and not lock.is_symlink()
    owned_helper.quiescent(RUNTIME)
    for name in policy["closed_process_receipts"]:
        owned_helper.group_absent(read(ROOT / name)["pgid"])
    sys.path[:0] = [str(ROOT / "python/mozbuild"), str(ROOT / "testing/mozbase/mozshellutil")]
    from mozbuild.rust_commands import CargoInvocation, compose_env, compose_mach_cargo_argv, load_cargo_spec
    spec_path = ROOT / policy["configured_spec"]
    command, substs, src, obj = load_cargo_spec(read(spec_path))
    assert src == str(ROOT) and obj == str(ROOT / "objdir-full.noindex")
    assert Path(obj).is_dir()
    invocation = CargoInvocation.from_environ(ENV)
    argv = compose_mach_cargo_argv(command, substs, invocation, "check", extra_cli_flags=("--offline",), jobs=2, auto_args=True)
    env = compose_env(command, substs, ENV, invocation, src, obj, ltoable=True, subcommand="check")
    assert env["CARGO_TARGET_DIR"] == obj
    assert os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize >= policy["start_free_bytes"]
    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
    output.mkdir()
    state.save(output / "PRE.json", compact(before, flags, controls["CURRENT-EPOCH.json"]))
    state.save(output / "COMMAND.json", {"argv": argv, "cwd": command.working_directory, "target_directory": obj, "configured_spec_sha256": sha(spec_path), "composition_sha256": policy["references"]["python/mozbuild/mozbuild/rust_commands.py"], "scope": "Configured Gecko Rust graph only; no linked browser build or tests"})
    state.save(output / "SOURCES.json", {n: dict(roles[n], identity=claims[n]["identity"], mode=modes[n]) for n in roles})
    cancelled = [False]
    def stop(signum, frame):
        cancelled[0] = True
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, stop)
    processes, publication_errors, restoration_errors, touched = {}, [], [], []
    error = None
    with lock.open("x") as stream:
        stream.write(json.dumps({"pid": os.getpid(), "runtime": policy["output"]}) + "\n")
    lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
    try:
        assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
        for name in roles:
            touched.append(name)
            owned_helper.write_owned(ROOT, claims[name], candidate[name])
        overlay = copy.deepcopy(epoch)
        for name, record in roles.items():
            if name in overlay["pins"]:
                assert overlay["pins"][name] == record["base_sha256"]
            overlay["pins"][name] = record["candidate_sha256"]
            overlay["installed_identities"][name] = claims[name]["identity"]
        index = state.h.index_state(ROOT, ENV)
        assert all(index[k] == before["index"][k] for k in ("head", "entries", "cached_diff"))
        assert state.h.git(ROOT, ENV, *outside_args) == outside
        overlay["semantic_index"] = state.h.semantic_index(index)
        overlay["raw_index_observation"]["current"] = index["raw_index"]
        overlay["modified_native_paths"] = sorted(set(epoch["modified_native_paths"]) | set(roles))
        overlay["counts"].update(roles=len(overlay["pins"]), installed_identities=len(overlay["installed_identities"]), native_modified_paths=len(overlay["modified_native_paths"]))
        state.a.verify_current(state.h, ROOT, ENV, overlay)
        for item in list(accepted.values()) + list(control_claims.values()):
            owned_helper.claim(ROOT, item["path"], item["owned_sha256"], item["identity"])
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        assert all(state.h.git(path, ENV, "ls-files", "-v", "-z") == flags[n] for n, path in roots.items())
        state.save(output / "INSTALLED.json", {n: {"sha256": sha(ROOT / n), "identity": claims[n]["identity"]} for n in roles})
        state.save(output / "BUILD-PREFLIGHT.json", {"free_bytes": os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize, "start_minimum_bytes": policy["start_free_bytes"], "running_stop_bytes": policy["running_stop_bytes"]})
        deadline = time.monotonic() + policy["timeout_seconds"]
        builder.run(Path(command.working_directory), Path(obj), output, env, lambda: cancelled[0] or time.monotonic() >= deadline, processes, control, argv, publication_errors)
    except BaseException as exc:
        error = repr(exc)
        (output / "ERROR-TRACEBACK.txt").write_text(traceback.format_exc())
    finally:
        if processes:
            restoration_errors.append("Owned compiler groups remain; source restoration deferred")
        else:
            for name in reversed(touched):
                try:
                    owned_helper.write_owned(ROOT, claims[name], base[name])
                except BaseException as exc:
                    restoration_errors.append(name + ": " + repr(exc))
        state.save(output / "RESTORATION.json", {"errors": restoration_errors, "owned_processes": processes, "sources": {n: {"sha256": sha(ROOT / n), "identity": [(ROOT / n).lstat().st_dev, (ROOT / n).lstat().st_ino], "mode": stat.S_IMODE((ROOT / n).lstat().st_mode)} for n in roles}})
    preservation_error = None
    try:
        assert not restoration_errors and not processes
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        index = state.h.index_state(ROOT, ENV)
        assert state.h.semantic_index(index) == epoch["semantic_index"]
        post_epoch = copy.deepcopy(epoch)
        post_epoch["raw_index_observation"]["current"] = index["raw_index"]
        after = state.a.verify_current(state.h, ROOT, ENV, post_epoch)
        assert after["nested_index"] == before["nested_index"]
        assert all(state.h.git(path, ENV, "ls-files", "-v", "-z") == flags[n] for n, path in roots.items())
        for item in list(claims.values()) + list(accepted.values()) + list(control_claims.values()):
            owned_helper.claim(ROOT, item["path"], item["owned_sha256"], item["identity"])
        assert all(sha(ROOT / n) == roles[n]["base_sha256"] and stat.S_IMODE((ROOT / n).lstat().st_mode) == modes[n] for n in roles)
        state.save(output / "POST.json", compact(after, flags, controls["CURRENT-EPOCH.json"]))
        state.save(output / "RAW-INDEX-OBSERVATION.json", {"before": before["index"]["raw_index"], "after": index["raw_index"], "changed": index["raw_index"] != before["index"]["raw_index"], "semantic_index_unchanged": True, "canonical_updated": False, "cause": "not established" if index["raw_index"] != before["index"]["raw_index"] else None})
        assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
        lock.unlink()
    except BaseException as exc:
        preservation_error = repr(exc)
        (output / "PRESERVATION-TRACEBACK.txt").write_text(traceback.format_exc())
    inner = read(output / "build-RESULT.json") if (output / "build-RESULT.json").exists() else None
    actual_success = inner is not None and inner.get("exit") == 0 and inner.get("error") is None and inner.get("stop_reason") is None and inner.get("owned_group_absent") is True and inner.get("cleanup_errors") == []
    success = error is None and preservation_error is None and not publication_errors and actual_success
    state.save(output / "RESULT.json", {"success": success, "error": error, "preservation_error": preservation_error, "publication_errors": publication_errors, "source_restored": not restoration_errors and not processes, "preservation_verified": preservation_error is None, "owned_processes": processes, "runtime_controls_unchanged": preservation_error is None, "actual_cargo_success": actual_success, "browser_build_performed": False, "browser_tests_performed": False, "new_target_directory_created": False, "full_epoch_copies_saved": 0})
    assert success, "Typecheck or preservation failed; inspect exact receipts and retained lock"
    print("Configured Gecko Rust check passed; exact source bodies restored and canonical controls unchanged", flush=True)


if __name__ == "__main__":
    main()
