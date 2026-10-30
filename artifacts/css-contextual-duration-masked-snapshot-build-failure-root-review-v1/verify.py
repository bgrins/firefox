import argparse
import copy
import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path
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


def failure_join(result, build, restoration, backup, terminal_exit):
    assert terminal_exit == 1
    assert result['success'] is False and result['error'] == 'AssertionError()'
    assert result['candidate_phase'] is None and result['publication_errors'] == []
    assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['native_fix_acceptance'] is False
    assert result['success_scope'] == 'build, complete observation and restoration; callback PASS is separate'
    assert build['exit'] == 2 and build['owned_group_absent']
    assert build['cleanup_errors'] == [] and build['error'] is None and build['stop_reason'] is None
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert backup['verified_original_restoration'] and backup['retained_after_failure'] and not backup['removed']


def main():
    assert CONFIG['execution_enabled'] and OWNER_SHA is not None, 'Root review/actual owner binding required'
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=int, required=True)
    parser.add_argument('--terminal', required=True)
    parser.add_argument('--exit', type=int, required=True, dest='exit_code')
    parser.add_argument('--result-sha256', required=True)
    args = parser.parse_args()
    assert args.session > 0 and args.terminal and all(c in '0123456789abcdef' for c in args.terminal)
    assert (args.session, args.terminal, args.exit_code, args.result_sha256) == (CONFIG['actual_terminal']['session'], CONFIG['actual_terminal']['terminal'], 1, CONFIG['actual_terminal']['result_sha256'])
    assert len(args.result_sha256) == 64 and all(c in '0123456789abcdef' for c in args.result_sha256)
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    for name in ('ROOT-BACKUP-CLEANUP.json', 'ROOT-TERMINAL.json', 'ROOT-REPLAY.json', 'SYMLINKS.json', 'FILES.json'):
        assert not (PAIR / name).exists() and not (PAIR / name).is_symlink()
    assert not REFRESH.exists() and not REFRESH.is_symlink()
    for name, record in read(REVIEW / 'REFERENCES.json').items():
        assert sha(ROOT / name) == record['sha256'], name
    for name, digest in CONFIG['saved_runtime_inputs'].items():
        assert sha(PAIR / name) == digest, name
    for name in CONFIG['absent_paths']:
        assert not (PAIR / name).exists() and not (PAIR / name).is_symlink(), name
    policy = read(HERE / 'POLICY.json')
    baseline = load('matching_root_baseline', str((HERE / 'baseline.py').relative_to(ROOT)))
    prepared, owner, roles = baseline.prepare(OWNER_SHA)
    assert prepared == policy and policy['execution_enabled'] and policy['candidate_execution_enabled']
    assert set(roles) == {'layout/style/AnimationCollection.h', 'layout/style/nsAnimationManager.cpp', 'layout/style/GeckoBindings.cpp', 'layout/style/nsAnimationManager.h', 'servo/components/style/context.rs', 'servo/components/style/matching.rs', 'layout/style/ServoTypes.h'}
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
    failure_join(result, build, restoration, backup, args.exit_code)
    failure = read(PAIR / 'FAILURE-TRACEBACK.json')
    assert failure['error'] == result['error']
    assert "assert process.returncode == 0 and stop_reason is None and failure is None" in failure['traceback']
    command = read(PAIR / 'candidate-build/COMMAND.json')
    assert command['source_sha256'] == {name: record['candidate_sha256'] for name, record in roles.items()}
    assert command['owner_manifest'] == OWNER_SHA
    assert command['command'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
    log = (PAIR / 'candidate-build/build.log').read_text()
    assert "error: enumeration redeclared with different underlying type 'uint8_t'" in log
    assert "(was 'uint16_t'" in log and 'GeckoBindings.h:36:12' in log
    for name in ('build', 'wake'):
        assert read(PAIR / ('candidate-build/' + name + '-GROUP-CLEANUP.json'))['owned_group_absent']
    assert read(PAIR / 'candidate-build/WAKE-RESULT.json')['owned_group_absent']
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        owner.group_absent(read(PAIR / 'candidate-build' / name)['pgid'])
    for path in policy['closed_process_receipts']:
        owner.group_absent(read(ROOT / path)['pgid'])
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
    assert not backup['removed'] and backup['retained_after_failure']
    assert Path(restoration['backup_directory']) == PAIR / 'backups'
    assert (PAIR / 'backups').is_dir() and not (PAIR / 'backups').is_symlink()
    assert bundle.scan(PAIR / 'backups') == read(PAIR / 'BACKUPS.json')['owned_inventory']
    shutil.rmtree(PAIR / 'backups')
    save(PAIR / 'ROOT-BACKUP-CLEANUP.json', {'removed': not (PAIR / 'backups').exists(), 'verified_original_restoration': True, 'inventory_verified_before_removal': True, 'owner_failure_receipt_preserved': True, 'owned_backup_bytes': backup['owned_backup_bytes']})
    assert sha(PAIR / 'CANDIDATE-RESULT.json') == result_sha
    app_entry = ROOT / policy['wpt']['application_ini']
    summary = {'build_success': False, 'build_exit': build['exit'], 'build_result_sha256': sha(PAIR / 'candidate-build/build-RESULT.json'), 'build_log_sha256': sha(PAIR / 'candidate-build/build.log'), 'failure_traceback_sha256': sha(PAIR / 'FAILURE-TRACEBACK.json'), 'candidate_result_sha256': result_sha, 'browser_executed': False, 'observation_complete': False, 'comparison_gate_passed': None, 'absence_verified': CONFIG['absent_paths'], 'owner_failure_preserved': True, 'native_acceptance': False}
    save(PAIR / 'ROOT-REPLAY.json', summary)
    terminal = {'session_id': args.session, 'terminal_chunk': args.terminal, 'exit': args.exit_code, 'owner_sha256': OWNER_SHA, 'result_sha256': result_sha, 'build_success': False, 'build_exit': build['exit'], 'browser_executed': False, 'observation_complete': False, 'comparison_gate_passed': None, 'state_and_application_restoration_independently_verified': True, 'raw_index_observation': observation, 'restored_application_entry': bundle.entry(app_entry), 'restored_application_target': bundle.entry(app_entry.resolve()), 'backup_removed_bytes': backup['owned_backup_bytes'], 'owner_failure_preserved': True, 'native_acceptance': False}
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
