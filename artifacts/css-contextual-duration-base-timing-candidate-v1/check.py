import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    source_dir = ROOT / policy['baseline_capsule']['directory']
    assert sha(source_dir / 'FILES.json') == policy['baseline_capsule']['sha256']
    assert sha(source_dir / 'POLICY.json') == policy['original_admission_policy_sha256']
    source = read(source_dir / 'POLICY.json')
    load('original_saved_binding_check', source_dir / 'check.py').check_binding(source)
    assert policy['controls'] == source['controls'] and policy['head'] == source['head']
    assert policy['prepared_application_metadata'] == {key: value for key, value in source['prepared_application_metadata'].items() if key not in ('build_revision', 'harness_revision', 'source_role')}
    assert policy['accepted_current_payloads'] == source['accepted_current_payloads'] and len(policy['accepted_current_payloads']) == 29
    assert policy['source_context_pins'] == source['source_role_pins']
    assert policy['record_kinds'] == source['record_kinds'] and len(policy['record_kinds']) == 7
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths']) == {'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h', 'servo/components/style/matching.rs', 'layout/style/nsAnimationManager.cpp'}
    landing = ROOT / policy['landing_package']['directory']
    assert sha(landing / 'FILES.json') == policy['landing_package']['manifest_sha256']
    payloads = read(landing / 'PAYLOADS.json')
    prototype = ROOT / policy['timing_prototype']['directory']
    assert sha(prototype / 'FILES.json') == policy['timing_prototype']['manifest_sha256']
    native = read(prototype / 'SOURCE-ROLES.json')
    built = read(ROOT / policy['original_build']['epoch'])
    for name, role in roles.items():
        assert role['base_sha256'] == source['source_role_pins'][name] == built['pins'][name]
        assert name not in built['modified_native_paths']
        if name in native:
            assert role['candidate_sha256'] == native[name]['candidate_sha256'] == sha(ROOT / native[name]['candidate_capture'])
            if name == 'layout/style/nsAnimationManager.cpp':
                assert role['base_sha256'] == native[name]['base_sha256']
            else:
                assert native[name]['base_sha256'] == payloads[name]['candidate_sha256']
        else:
            assert role['base_sha256'] == payloads[name]['base_sha256']
            assert role['candidate_sha256'] == sha(landing / payloads[name]['payload']) == payloads[name]['candidate_sha256']
        assert role['candidate_sha256'] == sha(ROOT / role['candidate_capture'])
    comparison = load('progress_comparison_check', HERE / 'comparison.py')
    assert policy['wpt'] == comparison.expected_wpt(ROOT, policy)
    assert len(policy['wpt']['expected_subtests']) == 3 and sum(map(len, policy['wpt']['expected_subtests'].values())) == 7
    assert policy['admission_binding'] == source['admission_binding']
    trace_policy = read(ROOT / source['restored_owner'] / 'POLICY.json')
    assert policy['prepared_flag_hashes'] == trace_policy['prepared_flag_hashes']
    assert policy['head'] == source['head'] == policy['wpt']['harness_revision']
    if policy['baseline_binding'] is None:
        assert not policy['execution_enabled'] and not policy['candidate_execution_enabled'] and policy['activation_pending']


def validate_actual_bindings(policy):
    validate_policy(policy)
    assert policy['baseline_binding'] is not None
    return load('progress_actual_original', HERE / 'comparison.py').replay_all(ROOT, policy)


