import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('refresh',HERE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.read(HERE/'POLICY.json')
assert not p['execution_enabled']
if p['pending_runtime_binding']:
 try:m.saved(p)
 except AssertionError as exc:assert str(exc)=='Completed paired runtime binding is pending'
 else:raise AssertionError('pending runtime admitted')
 print(json.dumps({'pending_runtime_rejected':True,'execution_disabled':True,'live_state_read':False}))
 raise SystemExit(0)
owner,review,pre,post,raw=m.saved(p)
epoch={'semantic_index':{k:v for k,v in pre['snapshot']['index'].items() if k!='raw_index'},'raw_index_observation':{'current':raw['before'],'sentinel':'retained'},'pins':{'sentinel':'unchanged'},'counts':{'sentinel':1}}
updated=m.derive(epoch,pre['snapshot'],post,raw)
expected=copy.deepcopy(epoch);expected['raw_index_observation']['current']=raw['after']
assert updated==expected and epoch['raw_index_observation']['current']==raw['before']
negative=0
for key,value in [('before','wrong'),('after','wrong'),('semantic_index_unchanged',False),('canonical_updated',True)]:
 changed=copy.deepcopy(raw);changed[key]=value
 try:m.derive(epoch,pre['snapshot'],post,changed)
 except AssertionError:negative+=1
 else:raise AssertionError(key)
changed=copy.deepcopy(post);changed['index']['entries']='wrong'
try:m.derive(epoch,pre['snapshot'],changed,raw)
except AssertionError:negative+=1
else:raise AssertionError('semantic mutation admitted')
for key in ['live_audit','audit_terminal','cleanup','runtime_manifest_sha256','owner_terminal']:
 changed=copy.deepcopy(p);changed[key]=None
 try:m.saved(changed)
 except (AssertionError,TypeError,RuntimeError):negative+=1
 else:raise AssertionError(key)
actual_index = copy.deepcopy(post['index']); actual_index['raw_index'] = 'f' * 64
current, expected = m.admit_current_raw(updated, post, actual_index)
assert current['raw_index_observation']['current'] == expected['index']['raw_index'] == 'f' * 64
assert updated['raw_index_observation']['current'] == post['index']['raw_index'] == raw['after']
current_expected = copy.deepcopy(updated); current_expected['raw_index_observation']['current'] = 'f' * 64
post_expected = copy.deepcopy(post); post_expected['index']['raw_index'] = 'f' * 64
assert current == current_expected and expected == post_expected
for key in ('head','entries','cached_diff','working_diff'):
 changed = copy.deepcopy(actual_index); changed[key] = 'wrong'
 try:m.admit_current_raw(updated,post,changed)
 except AssertionError:negative += 1
 else:raise AssertionError('fresh observation admitted changed '+key)
print(json.dumps({'saved_restoration_authenticated':True,'raw_before':raw['before'],'raw_after':raw['after'],'negative_checks':negative,'only_changed_field':'raw_index_observation.current','live_state_read':False,'publication_executed':False}))
