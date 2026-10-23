import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / "css-hidden-query-repairs-runtime-v1"
RUNTIME_MANIFEST = "ffed9eeb5f286209632cc294a059de01aaf882c16467dc1c913c9fc2cccb84b5"
assert hashlib.sha256((RUNTIME / "FILES.json").read_bytes()).hexdigest() == RUNTIME_MANIFEST
for name, digest in json.loads((RUNTIME / "FILES.json").read_text())["files"].items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert hashlib.sha256((RUNTIME / name).read_bytes()).hexdigest() == digest, name
state = json.loads((RUNTIME / "STATE.json").read_text())
assert state["status"] == "terminal" and state["restored"]
assert state["restore_build_exit"] == 0 and state["recovery_errors"] == []
assert "failure" not in state
assert (RUNTIME / "BEFORE.json").read_bytes() == (RUNTIME / "FINAL.json").read_bytes()
PHASES = ["baseline", "column-provider", "skipped-line-block", "both"]
reports = {}
pins = {}
for phase in PHASES:
    path = RUNTIME / phase / "RUN.json"
    raw = RUNTIME / phase / "raw.json"
    run = json.loads(path.read_text())
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    assert run["complete"] and run["before"] == run["after"]
    assert run["rows"] == [r for r in events if r.get("action") == "test_status"]
    assert run["ends"] == [r for r in events if r.get("action") == "test_end"]
    assert len(run["rows"]) == 66 and len(run["ends"]) == 7
    assert all(r["status"] == "OK" for r in run["ends"])
    rows = {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in run["rows"]}
    assert len(rows) == 66
    reports[phase] = rows
    for p in [path, raw]:
        pins[str(p.relative_to(RUNTIME))] = hashlib.sha256(p.read_bytes()).hexdigest()
base = reports["baseline"]
assert all(set(rows) == set(base) for rows in reports.values())
prior_path = HERE.parent / "css-hidden-layout-column-runtime-v1/both/RUN.json"
prior = json.loads(prior_path.read_text())
assert base == {(r["test"], r["subtest"]): (r["status"], r.get("message")) for r in prior["rows"]}
result = {"runtime_manifest_sha256": RUNTIME_MANIFEST,
          "input_sha256": pins, "prior_sha256": hashlib.sha256(prior_path.read_bytes()).hexdigest(),
          "baseline_matches_prior": True, "phases": {}, "pairs": {}}
for phase, rows in reports.items():
    result["phases"][phase] = {
        "counts": dict(Counter(value[0] for value in rows.values())),
        "files": {test: dict(Counter(value[0] for key, value in rows.items() if key[0] == test))
                  for test in sorted({key[0] for key in rows})},
        "failures": [{"test": k[0], "subtest": k[1], "message": v[1]}
                     for k, v in rows.items() if v[0] != "PASS"],
    }
for before, after in [("baseline", "column-provider"), ("baseline", "skipped-line-block"),
                      ("baseline", "both"), ("column-provider", "both"), ("skipped-line-block", "both")]:
    a, b = reports[before], reports[after]
    result["pairs"][before + " -> " + after] = {
        "transitions": dict(Counter(a[k][0] + "->" + b[k][0] for k in a)),
        "changes": [{"test": k[0], "subtest": k[1], "before": a[k], "after": b[k]}
                    for k in a if a[k] != b[k]],
    }
result["four_phase_patterns"] = dict(Counter("/".join(reports[p][k][0] for p in PHASES) for k in base))
result["baseline_failure_matrix"] = [
    {"test": k[0], "subtest": k[1], "outcomes": {p: reports[p][k] for p in PHASES}}
    for k in base if base[k][0] == "FAIL"
]
(HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"phases": {p: r["counts"] for p, r in result["phases"].items()},
                  "patterns": result["four_phase_patterns"],
                  "pairs": {p: r["transitions"] for p, r in result["pairs"].items()}}, indent=2))
