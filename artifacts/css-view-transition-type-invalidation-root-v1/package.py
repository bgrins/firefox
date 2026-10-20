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
PATCH = ROOT / "artifacts/css-view-transition-type-invalidation-root-v1/fix-candidate-v2.patch"
PINS = {'dom/view-transitions/ViewTransition.cpp': '93725f16af96dd6bf73e4e9dd27cfbe18b690059b486d6e1086fa234bef39ccf', 'dom/view-transitions/ViewTransition.h': 'ae1648ef541465399e4e52fa189e957994c63c7559a608a77e85c40ef9a74d67', 'dom/view-transitions/ViewTransitionTypeSet.cpp': '4ac46ca2f54b2ad77b716a11b43467f59b19d1d880f0d2948a4355bdaf1a3edf', 'testing/web-platform/tests/css/css-view-transitions/view-transition-types-style-invalidation.html': '41cded591e60ca2ffb7db363fa10de520157757b29eac870463adc723f6025c3'}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)

def sha(data):
    return hashlib.sha256(data).hexdigest()

patch_hash = sha(PATCH.read_bytes())
require(patch_hash == "a17790522e9e2c39aab2b235e5f96720ca286b2442e0fbbedc7912f7097984a7", "Patch identity")
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
        require(sorted(paths) == sorted(PINS), "Exact four-file roster")
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
