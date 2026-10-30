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
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    assert policy['execution_enabled'] == policy['trace_execution_enabled']
    assert isinstance(policy['execution_enabled'], bool)
    if policy['execution_enabled']:
        assert policy['activation_pending'] == []
    else:
        assert policy['activation_pending']
    assert policy['trace_source_role'] == 'instrumented-original'
    assert policy['source_paths'] == ['dom/animation/EffectCompositor.cpp']
    assert policy['trace_environment'] == {'MOZ_DURATION_RESTYLE_TRACE':'1'}
    assert policy['runtime_output'] == 'artifacts/css-contextual-duration-feedback-trace-original-runtime-1'
    assert policy['wpt'] == policy['phases']['feedback'] and set(policy['phases']) == {'feedback'}
    settings = policy['wpt']
    assert settings['phase_revisions'] == {'original':policy['head']}
    assert settings['harness_revision'] == policy['head']
    assert policy['restored_app_revision'] != policy['head']
    assert policy['prepared_application_metadata']['revision'] == policy['restored_app_revision']
    inputs = read(ROOT / policy['feedback_transport']['directory'] / 'INPUTS.json')
    assert sha(ROOT / policy['feedback_transport']['directory'] / 'INPUTS.json') == policy['feedback_transport']['inputs_sha256']
    for key in ('resources','metadata','manifest','test_types','expected_subtests'):
        assert settings[key] == inputs[key]
    assert inputs['expected_callbacks'] == 2 and inputs['expected_endings'] == 1
    assert inputs['calibrated_acquisition_requires_all_pass'] and inputs['numeric_feedback_oracle'] is False
    assert (settings['expected_subtest_count'],settings['expected_target_count'],settings['expected_control_count'],settings['expected_page_count'],settings['expected_regression_signature_count']) == (2,0,2,1,3)
    assert settings['target_subtests'] == {}
    assert policy['record_schema_helper'] == inputs['transport']['helper']
    assert policy['record_kinds'] == {name:kind for kind,name in inputs['transport']['record_files'].items()}
    roles = read(HERE / 'SOURCE-ROLES.json')
    logger = read(ROOT / policy['logger']['directory'] / 'SOURCE-ROLES.json')
    assert set(roles) == {logger['source_path']} == {'dom/animation/EffectCompositor.cpp'}
    for kind in ('base','candidate'):
        entry = roles[logger['source_path']]
        assert entry[kind + '_sha256'] == logger[kind + '_sha256']
        assert entry[kind + '_capture'] == policy['logger']['directory'] + '/' + logger[kind + '_capture']
    assert policy['source_context_pins']['servo/components/style/matching.rs'] == '41e95acc6e2903963df96bee70c260aeebffdd9b4d5dfc18bd6e875f9352035d'
    predecessor = read(ROOT / 'artifacts/css-contextual-duration-feedback-consistency-candidate-v1/POLICY.json')
    for key in ('accepted_current_payloads','accepted_epoch_records','source_context_pins','resource_policy','rebuilt_binaries','original_build','prepared_flag_hashes'):
        assert policy[key] == predecessor[key], key
    assert len(policy['accepted_current_payloads']) == 29
    assert policy['controls']['OWNED.json'] == predecessor['controls']['OWNED.json']
    assert policy['controls']['ROLE.json'] == predecessor['controls']['ROLE.json']
    terminal = read(ROOT / policy['prepared_state_evidence']['restoration'])
    refresh = read(ROOT / policy['prepared_state_evidence']['refresh'])
    assert terminal['state_and_application_restoration_independently_verified']
    assert terminal['raw_replay_verified'] and terminal['backup_removed_bytes'] == 1008605176
    assert refresh['source_application_git_and_acceptance_unchanged'] and refresh['full_state_matches_restored_pair']
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    assert policy['controls']['CURRENT-EPOCH.json'] == refresh['after_epoch']
    assert refresh['raw_index']['after'] == terminal['raw_index_observation']['after']
    app = policy['prepared_application_metadata']
    assert app['entry_identity'] == terminal['restored_application_entry']['identity']
    assert app['identity'] == terminal['restored_application_target']['identity']
    assert app['sha256'] == terminal['restored_application_target']['sha256']


