import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def replace_bytes(path, data):
    descriptor, name = tempfile.mkstemp(prefix='.zoom-install-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def authenticate(manifest_pin):
    assert sha(HERE / 'FILES.json') == manifest_pin
    for name, pin in read(HERE / 'FILES.json').items():
        assert sha(HERE / name) == pin['sha256']
    for name, pin in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin


def check_state(policy, roles, epoch, role, owned, mode, epoch_pin):
    assert epoch['semantic_index']['head'] == policy['head']
    assert epoch['installed_identities'] == read(HERE / 'INITIAL-EPOCH.json')['installed_identities']
    assert len(epoch['installed_identities']) == policy['installed_identity_count']
    initial_owned = read(HERE / 'INITIAL-OWNED.json')
    assert len(owned) == policy['owned_count'] and set(owned) == set(initial_owned)
    assert all(v['identity'] == initial_owned[k]['identity'] for k, v in owned.items())
    assert all(v == initial_owned[k] for k, v in owned.items() if k not in roles)
    if mode == 'original':
        assert epoch_pin == policy['initial_epoch_sha256']
        assert epoch == read(HERE / 'INITIAL-EPOCH.json')
        assert role == read(HERE / 'INITIAL-ROLE.json') and owned == initial_owned
        assert set(epoch['modified_native_paths']) == set(roles)
    else:
        assert mode == 'candidate' and epoch_pin != policy['initial_epoch_sha256']
        assert epoch['modified_native_paths'] == []
        assert epoch['registered_number_transition'] == {
            'role': 'original', 'variant': policy['variant'], 'compiled': True,
            'last_phase': policy['baseline_build'], 'accepted': False}
        assert role['role'] == 'original' and role['variant'] == policy['variant']
        assert role['paired_head'] == policy['head'] and role['built'] is True
        assert role['last_build'] == policy['baseline_build']
        assert role['last_install'] == policy['baseline_install']
        assert epoch['zoom_standalone_transition'] == {
            'manifest_sha256': sha(HERE / 'FILES.json'), 'source_paths': 9,
            'prior_epoch_sha256': policy['initial_epoch_sha256'], 'accepted': False,
            'prototype_recovery': str(HERE.relative_to(ROOT)), 'mode': 'original'}
        initial = read(HERE / 'INITIAL-EPOCH.json')
        rebuilt = {'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
                   'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                   'objdir-full.noindex/dist/bin/gtest/XUL',
                   'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL'}
        assert set(epoch['pins']) == set(initial['pins'])
        assert all(pin == initial['pins'][name] for name, pin in epoch['pins'].items()
                   if name not in set(roles) | rebuilt)
        expected = copy.deepcopy(initial)
        for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
            for name, record in roles.items():
                if name in expected[key]:
                    expected[key][name] = record['original_sha256']
        for name in rebuilt:
            expected['pins'][name] = epoch['pins'][name]
        expected['modified_native_paths'] = []
        expected['counts']['native_modified_paths'] = 0
        expected['semantic_index']['working_diff'] = epoch['semantic_index']['working_diff']
        expected['raw_index_observation']['current'] = epoch['raw_index_observation']['current']
        expected['registered_number_transition'] = epoch['registered_number_transition']
        expected['zoom_standalone_transition'] = epoch['zoom_standalone_transition']
        assert epoch == expected
    assert set(roles) == set(read(HERE / 'INITIAL-EPOCH.json')['modified_native_paths'])
    assert len(roles) == 9 and sum('candidate' in v for v in roles.values()) == 7
    assert all(roles[n]['identity'] == epoch['installed_identities'][n] for n in roles)
    for name, record in roles.items():
        expected = record['prototype_sha256' if mode == 'original' else 'original_sha256']
        assert epoch['pins'][name] == expected
        assert owned[name]['owned_sha256'] == expected


def preserve_recovery(s, policy, roles):
    restoration = read(RUNTIME / 'RESTORATION-PLAN.json')['paths']
    assert len(restoration) == policy['parked_count']
    for name, pins in restoration.items():
        assert sha(RUNTIME / 'prototype-original' / name) == pins['prototype_original']
        assert hashlib.sha256(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)).hexdigest() == pins['head_original']
        if name not in roles:
            assert sha(ROOT / name) == pins['head_original']
    recovery = read(ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
    assert len(recovery) == policy['recovery_count']
    ledger = read(ROOT / 'artifacts/css-local-signing-20261027-v21/ROADMAP-UPDATE.json')['after']
    for name, pin in recovery.items():
        if name in ledger:
            assert sha(ROOT / name) == ledger[name]
        else:
            source = (RUNTIME / 'prototype-original' / name if name in restoration else
                      ROOT / roles[name]['original'] if name in roles else ROOT / name)
            assert sha(source) == pin, name
    untracked = s.h.git(ROOT, ENV, 'ls-files', '--others', '--exclude-standard',
                       'dom/animation', 'layout/style/test/gtest', 'servo/components/style',
                       'testing/web-platform/tests/css').decode().splitlines()
    assert len(untracked) == policy['untracked_project_count'] and set(untracked) <= set(recovery)
    return untracked


def ownership_helper():
    spec = importlib.util.spec_from_file_location('owned_transition', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def process_census_clear(text, own_pid):
    rows = {}
    for line in text.splitlines():
        parts = line.strip().split(None, 3)
        assert len(parts) == 4
        pid, parent, group = map(int, parts[:3])
        assert pid not in rows
        rows[pid] = (parent, group, parts[3])
    assert own_pid in rows
    ancestors = set()
    cursor = own_pid
    while cursor in rows and cursor not in ancestors:
        ancestors.add(cursor)
        cursor = rows[cursor][0]
    blocked = []
    for pid, (_, _, command) in rows.items():
        if pid in ancestors:
            continue
        if (str(ROOT / 'objdir-full.noindex') in command or
            './mach build' in command or './mach wpt' in command or
            'mach test' in command or 'mach gtest' in command):
            blocked.append([pid, command])
    assert not blocked, ('active build/browser/test process', blocked)


def quiescent(ownership, role):
    ownership.quiescent(RUNTIME)
    build = RUNTIME / role['last_build']
    result = read(build / 'RESULT.json')
    assert result['command_success'] and result['preservation_verified']
    assert result['owned_processes'] == {} and result['publication_errors'] == []
    for name in ['build-PROCESS.json', 'WAKE-PROCESS.json']:
        ownership.group_absent(read(build / name)['pgid'])
    for name in read(HERE / 'QUIESCENCE-PINS.json'):
        if name.endswith('/PROCESS.json'):
            ownership.group_absent(read(ROOT / name)['pgid'])
        elif name.endswith('/CLEANUP.json'):
            assert read(ROOT / name)['owned_group_absent']
        elif name.endswith('/RESULT.json'):
            result = read(ROOT / name)
            if name.startswith('artifacts/css-registered-container-zoom-runtime-'):
                assert result['complete'] and result['execution_preserved']
            else:
                assert result['observation_gate_passed'] and result['execution_error'] is None
                assert result['preservation_error'] is None
                assessment = read((ROOT / name).with_name('ASSESSMENT.json'))
                assert assessment['complete'] and assessment['execution_preserved']
    census = subprocess.run(['ps', '-axo', 'pid=,ppid=,pgid=,command='],
                            check=True, capture_output=True, text=True).stdout
    process_census_clear(census, os.getpid())


def prewrite_guard(ownership, controls, native, manifest_pin):
    authenticate(manifest_pin)
    for name, item in controls.items():
        ownership.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
    for name, item in native.items():
        ownership.claim(ROOT, name, item['owned_sha256'], item['identity'])


def main():
    assert read(HERE / 'POLICY.json')['execution_enabled'] is True, 'Disabled checkpoint; successor review required'
    mode, manifest_pin, epoch_pin = sys.argv[1:]
    assert mode in ('original', 'candidate') and len(epoch_pin) == 64
    authenticate(manifest_pin)
    assert not any(os.environ.get(k) for k in
                   ['GIT_DIR', 'GIT_INDEX_FILE', 'GIT_WORK_TREE', 'RUSTFLAGS', 'CARGO_TARGET_DIR'])
    assert shutil.disk_usage(ROOT).free > 35 * 2**30
    spec = importlib.util.spec_from_file_location('standalone_state', RUNTIME / 'state.py')
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    policy, roles = read(HERE / 'POLICY.json'), read(HERE / 'SOURCE-ROLES.json')
    ownership = ownership_helper()
    controls_before = {name: (RUNTIME / name).read_bytes()
                       for name in ['ROLE.json', 'OWNED.json', 'CURRENT-EPOCH.json']}
    controls_owned = {name: ownership.claim(ROOT, str((RUNTIME / name).relative_to(ROOT)),
                      hashlib.sha256(data).hexdigest()) for name,data in controls_before.items()}
    epoch_bytes = controls_before['CURRENT-EPOCH.json']
    assert hashlib.sha256(epoch_bytes).hexdigest() == epoch_pin
    epoch, role, owned = [json.loads(controls_before[n]) for n in
                           ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']]
    check_state(policy, roles, epoch, role, owned, mode, epoch_pin)
    quiescent(ownership, role)
    before = s.a.verify_current(s.h, ROOT, ENV, epoch)
    assert s.h.git(ROOT, ENV, 'symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
    flags = {name: s.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z')
             for name in ['.', 'artifacts/css-spec-lean']}
    untracked = preserve_recovery(s, policy, roles)
    if mode == 'candidate':
        build = RUNTIME / policy['baseline_build']
        assert (build / 'EPOCH.json').read_bytes() == epoch_bytes
        result = read(build / 'RESULT.json')
        assert result == {'command_success': True, 'error': None, 'publication_errors': [],
                          'owned_processes': {}, 'source_role': 'original', 'preservation_verified': True}
        assert read(build / 'POST.json') == before
        installed = read(RUNTIME / policy['baseline_install'] / 'RESULT.json')
        assert installed['installed'] and installed['mode'] == 'original'
        assert installed['manifest_sha256'] == manifest_pin and installed['modified_native_paths'] == 0
    selected = roles if mode == 'original' else {k: v for k, v in roles.items() if 'candidate' in v}
    target_key = 'original' if mode == 'original' else 'candidate'
    source_key = 'prototype' if mode == 'original' else 'original'
    native_owned, desired, restore = {}, {}, {}
    for name, record in roles.items():
        path = ROOT / name
        st = path.lstat()
        assert path.is_file() and not path.is_symlink()
        assert [st.st_dev, st.st_ino] == record['identity']
        assert sha(path) == record[source_key + '_sha256']
        assert hashlib.sha256(s.h.git(ROOT, ENV, 'show', 'HEAD:' + name)).hexdigest() == record['original_sha256']
        native_owned[name] = ownership.claim(ROOT, name, record[source_key + '_sha256'], record['identity'])
        for key in ['original', 'prototype'] + (['candidate'] if 'candidate' in record else []):
            data = ownership.body(ROOT / record[key])
            assert hashlib.sha256(data).hexdigest() == record[key + '_sha256']
            if key == source_key:
                restore[name] = data
            if name in selected and key == target_key:
                desired[name] = data
    run = RUNTIME / policy['baseline_install' if mode == 'original' else 'candidate_install']
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    with lock.open('x') as stream:
        json.dump({'pid': os.getpid(), 'mode': mode, 'epoch_sha256': epoch_pin}, stream)
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    changed, controls_after = [], {}
    current = copy.deepcopy(epoch)
    try:
        run.mkdir()
        save(run / 'PRE.json', before)
        save(run / 'FLAGS.json', {name: hashlib.sha256(body).hexdigest() for name,body in flags.items()})
        save(run / 'INITIAL-EPOCH.json', epoch)
        save(run / 'PREVIOUS-ROLE.json', role)
        save(run / 'PREVIOUS-OWNED.json', owned)
        save(run / 'SOURCE-ROLES.json', roles)
        assert s.a.verify_current(s.h, ROOT, ENV, epoch) == before
        prewrite_guard(ownership, controls_owned, native_owned, manifest_pin)
        quiescent(ownership, role)
        prewrite_guard(ownership, controls_owned, native_owned, manifest_pin)
        for name, record in selected.items():
            path = ROOT / name
            st = path.lstat()
            assert [st.st_dev, st.st_ino] == record['identity'] and not path.is_symlink()
            assert sha(path) == record[source_key + '_sha256']
            changed.append(name)
            ownership.write_owned(ROOT, native_owned[name], desired[name])
            for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
                if name in current[key]:
                    current[key][name] = s.h.fingerprint(ROOT, name)
            owned[name]['owned_sha256'] = record[target_key + '_sha256']
        state = s.h.index_state(ROOT, ENV)
        semantic = s.h.semantic_index(state)
        assert {k:v for k,v in semantic.items() if k != 'working_diff'} == {
            k:v for k,v in epoch['semantic_index'].items() if k != 'working_diff'}
        assert s.h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
        current['semantic_index'] = semantic
        current['raw_index_observation']['current'] = state['raw_index']
        current['modified_native_paths'] = [] if mode == 'original' else sorted(selected)
        assert sorted(s.h.git(ROOT, ENV, 'diff', '--name-only').decode().splitlines()) == current['modified_native_paths']
        current['counts']['native_modified_paths'] = len(current['modified_native_paths'])
        current['registered_number_transition'] = {'role': mode, 'variant': policy['variant'],
            'compiled': False, 'last_phase': run.name, 'accepted': False}
        current['zoom_standalone_transition'] = {'manifest_sha256': manifest_pin,
            'source_paths': len(selected), 'prior_epoch_sha256': epoch_pin, 'accepted': False,
            'prototype_recovery': str(HERE.relative_to(ROOT)), 'mode': mode}
        after = s.a.verify_current(s.h, ROOT, ENV, current)
        assert preserve_recovery(s, policy, roles) == untracked
        assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == b for n,b in flags.items())
        save(run / 'INDEX-OBSERVATION.json', {'before_raw': before['index']['raw_index'],
            'after_raw': state['raw_index'], 'semantic_entries_head_cached_unchanged': True,
            'flags_unchanged': True, 'drift_cause': 'unknown' if state['raw_index'] != before['index']['raw_index'] else 'no drift'})
        authenticate(manifest_pin)
        role.update({'role': mode, 'variant': policy['variant'], 'built': False,
                     'paired_head': policy['head'], 'last_install': run.name})
        controls_after = {'ROLE.json': (json.dumps(role, indent=2)+'\n').encode(),
                          'OWNED.json': (json.dumps(owned, indent=2, sort_keys=True)+'\n').encode(),
                          'CURRENT-EPOCH.json': (json.dumps(current, indent=2, sort_keys=True)+'\n').encode()}
        for name, data in controls_after.items():
            ownership.claim(ROOT, controls_owned[name]['path'], controls_owned[name]['owned_sha256'], controls_owned[name]['identity'])
            previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
            try:
                replace_bytes(RUNTIME / name, data)
                controls_owned[name] = ownership.claim(ROOT, controls_owned[name]['path'], hashlib.sha256(data).hexdigest())
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        assert all((RUNTIME / n).read_bytes() == b for n,b in controls_after.items())
        save(run / 'POST.json', after)
        save(run / 'EPOCH.json', current)
        save(run / 'RESULT.json', {'installed': True, 'mode': mode, 'compiled': False,
             'accepted': False, 'manifest_sha256': manifest_pin,
             'modified_native_paths': len(current['modified_native_paths']),
             'existing_work_preserved': True, 'epoch_sha256': sha(RUNTIME / 'CURRENT-EPOCH.json')})
    except BaseException:
        for name, data in controls_before.items():
            ownership.claim(ROOT, controls_owned[name]['path'], controls_owned[name]['owned_sha256'], controls_owned[name]['identity'])
            replace_bytes(RUNTIME / name, data)
        for name in reversed(changed):
            path = ROOT / name
            st = path.lstat()
            assert [st.st_dev, st.st_ino] == roles[name]['identity'] and not path.is_symlink()
            ownership.write_owned(ROOT, native_owned[name], restore[name])
        restored_state = s.h.index_state(ROOT, ENV)
        assert s.h.semantic_index(restored_state) == epoch['semantic_index']
        restored = copy.deepcopy(epoch)
        restored['raw_index_observation']['current'] = restored_state['raw_index']
        restored_check = s.a.verify_current(s.h, ROOT, ENV, restored)
        assert restored_check['nested_index'] == before['nested_index']
        assert preserve_recovery(s, policy, roles) == untracked
        assert all(s.h.git(ROOT / n, ENV, 'ls-files', '-v', '-z') == b for n,b in flags.items())
        assert (RUNTIME / 'CURRENT-EPOCH.json').read_bytes() == controls_before['CURRENT-EPOCH.json']
        replace_bytes(RUNTIME / 'CURRENT-EPOCH.json', (json.dumps(restored, indent=2, sort_keys=True)+'\n').encode())
        save(run / 'ROLLED-BACK.json', {'restored': changed,
            'before_raw': epoch['raw_index_observation']['current'], 'after_raw': restored_state['raw_index'],
            'drift_cause': 'unknown' if restored_state['raw_index'] != epoch['raw_index_observation']['current'] else 'no drift',
            'full_restored_semantics_sources_controls_verified': True,
            'refreshed_epoch_sha256': sha(RUNTIME / 'CURRENT-EPOCH.json')})
        raise
    finally:
        assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
        lock.unlink()
    print((run / 'RESULT.json').read_text(), flush=True)


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise RuntimeError('Interrupted transition: ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    main()
