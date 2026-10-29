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
    selected = authenticate(str(HERE.relative_to(ROOT)), sys.argv[2])
    policy = read(HERE / "POLICY.json")
    for package in policy["packages"]:
        for name, pin in authenticate(package["directory"], package["sha256"]).items():
            assert name not in selected
            selected[name] = pin
    for name, pin in policy["previous_receipts"].items():
        assert digest((ROOT / name).read_bytes()) == pin
        assert name not in selected
        selected[name] = pin
    for name, pin in policy["helpers"].items():
        assert digest((ROOT / name).read_bytes()) == pin
    assert all(n.startswith("artifacts/") and not n.startswith("artifacts/css-spec-lean/") for n in selected)
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    assert git("rev-parse", "HEAD").decode().strip() == policy["head"]
    assert git("symbolic-ref", "HEAD").decode().strip() == policy["branch"]
    roadmap = policy["roadmap"]
    original = (ROOT / roadmap["path"]).read_bytes()
    assert digest(original) == roadmap["before_sha256"]
    assert git("show", policy["head"] + ":" + roadmap["path"]) == original
    postimage = (HERE / "ROADMAP-PREFIX.md").read_bytes() + original
    assert digest(postimage) == roadmap["after_sha256"]
    existing = set(git("ls-tree", "-r", "--name-only", policy["head"]).decode().splitlines())
    skipped = {}
    for name in list(selected):
        if name in existing:
            assert digest(git("show", policy["head"] + ":" + name)) == selected[name], name
            skipped[name] = selected.pop(name)
    selected[roadmap["path"]] = roadmap["after_sha256"]
    if sys.argv[1] == "--check":
        print(json.dumps({"selected": len(selected), "already_committed_identical": len(skipped), "capsule_sha256": sys.argv[2], "execution_enabled": policy["execution_enabled"]}, sort_keys=True))
        return
    assert policy["execution_enabled"] is True
    assert git("config", "--get", "commit.gpgsign").strip() == b"true"
    state = load("compact_state", policy["state_helper"])
    owned = load("compact_ownership", policy["ownership_helper"])
    controls = {n: (RUNTIME / n).read_bytes() for n in ("CURRENT-EPOCH.json", "ROLE.json", "OWNED.json")}
    assert {n: digest(body) for n, body in controls.items()} == policy["controls"]
    epoch = json.loads(controls["CURRENT-EPOCH.json"])
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    assert epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"]
    assert epoch["accepted_sibling_count_rule_cache"]["fix"] == 146
    assert epoch["accepted_round_context_quotient"]["fix"] == 145
    assert epoch["accepted_round_special_knowledge"]["fix"] == 144
    assert epoch["committed_research_working_payloads"][roadmap["path"]] == roadmap["before_sha256"]
    old_flags, nested_flags = flags(ROOT), flags(ROOT / "artifacts/css-spec-lean")
    def untracked_names():
        return {n for n in git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0") if n and not n.startswith(policy["output"] + "/")}
    untracked = untracked_names()
    native_claims = {name: owned.claim(ROOT, name, record["sha256"], record["identity"]) for name, record in policy["accepted_current_payloads"].items()}
    for name, record in policy["accepted_current_payloads"].items():
        assert digest(git("show", policy["head"] + ":" + name)) == record["sha256"]
    control_claims = {n: owned.claim(ROOT, str((RUNTIME / n).relative_to(ROOT)), digest(body)) for n, body in controls.items()}
    roadmap_claim = owned.claim(ROOT, roadmap["path"], roadmap["before_sha256"])
    owned.quiescent(RUNTIME)
    owned.quiescent(ROOT / "artifacts/css-page-selector-native-runtime-v1")
    lock = RUNTIME / "SOURCE-TRANSITION.lock"
    assert not lock.exists()
    output = ROOT / policy["output"]
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    save(output / "PRE.json", {"head": policy["head"], "control_hashes": policy["controls"], "full_verifier_passed": True, "selection": selected, "already_committed_identical": skipped, "snapshot_sha256": digest(owned.encoded(before))})
    lock.mkdir()
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    staged = False
    committed = False
    canonical_started = False
    final_published = False
    try:
        with tempfile.TemporaryDirectory(prefix="css-research-signing-", dir="/private/tmp") as temporary:
            temporary = Path(temporary)
            index_env = dict(ENV, GIT_INDEX_FILE=str(temporary / "index"))
            git("read-tree", policy["head"], env=index_env)
            names = temporary / "paths"
            names.write_bytes(b"".join(n.encode() + b"\0" for n in selected if n != roadmap["path"]))
            git("add", "-f", "--pathspec-from-file=" + str(names), "--pathspec-file-nul", env=index_env)
            blob = git("hash-object", "-w", "--stdin", data=postimage).decode().strip()
            git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + roadmap["path"], env=index_env)
            assert sorted(git("diff", "--cached", "--name-only", policy["head"], env=index_env).decode().splitlines()) == sorted(selected)
            for name, pin in selected.items():
                assert digest(git("show", ":" + name, env=index_env)) == pin
                assert git("ls-files", "--stage", "--", name, env=index_env).split()[0] == b"100644"
            tree = git("write-tree", env=index_env).decode().strip()
            patch = temporary / "selected.patch"
            patch.write_bytes(git("diff", "--cached", "--binary", "--full-index", policy["head"], env=index_env))
            assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
            assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
            for claim in native_claims.values():
                owned.claim(ROOT, claim["path"], claim["owned_sha256"], claim["identity"])
            owned.write_owned(ROOT, roadmap_claim, postimage)
            git("apply", "--cached", "--check", str(patch))
            staged = True
            git("apply", "--cached", str(patch))
            assert git("write-tree").decode().strip() == tree
            message = output / "message.txt"
            message.write_text(policy["message"].rstrip() + "\n")
            with (output / "commit.log").open("x") as stream:
                result = subprocess.run(GIT + ["commit", "--file", str(message)], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
            assert result.returncode == 0, "Signing failed; selected index and roadmap retained for explicit recovery"
            committed = True
        commit = git("rev-parse", "HEAD").decode().strip()
        assert git("rev-parse", commit + "^").decode().strip() == policy["head"]
        assert git("rev-parse", commit + "^{tree}").decode().strip() == tree
        assert sorted(git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()) == sorted(selected)
        with (output / "signature.log").open("x") as stream:
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
        assert untracked_names() == untracked - set(selected)
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
        save(output / "FINAL-CHECK.json", {"head": commit, "parent": policy["head"], "tree": tree, "signature_verified": True, "runtime_epoch_synchronized": True, "current_epoch_sha256": digest(owned.encoded(updated)), "accepted_fixes": 145, "tracked_fixes": 146, "accepted_fix_increment": 0, "canonical_coverage_increment": 0, "provider_candidate_accepted": False, "candidate_compiled_or_executed": False, "native_and_binary_payloads_preserved": True, "nested_index_and_flags_preserved": True, "unselected_untracked_names_preserved": True, "untracked_before": len(untracked), "untracked_after": len(untracked_names()), "selection_count": len(selected), "full_epoch_copies_saved": 0})
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
        if not staged:
            try:
                owned.write_owned(ROOT, roadmap_claim, original)
                assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
            except BaseException as rollback:
                rollback_errors.append(repr(rollback))
        save(output / "FAILURE.json", {"error": repr(error), "staging_attempted": staged, "commit_command_succeeded": committed, "rollback_errors": rollback_errors, "manual_recovery_required": staged or bool(rollback_errors), "canonical_old_head_not_certified_after_signed_commit": committed and not final_published, "synchronized_final_receipt_preserved": final_published, "note": "No signing retry or index reset is automatic. Pending staged state retains the lock; a published synchronized final receipt is never invalidated by lock-release failure."})
        if not staged and not rollback_errors:
            assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
            lock.rmdir()
        raise


if __name__ == "__main__":
    main()
