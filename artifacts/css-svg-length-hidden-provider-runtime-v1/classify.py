def classify(rows, names, need):
    need(len(rows) == 4 and [r["subtest"] for r in rows] == names, "four ordered identities")
    failures = []
    for row in rows:
        need(row["status"] in ("PASS", "FAIL"), "completed assertion outcome")
        if row["status"] == "FAIL":
            need(row["subtest"] == "vw: hidden iframe provider" and row.get("message") ==
                 "assert_equals: first value under current-viewport hypothesis expected 40 but got 20",
                 "calibration/control/later/unpredicted failure")
            failures.append({"subtest": row["subtest"], "value": 20, "expected_hypothesis": 40,
                             "message": row["message"]})
    return {"calibrated": 4, "counts": {s: sum(r["status"] == s for r in rows) for s in ("PASS", "FAIL")},
            "first_read_mismatches": failures, "rows": rows,
            "failed_first_assertion_stops_repeat_and_post_query_assertions": True,
            "window_observation_array_exported": False, "native_flush_branch_observed": False,
            "normative_verdict": "INCONCLUSIVE", "accepted_bug": False}
