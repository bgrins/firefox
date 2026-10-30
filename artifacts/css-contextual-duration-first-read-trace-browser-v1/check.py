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
    if policy['head'] is None:
        assert all(policy[key] is None for key in ('controls', 'prepared_application_metadata', 'prepared_flag_hashes', 'native_checkpoint', 'fresh_restoration_binding', 'role_current_unpinned_sources'))
        assert not policy['execution_enabled'] and not policy['candidate_execution_enabled'] and policy['activation_pending']
    else:
        assert policy['head'] == source['head'], 'A changed research HEAD requires a separately reviewed handoff or fresh original'
        historical = {key: value for key, value in source['prepared_application_metadata'].items() if key not in ('build_revision', 'harness_revision', 'source_role', 'identity', 'entry_identity')}
        assert historical == {key: value for key, value in policy['prepared_application_metadata'].items() if key not in ('identity', 'entry_identity')}
    assert policy['accepted_current_payloads'] == source['accepted_current_payloads'] and len(policy['accepted_current_payloads']) == 29
    assert policy['source_context_pins'] == source['source_role_pins']
    assert policy['record_kinds'] == source['record_kinds'] and len(policy['record_kinds']) == 9
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths']) == {'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h', 'servo/components/style/matching.rs', 'layout/base/PresShell.h', 'layout/style/nsComputedDOMStyle.cpp'}
    landing = ROOT / policy['landing_package']['directory']
    assert sha(landing / 'FILES.json') == policy['landing_package']['manifest_sha256']
    payloads = read(landing / 'PAYLOADS.json')
    package = ROOT / policy['instrumentation']['directory']
    assert sha(package / 'FILES.json') == policy['instrumentation']['manifest_sha256']
    traced = read(package / 'SOURCE-ROLES.json')
    for fixture in read(package / 'FIXTURES.json'):
        page = fixture['execution_page']
        assert policy['wpt']['resources'][page.lstrip('/')] == fixture['fixture']
        assert policy['wpt']['expected_subtests'][page] == fixture['roster'][page]
        assert sha(ROOT / fixture['executed_capture']) == sha(ROOT / fixture['fixture']['path']) == fixture['fixture']['sha256']
    built = read(ROOT / policy['original_build']['epoch'])
    join = read(ROOT / 'artifacts/css-contextual-duration-first-read-branch-join-v1/SOURCE-JOIN.json')
    assert policy['role_build_unpinned_sources'] == ['layout/base/PresShell.h']
    for name, role in roles.items():
        assert sha(ROOT / role['base_capture']) == role['base_sha256']
        assert sha(ROOT / role['candidate_capture']) == role['candidate_sha256']
        assert name not in built['modified_native_paths']
        if name in payloads:
            assert role['base_sha256'] == source['source_role_pins'][name] == built['pins'][name] == payloads[name]['base_sha256']
            semantic = payloads[name]['candidate_sha256']
            assert sha(landing / payloads[name]['payload']) == semantic
            if name in traced:
                assert traced[name]['base_sha256'] == semantic
            else:
                assert role['candidate_sha256'] == semantic
        else:
            captured = join['files'][name]
            assert captured['current_equals_head'] and captured['head_equals_original']
            assert all(row['sha256'] == role['base_sha256'] for row in captured['whole_files'].values())
            if name in policy['role_build_unpinned_sources']:
                assert name not in built['pins'] and captured['historical_build_pin'] is None
            else:
                assert built['pins'][name] == role['base_sha256']
            assert traced[name]['base_sha256'] == role['base_sha256']
        if name in traced:
            assert traced[name]['candidate_sha256'] == role['candidate_sha256']
    assert policy['instrumentation']['environment'] == {'MOZ_DURATION_FIRST_READ_TRACE': '1'}
    comparison = load('progress_comparison_check', HERE / 'comparison.py')
    assert policy['wpt'] == comparison.expected_wpt(ROOT, policy)
    assert len(policy['wpt']['expected_subtests']) == 3 and sum(map(len, policy['wpt']['expected_subtests'].values())) == 9
    if policy['baseline_binding'] is None:
        assert not policy['execution_enabled'] and not policy['candidate_execution_enabled'] and policy['activation_pending']


def validate_actual_bindings(policy):
    validate_policy(policy)
    assert policy['baseline_binding'] is not None and policy['fresh_restoration_binding'] is not None
    assert policy['role_current_unpinned_sources'] is not None
    return load('progress_actual_original', HERE / 'comparison.py').replay_all(ROOT, policy)


def check(policy):
    validate_policy(policy)
    for name, digest in policy['references'].items():
        assert sha(ROOT / name) == digest, name
    source = read(ROOT / policy['baseline_capsule']['directory'] / 'POLICY.json')
    comparison = load('progress_static_comparison', HERE / 'comparison.py')
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
    for row in rows[1:6]:
        row.update(status='FAIL', expected='PASS', message='synthetic ordinary or animated failure')
    settings['target_subtests'] = {page: [row['subtest'] for row in rows if row['test'] == page and row['status'] == 'FAIL'] for page in settings['expected_subtests']}
    settings.update(expected_target_count=5, expected_control_count=4, expected_regression_signature_count=7)
    configuration = comparison.phase_policy(settings)
    saved = assessor.assess(original, 1, configuration, checks, run_binding=app)
    assert saved['complete'] and len(saved['regression_signature']) == 7
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
        return next(item for item in value if item.get('action') == 'test_status')

    reject('original PASS changed', lambda value: row(value).update(status='FAIL', expected='PASS', message='regression'), 1)
    reject('repair still FAIL', lambda value: [item for item in value if item.get('action') == 'test_status'][1].update(status='FAIL', expected='PASS', message='still stale'), 1)
    reject('PASS message changed', lambda value: row(value).update(message='new diagnostic'))
    reject('expected field presence changed', lambda value: row(value).update(expected='PASS'))
    reject('intermittent field presence changed', lambda value: row(value).update(known_intermittent=[]))
    reject('missing callback', lambda value: value.remove(row(value)))
    reject('duplicate callback', lambda value: value.insert(2, copy.deepcopy(row(value))))
    reject('ending changed', lambda value: next(item for item in value if item.get('action') == 'test_end').update(message='different'))
    reject('wrong build', lambda value: value[0]['run_info'].update(browser_build_id='wrong'))
    reject('crash', lambda value: value.append({'action': 'crash'}))
    reject('wrong exit', lambda value: None, 1)
    comparison.replay_all(ROOT, policy)
    comparison.replay_uninstrumented(ROOT, policy)
    check_failure_retention(policy)
    print(json.dumps({'synthetic_five_failure_projection_repaired': True, 'ordinary_or_animated_failure_names_treated_equally': True, 'negative_checks': rejected, 'references_authenticated': len(policy['references']), 'baseline_actual_binding_pending': policy['baseline_binding'] is None, 'browser_or_live_guard_executed': False}))


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
    comparison = SimpleNamespace(compare_uninstrumented=lambda *args: {'full_callback_and_ending_signatures_equal': False})
    trace = SimpleNamespace(header=lambda root, policy: {'synthetic': True}, capture=lambda *args: {'diagnostic_capture_complete': False})
    phases.load = lambda name, path: fake if path.name == 'wpt.py' else trace if path.name == 'trace_capture.py' else comparison if path.name == 'comparison.py' else collector
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
        assert len(receipt['missing']) == 9 and not receipt['errors'] and not receipt['complete']
        assert (output / 'candidate-wpt/raw.jsonl').read_text() == 'retained synthetic raw evidence'
    assert not output.exists()


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check(read(HERE / 'POLICY.json'))
