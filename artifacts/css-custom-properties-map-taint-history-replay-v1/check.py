import hashlib,json,sys
from pathlib import Path
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError('use -I -S without -O')
p=Path(__file__).resolve().parent
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def read(n):return json.loads((p/n).read_text())
m=read('MANIFEST.json');s=read('FREEZE.json')
assert h(p/'MANIFEST.json')==s['manifest_sha256']
assert all(not f.is_symlink() for f in p.rglob('*'))
assert set(m)|{'FREEZE.json','MANIFEST.json'}=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}
for n,v in m.items():assert h(p/n)==v,n
for n in ['canonical','relocated-output']:
 r=read(n+'/CHECK.json');assert r['new_axiom_reports']==9 and len(r['compiled_modules'])==13
 assert all(c['exit']==0 for c in r['commands'])
 assert len(r['mutations'])==4 and r['mutations'][0]['observed']=='|'.join(['true']*7)
 assert all(x['observed']==x['expected'] and x['compiled'] for x in r['mutations'])
 assert all(x['observed']!=r['mutations'][0]['observed'] for x in r['mutations'][1:])
 assert r['native_execution']==False
g=read('GUARDS.json');assert len(g)==9 and all(x['exit']!=0 and x['no_output'] for x in g)
print('PASS',len(m),'receipt inputs; 9 new audits, 3 semantic mutants, 9 guards')
