import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper, bindings = load("run"), load("bindings")
policy = helper.read(HERE / "POLICY.json")
epoch = helper.read(ROOT / "artifacts/css-local-signing-20261027-v25/CURRENT-EPOCH.json")
for path in HERE.glob("*.py"):
    ast.parse(path.read_text())
for name, pin in helper.read(HERE / "REFERENCES.json").items():
    assert helper.sha(ROOT / name) == pin, name
for name, item in helper.read(HERE / "SOURCE-PINS.json").items():
    if item["exists"]:
        assert helper.sha(HERE / item["capture"]) == helper.sha(ROOT / item["origin"]) == item["sha256"], name
    else:
        assert not (ROOT / item["origin"]).exists(), name
old = ROOT / "artifacts/css-registered-zoom-final-wpt-v1"
oldpins = helper.read(old / "SOURCE-PINS.json")
pins = helper.read(HERE / "SOURCE-PINS.json")
assert all(pins[name] == item for name, item in oldpins.items())
oldpolicy = helper.read(old / "POLICY.json")
assert all(policy["target_subtests"][name] == names for name, names in oldpolicy["target_subtests"].items())
assert policy["held_subtests"] == oldpolicy["held_subtests"]
assert policy["phase_binaries"] == oldpolicy["phase_binaries"]
actual = bindings.validate_phase(ROOT, HERE, policy, epoch, helper)
rejected = []
for label in ["wrong HEAD", "unaccepted build", "dirty native", "source drift", "binary drift"]:
    p, e = copy.deepcopy(policy), copy.deepcopy(epoch)
    if label == "wrong HEAD": e["semantic_index"]["head"] = "0" * 40
    elif label == "unaccepted build": e["registered_number_transition"]["accepted"] = False
    elif label == "dirty native": e["modified_native_paths"] = ["unexpected.rs"]
    elif label == "source drift": e["pins"][next(iter(p["source_roles"]["candidate"]))] = "0" * 64
    elif label == "binary drift": e["pins"][p["normal_binaries"][0]] = "0" * 64
    try:
        bindings.validate_phase(ROOT, HERE, p, e, helper)
    except RuntimeError:
        rejected.append(label)
    else:
        raise AssertionError(label)
result = {"actual_phase_binding": actual, "binding_rejects": rejected,
          "prior_668_inputs_unchanged": True, "fixture_resource_hashes_verified": True,
          "python_syntax": True, "browser_executed": False, "main_executed": False,
          "live_mutations": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"actual_binding_passed": True, "binding_rejects": len(rejected), "prior_668_unchanged": True}))
