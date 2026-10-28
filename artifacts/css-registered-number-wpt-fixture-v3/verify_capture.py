import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "artifacts/css-registered-number-wpt-fixture-v2"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pins = read(HERE / "SOURCE-PINS.json")
for name,item in pins.items():
    source = ROOT / item["origin"]
    assert source.exists() == item["exists"], name
    if item["exists"]:
        assert not source.is_symlink() and sha(source) == item["sha256"], name
        capture = HERE / item["capture"]
        assert sha(capture) == item["sha256"] and capture.stat().st_size == item["bytes"], name
for name,expected in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == expected, name
selected = read(HERE / "SELECTED.json")
a = read(HERE / "TARGET-SUBTESTS.json")
b = read(HERE / "HELD-SUBTESTS.json")
reg = read(HERE / "REGRESSION-SUBTESTS.json")
assert sum(map(len,a.values())) == 104 and sum(map(len,b.values())) == 16
assert sum(map(len,reg.values())) == 446
assert len(selected) == 23 and sum(kind == "reftest" for kind in selected.values()) == 6
assert set(a).isdisjoint(b) and set(a).isdisjoint(reg) and set(b).isdisjoint(reg)
assert set(a) | set(b) | set(reg) == {name for name,kind in selected.items() if kind == "testharness"}
enumeration = read(HERE / "ENUMERATION.json")
assert enumeration["target_pages"] == a and enumeration["held_pages"] == b
old_names = read(PREVIOUS / "ENUMERATION.json")["target_names"]
assert old_names == enumeration["original58_names"]
old_path = (PREVIOUS / "NEW-WPT-PATH.txt").read_text().strip()
assert (HERE / "historical/prior58.html").read_bytes() == (PREVIOUS / "candidate" / old_path).read_bytes()
assert (HERE / "REGRESSION-SUBTESTS.json").read_bytes() == (PREVIOUS / "REGRESSION-SUBTESTS.json").read_bytes()
assert (HERE / "observation-only.html").read_bytes() == (PREVIOUS / "observation-only.html").read_bytes()
for names in list(a.values())+list(b.values())+list(reg.values()):assert len(names) == len(set(names))
for kind,pages in (("candidate",a),("held",b)):
    for name in pages:
        assert (HERE / (kind+"/testing/web-platform/tests"+name)).read_bytes() == (HERE / ("capture/testing/web-platform/tests"+name)).read_bytes()
manifest=read(HERE / "SUBSET-MANIFEST.json")
for name,expected in read(HERE / "EXISTING-MANIFEST-ENTRIES.json").items():
    value=manifest["items"][expected["type"]]
    for part in Path(name.lstrip("/")).parts:value=value[part]
    assert value == expected["entry"],name
assert len(read(HERE / "EXISTING-MANIFEST-ENTRIES.json")) == 21
assert "observation-only" not in json.dumps(manifest)
assert not any(name.endswith("/registered-numeric-relative-units.html") for name in selected)
partition=read(HERE / "PRIOR58-PARTITION.json")
assert partition["A_original_PASS"] == 38 and partition["A_original_FAIL"] == 17 and partition["B_original_FAIL"] == 3
assert len(partition["mapping"]) == 58
excluded=read(HERE / "EXCLUDED-PERCENTAGE-DIVISION.json")
assert len(excluded["rows"]) == 4
assert not any(case["group"] == "percentage" and case["kind"].startswith("provider") for case in read(HERE / "BREADTH-CASES.json"))
for name in read(HERE / "REFERENCES-TO-COPY.json"):
    assert (HERE / ("capture/testing/web-platform/tests"+name)).is_file()
for file in HERE.glob("*.py"):ast.parse(file.read_text(),filename=str(file))
print(json.dumps({"source_capture_bindings":len(pins),"A_required":104,"B_held":16,"regressions":446,"reftests":6,
                  "original58_mapped_once":True,"prior21_regression_manifest_entries_unchanged":True,
                  "percentage_provider_division_excluded":True,"self_font_observation_excluded":True,
                  "browser_executed":False,"native_source_pins_frozen":False},indent=2))
