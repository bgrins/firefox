import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
original = ROOT / "artifacts/css-sibling-count-cross-parent-probe-v1/observe.js"
line = "          await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));\n"
source = original.read_text()
assert source.count(line) == 1
assert (HERE / "observe-synchronous.js").read_text() == source.replace(line, "", 1)
result = read(HERE / "RESULT.json")
assert result["source_observer_sha256"] == sha(original)
observed = read(HERE / "OBSERVATION-SYNCHRONOUS.json")
assert observed["userAgent"] == result["userAgent"] and "Firefox/158.0" in observed["userAgent"]
rows = observed["observation"]["results"]
assert observed["observation"]["schema"] == 1
assert len(rows) == 6 and {(r["property"], r["basis"]) for r in rows} == {(p, b) for p in ("width", "opacity", "font-weight") for b in ("count", "index")}
phases = ["initial", "siblings added", "restored"]
indices = [[1, 2, 3], [2, 3, 3], [1, 2, 3]]
counts = [[2, 2, 3], [3, 3, 4], [2, 2, 3]]
mismatches, records, controls = [], 0, 0
for row in rows:
    assert row["supported"] and row["specified"]
    assert len(row["snapshots"]) == 3
    for phase_index, snapshot in enumerate(row["snapshots"]):
        assert snapshot["phase"] == phases[phase_index] and snapshot["parentDifferences"] == []
        assert len(snapshot["values"]) == 3
        for target, value in enumerate(snapshot["values"]):
            assert value["index"] == indices[phase_index][target] and value["count"] == counts[phase_index][target]
            expected_input = value["count"] if row["basis"] == "count" else value["index"]
            assert value["input"] == expected_input and value["literalSpecified"]
            expected = {"width": str(expected_input * 10) + "px", "opacity": str(expected_input / 10), "font-weight": str(expected_input * 100)}[row["property"]]
            assert value["expected"] == expected and value["actual"] == value["repeat"] and value["actual"] and value["animations"] == 0
            if row["property"] == "width":
                assert value["literalWidth"] == expected_input * 10
                assert value["width"] == float(value["actual"].removesuffix("px"))
            else:
                assert value["width"] is None and value["literalWidth"] is None
            records += 1
            if row["basis"] == "index" or row["property"] == "font-weight":
                assert value["actual"] == expected
                controls += 1
            if value["actual"] != expected:
                assert row["basis"] == "count" and row["property"] in ("width", "opacity") and target == 2
                mismatches.append({"property": row["property"], "basis": row["basis"], "phase": snapshot["phase"], "target": target, "actual": value["actual"], "expected": expected, "width": value["width"], "literalWidth": value["literalWidth"]})
assert records == result["record_count"] == 54 and controls == result["controls_correct"] == 36
assert len(mismatches) == 6 and mismatches == result["mismatches"]
assert result["css_preferences_changed"] is False and result["preference_readback_available"] is False and result["native_patch_applied"] is False
print(json.dumps({"verified": True, "records": records, "calibrated_controls": controls, "mismatches": len(mismatches), "delta": "exact single double-rAF await removal", "factory_default_claim": False}, sort_keys=True))
