import copy, hashlib, importlib.util, json, os, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS="0")
GIT=["git","--no-optional-locks","-c","core.fsmonitor=false"]
def read(p): return json.loads((ROOT/p).read_text())
def save(p,d):
 with (HERE/p).open("x") as f: json.dump(d,f,indent=2,sort_keys=True);f.write("\n")
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
h=load("preserve","artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py")
a=load("epoch","artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py")
run="artifacts/css-quote-scope-append-coc-execution-v2/"
result=read(run+"RESULT.json");outer=read(run+"OUTER-EXECUTION.json")
assert result["success"] and not result["recovery_errors"] and result["error"] is None
assert outer["exit_code"]==0 and outer["terminal"] is True
final=read(run+"FINAL.json")
old=read("artifacts/css-quote-scope-append-admission-v2/CURRENT-EPOCH.json")
binaries=read("artifacts/css-quote-scope-append-admission-v2/ADMISSION.json")["binaries"]
assert set(final["pins"])==set(old["pins"])
changed={n for n in old["pins"] if old["pins"][n]!=final["pins"][n]}
assert changed<=set(binaries),changed
assert h.semantic_index(final["index"])==old["semantic_index"]
current=copy.deepcopy(old);current["pins"]=final["pins"]
state=h.index_state(ROOT,ENV)
assert h.semantic_index(state)==old["semantic_index"]
current["raw_index_observation"]["current"]=state["raw_index"]
for name,repo in [("root",ROOT),("nested",ROOT/"artifacts/css-spec-lean")]:
 actual=hashlib.sha256(h.git(repo,ENV,"ls-files","-v","-z")).hexdigest()
 assert actual==read("artifacts/css-quote-scope-append-admission-v2/INDEX-FLAGS.json")[name]
a.verify_current(h,ROOT,ENV,current)
save("INITIAL-EPOCH.json",current);save("CURRENT-EPOCH.json",current)
save("ADMISSION.json",{"changed_binary_paths":sorted(changed),"all_other_roles_preserved":True,"source_index_restored":True,"outer_exit":0})
print("Signing epoch verified; changed binaries:",len(changed),flush=True)
