import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
PAIR = ROOT / 'artifacts/css-contextual-duration-broader-candidate-runtime-1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 2 and sha(HERE / 'FILES.json') == sys.argv[1]
    for name, pin in read(HERE / 'FILES.json').items():
        assert sha(HERE / name) == pin
    policy = read(HERE / 'POLICY.json')
    assert policy['execution_enabled'] is True and policy['terminal'] is not None
    assert all(str((PAIR / name).relative_to(ROOT)) in policy['references'] for name in policy['required_pair_evidence'])
    assert all(sha(ROOT / n) == pin for n, pin in policy['references'].items())
    assert {n: sha(RUNTIME / n) for n in policy['controls']} == policy['controls']
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    result = read(PAIR / 'CANDIDATE-RESULT.json')
    terminal = read(PAIR / policy['terminal_path'])
    assert terminal == policy['terminal'] and terminal['exit'] == 1
    assert terminal['result_sha256'] == sha(PAIR / 'CANDIDATE-RESULT.json')
    assert terminal['restoration_independently_verified'] and terminal['restoration_check_exit'] == 0
    assert terminal['phase_replay_sha256'] == sha(PAIR / 'ROOT-PHASE-REPLAY.json')
    replay = read(PAIR / 'ROOT-PHASE-REPLAY.json')
    assert replay == policy['phase_replay'] and replay['feedback_executed'] is False
    assert replay['restyle_raw_replayed'] and replay['restyle_timestamp_signature_differences'] == 4
    assert result == policy['expected_candidate_result']
    assert not result['success'] and result['restoration_verified']
    assert result['runtime_controls_unchanged'] and result['empty_staging_preserved']
    assert result['publication_errors'] == [] and result['candidate_phase'] is None
    assert result['native_fix_acceptance'] is False
    restoration = read(PAIR / 'RESTORATION.json')
    assert restoration['owned_processes'] == {} and restoration['errors'] == []
    backup = read(PAIR / 'BACKUP-CLEANUP.json')
    assert backup['verified_original_restoration'] and backup['retained_after_failure'] and not backup['removed']
    cleanup = read(PAIR / 'ROOT-BACKUP-CLEANUP.json')
    assert cleanup == policy['root_backup_cleanup'] and cleanup['removed']
    assert cleanup['verified_original_restoration'] and cleanup['full_state_verified_against_restored_POST']
    assert cleanup['owned_inventory_verified'] and cleanup['historical_owner_result_unchanged']
    assert cleanup['owned_backup_bytes'] == backup['owned_backup_bytes']
    assert not (PAIR / 'backups').exists() and not (PAIR / 'backups').is_symlink()
    build = read(PAIR / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
    assert build['error'] is None and build['stop_reason'] is None
    for kind, count in [('normative', 49), ('reftest', 0), ('inactive', 1)]:
        phase = PAIR / (kind + '-wpt')
        assert replay['successful_phases'][kind]['raw_sha256'] == sha(phase / 'raw.jsonl')
        assert replay['successful_phases'][kind]['rows'] == count
        outcome = read(phase / 'RESULT.json')
        assert outcome['success'] and outcome['comparison_gate_passed'] and outcome['preservation_verified']
        assert outcome['exit'] == 0 and outcome['execution_error'] is None
        assessment = read(phase / 'ASSESSMENT.json')
        assert assessment['complete'] and assessment['errors'] == [] and assessment['comparison_errors'] == []
        assert assessment['comparison_gate_passed'] and assessment['observed_subtest_count'] == count
        assert all(row['status'] == 'PASS' for row in assessment['rows'])
        phase_cleanup = read(phase / 'CLEANUP.json')
        assert phase_cleanup['owned_group_absent'] and phase_cleanup['temporary_root_removed']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json')
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
    restyles = read(PAIR / 'restyles/RESULT.json')
    assert restyles == policy['expected_restyle_result']
    assert restyles['exit'] == 0 and restyles['execution_error'] is None and restyles['owned_group_absent']
    assert restyles['preservation_verified'] and not restyles['comparison_passed']
    assert read(PAIR / 'restyles/CLEANUP.json')['owned_group_absent']
    assert read(PAIR / 'restyles/PRE.json') == read(PAIR / 'restyles/POST.json')
    assert read(PAIR / 'restyles/APPLICATION-METADATA.json') == read(PAIR / 'restyles/APPLICATION-METADATA-POST.json')
    differences = read(PAIR / 'RESTYLE-SIGNATURE-DIFFERENCES.json')
    assert differences == policy['expected_restyle_differences']
    assert [item['index'] for item in differences] == [24, 25, 27, 28]
    for item in differences:
        assert item['original']['status'] == item['candidate']['status'] == 'PASS'
        assert {k:v for k,v in item['original'].items() if k != 'message'} == {k:v for k,v in item['candidate'].items() if k != 'message'}
    assert all(not (PAIR / name).exists() for name in ('feedback-wpt','feedback-records','FEEDBACK-BINDING.json','FEEDBACK-RECORDS.json','PHASES-POST.json'))
    observation = read(PAIR / 'RAW-INDEX-OBSERVATION.json')
    assert observation == policy['raw_index_observation']
    assert observation['semantic_index_unchanged'] and not observation['canonical_updated']
    assert observation['before'] != observation['after']
    source = RUNTIME / 'CURRENT-EPOCH.json'
    old_bytes = source.read_bytes()
    old = json.loads(old_bytes)
    assert old['semantic_index']['head'] == policy['head'] and old['staged_working'] == {}
    assert old['raw_index_observation']['current'] == observation['before']
    new = copy.deepcopy(old)
    new['raw_index_observation']['current'] = observation['after']
    check = copy.deepcopy(new)
    check['raw_index_observation']['current'] = observation['before']
    assert check == old
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    state = load('index_refresh_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
    owner = load('index_refresh_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
    snapshot = state.a.verify_current(state.h, ROOT, env, new)
    assert snapshot == read(PAIR / 'POST.json')
    claim = owner.claim(ROOT, str(source.relative_to(ROOT)), policy['controls']['CURRENT-EPOCH.json'])
    assert all(sha(ROOT / n) == pin for n, pin in policy['references'].items())
    try:
        owner.write_owned(ROOT, claim, owner.encoded(new))
        assert state.a.verify_current(state.h, ROOT, env, new) == snapshot
        assert all(sha(RUNTIME / n) == policy['controls'][n] for n in ('OWNED.json', 'ROLE.json'))
    except BaseException:
        owner.write_owned(ROOT, claim, old_bytes)
        raise
    state.save(HERE / 'RESULT.json', {
        'only_changed_field': 'raw_index_observation.current',
        'before_epoch': policy['controls']['CURRENT-EPOCH.json'],
        'after_epoch': sha(source), 'raw_index': observation,
        'source_application_git_and_acceptance_unchanged': True,
        'full_state_matches_restored_pair': True,
        'candidate_comparison_success': False,
        'candidate_failure': 'four restyle timestamp diagnostic differences; feedback not run',
        'raw_byte_drift_cause': 'unknown',
    })
    print('Refreshed only the raw-index observation; full restored state verified', flush=True)


if __name__ == '__main__':
    main()
