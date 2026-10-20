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
PATCH = ROOT / "artifacts/css-flex-cross-baseline-overflow-fix-v2/fix-candidate-v2.patch"
PATCH_SHA = "a99b449fd999c806036ab0d9955d3ea995bb4255c28f3d05a47c12b4f938c8be"


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


assert sha(PATCH.read_bytes()) == PATCH_SHA
head = git("rev-parse", "HEAD").decode().strip()
index = git("diff", "--cached", "--binary")
worktree = git("diff", "--binary")
negative = json.loads((ROOT / "artifacts/css-sticky-negative-inset-overflow-commit-v1/PACKAGING.json").read_text())
records = []
for upstream in negative["bases"]:
    base = upstream["base"]
    with tempfile.TemporaryDirectory(prefix="css-baseline-sum-package-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("read-tree", base, env=env)
        original = git("write-tree", env=env)
        for name in negative["prefix_recipes"]:
            recipe = json.loads((ROOT / "artifacts" / name).read_text())
            patch = ROOT / recipe["patch"]
            assert sha(patch.read_bytes()) == recipe["patch_sha256"]
            git("apply", "--cached", str(patch), env=env)
        integrated = ROOT / upstream["integration_patch"]
        assert sha(integrated.read_bytes()) == upstream["integration_sha256"]
        git("apply", "--cached", str(integrated), env=env)
        parent = git("write-tree", env=env).decode().strip()
        assert git("show", ":" + CPP, env=env) == git("show", base + ":" + CPP)
        git("apply", "--cached", "--check", str(PATCH), env=env)
        git("apply", "--cached", str(PATCH), env=env)
        paths = git("diff", "--cached", "--name-only", parent, env=env).decode().splitlines()
        assert len(paths) == 2 and CPP in paths
        wpt = next(p for p in paths if p != CPP)
        assert git("show", ":" + wpt, env=env) == (ROOT / wpt).read_bytes()
        source = git("show", ":" + CPP, env=env)
        frozen = ROOT / ("artifacts/css-flex-cross-baseline-overflow-fix-v2/standalone-" + base[:12] + ".cpp")
        assert source == frozen.read_bytes()
        git("diff", "--cached", "--check", parent, env=env)
        git("apply", "--cached", "--reverse", str(PATCH), env=env)
        assert git("write-tree", env=env).decode().strip() == parent
        git("apply", "--cached", "--reverse", str(integrated), env=env)
        for name in reversed(negative["prefix_recipes"]):
            recipe = json.loads((ROOT / "artifacts" / name).read_text())
            git("apply", "--cached", "--reverse", str(ROOT / recipe["patch"]), env=env)
        assert git("write-tree", env=env) == original
        records.append({"base": base, "patch_sha256": PATCH_SHA, "native_paths": paths,
                        "standalone_cpp_sha256": sha(source), "exact_frozen_source": True,
                        "live_wpt_bytes_match": True, "all_round_trips_exact": True})
assert git("rev-parse", "HEAD").decode().strip() == head
assert git("diff", "--cached", "--binary") == index
assert git("diff", "--binary") == worktree
result = {"head": head, "head_index_worktree_preserved": True, "bases": records,
          "source_only": True, "isolated_upstream_build_browser": "NOT_RUN"}
(HERE / "PACKAGING.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
