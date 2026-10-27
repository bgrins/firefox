import hashlib,json,stat,difflib
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((p/'FILES.json').read_text())
a={str(f.relative_to(p)) for f in p.rglob('*') if not f.is_dir()}-{'FILES.json','FREEZE.json'}
if a!=set(m):raise SystemExit('roster mismatch')
for n,h in m.items():
 f=p/n
 if not stat.S_ISREG(f.lstat().st_mode) or sha(f.read_bytes())!=h:raise SystemExit(n)
b=(p/'head/nsGridContainerFrame.cpp').read_text();c=(p/'candidate-nsGridContainerFrame.cpp').read_text()
old='  if (HidesContentForLayout()) {\n    return bSize;\n  }'
new='  if (HidesContentForLayout()) {\n    MarkPrincipalChildrenDirty();\n    return bSize;\n  }'
if b.count(old)!=1 or c!=b.replace(old,new):raise SystemExit('candidate delta')
d=''.join(difflib.unified_diff(b.splitlines(True),c.splitlines(True),fromfile='a/layout/generic/nsGridContainerFrame.cpp',tofile='b/layout/generic/nsGridContainerFrame.cpp'))
if d!=(p/'candidate.patch').read_text():raise SystemExit('patch')
for n in ['nsGridContainerFrame.cpp','nsContainerFrame.cpp']:
 if (p/'head'/n).read_bytes()!=(p/'working'/n).read_bytes():raise SystemExit('source role')
print('PASS',len(m),'payloads; exact one-call candidate; local/HEAD source equality')
