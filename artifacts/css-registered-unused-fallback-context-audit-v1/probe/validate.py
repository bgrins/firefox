def summarize(value):
    names = ["direct", "valid-primary-no-fallback", "valid-primary-px-fallback",
             "valid-primary-em-fallback", "used-em-fallback-cycle", "direct-em-cycle",
             "inherited-provider-unused-em", "number-unused-em", "universal-unused-em",
             "inherited-computed-length", "provider-unused-em"]
    assert isinstance(value["userAgent"], str) and value["userAgent"]
    assert value["registrationRules"] == ["CSSPropertyRule"] * 4
    rows = value["rows"]
    assert [row["id"] for row in rows] == names
    for row in rows:
        assert row["observed"] == row["repeat"]
        assert isinstance(row["computed"], str)
    return {"userAgent": value["userAgent"], "rows": rows,
            "differences_from_short_circuit_hypothesis": [row["id"] for row in rows if row["observed"] != row["expected"]],
            "calibration_failures": [row["id"] for row in rows if row.get("calibration") and row["observed"] != row["expected"]]}
