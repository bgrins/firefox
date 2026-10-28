import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("breadth_validation", HERE / "validate.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
cases = validation.CASES
rows = []
for case in cases:
    snapshots = []
    for step in case["snapshots"]:
        actual = {"value": "", "number": None, "fontSize": "", "width": "200px"}
        actual.update(step["expected"])
        snapshots.append({"label": step["label"], "actual": actual})
    rows.append({"id": case["id"], "registrationErrors": [], "snapshots": snapshots})
value = {"observation": {"userAgent": "synthetic", "queryOrder": ["parentFontSize", "value", "number", "fontSize", "width"], "rows": rows}}
original = validation.summarize(value)
assert not original["calibration_failures"] and not original["calibrated_disagreements"]
changed = copy.deepcopy(value)
lookup = {row["id"]: row for row in changed["observation"]["rows"]}
lookup["angle:direct:ready-unused"]["snapshots"][0]["actual"]["fontSize"] = "100px"
candidate = validation.summarize(changed)
assert candidate["calibrated_disagreements"] == ["angle:direct:ready-unused"]
assert len(validation.compare(original, candidate)["changed_rows"]) == 1
lookup["angle:direct:literal"]["snapshots"][0]["actual"]["fontSize"] = "100px"
blocked = validation.summarize(changed)
assert "angle:direct:literal" in blocked["calibration_failures"]
assert "angle:direct:ready-unused" not in blocked["calibrated_disagreements"]
assert next(row for row in blocked["rows"] if row["id"] == "angle:direct:ready-unused")["blocked_by_calibration"] == ["angle:direct:literal"]
changed = copy.deepcopy(value)
lookup = {row["id"]: row for row in changed["observation"]["rows"]}
lookup["integer:math-control:math"]["snapshots"][0]["actual"]["value"] = "3"
lookup["integer:provider-math:math"]["snapshots"][0]["actual"]["number"] = "3"
blocked = validation.summarize(changed)
assert "integer:provider-math:math" not in blocked["calibrated_disagreements"]
assert next(row for row in blocked["rows"] if row["id"] == "integer:provider-math:math")["blocked_by_calibration"] == ["integer:math-control:math"]
changed = copy.deepcopy(value)
changed["observation"]["rows"][1]["registrationErrors"] = [{"name":cases[1]["names"]["value"], "error":"unsupported"}]
assert not validation.summarize(changed)["calibrated_disagreements"]
rejected = []
for index in range(len(cases)):
    invalid = copy.deepcopy(value)
    invalid["observation"]["rows"].pop(index)
    try:
        validation.summarize(invalid)
    except AssertionError:
        rejected.append(cases[index]["id"])
    else:
        raise AssertionError("Missing row accepted")
invalid = copy.deepcopy(value)
invalid["observation"]["rows"][-1]["snapshots"].pop()
try:
    validation.summarize(invalid)
except AssertionError:
    rejected.append("missing mutation snapshot")
else:
    raise AssertionError("Incomplete mutation accepted")
for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
previous = ROOT / "artifacts/css-registered-number-self-font-observation-v1"
assert (HERE / "run.py").read_text() == (previous / "run.py").read_text().replace("css-registered-number-self-font-runtime-", "css-registered-numeric-breadth-runtime-")
assert (HERE / "POLICY.json").read_bytes() == (previous / "POLICY.json").read_bytes()
for path in HERE.glob("*.py"):
    ast.parse(path.read_text(), filename=str(path))
print(json.dumps({"cases":len(cases), "all_proposed_oracles_synthetic_control":True,
                  "failed_literal_calibration_blocks_disagreement_classification":True,
                  "failed_direct_math_calibration_blocks_provider_math_classification":True,
                  "unsupported_registration_not_classified":True,
                  "changed_values_retained_without_acceptance":True, "rejected_incomplete_controls":len(rejected),
                  "runner_changed_only_owned_output_prefix":True, "source_role_policy_unchanged":True,
                  "browser_executed":False, "server_started":False, "native_execution":False}, indent=2))
