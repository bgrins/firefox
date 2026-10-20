import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
state=json.loads((HERE/'STATE.json').read_text());run=json.loads((HERE/'installed/RUN.json').read_text())
assert state['status']=='terminal' and state['installed'] and state['build_exit']==0
assert state['head_unchanged'] and state['index_unchanged']
assert run['exit']==0 and run['complete'] and run['before']==run['after']
for n,h in run['before'].items():
 if h is not None and not n.startswith('objdir-full.noindex/'):
  assert hashlib.sha256((HERE/'installed/inputs'/n).read_bytes()).hexdigest()==h,n
assert len(run['rows'])==510 and all(r['status']=='PASS' for r in run['rows'])
assert len({(r['test'],r['subtest']) for r in run['rows']})==510
assert len(run['ends'])==4 and all(r['status']=='OK' for r in run['ends'])
expected={'relative-position-overflow-continuations.html':140,'table-caption-percentage-height-resize.html':16,'flexbox-overflow-container-final-position.html':336,'flexbox-baseline-percentage-padding-resize.html':18}
for name,count in expected.items():assert sum(r['test'].endswith('/'+name) for r in run['rows'])==count
print(json.dumps({'installed':True,'build_exit':0,'passing_subtests':510,'files':4,'head_index_unchanged':True,'counts':expected},indent=2))
