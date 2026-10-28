def summarize(value):
    assert isinstance(value, dict) and set(value) == {"observation", "calibrations"}
    observation = value["observation"]
    assert isinstance(observation["userAgent"], str) and observation["userAgent"]
    rows = observation["rows"]
    expected = [(order, query) for order in ("number-first", "font-first")
                for query in ("number-first", "font-first")]
    assert [(row["order"], row["query"]) for row in rows] == expected
    for row in rows:
        assert all(isinstance(row[key], str) for key in ("first", "number", "fontSize", "width"))
    calibrations = value["calibrations"]
    assert [(row["id"], row["expected"]) for row in calibrations] == [("literal-number", "5"), ("true-var-self-cycle", "3")]
    for row in calibrations:
        assert all(isinstance(row[key], str) for key in ("number", "fontSize", "width"))
    return {"structure_complete": True, "userAgent": observation["userAgent"], "rows": rows,
            "calibrations": calibrations,
            "calibration_discrepancies": [row["id"] for row in calibrations
                if row["number"] != row["expected"] or
                   row["fontSize"] != row["expected"] + "px" or row["width"] != row["expected"] + "px"],
            "normative_verdict": "not evaluated", "native_fix_acceptance": False}


def compare(original, candidate):
    assert [(row["order"], row["query"]) for row in original["rows"]] == [(row["order"], row["query"]) for row in candidate["rows"]]
    changes = []
    for before, after in zip(original["rows"], candidate["rows"]):
        fields = {key: {"original": before[key], "candidate": after[key]}
                  for key in ("first", "number", "fontSize", "width") if before[key] != after[key]}
        if fields:
            changes.append({"order": before["order"], "query": before["query"], "changed_values": fields})
    return {"changed_rows": changes, "calibrations_original": original["calibrations"],
            "calibrations_candidate": candidate["calibrations"],
            "normative_verdict": "not evaluated", "native_fix_acceptance": False}
