from pathlib import Path
import hashlib,json,stat
p=Path(__file__).resolve().parent
m=json.loads((p/'FILES.json').read_text())
a={str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir()}-{'FILES.json','FREEZE.json'}
if a!=set(m):raise SystemExit('roster')
for n,h in m.items():
 f=p/n
 if not stat.S_ISREG(f.lstat().st_mode) or hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise SystemExit(n)
r=json.loads((p/'EXPECTED-ROSTERS.json').read_text())
if sorted(map(len,r.values()))!=[4,12]:raise SystemExit('case roster')
print('PASS',len(m),'payloads; main12 + separate calibration4')
