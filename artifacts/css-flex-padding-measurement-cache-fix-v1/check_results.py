import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_run(name):
    directory = HERE / name
    record = json.loads((directory / "RUN.json").read_text())
    events = [json.loads(line) for line in (directory / "raw.json").read_text().splitlines()]
    rows = [event for event in events if event.get("action") == "test_status"]
    ends = [event for event in events if event.get("action") == "test_end"]
    assert record["complete"] and record["before"] == record["after"]
    assert rows == record["rows"] and ends == record["harness"]
    assert sum(event.get("action") == "suite_end" for event in events) == 1
    return record, {(row["test"], row["subtest"]): row for row in rows}, ends


baseline, old, old_ends = load_run("baseline-wpt-v1")
candidate, new, new_ends = load_run("candidate-wpt-v1")
final, regressions, final_ends = load_run("final-regressions-v1")
assert len(old) == len(new) == 18 and old.keys() == new.keys()
expected_failures = {
    f"{group} baseline, percent padding, {change}"
    for group in ["first", "last"] for change in ["shrink", "grow"]
}
actual_failures = {key[1] for key, row in old.items() if row["status"] == "FAIL"}
assert actual_failures == expected_failures
assert baseline["exit"] == 1 and candidate["exit"] == final["exit"] == 0
assert all(row["status"] == "PASS" for row in new.values())
assert all(row["status"] == "PASS" for row in regressions.values())
assert all(row["status"] == "OK" for row in old_ends + new_ends)
assert len(old_ends) == len(new_ends) == 1
assert len(regressions) == 20 and len(final_ends) == 9
assert sum(row["status"] == "OK" for row in final_ends) == 2
assert sum(row["status"] == "PASS" for row in final_ends) == 7
for key, row in old.items():
    if row["status"] == "PASS":
        assert (row["status"], row.get("message")) == (
            new[key]["status"], new[key].get("message"))
for key, row in new.items():
    assert (row["status"], row.get("message")) == (
        regressions[key]["status"], regressions[key].get("message"))
test = "testing/web-platform/tests/css/css-flexbox/flexbox-baseline-percentage-padding-resize.html"
digest = hashlib.sha256((HERE / "wpt.html").read_bytes()).hexdigest()
assert all(record["before"][test] == digest for record in [baseline, candidate, final])
for record, filename in [(baseline, "before.cpp"), (candidate, "candidate.cpp"),
                         (final, "candidate-formatted.cpp")]:
    assert record["before"]["layout/generic/nsFlexContainerFrame.cpp"] == hashlib.sha256(
        (HERE / filename).read_bytes()).hexdigest()
print(json.dumps({"paired_cases": 18, "fixed": 4, "unchanged_controls": 14,
                  "final_subtests": 20, "final_reftests": 7, "final_harnesses": 2}))
