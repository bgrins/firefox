import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CPP = "layout/generic/StickyScrollContainer.cpp"
TEST = "testing/web-platform/tests/css/css-position/sticky/position-sticky-containing-block-writing-mode.html"
BASES = ["32226ddf3a29d58a52291babebdff2a5a7ce46c6",
         "11482ee213bf63c749b6d205c2c7591d783bdaa8"]
GIT = ["git", "-c", "core.fsmonitor=false"]


def replace(source, old, new):
    assert source.count(old) == 1
    return source.replace(old, new)


def transform(source):
    source = replace(source,
        "  StyleDirection direction = cbFrame->StyleVisibility()->mDirection;",
        "  WritingMode writingMode = cbFrame->GetWritingMode();")
    source = replace(source, "      effectiveOffsets.bottom -= delta;",
        "      effectiveOffsets.Side(writingMode.PhysicalSide(\n"
        "          writingMode.IsVertical() ? LogicalSide::IEnd : LogicalSide::BEnd)) -=\n"
        "          delta;")
    return replace(source,
        "      if (direction == StyleDirection::Ltr) {\n"
        "        effectiveOffsets.right -= delta;\n"
        "      } else {\n"
        "        effectiveOffsets.left -= delta;\n"
        "      }",
        "      effectiveOffsets.Side(writingMode.PhysicalSide(\n"
        "          writingMode.IsVertical() ? LogicalSide::BEnd : LogicalSide::IEnd)) -=\n"
        "          delta;")


assert not (OUT / "standalone-apply-v1.json").exists()
original = subprocess.check_output(GIT + ["show", BASES[0] + ":" + CPP], cwd=ROOT).decode()
auto = (OUT / "StickyScrollContainer-before.cpp").read_text()
combined = (ROOT / CPP).read_text()
assert transform(auto) == combined
writing = transform(original)
variants = {"original": original, "auto-only": auto,
            "writing-only": writing, "combined": combined}
for name, source in variants.items():
    (OUT / ("variant-" + name + ".cpp")).write_text(source)
patch = "".join(difflib.unified_diff(original.splitlines(True), writing.splitlines(True),
                                     fromfile="a/" + CPP, tofile="b/" + CPP))
patch += "".join(difflib.unified_diff([], (ROOT / TEST).read_text().splitlines(True),
                                     fromfile="/dev/null", tofile="b/" + TEST))
(OUT / "fix-candidate-v1.patch").write_text(patch)
checks = []
for revision in BASES:
    source = subprocess.check_output(GIT + ["show", revision + ":" + CPP], cwd=ROOT)
    assert source == original.encode()
    with tempfile.TemporaryDirectory(prefix="sticky-writing-standalone-") as directory:
        temp = Path(directory)
        path = temp / CPP
        path.parent.mkdir(parents=True)
        path.write_bytes(source)
        subprocess.run(GIT + ["apply", "--check", "-"], cwd=temp, input=patch.encode(), check=True)
        subprocess.run(GIT + ["apply", "-"], cwd=temp, input=patch.encode(), check=True)
        assert path.read_text() == writing
        assert (temp / TEST).read_bytes() == (ROOT / TEST).read_bytes()
        subprocess.run(GIT + ["apply", "--reverse", "-"], cwd=temp, input=patch.encode(), check=True)
        assert path.read_bytes() == source and not (temp / TEST).exists()
    checks.append({"revision": revision, "check_exit": 0, "apply_exit": 0,
                   "exact_candidate": True, "reverse_restores_original": True})
record = {"files": [CPP, TEST], "patch_sha256": hashlib.sha256(patch.encode()).hexdigest(),
          "variants_sha256": {n: hashlib.sha256(s.encode()).hexdigest() for n, s in variants.items()},
          "wpt_sha256": hashlib.sha256((ROOT / TEST).read_bytes()).hexdigest(),
          "checks": checks,
          "scope": "Standalone writing-mode fix excludes auto-inset fix; combined source is the exact same transformation of auto-only source. Other worktree repairs remain outside this patch."}
(OUT / "standalone-apply-v1.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
