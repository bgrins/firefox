import json
import statistics
import sys
from pathlib import Path


def verify(result):
    if result.get("valid") is not True or result.get("error") is not None:
        raise ValueError("Browser result is incomplete or failed calibration")
    if result.get("label") not in {"before", "candidate", "restored"}:
        raise ValueError("Unknown build label")
    config = {
        "counts": [100, 1000], "selectorRules": [0, 200],
        "properties": ["opacity", "transform"],
        "modes": ["animate", "first-play", "replay", "registered-seek"],
        "warmupBatches": 2, "measuredBatches": 7, "startupMs": 3000,
        "yieldMs": 10, "duration": 1000000,
    }
    if result.get("config") != config:
        raise ValueError("Changed benchmark configuration")
    cases = [
        dict(id=f"{mode}/{prop}/{count}/{rules}", mode=mode,
             property=prop, count=count, rules=rules)
        for count in config["counts"] for rules in config["selectorRules"]
        for prop in config["properties"] for mode in config["modes"]
    ]
    if result.get("caseOrder") != [c["id"] for c in cases]:
        raise ValueError("Changed case order")
    rows, cleanup = result.get("rows", []), result.get("cleanup", [])
    if len(rows) != 288 or len(cleanup) != 288:
        raise ValueError("Incomplete raw sample or cleanup history")
    groups = {c["id"]: [] for c in cases}
    for index, (row, clean) in enumerate(zip(rows, cleanup)):
        round_index, j = divmod(index, 32)
        case = cases[(j + round_index) % 32]
        expected = dict(case, round=round_index, warmup=round_index < 2)
        if any(row.get(k) != v for k, v in expected.items()):
            raise ValueError("Duplicate, reordered or changed batch")
        if clean != dict(case=case["id"], round=round_index,
                         warmup=round_index < 2, removed=True, error=None):
            raise ValueError("Missing or failed scoped cleanup")
        if row.get("correctness") != "PASS" or "error" in row:
            raise ValueError("Failed literal or identity calibration")
        values = [row.get(k) for k in ("apiMs", "flushMs", "totalMs")]
        if any(type(v) not in (float, int) or not 0 <= v < float("inf") for v in values):
            raise ValueError("Malformed duration")
        if abs(values[0] + values[1] - values[2]) > 0.000001:
            raise ValueError("Inconsistent timing boundaries")
        if not row["warmup"]:
            groups[case["id"]].append(row)
    return {
        "status": "COMPLETE_CALIBRATED_LOCAL_TIMINGS",
        "label": result["label"], "measured_batches": 224,
        "warmup_batches_retained": 64,
        "descriptive_only": True,
        "cases": {key: {field: {
            "median": statistics.median(row[field] for row in rows),
            "min": min(row[field] for row in rows),
            "max": max(row[field] for row in rows),
            "zero_samples": sum(row[field] == 0 for row in rows),
        } for field in ("apiMs", "flushMs", "totalMs")}
                  for key, rows in groups.items()},
    }


if __name__ == "__main__":
    print(json.dumps(verify(json.loads(Path(sys.argv[1]).read_text())), indent=2))
