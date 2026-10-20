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
WPT = "testing/web-platform/tests/css/css-position/sticky/position-sticky-auto-insets-large-coordinate.html"
PATCH = ROOT / "artifacts/css-sticky-sentinel-fix-v1/fix-candidate-v1.patch"
PATCH_SHA = "618df0d65352c15d9e5c75b1c86ac7ede7ee3c113932ceaf788066c95b9bccec"
GIT = ["git", "-c", "core.fsmonitor=false"]
RECIPES = [
    "css-view-transition-type-invalidation-commit-v1/native.json",
    "css-sticky-offset-alias-commit-v1/native.json",
    "css-sticky-insets-commit-v1/auto-native.json",
    "css-sticky-insets-commit-v1/writing-native.json",
    "css-sticky-negative-inset-overflow-commit-v1/native.json",
    "css-flex-cross-baseline-overflow-commit-v1/native.json",
]


def git(*args, env=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def transform(source):
    anchor = "  nsPoint position = aFrame->GetNormalPosition();\n"
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor +
        "  const nsMargin* computedOffsets =\n"
        "      aFrame->GetProperty(nsIFrame::ComputedOffsetProperty());\n"
        "  if (!computedOffsets) {\n"
        "    return position;\n"
        "  }\n")
    for axis, side, expression in [
        ("y", "top", "std::max(position.y, std::min(stick.Y(), contain.YMost()))"),
        ("y", "bottom", "std::min(position.y, std::max(stick.YMost(), contain.y))"),
        ("x", "left", "std::max(position.x, std::min(stick.X(), contain.XMost()))"),
        ("x", "right", "std::min(position.x, std::max(stick.XMost(), contain.x))"),
    ]:
        statement = f"  position.{axis} = {expression};\n"
        if statement not in source:
            statement = statement.replace("stick.Y()", "stick.y").replace("stick.X()", "stick.x")
        assert source.count(statement) == 1
        source = source.replace(statement, f"  if (computedOffsets->{side} != NS_AUTOOFFSET) {{\n" +
                                "  " + statement + "  }\n")
    return source


assert sha(PATCH.read_bytes()) == PATCH_SHA
head = git("rev-parse", "HEAD").decode().strip()
index = git("diff", "--cached", "--binary")
worktree = git("diff", "--binary")
recipes = [json.loads((ROOT / "artifacts" / n).read_text()) for n in RECIPES]
for r in recipes:
    assert sha((ROOT / r["patch"]).read_bytes()) == r["patch_sha256"]
records = []
for base in [head, "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    with tempfile.TemporaryDirectory(prefix="css-sentinel-package-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git("read-tree", base, env=env)
        original_tree = git("write-tree", env=env)
        before = git("show", ":" + CPP, env=env).decode()
        git("apply", "--cached", "--check", str(PATCH), env=env)
        git("apply", "--cached", str(PATCH), env=env)
        standalone = git("show", ":" + CPP, env=env).decode()
        assert standalone == transform(before)
        assert git("show", ":" + WPT, env=env) == (ROOT / WPT).read_bytes()
        git("apply", "--cached", "--reverse", str(PATCH), env=env)
        assert git("write-tree", env=env) == original_tree
        for r in recipes:
            git("apply", "--cached", str(ROOT / r["patch"]), env=env)
        parent_tree = git("write-tree", env=env)
        parent = git("show", ":" + CPP, env=env).decode()
        combined = transform(parent)
        assert combined.encode() == (ROOT / CPP).read_bytes()
        patch = "".join(difflib.unified_diff(parent.splitlines(True), combined.splitlines(True),
                                           fromfile="a/" + CPP, tofile="b/" + CPP))
        patch += "--- /dev/null" + PATCH.read_text().split("--- /dev/null", 1)[1]
        target = HERE / ("sentinel-after-negative-" + base[:12] + ".patch")
        target.write_text(patch)
        git("apply", "--cached", "--check", str(target), env=env)
        git("apply", "--cached", str(target), env=env)
        assert git("show", ":" + CPP, env=env) == combined.encode()
        assert git("show", ":" + WPT, env=env) == (ROOT / WPT).read_bytes()
        paths = git("diff", "--cached", "--name-only", parent_tree.decode().strip(), env=env).decode().splitlines()
        assert paths == [CPP, WPT]
        git("diff", "--cached", "--check", parent_tree.decode().strip(), env=env)
        git("apply", "--cached", "--reverse", str(target), env=env)
        assert git("write-tree", env=env) == parent_tree
        for r in reversed(recipes):
            git("apply", "--cached", "--reverse", str(ROOT / r["patch"]), env=env)
        assert git("write-tree", env=env) == original_tree
        records.append({"base": base, "standalone_patch_sha256": PATCH_SHA,
                        "integration_patch": str(target.relative_to(ROOT)),
                        "integration_sha256": sha(target.read_bytes()), "native_paths": paths,
                        "standalone_cpp_sha256": sha(standalone.encode()),
                        "parent_cpp_sha256": sha(parent.encode()), "combined_cpp_sha256": sha(combined.encode()),
                        "same_guard_transform": True, "combined_matches_live_source": True,
                        "exact_apply_reverse": True})
assert git("rev-parse", "HEAD").decode().strip() == head
assert git("diff", "--cached", "--binary") == index
assert git("diff", "--binary") == worktree
result = {"head": head, "bases": records, "prefix_recipes": RECIPES,
          "head_index_worktree_preserved": True, "isolated_upstream_runtime": "NOT_RUN",
          "integration_difference": "The preceding negative-inset repair stores direct edges; identical guards wrap Y()/X() accessor expressions instead of y/x fields."}
(HERE / "PACKAGING.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
