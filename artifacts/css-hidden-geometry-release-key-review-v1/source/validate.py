import math


def summarize(observation):
    assert set(observation) == {"rows", "userAgent"}
    assert "Firefox/158." in observation["userAgent"]
    rows = observation["rows"]
    expected = {(nested, insertion, mode, hidden, api)
                for nested in (False, True) for insertion in ("append", "prepend")
                for mode in ("shrink", "no-shrink", "zero-sibling")
                for hidden in (False, True) for api in ("bounding", "offset")}
    assert isinstance(rows, list) and len(rows) == 48
    seen = set()
    differences, calibration_failures, repeated_changes = [], [], []
    def vector(value, size=2):
        return (isinstance(value, list) and len(value) == size and
                all(type(n) in (float, int) and math.isfinite(n) for n in value))
    for row in rows:
        assert set(row) == {"nested", "insertion", "mode", "hidden", "api", "stages"}
        assert type(row["nested"]) is bool and type(row["hidden"]) is bool
        key = tuple(row[k] for k in ("nested", "insertion", "mode", "hidden", "api"))
        assert key in expected and key not in seen
        seen.add(key)
        assert isinstance(row["stages"], list) and len(row["stages"]) == 5
        assert [s["phase"] for s in row["stages"]] == ["warm", "visibility", "insert", "remove", "show"]
        for stage in row["stages"]:
            assert set(stage) == {"phase", "outer", "first", "second", "third", "visible", "expected"}
            assert vector(stage["outer"], 3)
            assert all(vector(stage[k]) for k in ("first", "second", "third", "visible", "expected"))
            oracle = [50 if stage["phase"] == "insert" and row["mode"] == "shrink" else 100, 32]
            assert stage["expected"] == oracle
            item = {"configuration": key, **stage}
            if stage["visible"] != oracle:
                calibration_failures.append(item)
            if stage["first"] != stage["visible"]:
                differences.append(item)
            if not stage["first"] == stage["second"] == stage["third"]:
                repeated_changes.append(item)
    assert seen == expected
    return {"rows": 48, "stages": 240, "differences": differences,
            "calibration_failures": calibration_failures, "repeated_changes": repeated_changes}
