import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).resolve().parent
CONFIG = json.loads((REVIEW / 'POLICY.json').read_text())
HERE = ROOT / CONFIG['owner_directory']
PAIR = ROOT / CONFIG['runtime_directory']
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
REFRESH = ROOT / CONFIG['refresh_path']
OWNER_SHA = CONFIG['owner_manifest_sha256']
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def outcome_join(result, phase, assessment, terminal_exit, phase_hashes):
    assert assessment['complete'] and assessment['errors'] == []
    assert len(assessment['rows']) == 2 and all(r['status'] in ('PASS', 'FAIL') for r in assessment['rows'])
    assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
    assert phase['execution_error'] is None and phase['preservation_verified']
    assert phase['native_fix_acceptance'] is False
    passed = assessment['comparison_gate_passed']
    assert phase['comparison_gate_passed'] == phase['success'] == result['success'] == passed
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['publication_errors'] == [] and not result['native_fix_acceptance']
    if passed:
        assert terminal_exit == phase['exit'] == 0
        assert all(r['status'] == 'PASS' for r in assessment['rows']) and assessment['comparison_errors'] == []
        assert result['error'] is None and result['candidate_phase'] == phase_hashes
    else:
        assert terminal_exit == phase['exit'] == 1
        assert any(r['status'] == 'FAIL' for r in assessment['rows']) and assessment['comparison_errors']
        assert result['candidate_phase'] is None
        assert result['error'] == repr(AssertionError((None, True, assessment['errors'], assessment['comparison_errors'])))
    return passed


