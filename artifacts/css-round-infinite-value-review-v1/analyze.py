import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[2]
directory = root / "artifacts/css-round-infinite-value-browser-v1"
modes = ["nearest", "up", "down", "to-zero"]
reports = {}
for filename, count in [("system-observation.json", 224),
                        ("system-leaf-detached-observation.json", 72)]:
    path = directory / filename
    data = json.loads(path.read_text())
    rows = data["snapshots"]
    assert len(rows) == data["snapshotCount"] == count
    mismatches = Counter()
    resolved_mismatches = Counter()
    if count == 72:
        keys = {(r["kind"], r["mode"], r["sign"], r["phase"]) for r in rows}
        assert keys == set(itertools.product(
            ["nan-step", "relative-leaf-step", "fixed-finite-step"], modes, [1, -1], range(3)))
    else:
        cases = ["positive-infinities", "negative-infinities", "contextual-infinities",
                 "positive-finite-infinite-step", "negative-finite-infinite-step",
                 "zero-infinite-step", "nan-infinite-step", "contextual-finite-infinite-step",
                 "infinite-finite-step", "contextual-infinite-finite-step", "finite-zero-step",
                 "finite-nan-step", "finite-contextual-step", "infinite-contextual-step"]
        assert {(r["id"], r["mode"], r["phase"]) for r in rows} == set(
            itertools.product(cases, modes, range(4)))
    for row in rows:
        assert row["supported"] and row["specified"]
        assert row["resolvedSupported"] and row["resolvedSpecified"]
        assert row["actual"] == row["repeated"]
        assert float(row["literal"]) == row["expected"]
        calibration = row["inputCalibration"]
        assert calibration["font"] == f'{row["font"]}px'
        if count == 72:
            assert row["font"] == [8, 0, 8][row["phase"]]
            assert calibration["width"] == f'{row["font"]}px'
            assert calibration["nanSupported"] and calibration["nanSpecified"]
            assert float(calibration["nanEncoding"]) == 0
            expected = 0 if row["kind"] == "nan-step" or (
                row["kind"] == "relative-leaf-step" and row["font"] == 0
            ) else 0.5 + 0.25 * row["sign"]
            assert row["expected"] == expected
            key = row["kind"]
        else:
            assert row["font"] == [8, 16, 32, 8][row["phase"]]
            assert calibration["difference"] == f'{row["font"] - 16}px'
            assert float(calibration["signEncoding"]) == (0.25 if row["font"] < 16 else
                                                         0.5 if row["font"] == 16 else 0.75)
            key = row["id"]
            if key == "infinite-contextual-step":
                assert row["expected"] == 0
        if float(row["actual"]) != row["expected"]:
            mismatches[key] += 1
        if float(row["resolved"]) != row["expected"]:
            resolved_mismatches[key] += 1
    reports[filename] = {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "browser": data["userAgent"], "rows": count,
        "direct_calibration_failures": 0, "mismatches": dict(mismatches),
        "resolved_round_diagnostic_mismatches": dict(resolved_mismatches),
    }
assert reports["system-observation.json"]["mismatches"] == {
    "contextual-infinities": 16, "nan-infinite-step": 16,
    "contextual-finite-infinite-step": 5, "infinite-contextual-step": 16}
assert reports["system-leaf-detached-observation.json"]["mismatches"] == {
    "nan-step": 24, "relative-leaf-step": 8}
print(json.dumps(reports, indent=2, sort_keys=True))
