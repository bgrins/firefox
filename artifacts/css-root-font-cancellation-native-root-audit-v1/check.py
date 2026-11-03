import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b = read(HERE/'BINDINGS.json')
assert not b['execution_enabled'] and b['pending_owner_terminal']
assert all(b[k] is None for k in ('launch','outer_group','owner_manifest_sha256','result_sha256','terminal_sha256'))
for path,pin in b['references'].items():
    assert sha(ROOT/path)==pin
parent=(ROOT/'artifacts/css-keyframe-font-unit-native-root-audit-v2/audit.py').read_text()
source=(HERE/'audit.py').read_text()
expected=parent.replace('css-keyframe-font-unit-candidate-browser-v3','css-root-font-cancellation-candidate-browser-v2').replace('css-keyframe-font-unit-candidate-browser-runtime-v1','css-root-font-cancellation-candidate-browser-runtime-v1').replace("['font_units', 'controls']","['cancellation']").replace('== 61\n','== 8\n').replace('== 5\n','== 1\n')
assert source==expected
compile(source,str(HERE/'audit.py'),'exec')
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='raw_summary')
namespace={'Counter':Counter}
exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-raw-summary','exec'),namespace)
summary=namespace['raw_summary']
want={'/a':['one','two']}
events=[{'action':'suite_start'},{'action':'test_start','test':'/a'},{'action':'test_status','test':'/a','subtest':'one','status':'PASS'},{'action':'test_status','test':'/a','subtest':'two','status':'FAIL'},{'action':'test_end','test':'/a','status':'OK'},{'action':'suite_end'}]
r=summary(events,want)
assert r['complete_raw_roster'] and not r['all_callbacks_pass']
clean=copy.deepcopy(events);clean[3]['status']='PASS'
assert summary(clean,want)['all_callbacks_pass']
crash=events[:2]+[{'action':'test_end','test':'/a','status':'CRASH'}]
assert summary(crash,want)['crash_events']==1 and not summary(crash,want)['complete_raw_roster']
rejected=[]
for label,mutation in [('missing callback',lambda e:e.pop(2)),('duplicate callback',lambda e:e.insert(2,e[2])),('missing start',lambda e:e.pop(1)),('missing suite end',lambda e:e.pop()),('explicit crash',lambda e:e.append({'action':'crash'})),('outside page callback',lambda e:e.insert(0,e.pop(2)))]:
    bad=copy.deepcopy(events);mutation(bad)
    assert not summary(bad,want)['complete_raw_roster'];rejected.append(label)
print(json.dumps({'saved_only':True,'exact_parent_body_except_owner_runtime_lane_totals':True,'raw_scope_positive_cases':3,'rejected_incomplete_streams':rejected,'live_audit_not_executed':True,'future_outcome_pending':True}))
