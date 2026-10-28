import copy
import importlib.util
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[1]
spec = importlib.util.spec_from_file_location('projection',here/'projection.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
p = json.loads((here/'POLICY.json').read_text())
e = root/p['paired_runtime']
read = lambda n:json.loads((e/n).read_text())
args = [read('PRE-CURRENT-EPOCH.json'),read('PRE-OBSERVATION-EPOCH.json'),read('POST-OBSERVATION-EPOCH.json'),read('RAW-INDEX-OBSERVATION.json'),p['source_roles']]
result=m.derive(*args)
expected=copy.deepcopy(args[0]);expected['raw_index_observation']['current']=args[3]['after']
assert result==expected
rejected=0
for target,field in [(1,'pins'),(1,'installed_identities'),(1,'counts'),(2,'pins'),(2,'installed_identities'),(2,'counts'),(2,'semantic_index'),(2,'nested_semantic_index')]:
    changed=copy.deepcopy(args);changed[target][field]['unexpected']='changed'
    try:m.derive(*changed)
    except AssertionError:rejected+=1
    else:raise AssertionError((target,field))
changed=copy.deepcopy(args);changed[4].pop(next(iter(changed[4])))
try:m.derive(*changed)
except AssertionError:rejected+=1
else:raise AssertionError('source roster')
assert rejected==9
print(json.dumps({'saved_actual_projection':True,'negative_controls':rejected,'live_checks':False,'main_executed':False}))
