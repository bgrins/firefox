#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parent
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
frozen = json.loads((root / "FREEZE.json").read_text())
assert digest(root / "INPUTS.json") == frozen["inputs_sha256"]
inputs = json.loads((root / "INPUTS.json").read_text())
for name, expected in inputs.items():
    assert digest(root / name) == expected, name
pins = json.loads((root / "SOURCE-PINS.json").read_text())["pins"]
for flat, path in {
    "custom_properties.rs": "servo/components/style/custom_properties.rs",
    "cascade.rs": "servo/components/style/properties/cascade.rs",
    "registered_value.rs": "servo/components/style/properties_and_values/value.rs",
}.items():
    assert digest(root / "native" / flat) == pins[path]
for row in json.loads((root / "spec/FETCH.json").read_text()):
    assert row["status"] == 200
    assert digest(root / "spec" / (row["name"] + ".html")) == row["sha256"]
cases = json.loads((root / "CASES.json").read_text())
assert len(cases) == 14 and len({row["name"] for row in cases}) == 14
assert sum(row["expected"] != row["predicted_native"] for row in cases) == 7
html = (root / "registered-unit-token-classification.html").read_text()
script = re.findall(r"<script>(.*?)</script>", html, re.S)
assert len(script) == 1
assert json.loads(re.search(r"const cases = (.*?);\n", script[0], re.S)[1]) == cases
with tempfile.TemporaryDirectory(prefix="unit-token-probe-") as tmp:
    path = Path(tmp) / "probe.js"
    path.write_text(script[0])
    node = shutil.which("node") or "/opt/homebrew/bin/node"
    subprocess.run([node, "--check", str(path)], check=True, capture_output=True)
print(json.dumps({"status": "PASS", "entries": len(inputs), "cases": len(cases),
                  "predicted_failures": 7, "browser_execution": "NOT RUN"}, indent=2))
