import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    assert policy['execution_enabled'] == policy['candidate_execution_enabled']
    if policy['execution_enabled']:
        assert policy['activation_pending'] == [] and policy['proposal_independent_review']['status'] == 'clear'
    else:
        assert policy['activation_pending']
    roles = json.loads((HERE/'SOURCE-ROLES.json').read_bytes())
    expected = {'dom/animation/EffectCompositor.cpp','dom/animation/EffectCompositor.h','servo/components/style/matching.rs'}
    assert set(roles) == set(policy['source_paths']) == expected
    assert policy['runtime_output'] == 'artifacts/css-contextual-duration-restyle-tristate-browser-runtime-1'
    proposal = ROOT/policy['proposal']['directory']
    assert hashlib.sha256((proposal/'FILES.json').read_bytes()).hexdigest() == policy['proposal']['manifest_sha256']
    for name,pin in json.loads((proposal/'FILES.json').read_bytes()).items():
        assert hashlib.sha256((proposal/name).read_bytes()).hexdigest() == (pin['sha256'] if isinstance(pin,dict) else pin)
    for name,record in roles.items():
        for kind in ('base','candidate'):
            assert hashlib.sha256((ROOT/record[kind+'_capture']).read_bytes()).hexdigest() == record[kind+'_sha256']
        if name.startswith('dom/'):
            assert b'DURATION_RESTYLE_TRACE' not in (ROOT/record['candidate_capture']).read_bytes()
    equivalence = policy['source_equivalence']
    assert equivalence['paths'] == sorted(expected)
    assert equivalence['required_base_pins'] == {name:record['base_sha256'] for name,record in roles.items()}
    assert equivalence['build_revision'] == policy['wpt']['phase_revisions']['original']
    assert equivalence['current_revision'] == policy['head']
    assert equivalence['historical_build_epoch'] == policy['original_build']['epoch']
    assert equivalence['require_both_git_blobs_at_admission'] and equivalence['require_absent_from_historical_modified_paths']
    epoch = json.loads((ROOT/equivalence['historical_build_epoch']).read_bytes())
    for name,pin in equivalence['required_base_pins'].items():
        assert epoch['pins'][name] == pin and name not in epoch['modified_native_paths']
    predecessor = json.loads((ROOT/'artifacts/css-contextual-duration-feedback-consistency-candidate-v1/POLICY.json').read_bytes())
    for key in ('accepted_current_payloads','accepted_epoch_records','source_context_pins','resource_policy','rebuilt_binaries','original_build','prepared_flag_hashes','wpt','phases','feedback_transport','record_schema_helper','record_kinds','baseline_capsule','baseline_binding'):
        assert policy[key] == predecessor[key],key
    terminal = json.loads((ROOT/policy['prepared_state_evidence']['restoration']).read_bytes())
    refresh = json.loads((ROOT/policy['prepared_state_evidence']['refresh']).read_bytes())
    assert terminal['state_and_application_restoration_independently_verified'] and terminal['raw_replay_verified']
    assert terminal['backup_removed_bytes'] == 1008605176
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert policy['controls']['CURRENT-EPOCH.json'] == refresh['after_epoch']
    assert refresh['observation'] == terminal['raw_index_observation']
    for key in ('OWNED.json','ROLE.json'):
        assert policy['controls'][key] == predecessor['controls'][key]
    app = policy['prepared_application_metadata']
    assert app['entry_identity'] == terminal['restored_application_entry']['identity']
    assert app['identity'] == terminal['restored_application_target']['identity']
    assert app['sha256'] == terminal['restored_application_target']['sha256']


