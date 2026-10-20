#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
root = Path(__file__).resolve().parent
manifest = json.loads((root / "FILES.json").read_text())
actual = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name not in {"FILES.json", "FREEZE.json"})
assert actual == sorted(manifest), "closed roster mismatch"
for name, expected in manifest.items():
    path = root / name
    assert not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
freeze = json.loads((root / "FREEZE.json").read_text())
assert freeze["files_sha256"] == hashlib.sha256((root / "FILES.json").read_bytes()).hexdigest()
print(json.dumps({"verified_payloads": len(manifest), "files_sha256": freeze["files_sha256"]}))
