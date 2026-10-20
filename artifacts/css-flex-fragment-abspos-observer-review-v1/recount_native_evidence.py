#!/usr/bin/env python3
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "native-candidate-evidence"


def fields(line):
    return dict(item.split("=", 1) for item in line.split() if "=" in item)


def main():
    trace = (ROOT / "css-flex-overflow-external-resize-trace-v1/project/browser.log").read_text()
    mark = None
    ancestry = None
    after = {}
    joined = []
    for line in trace.splitlines():
        if line.startswith("COLUMN_TRACE after"):
            row = fields(line)
            after[row["child"]] = row
        elif line.startswith("COLUMN_TRACE mark"):
            mark = fields(line)
            assert after[mark["pif"]]["next"] == "1"
        elif line.startswith("OC_ANCESTRY"):
            ancestry = fields(line)
            assert ancestry["parent"] == mark["child"]
        elif line.startswith("OC_TRACE pre"):
            row = fields(line)
            assert row["parent"] == ancestry["flex"]
            assert all(row[k] == "1" for k in ["pd", "all", "dirty"])
            assert row["ir"] == "0" and row["br"] == "1" and row["rel"] == "0"
            assert row["exceeds"] == "-1"
            joined.append({"previous_column_requested_reflow": True,
                           "column_previously_clean": mark["dirty"] == "0",
                           "column_child_equals_flex_parent": True,
                           "old_width": int(row["oldC"]), "final_width": int(row["newC"])})
        elif line.startswith("OC_TRACE branch="):
            assert "branch=reflow" in line
    assert len(joined) == 24
    assert sum(row["column_previously_clean"] for row in joined) == 18

    wpt = ROOT / "css-flex-overflow-container-fix-v1"
    results = []
    for kind in ["baseline", "candidate"]:
        statuses = {}
        for line in (wpt / kind / "raw.json").read_text().splitlines():
            event = json.loads(line)
            if event.get("action") == "test_status":
                key = (event["test"], event["subtest"])
                assert key not in statuses
                statuses[key] = event["status"]
        assert len(statuses) == 336
        results.append(statuses)
    assert results[0].keys() == results[1].keys()
    pairs = Counter((results[0][key], results[1][key]) for key in results[0])
    assert pairs == {("FAIL", "PASS"): 112, ("PASS", "PASS"): 224}
    assert all("vertical-rl" in key[1] for key, value in results[0].items() if value == "FAIL")
    regression = ROOT / "css-flex-overflow-regression-v1"
    file_results = []
    for kind in ["baseline", "candidate"]:
        statuses = {}
        for line in (regression / kind / "raw.json").read_text().splitlines():
            event = json.loads(line)
            if event.get("action") == "test_end":
                assert event["test"] not in statuses
                statuses[event["test"]] = event["status"]
        assert len(statuses) == 35
        file_results.append(statuses)
    assert file_results[0].keys() == file_results[1].keys()
    existing = {key: status for key, status in file_results[0].items()
                if "flexbox-overflow-container-final-position.html" not in key}
    assert len(existing) == 34
    assert all(file_results[1][key] == value for key, value in existing.items())
    assert Counter(existing.values()) == {"PASS": 24, "FAIL": 10}
    modes = ROOT / "css-flex-overflow-child-mode-runtime-v1"
    mode_rows = {kind: json.loads((modes / kind / "RESULT.json").read_text())["observations"][0]["rows"]
                 for kind in ["release", "baseline", "candidate"]}
    assert mode_rows["release"] == mode_rows["baseline"]
    assert all(len(rows) == 30 for rows in mode_rows.values())
    unchanged_modes = 0
    same_mode_correct = 0
    separate_block_omission = 0
    for before, after in zip(mode_rows["baseline"], mode_rows["candidate"]):
        for key in ["childMode", "flexDirection", "inlineOffset", "blockOffset"]:
            assert before[key] == after[key]
        assert before["blockReference"] == after["blockReference"]
        if before["childMode"] != "vertical-rl":
            assert before["actual"] == after["actual"]
            unchanged_modes += 1
        elif before["blockOffset"] == 0:
            expected = [[i * 100 + before["inlineOffset"], 0, 100, 160] for i in range(4)]
            assert after["actual"]["descendants"] == expected
            same_mode_correct += 1
        else:
            expected = [[i * 100, before["blockOffset"] if i == 0 else 0, 100, 160]
                        for i in range(4)]
            assert after["actual"]["descendants"] == expected
            assert before["actual"]["descendants"][1][1] == 0
            separate_block_omission += 1
    assert (unchanged_modes, same_mode_correct, separate_block_omission) == (20, 6, 4)
    print(json.dumps({"column_oc_identity_joins": joined,
                      "existing_regression_files": dict(Counter(existing.values())),
                      "child_modes": {"unchanged_opposite_orthogonal": unchanged_modes,
                         "same_mode_zero_inline_correct": same_mode_correct,
                         "preexisting_block_offset_omission": separate_block_omission},
                      "paired_wpt": [{"before": a, "after": b, "count": n}
                                     for (a, b), n in sorted(pairs.items())]}, indent=2))


if __name__ == "__main__":
    main()
