#!/usr/bin/env python3
import argparse
import difflib
import hashlib
import json
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("--manifest-sha",required=True)
a=parser.parse_args()
root=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(root/"MANIFEST.json").read_bytes()
assert sha(raw)==a.manifest_sha
manifest=json.loads(raw)
for name,digest in manifest["files"].items():
    p=root/name
    assert not p.is_symlink() and p.resolve().is_relative_to(root)
    assert sha(p.read_bytes())==digest,"input mismatch: "+name
pins=json.loads((root/"PINS.json").read_text())
for version in ["original","candidate"]:
    for name,digest in pins[version].items():assert sha((root/version/name).read_bytes())==digest
assert (root/"original/custom_properties.rs").read_bytes()==(root/"candidate/custom_properties.rs").read_bytes()
old=(root/"original/cascade.rs").read_text();new=(root/"candidate/cascade.rs").read_text()
start="pub fn update_attributes_map("
end="/// Computes the map"
assert old.split(start,1)[0]==new.split(start,1)[0]
assert old.split(start,1)[1].split(end,1)[1]==new.split(start,1)[1].split(end,1)[1]
body=new.split(start,1)[1].split(end,1)[0]
assert body.index("refs_stack.push(&fallback.references)") < body.index("if !next.is_attr_with_type()") < body.index("next.attribute_data.namespace()")
assert "!context.map().contains_attr(&next.name, namespace)" in new
patch="".join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile="a/servo/components/style/properties/cascade.rs",tofile="b/servo/components/style/properties/cascade.rs"))
assert patch==(root/"recursive-preload.patch").read_text()
assert sha(patch.encode())==pins["patch_sha256"]=="9500832151dae10c42f4f62011a75308aba152297aa47a8e307ce1248fc11286"
cases=json.loads((root/"CASES.json").read_text());assert len(cases)==16
assert sum(c["role"]=="preload witness" for c in cases)==10
html=(root/"attr-fallback-preparation.html").read_text()
assert sha(html.encode())==pins["final_wpt_sha256"]
rows=json.loads("["+html.split("const cases = [",1)[1].split("];",1)[0]+"]")
assert rows==[[c[k] for k in ["name","declarations","attributes","property","expected"]] for c in cases]
assert len(set(c["name"] for c in cases))==16
assert all(c["status"]=="UNEXECUTED final WPT" for c in cases)
assert any("attr(missing," in c["declarations"] for c in cases)
assert cases[-1]["attributes"]["chain"]=="var(--v)"
assert "sheet.deleteRule(ruleIndex)" in html and "assert_implements_optional" not in html
for directory,digest,names,count in [
 ("diagnostics19","96b52eefcfb00848c0450e5893d03258c484be7e1d7163a377b421072ae22350",["attr-fallback-preload.html","CASES.json","REPORT.md"],19),
 ("diagnostics6","7cbf332d29482991a2e130f9503d130a095d9a7d0903dc023f6f9089d5b4706e",["attr-fallback-readiness.html","CASES.json","REPORT.md"],6)]:
    raw=(root/directory/"PARENT-MANIFEST.json").read_bytes();assert sha(raw)==digest
    parent=json.loads(raw)["files"]
    for name in names:assert sha((root/directory/name).read_bytes())==parent[name]
    assert len(json.loads((root/directory/"CASES.json").read_text()))==count
receipt=json.loads((root/"baseline19/baseline-v1-receipt.json").read_text())
raw=[json.loads(line) for line in (root/"baseline19/baseline-v1.jsonl").read_text().splitlines() if line.strip()]
assert [r for r in raw if r.get("action") in ["test_status","test_end"]]==receipt["statuses"]
assert receipt["pins_before"]==receipt["pins_after"] and receipt["all_inputs_unchanged"]
statuses=[r for r in raw if r.get("action")=="test_status"]
assert sum(r["status"]=="FAIL" for r in statuses)==9
assert sum(r["status"]=="PASS" for r in statuses)==10
assert sum(r.get("action")=="suite_end" for r in raw)==1
spec=(root/"spec-snapshot.html").read_bytes()
assert sha(spec)==json.loads((root/"spec-snapshot-fetch.json").read_text())["sha256"]
assert b'id="attr-substitution"' in spec
print(json.dumps({"status":"PASS","authenticated_files":len(manifest["files"]),"final_wpt_cases":16,"unchanged_diagnostic_cases":25,"native_status":"NOT COMPILED BY REVIEWER","final_wpt_status":"UNEXECUTED BY REVIEWER","scope":"integrity, exact source composition and fixture/baseline identity"},indent=2))
