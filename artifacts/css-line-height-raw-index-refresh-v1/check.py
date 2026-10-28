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
pre['pins']['font'] = 'font-base'
post = copy.deepcopy(pre)
post['raw_index_observation']['current'] = 'new'
raw = {'before':'old','after':'new','semantic_index_unchanged':True,'runtime_epoch_updated':False}
expected = copy.deepcopy(old)
expected['raw_index_observation']['current'] = 'new'
assert m.derive(old,pre,post,raw) == expected
same = dict(raw,after='old')
assert m.derive(old,pre,pre,same) == old
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
