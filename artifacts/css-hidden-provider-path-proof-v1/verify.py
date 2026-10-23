import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
import argparse,hashlib,json,stat
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;repo=here.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
need(sha(here/"FILES.json")==a.manifest_sha,"Outer pin")
m=json.loads((here/"FILES.json").read_text());actual=set()
for f in here.rglob("*"):
    mode=f.lstat().st_mode
    if stat.S_ISDIR(mode):continue
    need(stat.S_ISREG(mode),"Nonregular payload")
    actual.add(f.relative_to(here).as_posix())
need(actual==set(m)|{"FILES.json","FREEZE.json"},"Closed outer roster")
for n,h in m.items():need(sha(here/n)==h,"Outer hash")
need(sha(here/"capsule-v2/FILES.json")=="12b6ad7af5a041038d437ef33d740daeac75a63817c1f58d12d3431aa3d72b93","Inner pin")
b=json.loads((here/"capsule-v2/BINDINGS.json").read_text())
for n,h in b["dependencies"].items():need(sha(repo/n)==h,"Dependency")
for role in ["replay-canonical-v2","replay-relocated-v2"]:
    s=json.loads((here/role/"SUMMARY.json").read_text())
    need(s["status"]=="PASS_SCOPED_PATH_PROVIDER_COMPOSITION" and s["new_audits"]==15 and s["falseclaims"]==2 and s["temporary_products_removed"],"Replay receipt")
need(not any(f.suffix in {".olean",".o",".pyc"} for f in here.rglob("*")),"Disposable product")
print("PASS: sealed scoped model/source bindings, two successful replay receipts and cleanup; use capsule-v2/replay.py for fresh kernel replay")
