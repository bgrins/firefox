import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review = load("expanded_terminal_review_test", HERE / "review.py")
assessor = load("strict_signature", ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py")
config = review.read(HERE / "POLICY.json")
assert config["execution_enabled"] is False and config["source_or_canonical_mutations_allowed"] is False
review.authenticate(ROOT / config["owner_directory"], config["owner_manifest_sha256"])
for name, pin in review.read(HERE / "REFERENCES.json").items():
    assert review.sha(ROOT / name) == pin
old = [{"action": "test_status", "test": "/one", "subtest": "case", "status": "FAIL", "expected": "PASS", "message": "old"}, {"action": "test_end", "test": "/one", "status": "OK"}]
extra = {"action": "test_status", "test": "/two", "subtest": "new", "status": "PASS"}
assert review.compare_inherited(old, old + [extra], assessor.signature)["unchanged"] == 2
for field, value in [("status", "PASS"), ("message", "new"), ("expected", "FAIL"), ("known_intermittent", [])]:
    changed = copy.deepcopy(old)
    changed[0][field] = value
    result = review.compare_inherited(old, changed + [extra], assessor.signature)
    assert result["unchanged"] == 1 and len(result["differences"]) == 1
rejected = 0
for current in [old[:1], old + [copy.deepcopy(old[0])]]:
    try:
        review.compare_inherited(old, current, assessor.signature)
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("invalid inherited roster admitted")
for path in HERE.glob("*.py"):
    ast.parse(path.read_text())
assert rejected == 2
print(json.dumps({"comparison_cases": 5, "roster_negatives": 2, "owner_authenticated": True, "terminal_receipt_only": True, "live_guard_executed": False}))
