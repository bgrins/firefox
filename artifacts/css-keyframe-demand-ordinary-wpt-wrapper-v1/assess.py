from collections import Counter


def assess(events, code, tests, expected_failures, checks):
    rows = [e for e in events if e.get("action") == "test_status"]
    starts = [e for e in events if e.get("action") == "test_start"]
    ends = [e for e in events if e.get("action") == "test_end"]
    suites = [e for e in events if e.get("action") == "suite_start"]
    identities = [(r.get("test"), r.get("subtest")) for r in rows]
    config = {"expected_subtests": {test: [] for test in tests}, "reftests": []}
    errors = []
    if not checks.lifecycle(events, config):
        errors.append("incomplete or invalid ordered lifecycle")
    if len(starts) != len(tests) or len(ends) != len(tests):
        errors.append("each selected test must start and end exactly once")
    if len(identities) != len(set(identities)):
        errors.append("duplicate subtest identity")
    if any(not isinstance(r.get("subtest"), str) or r.get("test") not in tests
           or r.get("status") not in ("PASS", "FAIL") for r in rows):
        errors.append("invalid subtest identity or non-completed status")
    if any(not any(r["test"] == test for r in rows) for test in tests):
        errors.append("selected test has no reported subtests")
    if any(e.get("status") != "OK" or e.get("expected", "OK") != "OK"
           or e.get("known_intermittent") for e in ends):
        errors.append("non-OK testharness completion")
    run_info = suites[0].get("run_info") if len(suites) == 1 else None
    if not isinstance(run_info, dict) or not {"os", "debug"} <= set(run_info):
        errors.append("missing platform/build run_info")
    faults = checks.infrastructure_faults(events)
    if faults:
        errors.append("infrastructure faults")
    if not checks.exit_matches_results(code, rows + ends):
        errors.append("exit status inconsistent with observed outcomes")
    observed = {(r["test"], r["subtest"]): r for r in rows}
    for test, name in expected_failures:
        row = observed.get((test, name))
        if row is None or row.get("expected", row["status"]) != "FAIL":
            errors.append("expected-FAIL metadata missing: " + name)
    unexpected = [e for e in rows + ends
                  if e["status"] != e.get("expected", e["status"])
                  and e["status"] not in e.get("known_intermittent", [])]
    return {
        "complete": not errors, "errors": errors, "run_info": run_info,
        "observed_subtest_count": len(rows), "rows": rows, "starts": starts, "ends": ends,
        "per_test": {test: {"subtests": dict(Counter(r["status"] for r in rows if r["test"] == test)),
                            "harness": [e["status"] for e in ends if e["test"] == test]}
                     for test in tests},
        "unexpected": unexpected, "infrastructure_faults": faults,
        "regression_gate_passed": not errors and not unexpected and code == 0,
        "subtest_cardinality_policy": "Observed identities only; no predeclared count or exact completeness claim within each test body",
        "oracle_caveat": "attr-cycle retains its existing upstream oracle; success does not establish current-ED conformance",
    }
