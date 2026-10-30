import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    assert policy['execution_enabled'] == policy['trace_execution_enabled']
    assert isinstance(policy['execution_enabled'],bool)
    pending = ('baseline_binding','controls','prepared_application_metadata','prepared_flag_hashes','prepared_state_evidence')
    if any(policy[key] is None for key in pending):
        assert all(policy[key] is None for key in pending)
        assert not policy['execution_enabled'] and policy['activation_pending']
    elif policy['execution_enabled']:
        assert policy['activation_pending'] == []
    assert policy['trace_source_role'] == 'instrumented-candidate'
    assert policy['source_paths'] == ['dom/animation/EffectCompositor.cpp','servo/components/style/matching.rs']
    assert policy['runtime_output'] == 'artifacts/css-contextual-duration-feedback-trace-candidate-runtime-1'
    assert policy['trace_environment'] == {'MOZ_DURATION_RESTYLE_TRACE':'1'}
    assert policy['wpt'] == policy['phases']['feedback'] and set(policy['phases']) == {'feedback'}
    comparison = load('trace_policy_comparison',HERE / 'comparison.py')
    assert policy['wpt'] == comparison.expected_wpt(ROOT,policy)
    source = read(ROOT / policy['baseline_capsule']['directory'] / 'POLICY.json')
    for key in ('head','restored_app_revision','accepted_current_payloads','accepted_epoch_records','source_context_pins','resource_policy','rebuilt_binaries','original_build','logger','feedback_transport','trace_parser','trace_environment','record_schema_helper','record_kinds'):
        assert policy[key] == source[key], key
    assert len(policy['accepted_current_payloads']) == 29
    roles = read(HERE / 'SOURCE-ROLES.json')
    original_roles = read(ROOT / policy['baseline_capsule']['directory'] / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths'])
    assert roles['dom/animation/EffectCompositor.cpp'] == original_roles['dom/animation/EffectCompositor.cpp']
    matching = roles['servo/components/style/matching.rs']
    assert matching['base_sha256'] == source['source_context_pins']['servo/components/style/matching.rs'] == '41e95acc6e2903963df96bee70c260aeebffdd9b4d5dfc18bd6e875f9352035d'
    assert matching['candidate_sha256'] == 'c3b2ddf2a3fb0ab2a8f5e74acaad0502e9e61f83e0427a300e106207ea1e7e64'
    if policy['baseline_binding'] is not None:
        assert policy['baseline_binding']['directory'] == 'artifacts/css-contextual-duration-feedback-trace-original-runtime-1'
        assert policy['baseline_binding']['terminal_path'] == 'ROOT-TERMINAL.json'
        assert policy['baseline_binding']['terminal']['exit'] == 0
        assert policy['controls']['OWNED.json'] == source['controls']['OWNED.json']
        assert policy['controls']['ROLE.json'] == source['controls']['ROLE.json']
        assert policy['prepared_flag_hashes'] == source['prepared_flag_hashes']
        assert policy['prepared_application_metadata']['revision'] == policy['restored_app_revision']
        for key in ('restoration','refresh'):
            path = policy['prepared_state_evidence'][key]
            assert policy['references'][path] == sha(ROOT / path)


def check():
    policy = read(HERE / 'POLICY.json')
    validate_policy(policy)
    authenticated, deferred = 0, []
    for name,pin in policy['references'].items():
        if name.startswith('artifacts/'):
            assert sha(ROOT / name) == pin,name
            authenticated += 1
        else:
            deferred.append(name)
    for package in (policy['logger'],policy['feedback_transport'],policy['trace_parser'],policy['baseline_capsule']):
        directory = ROOT / package['directory']
        assert sha(directory / 'FILES.json') == package.get('manifest_sha256',package.get('sha256'))
        for name,entry in read(directory / 'FILES.json').items():
            assert sha(directory / name) == (entry['sha256'] if isinstance(entry,dict) else entry)
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    original = ROOT / policy['baseline_capsule']['directory']
    for name in ('assess.py','trace.py'):
        assert (HERE / name).read_bytes() == (original / name).read_bytes()
    old_records = (original / 'phases.py').read_text().split('\ndef feedback_records',1)[1].split('\ndef require_calibration',1)[0]
    new_records = (HERE / 'phases.py').read_text().split('\ndef feedback_records',1)[1].split('\ndef require_calibration',1)[0]
    assert old_records == new_records
    phases = load('trace_candidate_phase_checks',HERE / 'phases.py')
    comparison = load('trace_candidate_comparison_checks',HERE / 'comparison.py')
    synthetic = load('trace_candidate_synthetic',ROOT / 'artifacts/css-contextual-duration-feedback-consistency-original-v2/check.py')
    assessor = load('trace_candidate_assessor',HERE / 'assess.py')
    checks = load('trace_candidate_wpt_checks',ROOT / policy['wpt']['checks_helper'])
    config, app, events = synthetic.synthetic(policy['wpt'])
    config['phase_revisions']['candidate'] = app['revision']
    app['trace_source_role'] = 'instrumented-original'
    observed = assessor.assess(events,0,config,checks,run_binding=app)
    assert observed['complete']
    candidate_app = dict(app,browser_build_id='synthetic-trace-candidate',source_role='candidate',trace_source_role='instrumented-candidate')
    candidate = copy.deepcopy(events)
    candidate[0]['run_info']['browser_build_id'] = candidate_app['browser_build_id']
    passed = assessor.assess(candidate,0,config,checks,original=observed,run_binding=candidate_app)
    assert passed['complete'] and passed['comparison_gate_passed']
    failed = copy.deepcopy(candidate)
    for event in failed:
        if event.get('action') == 'test_status':
            event.update(status='FAIL',expected='PASS',message='synthetic fixed 2000 ms override failure')
    failed_assessment = assessor.assess(failed,1,config,checks,original=observed,run_binding=candidate_app)
    assert failed_assessment['complete'] and not failed_assessment['comparison_gate_passed']
    assert len(failed_assessment['rows']) == 2 and all(row['status']=='FAIL' for row in failed_assessment['rows'])
    rejected = []
    def reject(label,operation):
        try:operation()
        except (AssertionError,KeyError,ValueError):rejected.append(label)
        else:raise AssertionError(label)
    reject('failed controls are not calibration',lambda:phases.require_calibration(failed_assessment,{'calibrated_acquisition':False}))
    for key,value in [('source_paths',['dom/animation/EffectCompositor.cpp']),('trace_source_role','instrumented-original'),('runtime_output','artifacts/css-contextual-duration-feedback-trace-original-runtime-1'),('execution_enabled',True)]:
        changed = copy.deepcopy(policy);changed[key]=value
        reject('policy '+key,lambda:validate_policy(changed))
    metadata = {'revision':policy['head'],'build_revision':policy['head'],'source_role':'candidate','trace_source_role':'instrumented-candidate'}
    phases.require_metadata(policy,metadata)
    for key,value in [('revision',policy['restored_app_revision']),('build_revision',policy['restored_app_revision']),('source_role','original'),('trace_source_role','instrumented-original')]:
        changed = dict(metadata);changed[key]=value
        reject('metadata '+key,lambda:phases.require_metadata(policy,changed))
    before = {'index':{'raw_index':'before','head':'unchanged','entries':'same'},'nested_index':{'raw':'same'},'working_sources_binaries_research_preserved':True}
    after = copy.deepcopy(before);after['index']['raw_index']='after'
    current = copy.deepcopy(after);current['index']['raw_index']='reconciled'
    comparison.require_restored_snapshots(before,after,current)
    for label,changed in [('root HEAD',copy.deepcopy(current)),('nested index',copy.deepcopy(current)),('source preservation',copy.deepcopy(current))]:
        if label=='root HEAD':changed['index']['head']='wrong'
        elif label=='nested index':changed['nested_index']['raw']='wrong'
        else:changed['working_sources_binaries_research_preserved']=False
        reject('snapshot '+label,lambda:comparison.require_restored_snapshots(before,after,changed))
    with tempfile.TemporaryDirectory(prefix='css-trace-candidate-check-') as directory:
        output = Path(directory)
        failure = AssertionError('synthetic candidate comparison failed')
        def save(path,value):
            with path.open('x') as stream:json.dump(value,stream)
        def fail(*args):raise failure
        fake_wpt = SimpleNamespace(save=save,run=fail)
        fake_trace = SimpleNamespace(capture=lambda phase:{'trace_syntax_and_sequence_valid':True,'numeric_or_convergence_oracle':False})
        fake_comparison = SimpleNamespace(original_directory=lambda *args:output/'synthetic-original')
        saved_load, saved_records = phases.load, phases.feedback_records
        phases.load = lambda name,path:{'wpt.py':fake_wpt,'trace.py':fake_trace,'comparison.py':fake_comparison}[path.name]
        phases.feedback_records = lambda *args:{'calibrated_acquisition':False,'records':{},'numeric_or_convergence_oracle':False}
        try:
            phases.run(ROOT,HERE,output,policy,{},lambda:{'synthetic':True},{},lambda:False)
        except AssertionError as error:
            assert error is failure
        else:raise AssertionError('candidate rejection converted to success')
        finally:phases.load, phases.feedback_records = saved_load,saved_records
        assert read(output/'FEEDBACK-RECORDS.json')['calibrated_acquisition'] is False
        assert read(output/'TRACE-INDEX.json')['trace_syntax_and_sequence_valid']
        assert read(output/'DIAGNOSTICS.json')['phase_error'] == repr(failure)
        assert not (output/'PHASES-POST.json').exists()
    if policy['baseline_binding'] is not None:
        comparison.replay_all(ROOT,policy)
    return {'positive_checks':6,'negative_checks':rejected,'candidate_failure_retained_after_diagnostics':True,'artifact_references_authenticated':authenticated,'deferred_nonartifact_references':deferred,'actual_baseline_binding_pending':policy['baseline_binding'] is None,'live_guard_build_browser_executed':False}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2,sort_keys=True))
