import difflib
import hashlib
import json
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
refs = json.loads((P / "REFERENCES.json").read_text())
for name, digest in refs.items():
    assert sha((ROOT / name).read_bytes()) == digest, name
roles = json.loads((P / "SOURCE-ROLES.json").read_text())
comments = json.loads((P / "COMMENTS.json").read_text())
parent_delta = []
native_delta = []
for role, bindings in roles.items():
    texts = {}
    for name, binding in bindings.items():
        data = (ROOT / binding["path"]).read_bytes()
        assert sha(data) == binding["sha256"], (role, name)
        texts[name] = data.decode()
    stripped = texts["candidate"]
    if role.endswith("custom_properties.rs"):
        for comment in comments.values():
            line = "        /// " + comment + "\n"
            assert stripped.count(line) == 1
            stripped = stripped.replace(line, "")
    assert stripped == texts["parent"], role
    parent_delta.extend(difflib.unified_diff(texts["parent"].splitlines(True), texts["candidate"].splitlines(True), fromfile="a/" + role, tofile="b/" + role))
    native_delta.extend(difflib.unified_diff(texts["base"].splitlines(True), texts["candidate"].splitlines(True), fromfile="a/" + role, tofile="b/" + role))
assert "".join(parent_delta) == (P / "PARENT-DELTA.patch").read_text()
assert "".join(native_delta) == (P / "native.patch").read_text()
subprocess.run(["rustfmt", "--check", "--edition", "2024", "--config", "skip_children=true", *[str(ROOT / v["candidate"]["path"]) for v in roles.values()]], check=True)
print(json.dumps({"references": len(refs), "roles": len(roles), "added_doc_comments": len(comments), "stripping_comments_recovers_exact_parent": True, "exact_patches": 2, "format": True, "native_run": False, "extracted_tests_rerun": False}))
