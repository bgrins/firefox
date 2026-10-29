import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MOVES = ROOT / "artifacts/css-sibling-context-move-browser-runtime-1"
ORDINARY = ROOT / "artifacts/css-sibling-context-reparenting-browser-runtime-1"
def load(path):
    return json.loads(path.read_bytes())
def events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]
def rows(path):
    return [e for e in events(path) if e.get("action") == "test_status"]
move_rows = rows(MOVES / "raw.jsonl")
ordinary_rows = rows(ORDINARY / "raw.jsonl")
expected = load(ROOT / "artifacts/css-sibling-context-move-boundary-v1/EXPERIMENT.json")["target_subtests"]
assert Counter((r["test"], r["subtest"]) for r in move_rows) == Counter((p, n) for p, ns in expected.items() for n in ns)
assert Counter(r["status"] for r in move_rows) == {"PASS": 15, "FAIL": 3}
ordinary_expected = load(ROOT / "artifacts/css-sibling-context-reparenting-probe-v1/EXPERIMENT.json")["target_subtests"]
assert Counter((r["test"], r["subtest"]) for r in ordinary_rows) == Counter((p, n) for p, ns in ordinary_expected.items() for n in ns)
assert load(MOVES / "APPLICATION-METADATA.json") == load(ORDINARY / "APPLICATION-METADATA.json")
assert load(MOVES / "BINARY-PINS.json") == load(ORDINARY / "BINARY-PINS.json")
assert len(ordinary_rows) == 6 and all(r["status"] == "PASS" for r in ordinary_rows)
for runtime in (MOVES, ORDINARY):
    ends = [e for e in events(runtime / "raw.jsonl") if e.get("action") == "test_end"]
    assert len(ends) == 1 and ends[0]["status"] == "OK"
    assert load(runtime / "PRE.json") == load(runtime / "POST.json")
    assert load(runtime / "APPLICATION-METADATA.json") == load(runtime / "APPLICATION-METADATA-POST.json")
    result = load(runtime / "RESULT.json")
    driver = load(runtime / "OBSERVATION-DRIVER.json")
    assert result["success"] and result["preservation_verified"] and result["execution_error"] is None
    assert driver["success"] and driver["error"] is None and driver["preservation_error"] is None and driver["owned_processes"] == {}
failures = []
for row in move_rows:
    if row["status"] == "PASS":
        continue
    message = row["message"]
    assert message.startswith("assert_equals: Own sibling context; ")
    record, _ = json.JSONDecoder().raw_decode(message[message.index("{"):])
    prop = record["property"]
    assert record["operation"] == "reparent-moveBefore" and record["basis"] == "count"
    assert row["subtest"] == f"reparent-moveBefore: {prop} sibling-count"
    assert [s["phase"] for s in record["snapshots"]] == ["initial", "moved", "restored"]
    differences = []
    for phase, snapshot in enumerate(record["snapshots"]):
        counts = [1, 3, 3] if phase == 1 else [2, 2, 2]
        indices = [1, 3, 1] if phase == 1 else [1, 2, 1]
        parents = ["left", "right", "right"] if phase == 1 else ["left", "left", "right"]
        assert snapshot["parentDifferences"] == [] and len(snapshot["values"]) == 3
        for i, value in enumerate(snapshot["values"]):
            n = counts[i]
            literal = f"{n * 10}px" if prop == "width" else f"0.{n}" if prop == "opacity" else str(n * 100)
            assert (value["count"], value["input"], value["index"], value["parent"]) == (n, n, indices[i], parents[i])
            assert value["expected"] == literal and value["repeat"] == value["actual"] and value["animations"] == 0
            if prop == "width":
                assert value["referenceWidth"] == n * 10 and value["width"] == int(value["actual"][:-2])
            if value["actual"] != value["expected"]:
                differences.append({"phase": snapshot["phase"], "target": i, "actual": value["actual"], "expected": value["expected"]})
    assert [(x["phase"], x["target"]) for x in differences] == [("moved", 0), ("restored", 2)]
    failures.append({"property": prop, "differences": differences})
assert {f["property"] for f in failures} == {"width", "opacity", "font-weight"}
paths = [r / n for r in (MOVES, ORDINARY) for n in ("raw.jsonl", "RESULT.json", "OBSERVATION-DRIVER.json", "PRE.json", "POST.json", "APPLICATION-METADATA.json", "APPLICATION-METADATA-POST.json", "BINARY-PINS.json")]
paths += [ROOT / "artifacts/css-sibling-context-move-boundary-v1/sibling-context-moves.html", ROOT / "artifacts/css-sibling-context-move-boundary-v1/EXPERIMENT.json", ROOT / "artifacts/css-sibling-context-reparenting-probe-v1/EXPERIMENT.json"]
report = {"move_counts": {"PASS": 15, "FAIL": 3}, "ordinary_counts": {"PASS": 6}, "ok_endings": 2, "failed_case_records_checked": 27, "calibration_failures": 0, "stale_records": 6, "failures": failures, "saved_preservation_and_driver_checks": True, "new_fix_accepted": False, "source_cause_proven": False, "references": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
print(json.dumps(report, indent=2, sort_keys=True))
