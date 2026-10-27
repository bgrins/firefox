import collections
import hashlib
import json
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-svg-hidden-embedder-comparison-runtime-v1"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
pins = {}

def authenticate(path, expected):
    assert sha(path) == expected, str(path)
    pins[str(path.relative_to(ROOT))] = expected

draft = "40cde4e016c37181d5e2b03f7496e0d2330ed887eb70bf53645431f95486e51b"
authenticate(RUNTIME / "DRAFT-FILES.json", draft)
for name, expected in read(RUNTIME / "DRAFT-FILES.json").items():
    authenticate(RUNTIME / name, expected)
for name, expected in read(RUNTIME / "REFERENCES.json").items():
    authenticate(ROOT / name, expected)
config = read(RUNTIME / "CONFIG.json")
for item in config["required_seals"].values():
    path = ROOT / item["path"]
    authenticate(path, item["sha256"])
    for name, expected in read(path).items():
        authenticate(path.parent / name, expected)
state = read(RUNTIME / "STATE.json")
before = read(RUNTIME / "BEFORE.json")
resources = read(RUNTIME / "RESOURCES.json")
assert len(config["head_pins"]) == 56 and len(config["sources"]) == 33
assert len(config["candidate_pins"]) == 5
for name, expected in config["head_pins"].items():
    body = subprocess.check_output(["git", "show", config["head"] + ":" + name], cwd=ROOT)
    assert hashlib.sha256(body).hexdigest() == expected
for name, expected in config["candidate_pins"].items():
    authenticate(ROOT / config["candidate_sources"][name], expected)
for name, expected in read(RUNTIME / "TEST-SOURCE-PINS.json").items():
    body = subprocess.check_output(["git", "show", config["head"] + ":" + name], cwd=ROOT)
    assert hashlib.sha256(body).hexdigest() == expected

main = "/svg/types/scripted/SVGLength-hidden-embedding-viewport.html"
mainNames = [f"{depth} iframe levels: {unit} {method} {history}"
             for depth in [1, 2] for unit in ["vw", "vh"]
             for method in ["value", "convertToSpecifiedUnits"]
             for history in ["visible-resize", "hidden-only", "hidden-resize"]]
