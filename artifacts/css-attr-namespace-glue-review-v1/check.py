#!/usr/bin/env python3
import argparse
import difflib
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
assert sha(raw) == args.manifest_sha
manifest = json.loads(raw)
for name, digest in manifest["files"].items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert sha(path.read_bytes()) == digest, "input mismatch: " + name
for name in ["custom_properties.rs", "properties__cascade.rs", "glue.rs"]:
    a = Path("original" if name == "glue.rs" else "candidate-v2") / name
    b = Path("candidate-v3") / name
    delta = "".join(difflib.unified_diff((root/a).read_text().splitlines(True), (root/b).read_text().splitlines(True), fromfile=str(a), tofile=str(b)))
    assert delta == (root / (name + ".diff")).read_text()
assert (root / "candidate-v2/properties__cascade.rs").read_bytes() == (root / "candidate-v3/properties__cascade.rs").read_bytes()
c = (root / "candidate-v3/custom_properties.rs").read_text()
normalized = c.replace("    /// Store a computed attribute value by its expanded name.\n", "").replace("    /// The resolved namespace, including the null namespace.\n", "").replace("pub fn insert_attr(", "pub(crate) fn insert_attr(").replace("pub fn namespace(&self)", "pub(crate) fn namespace(&self)")
assert normalized == (root / "candidate-v2/custom_properties.rs").read_text()
glue = (root / "candidate-v3/glue.rs").read_text()
old = (root / "original/glue.rs").read_text()
start = "    // Build the attributes Map that ComputedSubstitutionFunctions needs"
end = "    let Ok(result) = custom_properties::substitute("
assert glue.split(start)[0] == old.split(start)[0]
assert glue.split(end)[1] == old.split(end)[1]
body = glue.split(start)[1].split(end)[0]
assert body.index("reference.attribute_data.namespace()") < body.index("get_attr_value_for_cycle_resolution(") < body.index("insert_attr(&reference.name, namespace, value)")
assert "Some(style.custom_properties().clone()),\n        None," in body
files = {
 "candidate-v3/properties__cascade.rs":2,
 "supplement/servo/components/style/properties/properties.mako.rs":1,
 "supplement/servo/components/style/queries/condition.rs":2,
 "supplement/servo/components/style/queries/feature_expression.rs":1,
 "candidate-v3/glue.rs":1,
}
for f, expected in files.items():
    s = (root/f).read_text(); calls = s.split("ComputedSubstitutionFunctions::new(")[1:]
    assert len(calls) == expected, f
    for call in calls:
        depth = 1; i = 0
        while depth:
            ch = call[i]; depth += (ch == "(") - (ch == ")"); i += 1
        text = call[:i-1]
        assert re.search(r",\s*None,?\s*$", text), (f, text)
manifest_text = (root / "supplement/layout/inspector/tests/mochitest.toml").read_text()
for name in ["test_getSubstitutedValue.html", "test_getComputationSteps.html"]:
    assert '["' + name + '"]' in manifest_text
    assert (root / "supplement/layout/inspector/tests" / name).is_file()
test = (root / "supplement/layout/inspector/tests/test_getSubstitutedValue.html").read_text()
assert 'attr(data-x type(<number>))' in test and 'attr(data-y type(<color>))' in test
spec = (root / "spec-snapshot.html").read_bytes()
assert sha(spec) == json.loads((root / "spec-snapshot-fetch.json").read_text())["sha256"]
assert b'id="attr-substitution"' in spec
print(json.dumps({"status":"PASS", "authenticated_files":len(manifest["files"]), "constructors_checked":7, "runtime":"NOT RUN", "scope":"integrity and exact static correspondence only"},indent=2))
