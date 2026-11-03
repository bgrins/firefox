import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'artifacts/css-root-font-cancellation-observer-v1'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
for path,pin in read(HERE/'REFERENCES.json').items():assert sha(ROOT/path)==pin
assert (HERE/'BINDINGS.json').read_bytes()==(PARENT/'BINDINGS.json').read_bytes()
b=read(HERE/'BINDINGS.json');assert not b['execution_enabled']
assert all(b[k] is None for k in ('owner_manifest','runtime_manifest','owner_terminal','owner_result','build_result','restoration'))
old=(PARENT/'compare.py').read_text();new=(HERE/'compare.py').read_text()
old_nodes=ast.parse(old).body;new_nodes=ast.parse(new).body
for node in old_nodes:
    if isinstance(node,ast.FunctionDef) and node.name!='main':
        found=next(n for n in new_nodes if isinstance(n,ast.FunctionDef) and n.name==node.name)
        assert ast.dump(node,include_attributes=False)==ast.dump(found,include_attributes=False)
assert (HERE/'PARENT-DELTA.patch').read_text()==''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str((PARENT/'compare.py').relative_to(ROOT)),tofile=str((HERE/'compare.py').relative_to(ROOT))))
module=load('observer',HERE/'compare.py')
assessor=load('actual_signature',ROOT/b['baseline']['directory']/'assess.py')
raw=read(ROOT/b['baseline']['path']);assert sha(ROOT/b['baseline']['path'])==b['baseline']['sha256']
baseline={'rows':[assessor.signature(r) for r in raw['rows']],'ends':[assessor.signature(r) for r in raw['endings']]}
rows=copy.deepcopy(baseline['rows'])
for row in rows:
    if row['status']=='FAIL':row.update(status='PASS',expected='PASS',expected_field_present=False,message=None,message_field_present=False)
report=module.compare_signatures(baseline,rows,baseline['ends'],True)
assert report['witness_closed_under_known_fix']
owner={'success':True,'error':None};phase={'success':True,'execution_error':None}
assert module.finish_observation(report,owner,[phase])['witness_closed_under_known_fix']
blocked=[]
for label,o,phases in [
    ('full PASS with owner error',dict(owner,error='owner cleanup exception'),[phase]),
    ('full PASS with phase error',owner,[dict(phase,execution_error='phase exception')]),
    ('full PASS with owner unsuccessful',dict(owner,success=False),[phase]),
    ('full PASS with phase unsuccessful',owner,[dict(phase,success=False)]),
    ('full PASS with no recorded phase',owner,[])]:
    before=copy.deepcopy((report,o,phases));actual=module.finish_observation(report,o,phases)
    assert actual['observation_complete'] and not actual['execution_successful'] and not actual['witness_closed_under_known_fix']
    assert actual['rows']==report['rows'] and actual['endings']==report['endings']
    assert (report,o,phases)==before
    blocked.append(label)
failed=module.compare_signatures(baseline,baseline['rows'],baseline['ends'],True)
actual=module.finish_observation(failed,owner,[phase])
assert actual['observation_complete'] and actual['execution_successful'] and not actual['witness_closed_under_known_fix']
assert actual['candidate_statuses']=={'PASS':6,'FAIL':2} and len(actual['remaining_failures'])==2
incomplete=module.compare_signatures(baseline,[],[],False)
assert not module.finish_observation(incomplete,owner,[phase])['witness_closed_under_known_fix']
assert not (HERE/'RESULT.json').exists()
print(json.dumps({'saved_only':True,'positive_scope_cases':3,'closure_blocking_controls':blocked,'inherited_stream_suite_not_rerun':True,'future_runtime_pending':True,'live_operations':False}))
