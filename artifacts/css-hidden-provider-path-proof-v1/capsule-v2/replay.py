import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,json,os,re,stat,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);p.add_argument("--repo",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;repo=a.repo.resolve();out=a.output.resolve()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def auth(folder,pin):
    need(sha(folder/"FILES.json")==pin,"Manifest pin")
    m=read(folder/"FILES.json");m=m.get("files",m);actual=set()
    for f in folder.rglob("*"):
        mode=f.lstat().st_mode
        if stat.S_ISDIR(mode):continue
        need(stat.S_ISREG(mode),"Nonregular input")
        actual.add(f.relative_to(folder).as_posix())
    need(actual==set(m)|{"FILES.json","FREEZE.json"},"Closed roster")
    for n,h in m.items():
        need(not Path(n).is_absolute() and ".." not in Path(n).parts,"Unsafe path")
        need(sha(folder/n)==h,"Payload "+n)
    return m
need(not out.exists() and out!=here and here not in out.parents and out not in here.parents,"Fresh outside output")
auth(here,a.manifest_sha)
b=read(here/"BINDINGS.json")
for n,h in b["dependencies"].items():need(sha(repo/n)==h,"Dependency "+n)
sub=repo/"artifacts/css-hidden-subtree-proof-v1/capsule"
auth(sub,b["dependencies"]["artifacts/css-hidden-subtree-proof-v1/capsule/FILES.json"])
line=repo/"artifacts/css-hidden-skipped-line-proof-v1/capsule"
auth(line,b["dependencies"]["artifacts/css-hidden-skipped-line-proof-v1/capsule/FILES.json"])
column=repo/"artifacts/css-hidden-column-provider-proof-v1"
auth(column,b["dependencies"]["artifacts/css-hidden-column-provider-proof-v1/FILES.json"])
audit=repo/"artifacts/css-hidden-ordinary-block-query-audit-v1"
auth(audit,b["dependencies"]["artifacts/css-hidden-ordinary-block-query-audit-v1/FILES.json"])
before=(audit/"source/ReflowLine.before.cpp").read_bytes();after=(audit/"source/ReflowLine.candidate.cpp").read_bytes();added=b["added_block"].encode()
need(after.count(added)==1 and after.replace(added,b"",1)==before,"Exact source delta")
full=(repo/"artifacts/css-hidden-layout-column-runtime-v1/baseline/inputs/layout/generic/nsBlockFrame.cpp").read_bytes()
need(full.count(before)==1 and hashlib.sha256(full.replace(before,after,1)).hexdigest()==b["full_candidate_sha256"],"Full source join")
lean=read(here/"TOOLS.json")["lean"];need(sha(Path(lean["path"]))==lean["sha256"],"Compiler pin")
names=read(here/"AUDITS.json")
need(names==["ProviderPath."+n for n in re.findall(r"^theorem (\w+)",(here/"lean/ProviderPath.lean").read_text(),re.M)],"Theorem roster")
need(names==re.findall(r"#print axioms ([\w.]+)",(here/"lean/Audit.lean").read_text()),"Audit source roster")
out.mkdir(parents=True);commands=[];summary={"status":"INCOMPLETE"}
def run(name,cmd,cwd,env,success=True):
    r=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True)
    (out/(name+".stdout")).write_text(r.stdout);(out/(name+".stderr")).write_text(r.stderr)
    commands.append({"name":name,"argv":[str(x) for x in cmd],"exit":r.returncode})
    need((r.returncode==0) if success else (r.returncode!=0),"Unexpected exit "+name)
    return r.stdout,r.stderr
try:
    with tempfile.TemporaryDirectory(prefix="provider-path-lean-",dir=out) as temp:
        work=Path(temp);env=dict(os.environ,LEAN_PATH=str(work))
        for name in ["Hidden","Subtree"]:(work/(name+".lean")).write_bytes((sub/"lean"/(name+".lean")).read_bytes())
        (work/"LineReady.lean").write_bytes((line/"lean/LineReady.lean").read_bytes())
        (work/"ProviderReadiness.lean").write_bytes((column/"lean/ProviderReadiness.lean").read_bytes())
        for f in (here/"lean").glob("*.lean"):(work/f.name).write_bytes(f.read_bytes())
        for name in ["Hidden","Subtree","LineReady","ProviderReadiness","ProviderPath"]:
            stdout,stderr=run(name,[lean["path"],"-o",name+".olean",name+".lean"],work,env)
            need(not stdout and not stderr,"Compiler diagnostic")
        stdout,stderr=run("audits",[lean["path"],"Audit.lean"],work,env)
        need(not stderr and re.findall(r"^'([\w.]+)'",stdout,re.M)==names,"Exact kernel audit")
        for line in stdout.splitlines():
            match=re.search(r"depends on axioms: \[(.*?)\]",line)
            need(match is not None or "does not depend on any axioms" in line,"Audit format")
            if match:need(set(match.group(1).split(", "))<={"propext","Classical.choice","Quot.sound"},"Unexpected axiom")
        for f in sorted((here/"falseclaims").glob("*.lean")):
            (work/f.name).write_bytes(f.read_bytes());stdout,stderr=run("false-"+f.stem,[lean["path"],f.name],work,env,False)
            need("Tactic `decide` proved that the proposition" in stdout and "is false" in stdout and not stderr,"Falseclaim reason")
        summary={"status":"PASS_SCOPED_PATH_PROVIDER_COMPOSITION","new_audits":len(names),"reused_modules":["Hidden","Subtree","LineReady","ProviderReadiness"],"falseclaims":2,"exact_full_method_binding":True,"native_execution":False,"actual_reachability_proved":False}
finally:
    summary["temporary_products_removed"]=not any(x.is_dir() for x in out.iterdir())
    (out/"COMMANDS.json").write_text(json.dumps(commands,indent=2)+"\n")
    (out/"SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary))
