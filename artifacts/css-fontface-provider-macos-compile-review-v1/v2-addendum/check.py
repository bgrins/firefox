#!/usr/bin/env python3
import difflib
import hashlib
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((ROOT / "MANIFEST.json").read_text())
for rel, digest in manifest["files"].items():
    assert sha(ROOT / rel) == digest, rel
parent = ROOT.parent
auth = json.loads((ROOT / "AUTHENTICATION.json").read_text())
assert sha(parent / "MANIFEST.json") == auth["original_review_manifest_sha256"]
for rel, digest in json.loads((parent / "MANIFEST.json").read_text())["files"].items():
    assert sha(parent / rel) == digest, rel
patch, formatting = [], []
for name, pin in json.loads((ROOT / "NATIVE-PINS.json").read_text()).items():
    original = (parent / "source" / name).read_text()
    proposal = (parent / "candidate" / name).read_text()
    expected = proposal
    if name == "layout/style/FontFaceImpl.cpp":
        old = "  RefPtr<StyleLockedFontFaceRule> descriptors =\n      Servo_FontFaceRule_Clone(GetData()).Consume();"
        new = "  RefPtr<StyleLockedFontFaceRule> descriptors = GetData();\n  if (previousEntry) {\n    descriptors = Servo_FontFaceRule_Clone(descriptors).Consume();\n  }"
        assert expected.count(old) == 1
        expected = expected.replace(old, new).replace(
            "  // Parse without publishing descriptors until provider preparation succeeds.",
            "  // Prepare existing providers before publishing new descriptors.")
    preformat = (ROOT / "preformat" / name).read_text()
    final = (ROOT / "candidate" / name).read_text()
    assert expected == preformat, name
    assert re.sub(r"\s+", "", preformat) == re.sub(r"\s+", "", final), name
    assert sha(parent / "source" / name) == pin["original"]
    assert sha(ROOT / "candidate" / name) == pin["candidate"]
    patch.extend(difflib.unified_diff(original.splitlines(True), final.splitlines(True), fromfile="a/" + name, tofile="b/" + name))
    formatting.extend(difflib.unified_diff(preformat.splitlines(True), final.splitlines(True), fromfile="preformat/" + name, tofile="candidate/" + name))
assert "".join(patch) == (ROOT / "native.patch").read_text()
assert "".join(formatting) == (ROOT / "format.patch").read_text()
print(json.dumps({"authenticated_addendum_inputs": len(manifest["files"]), "native_files": 16, "exact_adaptation": True, "patches_regenerated": 2, "compiler_run": False, "status": "PASS_SOURCE_ONLY"}, indent=2))
