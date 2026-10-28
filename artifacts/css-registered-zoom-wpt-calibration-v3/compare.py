def need(value, message):
    if not value:
        raise ValueError(message)


def signatures(assessment, policy):
    rows = assessment["rows"]
    expected = {(test, name) for test, names in policy["target_subtests"].items() for name in names}
    result = {}
    for row in rows:
        key = (row["test"], row["subtest"])
        need(key in expected and key not in result, "unknown/duplicate comparison identity")
        need(row["status"] in ("PASS", "FAIL"), "comparison requires complete PASS/FAIL observations")
        result[key] = {"status":row["status"], "message_present":"message" in row, "message":row.get("message"),
                       "expected_present":"expected" in row, "expected":row.get("expected"),
                       "known_intermittent_present":"known_intermittent" in row,
                       "known_intermittent":row.get("known_intermittent")}
    need(set(result) == expected and len(result) == 56, "exact 56 comparison identities")
    return result


def compare(original, candidate, policy):
    need(original["complete"] and original["execution_preserved"] and candidate["complete"] and candidate["execution_preserved"], "complete preserved phases")
    for assessment in [original, candidate]:
        binding = assessment["run_binding"]
        need(binding["revision"] == policy["frozen_head"], "comparison HEAD")
        need(assessment["run_info"]["browser_build_id"] == binding["browser_build_id"], "phase BuildID binding")
    left_info, right_info = dict(original["run_info"]), dict(candidate["run_info"])
    left_info.pop("browser_build_id"); right_info.pop("browser_build_id")
    need(left_info == right_info, "non-BuildID run_info drift")
    left, right = signatures(original, policy), signatures(candidate, policy)
    counts = {"repaired":0, "new_failures":0, "unchanged_pass":0, "unchanged_fail":0, "changed_fail":0}
    comparisons = []
    for key in sorted(left):
        a,b = left[key], right[key]
        category = ("repaired" if a["status"] == "FAIL" and b["status"] == "PASS" else
                    "new_failures" if a["status"] == "PASS" and b["status"] == "FAIL" else
                    "unchanged_pass" if b["status"] == "PASS" else
                    "unchanged_fail" if a == b else "changed_fail")
        counts[category] += 1
        comparisons.append({"test":key[0],"subtest":key[1],"category":category,"signature_changed":a != b,"original":a,"candidate":b})
    return {"counts":counts,"rows":comparisons,"complete_comparison":True,"native_fix_acceptance":False,
            "limitation":"Failure messages include only the first failing assertion; a repaired test checks all assertions, while changed FAIL is not necessarily an improvement."}
