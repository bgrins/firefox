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
    item(5, '01-transient-recascade-source', 'Model transient animation rule recascading'),
    item(5, '02-transient-recascade-build-failure', 'Record recascade enum failure and revised setup'),
    item(5, '03-transient-recascade-geometry-failure', 'Diagnose scroll geometry in recascade tests'),
    item(5, '04-transient-recascade-acceptance', 'Validate bounded transient recascade helper'),
    item(5, '05-transition-origin-investigation', 'Investigate null-progress transition origin selection'),
    item(5, '06-transition-origin-conditional-model', 'Prove conditional transition origin properties'),
    item(5, '07-transition-origin-held-proposal', 'Record a held transition origin-filtering proposal'),
    item(5, '08-webkit-inconclusive-comparison', 'Record inconclusive WebKit timing comparison'),
    item(5, '09-composed-recascade-source', 'Prepare combined animation composition diagnostics'),
    item(5, "10-pending-timing-witness", "Demonstrate pending animation sampling time divergence"),
    item(5, "11-public-provider-design", "Map public pseudo style provider integration requirements"),
    item(5, "12-unordered-combinator-proof", "Prove bounded CSS unordered grammar semantics"),
]
assert checked(ROOT, ["rev-parse", "HEAD"]).decode().strip() == "449da6d3112d164287e6a76de66c45344e4cc2a7"
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
