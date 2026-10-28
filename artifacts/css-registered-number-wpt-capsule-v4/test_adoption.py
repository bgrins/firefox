import copy
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("adoption_runner", HERE / "run.py")
adoption = load("adoption_checks", HERE / "adoption.py")
helper = SimpleNamespace(**vars(runner))
receipt = runner.read(HERE / "ADOPTED-ORIGINAL.json")
baseline = ROOT / receipt["runtime"] / "ASSESSMENT.json"
policy = runner.read(HERE / "POLICY.json")


def validate(here=HERE, current=policy, path=baseline, digest=receipt["assessment_sha256"], helpers=helper):
    return adoption.validate(ROOT, here, path, digest, current, helpers)


accepted = validate()
assert accepted["retains_original_provenance"] and accepted["phase"] == "original-2"
rejected = []


def reject(label, **kwargs):
    try:
        validate(**kwargs)
    except (AssertionError, RuntimeError, KeyError, ValueError):
        rejected.append(label)
    else:
        raise AssertionError(label)


reject("other assessment path", path=baseline.with_name("OTHER.json"))
reject("other assessment digest", digest="0" * 64)
for key in policy:
    changed = copy.deepcopy(policy)
    if key == "source_roles":
        name = next(iter(changed[key]["original"]))
        changed[key]["original"][name] = "0" * 64
    else:
        changed[key] = None
    reject("experiment policy drift: " + key, current=changed)
with tempfile.TemporaryDirectory(prefix="number-adoption-check-") as temporary:
    scratch = Path(temporary) / "capsule"
    shutil.copytree(HERE, scratch)
    for name in ["SOURCE-PINS.json", "SELECTED.json", "TARGET-SUBTESTS.json", "HELD-SUBTESTS.json",
                 "HELD-COMPARISON-POLICY.json", "REGRESSION-SUBTESTS.json", "SUBSET-MANIFEST.json",
                 "EXISTING-MANIFEST-ENTRIES.json", "REFERENCES-TO-COPY.json", "assess.py",
                 "capture/testing/web-platform/tests/css/css-properties-values-api/registered-numeric-selected-dependencies.html"]:
        path = scratch / name
        saved = path.read_bytes()
        path.write_bytes(saved + b"\n")
        reject("fixture/assessor capture drift: " + name, here=scratch)
        path.write_bytes(saved)
    path = scratch / "ADOPTED-ORIGINAL.json"
    for name in ["raw.jsonl", "ASSESSMENT.json", "RESULT.json", "EPOCH.json", "NORMAL-BINARIES.json",
                 "APPLICATION-METADATA.json", "APPLICATION-METADATA-POST.json", "PRE.json", "POST.json", "CLEANUP.json"]:
        altered = copy.deepcopy(receipt)
        altered["runtime_files"][name] = "0" * 64
        path.write_text(json.dumps(altered))
        reject("saved runtime drift: " + name, here=scratch)
    altered = copy.deepcopy(receipt)
    altered["predecessor_manifest_sha256"] = "0" * 64
    path.write_text(json.dumps(altered))
    reject("other predecessor capsule", here=scratch)
    path.write_text(json.dumps(receipt))
    assert validate(here=scratch) == accepted
print(json.dumps({"exact_original_accepted": accepted, "rejected_controls": rejected,
                  "negative_count": len(rejected), "scratch_removed": not Path(temporary).exists(),
                  "raw_assessment_recomputed": True, "browser_executed": False}, indent=2))
