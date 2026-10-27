import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("length_validator", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def fixture():
    rows = []
    for binding, operation in v.IDENTITIES:
        observed, unit = (25, 2) if operation == "to-percentage" else (200, 5) if operation == "to-px" else (200, 2)
        specified = 50 if operation == "value" else observed
        sample = {"observed": observed, "unit": unit, "specified": specified}
        warm = {"host": [200, 100], "svg": [200, 100], "value": 100}
        rows.append({"binding": binding, "operation": operation, "warm": copy.deepcopy(warm), "first": copy.deepcopy(sample),
                     "repeated": copy.deepcopy(sample), "control": copy.deepcopy(sample), "reset": copy.deepcopy(warm),
                     "controlGeometry": {"host": [400, 100], "svg": [400, 100]},
                     "after": {"host": [400, 100], "svg": [400, 100], "value": 100 if operation == "to-percentage" else 200,
                               "specified": specified, "unit": unit},
                     "expected": observed, "calibrated": True, "stable": True, "matches": True})
    return {"compatMode": "CSS1Compat", "rows": rows}


checks = []
p = fixture()
assert v.validate(p)["counts"] == {"PASS": 6, "FAIL": 0, "UNCALIBRATED": 0}
checks.append("all-correct")
p = fixture()
for row in p["rows"]:
    if row["operation"] != "value":
        wrong = 100 if row["operation"] == "to-px" else 50
        row["first"]["observed"] = row["first"]["specified"] = wrong
        row["repeated"] = copy.deepcopy(row["first"])
        row["after"]["specified"] = wrong
        row["after"]["value"] = 100 if row["operation"] == "to-px" else 200
        row["matches"] = False
summary = v.validate(p)
assert summary["counts"] == {"PASS": 2, "FAIL": 4, "UNCALIBRATED": 0}
assert summary["calibrated"] == summary["stable"] == 6 and summary["getter_controls_pass"] == 2
checks.append("predicted-conversion-failures-are-observations")
p = fixture()
p["rows"][0]["warm"]["host"][0] = 199
p["rows"][0]["calibrated"] = False
assert v.validate(p)["counts"]["UNCALIBRATED"] == 1
checks.append("geometry-failure-inconclusive")
p = fixture()
p["rows"][0]["control"]["specified"] = 49
assert v.validate(p)["counts"]["UNCALIBRATED"] == 1
checks.append("reference-specified-units-independent-of-self-flag")
p = fixture()
p["rows"][0]["first"]["observed"] = 100
p["rows"][0]["matches"] = False
p["rows"][0]["stable"] = False
assert v.validate(p)["getter_controls_pass"] == 1
checks.append("getter-control-failure-detected")
mutations = {
    "duplicate-identity": lambda p: p["rows"][1].update(operation="value"),
    "missing-row": lambda p: p["rows"].pop(),
    "unexpected-key": lambda p: p["rows"][0].update(extra=1),
    "nonfinite-first": lambda p: p["rows"][0]["first"].update(observed=float("nan")),
    "nonfinite-after": lambda p: p["rows"][0]["after"].update(value=float("inf")),
    "boolean-number": lambda p: p["rows"][0]["first"].update(observed=True),
    "false-expected-factor": lambda p: p["rows"][1].update(expected=100),
    "numeric-flag": lambda p: p["rows"][0].update(calibrated=1),
    "false-match-flag": lambda p: p["rows"][0].update(matches=False),
    "bad-reset-schema": lambda p: p["rows"][0]["reset"].update(extra=1),
}
for name, mutate in mutations.items():
    p = fixture()
    mutate(p)
    try:
        v.validate(p)
    except ValueError:
        checks.append("reject-" + name)
    else:
        raise AssertionError(name)
for path in HERE.glob("*.py"):
    compile(path.read_text(), str(path), "exec")
print(json.dumps({"status": "PASS", "checks": checks, "count": len(checks),
                  "scope": "synthetic validation only; no browser or native execution",
                  "validator_sha256": hashlib.sha256((HERE / "validate.py").read_bytes()).hexdigest()}, indent=2))
