import copy
import importlib.util
import json
from pathlib import Path

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('projection', here/'projection.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
old = {'staged_working':{},'raw_index_observation':{'current':'old','prior':'historical'},'pins':{'source':'source','binary':'binary'},'semantic_index':{'head':'head','entries':'entries','cached_diff':'empty'},'nested_semantic_index':{'entries':'nested'}}
pre = copy.deepcopy(old)
pre['raw_index_observation']['current'] = 'observed'
post = copy.deepcopy(pre)
post['raw_index_observation']['current'] = 'new'
raw = {'canonical_epoch_raw':'old','before':'observed','after':'new','semantic_index_unchanged':True,'runtime_epoch_updated':False}
expected = copy.deepcopy(old)
expected['raw_index_observation']['current'] = 'new'
assert m.derive(old,pre,post,raw) == expected
same = dict(raw,after='observed')
assert m.derive(old,pre,pre,same) == pre
rejected = 0
for field in ('pins','semantic_index','nested_semantic_index'):
 altered = copy.deepcopy(post)
 altered[field]['unexpected'] = 'changed'
 try:
  m.derive(old,pre,altered,raw)
 except AssertionError:
  rejected += 1
 else:
  raise AssertionError(field)
for key,value in [('before','wrong'),('semantic_index_unchanged',False),('runtime_epoch_updated',True)]:
 altered = dict(raw,**{key:value})
 try:
  m.derive(old,pre,post,altered)
 except AssertionError:
  rejected += 1
 else:
  raise AssertionError(key)
assert rejected == 6
print(json.dumps({'positive_controls':2,'negative_controls':rejected,'main_executed':False,'live_checks':False}))

root=here.parents[1]
e=root/'artifacts/css-random-grid-typecheck-runtime-4'
read=lambda n:json.loads((e/n).read_text())
a=m.derive(read('PRE-CURRENT-EPOCH.json'),read('OBSERVATION-EPOCH.json'),read('POST-OBSERVATION-EPOCH.json'),read('RAW-INDEX-OBSERVATION.json'))
assert a==read('POST-OBSERVATION-EPOCH.json')
print('Actual saved epoch projection passed; no live checks')
