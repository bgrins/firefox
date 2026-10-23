import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
import argparse, hashlib, json, stat, subprocess, tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def need(ok,msg):
    if not ok: raise RuntimeError(msg)
def authenticate(folder,pin):
    need(sha(folder/"FILES.json")==pin,"Manifest identity")
    m=read(folder/"FILES.json");actual=set()
    for p in folder.rglob("*"):
        mode=p.lstat().st_mode
        if stat.S_ISDIR(mode): continue
        need(stat.S_ISREG(mode),"Nonregular entry")
        actual.add(p.relative_to(folder).as_posix())
    need(actual==set(m)|{"FILES.json","FREEZE.json"},"Closed roster")
    for name,h in m.items():
        need(not Path(name).is_absolute() and ".." not in Path(name).parts,"Invalid path")
        need(sha(folder/name)==h,"Payload hash")
authenticate(here,a.manifest_sha)
pins=read(here/"INPUT-PINS.json")
for name,pin in pins.items(): need(sha(root/name)==pin,"External pin "+name)
runtime=root/"artifacts/css-hidden-layout-column-runtime-v1"
authenticate(runtime,pins["artifacts/css-hidden-layout-column-runtime-v1/FILES.json"])
state=read(runtime/"STATE.json")
need(state["status"]=="terminal" and state["restored"] and state["restore_build_exit"]==0 and not state["recovery_errors"] and "failure" not in state,"Runtime terminal state")
need(read(runtime/"BEFORE.json")==read(runtime/"FINAL.json")==read(runtime/"INPUTS.json")["before"],"Historical restoration")
need(set(state["phases"])=={"baseline","both"},"Main phase roster")
need(set(state["traces"])=={"trace-both-column"},"Trace phase roster")
for phase in list(state["phases"].values())+list(state["traces"].values()):
    need(phase["build_exit"]==0 and phase["wpt"]["complete"],"Incomplete build/WPT")
for phase in ["baseline","both"]:
    need(read(runtime/(phase+"-timing-parent.json"))["measurement_complete"],"Incomplete cost")
with tempfile.TemporaryDirectory(prefix="hidden-decision-") as tmp:
    output=Path(tmp)/"check.json"
    subprocess.run([sys.executable,"-I","-S",str(here/"analyze-column.py"),"--runtime",str(runtime),"--prior",str(root/"artifacts/css-hidden-flex-combined-runtime-v1"),"--phases","baseline","both","--output",str(output)],check=True)
    need(output.read_bytes()==(here/"COLUMN-COST-CHECK.json").read_bytes(),"Independent recount mismatch")
print("PASS: sealed runtime, historical restoration, exact two-phase outcomes and controlled cost recount; scoped decision and installation inputs authenticated")
