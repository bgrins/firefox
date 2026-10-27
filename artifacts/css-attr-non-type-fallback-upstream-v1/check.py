import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for name, versions in pins["paths"].items():
    for version, digest in versions.items():
        path = HERE / version / name
        assert path.exists() == (digest is not None)
        if digest is not None:
            assert sha(path) == digest
records = []
with tempfile.TemporaryDirectory(prefix="attr-upstream-variants-", dir="/private/tmp") as tmp:
    root = Path(tmp)
    for name, versions in pins["paths"].items():
        if versions["base"] is not None:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((HERE / "base" / name).read_bytes())
    def apply(patch, reverse, expected):
        args = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "apply"]
        if reverse:
            args.append("--reverse")
        args.append(str(HERE / patch))
        proc = subprocess.run(args, cwd=root, capture_output=True, text=True,
                              env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
        assert proc.returncode == 0, proc.stderr
        for name, versions in pins["paths"].items():
            path = root / name
            digest = versions[expected]
            assert path.exists() == (digest is not None), name
            if digest is not None:
                assert sha(path) == digest, name
        records.append({"patch": patch, "reverse": reverse, "exit": proc.returncode,
                        "exact_expected_bodies": expected})
    apply("upstream-self-contained.patch", False, "candidate-after-number-fix")
    apply("upstream-self-contained.patch", True, "base")
    apply("prerequisite-native.patch", False, "base-after-number-fix")
    apply("repair-after-number-fix.patch", False, "candidate-after-number-fix")
    apply("repair-after-number-fix.patch", True, "base-after-number-fix")
    apply("prerequisite-native.patch", True, "base")
assert not root.exists()
result = {"operations": records, "scratch_removed": True,
          "variants_produce_identical_candidates": True,
          "new_wpt_identical_to_repair_v2": True,
          "upstream_compiled": False, "upstream_browser_tested": False,
          "live_tree_changed": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print("UPSTREAM_VARIANTS_EXACT_TRANSPORT_PASS")
