#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import subprocess

base = Path(__file__).resolve().parent
repo = base.parent.parent
sha = lambda data: hashlib.sha256(data).hexdigest()
primary = json.loads((base / "PRIMARY-SOURCES.json").read_text())["sources"]
for pin in primary:
    assert sha((base / pin["file"]).read_bytes()) == pin["sha256"], pin["file"]
html_hashes = {p["sha256"] for p in primary if p["file"].endswith(".html")}
sections = 0
for pin in json.loads((base / "DISCOVERY.json").read_text()):
    content = (base / (pin["name"] + ".md")).read_bytes()
    assert sha(content) == pin["sha256"], pin["name"]
    if pin["exit"] == 0:
        match = re.search(rb"\*\*SHA\*\*: hash:([0-9a-f]{64})", content)
        if match is None:
            match = re.search(rb"\*\*SHA:\*\* hash:([0-9a-f]{64})", content)
        assert match and match[1].decode() in html_hashes, pin["name"]
        sections += 1
native = json.loads((base / "NATIVE-SOURCES.json").read_text())
for name, pin in native.items():
    content = (repo / pin["location"]).read_bytes()
    assert sha(content) == pin["sha256"], name
    original = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "show", f"{pin['revision']}:{name}"],
        cwd=repo, capture_output=True, check=True,
    ).stdout
    assert content == original, name
fixture = json.loads((base / "FIXTURE.json").read_text())
assert sha((base / "reviewed-probe.html").read_bytes()) == fixture["sha256"]
anchors = json.loads((base / "ANCHORS.json").read_text())
assert all(x["exit"] == 0 for x in anchors)
runtime = json.loads((base / "RUNTIME-READOUT.json").read_text())
for name in ["log", "test_results"]:
    assert sha((repo / runtime[name + "_source"]).read_bytes()) == runtime[name + "_sha256"]
assert all(x["count"] == 16 for x in runtime["summary"].values())
print(json.dumps({
    "result": "PASS", "primary_snapshots": len(primary),
    "section_snapshots_matching_fresh_html": sections,
    "native_git_files": len(native), "validated_anchor_receipts": len(anchors),
    "runtime_modes": len(runtime["summary"]), "observations_per_mode": 16,
    "fixture_sha256": fixture["sha256"],
    "scope": "Source and snapshot authentication; not a native termination proof",
}, indent=2))
