import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
read = lambda p: json.loads(p.read_bytes())
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda p: digest(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_adoption(policy, original, observed, staging, role):
    assert original["semantic_index"]["head"] == policy["head"]
    assert original["staged_working"] == {}
    assert original["registered_number_transition"] == {
        "role": "candidate", "variant": "registered-provider-default-v4",
        "compiled": True, "accepted": False,
        "last_phase": "provider-default-candidate-build-2",
    }
    assert role["role"] == "candidate" and role["variant"] == "registered-provider-default-v4"
    assert role["built"] is True and role["last_build"] == "provider-default-candidate-build-2"
    assert staging["build_epoch_sha256"] == policy["expected_runtime_epoch"]
    assert staging["observation_epoch_sha256"] == policy["observed_epoch_sha256"]
    assert len(staging["staged_files"]) == policy["staged_paths"] == 36
    assert len(set(staging["staged_files"])) == 36
    assert set(staging["staged_files"]) == set(staging["staged_working"])
    assert all(n.startswith("artifacts/") and n != "artifacts/css-spec-lean"
               and not n.startswith("artifacts/css-spec-lean/") for n in staging["staged_files"])
    assert staging["semantic_index"]["head"] == original["semantic_index"]["head"]
    assert staging["semantic_index"]["working_diff"] == original["semantic_index"]["working_diff"]
    expected = copy.deepcopy(original)
    expected["semantic_index"] = staging["semantic_index"]
    expected["raw_index_observation"]["current"] = staging["raw_index"]
    expected["staged_working"] = staging["staged_working"]
    assert expected == observed
    return expected


def absent_output(runtime, label):
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", label)
    assert runtime.is_dir() and not runtime.is_symlink()
    path = runtime / label
    assert not os.path.lexists(path)
    return path


def main():
    manifest, expected_runtime = sys.argv[1:]
    policy = read(HERE / "POLICY.json")
    assert policy["execution_enabled"], "Disabled pending review"
    assert not any(os.environ.get(k) for k in [
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "RUSTFLAGS", "CARGO_TARGET_DIR",
    ])
    ownership = load("adoption_ownership", "artifacts/css-registered-number-source-transition-v4/transition.py")
    creation = load("adoption_creation", "artifacts/css-registered-admission-wpt-install-v1/install.py")
    runtime = ROOT / policy["runtime"]
    state = load("adoption_state", str((runtime / "state.py").relative_to(ROOT)))
    capsule = ROOT / policy["staged_capsule"]
    guard = load("adoption_staged_guard", str((capsule / "epoch.py").relative_to(ROOT)))

    def authenticate():
        ownership.authenticate(HERE, manifest)
        ownership.authenticate(capsule, policy["staged_capsule_sha256"])
        for name, pin in read(HERE / "REFERENCES.json").items():
            assert sha(ROOT / name) == pin, name

    authenticate()
    bodies = {n: ownership.body(runtime / n) for n in ["CURRENT-EPOCH.json", "ROLE.json", "OWNED.json"]}
    assert digest(bodies["CURRENT-EPOCH.json"]) == expected_runtime == policy["expected_runtime_epoch"]
    assert digest(bodies["ROLE.json"]) == policy["role_sha256"]
    assert digest(bodies["OWNED.json"]) == policy["owned_sha256"]
    original, role = json.loads(bodies["CURRENT-EPOCH.json"]), json.loads(bodies["ROLE.json"])
    target_bytes = ownership.body(capsule / "OBSERVATION-EPOCH.json")
    assert digest(target_bytes) == policy["observed_epoch_sha256"]
    observed, staging = json.loads(target_bytes), read(capsule / "STAGING.json")
    validate_adoption(policy, original, observed, staging, role)
    assert sha(ROOT / staging["staged_patch"]) == staging["staged_patch_sha256"]
    before = guard.verify_current(state.h, ROOT, ENV, observed)
    flags = {n: state.h.git(ROOT / n, ENV, "ls-files", "-v", "-z") for n in [".", "artifacts/css-spec-lean"]}
    claims = {n: ownership.claim(ROOT, str((runtime / n).relative_to(ROOT)), digest(data)) for n, data in bodies.items()}

    def preserve():
        assert guard.verify_current(state.h, ROOT, ENV, observed) == before
        assert all(state.h.git(ROOT / n, ENV, "ls-files", "-v", "-z") == data for n, data in flags.items())
        assert all((runtime / n).read_bytes() == bodies[n] for n in ["ROLE.json", "OWNED.json"])

    def recheck_claims():
        authenticate()
        for claim in claims.values():
            ownership.claim(ROOT, claim["path"], claim["owned_sha256"], claim["identity"])

    def quiescent():
        ownership.quiescent(runtime)
        build = runtime / role["last_build"]
        result = read(build / "RESULT.json")
        assert result["command_success"] and result["preservation_verified"]
        assert not result["owned_processes"] and not result["publication_errors"]
        assert read(build / "EPOCH.json") == original
        for name in ["build-PROCESS.json", "WAKE-PROCESS.json"]:
            ownership.group_absent(read(build / name)["pgid"])
        for name in policy["completed_observers"]:
            directory = ROOT / name
            result, cleanup = read(directory / "RESULT.json"), read(directory / "CLEANUP.json")
            assert result["observation_gate_passed"] and result["execution_error"] is None and result["preservation_error"] is None
            assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
            ownership.group_absent(read(directory / "PROCESS.json")["pgid"])

    quiescent()
    output = absent_output(runtime, policy["adoption_label"])
    lock = runtime / "SOURCE-TRANSITION.lock"
    assert not os.path.lexists(lock)
    lock_claim, changed, output_identity = None, False, None
    try:
        blocked = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
        try:
            lock_claim = creation.create_owned(ownership, ROOT, str(lock.relative_to(ROOT)), creation.parent_pins(ROOT, lock))
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, blocked)
        output.mkdir()
        info = output.stat()
        output_identity = (info.st_dev, info.st_ino)
        ownership.save(output / "PRE.json", before)
        for name, data in bodies.items():
            (output / ("PRE-" + name)).write_bytes(data)
        ownership.save(output / "STAGING.json", staging)
        preserve()
        recheck_claims()
        quiescent()
        recheck_claims()
        changed = True
        ownership.write_owned(ROOT, claims["CURRENT-EPOCH.json"], target_bytes)
        preserve()
        recheck_claims()
        assert (runtime / "CURRENT-EPOCH.json").read_bytes() == target_bytes
        ownership.save(output / "POST.json", before)
        (output / "EPOCH.json").write_bytes(target_bytes)
        ownership.save(output / "RESULT.json", {
            "adopted": True, "metadata_only": True, "preservation_verified": True,
            "source_or_index_writes": False, "staged_paths": 36,
            "old_epoch_sha256": expected_runtime, "epoch_sha256": digest(target_bytes),
            "native_fix_accepted": False,
        })
    except BaseException as error:
        failures = []
        try:
            if changed:
                ownership.write_owned(ROOT, claims["CURRENT-EPOCH.json"], bodies["CURRENT-EPOCH.json"])
            assert all((runtime / n).read_bytes() == data for n, data in bodies.items())
            preserve()
            recheck_claims()
        except BaseException as rollback:
            failures.append(repr(rollback))
        if output_identity is not None and not output.is_symlink() and output.is_dir() and (output.stat().st_dev, output.stat().st_ino) == output_identity:
            ownership.save(output / "FAILURE.json", {"error": repr(error), "rollback_errors": failures,
                           "manual_recovery_required": bool(failures), "old_controls_restored": not failures})
        raise
    finally:
        if lock_claim:
            ownership.claim(ROOT, lock_claim["path"], lock_claim["owned_sha256"], lock_claim["identity"])
            lock.unlink()
    print("Adopted exact staged epoch", digest(target_bytes), flush=True)


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise RuntimeError("Interrupted: " + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
