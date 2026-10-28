import copy
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = json.loads((HERE / "POLICY.json").read_text())
helper = load("observer_wpt_helper", ROOT / policy["wpt_capsule"] / "run.py")
adoption = load("observer_adoption", HERE / "adoption.py")
receipt = helper.read(HERE / "ADOPTED-ORIGINAL.json")
original = ROOT / receipt["runtime"] / "RESULT.json"


def validate(here=HERE, current=policy, path=original, digest=receipt["result_sha256"]):
    return adoption.validate(ROOT, here, path, digest, current, helper)


accepted = validate()
rejected = []


def reject(label, **kwargs):
    try:
        validate(**kwargs)
    except (AssertionError, RuntimeError, KeyError, ValueError):
        rejected.append(label)
    else:
        raise AssertionError(label)


reject("other original result", path=original.with_name("OTHER.json"))
reject("other original digest", digest="0" * 64)
for key in policy:
    changed = copy.deepcopy(policy)
    if key == "source_roles":
        name = next(iter(changed[key]["original"]))
        changed[key]["original"][name] = "0" * 64
    else:
        changed[key] = None
    reject("policy drift: " + key, current=changed)
with tempfile.TemporaryDirectory(prefix="number-observer-adoption-") as temporary:
    scratch = Path(temporary) / "capsule"
    shutil.copytree(HERE, scratch)
    for name in ["report.js", "report.html", "CASES.json", "validate.py"]:
        path = scratch / name
        saved = path.read_bytes()
        path.write_bytes(saved + b"\n")
        reject("observer payload drift: " + name, here=scratch)
        path.write_bytes(saved)
    path = scratch / "ADOPTED-ORIGINAL.json"
    for name in receipt["runtime_files"]:
        altered = copy.deepcopy(receipt)
        altered["runtime_files"][name] = "0" * 64
        path.write_text(json.dumps(altered))
        reject("saved original runtime drift: " + name, here=scratch)
    altered = copy.deepcopy(receipt)
    altered["predecessor_manifest_sha256"] = "0" * 64
    path.write_text(json.dumps(altered))
    reject("other predecessor capsule", here=scratch)
    path.write_text(json.dumps(receipt))
    assert validate(here=scratch) == accepted
validation = load("observer_validator_controls", HERE / "validate.py")
print(json.dumps({"adopted_original": accepted, "rejected_controls": rejected,
                  "negative_count": len(rejected), "validator_controls": validation.checks(),
                  "raw_summary_recomputed": True, "scratch_removed": not Path(temporary).exists(),
                  "browser_executed": False}, indent=2))
