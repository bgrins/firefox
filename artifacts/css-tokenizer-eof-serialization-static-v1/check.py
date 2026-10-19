#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
freeze = json.loads((root / "FREEZE.json").read_text())
assert hashlib.sha256((root / "MANIFEST.json").read_bytes()).hexdigest() == freeze["manifest_sha256"]
manifest = json.loads((root / "MANIFEST.json").read_text())
for name, digest in manifest.items():
    path = root / name
    assert not path.is_symlink() and path.is_file(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
pins = json.loads((root / "SOURCE-PINS.json").read_text())
for item in pins["files"]:
    assert manifest["source/" + item["path"]] == item["sha256"]
rows = json.loads((root / "evidence/root-browser-result.json").read_text())["rows"]
eof = [r for r in rows if r.get("test") == "/css/css-syntax/escaped-eof.html" and r["action"] == "test_status"]
assert len(eof) == 5 and sum(r["status"] == "FAIL" for r in eof) == 3
src = (root / "source/servo/components/style/custom_properties.rs").read_text()
assert "Serialize as escaped U+FFFD" in src
assert "reference.end = input.position().byte_index() - input_start.byte_index()" in src
assert "dest.write_str(&self.css)" in src
print(json.dumps({"authenticated_files": len(manifest), "source_files": len(pins["files"]), "root_eof_failures": 3, "scope": "static evidence integrity; no browser, compiler, or formal proof replay"}))
