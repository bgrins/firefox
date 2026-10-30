import hashlib
import importlib.util
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, binding, stage):
    assert binding is not None
    assert binding['owner_directory'] == 'artifacts/css-hyphenation-ownership-native-pair-v1'
    assert binding['owner_manifest_sha256'] == '1a5490029693ea49aa591b0902f2d4a185d71a3954ee88edf0cc4b89d4d369d2'
    here = root / binding['owner_directory']
    baseline = load('nowrap_evidence_baseline', here / 'baseline.py')
    policy, ownership, roles = baseline.prepare(binding['owner_manifest_sha256'])
    admission = load('nowrap_evidence_admission', here / 'admission.py')
    output = admission.authenticate(root, {'directory': binding['runtime_directory'], 'manifest_sha256': binding['runtime_manifest_sha256']})
    assert binding['runtime_directory'] == policy['runtime_output'] == 'artifacts/css-hyphenation-ownership-native-pair-runtime-1'
    result = read(output / 'RESULT.json')
    terminal = read(output / 'ROOT-OWNER-TERMINAL.json')
    assert terminal['session'] == 27391 and terminal['launch'] == '71c531'
    assert terminal['terminal'] and terminal['exit'] == 0 and terminal['result_sha256'] == sha(output / 'RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
    assert result['error'] is None and result['publication_errors'] == []
    live = read(output / 'ROOT-LIVE-RESTORATION.json')
    live_terminal = read(output / 'ROOT-LIVE-AUDIT-TERMINAL.json')
    assert live_terminal['exit'] == 0 and live_terminal['terminal']
    assert live_terminal['audit_sha256'] == sha(output / 'ROOT-LIVE-RESTORATION.json')
    assert live['audit_script_sha256'] == sha(root / 'artifacts/css-hyphenation-ownership-native-live-audit-v1.py')
    assert live['owner_result_sha256'] == sha(output / 'RESULT.json')
    for field in ('independent_live_restoration_verified', 'application_and_extras_semantically_restored', 'source_and_binary_hashes_restored', 'flags_restored', 'controls_unchanged', 'backup_removed'):
        assert live[field] is True
    assert live['snapshot'] == read(output / 'POST.json') and not live['native_acceptance']
    cleanup = read(output / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    restoration = read(output / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert set(stage['head_preimages']) == set(roles) == {'dom/base/nsLineBreaker.cpp','dom/base/nsLineBreaker.h','layout/generic/nsTextFrame.cpp'}
    for name, record in roles.items():
        assert record['base_sha256'] == stage['head_preimages'][name]
        assert record['candidate_sha256'] == stage['files'][name]['sha256']
        assert restoration['sources'][name]['sha256'] == record['base_sha256']
    tests = set(stage['files']) - set(roles)
    expected_pages = ['/css/css-text/hyphens/hyphenate-limit-chars-inline-ownership.html', '/css/css-text/hyphens/hyphenate-limit-chars-dynamic.html', '/css/css-text/hyphens/hyphenate-limit-chars-pseudo-ownership.html']
    assert tests == {'testing/web-platform/tests' + page for page in expected_pages}
    assert set(stage['adopt_existing_tests']) == tests and stage['create_tests'] == []
    assert policy['ownership_target_pages'] == [expected_pages[0]]
    for test in tests:
        url = '/' + test.removeprefix('testing/web-platform/tests/')
        assert policy['wpt_lanes']['regression']['resources'][url]['sha256'] == stage['files'][test]['sha256']
    comparison = load('nowrap_evidence_comparison', here / 'comparison.py')
    assessor = load('nowrap_evidence_assessor', here / 'assess.py')
    checks = load('nowrap_evidence_streams', root / policy['wpt']['checks_helper'])
    builds = {role: comparison.build_binding(root, here, output, policy, role) for role in ('original', 'candidate')}
    ports = load('language_bound_port_comparison', here / 'port_comparison.py')
    comparisons, group_ids = {}, []
    corrected = None
    for role in ('original', 'candidate'):
        for filename in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
            group_ids.append(read(output / (role + '-build') / filename)['pgid'])
    original_outcomes = read(output / 'original-OUTCOMES.json')
    candidate_outcomes = read(output / 'candidate-OUTCOMES.json')
    for lane in policy['lane_order']:
        original = comparison.replay_original(root, here, output, policy, lane, assessor, checks)
        phase = output / ('candidate-wpt-' + lane)
        settings = policy['wpt_lanes'][lane]
        phase_result = read(phase / 'RESULT.json')
        assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
        for filename, key in [('raw.jsonl', 'raw_sha256'), ('ASSESSMENT.json', 'assessment_sha256'), ('RESULT.json', 'result_sha256')]:
            assert sha(phase / filename) == candidate_outcomes['lanes'][lane][key]
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == builds['candidate']['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == builds['candidate']['binaries']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json') == builds['candidate']['snapshot'] == read(output / 'candidate-PHASES-PRE.json') == read(output / 'candidate-PHASES-POST.json')
        staged = read(phase / 'STAGED-RESOURCES.json')
        assert all(sha(phase / name) == pin for name, pin in staged.items())
        for url, record in settings['resources'].items():
            assert sha(phase / 'tests' / url[1:]) == record['sha256']
        for kind, folder in [('portable', 'metadata'), ('mozilla', 'mozilla-metadata')]:
            assert sha(phase / folder / 'MANIFEST.json') == settings['manifests'][kind]['sha256']
            for name, record in settings['metadata'][kind].items():
                path = phase / folder / name
                if record['sha256'] is None:
                    assert not path.exists() and not path.is_symlink()
                else:
                    assert sha(path) == record['sha256']
        expected = comparison.phase_policy(settings, builds, policy['head'])
        assert expected == read(phase / 'ASSESSMENT-POLICY.json')
        events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
        actual = assessor.assess(events, phase_result['exit'], expected, checks, original=original, run_binding=builds['candidate']['application_metadata'])
        assert actual == read(phase / 'ASSESSMENT.json') and actual['complete']
        behavior = comparison.behavior(original, actual, assessor.signature)
        assert behavior == read(phase / 'BEHAVIOR-COMPARISON.json')
        if lane in ('target', 'context'):
            assert behavior['publication_observation_gate'] and actual['comparison_errors'] == []
            assert len(actual['rows']) == (169 if lane=='target' else 8)
            assert len(actual['ends']) == 1 and actual['ends'][0]['status'] == 'OK'
        else:
            assert len(actual['rows']) == 720 and len(actual['ends']) == 21
            corrected = ports.compare(root, output.resolve(), policy, original, actual, assessor.signature)
            assert corrected['derived_ownership_gate'] and corrected['target_callbacks']==289
            assert corrected['preserved_signatures']==452 and corrected['port_bound_reftest_endings']==4
        comparisons[lane] = behavior
        for role in ('original', 'candidate'):
            source = output / (role + '-wpt-' + lane)
            clean = read(source / 'CLEANUP.json')
            assert clean['owned_group_absent'] and clean['temporary_root_removed']
            group_ids.append(read(source / 'PROCESS.json')['pgid'])
    assert len(group_ids) == 10 and sorted(group_ids) == sorted(live['independently_absent_process_groups'])
    combined = read(output / 'COMPARISON.json')
    assert combined['lanes'] == comparisons and not combined['native_acceptance']
    assert combined['publication_observation_gate'] == all(row['publication_observation_gate'] for row in comparisons.values())
    assert combined['all920_signatures_equal'] == all(row['all_signatures_equal'] for row in comparisons.values())
    assert corrected is not None
    corrected['publication_observation_gate'] = corrected['derived_ownership_gate'] and comparisons['target']['publication_observation_gate'] and comparisons['context']['publication_observation_gate']
    corrected['native_acceptance'] = False
    assert corrected == read(output / 'DERIVED-COMPARISON.json') and corrected['publication_observation_gate']
    assert sum(len(row['candidate_signatures']) for row in comparisons.values()) == 920
    assert len(original_outcomes['rows']) == len(candidate_outcomes['rows']) == 897
    assert len(original_outcomes['endings']) == len(candidate_outcomes['endings']) == 23
    return {'pair_head': policy['head'], 'ownership_target_PASS': 289,
            'preserved_other_callbacks': 608, 'preserved_endings': 23,
            'regression_port_bound_endings': 4, 'derived_gate': True,
            'stored_raw_gate': combined['publication_observation_gate'], 'complete_signatures': 920,
            'root_live_restoration_verified': True, 'native_publication_performed': False}
