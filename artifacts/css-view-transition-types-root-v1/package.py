import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("Use python3 -I -S without optimization")
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
PATCH = ROOT / "artifacts/css-view-transition-types-fix-v1/fix-candidate-v1.patch"
PINS = {
    "dom/base/Document.cpp": "fee2870b6beabb47c2a67d118c74e914c0840ce0cb88151bb0216b8d84f88576",
    "testing/web-platform/tests/css/css-view-transitions/view-transition-types-initial-duplicates.html":
        "1bf157cf9bf2c879a1c78e8a1ad227f6984fbb7f6e8faebd25c1e9bd89986b3c",
}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)

def sha(data):
    return hashlib.sha256(data).hexdigest()

patch_hash = sha(PATCH.read_bytes())
require(patch_hash == "c9e520ea2d2a991635f9af70531957e01635c1bdbd83e91607898466bc26c345", "Patch identity")
head = git("rev-parse", "HEAD").decode().strip()
index = git("write-tree")
worktree = {p: sha((ROOT / p).read_bytes()) for p in PINS}
require(worktree == PINS, "Accepted live candidate identity")
records = {}
for label, base in [("integration", head), ("standalone", "976279105b2e78b8666a959eb3f25c9176cefaf8")]:
    with tempfile.TemporaryDirectory(prefix="css-transition-package-", dir="/private/tmp") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("read-tree", base, env=env)
        git("apply", "--cached", "--check", str(PATCH), env=env)
        git("apply", "--cached", str(PATCH), env=env)
        paths = git("diff", "--cached", "--name-only", base, env=env).decode().splitlines()
        require(sorted(paths) == sorted(PINS), "Exact two-file roster")
        require({p: sha(git("show", ":" + p, env=env)) for p in paths} == PINS, "Exact accepted source and WPT")
        tree = git("write-tree", env=env).decode().strip()
        git("diff", "--cached", "--check", base, env=env)
        git("apply", "--cached", "--reverse", str(PATCH), env=env)
        require(git("write-tree", env=env) == git("rev-parse", base + "^{tree}"), "Exact reverse")
        records[label] = {"base": base, "candidate_tree": tree, "paths": paths, "pins": PINS,
            "patch": str(PATCH.relative_to(ROOT)), "sha256": patch_hash, "exact_apply_reverse": True}
require(git("rev-parse", "HEAD").decode().strip() == head, "HEAD changed")
require(git("write-tree") == index, "Real index changed")
require({p: sha((ROOT / p).read_bytes()) for p in PINS} == worktree, "Worktree changed")
records["scope"] = "Source-only applicability at both bases; historical paired runtime retained separately. Formal acceptance still pending; no new isolated build or browser claim."
(HERE / "PACKAGING.json").write_text(json.dumps(records, indent=2) + "\n")
print(json.dumps(records, indent=2))
