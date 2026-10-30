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
    assert policy['predecessor']=={'directory':'artifacts/css-prioritary-selection-original77-bound-template-v1','manifest_sha256':'3c10cba64b3cbaea836d37cbdcb6cd9cd7866e1202ac2a4da8b381d3d805e4ce'}
    assert policy['candidate_lifecycle_predecessor']=={'directory':'artifacts/css-prioritary-selection-candidate-v2','manifest_sha256':'238938ba1fab12f3d759e901dcba57afa9bdbd383d2212a65833926cef12dfec'}
    assert policy['proposal']=={'directory':'artifacts/css-prioritary-selected-declaration-proposal-v4','manifest_sha256':'0becefa8026daa7ae23a98c522df65c6396c2377d31f5a28e2d2442a50198212'}
    for key in ['predecessor','candidate_lifecycle_predecessor','proposal','suite_binding','capture_binding','intermediate_guard_binding']:
        binding=policy[key];ownership.authenticate(ROOT/binding['directory'],binding['manifest_sha256'])
    old=read(ROOT/policy['predecessor']['directory']/'POLICY.json')
    previous=ROOT/policy['candidate_lifecycle_predecessor']['directory']
    mutable={'owner_directory','runtime_output','predecessor','candidate_lifecycle_predecessor','proposal','proposal_independent_review','provider_source_role','source_paths','semantic_original_sources','activation_pending','references','execution_enabled','candidate_execution_enabled','head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','restoration_binding','baseline_binding','baseline_capsule','original_admission_policy_sha256','disabled_preimage','restored_context_claims','wpt','wpt_lanes','target_evidence','intermediate_consumed_inputs'}
    assert {k:v for k,v in policy.items() if k not in mutable}=={k:v for k,v in old.items() if k not in mutable}
    assert policy['owner_directory']==str(HERE.relative_to(ROOT)) and policy['runtime_output']=='artifacts/css-prioritary-selection-candidate-runtime-3'
    assert policy['disabled_preimage']=={'directory':'artifacts/css-prioritary-selection-candidate77-disabled-v1','manifest_sha256':'f46af0315ef689e241d991afbaaf2bcbb9a7482eefb2bd5464c6a8d6b830fd43'} and policy['restored_context_claims']=={}
    assert policy['provider_source_role']=='provider-cascade-value-candidate'
    assert policy['proposal_independent_review'] is None
    load('pending_admission',HERE/'admission.py').validate(ROOT,policy)
    assert policy['target_evidence']=={
        'original45':{'directory':'artifacts/css-registered-selected-color-original-runtime-2','manifest_sha256':'51b97af4f978829b361b2ff876d8fe5299a8f212d53868758483f2ff04e2f7a7'},
        'union_only45':{'directory':'artifacts/css-registered-selected-color-union-only-candidate-runtime-1','manifest_sha256':'6d27372adf4286a1eb0abb2c3b18c36e042467c8ebdbfd74c037cb13d608de9b'}}
    evidence=read(HERE/'TARGET-EVIDENCE.json')
    assert evidence['original45']==policy['target_evidence']['original45'] and evidence['union_only45']==policy['target_evidence']['union_only45']
    a,b=[ROOT/policy['target_evidence'][key]['directory'] for key in ['original45','union_only45']]
    for key in ['original45','union_only45']:
        binding=policy['target_evidence'][key];ownership.authenticate(ROOT/binding['directory'],binding['manifest_sha256'])
    original={(r['test'],r['subtest']):r for r in read(a/'OUTCOMES.json')['rows']}
    pairs=read(b/'OUTCOMES.json')['rows'];assert len(original)==len(pairs)==45
    improved=[]
    for pair in pairs:
        before,after=pair['original'],pair['candidate'];key=(before['test'],before['subtest'])
        assert before==original[key] and key==(after['test'],after['subtest'])
        if before['status']!=after['status']:
            assert before['status']=='FAIL' and after['status']=='PASS'
            improved.append({'test':key[0],'subtest':key[1]})
    assert len(improved)==8 and evidence['color_only_improvements']==improved
    targets=read(previous/'TARGETS.json');old_targets={(p,n) for p,ns in targets.items() for n in ns};assert len(old_targets)==15
    targets['/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html'].append('Prioritary forced-color selection: auto')
    for row in improved:
        assert (row['test'],row['subtest']) not in old_targets
        targets.setdefault(row['test'],[]).append(row['subtest'])
    assert read(HERE/'TARGETS.json')==targets and sum(map(len,targets.values()))==24
    assert evidence['total_disjoint_targets']==24 and evidence['future_original77_counts'] is None and evidence['candidate77_outcome'] is None
    for current,settings in [(policy['wpt'],old['wpt']),*[(policy['wpt_lanes'][lane],old['wpt_lanes'][lane]) for lane in policy['lane_order']]]:
        selected={p:ns for p,ns in targets.items() if p in settings['expected_subtests']}
        assert all(set(ns)<=set(settings['expected_subtests'][p]) for p,ns in selected.items())
        count=sum(map(len,selected.values()));controls=settings['expected_subtest_count']-count
        expected=dict(settings,phase_revisions={'original':policy['head'],'candidate':policy['head']},harness_revision=policy['head'],target_subtests=selected,expected_target_count=count,expected_control_count=controls,expected_regression_signature_count=controls+settings['expected_page_count'])
        assert current==expected
    roles=read(HERE/'SOURCE-ROLES.json');proposed=read(ROOT/policy['proposal']['directory']/'SOURCE-ROLES.json')
    prior=read(ROOT/policy['predecessor']['directory']/'SOURCE-ROLES.json');assert set(roles)==set(proposed)==set(policy['source_paths']) and len(roles)==3
    admission=read(ROOT/policy['source_equivalence']['path'])
    for name,role in roles.items():
        base={'path':prior[name]['base_capture'],'sha256':prior[name]['base_sha256']} if name in prior else proposed[name]['base']
        assert role=={'base_capture':base['path'],'base_sha256':base['sha256'],'candidate_capture':proposed[name]['candidate']['path'],'candidate_sha256':proposed[name]['candidate']['sha256']}
        for kind in ['base','candidate']:assert sha(ROOT/role[kind+'_capture'])==role[kind+'_sha256']
        assert policy['source_context_pins'][name]==role['base_sha256']==admission['sources'][name]['working_sha256']
        assert policy['committed_source_preimages'][name]==proposed[name]['base']['sha256']==admission['sources'][name]['head_sha256']
        if name in policy['accepted_current_payloads']:
            assert policy['accepted_current_payloads'][name]=={'sha256':role['base_sha256'],'identity':admission['sources'][name]['identity']}
    assert policy['semantic_original_sources']=={name:r['base']['sha256'] for name,r in proposed.items()}
    assert len(policy['accepted_current_payloads'])==29
    for name in ['baseline.py','wpt.py','assess.py']:assert (HERE/name).read_bytes()==(previous/name).read_bytes()
    for name in ['inputs.py','intermediate.py','review_scope.py']:assert (HERE/name).read_bytes()==(ROOT/policy['intermediate_guard_binding']['directory']/name).read_bytes()
    for name,digest in policy['references'].items():assert sha(ROOT/name)==digest,name
    closure=load('candidate_closure',HERE/'closure.py')
    assert policy['intermediate_consumed_inputs']==closure.external_inputs(ROOT,policy,roles)
    for name,digest in policy['intermediate_consumed_inputs'].items():
        if name.startswith('artifacts/'):assert digest is not None and sha(ROOT/name)==digest,name
    closure.require_epoch_coverage(read(ROOT/policy['original_build']['epoch']),policy)
    candidate=load('candidate_owner',HERE/'candidate.py')
    assert candidate.expected_modified_paths(['servo/components/style/custom_properties.rs'],roles,policy['committed_source_preimages'])==sorted(roles)
    old_body=(previous/'candidate.py').read_text();body=(HERE/'candidate.py').read_text()
    assert body[body.index('    finally:'):]==old_body[old_body.index('    finally:'):]
    assert body.count('state.a.verify_current(state.h, ROOT, env,')==3
    assert body.count('intermediate.verify_intermediate(')==1


