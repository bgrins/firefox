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
prior_path = "artifacts/css-untracked-audit-checkpoint-20261028-v1/inventory.json"
landing = "testing/web-platform/tests/css/css-values/tree-counting/sibling-count-cross-parent-invalidation.html"
landing_hash = "f3e3644a0c9440cbe65d1bc99cc04c169320f86444daa96a57995b282b64e02b"
source = "servo/components/style/values/computed/mod.rs"
assert head == "0ebf4903e6e7f7216c8ba35d0941958d45c24f73"
prior = read(prior_path)
actual = paths()
assert actual == sorted(prior["paths"] + [landing]) and len(actual) == 564
assert landing not in prior["paths"]
old_project = prior["project_files"]
project_names = {r["path"] for r in old_project}
assert len(project_names) == 68
outside = sorted(set(actual) - project_names - {landing})
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
assert tracked == sorted(["servo/components/style/custom_properties.rs", source]) and staged == []
epoch = read("artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json")
assert epoch["semantic_index"]["head"] == head and epoch["modified_native_paths"] == tracked
assert epoch["registered_number_transition"]["accepted"] is False
held = "servo/components/style/custom_properties.rs"
assert sha((ROOT/held).read_bytes()) == epoch["pins"][held]
assert sha((ROOT/source).read_bytes()) == epoch["pins"][source] == "557bcb142d276c32822f5484045e27a5186de1ded244dbd599986f8eba79ee6c"
landing_record = metadata(landing)
assert landing_record["kind"] == "file"
assert sha((ROOT/landing).read_bytes()) == landing_hash == epoch["pins"][landing]
assert landing_record["identity"] == epoch["installed_identities"][landing]
owned = read("artifacts/css-registered-number-native-runtime-v1/OWNED.json")
assert owned[landing]["identity"] == landing_record["identity"] and owned[landing]["owned_sha256"] == landing_hash
assert epoch["sibling_count_rule_cache_transition"]["accepted"] is False
landing_record.update(sha256=landing_hash, classification="owned pending native landing test", accepted=False)
nested = git("status","--porcelain=v1","-z",cwd=ROOT/"artifacts/css-spec-lean").decode()
assert nested == prior["nested_status"] == "?? .DS_Store\0"
metadata_only = [metadata(n) for n in outside]
old_metadata = {r["path"]: r for r in prior.get("unrelated_metadata", [])}
metadata_changes = [r["path"] for r in metadata_only if r["path"] in old_metadata and r != old_metadata[r["path"]]]
assert paths() == actual and git("rev-parse","HEAD").decode().strip() == head
print(json.dumps(dict(head=head,paths=actual,count=564,project_count=68,unrelated_count=495,root_untracked=564,project_untracked=68,unrelated_untracked=495,
    baseline_paths=prior["paths"],only_added=[landing],only_removed=[],landing_files=[landing_record],landing_count=1,
    project_files=records,unrelated_metadata=metadata_only,unrelated_contents_read=False,
    unrelated_names_unchanged=True,unrelated_content_equality_claimed=False, unrelated_metadata_changed_paths=metadata_changes,
    unexpected_paths=[],unsaved_project_paths=[],tracked_dirty=tracked,staged_paths=staged,
    held_provider_sha256=epoch["pins"][held],nested_status=nested,stable_on_repeat=True,
    recovery_manifest_entries=75,recovery_commit=commit,recovery_commit_is_ancestor=True,
    recovery_signature_verified=True,recovery_signature_output=sig.stdout+sig.stderr,
    head_signature_verified=True,head_signature_output=head_sig.stdout+head_sig.stderr,
    references={n:sha((ROOT/n).read_bytes()) for n in [prior_path,pins_path,signers]},
    source_index_runtime_mutations=False),indent=2,sort_keys=True))
