#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parent
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
manifest = json.loads((root / "FILES.json").read_text())
all_paths = list(root.rglob("*"))
assert not any(p.is_symlink() for p in all_paths), "symlink in capsule"
actual = sorted(str(p.relative_to(root)) for p in all_paths if p.is_file() and str(p.relative_to(root)) not in {"FILES.json", "FREEZE.json"})
assert actual == sorted(manifest), "closed roster mismatch"
for name, expected in manifest.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
freeze = json.loads((root / "FREEZE.json").read_text())
assert freeze["files_sha256"] == hashlib.sha256((root / "FILES.json").read_bytes()).hexdigest()
assert freeze["payload_count"] == len(manifest)
subprocess.run([sys.executable, "-I", "-S", "-B", str(root / "analyze.py"), "--check"], check=True)
print(json.dumps({"verified_payloads": len(manifest), "files_sha256": freeze["files_sha256"]}))