def check():
    policy=read(HERE/'POLICY.json');validate_policy(policy)
    template=load('original77_streams',ROOT/policy['predecessor']['directory']/'check.py')
    assessor=load('candidate_assessor',HERE/'assess.py');checks=load('stream_checks',ROOT/policy['wpt']['checks_helper'])
    comparison=load('candidate_comparison',HERE/'comparison.py');streams=[];improvements=[]
    for lane in policy['lane_order']:
        events,code,settings,app=template.synthetic(policy,lane,'FAIL');settings=comparison.phase_policy(settings)
        before=assessor.assess(events,code,settings,checks,run_binding=app)
        after=assessor.assess(events,code,settings,checks,original=before,run_binding=app)
        result=comparison.behavior(before,after,settings,assessor.signature)
        assert before['complete'] and after['complete'] and result['all_signatures_equal'] and not result['repair_observation_gate']
        assert json.loads(json.dumps(result))==result
        streams.append([lane,len(after['rows']),len(after['ends'])])
        improved=copy.deepcopy(events)
        for row in improved:
            if row.get('action')=='test_status' and row.get('subtest') in settings['target_subtests'].get(row['test'],[]):
                row['status']='PASS';row.pop('expected',None);row.pop('message',None)
        improved_exit=int(any(row['status']!=row.get('expected', 'FAIL' if row['test'].endswith('/forced-colors-mode-51.html') else 'PASS') for row in improved if row.get('action')=='test_status'))
        after=assessor.assess(improved,improved_exit,settings,checks,original=before,run_binding=app)
        result=comparison.behavior(before,after,settings,assessor.signature)
        assert result['repair_observation_gate'] and len(result['differences'])==settings['expected_target_count']
        assert result==json.loads(json.dumps(result)) and all(isinstance(row['identity'],list) for row in result['differences'])
        improvements.append([lane,len(result['differences'])])
        pass_events,pass_code,_,_=template.synthetic(policy,lane,'PASS')
        before=assessor.assess(pass_events,pass_code,settings,checks,run_binding=app)
        regression=copy.deepcopy(pass_events);next(row for row in regression if row.get('action')=='test_status').update(status='FAIL',expected='PASS',message='regression')
        after=assessor.assess(regression,1,settings,checks,original=before,run_binding=app)
        assert after['complete'] and not comparison.behavior(before,after,settings,assessor.signature)['repair_observation_gate']
        changed=copy.deepcopy(before);changed['ends'][0]['status']='ERROR'
        assert not comparison.behavior(before,changed,settings,assessor.signature)['repair_observation_gate']
    assert streams==[['ordinary',68,8],['forced_colors',3,2],['mozilla_appearance',6,2]]
    assert improvements==[['ordinary',21],['forced_colors',2],['mozilla_appearance',1]]
    negatives=0
    for change in [lambda p:p.update(execution_handoff=None),lambda p:p['baseline_binding']['terminal'].update(exit=1),lambda p:p.update(baseline_binding={}),lambda p:p.update(head='e'*40),lambda p:p['wpt_lanes']['ordinary'].update(capture=None),lambda p:p['wpt_lanes']['forced_colors']['target_subtests'].clear(),lambda p:p['intermediate_consumed_inputs'].pop('artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py'),lambda p:p['accepted_current_payloads']['servo/components/style/properties_and_values/value.rs']['identity'].__setitem__(1,0),lambda p:p['source_context_pins'].pop('servo/components/style/properties/cascade.rs'),lambda p:p['semantic_original_sources'].update({'servo/components/style/custom_properties.rs':'0'*64}),lambda p:p['target_evidence']['union_only45'].update(manifest_sha256='0'*64),lambda p:p['execution_handoff'].update(source_claims_sha256='0'*64),lambda p:p['prepared_application_metadata']['identity'].__setitem__(1,0),lambda p:p['controls'].update({'CURRENT-EPOCH.json':'0'*64}),lambda p:p['execution_handoff'].update(reviewer_manifest_sha256='0'*64)]:
        bad=copy.deepcopy(policy);change(bad)
        try:validate_policy(bad)
        except (AssertionError,KeyError,TypeError):negatives+=1
        else:raise AssertionError('bad preparation accepted')
    print(json.dumps({'references':len(policy['references']),'consumed_inputs':len(policy['intermediate_consumed_inputs']),'actual_binding_negatives':negatives,'all_FAIL_retained':streams,'target_improvements':improvements,'all_original_PASS_and_endings_preserved':True,'JSON_behavior_roundtrip':True,'modified_native_roles':3,'live_operations':False}))


if __name__=='__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    sys.dont_write_bytecode=True
    check()
