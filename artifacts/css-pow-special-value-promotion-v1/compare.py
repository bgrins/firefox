def validate_completed_assessments(original, candidate, comparison, signature):
    expected = {(test, name) for test, names in comparison["expected_subtests"].items() for name in names}
    targets = {(test, name) for test, names in comparison["target_subtests"].items() for name in names}
    assert len(expected) == 147 and len(targets) == 18 and targets <= expected
    controls = expected - targets
    assert len(controls) == 129 and len(comparison["expected_subtests"]) == 2
    for assessment in (original, candidate):
        assert assessment["complete"] and assessment["errors"] == [] and assessment["fixture_setup_errors"] == []
        assert assessment["observed_subtest_count"] == len(assessment["rows"]) == 147
        assert {(row["test"], row["subtest"]) for row in assessment["rows"]} == expected
        assert len(assessment["ends"]) == 2 and all(end["status"] == "OK" for end in assessment["ends"])
        assert {end["test"] for end in assessment["ends"]} == set(comparison["expected_subtests"])
        assert len(assessment["regression_signature"]) == 131
    assert candidate["comparison_gate_passed"] and candidate["comparison_errors"] == []
    assert candidate["regression_signature"] == original["regression_signature"]
    old_rows = {(row["test"], row["subtest"]): row for row in original["rows"]}
    new_rows = {(row["test"], row["subtest"]): row for row in candidate["rows"]}
    assert all(new_rows[key]["status"] == "PASS" for key in targets)
    assert all(row["status"] == "PASS" for row in candidate["rows"]
               if row["test"] in comparison["candidate_required_pass_pages"])
    assert all(signature(new_rows[key]) == signature(row) for key, row in old_rows.items()
               if key in controls or row["status"] == "PASS")
    assert {end["test"]: signature(end) for end in candidate["ends"]} == {end["test"]: signature(end) for end in original["ends"]}

