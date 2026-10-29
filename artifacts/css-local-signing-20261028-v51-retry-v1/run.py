import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
GIT = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]
digest = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def git(*args, env=ENV, data=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, pin):
    directory = ROOT / directory
    assert digest((directory / "FILES.json").read_bytes()) == pin
    result = {}
    for name, entry in read(directory / "FILES.json").items():
        expected = entry["sha256"] if isinstance(entry, dict) else entry
        part = Path(name)
        assert not part.is_absolute() and ".." not in part.parts
        path = directory / part
        assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink()
        assert digest(path.read_bytes()) == expected, str(path)
        if isinstance(entry, dict):
            assert set(entry) == {"sha256", "bytes"} and path.stat().st_size == entry["bytes"]
        result[str(path.relative_to(ROOT))] = expected
    result[str((directory / "FILES.json").relative_to(ROOT))] = pin
    return result


def flags(root):
    rows = subprocess.check_output(GIT + ["ls-files", "-v", "-z"], cwd=root, env=ENV)
    return {row[2:].decode(): row[:1].decode() for row in rows.split(b"\0") if row}


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    authenticate(str(HERE.relative_to(ROOT)), sys.argv[2])
    recovery = read(HERE / "POLICY.json")
    for name, pin in recovery["references"].items():
        assert digest((ROOT / name).read_bytes()) == pin
    origin = ROOT / recovery["original_capsule"]
    authenticate(recovery["original_capsule"], recovery["original_manifest_sha256"])
    policy = read(origin / "POLICY.json")
    for name, pin in policy["helpers"].items():
        assert digest((ROOT / name).read_bytes()) == pin
    output = ROOT / policy["output"]
    failed = read(output / "FAILURE.json")
    assert failed["staging_attempted"] and not failed["commit_command_succeeded"]
    assert not failed["canonical_old_head_not_certified_after_signed_commit"]
    assert failed["rollback_errors"] == [] and not failed["synchronized_final_receipt_preserved"]
    assert not (output / "FINAL-CHECK.json").exists()
    pre = read(output / "PRE.json")
    selected = pre["selection"]
    assert len(selected) == 233 and pre["head"] == policy["head"]
    assert pre["control_hashes"] == policy["controls"]
    roadmap = policy["roadmap"]
    assert selected[roadmap["path"]] == roadmap["after_sha256"]
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    assert git("rev-parse", "HEAD").decode().strip() == policy["head"]
    assert git("symbolic-ref", "HEAD").decode().strip() == policy["branch"]
    assert git("config", "--get", "commit.gpgsign").strip() == b"true"
    assert sorted(git("diff", "--cached", "--name-only", policy["head"]).decode().splitlines()) == sorted(selected)
    for name, pin in selected.items():
        assert digest((ROOT / name).read_bytes()) == pin
        assert digest(git("show", ":" + name)) == pin
        assert git("ls-files", "--stage", "--", name).split()[0] == b"100644"
    assert digest(git("ls-files", "--stage", "-z")) == recovery["pending_index_entries_sha256"]
    state = load("retry_state", policy["state_helper"])
    owned = load("retry_ownership", policy["ownership_helper"])
    controls = {n: (RUNTIME / n).read_bytes() for n in ("CURRENT-EPOCH.json", "ROLE.json", "OWNED.json")}
    assert {n: digest(body) for n, body in controls.items()} == policy["controls"]
    epoch = json.loads(controls["CURRENT-EPOCH.json"])
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    actual_pending = state.h.index_state(ROOT, ENV)
    assert state.h.semantic_index(actual_pending) == recovery["pending_semantic_index"]
    assert actual_pending["working_diff"] == epoch["semantic_index"]["working_diff"]
    nested_before = state.h.index_state(ROOT / "artifacts/css-spec-lean", ENV)
    assert state.h.semantic_index(nested_before) == epoch["nested_semantic_index"]
    for mapping in ("pins", "staged_working", "committed_research_working_payloads"):
        expected = dict(epoch[mapping])
        if roadmap["path"] in expected:
            assert expected[roadmap["path"]] == roadmap["before_sha256"]
            expected[roadmap["path"]] = roadmap["after_sha256"]
        assert {n: state.h.fingerprint(ROOT, n) for n in expected} == expected
    for name, identity in epoch["installed_identities"].items():
        info = (ROOT / name).lstat()
        assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity
    native = {n for n in git("diff", "--name-only").decode().splitlines() if not n.startswith("artifacts/")}
    assert native == set(epoch["modified_native_paths"]) == {"servo/components/style/custom_properties.rs"}
    native_untracked = {n for n in git("ls-files", "--others", "--exclude-standard", "--", "layout", "dom", "servo", "mfbt").decode().splitlines() if not n.startswith("artifacts/")}
    assert native_untracked == set(epoch["untracked_native"])
    native_claims = {n: owned.claim(ROOT, n, rec["sha256"], rec["identity"]) for n, rec in policy["accepted_current_payloads"].items()}
    for name, rec in policy["accepted_current_payloads"].items():
        assert digest(git("show", policy["head"] + ":" + name)) == rec["sha256"]
    old_flags, nested_flags = flags(ROOT), flags(ROOT / "artifacts/css-spec-lean")
    assert digest(owned.encoded(old_flags)) == recovery["root_flags_sha256"]
    assert digest(owned.encoded(nested_flags)) == recovery["nested_flags_sha256"]
    def untracked_names():
        return {n for n in git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0") if n and not n.startswith(recovery["output"] + "/") and not n.startswith(policy["output"] + "/")}
    untracked = untracked_names()
    assert len(untracked) == 563 and digest(owned.encoded(sorted(untracked))) == recovery["untracked_names_sha256"]
    lock = RUNTIME / "SOURCE-TRANSITION.lock"
    assert lock.is_dir() and not lock.is_symlink() and not list(lock.iterdir())
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    assert lock_identity == recovery["lock_identity"]
    before = {"index": actual_pending, "nested_index": nested_before}
    assert state.h.index_state(ROOT, ENV) == actual_pending
    assert state.h.index_state(ROOT / "artifacts/css-spec-lean", ENV) == nested_before
    message = output / "message.txt"
    assert message.read_text() == policy["message"]
    tree = recovery["staged_tree"]
    if sys.argv[1] == "--check":
        print("Authenticated exact retained staging and controls; no signing retry", tree)
        return
    assert recovery["execution_enabled"] and recovery["user_retry_authorized"]
    owned.quiescent(RUNTIME)
    owned.quiescent(ROOT / "artifacts/css-page-selector-native-runtime-v1")
    control_claims = {n: owned.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    retry_output = ROOT / recovery["output"]
    assert not retry_output.exists() and not retry_output.is_symlink()
    retry_output.mkdir()
    save(retry_output / "PRE.json", {"head": policy["head"], "staged_tree": tree, "selection_sha256": digest(owned.encoded(selected)), "lock_identity": lock_identity, "controls": policy["controls"], "no_restaging": True})
    committed = canonical_started = final_published = False
    try:
        assert state.h.index_state(ROOT, ENV) == actual_pending
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        with (retry_output / "commit.log").open("x") as stream:
            result = subprocess.run(GIT + ["commit", "--file", str(message)], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
        assert result.returncode == 0, "Signing retry failed; exact pending selection and lock retained"
        committed = True
        commit = git("rev-parse", "HEAD").decode().strip()
        assert git("rev-parse", commit + "^").decode().strip() == policy["head"]
        assert git("rev-parse", commit + "^{tree}").decode().strip() == tree
        assert sorted(git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()) == sorted(selected)
        with (retry_output / "signature.log").open("x") as stream:
            subprocess.run(GIT + ["-c", "gpg.ssh.allowedSignersFile=" + str(ROOT / policy["allowed_signers"]), "verify-commit", commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
        actual = state.h.index_state(ROOT, ENV)
        assert not git("diff", "--cached", "--name-only")
        assert actual["working_diff"] == before["index"]["working_diff"]
        assert state.h.index_state(ROOT / "artifacts/css-spec-lean", ENV) == before["nested_index"]
        now_flags = flags(ROOT)
        assert all(now_flags[n] == value for n, value in old_flags.items())
        assert set(now_flags) == set(old_flags) | set(selected)
        assert all(now_flags[n] == "H" for n in set(now_flags) - set(old_flags))
        assert flags(ROOT / "artifacts/css-spec-lean") == nested_flags
        assert untracked_names() == untracked
        updated = copy.deepcopy(epoch)
        updated["semantic_index"] = state.h.semantic_index(actual)
        updated["raw_index_observation"]["current"] = actual["raw_index"]
        for mapping in ("pins", "staged_working"):
            if roadmap["path"] in updated[mapping]:
                assert updated[mapping][roadmap["path"]] == roadmap["before_sha256"]
                updated[mapping][roadmap["path"]] = roadmap["after_sha256"]
        updated["committed_research_working_payloads"].update(selected)
        updated["counts"]["committed_research_payloads"] = len(updated["committed_research_working_payloads"])
        post = state.a.verify_current(state.h, ROOT, ENV, updated)
        for name, pin in selected.items():
            assert digest(git("show", commit + ":" + name)) == pin
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        for claim in native_claims.values():
            owned.claim(ROOT, claim["path"], claim["owned_sha256"], claim["identity"])
        canonical_started = True
        owned.write_owned(ROOT, control_claims["CURRENT-EPOCH.json"], owned.encoded(updated))
        assert state.a.verify_current(state.h, ROOT, ENV, updated) == post
        assert all((RUNTIME / n).read_bytes() == controls[n] for n in ("ROLE.json", "OWNED.json"))
        save(output / "FINAL-CHECK.json", {"head": commit, "parent": policy["head"], "tree": tree, "signature_verified": True, "runtime_epoch_synchronized": True, "current_epoch_sha256": digest(owned.encoded(updated)), "accepted_fixes": 145, "tracked_fixes": 146, "accepted_fix_increment": 0, "canonical_coverage_increment": 0, "provider_candidate_accepted": False, "candidate_compiled_or_executed": True, "candidate_restored_after_validation": True, "signing_performed_build_or_browser_execution": False, "native_and_binary_payloads_preserved": True, "nested_index_and_flags_preserved": True, "unselected_untracked_names_preserved": True, "untracked_before": len(untracked), "untracked_after": len(untracked_names()), "selection_count": len(selected), "full_epoch_copies_saved": 0, "explicit_retry": True, "original_failed_attempt_preserved": True})
        final_published = True
        assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
        lock.rmdir()
        print("Signed research checkpoint and synchronized canonical epoch", commit, flush=True)
    except BaseException as error:
        rollback_errors = []
        if canonical_started and not final_published:
            try:
                owned.write_owned(ROOT, control_claims["CURRENT-EPOCH.json"], controls["CURRENT-EPOCH.json"])
            except BaseException as rollback:
                rollback_errors.append(repr(rollback))
        save(retry_output / "FAILURE.json", {"error": repr(error), "commit_command_succeeded": committed, "canonical_started": canonical_started, "synchronized_final_receipt_preserved": final_published, "rollback_errors": rollback_errors, "manual_recovery_required": True, "no_reset_or_automatic_retry": True})
        raise


if __name__ == "__main__":
    main()
