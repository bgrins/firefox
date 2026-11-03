import copy
import importlib.util
import json
from pathlib import Path
import sys
import contextlib
import io

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
 for path,pin in p['references'].items(): assert m.sha(m.ROOT/path)==pin
 runtime=m.ROOT/p['runtime']
 pre,post,raw=(m.read(runtime/name) for name in ('PAIR-PRE.json','POST.json','RAW-INDEX-OBSERVATION.json'))
 terminal=m.read(runtime/'ROOT-OWNER-TERMINAL.json')
 assert terminal==p['actual_owner_terminal'] and terminal['result_sha256']==m.sha(runtime/'RESULT.json')
else:
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
for key in ([] if p['pending_runtime_binding'] else ['live_audit','audit_terminal','runtime_manifest_sha256','owner_terminal'] + (['cleanup'] if p['cleanup'] is not None else [])):
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
parent=(m.ROOT/'artifacts/css-resumable-minimum-font-diagnostic-raw-index-refresh-v2/run.py').read_text()
current_source=(HERE/'run.py').read_text()
for name,next_name in [('derive','admit_current_raw'),('admit_current_raw','saved')]:
 old=parent[parent.index('def '+name+'('):parent.index('def '+next_name+'(')]
 end=next_name
 new=current_source[current_source.index('def '+name+'('):current_source.index('def '+end+'(')]
 assert old==new
tail="    claims = {n:owner.claim"
assert parent[parent.index(tail):].replace('native-authority minimum-font diagnostic restored raw observation refresh','native-authority explicit-taint candidate restored raw observation refresh')==current_source[current_source.index(tail):]
start=current_source.index("    if actual_index['raw_index'] == epoch['raw_index_observation']['current']:")
end=current_source.index("    output = ROOT / policy['output']",start)
assert current_source.index('assert not lock.exists()') < start < current_source.index('output.mkdir()')
namespace={'json':json,'digest':m.digest}
exec("def branch(actual_index,epoch,policy,controls):\n"+current_source[start:end]+"    return 'write-required'\n",namespace)
with contextlib.redirect_stdout(io.StringIO()) as captured:
 assert namespace['branch']({'raw_index':'same'},{'raw_index_observation':{'current':'same'}},p,{'CURRENT-EPOCH.json':b'epoch'}) is None
assert json.loads(captured.getvalue())['updated'] is False
assert namespace['branch']({'raw_index':'different'},{'raw_index_observation':{'current':'same'}},p,{'CURRENT-EPOCH.json':b'epoch'})=='write-required'
print(json.dumps({'saved_restoration_authenticated':not p['pending_runtime_binding'],'pending_runtime_rejected':p['pending_runtime_binding'],'raw_before':raw['before'],'raw_after':raw['after'],'negative_checks':negative,'only_changed_field':'raw_index_observation.current','live_state_read':False,'publication_executed':False}))
