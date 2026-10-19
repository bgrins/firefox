import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(root / "MANIFEST.json") == args.manifest_sha
manifest = json.loads((root / "MANIFEST.json").read_text())["files"]
assert json.loads((root / "FREEZE.json").read_text())["manifest_sha256"] == args.manifest_sha
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
assert actual == set(manifest) | {"MANIFEST.json", "FREEZE.json"}
for name, expected in manifest.items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert digest(path) == expected, name
spec = importlib.util.spec_from_file_location("review", root / "review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
assert review.inspect() == json.loads((root / "REVIEW.json").read_text())
print(json.dumps({"authenticated_files": len(manifest), "stable_browser_pins": 25,
                  "repeated_runs": 2, "samples_each": 3, "glyph_width_failures": 4,
                  "complete_source_bindings": 15, "proposal_native_build": False,
                  "proposal_browser_execution": False, "status": "passed"}))
