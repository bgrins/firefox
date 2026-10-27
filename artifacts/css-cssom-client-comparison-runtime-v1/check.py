import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,why):
    if not ok:
        raise RuntimeError(why)
def authenticate(mapping,root):
    for n,h in mapping.items():
        assert sha(root/n)==h,n
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
c=read(HERE/'CONFIG.json')
assert not c['ready_for_execution'] and c['epoch'] is None and c['epoch_receipt'] is None
authenticate(read(HERE/'REFERENCES.json'),ROOT)
for n in ['run.py','tests.py','reuse.py','epoch_gate.py','baseline_gate.py','check.py']:
    compile((HERE/n).read_text(),n,'exec')
assert len(c['guard_sources'])==48 and len(c['sources'])==31 and len(c['modified_native_paths'])==25
assert len(c['install'])==1 and len(c['candidate_sources'])==2
assert len(c['baseline_tests'])==8 and sum(map(len,c['baseline_expected_subtests'].values()))==29
assert len(c['tests'])==21 and sum(map(len,c['expected_subtests'].values()))==170
assert sum(len(c['expected_subtests'][n]) for n in c['main_tests'])==40
assert len(set(c['tests']))==21
old=ROOT/'artifacts/css-cssom-offset-scroll-comparison-v1'
a=(HERE/'run.py').read_text();b=(old/'run.py').read_text();marker="finally:\n    state.update(status='restoring'"
assert a[a.index(marker):]==b[b.index(marker):]
for signature in ['replace_source']:
    fn=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==signature)
    assert ast.dump(fn(a),include_attributes=False)==ast.dump(fn(b),include_attributes=False)
assert (HERE/'baseline_gate.py').read_bytes()==(old/'baseline_gate.py').read_bytes()
fn=lambda text:next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='installed_epoch')
assert ast.dump(fn((HERE/'epoch_gate.py').read_text()),include_attributes=False)==ast.dump(fn((ROOT/'artifacts/css-cssom-client-precision-installed-draft-v1/run.py').read_text()),include_attributes=False)
e=load('epoch_check',HERE/'epoch_gate.py');expected,pins,ic,installation=e.installed_epoch(ROOT/'artifacts/css-cssom-offset-scroll-install-runtime-v1')
assert c['source_pins']=={**expected['sources'],'dom/base/Element.h':pins['dom/base/Element.h']}
assert c['modified_native_paths']==ic['modified_native_paths']
resources=read(HERE/'RESOURCES.json');owned,fixture=next(iter(c['install'].items()))
phase={**resources,**c['head_pins'],**c['baseline_pins'],owned:sha(HERE/fixture)}
class Wpt:
    CONFIG=c
    ROOT=ROOT
    HERE=HERE
    need=staticmethod(need)
    receipts={}
    @staticmethod
    def save(n,v):
        Wpt.receipts[n]=v
wpt=Wpt();reuse=load('reuse_check',HERE/'reuse.py')
retained=reuse.validate(wpt,load,sha,authenticate,phase)
assert len(retained['rows'])==141
negative=0
def rejected(call):
    global negative
    try:
        call()
    except (RuntimeError,AssertionError):
        negative+=1
    else:
        raise AssertionError('negative accepted')
for key,value in [('dom/base/Element.h','0'*64),('testing/web-platform/tests/css/cssom-view/offset-scroll-integer-precision.html',None),('testing/web-platform/tests/resources/testharness.js','0'*64)]:
    wrong=dict(phase);wrong[key]=value
    rejected(lambda:reuse.validate(wpt,load,sha,authenticate,wrong))
tests=load('tests_check',HERE/'tests.py');rows=[]
for test,names in c['baseline_expected_subtests'].items():
    for name in names:
        fail=test==c['main_test'] and name in c['baseline_failures']
        row={'test':test,'subtest':name,'status':'FAIL' if fail else 'PASS'}
        if fail:
            row.update(message=c['baseline_failures'][name],expected='PASS')
        rows.append(row)
fresh={'rows':rows,'ends':[{'test':n,'status':'OK'} for n in c['baseline_expected_subtests']]}
tests.require_phase(wpt,'baseline',fresh)
base={'rows':rows+retained['rows']};candidate=copy.deepcopy(base)
for row in candidate['rows']:
    if row['test'] in c['main_tests']:
        row['status']='PASS';row.pop('message',None);row.pop('expected',None)
candidate['ends']=[{'test':n,'status':'OK'} for n in c['expected_subtests']]
tests.require_phase(wpt,'candidate',candidate);tests.compare(wpt,base,candidate)
assert len(wpt.receipts['REPAIR-CLASSIFICATION.json']['main_repairs'])==10 and not wpt.receipts['REPAIR-CLASSIFICATION.json']['control_fail_to_pass']
control_improvement=copy.deepcopy(candidate)
next(row for row in control_improvement['rows'] if row['status']=='FAIL')['status']='PASS'
tests.compare(wpt,base,control_improvement)
assert len(wpt.receipts['REPAIR-CLASSIFICATION.json']['main_repairs'])==10 and len(wpt.receipts['REPAIR-CLASSIFICATION.json']['control_fail_to_pass'])==1
bad=copy.deepcopy(candidate);next(row for row in bad['rows'] if row['status']=='PASS' and row['test'] not in c['main_tests']).update(status='FAIL',known_intermittent=['PASS','FAIL'])
rejected(lambda:tests.compare(wpt,base,bad))
bad=copy.deepcopy(candidate);next(row for row in bad['rows'] if row['status']=='FAIL')['message']='changed retained diagnosis'
rejected(lambda:tests.compare(wpt,base,bad))
bad=copy.deepcopy(candidate);bad['rows'].pop();rejected(lambda:tests.compare(wpt,base,bad))
bad=copy.deepcopy(fresh);next(row for row in bad['rows'] if row['status']=='FAIL')['message']='calibration failure';rejected(lambda:tests.require_phase(wpt,'baseline',bad))
assert all(not (HERE/n).exists() for n in ['STATE.json','BEFORE.json','original','wpt-baseline','wpt-candidate'])
result={'disabled_unbound':True,'fresh_baseline_rows_files':[29,8],'candidate_rows_files':[170,21],
 'retained_baseline_rows_authenticated':141,'archived_header_resource_pinned':True,'source_guards':48,'normalized_sources':31,
 'original_native_paths':25,'existing32_preserved':True,'only_new8_owned':True,'atomic_helper_and_restoration_tail_unchanged':True,
 'installed_epoch_gate_unchanged':True,'synthetic_main_repairs':10,'control_improvements_reported_separately':True,
 'negative_checks':negative,'native_browser_build_index_actions':False}
(HERE/'STATIC-CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))
