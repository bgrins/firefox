import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,stat
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    def unique(items):
        d={}
        for k,v in items:
            require(k not in d,"duplicate JSON key");d[k]=v
        return d
    return json.loads(p.read_text(),object_pairs_hook=unique)
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);args=p.parse_args()
require(sha(R/"FILES.json")==args.manifest_sha,"external review manifest")
j=read(R/"FILES.json");names=set()
for e in j["files"]:
    n=e["path"];q=PurePosixPath(n)
    require(str(q)==n and not q.is_absolute() and ".." not in q.parts and n not in names and n not in ["FILES.json","FREEZE.json"],"path")
    names.add(n)
found=set();dirs=set()
for root,ds,fs in os.walk(R,followlinks=False):
    for n in ds+fs:
        f=Path(root)/n; rel=f.relative_to(R).as_posix();mode=f.lstat().st_mode
        if stat.S_ISREG(mode):found.add(rel)
        elif stat.S_ISDIR(mode):dirs.add(rel)
        else:raise RuntimeError("nonregular entry")
require(found==names|{"FILES.json","FREEZE.json"},"closed file roster")
require(dirs=={str(q) for n in names for q in PurePosixPath(n).parents if str(q)!="."},"closed directory roster")
for e in j["files"]:require(sha(R/e["path"])==e["sha256"],"hash: "+e["path"])
require(read(R/"FREEZE.json")["manifest_sha256"]==args.manifest_sha,"freeze")
require(sha(R/"relocated-capsule/FILES.json")=="3c22b32c3840977fcb195a5aa0eb28e1e324417014b027a8140a87c8ff4c5cee","producer binding")
rep=read(R/"replay/RESULT.json")
require([rep[k] for k in ["audits","cases","complete_comparisons","native_mutants","model_lifecycle_mutants"]]==[59,856,5136,7,5],"replay counts")
require(len(read(R/"kernel-challenges/RESULT.json")["results"])==10,"kernel challenges")
require(len(read(R/"GUARDS.json"))==8 and len(read(R/"AXIOMS.json"))==2,"negative controls")
require(read(R/"VERDICT.json")["verdict"]=="HOLD_FULL_ORIGINAL_FORMAL_SCOPE","verdict")
print(json.dumps({"status":"AUTHENTICATED_REVIEW_RECEIPTS","files":len(names),"verdict":"HOLD_FULL_ORIGINAL_FORMAL_SCOPE","note":"This command authenticates retained replay receipts; run relocated-capsule/check.py with a new external output for fresh execution."}))
