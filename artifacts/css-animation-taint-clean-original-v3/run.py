import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import time
import traceback

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check', '--run')
    baseline = load('activation_baseline', str((HERE / 'baseline.py').relative_to(ROOT)))
    policy, ownership, roles = baseline.prepare(sys.argv[2])
    assert policy['wpt'] is not None
    if sys.argv[1] == '--check':
        print('Authenticated candidate recipe; no live guard')
        return
    assert policy['execution_enabled'] and policy['candidate_execution_enabled']
    assert policy['activation_pending'] == []
    baseline.require_ready(policy)
    state, env, controls, original, flags, original_verify = baseline.guard(policy, ownership, roles)
    original_before = original_verify()
    assert original_before == read(ROOT / policy["restoration_binding"]["directory"] / "ROOT-REVIEW.json")["snapshot"]
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
    output.mkdir()
    epoch = copy.deepcopy(original)
    bases, candidates, claims = {}, {}, {}
    for name, record in roles.items():
        bases[name] = (ROOT / record['base_capture']).read_bytes()
        candidates[name] = (ROOT / record['candidate_capture']).read_bytes()
        assert hashlib.sha256(bases[name]).hexdigest() == record['base_sha256']
        assert hashlib.sha256(candidates[name]).hexdigest() == record['candidate_sha256']
        claims[name] = ownership.claim(ROOT, name, record['base_sha256'], epoch['installed_identities'].get(name))
        epoch['pins'][name] = record['base_sha256']
        epoch['installed_identities'][name] = claims[name]['identity']
    epoch['counts']['roles'] = len(epoch['pins'])
    epoch['counts']['installed_identities'] = len(epoch['installed_identities'])
    accepted = {}
    for name, record in policy['accepted_current_payloads'].items():
        accepted[name] = claims[name] if name in claims else ownership.claim(ROOT, name, record['sha256'], record['identity'])
        assert accepted[name]['owned_sha256'] == record['sha256'] and accepted[name]['identity'] == record['identity']
    before = state.a.verify_current(state.h, ROOT, env, epoch)
    unaffected_diff = hashlib.sha256(state.h.git(ROOT, env, 'diff', '--binary', '--', '.', *[':(exclude)' + name for name in roles])).hexdigest()
    bundle = load('activation_bundle', policy['bundle_helper'])
    builder = load('activation_builder', policy['phase_helper'])
    process_control = load('activation_process_control', policy['process_helper'])
    wpt = load('activation_wpt', str((HERE / 'wpt.py').relative_to(ROOT)))
    app = ROOT / policy['bundle_path']
    app_before = bundle.scan(app)
    extra_before = {name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}
    assert all(record['kind'] == 'file' for record in extra_before.values())
    assert all(bundle.entry(ROOT / name)['kind'] == 'file' and bundle.entry(ROOT / name)['nlink'] == 1 for name in policy['rebuilt_binaries'])
    assert all(name not in original['installed_identities'] for name in policy['rebuilt_binaries'])
    assert (app / 'Contents/Resources/application.ini').is_symlink()
    assert (app / 'Contents/Resources/application.ini').resolve() == ROOT / 'objdir-full.noindex/build/application.ini'
    size = sum(record['size'] for record in app_before.values() if record['kind'] == 'file') + sum(record['size'] for record in extra_before.values())
    free = lambda: os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize
    assert free() - size >= 27 * 1024**3
    state.save(output / 'BUILD-PRE.json', {'snapshot': before, 'controls': policy['controls'], 'sources': {name: dict(roles[name], identity=claim['identity']) for name, claim in claims.items()}, 'owned_backup_bytes': size})
    state.save(output / 'APP-PRE.json', app_before)
    state.save(output / 'EXTRA-PRE.json', extra_before)
    backups = output / 'backups'
    assert not backups.exists() and not backups.is_symlink()
    backups.mkdir()
    app_mapping = bundle.backup(app, app_before, backups / 'app')
    extra_mapping = bundle.backup(ROOT, extra_before, backups / 'extra')
    backup_snapshot = bundle.scan(backups)
    state.save(output / 'BACKUPS.json', {'app': app_mapping, 'extra': extra_mapping, 'bytes': size, 'owned_inventory': backup_snapshot})
    assert free() >= 27 * 1024**3
    assert bundle.scan(app) == app_before and {name: bundle.entry(ROOT / name) for name in extra_before} == extra_before
    assert state.a.verify_current(state.h, ROOT, env, epoch) == before
    lock = RUNTIME / 'SOURCE-TRANSITION.lock'
    assert not lock.exists() and not lock.is_symlink()
    with lock.open('x') as stream:
        json.dump({'pid': os.getpid(), 'runtime': policy['runtime_output'], 'operation': 'animation-taint-clean-original-v3'}, stream)
    lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
    stopped = [False]
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    owned, errors, restoration_errors = {}, [], []
    failure, phase_result, binaries = None, None, None
    touched = []
    def stable_controls():
        for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
        assert all((RUNTIME / name).read_bytes() == body for name, body in controls.items())
        for name, pin in policy['source_context_pins'].items():
            if name not in roles:
                assert sha(ROOT / name) == pin
        for record in accepted.values():
            if record['path'] not in roles:
                ownership.claim(ROOT, record['path'], record['owned_sha256'], record['identity'])
    def candidate_verify():
        stable_controls()
        local = copy.deepcopy(epoch)
        for name, record in roles.items():
            assert sha(ROOT / name) == record['candidate_sha256']
            local['pins'][name] = record['candidate_sha256']
        local['modified_native_paths'] = sorted(name for name in state.h.git(ROOT, env, 'diff', '--name-only').decode().splitlines() if not name.startswith('artifacts/'))
        assert local['modified_native_paths'] == []
        local['counts']['native_modified_paths'] = len(local['modified_native_paths'])
        assert binaries and set(binaries) == set(policy['rebuilt_binaries'])
        for name, pin in binaries.items():
            assert sha(ROOT / name) == pin
            local['pins'][name] = pin
        assert hashlib.sha256(state.h.git(ROOT, env, 'diff', '--binary', '--', '.', *[':(exclude)' + name for name in roles])).hexdigest() == unaffected_diff
        index = state.h.index_state(ROOT, env)
        assert all(index[key] == epoch['semantic_index'][key] for key in ('head', 'entries', 'cached_diff'))
        local['semantic_index'] = state.h.semantic_index(index)
        local['raw_index_observation']['current'] = index['raw_index']
        verified = state.a.verify_current(state.h, ROOT, env, local)
        assert verified['nested_index'] == before['nested_index']
        for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
        return verified
    try:
        stable_controls()
        for name in roles:
            touched.append(name)
            ownership.write_owned(ROOT, claims[name], candidates[name])
        build = output / 'original-build'
        build.mkdir()
        command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
        state.save(build / 'COMMAND.json', {'command': command, 'source_sha256': {name: sha(ROOT / name) for name in roles}, 'owner_manifest': sys.argv[2]})
        state.save(build / 'PREFLIGHT.json', {'free_bytes': free(), 'start_floor_bytes': 27 * 1024**3, 'running_stop_bytes': 15 * 1024**3, 'owned_backup_bytes': size, 'phase_helper_sha256': sha(ROOT / policy['phase_helper'])})
        deadline = time.monotonic() + policy['timeout_seconds']
        builder.run(ROOT, ROOT / 'objdir-full.noindex', build, env, lambda: stopped[0] or time.monotonic() >= deadline, owned, process_control, command, errors)
        inner = read(build / 'build-RESULT.json')
        assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
        assert not owned and not errors
        binaries = {name: sha(ROOT / name) for name in policy['rebuilt_binaries']}
        verified = candidate_verify()
        state.save(build / 'RESULT.json', {'command_success': True, 'preservation_verified': True, 'snapshot': verified, 'binaries': binaries, 'native_sources': {name: record['candidate_sha256'] for name, record in roles.items()}, 'browser_build_performed': True, 'error': None})
        phases = load('broader_candidate_phases', str((HERE / 'phases.py').relative_to(ROOT)))
        phase_result = phases.run(ROOT, HERE, output, policy, env, candidate_verify, owned, lambda: stopped[0])
    except BaseException as exc:
        failure = repr(exc)
        state.save(output / 'FAILURE-TRACEBACK.json', {'error': failure, 'traceback': traceback.format_exc()})
    finally:
        if owned:
            restoration_errors.append('Owned process groups remain: ' + repr(owned))
        if not restoration_errors:
            try:
                stable_controls()
                for name in reversed(touched):
                    try:
                        ownership.write_owned(ROOT, claims[name], bases[name])
                    except BaseException as exc:
                        restoration_errors.append(name + ': ' + repr(exc))
                app_after = bundle.scan(app)
                extra_after = {name: bundle.entry(ROOT / name) if (ROOT / name).exists() or (ROOT / name).is_symlink() else None for name in extra_before}
                state.save(output / 'APP-BEFORE-RESTORE.json', app_after)
                state.save(output / 'EXTRA-BEFORE-RESTORE.json', extra_after)
                bundle.restore(app, app_before, app_after, backups / 'app', app_mapping)
                for name, old in extra_before.items():
                    current = extra_after[name]
                    if current is None or bundle.semantic({name: current}) != bundle.semantic({name: old}):
                        bundle.restore_file(ROOT / name, current, backups / 'extra' / extra_mapping[name], old, ROOT)
                assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_before)
                assert bundle.semantic({name: bundle.entry(ROOT / name) for name in extra_before}) == bundle.semantic(extra_before)
            except BaseException as exc:
                restoration_errors.append(repr(exc))
        state.save(output / 'RESTORATION.json', {'errors': restoration_errors, 'owned_processes': owned, 'sources': {name: {'sha256': sha(ROOT / name), 'identity': [(ROOT / name).stat().st_dev, (ROOT / name).stat().st_ino]} for name in roles}, 'backup_directory': str(backups)})
    assert not restoration_errors, restoration_errors
    stable_controls()
    for name, record in roles.items():
        ownership.claim(ROOT, name, record["base_sha256"], claims[name]["identity"])
    index = state.h.index_state(ROOT, env)
    assert state.h.semantic_index(index) == original['semantic_index']
    restored = copy.deepcopy(original)
    restored['raw_index_observation']['current'] = index['raw_index']
    after = state.a.verify_current(state.h, ROOT, env, restored)
    expected = copy.deepcopy(original_before)
    expected['index']['raw_index'] = index['raw_index']
    assert after == expected
    for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
        assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
    state.save(output / 'POST.json', after)
    state.save(output / 'RAW-INDEX-OBSERVATION.json', {'before': original_before['index']['raw_index'], 'after': index['raw_index'], 'semantic_index_unchanged': True, 'canonical_updated': False})
    success = failure is None and not errors and phase_result is not None
    if success:
        assert bundle.scan(backups) == backup_snapshot
        shutil.rmtree(backups)
    state.save(output / 'BACKUP-CLEANUP.json', {'removed': success and not backups.exists(), 'verified_original_restoration': True, 'owned_backup_bytes': size, 'retained_after_failure': not success})
    assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
    lock.unlink()
    state.save(output / 'RESULT.json', {'success': success, 'error': failure, 'publication_errors': errors, 'phase': phase_result, 'provider_source_role': policy['provider_source_role'], 'build_revision': policy['head'], 'restoration_verified': True, 'runtime_controls_unchanged': True, 'empty_staging_preserved': True, 'native_fix_acceptance': False, 'full_epoch_copies_saved': 0, 'success_scope': 'build, complete observation and restoration; callback PASS is separate'})
    assert success, failure
    print('Activation paired observation complete; original source and application restored', flush=True)


if __name__ == '__main__':
    main()
