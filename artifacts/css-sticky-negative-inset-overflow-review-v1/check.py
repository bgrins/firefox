import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("require Python -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,os,re,stat,subprocess
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    def pairs(items):
        result={}
        for k,v in items:
            require(k not in result,"duplicate JSON key");result[k]=v
        return result
    return json.loads(p.read_text(),object_pairs_hook=pairs)
def authenticate(digest):
    require(sha(ROOT/"FILES.json")==digest,"external manifest")
    require(read(ROOT/"FREEZE.json")["files_sha256"]==digest,"freeze binding")
    rows=read(ROOT/"FILES.json")["files"];files={};dirs=set()
    for row in rows:
        name=row["path"];q=PurePosixPath(name)
        require(not q.is_absolute() and q.as_posix()==name and all(x not in [".","..",""] for x in q.parts),"path grammar")
        require(name not in files and name not in ["FILES.json","FREEZE.json"],"duplicate/reserved path")
        require(re.fullmatch("[0-9a-f]{64}",row["sha256"]) is not None,"digest grammar")
        files[name]=row["sha256"];dirs.update(str(p) for p in q.parents if str(p)!=".")
    seen=set();seen_dirs=set()
    for base,ds,fs in os.walk(ROOT,followlinks=False):
        for name in ds+fs:
            p=Path(base)/name;mode=p.lstat().st_mode;rel=str(p.relative_to(ROOT))
            if stat.S_ISREG(mode):seen.add(rel)
            elif stat.S_ISDIR(mode):seen_dirs.add(rel)
            else:raise ValueError("nonregular entry")
    require(seen==set(files)|{"FILES.json","FREEZE.json"} and seen_dirs==dirs,"closed roster")
    for name,digest in files.items():require(sha(ROOT/name)==digest,"file hash: "+name)
    return len(files)
def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);p.add_argument("--authenticate-only",action="store_true");p.add_argument("--out");args=p.parse_args()
    count=authenticate(args.manifest_sha)
    if args.authenticate_only:print(json.dumps({"files":count}));return
    spec=importlib.util.spec_from_file_location("independent_evidence",ROOT/"audit_evidence.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    require(m.audit()==read(ROOT/"EVIDENCE-AUDIT-v2.json"),"native evidence result")
    require(args.out is not None,"output required")
    out=Path(args.out).resolve();require(not out.exists() and out!=ROOT and ROOT not in out.parents,"absent external output")
    out.mkdir();target=out/"ranges"
    cmd=[sys.executable,"-I","-S",str(ROOT/"calibrate_ranges.py"),str(target)]
    proc=subprocess.run(cmd,capture_output=True,text=True);(out/"range-replay.log").write_text(proc.stdout+proc.stderr)
    (out/"COMMAND.json").write_text(json.dumps({"command":cmd,"exit":proc.returncode},indent=2)+"\n")
    require(proc.returncode==0,"range replay")
    require(read(target/"RESULT.json")==read(ROOT/"range-calibration/RESULT.json"),"range observations")
    require(authenticate(args.manifest_sha)==count,"inputs changed")
    result={"status":"pass","native_recommendation":"ACCEPT","formal_companion":"PENDING full stated contract","preexisting_range_lead_preserved":True}
    (out/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