def main():
    assert CONFIG['execution_enabled'] and OWNER_SHA is not None, 'Root review/actual owner binding required'
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=int, required=True)
    parser.add_argument('--terminal', required=True)
    parser.add_argument('--exit', type=int, required=True, dest='exit_code')
    parser.add_argument('--result-sha256', required=True)
    args = parser.parse_args()
    assert args.session > 0 and args.terminal and all(c in '0123456789abcdef' for c in args.terminal)
    assert args.exit_code in (0, 1)
    assert len(args.result_sha256) == 64 and all(c in '0123456789abcdef' for c in args.result_sha256)
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    for name in ('ROOT-BACKUP-CLEANUP.json', 'ROOT-TERMINAL.json', 'ROOT-REPLAY.json', 'SYMLINKS.json', 'FILES.json'):
        assert not (PAIR / name).exists() and not (PAIR / name).is_symlink()
    assert not REFRESH.exists() and not REFRESH.is_symlink()
    policy = read(HERE / 'POLICY.json')
    baseline = load('matching_root_baseline', str((HERE / 'baseline.py').relative_to(ROOT)))
    prepared, owner, roles = baseline.prepare(OWNER_SHA)
    assert prepared == policy and policy['execution_enabled'] and policy['candidate_execution_enabled']
    assert set(roles) == {'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h'}
    assert policy['runtime_output'] == str(PAIR.relative_to(ROOT))
    state = load('matching_root_state', policy['state_helper'])
    bundle = load('matching_root_bundle', policy['bundle_helper'])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    assert {name: sha(RUNTIME / name) for name in policy['controls']} == policy['controls']
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists() and not (RUNTIME / 'SOURCE-TRANSITION.lock').is_symlink()
    result_sha = sha(PAIR / 'CANDIDATE-RESULT.json')
    assert result_sha == args.result_sha256
    result = read(PAIR / 'CANDIDATE-RESULT.json')
    restoration = read(PAIR / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert set(restoration['sources']) == set(roles)
    backup = read(PAIR / 'BACKUP-CLEANUP.json')
    assert backup['verified_original_restoration']
    build = read(PAIR / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
    assert build['error'] is None and build['stop_reason'] is None
    compiled = read(PAIR / 'candidate-build/RESULT.json')
    assert compiled['command_success'] and compiled['preservation_verified'] and compiled['error'] is None
    assert compiled['native_sources'] == {name: record['candidate_sha256'] for name, record in roles.items()}
    assert set(compiled['binaries']) == set(policy['rebuilt_binaries'])
    command = read(PAIR / 'candidate-build/COMMAND.json')
    assert command['source_sha256'] == compiled['native_sources'] and command['owner_manifest'] == OWNER_SHA
    assert command['command'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
    phase = PAIR / 'candidate-wpt'
    for path in (PAIR / 'candidate-build/build-PROCESS.json', PAIR / 'candidate-build/WAKE-PROCESS.json', phase / 'PROCESS.json'):
        owner.group_absent(read(path)['pgid'])
    for path in policy['closed_process_receipts']:
        owner.group_absent(read(ROOT / path)['pgid'])
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    assessor = load('matching_root_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
    checks = load('matching_root_checks', policy['wpt']['checks_helper'])
    comparison = load('matching_root_comparison', str((HERE / 'comparison.py').relative_to(ROOT)))
    original = comparison.replay_original(ROOT, policy, assessor, checks)
    settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert settings == comparison.phase_policy(policy['wpt'])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    metadata = read(phase / 'APPLICATION-METADATA.json')
    phase_result = read(phase / 'RESULT.json')
    assessment = assessor.assess(events, phase_result['exit'], settings, checks, original=original, run_binding=metadata)
    assert json.loads(json.dumps(assessment)) == read(phase / 'ASSESSMENT.json')
    phase_hashes = {key: sha(phase / name) for key, name in [('assessment_sha256', 'ASSESSMENT.json'), ('raw_sha256', 'raw.jsonl'), ('result_sha256', 'RESULT.json')]}
    passed = outcome_join(result, phase_result, assessment, args.exit_code, phase_hashes)
    collector = load('same_element_root_records', str((HERE / 'records.py').relative_to(ROOT)))
    collection = collector.collect(ROOT, PAIR / 'progress-records', read(PAIR / 'PROGRESS-BINDING.json'), policy, assessment)
    assert collection == read(PAIR / 'PROGRESS-RECORDS.json')
    assert collection['complete'] and not collection['missing'] and not collection['errors'] and len(collection['records']) == 2
    phases = load('same_element_root_record_comparison', str((HERE / 'phases.py').relative_to(ROOT)))
    assert phases.record_comparison(ROOT, PAIR, policy, collection) == read(PAIR / 'RECORD-COMPARISON.json')

    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == compiled['snapshot']
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == metadata['build_revision'] == metadata['harness_revision'] == policy['head']
    assert metadata['source_role'] == 'candidate'
    assert compiled['binaries'] == read(phase / 'BINARY-PINS.json')
    for name, record in policy['wpt']['resources'].items():
        assert sha(phase / 'tests' / name) == record['sha256']
    assert sha(phase / 'metadata/MANIFEST.json') == policy['wpt']['manifest']['sha256']
    for name, role in roles.items():
        claim = restoration['sources'][name]
        assert claim['sha256'] == role['base_sha256']
        assert claim['identity'] == read(PAIR / 'CANDIDATE-PRE.json')['sources'][name]['identity']
        owner.claim(ROOT, name, role['base_sha256'], claim['identity'])
    for name, record in policy['accepted_current_payloads'].items():
        owner.claim(ROOT, name, record['sha256'], record['identity'])
    for name, pin in policy['source_context_pins'].items():
        assert sha(ROOT / name) == pin
    assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(PAIR / 'APP-PRE.json'))
    assert bundle.semantic({name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}) == bundle.semantic(read(PAIR / 'EXTRA-PRE.json'))
    for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
        assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == policy['prepared_flag_hashes'][name]
    old_bytes = (RUNTIME / 'CURRENT-EPOCH.json').read_bytes()
    old = json.loads(old_bytes)
    observation = read(PAIR / 'RAW-INDEX-OBSERVATION.json')
    assert observation['semantic_index_unchanged'] and not observation['canonical_updated']
    assert observation['before'] == old['raw_index_observation']['current']
    updated = copy.deepcopy(old)
    updated['raw_index_observation']['current'] = observation['after']
    snapshot = state.a.verify_current(state.h, ROOT, env, updated)
    assert snapshot == read(PAIR / 'POST.json')
    pre = read(PAIR / 'CANDIDATE-PRE.json')
    assert pre['controls'] == policy['controls']
    expected = copy.deepcopy(pre['snapshot'])
    expected['index']['raw_index'] = observation['after']
    assert snapshot == expected
    assert backup['owned_backup_bytes'] == pre['owned_backup_bytes'] == read(PAIR / 'BACKUPS.json')['bytes']
    if passed:
        assert backup['removed'] and not backup['retained_after_failure']
        assert not (PAIR / 'backups').exists() and not (PAIR / 'backups').is_symlink()
    else:
        assert not backup['removed'] and backup['retained_after_failure']
        assert Path(restoration['backup_directory']) == PAIR / 'backups'
        assert (PAIR / 'backups').is_dir() and not (PAIR / 'backups').is_symlink()
        assert bundle.scan(PAIR / 'backups') == read(PAIR / 'BACKUPS.json')['owned_inventory']
        shutil.rmtree(PAIR / 'backups')
        save(PAIR / 'ROOT-BACKUP-CLEANUP.json', {'removed': not (PAIR / 'backups').exists(), 'verified_original_restoration': True, 'inventory_verified_before_removal': True, 'owner_failure_receipt_preserved': True, 'owned_backup_bytes': backup['owned_backup_bytes']})
    assert sha(PAIR / 'CANDIDATE-RESULT.json') == result_sha
    app_entry = ROOT / policy['wpt']['application_ini']
    summary = {'original_rows': original['rows'], 'candidate_rows': assessment['rows'], 'candidate_endings': assessment['ends'], 'comparison_errors': assessment['comparison_errors'], 'comparison_gate_passed': passed, 'phase': phase_hashes, 'record_comparison_sha256': sha(PAIR / 'RECORD-COMPARISON.json'), 'numeric_feedback_endpoint_oracle': False, 'native_acceptance': False}
    save(PAIR / 'ROOT-REPLAY.json', summary)
    terminal = {'session_id': args.session, 'terminal_chunk': args.terminal, 'exit': args.exit_code, 'owner_sha256': OWNER_SHA, 'result_sha256': result_sha, 'build_success': True, 'callbacks_passed': sum(r['status'] == 'PASS' for r in assessment['rows']), 'callbacks_failed': sum(r['status'] == 'FAIL' for r in assessment['rows']), 'ending': 'OK', 'comparison_gate_passed': passed, 'raw_replay_verified': True, 'state_and_application_restoration_independently_verified': True, 'raw_index_observation': observation, 'restored_application_entry': bundle.entry(app_entry), 'restored_application_target': bundle.entry(app_entry.resolve()), 'backup_removed_bytes': backup['owned_backup_bytes'], 'native_acceptance': False}
    terminal.update(complete_records=2, private_records_independently_validated=True, numeric_feedback_endpoint_oracle=False)
    save(PAIR / 'ROOT-TERMINAL.json', terminal)
    symlinks, manifest = {}, {}
    for directory, dirs, files in os.walk(PAIR, followlinks=False):
        for name in dirs + files:
            path = Path(directory) / name
            if path.is_symlink():
                symlinks[str(path.relative_to(PAIR))] = os.readlink(path)
            elif path.is_file():
                manifest[str(path.relative_to(PAIR))] = sha(path)
    save(PAIR / 'SYMLINKS.json', symlinks)
    manifest['SYMLINKS.json'] = sha(PAIR / 'SYMLINKS.json')
    save(PAIR / 'FILES.json', manifest)
    if observation['before'] != observation['after']:
        unchanged = copy.deepcopy(updated)
        unchanged['raw_index_observation']['current'] = observation['before']
        assert unchanged == old
        claim = owner.claim(ROOT, str((RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), policy['controls']['CURRENT-EPOCH.json'])
        try:
            owner.write_owned(ROOT, claim, owner.encoded(updated))
            assert state.a.verify_current(state.h, ROOT, env, updated) == snapshot
            assert all(sha(RUNTIME / name) == policy['controls'][name] for name in ('OWNED.json', 'ROLE.json'))
        except BaseException:
            owner.write_owned(ROOT, claim, old_bytes)
            raise
    refresh = {'before_epoch': policy['controls']['CURRENT-EPOCH.json'], 'after_epoch': sha(RUNTIME / 'CURRENT-EPOCH.json'), 'only_changed_field': 'raw_index_observation.current', 'observation': observation, 'runtime_manifest_sha256': sha(PAIR / 'FILES.json'), 'full_restored_state_verified': True, 'accepted_fix_increment': 0}
    save(REFRESH, refresh)
    print(json.dumps({'terminal': terminal, 'refresh': refresh}, indent=2), flush=True)


if __name__ == '__main__':
    main()
