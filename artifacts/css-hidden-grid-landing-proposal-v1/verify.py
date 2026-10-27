import hashlib,json,stat,difflib
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/'FILES.json').read_text())
a={str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir()}-{'FILES.json','FREEZE.json'}
if a!=set(m):raise SystemExit('roster')
for n,h in m.items():
 f=p/n
 if not stat.S_ISREG(f.lstat().st_mode) or hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise SystemExit(n)
c=json.loads((p/'EXPERIMENT-PLAN.json').read_text())
if len(c['phases'])!=2 or len(c['sources_to_snapshot_restore'])!=24 or len(c['guard_sources'])!=29:raise SystemExit('plan')
if len(json.loads((p/'EXPECTED-ROSTER.json').read_text()))!=8:raise SystemExit('tests')
print('PASS',len(m),'payloads; two planned phases; eight tests')
