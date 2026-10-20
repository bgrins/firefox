import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("use python3 -I -S without optimization")
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

repo = Path(__file__).resolve().parents[2]
root = Path(__file__).resolve().parent
source = "servo/components/style/custom_properties.rs"

def git(*args, env=None, data=None):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args],
                                   cwd=repo, env=env, input=data)

def sha(data):
    return hashlib.sha256(data).hexdigest()

config = json.loads((root / "CANDIDATE.json").read_text())
run = json.loads((root / "FINAL-WPT.json").read_text())
head = git("rev-parse", "HEAD").decode().strip()
index = git("write-tree")
original = git("show", head + ":" + source)
candidate = (root / "candidate.rs").read_bytes()
if sha(original) != sha((root / "before.rs").read_bytes()) or sha(candidate) != config["source_sha256"]:
    raise RuntimeError("source identity mismatch")
tests = sorted({row["test"] for row in run["rows"]})
if len(tests) != 1:
    raise RuntimeError("unexpected WPT roster")
test = "testing/web-platform/tests" + tests[0]
test_bytes = (repo / test).read_bytes()
if not run["complete"] or run["after"][test] != sha(test_bytes):
    raise RuntimeError("passing WPT identity mismatch")
with tempfile.TemporaryDirectory(prefix="css-whitespace-integration-", dir="/private/tmp") as tmp:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
    git("read-tree", head, env=env)
    for name, data in [(source, candidate), (test, test_bytes)]:
        blob = git("hash-object", "-w", "--stdin", data=data).decode().strip()
        git("update-index", "--add", "--cacheinfo", "100644," + blob + "," + name, env=env)
    tree = git("write-tree", env=env).decode().strip()
    paths = git("diff", "--name-only", head, tree).decode().splitlines()
    if sorted(paths) != sorted([source, test]):
        raise RuntimeError("unexpected native patch paths")
    patch = git("diff", "--binary", "--full-index", head, tree, "--", source, test)
    path = root / "integration-native-wpt.patch"
    path.write_bytes(patch)
    git("apply", "--cached", "--reverse", str(path), env=env)
    if git("write-tree", env=env) != git("rev-parse", head + "^{tree}"):
        raise RuntimeError("reverse did not restore parent")
    git("apply", "--cached", str(path), env=env)
    if git("write-tree", env=env).decode().strip() != tree:
        raise RuntimeError("forward did not restore candidate")
if git("rev-parse", "HEAD").decode().strip() != head or git("write-tree") != index:
    raise RuntimeError("real HEAD/index changed")
record = {"base": head, "candidate_tree": tree, "paths": paths,
          "patch": str(path.relative_to(repo)), "sha256": sha(patch),
          "candidate_sha256": sha(candidate), "test_sha256": sha(test_bytes),
          "exact_apply_reverse": True, "head_and_index_preserved": True,
          "scope": "Exact previously tested candidate snapshot and WPT; later repairs excluded."}
(root / "INTEGRATION-PACKAGING.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
