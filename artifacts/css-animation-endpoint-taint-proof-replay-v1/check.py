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
for n in ['canonical-final','relocated-output']:
 r=read(n+'/CHECK.json');assert r['axiom_reports']==25 and len(r['modules'])==5 and r['source_bindings']==16
 assert all(c['exit']==0 for c in r['commands'])
 assert len(r['mutations'])==3 and r['mutations'][0]['observed']=='|'.join(['true']*8)
 assert all(x['observed']==x['expected'] and x['compiled'] for x in r['mutations'])
 assert r['mutations'][1]['observed']=='false|true|false|true|true|true|true|true'
 assert r['mutations'][2]['observed']=='true|false|true|false|true|true|true|true'
 assert r['native_execution']==False
g=read('GUARDS.json');assert len(g)==9 and all(x['exit']!=0 and x['no_output'] for x in g)
print('PASS',len(m),'receipt inputs; 25 audits, 2 semantic mutants, 9 guards')
