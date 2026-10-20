import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
s=json.loads((p/'STATE.json').read_text());assert s['status']=='terminal' and not s['accepted']
assert s['candidate_build_exit']==s['candidate_browser_exit']==s['restore_build_exit']==0
assert all(s[k] for k in ['source_restored','head_unchanged','index_unchanged'])
rows=[]
for kind in ['release','baseline','candidate']:
 r=json.loads((p/kind/'RESULT.json').read_text());assert r['stable'] and r['before']==r['after'] and r['profile_removed']
 a=r['observations'][0]['rows'];assert len(a)==30 and all(x['sizesCalibrated'] for x in a);rows.append(a)
assert rows[0]==rows[1]
assert all(a['actual']==b['actual'] for a,b in zip(rows[1],rows[2]) if a['childMode']!='vertical-rl')
assert sum(x['sameModeOracleMatches'] is True for x in rows[2])==6
assert sum(x['sameModeOracleMatches'] is False for x in rows[2])==4
assert all(a['blockReference']==b['blockReference'] for a,b in zip(rows[1],rows[2]))
print('30 three-build rows; 20 opposite/orthogonal controls preserved; relative block-offset lead remains separate')
