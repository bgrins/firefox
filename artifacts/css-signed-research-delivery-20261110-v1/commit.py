import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
GIT = ["git", "-c", "core.fsmonitor=false"]

def run(repo, args):
    return subprocess.run(GIT + args, cwd=repo, capture_output=True)

def checked(repo, args):
    result = run(repo, args)
    if result.returncode:
        raise RuntimeError((args, result.returncode, result.stderr.decode()))
    return result.stdout

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def item(version, name, subject):
    path = ROOT / f"artifacts/css-pending-delivery-audit-20261110-v{version}/{name}.json"
    data = json.loads(path.read_text())
    return {"repo": str(ROOT), "manifest": str(path.relative_to(ROOT)), "manifest_sha256": sha(path), "files": data["files"], "subject": "No bug - " + subject + ". r?#firefox-style-system-reviewers"}

jobs = [
    item(1, "02-lean-lexical-bridge", "Prove numeric lexical model correspondence"),
    item(1, "03-native-numeric-evidence", "Record native numeric differential evidence"),
    item(1, "04-numeric-next-preparation", "Prepare numeric feature sensitivity checks"),
    item(2, "01-numeric-lock-failure-and-v2-recipe", "Record numeric build lock failure and revised recipe"),
    item(2, "02-numeric-reuse-failure-and-v3-recipe", "Isolate numeric feature builds after reuse failure"),
    item(2, "03-numeric-v3-terminal-acceptance", "Validate isolated numeric feature comparisons"),
    item(4, "01-numeric-bounded-search", "Expand bounded native numeric differential search"),
    item(4, "02-numeric-library-integration-research", "Review standalone numeric library integration"),
    item(1, "05-getter-investigation", "Investigate keyframe serialization and sampling"),
    item(1, "06-getter-repair-research", "Validate specified keyframe getter repair"),
    item(1, "08-query-preparation-and-v1-evidence", "Prepare transient animation query experiments"),
    item(2, "04-query-v2-build-failure", "Record transient query build failure and restoration"),
    item(2, "05-query-v3-partial-execution", "Record partial transient query execution"),
    item(3, "01-query-v4-helper-acceptance", "Validate bounded transient animation query helper"),
    item(4, "03-structured-grammar-derivation", "Derive finite Lean grammars from CSS value tables"),
    item(4, "04-structured-grammar-transfer", "Check grammar extraction across CSS modules"),
    item(4, "05-code-verification-paper-assessment", "Assess protected specification and binary proof workflows"),
]
pilot = {}
for capsule in ["css-lean-comparator-pilot-20261110-v1", "css-lean-comparator-pilot-review-20261110-v1"]:
    for path in sorted((ROOT / "artifacts" / capsule).rglob("*")):
        assert not path.is_symlink(), path
        if path.is_file():
            assert not any(part in {".git", ".lake", "target", "__pycache__"} for part in path.parts), path
            assert path.suffix not in {".olean", ".ilean", ".o", ".pyc"}, path
            pilot[str(path.relative_to(ROOT))] = sha(path)
(OUT / "COMPARATOR-FILES.json").write_text(json.dumps(pilot, indent=2) + "\n")
jobs.append({"repo": str(ROOT), "manifest": str((OUT / "COMPARATOR-FILES.json").relative_to(ROOT)), "files": pilot, "subject": "No bug - Exercise protected theorem comparison with negative controls. r?#firefox-style-system-reviewers"})
canonical_manifest = ROOT / "artifacts/css-number-lexical-library-review-20261110-v1/APPLIED.json"
canonical = json.loads(canonical_manifest.read_text())
jobs.append({"repo": str(ROOT / "artifacts/css-spec-lean"), "manifest": str(canonical_manifest.relative_to(ROOT)), "files": canonical["files"], "subject": "Integrate verified numeric lexical correspondence"})
assert checked(ROOT, ["rev-parse", "HEAD"]).decode().strip() == "f8dda86bbc825386a13eb4182af532cc243a86a6"
assert checked(Path(jobs[-1]["repo"]), ["rev-parse", "HEAD"]).decode().strip() == canonical["base"]
seen = set()
for job in jobs:
    repo = Path(job["repo"])
    for path, digest in job["files"].items():
        key = (str(repo), path)
        assert key not in seen, key
        seen.add(key)
        assert not (repo / path).is_symlink(), path
        assert sha(repo / path) == digest, path
    assert checked(repo, ["config", "--get", "gpg.format"]).decode().strip() == "ssh"
    assert run(repo, ["diff", "--cached", "--quiet"]).returncode == 0
