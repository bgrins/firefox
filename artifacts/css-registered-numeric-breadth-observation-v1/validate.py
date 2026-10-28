import json
from pathlib import Path

CASES = json.loads((Path(__file__).parent / "CASES.json").read_text())


def summarize(value):
    assert isinstance(value, dict) and set(value) == {"observation"}
    observation = value["observation"]
    assert isinstance(observation["userAgent"], str) and observation["userAgent"]
    assert observation["queryOrder"] == ["parentFontSize", "value", "number", "fontSize", "width"]
    rows = observation["rows"]
    assert [row["id"] for row in rows] == [case["id"] for case in CASES]
    matches = {}
    summaries = []
    for row, case in zip(rows, CASES):
        assert isinstance(row["registrationErrors"], list)
        for error in row["registrationErrors"]:
            assert isinstance(error["name"], str) and isinstance(error["error"], str)
        assert [step["label"] for step in row["snapshots"]] == [step["label"] for step in case["snapshots"]]
        discrepancies = []
        for actual_step, expected_step in zip(row["snapshots"], case["snapshots"]):
            actual = actual_step["actual"]
            assert all(isinstance(actual[key], str) for key in ("value", "fontSize", "width"))
            assert isinstance(actual["number"], str) if case["names"]["number"] else actual["number"] is None
            for key, expected in expected_step["expected"].items():
                if actual[key] != expected:
                    discrepancies.append({"step": actual_step["label"], "property": key,
                                          "expected": expected, "actual": actual[key]})
        matches[case["id"]] = not row["registrationErrors"] and not discrepancies
        summaries.append(dict(row, kind=case["kind"], mode=case["mode"], syntax=case["syntax"], discrepancies=discrepancies))
    by_id = {row["id"]: row for row in summaries}
    for case in CASES:
        blocked = [name for name in case["requiresCalibration"] if not matches[name]]
        if by_id[case["id"]]["registrationErrors"]:
            blocked.append("own registration failed")
        by_id[case["id"]]["blocked_by_calibration"] = blocked
        by_id[case["id"]]["proposed_oracle_matches"] = matches[case["id"]]
    calibrations = [case["id"] for case in CASES if case["mode"] == "literal" or case["kind"] == "math-control"]
    return {"structure_complete": True, "userAgent": observation["userAgent"], "rows": summaries,
            "calibration_failures": [name for name in calibrations if not matches[name]],
            "calibrated_disagreements": [row["id"] for row in summaries if row["id"] not in calibrations
                and not row["blocked_by_calibration"] and not row["proposed_oracle_matches"]],
            "classification": "diagnostic observations only; no dependency bug automatically classified",
            "normative_verdict": "not evaluated", "native_fix_acceptance": False}


def compare(original, candidate):
    assert [row["id"] for row in original["rows"]] == [row["id"] for row in candidate["rows"]]
    changes = []
    for before, after in zip(original["rows"], candidate["rows"]):
        fields = {key: {"original": before[key], "candidate": after[key]}
                  for key in ("registrationErrors", "snapshots", "blocked_by_calibration", "proposed_oracle_matches")
                  if before[key] != after[key]}
        if fields:
            changes.append({"id": before["id"], "changes": fields})
    return {"changed_rows": changes, "calibration_failures_original": original["calibration_failures"],
            "calibration_failures_candidate": candidate["calibration_failures"],
            "normative_verdict": "not evaluated", "native_fix_acceptance": False}
