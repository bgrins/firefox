import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]
CPP = "layout/generic/nsFlexContainerFrame.cpp"
FIX = ROOT / "artifacts/css-flex-line-cross-sum-fix-v1"
PATCH = FIX / "fix-candidate-v1.patch"
PIN = "34a5ec601d2bc24d428160f6cbd5422b584a82cfeea3662fb96e9764135d3798"


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


assert sha(PATCH.read_bytes()) == PIN
head = git("rev-parse", "HEAD").decode().strip()
index = git("diff", "--cached", "--binary")
worktree = git("diff", "--binary")
prefix = json.loads((ROOT / "artifacts/css-sticky-sentinel-commit-v1/PACKAGING.json").read_text())["prefix_recipes"]
prefix += ["css-sticky-sentinel-commit-v1/native.json"]
recipes = [json.loads((ROOT / "artifacts" / n).read_text()) for n in prefix]
for r in recipes:
    assert sha((ROOT / r["patch"]).read_bytes()) == r["patch_sha256"]
baseline = next(r for r in recipes if "cross-baseline" in r["patch"])
changes = json.loads((FIX / "SOURCE-CHANGE.json").read_text())["replacements"]
records = []
for base in [head, "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    with tempfile.TemporaryDirectory(prefix="css-line-sum-package-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("read-tree", base, env=env)
        original = git("write-tree", env=env)
        for r in recipes:
            git("apply", "--cached", str(ROOT / r["patch"]), env=env)
        parent = git("write-tree", env=env).decode().strip()
        expected = git("show", ":" + CPP, env=env).decode()
        for before, after in changes:
            assert expected.count(before) == 1
            expected = expected.replace(before, after)
        git("apply", "--cached", "--check", str(PATCH), env=env)
        git("apply", "--cached", str(PATCH), env=env)
        paths = git("diff", "--cached", "--name-only", parent, env=env).decode().splitlines()
        assert len(paths) == 2 and CPP in paths
        wpt = next(p for p in paths if p != CPP)
        assert git("show", ":" + wpt, env=env) == (ROOT / wpt).read_bytes()
        assert git("show", ":" + CPP, env=env).decode() == expected
        git("diff", "--cached", "--check", parent, env=env)
        combined_tree = git("write-tree", env=env)
        git("apply", "--cached", "--reverse", str(ROOT / baseline["patch"]), env=env)
        assert git("show", ":" + CPP, env=env) == (FIX / ("standalone-" + base[:12] + ".cpp")).read_bytes()
        git("apply", "--cached", str(ROOT / baseline["patch"]), env=env)
        assert git("write-tree", env=env) == combined_tree
        git("apply", "--cached", "--reverse", str(PATCH), env=env)
        assert git("write-tree", env=env).decode().strip() == parent
        for r in reversed(recipes):
            git("apply", "--cached", "--reverse", str(ROOT / r["patch"]), env=env)
        assert git("write-tree", env=env) == original
        records.append({"base": base, "native_paths": paths, "patch_sha256": PIN,
                        "combined_cpp_sha256": sha(expected.encode()), "exact_two_replacements": True,
                        "baseline_patch_commutes": True, "standalone_matches_frozen": True,
                        "live_wpt_bytes_match": True, "exact_apply_reverse": True})
assert git("rev-parse", "HEAD").decode().strip() == head
assert git("diff", "--cached", "--binary") == index
assert git("diff", "--binary") == worktree
result = {"head": head, "head_index_worktree_preserved": True, "prefix_recipes": prefix,
          "bases": records, "isolated_upstream_runtime": "NOT_RUN"}
(HERE / "PACKAGING.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
