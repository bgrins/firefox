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
for kind in ['baseline','project']:
 r=json.loads((p/kind/'RESULT.json').read_text());assert r['stable'] and r['before']==r['after'] and r['profile_removed']
 a=r['observations'][0]['rows'];assert len(a)==8 and all(x['calibrated'] for x in a)
 assert all(x['geometryOK']==(kind=='project') for x in a)
lastmark=None; ancestry=None; visits=0; cleanmarks=0; branches=0
for line in (p/'project/browser.log').read_text().splitlines():
 if line.startswith('COLUMN_TRACE mark '):
  lastmark=dict(x.split('=',1) for x in line.split()[2:]);cleanmarks+=lastmark['dirty']=='0'
 elif line.startswith('OC_ANCESTRY '):
  ancestry=dict(x.split('=',1) for x in line.split()[1:]);assert ancestry['parent']==lastmark['child']
 elif line.startswith('OC_TRACE pre '):
  v=dict(x.split('=',1) for x in line.split()[2:]);visits+=1
  assert v['parent']==ancestry['flex'] and v['pd']==v['dirty']==v['all']=='1'
  assert v['ir']==v['rel']=='0' and v['br']=='1'
 elif line.startswith('OC_TRACE branch='):
  assert line.startswith('OC_TRACE branch=reflow ');branches+=1
assert visits==branches==24 and cleanmarks==18
print('Eight calibrated external-resize stages; 24 reflows linked to column dirty propagation; no skip observed')
