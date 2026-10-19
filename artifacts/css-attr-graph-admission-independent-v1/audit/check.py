#!/usr/bin/env python3
"""Check sealed source/probe correspondence, without executing a browser."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = json.loads((ROOT / "FREEZE.json").read_text())
assert digest(ROOT / "INPUTS.json") == freeze["inputs_sha256"]
entries = json.loads((ROOT / "INPUTS.json").read_text())
for name, expected in entries.items():
    assert digest(ROOT / name) == expected, name

source_freeze = json.loads((ROOT / "sources/FREEZE.json").read_text())
assert digest(ROOT / "sources/INPUTS.json") == source_freeze["inputs_sha256"]
source_inputs = json.loads((ROOT / "sources/INPUTS.json").read_text())
for path in (ROOT / "sources").rglob("*.rs"):
    name = str(path.relative_to(ROOT / "sources"))
    assert digest(path) == source_inputs[name], name
for record in json.loads((ROOT / "spec/FETCH.json").read_text()):
    assert record["status"] == 200
    assert digest(ROOT / "spec" / (record["name"] + ".html")) == record["sha256"]

cases = json.loads((ROOT / "CASES.json").read_text())
assert len(cases) == 13 and len({row["name"] for row in cases}) == 13
discrepancies = [row for row in cases if row["predicted_native_width"] != row["expected"]["width"]]
assert len(discrepancies) == 4
with tempfile.TemporaryDirectory(prefix="attr-graph-audit-") as tmp:
    for name in ["attr-registered-relative-dependencies.html", "unused-fallback-diagnostic.html"]:
        html = (ROOT / name).read_text()
        scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
        assert len(scripts) == 1
        if name.startswith("attr-"):
            actual = json.loads(re.search(r"const cases = (.*?);\n", scripts[0], re.S)[1])
            assert actual == cases
        else:
            assert "testharness" not in html and "diagnostic only; no normative assertion" in html
        path = Path(tmp) / (name + ".js")
        path.write_text(scripts[0])
        node = shutil.which("node") or "/opt/homebrew/bin/node"
        subprocess.run([node, "--check", str(path)], check=True, capture_output=True)
print(json.dumps({"status": "PASS", "entries": len(entries), "cases": len(cases),
                  "predicted_discrepant_rows": len(discrepancies),
                  "browser_execution": "NOT RUN", "formal_proof": "NOT CLAIMED"}, indent=2))