def check(policy):
    validate_policy(policy)
    for name, digest in policy['references'].items():
        assert sha(ROOT / name) == digest, name
    source = read(ROOT / policy['baseline_capsule']['directory'] / 'POLICY.json')
    comparison = load('progress_static_comparison', HERE / 'comparison.py')
    complete = {'complete': True, 'errors': [], 'missing': [], 'records': {str(n): {} for n in range(7)}}
    comparison.require_complete_collection(complete, {'complete_records': 7})
    missing = dict(complete, complete=False, records={'a': {}}, missing=[{'status': 'FAIL'}])
    try:
        comparison.require_complete_collection(missing, {'complete_records': 7})
    except AssertionError:
        pass
    else:
        raise AssertionError('Missing original FAIL record was accepted as complete')
    assessor = load('progress_static_assessor', HERE / 'assess.py')
    checks = load('progress_static_streams', ROOT / policy['wpt']['checks_helper'])
    settings = copy.deepcopy(policy['wpt'])
    settings['harness_revision'] = 'a' * 40
    settings['phase_revisions'] = {'original': 'b' * 40, 'candidate': 'a' * 40}
    app = {'browser_build_id': 'original-build', 'revision': 'b' * 40, 'build_revision': 'b' * 40, 'harness_revision': 'a' * 40, 'source_role': 'original', 'sha256': 'c' * 64, 'path': 'synthetic/application.ini', 'resolved': 'synthetic/application.ini'}
    candidate_app = dict(app, browser_build_id='candidate-build', revision='a' * 40, build_revision='a' * 40, source_role='candidate', sha256='d' * 64)
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': 'original-build', 'revision': 'a' * 40}}]
    for page, names in settings['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': page})
        for name in names:
            events.append({'action': 'test_status', 'test': page, 'subtest': name, 'status': 'PASS'})
        events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    original = copy.deepcopy(events)
    rows = [row for row in original if row['action'] == 'test_status']
    for row in rows[:1]:
        row.update(status='FAIL', expected='PASS', message='synthetic ordinary or animated failure')
    settings['target_subtests'] = {page: [row['subtest'] for row in rows if row['test'] == page and row['status'] == 'FAIL'] for page in settings['expected_subtests']}
    settings.update(expected_target_count=1, expected_control_count=6, expected_regression_signature_count=9)
    configuration = comparison.phase_policy(settings)
    saved = assessor.assess(original, 1, configuration, checks, run_binding=app)
    assert saved['complete'] and len(saved['regression_signature']) == 9
    candidate = copy.deepcopy(events)
    candidate[0]['run_info']['browser_build_id'] = 'candidate-build'

    def evaluate(stream, code=0):
        return assessor.assess(stream, code, configuration, checks, original=saved, run_binding=candidate_app)

    assert evaluate(candidate)['comparison_gate_passed']
    rejected = []

    def reject(label, mutation, code=0):
        value = copy.deepcopy(candidate)
        mutation(value)
        assert not evaluate(value, code)['comparison_gate_passed'], label
        rejected.append(label)

    def row(value):
        return [item for item in value if item.get('action') == 'test_status'][1]

    reject('original PASS changed', lambda value: row(value).update(status='FAIL', expected='PASS', message='regression'), 1)
    reject('repair still FAIL', lambda value: [item for item in value if item.get('action') == 'test_status'][0].update(status='FAIL', expected='PASS', message='still stale'), 1)
    reject('PASS message changed', lambda value: row(value).update(message='new diagnostic'))
    reject('expected field presence changed', lambda value: row(value).update(expected='PASS'))
    reject('intermittent field presence changed', lambda value: row(value).update(known_intermittent=[]))
    reject('missing callback', lambda value: value.remove(row(value)))
    reject('duplicate callback', lambda value: value.insert(2, copy.deepcopy(row(value))))
    reject('ending changed', lambda value: next(item for item in value if item.get('action') == 'test_end').update(message='different'))
    reject('wrong build', lambda value: value[0]['run_info'].update(browser_build_id='wrong'))
    reject('crash', lambda value: value.append({'action': 'crash'}))
    reject('wrong exit', lambda value: None, 1)
    check_calibration(policy)
    check_failure_retention(policy)
    check_record_projection(policy)
    print(json.dumps({'synthetic_contextual_failure_repaired': True, 'ordinary_or_animated_failure_names_treated_equally': True, 'negative_checks': rejected, 'references_authenticated': len(policy['references']), 'baseline_actual_binding_pending': policy['baseline_binding'] is None, 'browser_or_live_guard_executed': False}))


