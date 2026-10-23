import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "css-hidden-layout-column-runtime-v1"
PHASES = ["baseline", "both"]
reports = {}
inputs = {}
for phase in PHASES:
    path = RUNTIME / phase / "RUN.json"
    data = path.read_bytes()
    inputs[phase] = hashlib.sha256(data).hexdigest()
    run = json.loads(data)
    assert run["complete"] and run["before"] == run["after"]
    raw = RUNTIME / phase / "raw.json"
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    inputs[phase + "/raw"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    assert run["rows"] == [r for r in events if r.get("action") == "test_status"]
    assert run["ends"] == [r for r in events if r.get("action") == "test_end"]
    assert len(run["rows"]) == 66 and len(run["ends"]) == 7
    rows = {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in run["rows"]}
    ends = {r["test"]: r["status"] for r in run["ends"]}
    assert len(rows) == len(run["rows"])
    reports[phase] = (rows, ends)
base_rows, base_ends = reports["baseline"]
for rows, ends in reports.values():
    assert rows.keys() == base_rows.keys() and ends.keys() == base_ends.keys()
result = {"input_sha256": inputs, "phases": {}, "pairs": {}}
for phase, (rows, _) in reports.items():
    prior_path = HERE.parent / "css-hidden-layout-compact-runtime-v3" / phase / "RUN.json"
    prior_data = prior_path.read_bytes()
    prior = json.loads(prior_data)
    prior_rows = {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in prior["rows"]}
    assert len(prior_rows) == 58
    assert all(rows[k] == value for k, value in prior_rows.items())
    inputs["prior/" + phase] = hashlib.sha256(prior_data).hexdigest()
result["prior_58_outcomes_match"] = True
for phase, (rows, ends) in reports.items():
    result["phases"][phase] = {
        "counts": {s: sum(v[0] == s for v in rows.values()) for s in ["PASS", "FAIL"]},
        "ends": ends,
        "failures": [{"test": k[0], "subtest": k[1], "message": v[1]} for k, v in rows.items() if v[0] != "PASS"],
    }
for before, after in [("baseline", "both")]:
    a, ae = reports[before]
    b, be = reports[after]
    changed = [{"test": k[0], "subtest": k[1], "before": a[k], "after": b[k]} for k in a if a[k] != b[k]]
    result["pairs"][before + " -> " + after] = {
        "improvements": sum(a[k][0] == "FAIL" and b[k][0] == "PASS" for k in a),
        "regressions": sum(a[k][0] == "PASS" and b[k][0] == "FAIL" for k in a),
        "changes": changed,
        "end_changes": [{"test": k, "before": ae[k], "after": be[k]} for k in ae if ae[k] != be[k]],
    }
(HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"phases": {k: v["counts"] for k, v in result["phases"].items()}, "pairs": {k: {j: v[j] for j in ["improvements", "regressions", "end_changes"]} for k, v in result["pairs"].items()}}, indent=2))
