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
 a=r['observations'][0]['rows'];assert len(a)==90;rows.append(a)
 assert all(x['freshAndDynamicComputedEqual'] and x['dynamicTranslationMatches'] and x['allSizesPreserved'] and x['otherItemsUnchanged'] and x['restoredExactly'] for x in a)
 assert sum(x['calibrated'] for x in a)==80
 assert sum(not x['freshAndDynamicGeometryEqual'] for x in a)==20
 assert sum(x['calibrated'] and not x['freshAndDynamicGeometryEqual'] for x in a)==16
 assert all(x['freshAndDynamicGeometryEqual'] for x in a if x['kind']=='normal')
 assert sum(x['writingMode']=='horizontal-tb' and not x['freshAndDynamicGeometryEqual'] for x in a)==6
assert rows[0]==rows[1]
print('90 paired rows; 16 calibrated fresh/dynamic discrepancies, including six independent horizontal cases')
