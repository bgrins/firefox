import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
s=json.loads((p/'STATE.json').read_text());assert s['status']=='terminal' and not s['accepted']
assert s['candidate_build_exit']==s['restore_build_exit']==s['candidate']['exit']==0
assert all(s[k] for k in ['source_restored','head_unchanged','index_unchanged'])
runs=[]
for kind in ['baseline','candidate']:
 r=json.loads((p/kind/'RUN.json').read_text());assert r['complete'] and r['before']==r['after']
 raw=[json.loads(line) for line in (p/kind/'raw.json').read_text().splitlines()]
 assert [x for x in raw if x.get('action')=='test_status']==r['rows']
 assert [x for x in raw if x.get('action')=='test_end']==r['ends']
 assert len(r['ends'])==35 and len(r['rows'])==336; runs.append(r)
assert {x['test']:x['status'] for x in runs[0]['ends']}=={x['test']:x['status'] for x in runs[1]['ends']}
assert sum(x['status']=='FAIL' for x in runs[1]['ends'])==10
assert sum(x['status']=='PASS' for x in runs[1]['ends'])==24
assert sum(x['status']=='FAIL' for x in runs[0]['rows'])==112
assert all(x['status']=='PASS' for x in runs[1]['rows'])
assert {n:h for n,h in runs[0]['before'].items() if n.startswith('testing/')}=={n:h for n,h in runs[1]['before'].items() if n.startswith('testing/')}
print('34 existing outcomes unchanged; 336 candidate subtests pass; ten existing failures remain explicit')
