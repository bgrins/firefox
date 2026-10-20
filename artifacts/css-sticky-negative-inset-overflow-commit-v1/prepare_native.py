import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CPP = "layout/generic/StickyScrollContainer.cpp"
HEADER = "layout/generic/StickyScrollContainer.h"
GIT = ["git", "-c", "core.fsmonitor=false"]
PATCH = ROOT / "artifacts/css-sticky-negative-inset-overflow-fix-v1/fix-candidate-v1.patch"
PATCH_SHA = "68c14d1d2b0fdb2fad21efc9e670a6ddcdf40740c1e84230225f7bae57251484"
RECIPES = [
    "css-view-transition-type-invalidation-commit-v1/native.json",
    "css-sticky-offset-alias-commit-v1/native.json",
    "css-sticky-insets-commit-v1/auto-native.json",
    "css-sticky-insets-commit-v1/writing-native.json",
]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def transform(source, normalized):
    offset = "effectiveOffsets." if normalized else "computedOffsets->"
    changes = [
        ("StickyLimits limits{unbounded, unbounded};",
         "StickyLimits limits{nsRectAbsolute::FromRect(unbounded), unbounded};"),
        (f"    nscoord stickyViewHeight = sfSize.height - {offset}TopBottom();",
         "    const int64_t stickyViewHeight =\n"
         f"        int64_t(sfSize.height) - {offset}top - {offset}bottom;"),
        ("      nscoord delta = rect.height - stickyViewHeight;",
         "      const int64_t delta = int64_t(rect.height) - stickyViewHeight;"),
        (f"    nscoord stickyViewWidth = sfSize.width - {offset}LeftRight();",
         "    const int64_t stickyViewWidth =\n"
         f"        int64_t(sfSize.width) - {offset}left - {offset}right;"),
        ("      nscoord delta = rect.width - stickyViewWidth;",
         "      const int64_t delta = int64_t(rect.width) - stickyViewWidth;"),
        ("std::min(stick.y, contain.YMost())", "std::min(stick.Y(), contain.YMost())"),
        ("std::min(stick.x, contain.XMost())", "std::min(stick.X(), contain.XMost())"),
        ("  nsRectAbsolute stick = nsRectAbsolute::FromRect(stickRect);",
         "  const nsRectAbsolute& stick = stickRect;"),
    ]
    for before, after in changes:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


def diff(before, after, path):
    return "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                        fromfile="a/" + path, tofile="b/" + path))


assert sha(PATCH.read_bytes()) == PATCH_SHA
head = git("rev-parse", "HEAD").decode().strip()
real_index = git("diff", "--cached", "--binary")
real_worktree = git("diff", "--binary")
recipes = [json.loads((ROOT / "artifacts" / name).read_text()) for name in RECIPES]
for recipe in recipes:
    assert sha((ROOT / recipe["patch"]).read_bytes()) == recipe["patch_sha256"]
records = []
for base in [head, "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    with tempfile.TemporaryDirectory(prefix="css-negative-package-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("read-tree", base, env=env)
        original_tree = git("write-tree", env=env)
        before = git("show", ":" + CPP, env=env).decode()
        before_h = git("show", ":" + HEADER, env=env).decode()
        git("apply", "--cached", "--check", str(PATCH), env=env)
        git("apply", "--cached", str(PATCH), env=env)
        alone = git("show", ":" + CPP, env=env).decode()
        alone_h = git("show", ":" + HEADER, env=env).decode()
        assert transform(before, False) == alone
        assert before_h.count("    nsRect mStick;") == 1
        assert before_h.replace("    nsRect mStick;", "    nsRectAbsolute mStick;") == alone_h
        paths = git("diff", "--cached", "--name-only", base, env=env).decode().splitlines()
        assert len(paths) == 3 and CPP in paths and HEADER in paths
        wpt = next(p for p in paths if p not in [CPP, HEADER])
        assert git("show", ":" + wpt, env=env) == (ROOT / wpt).read_bytes()
        git("apply", "--cached", "--reverse", str(PATCH), env=env)
        assert git("write-tree", env=env) == original_tree
        for recipe in recipes:
            git("apply", "--cached", str(ROOT / recipe["patch"]), env=env)
        parent_tree = git("write-tree", env=env).decode().strip()
        parent = git("show", ":" + CPP, env=env).decode()
        parent_h = git("show", ":" + HEADER, env=env).decode()
        assert parent_h == before_h
        combined = transform(parent, True)
        integrated = diff(parent, combined, CPP) + diff(parent_h, alone_h, HEADER)
        integrated += "--- /dev/null" + PATCH.read_text().split("--- /dev/null", 1)[1]
        target = HERE / ("negative-after-insets-" + base[:12] + ".patch")
        target.write_text(integrated)
        git("apply", "--cached", "--check", str(target), env=env)
        git("apply", "--cached", str(target), env=env)
        assert git("show", ":" + CPP, env=env).decode() == combined
        assert git("show", ":" + HEADER, env=env).decode() == alone_h
        assert git("show", ":" + wpt, env=env) == (ROOT / wpt).read_bytes()
        assert git("diff", "--cached", "--name-only", parent_tree, env=env).decode().splitlines() == paths
        git("diff", "--cached", "--check", parent_tree, env=env)
        (HERE / ("combined-" + base[:12] + ".cpp")).write_text(combined)
        git("apply", "--cached", "--reverse", str(target), env=env)
        assert git("write-tree", env=env).decode().strip() == parent_tree
        for recipe in reversed(recipes):
            git("apply", "--cached", "--reverse", str(ROOT / recipe["patch"]), env=env)
        assert git("write-tree", env=env) == original_tree
        records.append({"base": base, "standalone_patch_sha256": PATCH_SHA,
                        "integration_patch": str(target.relative_to(ROOT)),
                        "integration_sha256": sha(target.read_bytes()),
                        "native_paths": paths, "original_cpp": sha(before.encode()),
                        "standalone_cpp": sha(alone.encode()), "parent_cpp": sha(parent.encode()),
                        "combined_cpp": sha(combined.encode()),
                        "exact_transform_standalone": True, "live_wpt_bytes_match": True,
                        "all_round_trips_exact": True})
assert git("rev-parse", "HEAD").decode().strip() == head
assert git("diff", "--cached", "--binary") == real_index
assert git("diff", "--binary") == real_worktree
record = {"head": head, "head_index_worktree_preserved": True, "bases": records,
          "prefix_recipes": RECIPES, "source_only": True,
          "integration_difference": "Widen the already normalized effectiveOffsets components after the auto-inset fix. Retain the preceding logical-end selection.",
          "isolated_upstream_build_browser": "NOT_RUN"}
(HERE / "PACKAGING.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
