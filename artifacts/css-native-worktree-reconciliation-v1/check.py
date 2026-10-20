import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S without optimization")
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
files = json.loads((root / "FILES.json").read_text())
actual = set()
for path in root.rglob("*"):
    if path.is_symlink():
        raise SystemExit("symlink rejected")
    if path.is_file():
        rel = str(path.relative_to(root))
        if rel not in {"FILES.json", "FREEZE.json"}:
            actual.add(rel)
if actual != set(files):
    raise SystemExit("roster differs")
for rel, digest in files.items():
    if hashlib.sha256((root / rel).read_bytes()).hexdigest() != digest:
        raise SystemExit("hash differs: " + rel)
freeze = json.loads((root / "FREEZE.json").read_text())
if freeze["files_sha256"] != hashlib.sha256((root / "FILES.json").read_bytes()).hexdigest():
    raise SystemExit("manifest differs")
pins = json.loads((root / "SOURCE-PINS.json").read_text())
if len(pins) != 21:
    raise SystemExit("native roster differs")
for row in pins:
    for kind in ("head", "worktree"):
        data = (root / "source" / kind / row["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != row[kind + "_sha256"]:
            raise SystemExit("snapshot differs")
for source, digest in json.loads((root / "INPUTS.json").read_text()).items():
    if hashlib.sha256((root / "inputs" / source).read_bytes()).hexdigest() != digest:
        raise SystemExit("input differs")
checks = [
    ("layout/generic/StickyScrollContainer.cpp", "artifacts/css-sticky-writing-mode-fix-v1/variant-combined.cpp"),
    ("dom/base/nsLineBreaker.cpp", "artifacts/css-nowrap-partitions-fix-v1/nsLineBreaker-candidate.cpp"),
]
for source, reference in checks:
    if (root / "source/worktree" / source).read_bytes() != (root / "inputs" / reference).read_bytes():
        raise SystemExit("combined snapshot differs")
numeric = "servo/components/style/properties_and_values/syntax/data_type.rs"
receipt = json.loads((root / "inputs/artifacts/css-registered-numeric-fix-v1/patched-inputs-v1.json").read_text())
if hashlib.sha256((root / "source/worktree" / numeric).read_bytes()).hexdigest() != receipt["sha256"][numeric]:
    raise SystemExit("numeric snapshot differs")
result = json.loads((root / "PATCH-CORRESPONDENCE.json").read_text())
hunks = [h for row in result["reversals"] for h in row["hunks"]]
if len(hunks) != 91 or sum(h["reverse"] == "exact" for h in hunks) != 82 or len(result["residual_paths"]) != 4:
    raise SystemExit("correspondence inventory differs")
print("PASS: closed audit inventory, 21 source pairs, historical combined candidates, 82/91 exact contexts; nine exceptions retained")
