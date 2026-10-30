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
    assert policy['predecessor']=={'directory':'artifacts/css-prioritary-selection-original-v2','manifest_sha256':'2119c8ff41df3ed46f842670865fa85d92e6b8e8e93facfc53a05900dd46c094'}
    original=ROOT/policy['predecessor']['directory'];ownership.authenticate(original,policy['predecessor']['manifest_sha256'])
    old=read(original/'POLICY.json')
    assert policy['proposal']=={'directory':'artifacts/css-prioritary-selected-declaration-proposal-v3','manifest_sha256':'832d247da7050b1038bcf1b96a8fa72fa2cef9f63c2f514da37fc182de9cfbc6'}
    ownership.authenticate(ROOT/policy['proposal']['directory'],policy['proposal']['manifest_sha256'])
    ownership.authenticate(ROOT/policy['candidate_lifecycle_predecessor']['directory'],policy['candidate_lifecycle_predecessor']['manifest_sha256'])
    mutable={'owner_directory','runtime_output','predecessor','candidate_lifecycle_predecessor','proposal','proposal_independent_review','provider_source_role','source_paths','activation_pending','semantic_original_sources','wpt','wpt_lanes','references','execution_enabled','candidate_execution_enabled','head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','restoration_binding','baseline_binding','baseline_capsule','original_admission_policy_sha256'}
    assert {k:v for k,v in policy.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert policy['owner_directory']==str(HERE.relative_to(ROOT)) and policy['runtime_output']=='artifacts/css-prioritary-selection-candidate-runtime-1'
    load('actual_candidate_admission',HERE/'admission.py').validate(ROOT,policy)
    load('original74_schema',original/'check.py').validate_policy(old)
    prepared=ROOT/'artifacts/css-prioritary-selection-candidate-v1'
    ownership.authenticate(prepared,'2d6b0ccc0ad3b2f22dfb307e34a41295efd8e79d898613c19b8bd7017cf2373b')
    for name in ['phases.py','wpt.py','assess.py','check_phases.py']:
        assert (HERE/name).read_bytes()==(prepared/name).read_bytes()
    assert (HERE/'baseline.py').read_text()==(prepared/'baseline.py').read_text().replace("    assert terminal == binding['terminal'] and terminal['exit'] == 0","    assert terminal.pop('active_owner_manifest_sha256') == capsule['sha256']\n    assert terminal == binding['terminal'] and terminal['exit'] == 0")
    assert (HERE/'candidate.py').read_text()==(prepared/'candidate.py').read_text().replace("'operation': 'prioritary-selection-candidate-v1'","'operation': 'prioritary-selection-candidate-v2'")
    targets=read(ROOT/'artifacts/css-registered-overridden-color-scheme-probe-v1/ROSTER.json')
    trace=ROOT/'artifacts/css-prioritary-rollback-expectations-spec-trace-v1'
    ownership.authenticate(trace,'11894e7c34c22e4a8f23b20122bd061fe180b68a1336acd3403607b3fc488a0c')
    cases=read(trace/'TARGETS.json')['cases']
    assert len(cases)==4 and all(case['verdict']=='REACHED' for case in cases)
    targets['/css/css-properties-values-api/registered-prioritary-selection.tentative.html']=[case['name'] for case in cases]
    targets['/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html']=['Prioritary forced-color selection: none']
    targets['/_mozilla/css/css-cascade/prioritary-appearance-selection.html']=['Prioritary appearance selection: earlier-author-winner']
    assert read(HERE/'TARGETS.json')==targets and sum(map(len,targets.values()))==15
    for current,settings in [(policy['wpt'],old['wpt']),*[(policy['wpt_lanes'][lane],old['wpt_lanes'][lane]) for lane in policy['lane_order']]]:
        selected={page:names for page,names in targets.items() if page in settings['expected_subtests']}
        assert all(set(names)<=set(settings['expected_subtests'][page]) for page,names in selected.items())
        count=sum(map(len,selected.values()));controls=settings['expected_subtest_count']-count
        expected=dict(settings,target_subtests=selected,expected_target_count=count,expected_control_count=controls,expected_regression_signature_count=controls+settings['expected_page_count'])
        assert current==expected
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
        assert not behavior['repair_observation_gate']
        assert len(behavior['candidate_signatures'])==settings['expected_subtest_count']+settings['expected_page_count']
        cases.append({'lane':lane,'all_FAIL_retained':len(after['rows']),'repair_gate':behavior['repair_observation_gate']})
    improvements=[]
    for lane in policy['lane_order']:
        events,code,settings,app=old_check.synthetic(policy,lane,'FAIL');settings=comparison.phase_policy(settings)
        before=assessor.assess(events,code,settings,checks,run_binding=app)
        improved=copy.deepcopy(events)
        for row in improved:
            if row.get('action')=='test_status' and row.get('subtest') in settings['target_subtests'].get(row['test'],[]):
                row['status']='PASS';row.pop('expected',None);row.pop('message',None)
        after=assessor.assess(improved,1,settings,checks,original=before,run_binding=app)
        result=comparison.behavior(before,after,settings,assessor.signature)
        count=settings['expected_target_count']
        assert result['repair_observation_gate'] and not result['all_signatures_equal'] and len(result['differences'])==count
        improvements.append([lane,count])
    assert improvements==[['ordinary',13],['forced_colors',1],['mozilla_appearance',1]]
    events,code,settings,app=old_check.synthetic(policy,'ordinary','PASS');settings=comparison.phase_policy(settings)
    before=assessor.assess(events,code,settings,checks,run_binding=app)
    regressed=copy.deepcopy(events);row=next(x for x in regressed if x.get('action')=='test_status');row.update(status='FAIL',expected='PASS',message='regression')
    after=assessor.assess(regressed,1,settings,checks,original=before,run_binding=app)
    assert after['complete'] and not comparison.behavior(before,after,settings,assessor.signature)['repair_observation_gate']
    negatives=0
    for change in [lambda p:p.update(execution_handoff=None),lambda p:p.update(head='e'*40),lambda p:p['baseline_binding']['terminal'].update(exit=1),lambda p:p['execution_handoff'].update(review_sha256='0'*64),lambda p:p['execution_handoff'].update(reviewer_manifest_sha256='0'*64),lambda p:p.update(baseline_binding={}),lambda p:p['wpt_lanes']['ordinary'].update(capture=None),lambda p:p['wpt_lanes']['ordinary']['target_subtests'].clear(),lambda p:p['prepared_application_metadata']['identity'].__setitem__(1,0),lambda p:p['prepared_flag_hashes'].update(root='0'*64),lambda p:p['wpt_lanes']['forced_colors']['target_subtests']['/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html'].append('Prioritary forced-color selection: auto')]:
        bad=copy.deepcopy(policy);change(bad)
        try:validate_policy(bad)
        except (AssertionError,KeyError,TypeError):negatives+=1
        else:raise AssertionError('invalid candidate policy accepted')
    result={'references':len(policy['references']),'actual_binding_negatives':negatives,'all_FAIL_lanes':cases,'target_improvements_preserved':improvements,'original_PASS_regression_rejected':True,'expected_modified_paths':['servo/components/style/properties/cascade.rs'],'native_or_browser_operations':False}
    print(json.dumps(result))


if __name__=='__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    sys.dont_write_bytecode=True
    check()
