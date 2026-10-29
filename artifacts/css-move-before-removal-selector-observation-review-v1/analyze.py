import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-move-before-removal-selector-browser-runtime-1"
FIXTURE = ROOT / "artifacts/css-move-before-removal-selector-probe-v1"
def read(path):
    return json.loads(path.read_bytes())
raw = [json.loads(line) for line in (RUNTIME / "raw.jsonl").read_text().splitlines()]
rows = [e for e in raw if e.get("action") == "test_status"]
expected = read(FIXTURE / "EXPERIMENT.json")["target_subtests"]
assert Counter((r["test"], r["subtest"]) for r in rows) == Counter((p, n) for p, ns in expected.items() for n in ns)
assert Counter(r["status"] for r in rows) == {"PASS": 9, "FAIL": 9}
ends = [e for e in raw if e.get("action") == "test_end"]
assert len(ends) == 1 and ends[0]["status"] == "OK"
children = {
    "first-child": ["moved", "target"], "last-child": ["target", "moved"],
    "only-child": ["target", "moved"], "nth-child(2)": ["moved", "target"],
    "adjacent-sibling": ["moved", "target"], "general-sibling": ["moved", "spacer", "target"],
    "parent-has": ["moved", "target"], "parent-empty": ["moved"],
    "sibling-index-moving-first": ["moved", "target"]}
widths = {name: [10, 30, 10] if name in ("first-child", "last-child", "only-child", "parent-empty") else [20, 10, 20] if name == "sibling-index-moving-first" else [30, 10, 30] for name in children}
failures = []
for row in rows:
    if row["status"] == "PASS":
        assert row["subtest"].startswith("appendChild: old-parent ")
        continue
    assert row["message"].startswith("assert_equals: Old-parent computed width; ")
    message = row["message"]
    data, _ = json.JSONDecoder().raw_decode(message[message.index("{"):])
    name = data["name"]
    assert data["method"] == "moveBefore" and row["subtest"] == "moveBefore: old-parent " + name
    assert [s["phase"] for s in data["snapshots"]] == ["initial", "moved", "restored"]
    for i, snapshot in enumerate(data["snapshots"]):
        child_ids = [n for n in children[name] if n != "moved"] if i == 1 else children[name]
        assert snapshot["sourceChildren"] == child_ids
        assert snapshot["destinationChildren"] == (["moved"] if i == 1 else [])
        assert all(snapshot[k] for k in ("retainedMoved", "retainedTarget", "connected", "subjectParent"))
        assert snapshot["literalSpecified"] == snapshot["literalComputed"] == str(widths[name][i]) + "px"
        assert snapshot["literalGeometry"] == widths[name][i]
        assert snapshot["actual"] == snapshot["repeat"] == str(widths[name][0]) + "px"
        assert snapshot["geometry"] == widths[name][0] and snapshot["animations"] == 0
        if name == "sibling-index-moving-first":
            assert snapshot["selectorMatches"] is None and snapshot["subjectIndex"] == (1 if i == 1 else 2)
        else:
            assert snapshot["selectorMatches"] == (widths[name][i] == 30)
            expected_index = None if name.startswith("parent-") else child_ids.index("target") + 1
            assert snapshot["subjectIndex"] == expected_index
    failures.append({"case": name, "actual_widths": [s["actual"] for s in data["snapshots"]], "expected_widths": widths[name], "selector_matches": [s["selectorMatches"] for s in data["snapshots"]]})
assert {f["case"] for f in failures} == set(children)
result = read(RUNTIME / "RESULT.json")
driver = read(RUNTIME / "OBSERVATION-DRIVER.json")
assert result["success"] and result["preservation_verified"] and result["execution_error"] is None and result["exit"] == 1
assert driver["success"] and driver["error"] is None and driver["preservation_error"] is None and driver["owned_processes"] == {}
assert read(RUNTIME / "PRE.json") == read(RUNTIME / "POST.json")
assert read(RUNTIME / "APPLICATION-METADATA.json") == read(RUNTIME / "APPLICATION-METADATA-POST.json")
cleanup = read(RUNTIME / "CLEANUP.json")
assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
terminal = read(RUNTIME / "ROOT-REPORTED-TERMINAL.json")
assert terminal["session_id"] == 66118 and terminal["terminal_receipt"] == "e3ad5f" and terminal["exit_code"] == 0
manifest = read(RUNTIME / "FILES.json")
for name, value in manifest.items():
    digest = value["sha256"] if isinstance(value, dict) else value
    assert hashlib.sha256((RUNTIME / name).read_bytes()).hexdigest() == digest, name
paths = [RUNTIME / n for n in ("raw.jsonl", "RESULT.json", "OBSERVATION-DRIVER.json", "PRE.json", "POST.json", "APPLICATION-METADATA.json", "APPLICATION-METADATA-POST.json", "CLEANUP.json", "ROOT-REPORTED-TERMINAL.json", "FILES.json")]
paths += [FIXTURE / "removal-selectors.html", FIXTURE / "FILES.json"]
report = {"ordinary_pass": 9, "move_before_fail": 9, "ok_endings": 1, "failure_snapshots_checked": 27, "calibration_failures": 0, "stale_moved_phase_records": 9, "known_family_not_nine_bugs": True, "native_acceptance": False, "failures": failures, "references": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
print(json.dumps(report, indent=2, sort_keys=True))