def check():
    policy = json.loads((HERE/'POLICY.json').read_bytes())
    validate_policy(policy)
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    assert policy['activation_pending']
    assert policy['checkpoint_mode'] == 'current_native_checkpoint'
    assert policy['head'] and policy['controls'] and policy['prepared_application_metadata'] and policy['prepared_flag_hashes']
    assert 'reference_checkpoint' not in policy and 'research_parent_head' not in policy
    assert set(policy['phases']) == {'feedback'} and policy['wpt'] == policy['phases']['feedback']
    comparison = load('feedback_compare',HERE/'comparison.py')
    assert comparison.expected_wpt(ROOT,policy) == policy['wpt']
    authenticated, deferred = 0, []
    for name,pin in policy['references'].items():
        if not name.startswith('artifacts/'):
            deferred.append(name)
            continue
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == pin, name
        authenticated += 1
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    original = load('feedback_synthetic',ROOT/policy['baseline_capsule']['directory']/'check.py')
    original_policy = json.loads((ROOT/policy['baseline_capsule']['directory']/'POLICY.json').read_bytes())
    settings, app, events = original.synthetic(original_policy['wpt'])
    assessor = load('feedback_assessor',HERE/'assess.py')
    checks = load('feedback_checks',ROOT/policy['wpt']['checks_helper'])
    observed = assessor.assess(events,0,settings,checks,run_binding=app)
    assert observed['complete']
    original_assessor = load('original_consistency_assessor',ROOT/policy['baseline_capsule']['directory']/'assess.py')
    assert observed == original_assessor.assess(events,0,settings,checks,run_binding=app)
    candidate_settings = copy.deepcopy(settings)
    candidate_settings['phase_revisions']['candidate'] = 'a'*40
    candidate_settings['candidate_required_pass_pages'] = list(settings['expected_subtests'])
    candidate_app = dict(app,revision='a'*40,build_revision='a'*40,source_role='candidate',browser_build_id='synthetic-candidate')
    candidate = copy.deepcopy(events)
    candidate[0]['run_info']['browser_build_id'] = 'synthetic-candidate'
    def assess(stream,code=0):
        return assessor.assess(stream,code,candidate_settings,checks,original=observed,run_binding=candidate_app)
    assert assess(candidate)['comparison_gate_passed']
    rejected = []
    def reject(label, mutate, code=0):
        stream = copy.deepcopy(candidate)
        mutate(stream)
        assert not assess(stream,code)['comparison_gate_passed'], label
        rejected.append(label)
    reject('callback failure',lambda s:s[2].update(status='FAIL',expected='PASS'),1)
    reject('callback message',lambda s:s[2].update(message='changed'))
    reject('expected presence',lambda s:s[2].update(expected='PASS'))
    reject('intermittent presence',lambda s:s[2].update(known_intermittent=[]))
    reject('ending message',lambda s:s[-2].update(message='changed'))
    reject('missing callback',lambda s:s.pop(2))
    reject('unknown callback',lambda s:s[2].update(subtest='unknown'))
    reject('wrong BuildID',lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
    reject('wrong harness',lambda s:s[0]['run_info'].update(revision='0'*40))
    reject('missing suite end',lambda s:s.pop())
    reject('crash',lambda s:s.append({'action':'crash'}))
    reject('wrong exit',lambda s:None,1)
    annotations = {'build_revision','harness_revision','source_role'}
    synthetic_policy = dict(policy,head='a'*40,prepared_application_metadata={k:v for k,v in app.items() if k not in annotations},historical_baseline_metadata=app,wpt=settings)
    assert comparison.original_metadata(synthetic_policy) == app
    for key,value in [('revision','0'*40),('source_role','candidate'),('sha256','0'*64)]:
        malformed = copy.deepcopy(synthetic_policy)
        malformed['prepared_application_metadata'][key] = value
        try:
            comparison.original_metadata(malformed)
        except AssertionError:
            rejected.append('metadata '+key)
        else:
            raise AssertionError(key)
    historical = {'index':{'raw_index':'old','entries':'same'},'nested_index':{'raw_index':'same'}}
    current = copy.deepcopy(historical);current['index']['raw_index']='new'
    comparison.admit_snapshot(historical,current)
    for label,wrong in [('index entries',copy.deepcopy(current)),('nested index',copy.deepcopy(current))]:
        if label=='index entries':wrong['index']['entries']='wrong'
        else:wrong['nested_index']['raw_index']='wrong'
        try:comparison.admit_snapshot(historical,wrong)
        except AssertionError:rejected.append(label)
        else:raise AssertionError(label)
    baseline = load('feedback_checkpoint',HERE/'baseline.py')
    native = json.loads((ROOT/policy['native_checkpoint']['path']).read_bytes())
    baseline.checkpoint_chain(policy,native)
    for key,value in [('head','0'*40),('signature_chain_verified',False),
                      ('runtime_epoch_synchronized',False),('accepted_fix',151),
                      ('accepted_fixes',150),('tracked',151)]:
        wrong = dict(native)
        wrong[key] = value
        try:
            baseline.checkpoint_chain(policy,wrong)
        except AssertionError:
            rejected.append('native checkpoint '+key)
        else:
            raise AssertionError(key)
    try:
        baseline.checkpoint_chain(dict(policy,checkpoint_mode='future_research'),native)
    except AssertionError:
        rejected.append('wrong checkpoint mode')
    else:
        raise AssertionError('wrong checkpoint mode')
    phases = load('feedback_records',HERE/'phases.py')
    with tempfile.TemporaryDirectory(prefix='duration-feedback-static-') as temporary:
        output = Path(temporary)
        records = output/'feedback-records'
        records.mkdir(mode=0o700)
        run_id = 'synthetic_run_1234567890'
        binding = {'directory':str(records),'identity':[records.stat().st_dev,records.stat().st_ino],'run_id':run_id}
        (output/'FEEDBACK-BINDING.json').write_text(json.dumps(binding))
        schema = load('record_schema',ROOT/policy['record_schema_helper'])
        def body(kind):
            count = 2 if kind=='coupled' else 1
            effect = {'name':'synthetic','time':None,'duration':1000,'progress':None,'state':'paused'}
            style = {'font':'28px','cssDuration':'1.75s','opacity':'0.75','outlineWidth':'0px'}
            def reading(order):
                return {'order':order,'style':copy.deepcopy(style),'effects':[copy.deepcopy(effect) for _ in range(count)],
                        'repeatEffects':[copy.deepcopy(effect) for _ in range(count)],'repeatStyle':copy.deepcopy(style),
                        'sameAnimations':[False]*count,'sameEffects':[True]*count,'currentEffects':[],
                        'afterMembershipStyle':copy.deepcopy(style)}
            return {'run_id':run_id,'kind':kind,'trajectories':[{'role':role,
                    'acquisition':{'beforeReady':reading('timing-first'),'afterReady':reading('timing-first')},
                    'phases':[{'name':name,'reads':[reading(order) for order in
                        (['timing-first','style-first'] if i%2 else ['style-first','timing-first'])]}
                        for i,name in enumerate(schema.PHASES)]} for role in schema.ROLES]}
        bodies = {name:body(kind) for name,kind in policy['record_kinds'].items()}
        (output/'feedback-wpt').mkdir()
        (output/'feedback-wpt/ASSESSMENT.json').write_text(json.dumps({'complete':True,'rows':[{'status':'PASS'},{'status':'PASS'}]}))
        def restore():
            for path in records.iterdir():
                path.unlink()
            os.chmod(records,0o700)
            for name,body in bodies.items():
                path = records/name
                path.write_text(json.dumps(body))
                path.chmod(0o600)
        restore()
        assert phases.feedback_records(ROOT,output,policy)['numeric_or_convergence_oracle'] is False
        def reject_record(label,mutate):
            restore()
            mutate()
            try:
                phases.feedback_records(ROOT,output,policy)
            except (AssertionError,FileNotFoundError):
                rejected.append(label)
            else:
                raise AssertionError(label)
        def changed_record(change):
            body = copy.deepcopy(bodies['coupled.json'])
            change(body)
            (records/'coupled.json').write_text(json.dumps(body))
        reject_record('missing record',lambda:(records/'coupled.json').unlink())
        reject_record('extra record',lambda:(records/'extra.json').write_text('{}'))
        reject_record('wrong run ID',lambda:changed_record(lambda b:b.update(run_id='wrong')))
        reject_record('wrong kind',lambda:changed_record(lambda b:b.update(kind='wrong')))
        reject_record('missing phase',lambda:changed_record(lambda b:b['trajectories'][0]['phases'].pop()))
        reject_record('missing effect field',lambda:changed_record(lambda b:b['trajectories'][0]['phases'][0]['reads'][0]['effects'][0].pop('duration')))
        reject_record('record permissions',lambda:(records/'coupled.json').chmod(0o644))
        reject_record('directory permissions',lambda:records.chmod(0o755))
        restore()
        changed_record(lambda b:b['trajectories'][0]['phases'][0]['reads'][0]['effects'][0].update(duration='unrestricted-measurement',progress=None))
        assert phases.feedback_records(ROOT,output,policy)['numeric_or_convergence_oracle'] is False
        (output/'feedback-wpt/ASSESSMENT.json').write_text(json.dumps({'complete':True,'rows':[{'status':'FAIL'},{'status':'PASS'}]}))
        assert phases.feedback_records(ROOT,output,policy)['calibrated_acquisition'] is False
    with tempfile.TemporaryDirectory(prefix='duration-tristate-failure-') as temporary:
        output = Path(temporary)
        failure = AssertionError('synthetic saved candidate comparison failure')
        def save(path,value):
            with path.open('x') as stream:json.dump(value,stream)
        def fail(*args):raise failure
        fake_wpt = SimpleNamespace(save=save,run=fail)
        fake_comparison = SimpleNamespace(original_directory=lambda *args:output/'synthetic-original')
        saved_load,saved_records = phases.load,phases.feedback_records
        phases.load = lambda name,path:fake_wpt if path.name=='wpt.py' else fake_comparison
        phases.feedback_records = lambda *args:{'calibrated_acquisition':False,'records':{},'numeric_or_convergence_oracle':False}
        try:phases.run(ROOT,HERE,output,policy,{},lambda:{'synthetic':True},{},lambda:False)
        except AssertionError as error:assert error is failure
        else:raise AssertionError('failure converted to success')
        finally:phases.load,phases.feedback_records=saved_load,saved_records
        assert json.loads((output/'FEEDBACK-RECORDS.json').read_bytes())['calibrated_acquisition'] is False
        assert json.loads((output/'DIAGNOSTICS.json').read_bytes())['phase_error']==repr(failure)
        assert not (output/'PHASES-POST.json').exists()
    actual_replayed = False
    if policy['baseline_binding'] is not None:
        binding = policy['baseline_binding']
        directory = ROOT/binding['directory']
        for capsule,pin in [(ROOT/policy['baseline_capsule']['directory'],policy['baseline_capsule']['sha256']),
                            (directory,binding['manifest_sha256'])]:
            assert hashlib.sha256((capsule/'FILES.json').read_bytes()).hexdigest() == pin
            for name,expected in json.loads((capsule/'FILES.json').read_bytes()).items():
                assert hashlib.sha256((capsule/name).read_bytes()).hexdigest() == expected
        terminal = json.loads((directory/binding['terminal_path']).read_bytes())
        assert terminal == binding['terminal'] and terminal['exit'] == 0
        assert terminal['owner_sha256'] == policy['baseline_capsule']['sha256']
        assert terminal['result_sha256'] == binding['result_sha256'] == hashlib.sha256((directory/'RESULT.json').read_bytes()).hexdigest()
        comparison.replay_all(ROOT,policy)
        actual_replayed = True
    return {'positive_comparisons':1,'positive_metadata_joins':1,'positive_checkpoint_chains':1,'positive_record_sets':2,'failed_calibration_retained_as_false':True,
            'negative_controls':rejected,'artifact_references_authenticated':authenticated,
            'deferred_nonartifact_references':deferred,'fresh_original_replayed':actual_replayed,
            'browser_build_or_live_guard_executed':False,'scratch_removed':True,'failure_diagnostic_retention_simulated':True,'positive_raw_only_state_join':True}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
