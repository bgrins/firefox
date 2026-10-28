import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
validation = load("validation", HERE / "validate.py")
runner = load("runner_without_main", HERE / "run.py")
rows = [{"order": order, "query": query, "first": "19", "number": "19", "fontSize": "19px", "width": "19px"}
        for order in ("number-first", "font-first") for query in ("number-first", "font-first")]
value = {"observation": {"userAgent": "synthetic-control", "rows": rows},
         "calibrations": [{"id": "literal-number", "expected": "5", "number": "5", "fontSize": "5px", "width": "5px"},
                          {"id": "true-var-self-cycle", "expected": "3", "number": "3", "fontSize": "3px", "width": "3px"}]}
original = validation.summarize(value)
assert not original["calibration_discrepancies"] and not original["native_fix_acceptance"]
changed = copy.deepcopy(value)
for row in changed["observation"]["rows"]:
    row.update(first="3", number="3", fontSize="3px", width="3px")
candidate = validation.summarize(changed)
comparison = validation.compare(original, candidate)
assert len(comparison["changed_rows"]) == 4 and comparison["normative_verdict"] == "not evaluated"
changed["calibrations"][1]["number"] = "9"
assert validation.summarize(changed)["calibration_discrepancies"] == ["true-var-self-cycle"]
rejected = []
for label, edit in [
    ("missing row", lambda v: v["observation"]["rows"].pop()),
    ("duplicate row", lambda v: v["observation"]["rows"].append(v["observation"]["rows"][0])),
    ("wrong order", lambda v: v["observation"]["rows"].reverse()),
    ("missing calibration", lambda v: v["calibrations"].pop()),
    ("non-string value", lambda v: v["observation"]["rows"][0].update(number=None)),
]:
    invalid = copy.deepcopy(value)
    edit(invalid)
    try:
        validation.summarize(invalid)
    except (AssertionError, KeyError, TypeError):
        rejected.append(label)
    else:
        raise AssertionError(label)
with tempfile.TemporaryDirectory(prefix="registered-number-observation-auth-") as temporary:
    directory = Path(temporary)
    (directory / "payload").write_text("original")
    manifest = {"payload": {"sha256": hashlib.sha256(b"original").hexdigest()}}
    (directory / "FILES.json").write_text(json.dumps(manifest))
    expected = hashlib.sha256((directory / "FILES.json").read_bytes()).hexdigest()
    runner.authenticate(directory, expected)
    (directory / "payload").write_text("modified")
    try:
        runner.authenticate(directory, expected)
    except RuntimeError:
        rejected.append("changed payload before helper import")
    else:
        raise AssertionError("changed helper admitted")
    try:
        runner.authenticate(directory, "0" * 64)
    except RuntimeError:
        rejected.append("stale manifest")
    else:
        raise AssertionError("stale manifest admitted")
assert (HERE / "observation-only.html").read_bytes() == (ROOT / "artifacts/css-registered-number-wpt-fixture-v2/observation-only.html").read_bytes()
policy = json.loads((HERE / "POLICY.json").read_text())
assert policy["source_roles"] == json.loads((ROOT / policy["wpt_capsule"] / "POLICY.json").read_text())["source_roles"]
runner.authenticate(ROOT / policy["wpt_capsule"], policy["wpt_capsule_manifest_sha256"])
for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
for path in HERE.glob("*.py"):
    ast.parse(path.read_text(), filename=str(path))
print(json.dumps({"exact_sealed_observation_page": True, "native_roles_match_normative_capsule": True,
                  "arbitrary_changed_observations_retained_without_verdict": True,
                  "calibration_discrepancy_recorded_without_gate": True, "rejected_controls": rejected,
                  "browser_executed": False, "server_started": False, "live_queries": False}, indent=2))
