import json
from pathlib import Path


def assess(output, code, policy):
    assert code in (0, 1)
    expected = json.loads((Path(__file__).parent / "TARGET-SUBTESTS.json").read_bytes())
    events = [json.loads(line) for line in (output / "raw.jsonl").read_text().splitlines()]
    rows = [e for e in events if e.get("action") == "test_status"]
    ends = [e for e in events if e.get("action") == "test_end"]
    assert len(rows) == 4 and len(expected) == 4 and {e["subtest"] for e in rows} == set(expected)
    assert all(e["test"] == policy["target"] and e["status"] in ("PASS", "FAIL") for e in rows)
    assert len(ends) == 1 and ends[0]["test"] == policy["target"] and ends[0]["status"] == "OK"
    assert not any(e.get("action") in ("crash", "process_error") or (e.get("action") == "log" and e.get("level") == "ERROR") for e in events)
    by_name = {e["subtest"]: e for e in rows}
    assert by_name[expected[1]]["status"] == "PASS"
    failures = {
        expected[0]: 'assert_equals: z-index should be 0 expected "0" but got "1"',
        expected[2]: 'assert_equals: initial outer scope returns zero expected "0px" but got "10px"',
        expected[3]: 'assert_equals: initial outer scope returns zero expected "0px" but got "10px"',
    }
    for name, message in failures.items():
        row = by_name[name]
        if row["status"] == "FAIL":
            assert row.get("message") == message, (name, row.get("message"))
    return {"pass": sum(e["status"] == "PASS" for e in rows), "fail": sum(e["status"] == "FAIL" for e in rows), "complete_subtests": 4, "same_tree_host_control_passed": True, "dynamic_calibrations_precede_allowed_target_failures": True, "known_mismatches_are_observations": True, "native_fix_acceptance": False}
