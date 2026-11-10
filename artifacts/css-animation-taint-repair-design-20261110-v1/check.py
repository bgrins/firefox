#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--check-live", action="store_true")
args = parser.parse_args()
base = Path(__file__).resolve().parent
repo = base.parent.parent
sha = lambda data: hashlib.sha256(data).hexdigest()
sources = json.loads((base / "SOURCES.json").read_text())
checked = []
for name, pin in sources.items():
    copied = (base / "source" / name).read_bytes()
    original = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "show", f"{pin['revision']}:{name}"],
        cwd=repo, capture_output=True, check=True,
    ).stdout
    assert sha(copied) == pin["sha256"], name
    assert original == copied, name
    row = {"path": name, "sha256": sha(copied), "git_matches": True}
    if args.check_live:
        assert (repo / name).read_bytes() == copied, name
        row["live_matches"] = True
    checked.append(row)
policies = json.loads((base / "POLICY-SOURCES.json").read_text())
for pin in policies:
    assert sha((base / pin["name"]).read_bytes()) == pin["sha256"], pin["name"]
excerpts = json.loads((base / "EXCERPTS.json").read_text())
assert len({x["id"] for x in excerpts}) == len(excerpts)
for excerpt in excerpts:
    assert excerpt["source"] in sources
    lines = (base / "source" / excerpt["source"]).read_text().splitlines(keepends=True)
    actual = "".join(lines[excerpt["start"] - 1:excerpt["end"]])
    assert actual == excerpt["text"] and actual.strip(), excerpt["id"]
print(json.dumps({
    "result": "PASS",
    "scope": "Source and excerpt authentication only; not a behavioral proof or patch validation",
    "revisions": sorted({x["revision"] for x in sources.values()}),
    "source_count": len(checked),
    "policy_snapshot_count": len(policies),
    "excerpt_count": len(excerpts),
    "sources": checked,
    "policy_snapshots": policies,
}, indent=2))
