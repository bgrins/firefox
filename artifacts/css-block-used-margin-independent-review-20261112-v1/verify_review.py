import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REPAIR = REPO / "artifacts/css-block-used-margin-repair-20261112-v1"
AUDIT = REPO / "artifacts/css-block-used-margin-audit-20261112-v1"
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
inputs = json.loads((REPAIR / "INPUTS.json").read_text())
pins = {}
for name, variants in inputs.items():
    for variant, expected in variants.items():
        p = REPAIR / variant / name
        assert digest(p) == expected
        pins[str(p.relative_to(REPO))] = expected
original = (REPAIR / "original/layout/generic/ReflowInput.cpp").read_text()
candidate = (REPAIR / "candidate/layout/generic/ReflowInput.cpp").read_text()
old = """    SetComputedLogicalMargin(cbWM, margin);
    return;
"""
new = """    SetComputedLogicalMargin(cbWM, margin);
    if (auto* propValue = mFrame->GetProperty(nsIFrame::UsedMarginProperty())) {
      *propValue = margin.GetPhysicalMargin(cbWM);
    }
    return;
"""
assert original.count(old) == 1
assert original.replace(old, new) == candidate
wpt = (REPAIR / "candidate/testing/web-platform/tests/css/cssom/resolved-margins-overconstrained-block.html").read_text()
rows = {int(k): json.loads(v) for k, v in re.findall(r"^  \[(\d+), (\[\[.*\]\])\],$", wpt, re.M)}
assert set(rows) == {40, 100, 200}
modes = {"auto": (None, None), "start-percent": (10, None), "end-percent": (None, 10), "percent": (10, 10)}
def used(width, pair):
    start, end = pair
    if width + (start or 0) + (end or 0) > 100:
        start = start or 0
        return [start, 100 - width - start]
    if start is None and end is None:
        return [(100 - width) // 2] * 2
    if start is None:
        return [100 - width - end, end]
    return [start, 100 - width - start]
def before(width, pair):
    initial = [v or 0 for v in pair]
    return initial if width + sum(initial) > 100 else used(width, pair)
for width, expected in rows.items():
    assert expected == [used(width, pair) for pair in modes.values()]
predicted = {}
for wm in ["horizontal-tb", "vertical-rl", "vertical-lr"]:
    for direction in ["ltr", "rtl"]:
        for mode, pair in modes.items():
            for sizes in [[40], [100], [200], [40, 200, 40, 100, 200]]:
                name = f"{wm} {direction}, {mode}, inline sizes " + " -> ".join(map(str, sizes))
                predicted[name] = "PASS" if all(before(n, pair) == used(n, pair) for n in sizes) else "FAIL"
assert Counter(predicted.values()) == {"PASS": 30, "FAIL": 66}
summary = {}
for phase in ["baseline", "fixed"]:
    report = json.loads((REPAIR / phase / "wptreport.json").read_text())
    results = report["results"]
    assert all(r["status"] == "OK" for r in results)
    target = next(r for r in results if r["test"].endswith("resolved-margins-overconstrained-block.html"))
    actual = {s["name"]: s["status"] for s in target["subtests"]}
    assert len(actual) == len(target["subtests"]) == 96
    assert actual == (predicted if phase == "baseline" else dict.fromkeys(predicted, "PASS"))
    counts = Counter(s["status"] for r in results for s in r["subtests"])
    if phase == "fixed":
        assert counts == {"PASS": 106} and len(results) == 3
    summary[phase] = {"files": len(results), "subtests": dict(counts), "browser_build_id": report["run_info"]["browser_build_id"]}
for rel in ["OBSERVATIONS.json", "quads-enabled/OBSERVATIONS.json"]:
    observations = json.loads((AUDIT / rel).read_text())
    assert len(observations) == 24
    assert len({(x["direction"], x["size"], x["margin"]) for x in observations}) == 24
    pins[str((AUDIT / rel).relative_to(REPO))] = digest(AUDIT / rel)
for rel in ["bug-381328.md", "bug-1298008.md", "RESULT.json", "quads-enabled/RESULT.json"]:
    pins[str((AUDIT / rel).relative_to(REPO))] = digest(AUDIT / rel)
for rel in ["INPUTS.json", "candidate.patch", "ACCEPTANCE.json", "baseline/wptreport.json", "fixed/wptreport.json", "baseline/COMMANDS.json", "fixed/COMMANDS.json", "build/COMMANDS.json", "fixed/CLEANUP.json", "build/CLEANUP.json"]:
    pins[str((REPAIR / rel).relative_to(REPO))] = digest(REPAIR / rel)
(HERE / "REVIEWED-INPUTS.json").write_text(json.dumps(pins, indent=2) + "\n")
(HERE / "CHECK.json").write_text(json.dumps({"status": "PASS source and retained-report checks", "source_delta": "exact three-line conditional cache refresh", "expected_table_rows": 12, "reports": summary, "own_native_runs": 0, "fresh_process_inspection": False, "native_universal_proof": False}, indent=2) + "\n")
print(json.dumps(summary))
