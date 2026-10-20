import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
s=json.loads((p/'STATE.json').read_text());assert s['status']=='terminal' and not s['accepted']
assert all(s[k]==0 for k in ['candidate_build_exit','candidate_browser_exit','restore_build_exit'])
assert all(s[k] for k in ['source_restored','head_unchanged','index_unchanged'])
rows=[]
for kind in ['baseline','candidate']:
 r=json.loads((p/kind/'RESULT.json').read_text());assert r['stable'] and r['before']==r['after'] and r['profile_removed']
 a=r['observations'][0]['rows'];assert len(a)==8
 assert all(x['expected']==[[i*100,0,100,160] for i in range(len(x['descendants']))] for x in a);rows.append(a)
assert sum(x['descendants']!=x['expected'] for x in rows[0])==7
assert all(x['descendants']==x['expected'] for x in rows[1])
assert all(len(a['fragments'])==len(b['fragments']) for a,b in zip(*rows))
print('Eight calibrated lifecycle stages; seven baseline failures corrected; restoration verified')
