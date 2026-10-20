import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((p/'FILES.json').read_text());f=json.loads((p/'FREEZE.json').read_text())
assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(m)|{'FILES.json','FREEZE.json'}
assert all(sha(p/k)==v for k,v in m.items()) and sha(p/'FILES.json')==f['files_sha256']
rows=[]
for kind in ['release','project']:
 r=json.loads((p/kind/'RESULT.json').read_text());assert r['stable'] and r['before']==r['after'] and r['profile_removed']
 a=r['observations'][0]['rows'];assert len(a)==30
 assert all(x['calibrated'] and x['sizesPreserved'] and x['translationMatches'] and x['otherItemsUnchanged'] and x['restoredExactly'] for x in a);rows.append(a)
assert rows[0]==rows[1]
print('30 paired horizontal offset-mutation controls all pass; initial nonzero layout remains separate')
