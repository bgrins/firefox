import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate_policy(policy):
    ownership=load('candidate_ownership',ROOT/policy['ownership_helper'])
    assert policy['predecessor']=={'directory':'artifacts/css-prioritary-selection-original-v1','manifest_sha256':'25f467e4f382b575ff4d78c1e32ddb20c6fa7e80fe5063a802272c8eb4658af8'}
    original=ROOT/policy['predecessor']['directory'];ownership.authenticate(original,policy['predecessor']['manifest_sha256'])
    old=read(original/'POLICY.json')
    assert policy['proposal']=={'directory':'artifacts/css-prioritary-selected-declaration-proposal-v2','manifest_sha256':'a5e2ed5b744eeccce20cf189b1c1f438138bfe66fe2cf1dfa0619a95ed6b46ee'}
    ownership.authenticate(ROOT/policy['proposal']['directory'],policy['proposal']['manifest_sha256'])
    ownership.authenticate(ROOT/policy['candidate_lifecycle_predecessor']['directory'],policy['candidate_lifecycle_predecessor']['manifest_sha256'])
    mutable={'owner_directory','runtime_output','predecessor','candidate_lifecycle_predecessor','proposal','proposal_independent_review','provider_source_role','source_paths','activation_pending','semantic_original_sources','wpt','wpt_lanes','references'}
    assert {k:v for k,v in policy.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert policy['owner_directory']==str(HERE.relative_to(ROOT)) and policy['runtime_output']=='artifacts/css-prioritary-selection-candidate-runtime-1'
    load('pending_candidate_admission',HERE/'admission.py').validate(ROOT,policy)
    projected=copy.deepcopy(policy)
    for key in mutable:
        if key in old:projected[key]=old[key]
        else:projected.pop(key,None)
    load('original74_schema',original/'check.py').validate_policy(projected)
    nine=read(ROOT/'artifacts/css-registered-overridden-color-scheme-probe-v1/ROSTER.json')
    expected=copy.deepcopy(old['wpt']);expected.update(target_subtests=nine,expected_target_count=9,expected_control_count=65,expected_regression_signature_count=76)
    assert policy['wpt']==expected
    lanes=copy.deepcopy(old['wpt_lanes']);lanes['ordinary'].update(target_subtests=nine,expected_target_count=9,expected_control_count=59,expected_regression_signature_count=67)
    assert policy['wpt_lanes']==lanes
    roles=read(HERE/'SOURCE-ROLES.json');prior=read(original/'SOURCE-ROLES.json')
    assert set(roles)==set(policy['source_paths'])=={'servo/components/style/custom_properties.rs','servo/components/style/properties/cascade.rs'}
    assert roles['servo/components/style/custom_properties.rs']==prior['servo/components/style/custom_properties.rs']
    proposed=read(ROOT/policy['proposal']['directory']/'SOURCE-ROLES.json')['servo/components/style/properties/cascade.rs']
    for name,role in roles.items():
        for kind in ['base','candidate']:assert sha(ROOT/role[kind+'_capture'])==role[kind+'_sha256']
    for kind in ['base','candidate']:
        assert roles['servo/components/style/properties/cascade.rs'][kind+'_capture']==proposed[kind]['path']
        assert roles['servo/components/style/properties/cascade.rs'][kind+'_sha256']==proposed[kind]['sha256']
    assert policy['semantic_original_sources']=={'servo/components/style/custom_properties.rs':prior['servo/components/style/custom_properties.rs']['candidate_sha256'],'servo/components/style/properties/cascade.rs':proposed['base']['sha256']}
    assert policy['provider_source_role']=='clean-provider-cascade-candidate'
    for path,digest in policy['references'].items():assert sha(ROOT/path)==digest,path
    candidate=load('candidate_paths',HERE/'candidate.py')
    assert candidate.expected_modified_paths(['servo/components/style/custom_properties.rs'],roles,policy['committed_source_preimages'])==['servo/components/style/properties/cascade.rs']


def check():
    policy=read(HERE/'POLICY.json');validate_policy(policy)
    original=ROOT/policy['predecessor']['directory'];old_check=load('original_stream_fixture',original/'check.py')
    assessor=load('candidate_assessor',HERE/'assess.py');checks=load('stream_checks',ROOT/policy['wpt']['checks_helper'])
    comparison=load('candidate_comparison',HERE/'comparison.py')
    cases=[]
    for lane in policy['lane_order']:
        events,code,settings,app=old_check.synthetic(policy,lane,'FAIL')
        settings=comparison.phase_policy(settings)
        before=assessor.assess(events,code,settings,checks,run_binding=app)
        after=assessor.assess(events,code,settings,checks,original=before,run_binding=app)
        assert before['complete'] and after['complete']
        behavior=comparison.behavior(before,after,settings,assessor.signature)
        assert behavior['all_signatures_equal']
        assert behavior['repair_observation_gate']==(lane!='ordinary')
        assert len(behavior['candidate_signatures'])==settings['expected_subtest_count']+settings['expected_page_count']
        cases.append({'lane':lane,'all_FAIL_retained':len(after['rows']),'repair_gate':behavior['repair_observation_gate']})
    events,code,settings,app=old_check.synthetic(policy,'ordinary','FAIL');settings=comparison.phase_policy(settings)
    before=assessor.assess(events,code,settings,checks,run_binding=app)
    improved=copy.deepcopy(events)
    for row in improved:
        if row.get('action')=='test_status' and row['test'] in settings['target_subtests']:
            row['status']='PASS';row.pop('expected',None);row.pop('message',None)
    after=assessor.assess(improved,1,settings,checks,original=before,run_binding=app)
    result=comparison.behavior(before,after,settings,assessor.signature)
    assert result['repair_observation_gate'] and not result['all_signatures_equal'] and len(result['differences'])==9
    events,code,settings,app=old_check.synthetic(policy,'ordinary','PASS');settings=comparison.phase_policy(settings)
    before=assessor.assess(events,code,settings,checks,run_binding=app)
    regressed=copy.deepcopy(events);row=next(x for x in regressed if x.get('action')=='test_status');row.update(status='FAIL',expected='PASS',message='regression')
    after=assessor.assess(regressed,1,settings,checks,original=before,run_binding=app)
    assert after['complete'] and not comparison.behavior(before,after,settings,assessor.signature)['repair_observation_gate']
    negatives=0
    for change in [lambda p:p.update(execution_enabled=True,candidate_execution_enabled=True),lambda p:p.update(head='e'*40),lambda p:p.update(baseline_binding={}),lambda p:p['wpt_lanes']['ordinary'].update(capture=None),lambda p:p['wpt_lanes']['ordinary']['target_subtests'].clear()]:
        bad=copy.deepcopy(policy);change(bad)
        try:validate_policy(bad)
        except (AssertionError,KeyError,TypeError):negatives+=1
        else:raise AssertionError('invalid candidate policy accepted')
    result={'references':len(policy['references']),'pending_binding_negatives':negatives,'all_FAIL_lanes':cases,'target_improvements_preserved':9,'original_PASS_regression_rejected':True,'expected_modified_paths':['servo/components/style/properties/cascade.rs'],'native_or_browser_operations':False}
    print(json.dumps(result))


if __name__=='__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    sys.dont_write_bytecode=True
    check()
