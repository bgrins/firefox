import importlib.util
import json
import os


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def historical(root, policy, h):
    pair = root / policy['paired_runtime']
    terminal = h.read(root / policy['pair_terminal']['path'])
    assert terminal == policy['pair_terminal']['record'] and terminal['exit'] == 0
    assert terminal['result_sha256'] == h.digest((pair / 'CANDIDATE-RESULT.json').read_bytes())
    result = h.read(pair / 'CANDIDATE-RESULT.json')
    assert result['success'] and result['error'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    restored = h.read(pair / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {}
    assert restored['sources'][policy['source']['path']]['sha256'] == policy['source']['base_sha256']
    cleanup = h.read(pair / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert not os.path.lexists(pair / 'backups')
    browser_dir = root / policy['paired_browser']
    browser = h.read(browser_dir / 'POLICY.json')
    assert tuple(browser['wpt'][key] for key in ('expected_subtest_count','expected_target_count','expected_control_count','expected_page_count','expected_regression_signature_count')) == (472,14,458,12,470)
    h.authenticate(root / browser['baseline_binding']['directory'], browser['baseline_binding']['manifest_sha256'])
    assessor = load('minmax_promotion_assessor', browser_dir / 'assess.py')
    comparison = load('minmax_promotion_comparison', browser_dir / 'comparison.py')
    checks = load('minmax_promotion_lifecycle', root / browser['wpt']['checks_helper'])
    original = comparison.replay_original(root, browser, assessor, checks)
    phase = pair / 'candidate-wpt'
    record = h.read(phase / 'RESULT.json')
    saved_policy = h.read(phase / 'ASSESSMENT-POLICY.json')
    assert saved_policy == comparison.phase_policy(browser['wpt'])
    replay = assessor.assess([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()],
        record['exit'], saved_policy, checks, original=original,
        run_binding=h.read(phase / 'APPLICATION-METADATA.json'))
    assert json.loads(json.dumps(replay)) == h.read(phase / 'ASSESSMENT.json')
    assert record['success'] and record['preservation_verified'] and record['execution_error'] is None and record['exit'] == 0
    assert replay['complete'] and replay['comparison_gate_passed'] and replay['comparison_errors'] == []
    assert replay['observed_subtest_count'] == 472 and len(replay['regression_signature']) == 470 and len(replay['ends']) == 12
    assert sum(row['status'] == 'PASS' for row in replay['rows']) == 470 and len(replay['unexpected']) == 0
    assert result['candidate_phase'] == {key:h.digest((phase / filename).read_bytes()) for key,filename in
        [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json')]}
    for role in ('original','candidate'):
        directory = pair / (role + '-wpt')
        assert h.read(directory / 'PRE.json') == h.read(directory / 'POST.json')
        assert h.read(directory / 'APPLICATION-METADATA.json') == h.read(directory / 'APPLICATION-METADATA-POST.json')
        cleanup = h.read(directory / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        h.group_absent(h.read(directory / 'PROCESS.json')['pgid'])
    for name in ('build-PROCESS.json','WAKE-PROCESS.json'):
        h.group_absent(h.read(pair / 'candidate-build' / name)['pgid'])
    inner = h.read(pair / 'candidate-build/build-RESULT.json')
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    build = h.read(pair / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    source = policy['source']
    assert build['native_sources'] == {source['path']:source['candidate_sha256']}
    tested = h.read(browser_dir / 'SOURCE-ROLES.json')[source['path']]
    assert tested['base_sha256'] == source['base_sha256'] and tested['candidate_sha256'] == source['candidate_sha256']
    assert (root / tested['candidate_capture']).read_bytes() == (root / source['candidate_capture']).read_bytes()
    for name,item in policy['tests'].items():
        relative = name.removeprefix('testing/web-platform/tests/')
        body = (root / item['capture']).read_bytes()
        assert h.digest(body) == item['sha256']
        assert body == (pair / 'original-wpt/tests' / relative).read_bytes() == (phase / 'tests' / relative).read_bytes()
    return {'pair_result_sha256':terminal['result_sha256'], 'comparison_gate_passed':True,
            'tested_source_sha256':source['candidate_sha256'], 'historical_harness_head':browser['head'],
            'source_and_fixtures_exact_tested_bytes':True, 'accepted':False}


def verify(root, policy, epoch, h):
    evidence = historical(root, policy, h)
    checkpoint = policy['reference_checkpoint']
    receipt = h.read(root / checkpoint['final_check'])
    assert h.digest((root / checkpoint['final_check']).read_bytes()) == checkpoint['final_check_sha256']
    assert checkpoint['signature_field'] in ('signature_verified','signature_chain_verified')
    assert receipt[checkpoint['signature_field']] is True and receipt['runtime_epoch_synchronized'] is True
    assert receipt['head'] == checkpoint['signed_head'] == policy['head'] == epoch['semantic_index']['head']
    s = h.load_state(root / 'artifacts/css-registered-number-native-runtime-v1')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    changed = s.h.git(root, env, 'diff', '--no-renames', '--name-only', evidence['historical_harness_head'], policy['head']).decode().splitlines()
    assert all(name.startswith('artifacts/') for name in changed)
    binding = policy['current_restoration']
    directory = root / binding['runtime']
    terminal = h.read(directory / binding['terminal_path'])
    assert terminal == binding['terminal'] and terminal['exit'] in (0, 1)
    assert binding['terminal_result_field'] in ('result_sha256','candidate_result_sha256')
    assert terminal[binding['terminal_result_field']] == binding['result_sha256']
    result = h.read(directory / binding['result_path'])
    assert h.digest((directory / binding['result_path']).read_bytes()) == binding['result_sha256']
    assert result['success'] == (terminal['exit'] == 0)
    assert result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['publication_errors'] == [] and result['empty_staging_preserved']
    assert (result['error'] is None) == result['success']
    restored = h.read(directory / 'RESTORATION.json')
    assert restored['errors'] == [] and restored['owned_processes'] == {} and restored['sources'] == binding['sources']
    cleanup = h.read(directory / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    assert not os.path.lexists(directory / 'backups')
    for name,item in binding['sources'].items():
        h.claim(root, name, item['sha256'], item['identity'])
        assert h.digest(s.h.git(root, env, 'show', policy['head'] + ':' + name)) == item['sha256']
    metadata = load('minmax_original_metadata', root / policy['metadata_helper'])
    previous = h.read(root / policy['original_build']['application_metadata'])
    app = metadata.application_metadata(root / policy['application_ini'], previous['revision'])
    assert app == policy['prepared_application_metadata']
    assert app['sha256'] == previous['sha256'] and app['browser_build_id'] == previous['browser_build_id']
    built = h.read(root / policy['original_build']['epoch'])
    build_result = h.read(root / policy['original_build']['result'])
    inner = h.read(root / policy['original_build']['inner_result'])
    assert build_result['command_success'] and build_result['preservation_verified'] and build_result['error'] is None
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == []
    assert inner['error'] is None and inner['stop_reason'] is None
    assert built['semantic_index']['head'] == previous['revision']
    assert built['pow_special_value_transition']['compiled'] and not built['pow_special_value_transition']['accepted']
    assert built['pow_special_value_transition']['source_sha256'] == policy['source']['base_sha256']
    for name in policy['rebuilt_binaries']:
        assert h.digest((root / name).read_bytes()) == epoch['pins'][name] == built['pins'][name]
    assert built['pins'][policy['source']['path']] == policy['source']['base_sha256']
    evidence.update(reference_checkpoint=checkpoint, current_restoration_result_sha256=binding['result_sha256'],
                    intervening_experiment_success=result['success'],
                    restored_application_metadata=app, installed_candidate_compiled=False)
    return evidence
