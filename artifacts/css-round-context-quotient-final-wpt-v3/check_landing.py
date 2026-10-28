import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h = load("landing_check_runner", HERE / "run.py")
b = load("landing_check_binding", HERE / "bindings.py")
p = h.read(HERE / "POLICY.json")
original = b.validate_original(ROOT, HERE, p, h)
prior = h.read(ROOT / p["paired_runtime"] / "candidate-wpt/ASSESSMENT.json")
projected = dict(prior, rows=b.remaining_rows(prior, h))
b.validate_final_assessment(ROOT, HERE, p, projected, h)
rejected = []
for label in ("failed omitted", "missing omitted", "duplicate omitted"):
    changed = copy.deepcopy(prior)
    row = next(e for e in changed["rows"] if e["test"] == b.LANDING_TEST and e["subtest"] == b.OMITTED_SUBTEST)
    if label == "failed omitted":
        row["status"] = "FAIL"
    elif label == "missing omitted":
        changed["rows"].remove(row)
    else:
        changed["rows"].append(copy.deepcopy(row))
    try:
        b.remaining_rows(changed, h)
    except RuntimeError:
        rejected.append(label)
    else:
        raise AssertionError(label)
for field, value in (("status", "FAIL"), ("message", "changed"), ("expected", "SKIP"), ("known_intermittent", ["FAIL"])):
    changed = copy.deepcopy(projected)
    changed["rows"][0][field] = value
    try:
        b.validate_final_assessment(ROOT, HERE, p, changed, h)
    except RuntimeError:
        rejected.append(field)
    else:
        raise AssertionError(field)
print(json.dumps({"historical_rows": [len(original["rows"]), len(prior["rows"])], "final_rows": len(projected["rows"]), "rejected_controls": rejected, "live_checks": False}))
