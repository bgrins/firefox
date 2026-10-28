import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = json.loads((HERE / "POLICY.json").read_text())
helper = load("helper",ROOT / policy["wpt_capsule"] / "run.py")
module = load("succession",HERE / "succession.py")
receipt = helper.read(HERE / "HEAD-SUCCESSION.json")
old = helper.read(ROOT / receipt["predecessor"] / "POLICY.json")
before = helper.read(ROOT / receipt["before_epoch"])
after = helper.read(ROOT / receipt["after_epoch"])
calibration = helper.read(ROOT / receipt["candidate_runtime"] / "EPOCH.json")
values = [receipt,policy,old,before,after,calibration]
module.validate_core(*values,helper.need)
negatives = []
for key in ["frozen_head","original_frozen_head","epoch_sha256","calibration_epoch_sha256","calibration_assessment_sha256","wpt_capsule_manifest_sha256"]:
    changed=copy.deepcopy(values);changed[1][key]="wrong";negatives.append(changed)
for key in ["old_head","new_head"]:
    changed=copy.deepcopy(values);changed[0][key]="wrong";negatives.append(changed)
for index in [3,4,5]:
    for key,value in [("role","original"),("variant","wrong"),("compiled",False),("accepted",True),("last_phase","wrong")]:
        changed=copy.deepcopy(values);changed[index]["registered_number_transition"][key]=value;negatives.append(changed)
    changed=copy.deepcopy(values);changed[index]["semantic_index"]["head"]="wrong";negatives.append(changed)
    for name in dict(policy["source_roles"]["candidate"],**policy["candidate_binaries"]):
        changed=copy.deepcopy(values);changed[index]["pins"][name]="wrong";negatives.append(changed)
for changed in negatives:
    try: module.validate_core(*changed,helper.need)
    except RuntimeError: continue
    raise AssertionError("corrupt succession core accepted")
historical=helper.read(ROOT / receipt["candidate_runtime"] / "APPLICATION-METADATA.json")
actual=dict(historical,revision=receipt["new_head"])
module.validate_metadata(actual,historical,receipt,helper.need)
metadata_negatives=0
for key in historical:
    changed=dict(actual);changed[key]="wrong"
    try: module.validate_metadata(changed,historical,receipt,helper.need)
    except RuntimeError: metadata_negatives+=1;continue
    raise AssertionError("metadata drift accepted")
validation=load("validation",HERE / "validate.py")
baseline=load("baseline",HERE / "baseline.py")
original=baseline.validate(ROOT,HERE,policy,helper,validation)
assert baseline.compare(original["summary"],original["summary"],validation)["changed_cases"]==0
for path in HERE.glob("*.py"):ast.parse(path.read_text())
print(json.dumps({"positive_core":1,"negative_core":len(negatives),"positive_metadata":1,"negative_metadata":metadata_negatives,
                  "original_baseline_replayed":True,"runner_main_executed":False,"browser_executed":False},indent=2))
