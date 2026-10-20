import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
import json,hashlib,stat
from pathlib import Path
R=Path(__file__).resolve().parent
def pairs(items):
 d={}
 for k,v in items:
  assert k not in d
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=read(R/'FREEZE.json');assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=read(R/'MANIFEST.json');files=set(m)|{'MANIFEST.json','FREEZE.json'};dirs=set()
for n in files:
 p=Path(n);assert not p.is_absolute() and '..' not in p.parts and str(p)==n
 dirs.update(str(q) for q in p.parents if str(q)!='.')
af=set();ad=set()
for p in R.rglob('*'):
 assert not p.is_symlink();mode=p.stat().st_mode
 if stat.S_ISDIR(mode):ad.add(str(p.relative_to(R)))
 else:assert stat.S_ISREG(mode);af.add(str(p.relative_to(R)))
assert af==files and ad==dirs
for n,h in m.items():assert sha(R/n)==h,n
r=read(R/'RESULT.json');assert r['status']=='ACCEPT_SCOPED_MODEL' and r['producer_inputs']==49
p=r['producer_result'];assert p['axiom_reports']==23 and p['source_bindings']==14 and p['native_execution'] is False
assert all(x['exit']==0 for x in p['commands'])
assert len(p['mutations'])==2 and all(x['compiled'] for x in p['mutations'])
assert p['mutations'][0]['observed']=='|'.join(['true']*10)
assert p['mutations'][1]['observed']=='false|false|false|false|true|true|true|true|true|true'
assert len(r['guards'])==6 and all(x['exit']!=0 and x['rejected_before_output'] for x in r['guards'])
assert r['independent_axioms'].count('depends on axioms: [propext]')==6
assert r['independent_axioms'].count('does not depend on any axioms')==1
print(json.dumps({'status':'PASS','review_inputs':len(m),'producer_inputs':49,'producer_audits':23,'independent_witnesses':7,'guards':6,'verdict':'ACCEPT_SCOPED_MODEL'}))
