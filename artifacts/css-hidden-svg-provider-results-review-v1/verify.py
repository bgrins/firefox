import sys
sys.dont_write_bytecode=True
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[1]
R=ROOT/'artifacts/css-hidden-svg-provider-runtime-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate(m,b):
    for n,h in m.items():assert sha(b/n)==h,n
def load(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
assert sha(R/'FILES.json')=='5dffa4053c3eba5f0f87c0f7954f7d171792cb0f4c88c1db5c791d07c3e4eaf9'
authenticate(read(R/'FILES.json'),R);authenticate(read(R/'DRAFT-FILES.json'),R);authenticate(read(R/'REFERENCES.json'),ROOT)
producer=ROOT/'artifacts/css-hidden-svg-provider-browser-v1'
assert sha(producer/'DRAFT-FILES.json')=='f4a1bcacf7d48c89c64cb00475d5c7e4e007dd9e6e0d520aef3bcf2cc3de1308'
for n in ('run.py','probe.html','validate.py'):assert (R/n).read_bytes()==(producer/n).read_bytes()
c=read(R/'CONFIG.json');old=read(producer/'CONFIG.json')
assert {n for n in c if c[n]!=old[n]}=={'ready_for_execution'} and c['ready_for_execution'] is True
node=next(n for n in ast.parse((R/'run.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='restored_epoch')
ns=dict(ROOT=ROOT,read=read,sha=sha,authenticate=authenticate,load=load)
exec(compile(ast.Module(body=[node],type_ignores=[]),'historical-svg-epoch','exec'),ns)
expected,pins,config,owned=ns['restored_epoch'](ROOT/c['epoch'])
assert read(R/'BEFORE.json')==read(R/'FINAL.json')=={'snapshot':expected,'pins':pins}
assert len(expected['sources'])==49 and len(pins)==337 and len(config['modified_native_paths'])==26
capture=read(R/'capture/RESULT.json');payload=read(R/'capture/payload.json')
assert capture['status']=='terminal' and capture['before']==capture['after']==pins
assert capture['observations']==[payload] and capture['cleanup_errors']==[]
assert capture['profile_removed'] is True and not (R/'capture/profile').exists()
pc=capture['process_cleanup'];assert pc['noLiveGroup'] is True and pc['terminal'] is True and pc['errors']==[]
validator=load('svg_raw_review',R/'validate.py');summary=validator.validate(payload)
summary['ordinary_controls_pass']=all(r['matched'] for r in summary['rows'] if not r['observations']['hidden'])
summary['recovery_controls_pass']=all(r['matches']['afterLayout'] and r['matches']['revealed'] and r['bboxMatchesLocalShape'] for r in summary['rows'])
assert summary==read(R/'SUMMARY.json')
assert summary['calibrated']==summary['stable']==8 and summary['matched']==6 and summary['mismatched']==2
assert summary['ordinary_controls_pass'] and summary['recovery_controls_pass']
assert all(type(r['hidden']) is bool and type(r['viewBox']) is bool for r in payload['rows'])
assert len({r['key'] for r in payload['rows']})==8
mismatches=[]
for row in payload['rows']:
    origin=[20,30] if row['method']=='getScreenCTM' else [0,0]
    warm=[1,0,0,1,*origin];changed=[2 if row['viewBox'] else 1,0,0,1,*origin]
    assert row['warm']==row['twinWarm']==row['restored']==row['twinRestored']==warm
    assert row['twinChanged']==changed
    assert row['hostChanged']==row['twinHostChanged']==[20,30,200,100]
    assert row['first']==row['repeat']
    assert row['afterBBox']==row['afterLayout']==row['revealed']==changed
    if row['first']!=changed:
        assert row['hidden'] and row['viewBox'] and row['first']==warm
        mismatches.append({'key':row['key'],'first':row['first'],'expected':changed,'afterBBox':row['afterBBox']})
assert [r['key'] for r in mismatches]==['getCTM-viewBox-hidden','getScreenCTM-viewBox-hidden']
state=read(R/'STATE.json');root=read(R/'ROOT-FINAL-CHECK.json')
assert state['status']=='terminal' and state['complete'] and state['preserved'] and state['native_changes'] is False
assert 'failure' not in state and 'preservation_failure' not in state
assert root['status']=='REPRODUCED_AND_PRESERVED' and root['session']==71193 and root['exit']==0
assert root['state_sha256']==sha(R/'STATE.json')
for n in ('all_live_pins_match','before_equals_final','raw_payload_recount_matches','profile_removed','owned_process_group_cleaned'):assert root[n] is True
assert root['new_accepted_fixes']==0
assert root['mismatch_keys']==[r['key'] for r in mismatches]
result={'status':'REPRODUCTION_AND_HISTORICAL_PRESERVATION_VERIFIED','runtime_files_sha256':sha(R/'FILES.json'),'payload_count':len(read(R/'FILES.json')),'payload_sha256':sha(R/'capture/payload.json'),'root_receipt_sha256':sha(R/'ROOT-FINAL-CHECK.json'),'calibrated':8,'stable':8,'matched':6,'mismatched':mismatches,'source_guards':49,'role_pins':337,'native_inventory':26,'installed_test_identities':owned,'binary_pins':{n:pins[n] for n in pins if n.endswith('/firefox') or n.endswith('/XUL')},'recovery_attribution':'first observed corrected matrix is after getBBox; intervening twin/host/style reads and later recovery reads are not isolated causal trials','native_branch_instrumented':False,'new_accepted_fixes':0,'later_live_state_asserted':False}
(D/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
