#!/usr/bin/env python3
import argparse
import collections
import difflib
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest_bytes = (root / "MANIFEST.json").read_bytes()
assert sha(manifest_bytes) == args.manifest_sha, "manifest identity mismatch"
manifest = json.loads(manifest_bytes)
for name, digest in manifest["files"].items():
    path = root / name
    assert not path.is_symlink() and path.resolve().is_relative_to(root)
    assert sha(path.read_bytes()) == digest, "input mismatch: " + name
# No artifact module is imported or executed. Parse authenticated data only.
scout = json.loads((root / "scout/INPUTS.json").read_text())
for name, digest in scout["files"].items():
    assert sha((root / "scout" / name).read_bytes()) == digest
spec = (root / "scout/css-values-5.html").read_text()
for anchor in ["attr-notation", "typedef-attr-name", "attr-substitution"]:
    assert 'id="' + anchor + '"' in spec
assert sha((root / "scout/css-values-5.html").read_bytes()) == json.loads((root / "scout/FETCH.json").read_text())["sha256"]
counts = {}
for phase, directory in [("baseline-v1", "baseline"), ("baseline-v3", "baseline-v3")]:
    base = root / directory
    receipt = json.loads((base / (phase + "-receipt.json")).read_text())
    assert receipt["pins_before"] == receipt["pins_after"] and receipt["all_inputs_unchanged"]
    bundled = 0
    for name, digest in receipt["pins_before"].items():
        path = base / "sources" / name.replace("/", "__")
        if path.exists():
            assert sha(path.read_bytes()) == digest, name
            bundled += 1
    raw = [json.loads(line) for line in (base / (phase + ".jsonl")).read_text().splitlines()]
    statuses = [r for r in raw if r["action"] in ["test_status", "test_end"]]
    assert statuses == receipt["statuses"]
    assert sum(r["action"] == "suite_end" for r in raw) == receipt["suite_end_count"] == 1
    summary = {}
    for row in statuses:
        result = summary.setdefault(row["test"], {})
        result[row["status"]] = result.get(row["status"], 0) + 1
    assert summary == receipt["counts"]
    counts[phase] = {"counts": summary, "bundled_pins": bundled}
wpt = (root / "baseline/sources/testing__web-platform__tests__css__css-values__attr-namespace-cache.html").read_text()
assert (root / "scout/probe.css").read_text() in wpt
assert (root / "scout/probe.js").read_text() in wpt
paths = ["servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs"]
def diff(original, candidate, path):
    return "".join(difflib.unified_diff(original.splitlines(keepends=True), candidate.splitlines(keepends=True), fromfile="a/" + path, tofile="b/" + path))
patch = ""
for path, digest in json.loads((root / "candidate-v2/INPUTS.json").read_text()).items():
    rel = path.removeprefix("servo/components/style/")
    candidate = root / "candidate-v2" / rel.replace("/", "__")
    assert sha(candidate.read_bytes()) == digest
    patch += diff((root / "scout/source" / rel).read_text(), candidate.read_text(), path)
assert patch == (root / "candidate-v2/native-draft-v2.patch").read_text()
port = root / "head-port"
head_patch = ""
for path, pins in json.loads((port / "PINS.json").read_text()).items():
    a, b = port / "original" / path, port / "candidate" / path
    assert sha(a.read_bytes()) == pins["original"] and sha(b.read_bytes()) == pins["candidate"]
    head_patch += diff(a.read_text(), b.read_text(), path)
assert head_patch == (port / "native-head.patch").read_text()
def changed_lines(patch):
    return [line for line in patch.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
expected = [line.replace("-use crate::{FxHashMap, FxHashSet};", "-use crate::FxHashMap;").replace("+use crate::{FxHashMap, FxHashSet, Namespace};", "+use crate::{FxHashMap, Namespace};") for line in changed_lines(patch)]
assert changed_lines(head_patch) == expected, "HEAD port changed unrelated lines"
result = {"status": "PASS", "authenticated_files": len(manifest["files"]), "raw_status_receipts": counts, "candidate_diff_exact": True, "head_port_only_import_adaptation": True, "scope": "integrity/source/diff/recorded-status replay; no compilation or browser execution"}
print(json.dumps(result, indent=2))