def check_failure_retention(policy):
    import tempfile
    from types import SimpleNamespace
    phases = load('progress_phase_failure_test', HERE / 'phases.py')
    collector = load('progress_collector_failure_test', HERE / 'records.py')
    rows = [{'test': rule['page'], 'subtest': rule['subtest'], 'status': 'FAIL'} for rule in policy['record_kinds'].values()]
    def save(path, value):
        with path.open('x') as stream:
            json.dump(value, stream)
    def fail_run(root, here, phase, *args):
        phase.mkdir()
        save(phase / 'ASSESSMENT.json', {'complete': True, 'rows': rows})
        (phase / 'raw.jsonl').write_text('retained synthetic raw evidence')
        raise AssertionError('synthetic comparison failure')
    fake = SimpleNamespace(save=save, run=fail_run)
    calibration = load('failure_calibration', HERE / 'calibration.py')
    phases.load = lambda name, path: fake if path.name == 'wpt.py' else calibration if path.name == 'calibration.py' else collector
    with tempfile.TemporaryDirectory(prefix='css-progress-phase-check-', dir='/private/tmp') as temporary:
        output = Path(temporary)
        current = dict(policy, baseline_binding={'directory': 'synthetic-original'})
        try:
            phases.run(ROOT, HERE, output, current, {}, lambda: {'synthetic': True}, {}, lambda: False)
        except AssertionError as error:
            assert str(error) == 'synthetic comparison failure'
        else:
            raise AssertionError('failed comparison was relabeled successful')
        receipt = read(output / 'PROGRESS-RECORDS.json')
        assert len(receipt['missing']) == 7 and not receipt['errors'] and not receipt['complete']
        assert (output / 'candidate-wpt/raw.jsonl').read_text() == 'retained synthetic raw evidence'
    assert not output.exists()


def synthetic_record(kind):
    if kind.startswith('depth-'):
        source = ROOT / 'artifacts/css-contextual-duration-finite-depth-original-runtime-1/progress-records' / (kind + '.json')
    else:
        source = ROOT / 'artifacts/css-contextual-duration-same-element-original-runtime-1/progress-records' / ((kind + '.json') if kind.startswith('same-element-') else 'same-element-acyclic.json')
    value = read(source)
    value.update(kind=kind, run_id='synthetic_record_projection')
    return value


def check_calibration(policy):
    source = ROOT / policy['baseline_capsule']['directory']
    original = load('original_calibration_checks', source / 'check.py')
    original.check_calibration(read(source / 'POLICY.json'))


def check_record_projection(policy):
    import tempfile
    phases = load('record_projection_check', HERE / 'phases.py')
    with tempfile.TemporaryDirectory(prefix='same-element-record-projection-', dir='/private/tmp') as temporary:
        root = Path(temporary)
        original = root / 'original/progress-records'
        candidate = root / 'candidate/progress-records'
        original.mkdir(parents=True)
        candidate.mkdir(parents=True)
        collection = {'records': {}, 'errors': [], 'missing': []}
        for filename in policy['record_kinds']:
            body = synthetic_record(policy['record_kinds'][filename]['kind'])
            (original / filename).write_text(json.dumps(body))
            changed = copy.deepcopy(body)
            changed['run_id'] = 'distinct_candidate_run'
            sample = changed['observations']['contextual']['samples'][0]
            sample['opacity' if 'opacity' in sample else 'value'] = None
            (candidate / filename).write_text(json.dumps(changed))
            collection['records'][filename] = {'schema_valid': True}
        current = dict(policy, baseline_binding={'directory': 'original'})
        report = phases.record_comparison(root, root / 'candidate', current, collection)
        assert all(row['observations_equal'] is False for row in report['records'].values())
        assert not report['numeric_or_cycle_endpoint_gate']
        first = next(iter(policy['record_kinds']))
        (candidate / first).write_text('malformed retained body')
        collection['records'][first]['schema_valid'] = False
        collection['errors'] = ['retained schema failure']
        report = phases.record_comparison(root, root / 'candidate', current, collection)
        assert report['records'][first]['candidate'] is None
        assert report['candidate_collection']['errors'] == ['retained schema failure']
    assert not root.exists()


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check(read(HERE / 'POLICY.json'))
