import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

check=load('pure_owner_check',ROOT/'artifacts/css-prioritary-selection-original77-bound-template-v1/check.py')
comparison=load('candidate_phase_comparison',HERE/'comparison.py')
phases=load('three_lane_phases',HERE/'phases.py')
wpt=load('real_save_helper',HERE/'wpt.py')
assessor=load('phase_assessor',HERE/'assess.py')
policy=check.read(HERE/'POLICY.json');policy['head']='e'*40;policy['baseline_binding']={'directory':'synthetic-original'}
stream_checks=load('phase_stream_checks',ROOT/policy['wpt']['checks_helper'])
initial={'synthetic':'preservation'}
binaries={'synthetic':'binary'}
seen=[]
with tempfile.TemporaryDirectory(prefix='css-candidate77-phases-',dir='/private/tmp') as scratch:
    output=Path(scratch)
    (output/'candidate-build').mkdir()
    wpt.save(output/'candidate-build/RESULT.json',{'binaries':binaries,'native_sources':{name:r['candidate_sha256'] for name,r in check.read(HERE/'SOURCE-ROLES.json').items()}})
    def fake_run(root,here,phase,role,policy,env,verify,owned,cancelled,*,original,lane):
        assert verify()==initial and not owned and not cancelled()
        seen.append(lane);phase.mkdir()
        events,code,settings,app=check.synthetic(policy,lane,'FAIL')
        settings=comparison.phase_policy(settings)
        before=assessor.assess(events,code,settings,stream_checks,run_binding=app)
        app=dict(app,source_role='candidate')
        assessment=assessor.assess(events,code,settings,stream_checks,original=before,run_binding=app)
        assert assessment['complete']
        behavior=comparison.behavior(before,assessment,settings,assessor.signature)
        wpt.save(phase/'BEHAVIOR-COMPARISON.json',behavior)
        for name,body in [('ASSESSMENT.json',assessment),('PRE.json',initial),('POST.json',initial),('APPLICATION-METADATA.json',app),('APPLICATION-METADATA-POST.json',app),('BINARY-PINS.json',binaries)]:wpt.save(phase/name,body)
        return {'lane':lane,'zoom_observation_sha256':'z'*64 if lane=='ordinary' else None,'zoom_comparison_sha256':'c'*64 if lane=='ordinary' else None}
    fake=SimpleNamespace(save=wpt.save,run=fake_run)
    spec=SimpleNamespace(loader=SimpleNamespace(exec_module=lambda module:None))
    with patch.object(phases.importlib.util,'spec_from_file_location',return_value=spec),patch.object(phases.importlib.util,'module_from_spec',return_value=fake):
        result=phases.run(ROOT,HERE,output,policy,{},lambda:initial,{},lambda:False)
    outcomes=check.read(output/'OUTCOMES.json')
    assert seen==policy['lane_order'] and set(result)==set(seen)
    assert outcomes['callbacks_failed']==77 and outcomes['callbacks_passed']==0
    assert len(outcomes['rows'])==77 and len(outcomes['endings'])==12
    assert outcomes['zoom_target_correctness'] is None
    compared=check.read(output/'COMPARISON.json')
    assert compared['repair_observation_gate'] is False and compared['all89_signatures_equal'] is True
    forced=next(r for r in outcomes['rows'] if r['test'].endswith('/forced-colors-mode-51.html'))
    assert forced['status']=='FAIL' and 'expected' not in forced
    assert check.read(output/'PHASES-PRE.json')==check.read(output/'PHASES-POST.json')==initial
assert not output.exists()
result={'real_candidate_phase_controller_mocked_wpt':True,'false_repair_gate_does_not_abort_observation':True,'all77FAIL_retained':True,'all12OK_retained':True,'expected_FAIL_raw_signature_retained':True,'lane_order':seen,'scratch_removed':True,'browser_execution':False}
(HERE/'PHASES-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
