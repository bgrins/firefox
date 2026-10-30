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
PAIR = ROOT / 'artifacts/css-contextual-duration-feedback-candidate-runtime-2'
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
    assert policy['runtime_manifest_sha256'] is not None and sha(PAIR / 'FILES.json') == policy['runtime_manifest_sha256']
    result = read(PAIR / 'CANDIDATE-RESULT.json')
    terminal = read(PAIR / policy['terminal_path'])
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['error'] is None and result['publication_errors'] == []
    assert result['empty_staging_preserved'] and result['native_fix_acceptance'] is False
    assert terminal == policy['terminal']
    assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(PAIR / 'CANDIDATE-RESULT.json')
    restoration = read(PAIR / 'RESTORATION.json')
    assert restoration['owned_processes'] == {} and restoration['errors'] == []
    backup = read(PAIR / 'BACKUP-CLEANUP.json')
    assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    assert not (PAIR / 'backups').exists() and not (PAIR / 'backups').is_symlink()
    build = read(PAIR / 'candidate-build/build-RESULT.json')
    assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
    assert build['error'] is None and build['stop_reason'] is None
    phase = PAIR / 'feedback-wpt'
    outcome = read(phase / 'RESULT.json')
    assert outcome['success'] and outcome['comparison_gate_passed'] and outcome['preservation_verified']
    assert outcome['exit'] == 0 and outcome['execution_error'] is None
    assessment = read(phase / 'ASSESSMENT.json')
    assert assessment['complete'] and assessment['errors'] == [] and assessment['comparison_errors'] == []
    assert assessment['comparison_gate_passed'] and assessment['observed_subtest_count'] == 3
    assert len(assessment['rows']) == 3 and all(row['status'] == 'PASS' for row in assessment['rows'])
    assert len(assessment['ends']) == 1 and assessment['ends'][0]['status'] == 'OK'
    assert result['candidate_phase'] == {'feedback': {key:sha(phase / name) for key,name in [('result_sha256','RESULT.json'),('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl')]}}
    assert read(PAIR / 'PHASES-PRE.json') == read(PAIR / 'PHASES-POST.json') == read(phase / 'PRE.json') == read(phase / 'POST.json')
    assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    records = load('feedback_refresh_records', policy['feedback_records_helper']).feedback_records(PAIR)
    assert records == read(PAIR / 'FEEDBACK-RECORDS.json') and records['numeric_or_convergence_oracle'] is False
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
        'feedback_comparison_success': True,
        'feedback_numeric_or_convergence_claim': False,
        'raw_byte_drift_cause': 'unknown',
    })
    print('Refreshed only the raw-index observation; full restored state verified', flush=True)


if __name__ == '__main__':
    main()
