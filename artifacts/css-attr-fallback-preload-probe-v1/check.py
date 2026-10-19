#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
raw = (root / "MANIFEST.json").read_bytes()
assert sha(raw) == args.manifest_sha
manifest = json.loads(raw)
for name, digest in manifest["files"].items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert sha(path.read_bytes()) == digest, "input mismatch: " + name
# All artifact data is authenticated before parsing; no artifact code imports.
cases = json.loads((root / "CASES.json").read_text())
assert len(cases) == 19 and len({c["name"] for c in cases}) == 19
assert all(c["status"] == "UNEXECUTED" for c in cases)
html = (root / "attr-fallback-preload.html").read_text()
embedded = json.loads(html.split("const cases = ", 1)[1].split(";\nfor (", 1)[0])
assert embedded == [[c["name"], c["declarations"], c["attributes"], c["expected"]] for c in cases]
assert "static_prediction" not in html and "assert_array_equals" in html
assert cases[1]["expected"] == {"width": "13px"}
assert cases[-1]["expected"] == {"width": "13px"}
for version in ["original", "namespace-candidate"]:
    custom = (root / "source" / version / "custom_properties.rs").read_text()
    cascade = (root / "source" / version / "cascade.rs").read_text()
    preload = cascade.split("pub fn update_attributes_map(", 1)[1].split("/// Computes the map", 1)[0]
    assert "for next in &refs.refs" in preload and "fallback" not in preload
    assert "let mut references = References::default();" in custom
    assert "primary_valid = !v.has_references();" in cascade
    assert "if !refs.flags.intersects(ReferenceFlags::VAR)" in cascade
spec = (root / "spec-snapshot.html").read_text()
for anchor in ["attr-notation", "attr-substitution", "typedef-attr-name"]:
    assert 'id="' + anchor + '"' in spec
assert sha((root / "spec-snapshot.html").read_bytes()) == json.loads((root / "spec-snapshot-fetch.json").read_text())["sha256"]
print(json.dumps({"status": "PASS", "authenticated_files": len(manifest["files"]), "cases": len(cases), "browser_status": "UNEXECUTED", "scope": "integrity, fixture identity and structural source observations only"}, indent=2))
