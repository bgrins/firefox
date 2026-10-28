import hashlib, json, os, stat, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args], cwd=cwd, env=ENV)
def read(name): return json.loads((ROOT/name).read_bytes())
def sha(body): return hashlib.sha256(body).hexdigest()
def paths(): return sorted(x.decode() for x in git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if x)
def metadata(name):
    s = (ROOT/name).lstat()
    kind = "file" if stat.S_ISREG(s.st_mode) else "symlink" if stat.S_ISLNK(s.st_mode) else "directory" if stat.S_ISDIR(s.st_mode) else "other"
    return dict(path=name, kind=kind, bytes=s.st_size, mode=stat.S_IMODE(s.st_mode), identity=[s.st_dev,s.st_ino])
head = git("rev-parse", "HEAD").decode().strip()
prior_path = "artifacts/css-untracked-audit-post-round-20261028-v1/inventory.json"
prior = read(prior_path)
actual = paths()
assert actual == prior["paths"] and len(actual) == 563
old_project = prior["project_files"]
project_names = {r["path"] for r in old_project}
assert len(project_names) == 68
outside = sorted(set(actual) - project_names)
assert outside == sorted(set(prior["paths"]) - project_names) and len(outside) == 495
recovery = "artifacts/css-worktree-recovery-20261028-v1"
pins_path = recovery + "/SOURCE-PINS.json"
pins = read(pins_path)
assert len(pins) == 75 and project_names <= set(pins)
assert git("show",head+":"+pins_path) == (ROOT/pins_path).read_bytes()
records = []
for old in old_project:
    name = old["path"]; m = metadata(name)
    assert m["kind"] == "file" and all(m[k] == old[k] for k in ("bytes","mode","identity"))
    body = (ROOT/name).read_bytes()
    assert sha(body) == old["sha256"] == pins[name]["sha256"]
    saved = recovery + "/working/" + name
    assert body == (ROOT/saved).read_bytes() == git("show",head+":"+saved)
    records.append(dict(m,sha256=sha(body),signed_copy_path=saved))
commit = git("log","-1","--format=%H",head,"--",recovery).decode().strip()
git("merge-base","--is-ancestor",commit,head)
signers = "artifacts/css-local-signing-20261027-v1/allowed-signers"
sig = subprocess.run(["git","--no-optional-locks","-c","gpg.ssh.allowedSignersFile="+str(ROOT/signers),"verify-commit",commit],cwd=ROOT,env=ENV,capture_output=True,text=True)
assert sig.returncode == 0
head_sig = subprocess.run(["git","--no-optional-locks","-c","gpg.ssh.allowedSignersFile="+str(ROOT/signers),"verify-commit",head],cwd=ROOT,env=ENV,capture_output=True,text=True)
assert head_sig.returncode == 0
tracked = sorted(x.decode() for x in git("diff","--name-only","-z").split(b"\0") if x)
staged = sorted(x.decode() for x in git("diff","--cached","--name-only","-z").split(b"\0") if x)
assert tracked == ["servo/components/style/custom_properties.rs"] and staged == []
epoch = read("artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json")
assert epoch["semantic_index"]["head"] == head and epoch["modified_native_paths"] == tracked
assert epoch["registered_number_transition"]["accepted"] is False
assert sha((ROOT/tracked[0]).read_bytes()) == epoch["pins"][tracked[0]]
nested = git("status","--porcelain=v1","-z",cwd=ROOT/"artifacts/css-spec-lean").decode()
assert nested == prior["nested_status"] == "?? .DS_Store\0"
metadata_only = [metadata(n) for n in outside]
assert paths() == actual and git("rev-parse","HEAD").decode().strip() == head
print(json.dumps(dict(head=head,paths=actual,count=563,project_count=68,unrelated_count=495,root_untracked=563,project_untracked=68,unrelated_untracked=495,
    project_files=records,unrelated_metadata=metadata_only,unrelated_contents_read=False,
    unrelated_names_unchanged=True,unrelated_content_equality_claimed=False,
    unexpected_paths=[],unsaved_project_paths=[],tracked_dirty=tracked,staged_paths=staged,
    held_provider_sha256=epoch["pins"][tracked[0]],nested_status=nested,stable_on_repeat=True,
    recovery_manifest_entries=75,recovery_commit=commit,recovery_commit_is_ancestor=True,
    recovery_signature_verified=True,recovery_signature_output=sig.stdout+sig.stderr,
    head_signature_verified=True,head_signature_output=head_sig.stdout+head_sig.stderr,
    references={n:sha((ROOT/n).read_bytes()) for n in [prior_path,pins_path,signers]},
    source_index_runtime_mutations=False),indent=2,sort_keys=True))