assert config["expected_subtests"][main] == mainNames
expectedIds = {(test, name) for test, names in config["expected_subtests"].items() for name in names}
assert len(expectedIds) == 52
assert config["baseline_expected_subtests"] == config["expected_subtests"]
fixture = sha(RUNTIME / "fixture.html")
results = {}
phaseRecords = {}
for phase in ["baseline", "candidate"]:
    directory = RUNTIME / ("wpt-" + phase)
    run = read(directory / "RUN.json")
    raw = directory / "raw.json"
    assert stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size < 128 * 1024 * 1024
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    rows = [e for e in events if e.get("action") == "test_status"]
    starts = [e for e in events if e.get("action") == "test_start"]
    ends = [e for e in events if e.get("action") == "test_end"]
    assert rows == run["rows"] and starts == run["starts"] and ends == run["ends"]
    assert len(starts) == len(ends) == 6
    assert {e["test"] for e in starts} == {e["test"] for e in ends} == set(config["expected_subtests"])
    assert all(e["status"] == "OK" for e in ends)
    assert sum(e.get("action") == "suite_start" for e in events) == 1
    assert sum(e.get("action") == "suite_end" for e in events) == 1
    assert not any(e.get("action") in ["crash", "suite_abort", "test_abort"] for e in events)
    assert not any(e.get("action") == "log" and e.get("level") in ["ERROR", "CRITICAL"] for e in events)
    assert not any(e.get("action") == "process_exit" and e.get("exitcode", e.get("returncode", 0)) != 0 for e in events)
    assert not any(e.get("action") == "assertion_count" and
                   not e.get("min_expected", 0) <= e["count"] <= e.get("max_expected", 0) for e in events)
    assert not any(e.get("action") in ["log", "process_output"] and
                   any(token in e.get("message", "") + e.get("data", "") for token in
                       ["PROCESS-CRASH", "TEST-UNEXPECTED-ERROR", "TEST-UNEXPECTED-TIMEOUT"]) for e in events)
    assert run["infrastructure_faults"] == [] and run["complete"] is True
    assert read(directory / "CLEANUP.json") == {"owned_group_absent": True, "errors": []}
    actual = {(r["test"], r["subtest"]): r for r in rows}
    assert len(rows) == len(actual) == 52 and set(actual) == expectedIds
    assert all(r["status"] in ["PASS", "FAIL"] for r in rows)
    assert run["exit"] == (1 if phase == "baseline" else 0)
    record = state["phases"][phase]
    assert record["build_exit"] == 0 and read(RUNTIME / (phase + "-build.json"))["exit"] == 0
    assert record["source_before_build"] == record["source_after_build"]
    source = {**config["head_pins"], **(config["candidate_pins"] if phase == "candidate" else {})}
    assert record["source_before_build"]["sources"] == source
    for key in ["head", "index_diff_sha256", "index_entries_sha256"]:
        assert record["source_before_build"][key] == before[key]
    if phase == "baseline":
        assert record["source_before_build"]["native_diff_sha256"] == hashlib.sha256(b"").hexdigest()
    expectedPins = {**resources, **source, **{name: fixture for name in config["install"]}, **record["binary_pins"]}
    assert len(expectedPins) == 405
    assert run["before"] == run["after"] == expectedPins
    counts = dict(collections.Counter(r["status"] for r in rows))
    assert counts == ({"PASS": 32, "FAIL": 20} if phase == "baseline" else {"PASS": 52})
    results[phase] = actual
    phaseRecords[phase] = {"counts": counts, "binary_pins": record["binary_pins"],
                           "phase_record_sha256": hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()}
    for name in ["RUN.json", "raw.json", "CLEANUP.json", "wpt.log"]:
        authenticate(directory / name, sha(directory / name))
    for suffix in ["-build.json", "-build.log"]:
        authenticate(RUNTIME / (phase + suffix), sha(RUNTIME / (phase + suffix)))

repairs = []
for key in sorted(expectedIds):
    old, new = results["baseline"][key], results["candidate"][key]
    assert new["status"] == "PASS"
    if old["status"] == "FAIL":
        assert key[0] == main
        name = key[1]
        depth = int(name[0])
        unit = "vw" if ": vw " in name else "vh"
        history = name.rsplit(" ", 1)[1]
        expected = (24 if unit == "vw" else 12) if history == "hidden-only" else (46 if unit == "vw" else 26)
        observed = (30 if unit == "vw" else 15) if depth == 1 and history.startswith("hidden") else (24 if unit == "vw" else 12)
        assert old["message"] == f"assert_equals: first viewport-dependent value expected {expected} but got {observed}"
        repairs.append({"test": key[0], "name": name, "expected": expected, "observed": observed,
                        "group": "visible overlap114" if history == "visible-resize" else "hidden additional"})
assert collections.Counter(r["group"] for r in repairs) == {"visible overlap114": 8, "hidden additional": 12}
comparison = read(RUNTIME / "COMPARISON.json")
assert comparison["regressions"] == comparison["changed_failures"] == []
assert sorted(comparison["repaired"]) == sorted([[r["test"], r["name"]] for r in repairs])
for name in ["BEFORE.json", "COMPARISON.json"]:
    authenticate(RUNTIME / name, sha(RUNTIME / name))
(HERE / "PRELIMINARY-CHECK.json").write_text(json.dumps({
    "status": "PHASES_REVIEWED_RESTORATION_PENDING", "phases": phaseRecords,
    "repairs": repairs, "controls_preserved": 28, "restoration_verified": False,
    "live_native_or_binary_read": False, "references": pins}, indent=2) + "\n")
print(json.dumps({"status": "PHASES_REVIEWED_RESTORATION_PENDING", "repairs": len(repairs), "controls": 28}))
