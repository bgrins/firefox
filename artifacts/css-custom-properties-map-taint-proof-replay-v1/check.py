import hashlib,json,sys
from pathlib import Path
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize): raise RuntimeError("use -I -S without -O")
p=Path(__file__).resolve().parent
def h(f): return hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'MANIFEST.json').read_text());s=json.loads((p/'FREEZE.json').read_text())
assert h(p/'MANIFEST.json')==s['manifest_sha256']
assert set(m)|{'MANIFEST.json','FREEZE.json'}=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}
assert all(not f.is_symlink() for f in p.rglob('*'))
for n,v in m.items(): assert h(p/n)==v,n
for n in ['canonical-sealed','relocated-sealed-output']:
 r=json.loads((p/n/'CHECK.json').read_text());assert r['axiom_reports']==31 and r['source_bindings']==27 and len(r['mutations'])==5
 assert all(c['exit']==0 for c in r['commands'])
 assert r['mutations'][0]['observed']=='|'.join(['true']*7)
 assert all(x['observed']!=r['mutations'][0]['observed'] and x['compiled_definitions'] for x in r['mutations'][1:])
g=json.loads((p/'GUARDS.json').read_text());assert len(g)==9 and all(x['exit']!=0 and x['no_output'] for x in g)
print('PASS',len(m),'receipt inputs; 31 audits, 4 semantic mutants, 9 guards')
