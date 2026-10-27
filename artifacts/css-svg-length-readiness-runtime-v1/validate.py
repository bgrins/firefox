import math

IDENTITIES = [(binding, operation) for binding in ("scalar", "list")
              for operation in ("value", "to-px", "to-percentage")]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def fields(value, keys, name):
    need(type(value) is dict and set(value) == set(keys), name + " schema")


def dimensions(value, name):
    need(type(value) is list and len(value) == 2 and all(number(n) for n in value), name + " finite dimensions")


def geometry(value, name, has_value=False):
    fields(value, ["host", "svg"] + (["value"] if has_value else []), name)
    dimensions(value["host"], name + " host")
    dimensions(value["svg"], name + " svg")
    if has_value:
        need(number(value["value"]), name + " finite value")


def sample(value, name):
    fields(value, ["observed", "unit", "specified"], name)
    need(number(value["observed"]) and number(value["specified"]), name + " finite values")
    need(type(value["unit"]) is int and 0 <= value["unit"] <= 10, name + " SVG unit")


def validate(payload):
    fields(payload, ["compatMode", "rows"], "payload")
    need(payload["compatMode"] == "CSS1Compat" and type(payload["rows"]) is list and len(payload["rows"]) == 6,
         "standards mode/six rows")
    rows = []
    for raw, (binding, operation) in zip(payload["rows"], IDENTITIES):
        fields(raw, ["binding", "operation", "warm", "first", "repeated", "after", "controlGeometry", "control",
                     "reset", "expected", "calibrated", "stable", "matches"], "row")
        need(raw["binding"] == binding and raw["operation"] == operation, "ordered identity")
        for field in ("calibrated", "stable", "matches"):
            need(type(raw[field]) is bool, "boolean " + field)
        need(number(raw["expected"]), "finite payload expectation")
        geometry(raw["warm"], "warm", True)
        geometry(raw["reset"], "reset", True)
        geometry(raw["controlGeometry"], "control geometry")
        for field in ("first", "repeated", "control"):
            sample(raw[field], field)
        after = raw["after"]
        fields(after, ["host", "svg", "value", "specified", "unit"], "after")
        dimensions(after["host"], "after host")
        dimensions(after["svg"], "after svg")
        need(number(after["value"]) and number(after["specified"]) and type(after["unit"]) is int
             and 0 <= after["unit"] <= 10, "after finite values/unit")
        expected_observed = 100 / 400 * 100 if operation == "to-percentage" else 50 / 100 * 400
        expected_unit = 5 if operation == "to-px" else 2
        expected_specified = 50 if operation == "value" else expected_observed
        expected_resolved = 100 if operation == "to-percentage" else 200
        expected = {"observed": expected_observed, "unit": expected_unit, "specified": expected_specified}
        warm = {"host": [200, 100], "svg": [200, 100], "value": 100}
        calibration = {
            "warm": raw["warm"] == warm,
            "updated_geometry": after["host"] == after["svg"] == [400, 100],
            "reference_geometry": raw["controlGeometry"] == {"host": [400, 100], "svg": [400, 100]},
            "reference_values": raw["control"] == expected,
            "reset": raw["reset"] == warm,
        }
        calibrated = all(calibration.values())
        stable = raw["first"] == raw["repeated"]
        first_matches = raw["first"] == expected
        after_matches = (after["value"] == expected_resolved and after["specified"] == expected_specified
                         and after["unit"] == expected_unit)
        need(raw["expected"] == expected_observed, "payload expectation disagrees with independent arithmetic")
        # Source fixture's calibrated flag omits reference specified-units; our gate is stricter.
        source_calibration = (calibration["warm"] and calibration["updated_geometry"] and calibration["reference_geometry"]
                              and raw["control"]["observed"] == expected_observed
                              and raw["control"]["unit"] == expected_unit and calibration["reset"])
        need(raw["calibrated"] == source_calibration and raw["stable"] == stable
             and raw["matches"] == (raw["first"]["observed"] == expected_observed and raw["first"]["unit"] == expected_unit),
             "payload self-flags disagree with raw values")
        status = "UNCALIBRATED" if not calibrated else "PASS" if stable and first_matches and after_matches else "FAIL"
        rows.append({"binding": binding, "operation": operation, "calibration": calibration, "calibrated": calibrated,
                     "stable": stable, "expected": expected, "expected_after_value": expected_resolved,
                     "first": raw["first"], "repeated": raw["repeated"], "after": after,
                     "first_matches": first_matches, "after_matches": after_matches, "status": status})
    return {"rows": rows, "calibrated": sum(r["calibrated"] for r in rows), "stable": sum(r["stable"] for r in rows),
            "getter_controls_pass": sum(r["status"] == "PASS" for r in rows if r["operation"] == "value"),
            "counts": {s: sum(r["status"] == s for r in rows) for s in ("PASS", "FAIL", "UNCALIBRATED")},
            "expectation_source": "independent 200→400 viewport arithmetic; fixed pinned fixture has no viewBox"}
