import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    ownership = load('selected_color_ownership', ROOT / policy['ownership_helper'])
    previous = ROOT / policy['predecessor']['directory']
    ownership.authenticate(previous, policy['predecessor']['manifest_sha256'])
    old = read(previous / 'POLICY.json')
    mutable = {'owner_directory','runtime_output','predecessor','proposal','references','source_paths','execution_enabled','candidate_execution_enabled','activation_pending','head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','suite_binding','wpt','source_roster','baseline_binding','baseline_capsule','original_admission_policy_sha256','restoration_binding','preparation_predecessor','correction_predecessor','preserved_absent_resources'}
    assert {k:v for k,v in policy.items() if k not in mutable} == {k:v for k,v in old.items() if k not in mutable}
    assert type(policy['execution_enabled']) is bool and policy['execution_enabled'] == policy['candidate_execution_enabled']
    assert bool(policy['activation_pending']) != policy['execution_enabled']
    assert policy['baseline_binding'] is None and policy['baseline_capsule'] is None
    assert policy['provider_source_role'] == 'clean-original'
    validate_actual_bindings(policy)
    suite = ROOT / policy['suite_binding']['directory']
    ownership.authenticate(suite,policy['suite_binding']['manifest_sha256'])
    load('selected_color_union',suite/'check.py').main()
    union = read(suite/'INPUTS.json')
    settings = dict(old['wpt'])
    settings.update(resources=union['resources'],metadata=union['metadata'],manifest={'path':str((suite/'MANIFEST.json').relative_to(ROOT)),'sha256':sha(suite/'MANIFEST.json')},expected_subtests=union['roster'],expected_subtest_count=42,expected_control_count=42,expected_page_count=3,expected_regression_signature_count=45,fixture_target_pages=list(union['roster']),phase_revisions={'original':policy['head'],'candidate':policy['head']},harness_revision=policy['head'])
    assert policy['wpt'] == settings
    assert len(settings['fixture_target_pages']) == len(set(settings['fixture_target_pages'])) == 3
    assert set(settings['fixture_target_pages']) == set(settings['expected_subtests'])
    assert settings['target_subtests'] == {}
    assert policy['preserved_absent_resources'] == old['preserved_absent_resources'] + union['new_metadata_absences']
    assert policy['source_roster'] == str((suite/'ROSTER.json').relative_to(ROOT))
    assert len(policy['accepted_current_payloads']) == 29
    for name,pin in policy['references'].items(): assert sha(ROOT / name) == pin, name
    proposal = ROOT / policy['proposal']['directory']
    ownership.authenticate(proposal, policy['proposal']['manifest_sha256'])
    proposed = read(proposal / 'SOURCE-ROLES.json')
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths'])
    original = 'provider_source_role' in policy
    assert set(roles) == ({'servo/components/style/custom_properties.rs'} if original else set(proposed))
    for name,role in roles.items():
        for kind in ('base','candidate'): assert sha(ROOT / role[kind+'_capture']) == role[kind+'_sha256']
        assert role['base_sha256'] == policy['source_context_pins'][name]
        assert role['candidate_sha256'] == proposed[name]['base_sha256' if original else 'candidate_sha256']
        assert proposed[name]['base_sha256'] == policy['committed_source_preimages'][name]
    assert all((HERE/n).read_bytes()==(previous/n).read_bytes() for n in ('phases.py','wpt.py'))
    assert (HERE/'assess.py').read_text() == (previous/'assess.py').read_text().replace('Active-value animation-taint comparison observations:', 'Selected-color dependency observations:')


def validate_actual_bindings(policy):
    load('selected_color_pending_admission', HERE / 'admission.py').validate(ROOT,policy)


def check():
    import copy
    policy=read(HERE/'POLICY.json');validate_policy(policy)
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    negatives=0
    changes = [
      lambda p:p.update(head='invented'),
      lambda p:p['controls'].update(**{'CURRENT-EPOCH.json':'0'*64}),
      lambda p:p['prepared_application_metadata'].update(identity=[1,2]),
      lambda p:p['prepared_application_metadata'].update(sha256='0'*64),
      lambda p:p['prepared_flag_hashes'].update(root='0'*64),
      lambda p:p['execution_handoff']['current'].update(sha256='0'*64),
      lambda p:p['wpt']['fixture_target_pages'].pop(),
      lambda p:p['wpt']['fixture_target_pages'].append(p['wpt']['fixture_target_pages'][0]),
    ]
    for change in changes:
        bad=copy.deepcopy(policy);change(bad)
        try:validate_policy(bad)
        except (AssertionError,TypeError,KeyError):negatives+=1
        else:raise AssertionError('Invalid admission accepted')
    projection=load('known_projection',ROOT/'artifacts/css-animation-taint-clean-candidate-v1/comparison.py')
    assessor=load('selected_color_assessor',HERE/'assess.py')
    checks=load('selected_color_stream_checks',ROOT/policy['wpt']['checks_helper'])
    settings=policy['wpt']; app={'browser_build_id':'synthetic','revision':policy['head'],'build_revision':policy['head'],'harness_revision':policy['head'],'source_role':'original','sha256':'c'*64,'path':'synthetic/application.ini','resolved':'synthetic/application.ini'}
    events=[{'action':'suite_start','run_info':{'os':'mac','debug':False,'browser_build_id':'synthetic','revision':policy['head']}}]
    for page,names in settings['expected_subtests'].items():
        events.append({'action':'test_start','test':page})
        events.extend({'action':'test_status','test':page,'subtest':name,'status':'FAIL','expected':'PASS','message':'ordinary synthetic assertion'} for name in names)
        events.append({'action':'test_end','test':page,'status':'OK'})
    events.append({'action':'suite_end'})
    result=assessor.assess(events,1,projection.phase_policy(settings),checks,run_binding=app)
    assert result['complete'] and len(result['rows'])==42 and len(result['ends'])==3
    assert all(row['status']=='FAIL' for row in result['rows'])
    for page in settings['expected_subtests']:
        malformed=copy.deepcopy(events)
        next(row for row in malformed if row.get('action')=='test_status' and row['test']==page)['message']='ReferenceError: missingFixtureFunction is not defined'
        rejected=assessor.assess(malformed,1,projection.phase_policy(settings),checks,run_binding=app)
        assert not rejected['complete'] and rejected['fixture_setup_errors']
    print(json.dumps({'references':len(policy['references']),'roles':1,'binding_negatives':negatives,'all42FAIL_retained':True,'all3_setup_error_pages_rejected':True,'no_live_operations':True}))


if __name__ == '__main__':
    import sys
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
