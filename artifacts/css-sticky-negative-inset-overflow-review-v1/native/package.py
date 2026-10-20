import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]
CPP = "layout/generic/StickyScrollContainer.cpp"
HEADER = "layout/generic/StickyScrollContainer.h"
WPT = "testing/web-platform/tests/css/css-position/sticky/position-sticky-large-negative-insets.html"
REPLACEMENTS = {
    "StickyLimits limits{unbounded, unbounded};":
        "StickyLimits limits{nsRectAbsolute::FromRect(unbounded), unbounded};",
    "nscoord stickyViewHeight = sfSize.height - effectiveOffsets.TopBottom();":
        "const int64_t stickyViewHeight =\n        int64_t(sfSize.height) - effectiveOffsets.top - effectiveOffsets.bottom;",
    "nscoord delta = rect.height - stickyViewHeight;":
        "const int64_t delta = int64_t(rect.height) - stickyViewHeight;",
    "nscoord stickyViewWidth = sfSize.width - effectiveOffsets.LeftRight();":
        "const int64_t stickyViewWidth =\n        int64_t(sfSize.width) - effectiveOffsets.left - effectiveOffsets.right;",
    "nscoord delta = rect.width - stickyViewWidth;":
        "const int64_t delta = int64_t(rect.width) - stickyViewWidth;",
    "std::min(stick.y, contain.YMost())": "std::min(stick.Y(), contain.YMost())",
    "std::min(stick.x, contain.XMost())": "std::min(stick.X(), contain.XMost())",
    "nsRectAbsolute stick = nsRectAbsolute::FromRect(stickRect);":
        "const nsRectAbsolute& stick = stickRect;",
}

def get(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def change(name, source):
    replacements = dict(REPLACEMENTS) if name == CPP else {"nsRect mStick;": "nsRectAbsolute mStick;"}
    if name == CPP and "sfSize.height - computedOffsets->TopBottom()" in source:
        replacements = {before.replace("effectiveOffsets.TopBottom()", "computedOffsets->TopBottom()")
                       .replace("effectiveOffsets.LeftRight()", "computedOffsets->LeftRight()"): 
                       after.replace("effectiveOffsets.top", "computedOffsets->top")
                       .replace("effectiveOffsets.bottom", "computedOffsets->bottom")
                       .replace("effectiveOffsets.left", "computedOffsets->left")
                       .replace("effectiveOffsets.right", "computedOffsets->right")
                       for before, after in replacements.items()}
    for before, after in replacements.items():
        assert source.count(before) == 1, (name, before)
        source = source.replace(before, after)
    return source

head = get("rev-parse", "HEAD").decode().strip()
index = Path(get("rev-parse", "--git-path", "index").decode().strip())
if not index.is_absolute():
    index = ROOT / index
index_pin = sha(index.read_bytes())
live = {name: (ROOT / name).read_bytes() for name in [CPP, HEADER, WPT]}
for name in [CPP, HEADER]:
    before = (HERE / ("before-" + Path(name).name)).read_text()
    assert change(name, before).encode() == live[name], name

patch = ""
for name in [CPP, HEADER]:
    before = get("show", head + ":" + name).decode()
    after = change(name, before)
    patch += "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                         fromfile="a/" + name, tofile="b/" + name))
patch += "".join(difflib.unified_diff([], live[WPT].decode().splitlines(True),
                                     fromfile="/dev/null", tofile="b/" + WPT))
patch_path = HERE / "fix-candidate-v1.patch"
patch_path.write_text(patch)
checks = []
for base in [head, "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    originals = {name: get("show", base + ":" + name) for name in [CPP, HEADER]}
    with tempfile.TemporaryDirectory(prefix="sticky-negative-inset-package-") as directory:
        work = Path(directory)
        for name, data in originals.items():
            file = work / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        for flags in [["--check"], []]:
            subprocess.run(GIT + ["apply", *flags, str(patch_path)], cwd=work, check=True)
        paths = sorted(str(f.relative_to(work)) for f in work.rglob("*") if f.is_file())
        assert paths == sorted([CPP, HEADER, WPT])
        assert (work / WPT).read_bytes() == live[WPT]
        after = {}
        for name, data in originals.items():
            expected = change(name, data.decode()).encode()
            assert (work / name).read_bytes() == expected
            after[name] = sha(expected)
        subprocess.run(GIT + ["apply", "--reverse", str(patch_path)], cwd=work, check=True)
        for name, data in originals.items():
            assert (work / name).read_bytes() == data
        assert not (work / WPT).exists()
        checks.append({"base": base, "paths": paths, "apply_reverse": True,
                       "before": {name: sha(data) for name, data in originals.items()}, "after": after})
assert get("rev-parse", "HEAD").decode().strip() == head
assert sha(index.read_bytes()) == index_pin
assert all((ROOT / name).read_bytes() == data for name, data in live.items())
result = {"patch_sha256": sha(patch.encode()), "live_pins": {name: sha(data) for name, data in live.items()},
          "checks": checks, "head_index_worktree_preserved": True,
          "scope": "Identical arithmetic/type/accessor replacements only, plus WPT. Pending H1/H2, positional-sentinel and explicit-offset repairs excluded. Source-only upstream application; no isolated upstream runtime claim."}
(HERE / "PACKAGING.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
