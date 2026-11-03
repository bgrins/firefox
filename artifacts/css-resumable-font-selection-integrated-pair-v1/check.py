import copy
import hashlib
import importlib.util
import json
import runpy
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
    assert policy['runtime_output'] == 'artifacts/css-resumable-font-selection-integrated-pair-runtime-1'
    assert policy['head'] == 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
    assert type(policy['execution_enabled']) is bool and policy['execution_enabled'] == policy['candidate_execution_enabled']
    admission = load('admission')
    source = admission.authenticate(ROOT, policy['source_binding'])
    assert source == ROOT / 'artifacts/css-resumable-font-selection-integrated-v2'
    native = ROOT / 'artifacts/css-resumable-font-size-integrated-native-typecheck-v1'
    old = read(native / 'POLICY.json')
    for name in ('head','image_commit','nowrap_commit','language_commit','ownership_commit','capacity_commit','authority_kind','additional_source_paths','ownership_helper','phase_helper','process_helper','state_helper','bundle_helper','bundle_path','extra_backup_paths','rebuilt_binaries','source_context_pins','restored_application_revision','timeout_seconds','metadata_current_pins','preserved_absent_metadata','preserved_absent_resources','required_typecheck_inputs','typecheck_binding','predecessor_binding','capture_source_owner','resource_policy'):
        assert policy[name] == old[name], name
    roles = read(HERE / 'SOURCE-ROLES.json')
    bindings = read(source / 'SOURCE-ROLES.json')
    assert len(roles) == 3 and set(roles) == set(bindings)
    for role, record in roles.items():
        expected = {}
        for kind in ('base','candidate'):
            expected[kind + '_capture'] = bindings[role][kind]['path']
            expected[kind + '_sha256'] = bindings[role][kind]['sha256']
            assert sha(ROOT / expected[kind + '_capture']) == expected[kind + '_sha256']
        assert record == expected
    assert policy['committed_source_preimages'] == {name: row['base_sha256'] for name,row in roles.items()}
    assert admission.authenticate(ROOT, policy['native_owner_binding']) == native
    compiled_roles = read(native / 'SOURCE-ROLES.json')
    source_roles, comments = read(source / 'SOURCE-ROLES.json'), read(source / 'COMMENTS.json')
    for role, record in compiled_roles.items():
        assert source_roles[role]['parent']['sha256'] == record['candidate_sha256']
        before = (ROOT / record['candidate_capture']).read_text()
        after = (ROOT / roles[role]['candidate_capture']).read_text()
        if role.endswith('custom_properties.rs'):
            for comment in comments.values():
                line = '        /// ' + comment + '\n'
                assert after.count(line) == 1
                after = after.replace(line, '')
        assert after == before
    binding = policy['compile_prerequisite']
    assert binding['directory'] == 'artifacts/css-resumable-font-size-integrated-native-typecheck-runtime-1'
    assert binding['source_bridge'] == 'four-doc-comments-only'
    runtime = admission.authenticate(ROOT, binding)
    result, command = read(runtime / 'RESULT.json'), read(runtime / 'candidate-check/COMMAND.json')
    assert result['success'] and result['restoration_verified'] and not result['native_fix_acceptance']
    assert result['phase']['cargo']['success'] and result['phase']['cargo']['errors'] == []
    assert command['owner_manifest'] == sha(native / 'FILES.json') and command['source_role'] == 'candidate'
    assert command['command'] == read(native / 'TYPECHECK.json')['command']
    assert command['source_sha256'] == {name: row['candidate_sha256'] for name,row in compiled_roles.items()}
    for key in ('live_audit','audit_terminal'):
        assert sha(ROOT / binding[key]['path']) == binding[key]['sha256']
    live, terminal = read(ROOT / binding['live_audit']['path']), read(ROOT / binding['audit_terminal']['path'])
    assert live['independent_live_restoration_verified'] and live['owner_result_sha256'] == sha(runtime / 'RESULT.json')
    assert all(live[key] is True for key in ('application_and_extras_semantically_restored','source_and_binary_hashes_restored','flags_restored','controls_unchanged','backup_removed'))
    assert len(live['independently_absent_process_groups']) == 2 and not live['native_acceptance']
    assert terminal['exit'] == 0 and terminal['audit_sha256'] == binding['live_audit']['sha256']
    assert all(policy['references'][path] == pin for path,pin in old['references'].items())
    assert policy['lane_order'] == ['metric','phase','typedattr']
    assert policy['diagnostic_lane_order'] == ['sizeforms','minimum_off','minimum_on','inputs']
    lanes = policy['lane_order'] + policy['diagnostic_lane_order']
    assert set(policy['wpt_lanes']) == set(policy['suite_bindings']) == set(lanes)
    previous = read(ROOT / 'artifacts/css-font-metric-computed-size-pair-v1/POLICY.json')
    for lane in ('metric','phase','typedattr','sizeforms'):
        assert policy['suite_bindings'][lane] == previous['suite_bindings'][lane]
        admission.authenticate(ROOT, policy['suite_bindings'][lane])
        expected = copy.deepcopy(previous['wpt_lanes'][lane])
        expected.update(harness_revision=policy['head'], phase_revisions={'original':policy['head'],'candidate':policy['head']})
        assert policy['wpt_lanes'][lane] == expected
    for mode in ('off','on'):
        lane = 'minimum_' + mode
        suite = admission.authenticate(ROOT, policy['suite_bindings'][lane])
        assert suite == ROOT / 'artifacts/css-minimum-font-size-preservation-stage-v1'
        inputs, roster = read(suite / 'INPUTS.json'), read(suite / 'ROSTER.json')
        page = inputs['prefs'][mode]['url']
        expected = copy.deepcopy(policy['wpt_lanes']['sizeforms'])
        expected.update(resources=inputs['resources'],expected_subtests={page:roster[page]},target_subtests={page:roster[page]},fixture_target_pages=[page],candidate_required_pass_pages=[page],expected_subtest_count=7,expected_target_count=7,expected_page_count=1,expected_regression_signature_count=1)
        expected['manifests']['portable'] = inputs['manifest']
        expected['metadata'] = {'portable':inputs['metadata'],'mozilla':{}}
        assert policy['wpt_lanes'][lane] == expected
    suite = admission.authenticate(ROOT, policy['suite_bindings']['inputs'])
    assert suite == ROOT / 'artifacts/css-font-input-dependency-wpt-v1'
    inputs, roster = read(suite / 'INPUTS.json'), read(suite / 'ROSTER.json')
    assert inputs['prefs'] == inputs['metadata'] == {}
    assert inputs['observations'] == 48 and inputs['callbacks'] == 24
    expected = copy.deepcopy(policy['wpt_lanes']['sizeforms'])
    expected.update(resources=inputs['resources'],expected_subtests=roster,target_subtests=roster,fixture_target_pages=list(roster),candidate_required_pass_pages=list(roster),expected_subtest_count=24,expected_target_count=24,expected_page_count=1,expected_regression_signature_count=1)
    expected['manifests']['portable'] = inputs['manifest']
    expected['metadata'] = {'portable':{},'mozilla':{}}
    assert policy['wpt_lanes']['inputs'] == expected
    assert policy['wpt'] == policy['wpt_lanes']['metric']
    assert sum(policy['wpt_lanes'][k]['expected_subtest_count'] for k in policy['lane_order']) == 21
    assert sum(policy['wpt_lanes'][k]['expected_subtest_count'] for k in lanes) == 63
    assert sum(policy['wpt_lanes'][k]['expected_page_count'] for k in lanes) == 7
    origins = read(HERE / 'ORIGINS.json')
    for name in ('baseline.py','inputs.py','intermediate.py','review_scope.py','phases.py','wpt.py','assess.py','comparison.py','check_identity.py'):
        assert (HERE / name).read_bytes() == (ROOT / origins[name]).read_bytes(), name
    expected_driver = (ROOT / origins['run.py']).read_text().replace('computed-size-pair21-v1','resumable-font-selection-pair39-v1')
    expected_driver = expected_driver.replace("        claims[name] = ownership.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'].get(name))", "        admitted = (baseline.current_capture(policy)['payload_claims'] | baseline.current_capture(policy)['additional_sources'])[name]\n        claims[name] = ownership.claim(ROOT, name, record['base_sha256'], admitted['identity'])\n        assert claims[name] == admitted")
    assert (HERE / 'run.py').read_text() == expected_driver
    expected_closure = (ROOT / origins['closure.py']).read_text().replace("for name, record in json.loads(path.read_bytes()).items():", "inventory = json.loads(path.read_bytes())\n        for name, record in inventory.get('files', inventory).items():")
    expected_closure = expected_closure.replace("add(str((path.parent / name).relative_to(root)), record['sha256'])", "add(str((path.parent / name).relative_to(root)), record if isinstance(record, str) else record['sha256'])")
    assert (HERE / 'closure.py').read_text() == expected_closure
    expected_admission = (ROOT / origins['admission.py']).read_text().replace("        assert sha(directory/name)==row['sha256'] and (directory/name).stat().st_size==row['bytes']", "        if isinstance(row, str):\n            assert len(row) == 64 and sha(directory/name) == row\n        else:\n            assert sha(directory/name)==row['sha256'] and (directory/name).stat().st_size==row['bytes']")
    assert (HERE / 'admission.py').read_text() == expected_admission
    for path,pin in policy['references'].items():
        assert sha(ROOT / path) == pin, path
    external = load('closure').external_inputs(ROOT,policy,roles)
    assert external == policy['intermediate_consumed_inputs']
    for path,pin in external.items():
        if path.startswith('artifacts/'):
            assert pin is not None and sha(ROOT / path) == pin, path
    if policy['current_binding'] is None:
        assert not policy['execution_enabled'] and policy['activation_pending']
        assert policy['controls'] is None and policy['accepted_current_payloads'] == {}
        assert policy['capture_owner'] is None and policy['refresh_lineage'] is None
    else:
        assert policy['activation_pending'] == []
        assert policy['capture_owner']['directory'] == 'artifacts/css-resumable-font-selection-integrated-pair-current-capture-v1'
        assert policy['current_binding']['path'] == 'artifacts/css-resumable-font-selection-integrated-pair-current-v1.json'
        capture = admission.validate_current(ROOT, policy, roles)
        assert capture['checkpoint_receipt']['sha256'] == '085fcdc6576fea84ef9e43fbc0d0c7f1111d9e7899d8d42f6040442e49d91d16'
        assert capture['controls']['CURRENT-EPOCH.json'] == '1861557ebb6ef3b3b55f38f0b068f0b6db4fc776ff78187958c16d35a6717ecb'
        assert policy['refresh_lineage'] == {'directory':'artifacts/css-resumable-font-size-integrated-raw-index-refresh-runtime-1','result_sha256':'d663a96d5333d2cd56852a7c414db0b146ce57127c9e0fde9e25557b4287c596'}
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
    return len(policy['lane_order'] + policy['diagnostic_lane_order'])


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
            _, _, metadata = synthetic(policy, 'metric', 'PASS', role)
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
        path = output / 'original-wpt-metric/APPLICATION-METADATA.json'; saved = read(path)
        bad = copy.deepcopy(saved); bad['source_role'] = 'candidate'; write(path, bad)
        rejected(lambda: comparison.replay_original(ROOT, here, output, local, 'metric', assessor, checks))
        write(path, saved)
        path = output / 'original-wpt-metric/raw.jsonl'; saved = path.read_bytes(); path.write_bytes(saved.replace(b'ordinary assertion failure', b'altered assertion', 1))
        rejected(lambda: comparison.replay_original(ROOT, here, output, local, 'metric', assessor, checks))
    finally:
        shutil.rmtree(directory)
    assert not directory.exists()
    return {'original_lanes_replayed': len(policy['lane_order'] + policy['diagnostic_lane_order']), 'build_positives': 2, 'build_and_replay_negatives': 6, 'scratch_removed': True}


if __name__ == '__main__':
    policy = read(HERE / 'POLICY.json')
    count = validate_policy(policy)
    runpy.run_path(str(HERE / 'check_identity.py'), run_name='__main__')
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    mutations = [('head', '0' * 40), ('committed_source_preimages', {}), ('intermediate_consumed_inputs', {}), ('suite_bindings', None)]
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
