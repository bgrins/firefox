import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
s=json.loads((p/'STATE.json').read_text());assert s['status']=='terminal' and not s['accepted']
assert s['candidate_build_exit']==s['restore_build_exit']==0
assert all(s[k] for k in ['source_restored','head_unchanged','index_unchanged'])
sets=[]
for kind in ['baseline','candidate']:
 r=json.loads((p/kind/'RUN.json').read_text());assert r['complete'] and r['before']==r['after']
 events=[json.loads(line) for line in (p/kind/'raw.json').read_text().splitlines()]
 a=[x for x in events if x.get('action')=='test_status'];assert len(a)==336
 assert a==r['rows'];sets.append({x['subtest']:x['status'] for x in a})
assert sets[0].keys()==sets[1].keys()
assert sum(x=='FAIL' for x in sets[0].values())==112 and all(x=='PASS' for x in sets[1].values())
assert sum(x=='PASS' for x in sets[0].values())==224
print('336 paired WPT observations; 112 failures corrected and 224 passes preserved; acceptance open')
