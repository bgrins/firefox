#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
raw = (root / "MANIFEST.json").read_bytes()
assert sha(raw) == args.manifest_sha, "manifest identity"
manifest = json.loads(raw)
for name, digest in manifest["files"].items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert sha(path.read_bytes()) == digest, "input mismatch: " + name
pins = json.loads((root / "PINS.json").read_text())
for version in ["original", "candidate"]:
    for name, digest in pins[version].items():
        assert sha((root / version / name).read_bytes()) == digest
assert (root / "original/custom_properties.rs").read_bytes() == (root / "candidate/custom_properties.rs").read_bytes()
patch = (root / "recursive-preload.patch").read_text().splitlines(keepends=True)
assert sha((root / "recursive-preload.patch").read_bytes()) == pins["patch_sha256"]
assert patch[:2] == ["--- a/servo/components/style/properties/cascade.rs\n", "+++ b/servo/components/style/properties/cascade.rs\n"]
source = (root / "original/cascade.rs").read_text().splitlines(keepends=True)
result = []
cursor = 0
i = 2
while i < len(patch):
    m = re.fullmatch(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@\n", patch[i])
    assert m, patch[i]
    start, old_count, new_start, new_count = map(int, m.groups())
    result.extend(source[cursor:start-1]); cursor = start-1
    assert len(result) == new_start-1
    i += 1
    old = new = 0
    while i < len(patch) and not patch[i].startswith("@@"):
        line = patch[i]; prefix = line[0]; body = line[1:]
        assert prefix in " +-"
        if prefix != "+":
            assert source[cursor] == body
            cursor += 1; old += 1
        if prefix != "-":
            result.append(body); new += 1
        i += 1
    assert (old, new) == (old_count, new_count)
result.extend(source[cursor:])
assert "".join(result) == (root / "candidate/cascade.rs").read_text()
candidate = (root / "candidate/cascade.rs").read_text()
body = candidate.split("pub fn update_attributes_map(", 1)[1].split("/// Computes the map", 1)[0]
assert body.index("refs_stack.push(&fallback.references)") < body.index("if !next.is_attr_with_type()") < body.index("next.attribute_data.namespace()")
assert "primary_valid = !v.has_references();" in candidate
assert candidate.index("for (var, has_refs) in &seen.var") < candidate.index("for (namespace, attributes) in &seen.attr")
cases = json.loads((root / "CASES.json").read_text())
assert len(cases) == 6 and all(c["status"] == "UNEXECUTED" for c in cases)
html = (root / "attr-fallback-readiness.html").read_text()
embedded = json.loads(html.split("const cases = ", 1)[1].split(";\nfor (", 1)[0])
assert embedded == [[c[k] for k in ["name", "declarations", "attributes", "expected"]] for c in cases]
assert cases[1]["attributes"]["chain"] == "var(--v)"
assert cases[2]["attributes"]["chain"] == "13px"
assert cases[1]["expected"] == cases[2]["expected"] == {"width":"13px", "height":"13px"}
assert "static_predictions" not in html
spec = (root / "spec-snapshot.html").read_text()
assert 'id="attr-substitution"' in spec
assert sha((root / "spec-snapshot.html").read_bytes()) == json.loads((root / "spec-snapshot-fetch.json").read_text())["sha256"]
print(json.dumps({"status":"PASS", "authenticated_files":len(manifest["files"]), "cases":6, "native_status":"UNCOMPILED", "browser_status":"UNEXECUTED", "scope":"integrity, exact patch, source observations and fixture identity only"}, indent=2))
