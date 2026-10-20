import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
observations=[]
for kind in ['release','project']:
 d=json.loads((HERE/kind/'RESULT.json').read_text())
 assert d['stable'] and d['before']==d['after'] and d['profile_removed']
 assert len(d['observations'])==1
 o=d['observations'][0];assert o['count']==len(o['rows'])==16 and o['lastBaselineSupported']
 keys={(r['alignment'],r['kind'],r['caption'],r['from'],r['to']) for r in o['rows']};assert len(keys)==16
 for r in o['rows']:
  assert all(r[k] for k in ['beforeCalibrated','restoreStable','repeatStable'])
  expected_failure=r['kind']=='percent' and r['caption']=='auto-caption'
  assert r['warmMatchesFresh'] == (not expected_failure)
  for name in ['before','warm','reference','restored','repeated']:
   assert r[name]['captionHeight']==20 and r[name]['tableWidth']==100 and r[name]['hostWidth']==240
  if expected_failure:
   assert r['warm']['computedHeight']==str(r['from']//2)+'px'
   assert r['reference']['computedHeight']==str(r['to']//2)+'px'
   assert r['warm']['tableHeight']==r['from']/2+20
   assert r['reference']['tableHeight']==r['to']/2+20
 assert o['discrepancies']==4
 observations.append(o)
assert observations[0]==observations[1]
print(json.dumps({'rows_per_browser':16,'discrepancies':4,'controls':12,'initial_restore_repeat_controls_each':16,'release_project_identical':True,'profiles_removed':True},indent=2))
