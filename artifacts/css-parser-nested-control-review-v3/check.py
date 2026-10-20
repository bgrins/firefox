import sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError('use -I -S without optimization')
from pathlib import Path
import hashlib,json,os,stat
r=Path(__file__).resolve().parent
m=json.loads((r/'FILES.json').read_text());actual=set()
for base,dirs,files in os.walk(r):
 for n in dirs:
  if not stat.S_ISDIR((Path(base)/n).lstat().st_mode):raise RuntimeError('invalid directory')
 for n in files:
  p=Path(base)/n
  if not stat.S_ISREG(p.lstat().st_mode):raise RuntimeError('invalid file')
  actual.add(p.relative_to(r).as_posix())
if actual!=set(m)|{'FILES.json','FREEZE.json'}:raise RuntimeError('roster mismatch')
for n,h in m.items():
 if hashlib.sha256((r/n).read_bytes()).hexdigest()!=h:raise RuntimeError('hash mismatch '+n)
f=json.loads((r/'FREEZE.json').read_text())
if hashlib.sha256((r/'FILES.json').read_bytes()).hexdigest()!=f['files_sha256']:raise RuntimeError('seal mismatch')
result=json.loads((r/'replay-output/RESULT.json').read_text())
if not(result['complete'] and result['audits']==39 and result['compiled_modules']==59 and result['cases']==18 and result['snapshots']==91):raise RuntimeError('result mismatch')
if result['native_mutants']!={'nested-union-outer-stop':10,'nested-omit-final-consume':25,'until-ignore-stop-error':5}:raise RuntimeError('mutant mismatch')
model=(r/'replay-output/model.txt').read_text()
for mode in ['debug','release']:
 if (r/('replay-output/native-'+mode)/'raw.txt').read_text()!=model:raise RuntimeError('native mismatch')
import re
names=json.loads((r/'relocated-source/AUDIT-NAMES.json').read_text())
actual=re.findall(r"'([^']+)' (?:depends on axioms:|does not depend on any axioms)",(r/'replay-output/AUDIT.txt').read_text())
if actual!=names or len(set(names))!=39:raise RuntimeError('audit mismatch')
guards=json.loads((r/'GUARDS.json').read_text())
if len(guards)!=21:raise RuntimeError('guard count')
for row in guards:
 if not row['output_absent'] or ((row['exit']==0)!=(row['case']=='intact-help')) or 'NESTED_SHADOW_BEFORE_GUARD' in row['stdout']+row['stderr']:raise RuntimeError('guard mismatch')
if json.loads((r/'MUTANT-CAUSE-KERNEL.json').read_text())['exit']!=0:raise RuntimeError('kernel mismatch')
print('PASS independent scoped nested-control v3 review')
