import ast
from collections import Counter
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=ROOT/'artifacts/css-attr-fallback-candidate-root-audit-v2/audit.py'
source=(HERE/'audit.py').read_text()
old=parent.read_text()
assert (HERE/'AUDIT-DELTA.patch').read_text()==''.join(difflib.unified_diff(old.splitlines(True),source.splitlines(True),fromfile=str(parent.relative_to(ROOT)),tofile=str((HERE/'audit.py').relative_to(ROOT))))
assert source[source.index('processes = []'):source.index('report = {')]==old[old.index('processes = []'):old.index('report = {')]
assert source[source.index('with (RUNTIME / "ROOT-LIVE-RESTORATION.json")'):]==old[old.index('with (RUNTIME / "ROOT-LIVE-RESTORATION.json")'):]
binding=read(HERE/'BINDINGS.json')
assert not binding['execution_enabled'] and binding['pending_owner_terminal']
assert all(binding[k] is None for k in ('result_sha256','terminal_sha256'))
for name,digest in binding['references'].items():assert sha(ROOT/name)==digest
launch=read(ROOT/binding['launch']['path'])
assert sha(ROOT/binding['launch']['path'])==binding['launch']['sha256']
assert launch['pgid']==binding['outer_group']==9316
assert launch['owner_manifest_sha256']==binding['owner_manifest_sha256']
assert sha(ROOT/'artifacts/css-explicit-taint-typed-reparse-candidate-browser-v1/FILES.json')==binding['owner_manifest_sha256']
module=ast.parse(source)
function=next(node for node in module.body if isinstance(node,ast.FunctionDef) and node.name=='raw_summary')
namespace={'Counter':Counter}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(HERE/'audit.py'),'exec'),namespace)
summary=namespace['raw_summary']
positive=0;negative=0
for name in ['css-explicit-attribute-taint-typed-reparse-fix-v1','css-attr-own-fallback-fix-v2','css-explicit-attribute-taint-existing-controls-v1']:
    roster=read(ROOT/'artifacts'/name/'ROSTER.json')
    events=[{'action':'suite_start'}]
    for page,names in roster.items():
        events.append({'action':'test_start','test':page})
        events.extend({'action':'test_status','test':page,'subtest':n,'status':'FAIL' if i==0 else 'PASS'} for i,n in enumerate(names))
        events.append({'action':'test_end','test':page,'status':'OK'})
    events.append({'action':'suite_end'})
    result=summary(events,roster)
    assert result['complete_raw_roster'] and not result['all_callbacks_pass'];positive+=1
    cases=[[e for e in events if e['action']!='suite_end'],events+[events[2]],events+[{'action':'crash'}]]
    for action,field,value in [('test_status','subtest','wrong'),('test_status','status','TIMEOUT'),('test_end','status','CRASH'),('test_start','test','wrong')]:
        bad=copy.deepcopy(events);next(e for e in bad if e['action']==action)[field]=value;cases.append(bad)
    for bad in cases:assert not summary(bad,roster)['complete_raw_roster'];negative+=1
first_guard=next(node for node in module.body if isinstance(node,ast.Assert) and 'pending_owner_terminal' in ast.unparse(node))
second_guard=next(node for node in module.body if isinstance(node,ast.Assert) and "outer_group" in ast.unparse(node))
compiled=compile(ast.Module(body=[first_guard,second_guard],type_ignores=[]),'actual admission assertions','exec')
valid={'execution_enabled':True,'pending_owner_terminal':False,'outer_group':123}
exec(compiled,{'binding':valid});positive+=1
for key,value in [('execution_enabled',False),('pending_owner_terminal',True),('outer_group',None),('outer_group',0),('outer_group',-1),('outer_group','123')]:
    bad=dict(valid);bad[key]=value
    try:exec(compiled,{'binding':bad})
    except AssertionError:negative+=1
    else:raise AssertionError('bad admission accepted')
print(json.dumps({'success':True,'positives':positive,'negatives':negative,'exact_restoration_core':True,'exact_exclusive_report_writer':True,'audit_execution':False,'live_state_reads':False,'pending_actual_owner_terminal':True}))
