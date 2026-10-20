import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
s=json.loads((p/'STATE.json').read_text());assert s['status']=='terminal' and not s['accepted']
assert all(s[k]==0 for k in ['candidate_build_exit','diagnostic_exit','restore_build_exit'])
assert all(s[k] for k in ['source_restored','head_unchanged','index_unchanged'])
r=json.loads((p/'project/RESULT.json').read_text());assert r['stable'] and r['before']==r['after'] and r['profile_removed']
a=r['observations'][0]['rows'];assert len(a)==4
assert all(x['descendants']==[[i*100,0,100,160] for i in range(4)] for x in a)
lines=(p/'project/browser.log').read_text().splitlines()
pre=[dict(x.split('=',1) for x in s.split()[2:]) for s in lines if s.startswith('OC_TRACE pre ')]
assert len(pre)==12 and all(x['pd']==x['dirty']==x['all']=='1' for x in pre)
assert sum(s.startswith('OC_TRACE branch=reflow') for s in lines)==12
assert not any(s.startswith('OC_TRACE branch=skip') for s in lines)
print('12 reflow visits; no skipped visit; restoration verified')
