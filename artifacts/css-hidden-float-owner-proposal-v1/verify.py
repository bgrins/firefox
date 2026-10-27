import hashlib,json,stat,difflib
from pathlib import Path
p=Path(__file__).resolve().parent
m=json.loads((p/'FILES.json').read_text())
a={str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir()}-{'FILES.json','FREEZE.json'}
if a!=set(m):raise SystemExit('roster')
for n,h in m.items():
 f=p/n
 if not stat.S_ISREG(f.lstat().st_mode) or hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise SystemExit(n)
a=(p/'before-nsBlockFrame.cpp').read_text();b=(p/'candidate-nsBlockFrame.cpp').read_text()
d=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/layout/generic/nsBlockFrame.cpp',tofile='b/layout/generic/nsBlockFrame.cpp'))
if d!=(p/'candidate.patch').read_text():raise SystemExit('patch')
print('PASS',len(m),'payloads; exact patch')
