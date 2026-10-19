from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest_path = root / "MANIFEST.json"
freeze = json.loads((root / "FREEZE.json").read_text())
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == freeze["manifest_sha256"]
manifest = json.loads(manifest_path.read_text())
for name, expected in manifest["files"].items():
    path = root / name
    assert path.resolve().is_relative_to(root)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
assert "2016/WD-cssom-1-20160317" in (root / "REPORT.md").read_text()
assert "2021/WD-cssom-1-20210826" in (root / "REPORT.md").read_text()
print(json.dumps({"status": "PASS", "files": len(manifest["files"]), "claim": "Research integrity only; no proof, native or browser execution."}, sort_keys=True))