assert run(ROOT, ["diff", "--quiet"]).returncode == 0
(OUT / "PLAN.json").write_text(json.dumps(jobs, indent=2) + "\n")
untracked_before = checked(ROOT, ["ls-files", "--others", "--exclude-standard", "-z"])
(OUT / "UNTRACKED-BEFORE.nul").write_bytes(untracked_before)
ds = ROOT / "artifacts/css-spec-lean/.DS_Store"
assert sha(ds) == "21e80780f65feb251cfd08d4faef1f230a97c6009b4454361ea58b3a2bf45498"
receipts = []
for index, job in enumerate(jobs, 1):
    repo = Path(job["repo"])
    paths = list(job["files"])
    group = OUT / f"commit-{index:02d}"
    group.mkdir(exist_ok=False)
    before = checked(repo, ["rev-parse", "HEAD"]).decode().strip()
    assert run(repo, ["diff", "--cached", "--quiet"]).returncode == 0
    for path, digest in job["files"].items():
        assert sha(repo / path) == digest, path
    pathspec = group / "paths.nul"
    pathspec.write_bytes(b"".join(p.encode() + b"\0" for p in paths))
    checked(repo, ["add", "-f", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul"])
    staged = checked(repo, ["diff", "--cached", "--name-only", "-z"]).decode().split("\0")[:-1]
    assert sorted(staged) == sorted(paths), staged
    print(f"Signing {index}/{len(jobs)}: {job['subject']}", flush=True)
    result = run(repo, ["commit", "-S", "-m", job["subject"]])
    (group / "commit.stdout").write_bytes(result.stdout)
    (group / "commit.stderr").write_bytes(result.stderr)
    after = checked(repo, ["rev-parse", "HEAD"]).decode().strip()
    receipt = {"repo": str(repo), "before": before, "after": after, "subject": job["subject"], "manifest": job["manifest"], "file_count": len(paths), "commit_exit": result.returncode}
    if result.returncode:
        assert after == before
        checked(repo, ["restore", "--staged", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul"])
        receipt["index_restored"] = run(repo, ["diff", "--cached", "--quiet"]).returncode == 0
    else:
        changed = checked(repo, ["diff-tree", "--no-commit-id", "--name-only", "-r", "-z", after]).decode().split("\0")[:-1]
        assert sorted(changed) == sorted(paths), changed
        key = checked(repo, ["config", "--get", "user.signingkey"]).decode().strip().removeprefix("key::")
        if not key.startswith(("ssh-", "ecdsa-")):
            key_path = Path(key).expanduser()
            if key_path.suffix != ".pub":
                key_path = Path(str(key_path) + ".pub")
            key = key_path.read_text().strip()
        parts = key.split()
        assert len(parts) >= 2 and parts[0].startswith(("ssh-", "ecdsa-"))
        principal = checked(repo, ["show", "-s", "--format=%ce", after]).decode().strip()
        with tempfile.TemporaryDirectory(prefix="css-signature-verification-") as temp:
            allowed = Path(temp) / "allowed-signers"
            allowed.write_text(principal + " " + parts[0] + " " + parts[1] + "\n")
            allowed.chmod(0o600)
            verified = run(repo, ["-c", "gpg.ssh.allowedSignersFile=" + str(allowed), "verify-commit", after])
        (group / "verify.stdout").write_bytes(verified.stdout)
        (group / "verify.stderr").write_bytes(verified.stderr)
        receipt["verify_exit"] = verified.returncode
        receipt["index_clean"] = run(repo, ["diff", "--cached", "--quiet"]).returncode == 0
        receipt["tracked_clean"] = run(repo, ["diff", "--quiet"]).returncode == 0
    (group / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    receipts.append(receipt)
    (OUT / "COMMITS.json").write_text(json.dumps(receipts, indent=2) + "\n")
    assert result.returncode == 0, receipt
    assert receipt["verify_exit"] == 0 and receipt["index_clean"] and receipt["tracked_clean"], receipt
    print(f"Verified {after} ({len(paths)} files)", flush=True)
assert checked(ROOT, ["ls-files", "--others", "--exclude-standard", "-z"]) == untracked_before
assert sha(ds) == "21e80780f65feb251cfd08d4faef1f230a97c6009b4454361ea58b3a2bf45498"
(OUT / "RESULT.json").write_text(json.dumps({"status":"PASS", "signed_verified_commits":len(receipts), "original_untracked_preserved":True, "canonical_ds_store_preserved":True},indent=2)+"\n")
print("All research commits signed and verified; original untracked files preserved.", flush=True)
