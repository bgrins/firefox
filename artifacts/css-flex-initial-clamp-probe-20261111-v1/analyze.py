import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
events = [json.loads(line) for line in (HERE / "raw.log").read_text().splitlines()]
rows = [json.loads(e["message"].split("CLAMP-PROBE ",1)[1]) for e in events if e.get("message", "").startswith("CLAMP-PROBE ")]
expected = json.loads((HERE / "CASES.json").read_text())
assert len(rows) == len(expected) == 36
assert [r["id"] for r in rows] == [r["id"] for r in expected]
assert len({r["id"] for r in rows}) == 36
for row, case in zip(rows, expected):
    assert row["expected"] == case
    assert row["size"] == case["size"]
failed = [r for r in rows if r["clamp"] != r["expected"]["clamp"]]
assert {r["id"] for r in failed} == {d + "-auto-" + c for d in ["column", "column-reverse"] for c in ["below-max", "below-min", "equal-max"]}
assert all(r["clamp"] == "clamped_to_max" and r["base"] == 20 and r["delta"] == 0 for r in failed)
statuses = [e for e in events if e["action"] == "test_status"]
assert len(statuses) == 72
assert sum(e["status"] == "PASS" for e in statuses) == 66
assert sum(e["status"] == "FAIL" for e in statuses) == 6
ends = [e for e in events if e["action"] == "test_end"]
assert len(ends) == 1 and ends[0]["status"] == "FAIL"
command = json.loads((HERE / "COMMANDS.json").read_text())
assert len(command) == 1 and command[0]["exit"] == 1
assert command[0]["pgid"] == 22968 and not command[0]["safe_cleanup"]
absence = json.loads((HERE / "ABSENCE-FOLLOWUP.json").read_text())
assert absence["pgid"] == 22968 and absence["killpg_absent"] and not absence["ps_matches"]
assert json.loads((HERE / "RESTORED.json").read_text())["status"] == "PASS"
for name, expected_hash in json.loads((HERE / "BEFORE.json").read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected_hash, name
assert not (ROOT / "dom/flex/test/chrome/test_flex_initial_clamp_probe.html").exists()
app = [json.loads(e["message"].split("PROBE-APP ",1)[1]) for e in events if e.get("message", "").startswith("PROBE-APP ")]
assert len(app) == 1
print(json.dumps({"status":"REPRODUCED", "cases":36, "correct_used_sizes":36,"clamp_mismatches":failed,"assertions":{"PASS":66,"FAIL":6},"harness_test_outcome":"FAIL", "application":app[0],"lifecycle":"Original wrapper inspection refusal preserved; separate fresh absence established; exact temporary edits restored"},indent=2))
