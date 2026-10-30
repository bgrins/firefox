import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path=None):
    spec = importlib.util.spec_from_file_location('pair_check_' + name, path or HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_policy(policy):
    assert policy['owner_directory'] == str(HERE.relative_to(ROOT))
    assert policy['runtime_output'] == 'artifacts/css-appearance-typed-attr-pair-runtime-1'
    assert policy['head'] == '272e8b2ddc4f6824c5d22e5395f275dc00ee34a6'
    admission = load('admission')
    suite = admission.authenticate(ROOT, policy['suite_binding'])
    assert policy['suite_binding']['manifest_sha256'] == '940fdda04d54d73778a608cb32dfa6274922ae9d93ac9ed3de3fabd5b9bfb759'
    data, roster = (read(suite / name) for name in ('INPUTS.json', 'ROSTER.json'))
    assert (data['callbacks'], data['pages'], data['signatures'], len(data['resources'])) == (4, 1, 5, 3)
    assert policy['lane_order'] == ['ordinary'] and policy['diagnostic_lane_order'] == []
    assert set(policy['wpt_lanes']) == {'ordinary'}
    prior = read(ROOT / 'artifacts/css-prioritary-publication-pair-v2/POLICY.json')
    for key in ('image_commit', 'ownership_helper', 'phase_helper', 'process_helper', 'state_helper', 'bundle_helper', 'bundle_path', 'extra_backup_paths', 'rebuilt_binaries', 'metadata_current_pins', 'preserved_absent_metadata', 'source_context_pins', 'restored_application_revision', 'timeout_seconds'):
        assert policy[key] == prior[key], key
    assert policy['preserved_absent_resources'] == sorted(set(prior['preserved_absent_resources']) | {'testing/web-platform/meta/css/css-ui/appearance-typed-attr-scheduling.tentative.html.ini'})
    changing = {'expected_subtests', 'target_subtests', 'expected_subtest_count', 'expected_target_count', 'expected_control_count', 'expected_page_count', 'expected_regression_signature_count', 'fixture_target_pages', 'candidate_required_pass_pages', 'phase_revisions', 'harness_revision', 'resources', 'manifests', 'metadata', 'capture', 'install_managed_resources'}
    settings = policy['wpt']
    assert settings == policy['wpt_lanes']['ordinary']
    assert {k: v for k, v in settings.items() if k not in changing} == {k: v for k, v in prior['wpt'].items() if k not in changing}
    assert settings['expected_subtests'] == settings['target_subtests'] == roster
    assert (settings['expected_subtest_count'], settings['expected_target_count'], settings['expected_control_count'], settings['expected_page_count'], settings['expected_regression_signature_count']) == (4, 4, 0, 1, 1)
    assert settings['fixture_target_pages'] == settings['candidate_required_pass_pages'] == sorted(roster)
    assert settings['phase_revisions'] == {'original': policy['head'], 'candidate': policy['head']}
    assert settings['harness_revision'] == policy['head']
    assert settings['resources'] == data['resources']
    assert settings['manifests']['portable'] == data['manifest']
    assert settings['manifests']['mozilla'] == prior['wpt']['manifests']['mozilla']
    assert settings['metadata'] == {'portable': {}, 'mozilla': {}}
    assert settings['capture'] is None and settings['install_managed_resources'] == {}
    assert all(not page.startswith('/_mozilla/') for page in roster)
    assert not data['prefs'] and not data['metadata']

    old_run = (ROOT / 'artifacts/css-prioritary-published-candidate-v1/candidate.py').read_text()
    new_run = (HERE / 'run.py').read_text()
    start, end = '    finally:\n        if owned:', '    success = failure is None'
    assert old_run[old_run.index(start):old_run.index(end)] == new_run[new_run.index(start):new_run.index(end)]
    old_wpt = (ROOT / 'artifacts/css-prioritary-published-candidate-v1/wpt.py').read_text()
    new_wpt = (HERE / 'wpt.py').read_text()
    start, end = '    process, code, error, cleanup =', '    after = verify()'
    assert old_wpt[old_wpt.index(start):old_wpt.index(end)] == new_wpt[new_wpt.index(start):new_wpt.index(end)]
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert roles == read(ROOT / 'artifacts/css-prioritary-published-candidate-v1/SOURCE-ROLES.json')
    assert policy['committed_source_preimages'] == {name: row['base_sha256'] for name, row in roles.items()}
    assert [name for name, row in roles.items() if row['base_sha256'] != row['candidate_sha256']] == ['servo/components/style/properties/cascade.rs']
    for row in roles.values():
        for kind in ('base', 'candidate'):
            assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
    admission.validate_prerequisite(ROOT, policy, roles)
    evidence = policy['prior_pair_evidence']
    for kind in ('runtime', 'audit'):
        directory = ROOT / evidence[kind + '_directory']
        assert sha(directory / 'FILES.json') == evidence[kind + '_manifest_sha256']
    audit = read(ROOT / evidence['audit_directory'] / 'AUDIT.json')
    assert audit == read(ROOT / evidence['runtime_directory'] / 'ROOT-REVIEW.json')
    assert audit['publication28_gate'] and not audit['diagnostic5_gate'] and not audit['combined_gate']
    assert not audit['native_acceptance']
    assert (HERE / 'assess.py').read_bytes() == (ROOT / policy['assessor_binding']['directory'] / 'assess.py').read_bytes()
    for name in ('inputs.py', 'review_scope.py'):
        assert (HERE / name).read_bytes() == (ROOT / policy['capture_owner']['directory'] / name).read_bytes()
    assert (HERE / 'intermediate.py').read_bytes() == (ROOT / policy['diagnostic_binding']['directory'] / 'intermediate.py').read_bytes()
    external = load('closure').external_inputs(ROOT, policy, roles)
    for name, pin in external.items():
        if name.startswith('artifacts/'):
            assert pin is not None and sha(ROOT / name) == pin, name
    assert policy['intermediate_consumed_inputs'] == external
    if policy['current_binding'] is None:
        assert policy['controls'] is None and policy['accepted_current_payloads'] == {}
        assert not policy['execution_enabled'] and not policy['candidate_execution_enabled'] and policy['activation_pending']
    else:
        capture = admission.validate_current(ROOT, policy, roles)
        assert capture['checkpoint_receipt']['sha256'] == '48cd5f34e7c62dc429dae364188789ad08c8aa0f5fdbd1c959cd10b583661c82'
    return len(external)


def rejected(action):
    try:
        action()
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError('negative control unexpectedly admitted')


def synthetic(policy, lane, status, role):
    metadata = {'browser_build_id': 'synthetic-' + role, 'revision': policy['head'], 'build_revision': policy['head'], 'harness_revision': policy['head'], 'source_role': role, 'sha256': ('a' if role == 'original' else 'b') * 64, 'path': 'synthetic/application.ini', 'resolved': 'synthetic/application.ini'}
    events = [{'action': 'suite_start', 'run_info': {'os': 'mac', 'debug': False, 'browser_build_id': metadata['browser_build_id'], 'revision': policy['head']}}]
    for page, names in policy['wpt_lanes'][lane]['expected_subtests'].items():
        events.append({'action': 'test_start', 'test': page})
        for name in names:
            row = {'action': 'test_status', 'test': page, 'subtest': name, 'status': status}
            if status == 'FAIL':
                row.update(expected='PASS', message='ordinary assertion failure')
            events.append(row)
        events.append({'action': 'test_end', 'test': page, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    return events, int(status == 'FAIL'), metadata


def stream_checks(policy):
    assessor, comparison = load('assess'), load('comparison')
    checks = load('stream_helpers', ROOT / policy['wpt']['checks_helper'])
    cases = []
    for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
        original_events, code, original_metadata = synthetic(policy, lane, 'FAIL', 'original')
        candidate_events, _, candidate_metadata = synthetic(policy, lane, 'PASS', 'candidate')
        builds = {role: {'application_metadata': meta} for role, meta in [('original', original_metadata), ('candidate', candidate_metadata)]}
        settings = comparison.phase_policy(policy['wpt_lanes'][lane], builds, policy['head'])
        original = assessor.assess(original_events, code, settings, checks, run_binding=original_metadata)
        assert original['complete'] and all(row['status'] == 'FAIL' for row in original['rows'])
        candidate = assessor.assess(candidate_events, 0, settings, checks, original=original, run_binding=candidate_metadata)
        behavior = comparison.behavior(original, candidate, assessor.signature)
        assert candidate['complete'] and behavior['publication_observation_gate'] and behavior['differences']
        assert json.loads(json.dumps(behavior)) == behavior
        failed_events, failed_code, _ = synthetic(policy, lane, 'FAIL', 'candidate')
        failed = assessor.assess(failed_events, failed_code, settings, checks, original=original, run_binding=candidate_metadata)
        assert failed['complete'] and not comparison.behavior(original, failed, assessor.signature)['publication_observation_gate']
        for mutation in ('metadata', 'role', 'revision', 'platform', 'setup', 'missing-ending'):
            events, binding = copy.deepcopy(candidate_events), copy.deepcopy(candidate_metadata)
            if mutation == 'metadata': binding['sha256'] = 'c' * 64
            elif mutation == 'role': binding['source_role'] = 'original'
            elif mutation == 'revision': events[0]['run_info']['revision'] = '0' * 40
            elif mutation == 'platform': events[0]['run_info']['debug'] = True
            elif mutation == 'setup': events[2].update(status='FAIL', expected='PASS', message='ReferenceError: setup')
            else: events = [row for row in events if not (row.get('action') == 'test_end' and row['test'] == next(iter(settings['expected_subtests'])))]
            actual = assessor.assess(events, int(mutation == 'setup'), settings, checks, original=original, run_binding=binding)
            assert not comparison.behavior(original, actual, assessor.signature)['publication_observation_gate'], mutation
        passing_events, _, _ = synthetic(policy, lane, 'PASS', 'original')
        passing = assessor.assess(passing_events, 0, settings, checks, run_binding=original_metadata)
        changed = copy.deepcopy(candidate_events); changed[2]['message'] = 'changed full signature'
        actual = assessor.assess(changed, 0, settings, checks, original=passing, run_binding=candidate_metadata)
        assert actual['complete'] and not comparison.behavior(passing, actual, assessor.signature)['publication_observation_gate']
        cases.append({'lane': lane, 'ordinary_FAIL_retained': len(original['rows']), 'candidate_PASS': len(candidate['rows']), 'endings': len(candidate['ends']), 'negative_cases': 7})
    return cases


def stage_checks(policy):
    wpt = load('wpt')
    directory = Path(tempfile.mkdtemp(prefix='css-publication-pair-saved-', dir=ROOT / 'artifacts'))
    try:
        for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
            output = directory / lane; output.mkdir()
            settings = policy['wpt_lanes'][lane]
            config, capture = wpt.prepare_inputs(ROOT, output, settings, 'original')
            assert capture is None and config.is_file()
            for kind, folder in [('portable', 'metadata'), ('mozilla', 'mozilla-metadata')]:
                for relative, row in settings['metadata'][kind].items():
                    target = output / folder / relative
                    assert (not target.exists()) if row['sha256'] is None else sha(target) == row['sha256']
    finally:
        shutil.rmtree(directory)
    assert not directory.exists()
    return 1


def replay_checks(policy):
    directory = Path(tempfile.mkdtemp(prefix='css-pair-replay-saved-', dir=ROOT / 'artifacts'))
    write = lambda path, value: path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    comparison, wpt, assessor = load('comparison'), load('wpt'), load('assess')
    checks = load('replay_stream_helpers', ROOT / policy['wpt']['checks_helper'])
    try:
        here, output = directory / 'owner', directory / 'runtime'
        here.mkdir(); output.mkdir()
        local = copy.deepcopy(policy); local['owner_directory'] = str(here.relative_to(ROOT))
        for name in ('SOURCE-ROLES.json', 'closure.py', 'inputs.py', 'review_scope.py'):
            shutil.copyfile(HERE / name, here / name)
        manifest = {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in here.iterdir()}
        write(here / 'FILES.json', manifest)
        external = load('closure').external_inputs(ROOT, local, read(here / 'SOURCE-ROLES.json'))
        assert external == local['intermediate_consumed_inputs']
        effective = load('inputs').bind_inputs(local['owner_directory'], (here / 'FILES.json').read_bytes(), sha(here / 'FILES.json'), external)
        capture = read(ROOT / policy['current_binding']['path'])
        snapshot = {'index': capture['snapshot']['index'], 'nested_index': capture['snapshot']['nested_index'], 'current_raw_stable_during_check': True, 'working_sources_binaries_preserved': True, 'archival_research_not_rechecked': True, 'verification_scope': 'intermediate-consumed-inputs-v1', 'consumed_inputs_sha256': hashlib.sha256(json.dumps(effective, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        builds = {}
        for role in ('original', 'candidate'):
            folder = output / (role + '-build'); folder.mkdir()
            _, _, metadata = synthetic(policy, 'ordinary', 'PASS', role)
            sources = {name: row['base_sha256' if role == 'original' else 'candidate_sha256'] for name, row in read(HERE / 'SOURCE-ROLES.json').items()}
            write(folder / 'COMMAND.json', {'command': ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2'], 'owner_manifest': sha(here / 'FILES.json'), 'source_role': role, 'source_sha256': sources})
            write(folder / 'build-RESULT.json', {'exit': 0, 'owned_group_absent': True, 'cleanup_errors': [], 'error': None, 'stop_reason': None})
            build = {'command_success': True, 'preservation_verified': True, 'browser_build_performed': True, 'error': None, 'native_sources': sources, 'binaries': {name: 'd' * 64 for name in policy['rebuilt_binaries']}, 'application_metadata': metadata, 'snapshot': snapshot}
            write(folder / 'RESULT.json', build)
            assert comparison.build_binding(ROOT, here, output, local, role) == build
            builds[role] = build
        outcomes = {}
        for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
            phase = output / ('original-wpt-' + lane); phase.mkdir()
            wpt.prepare_inputs(ROOT, phase, policy['wpt_lanes'][lane], 'original')
            events, code, metadata = synthetic(policy, lane, 'FAIL', 'original')
            settings = comparison.phase_policy(policy['wpt_lanes'][lane], {'original': builds['original']}, policy['head'])
            assessment = assessor.assess(events, code, settings, checks, run_binding=metadata)
            assert assessment['complete']
            for name, value in {'PRE.json': snapshot, 'POST.json': snapshot, 'APPLICATION-METADATA.json': metadata, 'APPLICATION-METADATA-POST.json': metadata, 'BINARY-PINS.json': builds['original']['binaries'], 'CLEANUP.json': {'owned_group_absent': True, 'temporary_root_removed': True}, 'ASSESSMENT-POLICY.json': settings, 'ASSESSMENT.json': assessment, 'RESULT.json': {'success': True, 'preservation_verified': True, 'execution_error': None, 'exit': code}}.items(): write(phase / name, value)
            (phase / 'raw.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in events))
            outcomes[lane] = {key: sha(phase / name) for name, key in [('ASSESSMENT.json', 'assessment_sha256'), ('raw.jsonl', 'raw_sha256'), ('RESULT.json', 'result_sha256')]}
        write(output / 'original-OUTCOMES.json', {'lanes': {k: v for k, v in outcomes.items() if k in policy['lane_order']}, 'diagnostics': {k: v for k, v in outcomes.items() if k in policy['diagnostic_lane_order']}})
        for name in ('original-PHASES-PRE.json', 'original-PHASES-POST.json'): write(output / name, snapshot)
        for lane in policy['lane_order'] + policy['diagnostic_lane_order']:
            actual = comparison.replay_original(ROOT, here, output, local, lane, assessor, checks)
            assert actual['complete'] and all(row['status'] == 'FAIL' for row in actual['rows'])
        path = output / 'original-build/COMMAND.json'; saved = read(path)
        for key, value in [('source_role', 'candidate'), ('source_sha256', {}), ('owner_manifest', '0' * 64), ('command', [])]:
            bad = copy.deepcopy(saved); bad[key] = value; write(path, bad)
            rejected(lambda: comparison.build_binding(ROOT, here, output, local, 'original'))
        write(path, saved)
        path = output / 'original-wpt-ordinary/APPLICATION-METADATA.json'; saved = read(path)
        bad = copy.deepcopy(saved); bad['source_role'] = 'candidate'; write(path, bad)
        rejected(lambda: comparison.replay_original(ROOT, here, output, local, 'ordinary', assessor, checks))
        write(path, saved)
        path = output / 'original-wpt-ordinary/raw.jsonl'; saved = path.read_bytes(); path.write_bytes(saved.replace(b'ordinary assertion failure', b'altered assertion', 1))
        rejected(lambda: comparison.replay_original(ROOT, here, output, local, 'ordinary', assessor, checks))
    finally:
        shutil.rmtree(directory)
    assert not directory.exists()
    return {'original_lanes_replayed': 1, 'build_positives': 2, 'build_and_replay_negatives': 6, 'scratch_removed': True}


if __name__ == '__main__':
    policy = read(HERE / 'POLICY.json')
    count = validate_policy(policy)
    mutations = [('head', '0' * 40), ('committed_source_preimages', {}), ('intermediate_consumed_inputs', {}), ('suite_binding', None)]
    if policy['current_binding'] is None:
        mutations.append(('execution_enabled', True))
    else:
        mutations.extend([('controls', {}), ('accepted_current_payloads', {})])
    for key, value in mutations:
        changed = copy.deepcopy(policy); changed[key] = value
        rejected(lambda: validate_policy(changed))
    streams = stream_checks(policy)
    stages = stage_checks(policy)
    replay = replay_checks(policy) if policy['current_binding'] is not None else None
    run = load('run')
    assert run.expected_modified_paths(['unrelated'], {'same': {'candidate_sha256': 'a'}, 'changed': {'candidate_sha256': 'b'}}, {'same': 'a', 'changed': 'a'}) == ['changed', 'unrelated']
    print(json.dumps({'consumed_inputs': count, 'binding_negatives': len(mutations), 'streams': streams, 'staged_lanes': stages, 'local_original_replay': replay, 'scratch_removed': True, 'native_or_browser_run': False, 'live_guard': False}, sort_keys=True))