def check():
    policy = read(HERE / 'POLICY.json')
    validate_policy(policy)
    authenticated, deferred = 0, []
    for name, pin in policy['references'].items():
        if not name.startswith('artifacts/'):
            deferred.append(name)
            continue
        assert sha(ROOT / name) == pin, name
        authenticated += 1
    for package in (policy['logger'],policy['feedback_transport'],policy['trace_parser']):
        directory = ROOT / package['directory']
        assert sha(directory / 'FILES.json') == package['manifest_sha256']
        for name, entry in read(directory / 'FILES.json').items():
            assert sha(directory / name) == (entry['sha256'] if isinstance(entry,dict) else entry)
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    predecessor = ROOT / 'artifacts/css-contextual-duration-feedback-consistency-candidate-v1'
    assert (HERE / 'assess.py').read_bytes() == (predecessor / 'assess.py').read_bytes()
    old_records = (predecessor / 'phases.py').read_text().split('\ndef feedback_records',1)[1].split('\ndef run(',1)[0].strip()
    new_records = (HERE / 'phases.py').read_text().split('\ndef feedback_records',1)[1].split('\ndef require_calibration',1)[0].strip()
    assert old_records == new_records
    phases = load('trace_phases_check', HERE / 'phases.py')
    trace = load('trace_parser_check', HERE / 'trace.py')
    synthetic = load('trace_synthetic', ROOT / 'artifacts/css-contextual-duration-feedback-consistency-original-v2/check.py')
    assessor = load('trace_assessor', HERE / 'assess.py')
    checks = load('trace_wpt_checks', ROOT / policy['wpt']['checks_helper'])
    config, app, events = synthetic.synthetic(policy['wpt'])
    app['trace_source_role'] = 'instrumented-original'
    observed = assessor.assess(events,0,config,checks,run_binding=app)
    phases.require_calibration(observed, {'calibrated_acquisition':True})
    rejected = []
    def reject(label, operation):
        try:
            operation()
        except (AssertionError, KeyError, ValueError):
            rejected.append(label)
        else:
            raise AssertionError(label)
    for index in (2,3):
        failed = copy.deepcopy(events)
        failed[index].update(status='FAIL',expected='PASS',message='synthetic fixed-duration calibration failure')
        result = assessor.assess(failed,1,config,checks,run_binding=app)
        assert result['complete']
        reject('original callback failure ' + str(index),lambda:phases.require_calibration(result,{'calibrated_acquisition':False}))
    reject('false record calibration',lambda:phases.require_calibration(observed,{'calibrated_acquisition':False}))
    for key,value in [('source_paths',['servo/components/style/matching.rs']),('runtime_output','artifacts/wrong'),('trace_source_role','candidate'),('trace_environment',{})]:
        changed = copy.deepcopy(policy); changed[key] = value
        reject('policy ' + key,lambda:validate_policy(changed))
    metadata = {'revision':policy['head'],'build_revision':policy['head'],'source_role':'original','trace_source_role':'instrumented-original'}
    phases.require_metadata(policy,metadata)
    for key,value in [('revision',policy['restored_app_revision']),('build_revision',policy['restored_app_revision']),('source_role','candidate'),('trace_source_role','original')]:
        changed = dict(metadata); changed[key] = value
        reject('metadata ' + key,lambda:phases.require_metadata(policy,changed))
    def entry(seq=1,pid=23,kind='coupled-passive'):
        return {'line':seq,'text':f'DURATION_RESTYLE_TRACE pid={pid} seq={seq} id={kind} element=0x123 pseudo=0 identifier=0x0 stage=request-before cascade=0 request=2 present=1 bit=1 servo=0 pre=0 root=0x0 flags=0 effect=0x0 animation=0x0'}
    intact = trace.parse('\n'.join(e['text'] for e in [entry(),entry(2)]))
    assert intact['trace_syntax_and_sequence_valid'] and len(intact['events_in_input_order']) == 2
    cap = trace.parse(entry()['text'] + '\nDURATION_RESTYLE_TRACE pid=23 cap-exhausted limit=4096')
    assert cap['truncated'] and cap['errors'] and not cap['trace_syntax_and_sequence_valid']
    for label,stream in [('gap',[entry(),entry(3)]),('duplicate',[entry(),entry()]),('missing start',[entry(2)])]:
        assert not trace.parse('\n'.join(e['text'] for e in stream))['trace_syntax_and_sequence_valid'];rejected.append('intact trace ' + label)
    for label,item in [('unknown ID',entry(kind='other')),('sequence overflow',entry(4097)),('zero pid',entry(pid=0))]:
        bad = trace.parse(item['text']);assert not bad['trace_syntax_and_sequence_valid'] and bad['errors'];rejected.append('trace event ' + label)
    independent = trace.parse(entry()['text'] + '\n' + entry(pid=24)['text'])
    assert independent['trace_syntax_and_sequence_valid']
    with tempfile.TemporaryDirectory(prefix='css-trace-owner-check-') as directory:
        output = Path(directory)
        captured = output / 'capture'
        captured.mkdir()
        raw = json.dumps({'action':'process_output','data':entry()['text']}) + '\n'
        (captured / 'raw.jsonl').write_text(raw)
        (captured / 'wpt.log').write_text('timestamp ' + entry()['text'] + '\n')
        captured_result = trace.capture(captured)
        assert captured_result['primary_stream'] == 'raw' and captured_result['trace_syntax_and_sequence_valid']
        assert (captured / 'raw.jsonl').read_text() == raw
        (captured / 'raw.jsonl').write_text('{}\n')
        assert trace.capture(captured)['primary_stream'] == 'log'
        (captured / 'raw.jsonl').write_text(json.dumps({'action':'unexpected','data':entry()['text']}) + '\n')
        malformed = trace.capture(captured)
        assert malformed['primary_stream'] == 'raw' and malformed['errors']
        assert not malformed['trace_syntax_and_sequence_valid']
        rejected.append('malformed raw carrier cannot fall back to valid log')
        failure = AssertionError('synthetic saved WPT rejection')
        def save(path,value):
            with path.open('x') as stream:json.dump(value,stream)
        def fail(*args):raise failure
        fake_wpt = SimpleNamespace(save=save,run=fail)
        fake_trace = SimpleNamespace(capture=lambda phase:dict(cap))
        original_load, original_records = phases.load, phases.feedback_records
        phases.load = lambda name,path: fake_wpt if path.name == 'wpt.py' else fake_trace
        phases.feedback_records = lambda *args:{'calibrated_acquisition':False,'records':{},'numeric_or_convergence_oracle':False}
        try:
            phases.run(ROOT,HERE,output,policy,{},lambda:{'synthetic':True},{},lambda:False)
        except AssertionError as error:
            assert error is failure
        else:
            raise AssertionError('failed WPT converted to success')
        finally:
            phases.load, phases.feedback_records = original_load, original_records
        assert read(output / 'FEEDBACK-RECORDS.json')['calibrated_acquisition'] is False
        assert read(output / 'TRACE-INDEX.json')['truncated']
        assert read(output / 'DIAGNOSTICS.json')['phase_error'] == repr(failure)
        assert not (output / 'PHASES-POST.json').exists()
    return {'positive_checks':8,'negative_checks':rejected,'failure_diagnostic_retention_simulated':True,'artifact_references_authenticated':authenticated,'deferred_nonartifact_references':deferred,'live_guard_build_browser_executed':False}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2,sort_keys=True))
