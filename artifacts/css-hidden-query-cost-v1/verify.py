import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
import argparse,hashlib,json,stat
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;repo=here.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
need(sha(here/"FILES.json")==a.manifest_sha,"Manifest")
m=json.loads((here/"FILES.json").read_text());actual=set()
for f in here.rglob("*"):
    mode=f.lstat().st_mode
    if stat.S_ISDIR(mode):raise RuntimeError("Unexpected directory")
    need(stat.S_ISREG(mode),"Nonregular file");actual.add(f.name)
need(actual==set(m)|{"FILES.json","FREEZE.json"},"Roster")
for n,h in m.items():need(sha(here/n)==h,"Payload")
d=json.loads((here/"DEPENDENCIES.json").read_text());old=repo/"artifacts/css-hidden-layout-cost-v4"
need(sha(old/"FILES.json")==d["cost_v4_manifest_sha256"],"Prior manifest")
need(sha(old/"cleanup.py")==sha(here/"cleanup.py")==d["cleanup_sha256"],"Cleanup preservation")
need(sha(old/"run.py")==d["runner_original_sha256"],"Original runner")
need(sha(repo/d["geometry_fixture_source"])==d["geometry_fixture_source_sha256"],"Geometry source")
print("PASS: sealed source-only cost fixture, preserved cleanup, pinned runner delta and static receipts; browser calibration still required")
