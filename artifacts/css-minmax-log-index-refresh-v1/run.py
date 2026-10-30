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
PAIR = ROOT / 'artifacts/css-minmax-log-baseline-runtime-1'
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
    assert all(sha(ROOT / n) == pin for n, pin in policy['references'].items())
    assert {n: sha(RUNTIME / n) for n in policy['controls']} == policy['controls']
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    result = read(PAIR / 'CANDIDATE-RESULT.json')
    terminal = read(PAIR / 'CANDIDATE-ROOT-REPORTED-TERMINAL.json')
    assert result['success'] and result['restoration_verified']
    assert terminal['session_id'] == 83012 and terminal['terminal_chunk'] == '0fce51'
    assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(PAIR / 'CANDIDATE-RESULT.json')
    assert read(PAIR / 'RESTORATION.json')['owned_processes'] == {}
    assert read(PAIR / 'BACKUP-CLEANUP.json')['removed'] and not (PAIR / 'backups').exists()
    observation = read(PAIR / 'RAW-INDEX-OBSERVATION.json')
    assert observation['semantic_index_unchanged'] and not observation['canonical_updated']
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
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'))
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
        'raw_byte_drift_cause': 'unknown',
    })
    print('Refreshed only the raw-index observation; full restored state verified', flush=True)


if __name__ == '__main__':
    main()
