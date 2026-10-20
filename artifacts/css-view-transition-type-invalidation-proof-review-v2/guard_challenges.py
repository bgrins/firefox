import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use -I -S without optimization")
sys.dont_write_bytecode = True
import copy, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
capsule=root/"capsule"
workspace=root/"guards"
workspace.mkdir(exist_ok=False)
records=[]
for name,flags,alter in [
    ("optimized",["-I","-S","-O"],None),
    ("double-optimized",["-I","-S","-OO"],None),
    ("not-isolated",["-S"],None),
    ("site-enabled",["-I"],None),
    ("shadow-before-import",["-S"],"shadow"),
    ("extra-file",["-I","-S"],"extra"),
    ("extra-directory",["-I","-S"],"directory"),
    ("nested-seal",["-I","-S"],"nested"),
    ("symlink",["-I","-S"],"symlink"),
    ("altered-input",["-I","-S"],"altered")]:
    source=workspace/name;shutil.copytree(capsule,source)
    if alter=="shadow":(source/"json.py").write_text('raise RuntimeError("REVIEW_SHADOW_EXECUTED")\n')
    if alter=="extra":(source/"extra.txt").write_text("extra")
    if alter=="directory":(source/"empty").mkdir()
    if alter=="nested":(source/"lean/FREEZE.json").write_text("{}")
    if alter=="symlink":(source/"lean/linked").symlink_to(source/"lean/Invalidation.lean")
    if alter=="altered":(source/"lean/Invalidation.lean").write_text((source/"lean/Invalidation.lean").read_text()+"\n")
    out=workspace/(name+"-output")
    command=[sys.executable,*flags,str(source/"check.py"),"--output",str(out)]
    p=subprocess.run(command,text=True,capture_output=True)
    if p.returncode==0 or out.exists() or "REVIEW_SHADOW_EXECUTED" in p.stderr:
        raise RuntimeError("guard failure: "+name)
    records.append(dict(name=name,command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,output_created=False))
    shutil.rmtree(source)
module_spec=importlib.util.spec_from_file_location("review_calibration",capsule/"calibration.py")
module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
cases=json.loads((capsule/"native/CASES.json").read_text())
module.validate_cases(cases)
for name in ["actor-out-of-range","name-out-of-range","bool-owner","delivery-mask","partial-action","extra-field","missing-row","duplicate-row","reordered-row"]:
    bad=copy.deepcopy(cases)
    if name=="actor-out-of-range":bad[18]["actions"][0][1]=2
    if name=="name-out-of-range":bad[18]["actions"][0][2]=2
    if name=="bool-owner":bad[18]["setup"][0]=True
    if name=="delivery-mask":bad[18]["actions"][1][2]=32
    if name=="partial-action":bad[18]["actions"][0].pop()
    if name=="extra-field":bad[18]["extra"]=0
    if name=="missing-row":bad.pop()
    if name=="duplicate-row":bad[-1]=bad[-2]
    if name=="reordered-row":bad[-1],bad[-2]=bad[-2],bad[-1]
    try:module.validate_cases(bad)
    except RuntimeError as error:records.append(dict(name=name,rejected=True,reason=str(error)))
    else:raise RuntimeError("case admission accepted: "+name)
(root/"GUARDS.json").write_text(json.dumps(records,indent=2)+"\n")
workspace.rmdir()
print(json.dumps({"negative_controls":len(records),"intact_case_roster":"PASS","temporary_copies_removed":True}))
