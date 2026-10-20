import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


head = git("rev-parse", "HEAD").decode().strip()
staged = git("diff", "--cached", "--binary")
inputs = json.loads((HERE / "STACK-INPUTS.json").read_text())
records = []
with tempfile.TemporaryDirectory(prefix="css-scroll-baseline-stack-") as temp:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / "index"))
    git("read-tree", inputs["base"], env=env)
    for item in inputs["native_patches"]:
        patch = ROOT / item["patch"]
        assert sha(patch.read_bytes()) == item["patch_sha256"]
        before = git("write-tree", env=env).decode().strip()
        git("apply", "--cached", "--check", str(patch), env=env)
        git("apply", "--cached", str(patch), env=env)
        after = git("write-tree", env=env).decode().strip()
        paths = git("diff", "--cached", "--name-only", before, env=env).decode().splitlines()
        assert sorted(paths) == sorted(item["files"])
        git("diff", "--cached", "--check", before, env=env)
        git("apply", "--cached", "--reverse", str(patch), env=env)
        assert git("write-tree", env=env).decode().strip() == before
        git("apply", "--cached", str(patch), env=env)
        assert git("write-tree", env=env).decode().strip() == after
        records.append({"recipe": item["recipe"], "patch_sha256": item["patch_sha256"],
                        "before_tree": before, "after_tree": after,
                        "paths": paths, "inverse_restores_tree": True})
assert len(records) == 10
assert git("rev-parse", "HEAD").decode().strip() == head
assert git("diff", "--cached", "--binary") == staged
result = {"status": "PASS", "head": head, "base": inputs["base"], "staged_diff_sha256": sha(staged),
          "real_head_and_staging_unchanged": True, "native_patches": records,
          "scope": "Ordered source application and exact deltas; no isolated build or runtime."}
(HERE / "STACK-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": "PASS", "native_patches": len(records), "head": head}))
