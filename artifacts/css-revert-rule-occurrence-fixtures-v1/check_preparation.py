from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import tempfile

artifact = Path(__file__).resolve().parent
root = artifact.parent.parent
resource = artifact / "inputs/css/css-cascade/resources"
script = resource / "revert-rule-shared-occurrences.js"
expected = json.loads((artifact / "EXPECTED.json").read_text())
subprocess.run(["node", "--check", str(script)], check=True)
registration = subprocess.run([
    "node", "-e",
    "const fs=require('fs'),vm=require('vm');const names=[];"
    "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),"
    "{promise_test:(_callback,name)=>names.push(name)});"
    "process.stdout.write(JSON.stringify(names));",
    str(script),
], check=True, capture_output=True, text=True)
assert json.loads(registration.stdout) == expected["callbacks"]
assert not re.search(r"cssRules|insertRule|deleteRule|replaceSync", script.read_text())
for stem in ["occurrence-shared", "occurrence-scoped"]:
    texts = [(resource / (name + ".css")).read_text()
             for name in [stem, stem + "-independent-a", stem + "-independent-b"]]
    assert len(set(texts)) == 3
    assert len({text.split("*/", 1)[1] for text in texts}) == 1
    assert "var(--occurrence-value, revert-rule) !important" in texts[0]
    for name in [stem, stem + "-independent-a", stem + "-independent-b"]:
        assert "max-age=3600" in (resource / (name + ".css.headers")).read_text()
source = json.loads((artifact / "diagnostic/SOURCE.json").read_text())
base = (root / source["base_path"]).read_bytes()
assert hashlib.sha256(base).hexdigest() == source["base_sha256"]
native_path = "servo/components/style/properties/cascade.rs"
candidate = (artifact / "diagnostic/candidate" / native_path).read_bytes()
patch = "".join(difflib.unified_diff(
    base.decode().splitlines(keepends=True),
    candidate.decode().splitlines(keepends=True),
    fromfile="a/" + native_path, tofile="b/" + native_path,
))
assert (artifact / "diagnostic/native.patch").read_text() == patch
subprocess.run([
    "rustfmt", "--check", "--config-path", str(root / "servo/rustfmt.toml"),
    str(artifact / "diagnostic/candidate" / native_path),
], check=True)
with tempfile.TemporaryDirectory(prefix="css-occurrence-patch-") as scratch:
    copied = Path(scratch) / native_path
    copied.parent.mkdir(parents=True)
    copied.write_bytes(base)
    for reverse, wanted in [(False, candidate), (True, base)]:
        command = ["patch", "--batch", "-p1", "-i", str(artifact / "diagnostic/native.patch")]
        if reverse:
            command.append("-R")
        subprocess.run(command, cwd=scratch, check=True, capture_output=True)
        assert copied.read_bytes() == wanted
print(json.dumps({
    "status": "PASS",
    "javascript_syntax": True,
    "inert_callback_registration_count": len(expected["callbacks"]),
    "resource_control_bodies_equal_comments_distinct": True,
    "diagnostic_rustfmt": True,
    "patch_forward_reverse_byte_exact": True,
    "temporary_patch_tree_removed": True,
    "browser_callbacks_executed": False,
    "rust_typecheck": False,
    "native_or_browser_execution": False,
}, indent=2))
