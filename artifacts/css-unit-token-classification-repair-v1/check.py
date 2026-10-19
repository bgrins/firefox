#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

freeze = json.loads((root / "FREEZE.json").read_text())
assert digest(root / "INPUTS.json") == freeze["inputs_sha256"]
inputs = json.loads((root / "INPUTS.json").read_text())
assert len(inputs) == freeze["entries"]
for name, expected in inputs.items():
    assert digest(root / name) == expected, name
base = json.loads((root / "BASE.json").read_text())
original = (root / "original/custom_properties.rs").read_bytes()
candidate = (root / "candidate/custom_properties.rs").read_bytes()
assert digest(root / "original/custom_properties.rs") == base["original_sha256"]
assert digest(root / "candidate/custom_properties.rs") == base["candidate_sha256"]
needle = b"                references.flags.insert(ReferenceFlags::from_unit(value));"
replacement = b"                if matches!(token, Token::Dimension { .. }) {\n                    references.flags.insert(ReferenceFlags::from_unit(value));\n                }"
assert original.count(needle) == 1
assert candidate == original.replace(needle, replacement)
assert (root / "fix.patch").read_bytes() == (root / "native.patch").read_bytes() + (root / "wpt.patch").read_bytes()
assert digest(root / "evidence/INPUTS.json") == json.loads((root / "evidence/FREEZE.json").read_text())["inputs_sha256"]
history = json.loads((root / "evidence/INPUTS.json").read_text())
for name, sha in history.items():
    if (root / "evidence" / name).is_file():
        assert digest(root / "evidence" / name) == sha, name
for item in json.loads((root / "evidence/spec/FETCH.json").read_text()):
    assert item["status"] == 200
    assert digest(root / "evidence/spec" / (item["name"] + ".html")) == item["sha256"]
cases = json.loads((root / "CASES.json").read_text())
prior = json.loads((root / "evidence/CASES.json").read_text())
assert cases == [{k: v for k, v in row.items() if k != "predicted_native"} for row in prior]
assert len(cases) == 14 and len({row["name"] for row in cases}) == 14
assert sum(row["expected"] != row["predicted_native"] for row in prior) == 7
wpt_name = "registered-property-unit-token-dependencies.html"
html = (root / wpt_name).read_text()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
assert len(scripts) == 1
assert json.loads(re.search(r"const cases = (.*?);\n", scripts[0], re.S)[1]) == cases
with tempfile.TemporaryDirectory(prefix="unit-token-repair-") as tmp:
    tree = Path(tmp)
    native = tree / base["path"]
    native.parent.mkdir(parents=True)
    native.write_bytes(original)
    wpt = tree / (root / "WPT-PATH.txt").read_text().strip()
    wpt.parent.mkdir(parents=True)
    patch = ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(root / "fix.patch")]
    subprocess.run(patch, cwd=tree, check=True, capture_output=True)
    assert native.read_bytes() == candidate
    assert wpt.read_bytes() == (root / wpt_name).read_bytes()
    subprocess.run(patch + ["-R"], cwd=tree, check=True, capture_output=True)
    assert native.read_bytes() == original
    assert not wpt.exists()
    script = tree / "test.js"
    script.write_text(scripts[0])
    node = shutil.which("node") or "/opt/homebrew/bin/node"
    subprocess.run([node, "--check", str(script)], check=True, capture_output=True)
print(json.dumps({"status": "PASS", "entries": len(inputs), "wpt_cases": 14,
                  "predicted_baseline_failures": 7, "exact_apply_reverse": "PASS",
                  "javascript_syntax": "PASS", "native_compilation": "NOT RUN",
                  "browser_execution": "NOT RUN", "optional_parser_fixture": "NOT COMPILED"}, indent=2))
