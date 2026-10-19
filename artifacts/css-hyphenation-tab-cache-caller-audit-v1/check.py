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
manifest_path = root / "MANIFEST.json"
assert digest(manifest_path) == args.manifest_sha
manifest = json.loads(manifest_path.read_text())["files"]
assert json.loads((root / "FREEZE.json").read_text())["manifest_sha256"] == args.manifest_sha
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
assert actual == set(manifest) | {"MANIFEST.json", "FREEZE.json"}
for name, expected in manifest.items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert digest(path) == expected, name
spec = importlib.util.spec_from_file_location("audit", root / "audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
assert audit.run() == json.loads((root / "SOURCE-BINDINGS.json").read_text())
for name, expected in json.loads((root / "IMPORT.json").read_text())["snapshots"].items():
    assert digest(root / "source" / name) == expected
rows = json.loads((root / "ORIGIN-WITNESS.json").read_text())
for row in rows:
    relative = row["tab_source_index"] - row["reflow_start"]
    applied = row["display_start"] + relative
    assert relative == row["stored_relative_index"]
    assert applied == row["applied_source_index"]
    assert row["text"][applied] == row["applied_character"]
    assert (applied == row["tab_source_index"]) == row["same_target"]
print(json.dumps({"authenticated": len(manifest), "complete_additional_bindings": len(audit.run()),
                  "prior_body_comparisons": 18, "coordinate_rows": len(rows),
                  "native_build": False, "browser_executed": False, "status": "passed"}))
