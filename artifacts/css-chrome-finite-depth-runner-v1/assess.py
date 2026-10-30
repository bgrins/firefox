import json


def assess(events, policy, exit_code):
    errors = []
    def require(value, message):
        if not value:
            errors.append(message)
    starts = [e for e in events if e.get("action") == "suite_start"]
    finishes = [e for e in events if e.get("action") == "suite_end"]
    begins = [e for e in events if e.get("action") == "test_start"]
    rows = [e for e in events if e.get("action") == "test_status"]
    ends = [e for e in events if e.get("action") == "test_end"]
    require(len(starts) == len(finishes) == len(begins) == len(ends) == 1, "exact suite/test lifecycle")
    require(len(rows) == 4 and {e.get("subtest") for e in rows} == set(policy["expected_names"]), "exact four callback roster")
    require(all(e.get("test") == policy["page"] for e in rows + begins + ends), "exact page")
    require(all(e.get("status") in ("PASS", "FAIL") for e in rows), "ordinary callback outcomes")
    require(all(e.get("status") == "OK" for e in ends), "OK test ending")
    require(not any(e.get("action") in ("crash", "valgrind_error") or
                    (e.get("action") == "log" and e.get("level") in ("ERROR", "CRITICAL")) for e in events), "infrastructure errors")
    if len(starts) == 1:
        info = starts[0].get("run_info", {})
        require(info.get("product") == "chrome" and info.get("browser_version") == policy["version"], "Chrome run_info/version")
    if len(starts) == len(finishes) == len(begins) == len(ends) == 1 and len(rows) == 4:
        positions = [events.index(starts[0]), events.index(begins[0]), *[events.index(e) for e in rows], events.index(ends[0]), events.index(finishes[0])]
        require(positions == sorted(positions) and len(set(positions)) == 8, "ordered lifecycle")
    require(all(e.get("expected", "PASS") == "PASS" and e.get("known_intermittent", []) == [] for e in rows), "no expected failures or intermittents")
    require(all(e.get("expected", "OK") == "OK" and e.get("known_intermittent", []) == [] for e in ends), "no expected ending failure")
    failures = sum(e.get("status") == "FAIL" for e in rows)
    require(exit_code == (1 if failures else 0), "child exit agrees with raw outcomes")
    return {"complete": not errors, "errors": errors, "rows": rows, "ends": ends,
            "passes": sum(e.get("status") == "PASS" for e in rows), "failures": failures,
            "browser_exit": exit_code, "all_callbacks_pass": not failures and not errors,
            "numeric_or_cycle_policy_inferred": False}


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
