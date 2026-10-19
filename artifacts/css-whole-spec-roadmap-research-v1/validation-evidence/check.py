from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
manifest_path = root / "validation-evidence/MANIFEST.json"
freeze = json.loads((root / "validation-evidence/FREEZE.json").read_text())
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == freeze["manifest_sha256"]
manifest = json.loads(manifest_path.read_text())
assert len(manifest["files"]) == len(set(manifest["files"]))
for name, expected in manifest["files"].items():
    path = root / name
    assert path.resolve().is_relative_to(root)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
print(json.dumps({"status": "PASS", "authenticated_files": len(manifest["files"]), "scope": "Owned research files only; no theorem replay or native/spec completeness claim."}, sort_keys=True))
