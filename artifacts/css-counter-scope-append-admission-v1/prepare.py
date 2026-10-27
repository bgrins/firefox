import copy,hashlib,importlib.util,json,os,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS="0")
def load(n,p):
 s=importlib.util.spec_from_file_location(n,ROOT/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
read=lambda p:json.loads((ROOT/p).read_text())
def save(n,d):
 with (HERE/n).open("x") as f:json.dump(d,f,indent=2,sort_keys=True);f.write("\n")
def ref(n):return {"path":n,"sha256":hashlib.sha256((ROOT/n).read_bytes()).hexdigest()}
h=load("preserve","artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py")
a=load("epoch","artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py")
c=load("controller","artifacts/css-quote-scope-append-coc-runtime-v2/compare.py")
old=read("artifacts/css-counter-scope-append-probe-runtime-v1/CURRENT-EPOCH.json")
a.verify_current(h,ROOT,ENV,old)
current=copy.deepcopy(old);roles=read("artifacts/css-counter-scope-append-comparison-inputs-v1/RESOURCE-PINS.json")
assert all(roles[n]==v for n,v in old["pins"].items());current["pins"]=roles;current["counts"]["roles"]=len(roles)
sources=read("artifacts/css-counter-scope-append-comparison-inputs-v1/SOURCE-PINS.json")
for n,s in sources.items():
 assert roles[n]==s["original_sha256"]
 info=(ROOT/n).lstat();assert stat.S_ISREG(info.st_mode);current["installed_identities"][n]=[info.st_dev,info.st_ino]
current["counts"]["installed_identities"]=len(current["installed_identities"])
check=a.verify_current(h,ROOT,ENV,current);save("CHECK.json",check);save("CURRENT-EPOCH.json",current)
flags={label:c.index_flags(h,repo,ENV) for label,repo in [("root",ROOT),("nested",ROOT/"artifacts/css-spec-lean")]}
admission={"status":"COUNTER_OCOC_EPOCH_VERIFIED","exit":0,"epoch":ref(str((HERE/"CURRENT-EPOCH.json").relative_to(ROOT))),"sources":{n:v["original_sha256"] for n,v in sources.items()},"binaries":{n:roles[n] for n in c.BINARY_ROLES},"index_flags":flags,"additional_roles":{},"baseline_probe_run":ref("artifacts/css-counter-scope-append-probe-runtime-v1/wpt-observation/RUN.json"),"evidence":[ref("artifacts/css-counter-scope-append-probe-runtime-v1/OUTER-EXECUTION.json"),ref("artifacts/css-counter-scope-append-probe-runtime-v1/RESULT.json"),ref("artifacts/css-local-signing-20261027-v6/FINAL-CHECK.json"),ref("artifacts/css-counter-scope-append-wpt-lint-v1/LINT.json")]}
save("ADMISSION.json",admission);print("Counter comparison epoch verified",len(roles),flush=True)
