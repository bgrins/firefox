import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S")
import argparse,hashlib,json,stat
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--manifest-sha",required=True);a=p.parse_args()
here=Path(__file__).resolve().parent;root=here.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
need(sha(here/"FILES.json")==a.manifest_sha,"Review pin")
m=json.loads((here/"FILES.json").read_text());actual=set()
for p in here.rglob("*"):
    mode=p.lstat().st_mode
    if stat.S_ISDIR(mode):continue
    need(stat.S_ISREG(mode),"Nonregular review entry");actual.add(p.relative_to(here).as_posix())
need(actual==set(m)|{"FILES.json","FREEZE.json"},"Review roster")
for n,h in m.items():need(sha(here/n)==h,"Review payload")
c=json.loads((here/"CHECK.json").read_text());producer=root/"artifacts/css-hidden-query-repairs-runtime-v1"
need(sha(producer/"DRAFT-FILES.json")==c["draft_sha256"],"Draft pin")
for n,h in c["payloads"].items():need(stat.S_ISREG((producer/n).lstat().st_mode) and sha(producer/n)==h,"Draft payload")
need(sha(root/"artifacts/css-hidden-layout-column-runtime-v1/FILES.json")==c["prior_manifest"],"Prior manifest")
print("PASS: reviewed 29-payload source draft and exact retained oracle; GO bounded diagnostic only")
