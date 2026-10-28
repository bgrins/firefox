import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
policy=json.loads((HERE/"POLICY.json").read_text())
parser=load("calibration_assessor",HERE/"assess.py")
checks=load("calibration_checks",ROOT/policy["helpers"]["checks"])
binding={"path":"/observation/application.ini","resolved":"/observation/application.ini", "sha256":"a"*64,"browser_build_id":"20261027180752","revision":policy["frozen_head"]}
def events(fail=False):
    out=[{"action":"suite_start","run_info":{"os":"mac","debug":False,"browser_build_id":binding["browser_build_id"],"revision":binding["revision"]}}]
    for test,names in policy["target_subtests"].items():
        out.append({"action":"test_start","test":test})
        for name in names:
            out.append({"action":"test_status","test":test,"subtest":name,"status":"FAIL" if fail else "PASS","expected":"PASS","message":"calibration assertion" if fail else None})
        out.append({"action":"test_end","test":test,"status":"OK"})
    out.append({"action":"suite_end"})
    return out

def assess(rows,code=1,info=binding):
    return parser.assess(rows,code,policy,checks,original=None,run_binding=info)
positive=[]
for fail in [False,True]:
    value=assess(events(fail),int(fail))
    assert value["complete"] and value["observed_subtest_count"]==68 and not value["comparison_gate_passed"]
    positive.append("all FAIL preserved as observation" if fail else "all PASS preserved as observation")
rejected=[]
def reject(label,rows,code=1,info=binding):
    assert not assess(rows,code,info)["complete"],label
    rejected.append(label)
base=events(True)
for i,row in enumerate(base):
    if row["action"]=="test_status":
        reject("missing identity: "+row["subtest"],base[:i]+base[i+1:])
first=next(i for i,row in enumerate(base) if row["action"]=="test_status")
reject("duplicate identity",base[:first]+[base[first]]+base[first:])
for status in ["TIMEOUT","NOTRUN","ERROR"]:
    changed=copy.deepcopy(base);changed[first]["status"]=status;reject("noncompleted "+status,changed)
reject("missing suite end",base[:-1])
reject("inconsistent command exit",base,0)
for field in ["browser_build_id","revision"]:
    changed=copy.deepcopy(base);changed[0]["run_info"][field]="wrong";reject("metadata mismatch "+field,changed)
changed=copy.deepcopy(base);changed[first]["subtest"]="unexpected name";reject("foreign identity",changed)
changed=copy.deepcopy(base);changed.insert(-1,{"action":"crash"});reject("crash",changed)
for i,row in enumerate(base):
    if row["action"]=="test_end":
        changed=copy.deepcopy(base);changed[i]["status"]="TIMEOUT";reject("noncompleted page "+row["test"],changed)
result={"positive_controls":positive,"rejected_count":len(rejected),"rejected_controls":rejected,"browser_executed":False,"native_validation":False}
(HERE/"CONTROLS.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"positive":len(positive),"rejects":len(rejected),"browser_executed":False}))
