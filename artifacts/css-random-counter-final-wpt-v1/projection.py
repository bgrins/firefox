from collections import Counter

PAGE = "/css/css-values/random-typed-parse-rollback.html"
OLD = "A successful number line-height parse keeps random index one"
NEW = "A successful number line-height parse keeps specified random index one"
ADDED = ('  const expected = getComputedStyle(reference).lineHeight;\n'
         '  assert_greater_than_equal(parseFloat(expected), 10, "Reference resolves against the font size");\n'
         '  assert_equals(getComputedStyle(target).lineHeight, expected, "Computed value");\n')


def require(value, message):
    if not value:
        raise RuntimeError(message)


def validate(old_policy, final_policy, old_body, final_body, original, candidate):
    require(old_body.count(ADDED) == 1 and old_body.count(OLD) == 1, "exact stronger callback")
    require(old_body.replace(ADDED, "").replace(OLD, NEW) == final_body, "only specified control projection")
    require(old_policy["tests"] == final_policy["tests"] and len(final_policy["tests"]) == 7, "same seven pages")
    for key in ("regression_subtests", "held_subtests"):
        require(old_policy[key] == final_policy[key], "unchanged " + key)
    targets = {page: [NEW if page == PAGE and n == OLD else n for n in names]
               for page, names in old_policy["target_subtests"].items()}
    require(targets == final_policy["target_subtests"], "one target name changed")
    require(sum(map(len, targets.values())) == 46 and sum(map(len, final_policy["regression_subtests"].values())) == 507, "exact target/regression counts")
    roster = dict(old_policy["regression_subtests"], **old_policy["target_subtests"], **old_policy["held_subtests"])
    identities = Counter((page, name) for page, names in roster.items() for name in names)
    for result in (original, candidate):
        require(result["complete"] is True and result["execution_preserved"] is True, "complete preserved historical run")
        require(Counter((r["test"], r["subtest"]) for r in result["rows"]) == identities, "exact historical553 roster")
        control = [r for r in result["rows"] if r["test"] == PAGE and r["subtest"] == OLD]
        require(len(control) == 1 and control[0]["status"] == "PASS", "historical stronger control passed")
    require(candidate["comparison_gate_passed"] is True, "paired comparison passed")
    require(all(r["status"] == "PASS" for r in candidate["rows"] if r["test"] in old_policy["target_subtests"]), "paired46 targets passed")
    require(candidate["regression_signature"] == original["regression_signature"], "historical regression signatures unchanged")
    return {"kind": "assertion_projection_only", "page": PAGE, "historical_control": OLD,
            "landing_control": NEW, "unchanged_subtest_identities": 552,
            "removed_assertions": 2, "raw_events_rewritten": False,
            "historical_assessment_relabelled": False, "requires_fresh_landing_execution": True}
