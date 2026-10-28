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


helper = load("run")
bindings = load("bindings")
policy = helper.read(HERE / "POLICY.json")
epoch = helper.read(ROOT / policy["staged_capsule"] / "OBSERVATION-EPOCH.json")
for path in HERE.glob("*.py"):
    ast.parse(path.read_text())
for name, item in helper.read(HERE / "SOURCE-PINS.json").items():
    if item["exists"]:
        assert helper.sha(HERE / item["capture"]) == helper.sha(ROOT / item["origin"]) == item["sha256"]
for name, pin in helper.read(HERE / "REFERENCES.json").items():
    assert helper.sha(ROOT / name) == pin, name
actual = bindings.validate_phase(ROOT, HERE, policy, epoch, helper)
rejected = []
for label in ["HEAD", "dirty native", "role drift", "local source attribution", "source stamp", "BuildID", "binary pin", "missing assertion"]:
    p, e = copy.deepcopy(policy), copy.deepcopy(epoch)
    if label == "HEAD": e["semantic_index"]["head"] = "0" * 40
    elif label == "dirty native": e["modified_native_paths"] = ["unexpected.rs"]
    elif label == "role drift": e["registered_number_transition"]["accepted"] = True
    elif label == "local source attribution": p["source_roles"]["candidate"] = {"unexpected.rs": "0" * 64}
    elif label == "source stamp": p["release_metadata"]["source_stamp"] = "0" * 40
    elif label == "BuildID": p["release_metadata"]["browser_build_id"] = "wrong"
    elif label == "binary pin": p["phase_binaries"][p["normal_binaries"][0]] = "0" * 64
    elif label == "missing assertion": next(iter(p["target_subtests"].values())).pop()
    try:
        bindings.validate_phase(ROOT, HERE, p, e, helper)
    except RuntimeError:
        rejected.append(label)
    else:
        raise AssertionError(label)
result = {"phase_binding": actual, "negative_bindings": rejected,
          "fixture_and_resource_hashes_verified": True, "python_syntax": True,
          "browser_executed": False, "main_executed": False, "live_mutations": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"binding_passed": True, "rejected": len(rejected), "browser_executed": False}))
