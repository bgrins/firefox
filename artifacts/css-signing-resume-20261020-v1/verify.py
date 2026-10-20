import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


plan = json.loads((HERE / "PLAN.json").read_text())
receipts = json.loads((HERE / "RECEIPTS.json").read_text())
assert len(receipts) == len(plan["items"]) == 48
head = git("rev-parse", "HEAD").decode().strip()
assert head == receipts[-1]["after"]
assert not git("diff", "--cached", "--name-only").strip()
checks = []
for item, receipt in zip(plan["items"], receipts):
    commit, parent = receipt["after"], receipt["before"]
    assert item["id"] == receipt["id"]
    assert git("rev-parse", commit + "^").decode().strip() == parent
    raw = git("cat-file", "commit", commit)
    assert b"\ngpgsig " in raw.split(b"\n\n", 1)[0]
    paths = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()
    assert sorted(paths) == sorted(item["files"]), item["id"]
    if "patch" in item:
        assert all(not p.startswith("artifacts/") for p in paths)
        assert any(p.startswith("testing/web-platform/tests/") for p in paths)
        patch = ROOT / item["patch"]
        assert hashlib.sha256(patch.read_bytes()).hexdigest() == item["patch_sha256"]
        with tempfile.TemporaryDirectory(prefix="css-signed-delta-") as temp:
            env = {**os.environ, "GIT_INDEX_FILE": str(Path(temp) / "index")}
            git("read-tree", parent, env=env)
            git("apply", "--cached", str(patch), env=env)
            assert git("write-tree", env=env).strip() == git("rev-parse", commit + "^{tree}").strip()
            git("apply", "--cached", "--reverse", str(patch), env=env)
            assert git("write-tree", env=env).strip() == git("rev-parse", parent + "^{tree}").strip()
        git("diff", "--check", parent, commit)
    else:
        assert all(p.startswith("artifacts/") for p in paths)
    checks.append({"id": item["id"], "commit": commit, "parent": parent, "signature_present": True, "paths": paths, "native": "patch" in item})
assert git("rev-parse", "HEAD").decode().strip() == head
assert not git("diff", "--cached", "--name-only").strip()
record = {"base": receipts[0]["before"], "head": head, "signed_commits": 48, "native_fixes": sum(c["native"] for c in checks), "exact_native_parent_deltas": True, "index_empty": True, "checks": checks}
(HERE / "ROOT-COMMIT-CHECK.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({k: v for k, v in record.items() if k != "checks"}, indent=2))
