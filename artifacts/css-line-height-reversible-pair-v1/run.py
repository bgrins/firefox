import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'], 'Disabled reversible experiment preparation'
assert len(sys.argv) == 3 and sys.argv[1] == policy['runtime_epoch_sha256']
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'MOZ_ARTIFACT_BUILDS', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_PROFILE'))
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin, name


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('pair_state', ROOT / 'artifacts/css-registered-number-native-runtime-v1/state.py')
ownership = load('pair_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
builder = load('pair_builder', ROOT / 'artifacts/css-registered-number-native-runtime-v1/phase.py')
control = load('pair_control', ROOT / 'artifacts/css-registered-number-native-runtime-v1/process_control.py')
guard = load('pair_staged_guard', HERE / 'epoch.py')
projection = load('pair_projection', HERE / 'projection.py')
bundle = load('pair_bundle', HERE / 'bundle.py')
wpt_cleanup = load('pair_wpt_cleanup', HERE / 'wpt_cleanup.py')
ownership.authenticate(HERE, sys.argv[2])
ownership.authenticate(ROOT / policy['source_package'], policy['source_manifest'])
ownership.authenticate(ROOT / policy['wpt_package'], policy['wpt_manifest'])
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {n: (runtime / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == policy['runtime_epoch_sha256']
assert hashlib.sha256(controls['ROLE.json']).hexdigest() == policy['role_sha256']
assert hashlib.sha256(controls['OWNED.json']).hexdigest() == policy['owned_sha256']
original = json.loads(controls['CURRENT-EPOCH.json'])
assert original['semantic_index']['head'] == policy['head']
observed = state.h.index_state(ROOT, ENV)
epoch = projection.derive(original, observed, state.h.git(ROOT, ENV, 'ls-files', '--stage', '-z'), read(HERE / 'STAGING.json'))
source = policy['source_path']
base = (ROOT / policy['source_package'] / 'base' / source).read_bytes()
candidate = (ROOT / policy['source_package'] / 'candidate' / source).read_bytes()
assert hashlib.sha256(base).hexdigest() == policy['source_roles']['base_sha256']
assert hashlib.sha256(candidate).hexdigest() == policy['source_roles']['candidate_sha256']
assert hashlib.sha256(state.h.git(ROOT, ENV, 'show', policy['head'] + ':' + source)).hexdigest() == policy['source_roles']['base_sha256']
source_claim = ownership.claim(ROOT, source, policy['source_roles']['base_sha256'])
epoch['pins'][source] = policy['source_roles']['base_sha256']
epoch['installed_identities'][source] = source_claim['identity']
epoch['counts']['roles'] = len(epoch['pins'])
epoch['counts']['installed_identities'] = len(epoch['installed_identities'])
epoch['counts']['staged_payloads'] = len(epoch['staged_working'])
before = guard.verify_current(state.h, ROOT, ENV, epoch)
assert sorted(state.h.git(ROOT, ENV, 'diff', '--name-only').decode().splitlines()) == sorted(epoch['modified_native_paths'])
assert before['nested_index'] == read(ROOT / 'artifacts/css-local-signing-20261028-v33/BEFORE.json')['nested_index']
flags = {n: state.h.git(path, ENV, 'ls-files', '-v', '-z') for n, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
control_claims = {n: ownership.claim(ROOT, str((runtime / n).relative_to(ROOT)), hashlib.sha256(body).hexdigest()) for n, body in controls.items()}
wpt_claims = {n: ownership.claim(ROOT, n, r['sha256'], r['identity']) for n, r in policy['installed_wpt'].items()}
for n, r in policy['installed_wpt'].items():
    assert sha(ROOT / r['source']) == r['sha256'] and not state.h.git(ROOT, ENV, 'ls-files', '--stage', '--', n)
assert set(policy['rebuilt_binaries']) == {
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
    'objdir-full.noindex/dist/bin/gtest/XUL',
}
app = ROOT / policy['bundle_path']
app_before = bundle.scan(app)
extra_before = {n: bundle.entry(ROOT / n) for n in policy['extra_backup_paths']}
assert all(r['kind'] == 'file' for r in extra_before.values())
assert all(n not in original['installed_identities'] for n in policy['rebuilt_binaries'])
assert all(bundle.entry(ROOT / n)['kind'] == 'file' and bundle.entry(ROOT / n)['nlink'] == 1 for n in policy['rebuilt_binaries'])
assert (app / 'Contents/Resources/application.ini').is_symlink()
assert (app / 'Contents/Resources/application.ini').resolve() == ROOT / 'objdir-full.noindex/build/application.ini'
backup_size = sum(r['size'] for r in app_before.values() if r['kind'] == 'file') + sum(r['size'] for r in extra_before.values())
free = lambda: os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize
assert free() - backup_size >= 35 * 1024**3
output = ROOT / policy['runtime_output']
assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
bundle.parents(ROOT, output)
lock = runtime / 'SOURCE-TRANSITION.lock'
assert not lock.exists() and not lock.is_symlink()
ownership.quiescent(runtime)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
assert guard.verify_current(state.h, ROOT, ENV, epoch) == before
output.mkdir()
for n, body in controls.items():
    (output / ('PRE-' + n)).write_bytes(body)
state.save(output / 'PRE.json', before)
state.save(output / 'PRE-OBSERVATION-EPOCH.json', epoch)
state.save(output / 'APP-PRE.json', app_before)
state.save(output / 'EXTRA-PRE.json', extra_before)
backups = output / 'backups'
backups.mkdir()
app_mapping = bundle.backup(app, app_before, backups / 'app')
extra_mapping = bundle.backup(ROOT, extra_before, backups / 'extra')
backup_snapshot = bundle.scan(backups)
state.save(output / 'BACKUPS.json', {'app': app_mapping, 'extra': extra_mapping, 'bytes': backup_size, 'owned_inventory': backup_snapshot})
assert free() >= 35 * 1024**3
assert bundle.scan(app) == app_before and {n: bundle.entry(ROOT / n) for n in extra_before} == extra_before
assert guard.verify_current(state.h, ROOT, ENV, epoch) == before
cancelled = [False]
def stop(signum, frame):
    cancelled[0] = True
for signum in (signal.SIGTERM, signal.SIGINT):
    signal.signal(signum, stop)
owned, publication_errors, restoration_errors = {}, [], []
error = None
active_wpt = None
active_role = None
active_process = None
wpt_cleanup_receipt = None
phase_results = {}
with lock.open('x') as stream:
    stream.write(json.dumps({'pid': os.getpid(), 'runtime': str(output.relative_to(ROOT))}) + '\n')
lock_identity = (lock.stat().st_dev, lock.stat().st_ino)


def unchanged_controls():
    assert all((runtime / n).read_bytes() == body for n, body in controls.items())
    for claim in list(control_claims.values()) + list(wpt_claims.values()):
        ownership.claim(ROOT, claim['path'], claim['owned_sha256'], claim['identity'])


def local_epoch(role, directory):
    local = copy.deepcopy(epoch)
    local['pins'][source] = policy['source_roles']['base_sha256' if role == 'original' else 'candidate_sha256']
    local['modified_native_paths'] = sorted(set(epoch['modified_native_paths']) | ({source} if role == 'candidate' else set()))
    local['counts']['native_modified_paths'] = len(local['modified_native_paths'])
    for name in policy['rebuilt_binaries']:
        local['pins'][name] = state.h.fingerprint(ROOT, name)
    assert sha(ROOT / source) == local['pins'][source]
    assert sorted(state.h.git(ROOT, ENV, 'diff', '--name-only').decode().splitlines()) == local['modified_native_paths']
    assert hashlib.sha256(state.h.git(ROOT, ENV, 'diff', '--binary', '--', '.', ':(exclude)' + source)).hexdigest() == epoch['semantic_index']['working_diff']
    index = state.h.index_state(ROOT, ENV)
    if role == 'original':
        assert index['working_diff'] == epoch['semantic_index']['working_diff']
    assert all(index[k] == epoch['semantic_index'][k] for k in ('head', 'entries', 'cached_diff'))
    local['semantic_index'] = state.h.semantic_index(index)
    local['raw_index_observation']['current'] = index['raw_index']
    local['reversible_line_height_phase'] = {'role': role, 'build_directory': str(directory.relative_to(ROOT)), 'source_package_manifest': policy['source_manifest'], 'owner_runtime': policy['runtime_output']}
    guard.verify_current(state.h, ROOT, ENV, local)
    for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
        assert state.h.git(path, ENV, 'ls-files', '-v', '-z') == flags[name]
    unchanged_controls()
    return local


try:
    for role in ('original', 'candidate'):
        assert not cancelled[0]
        unchanged_controls()
        if role == 'candidate':
            ownership.write_owned(ROOT, source_claim, candidate)
        directory = output / (role + '-build')
        directory.mkdir()
        command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
        state.save(directory / 'COMMAND.json', {'command': command, 'source_role': role, 'source_sha256': sha(ROOT / source), 'owner_manifest': sys.argv[2]})
        deadline = time.monotonic() + policy['timeout_seconds']
        builder.run(ROOT, ROOT / 'objdir-full.noindex', directory, ENV, lambda: cancelled[0] or time.monotonic() >= deadline, owned, control, command, publication_errors)
        assert not owned and not publication_errors
        current = local_epoch(role, directory)
        state.save(directory / 'EPOCH.json', current)
        state.save(directory / 'RESULT.json', {'command_success': True, 'preservation_verified': True, 'source_role': role, 'owned_processes': {}, 'error': None, 'publication_errors': [], 'browser_build_performed': True})
        active_wpt = output / (role + '-wpt')
        active_role = role
        active_process = None
        wpt_cleanup_receipt = None
        command = [sys.executable, '-I', '-S', '-B', str(ROOT / policy['wpt_package'] / 'run.py'), policy['wpt_manifest'], role + '-1', str(directory / 'EPOCH.json'), sha(directory / 'EPOCH.json'), str(active_wpt)]
        with (output / (role + '-wpt-driver.log')).open('x') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            active_process = process
            owned['wpt_wrapper'] = process.pid
            try:
                deadline = time.monotonic() + 900
                while process.poll() is None:
                    assert not cancelled[0] and time.monotonic() < deadline, 'WPT wrapper cancelled or timed out'
                    time.sleep(0.2)
                code = process.wait()
            finally:
                wpt_cleanup_receipt = wpt_cleanup.finish(process, active_wpt, role, policy, control)
                if wpt_cleanup_receipt['restoration_safe']:
                    owned.pop('wpt_wrapper')
                state.save(output / (role + '-WRAPPER-CLEANUP.json'), wpt_cleanup_receipt)
        cleanup = read(active_wpt / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        ownership.group_absent(read(active_wpt / 'PROCESS.json')['pgid'])
        assessment = read(active_wpt / 'ASSESSMENT.json')
        phase_results[role] = {'wrapper_exit': code, 'assessment_sha256': sha(active_wpt / 'ASSESSMENT.json')}
        assert code == 0 and assessment['complete'] and assessment['execution_preserved']
        active_wpt = None
        unchanged_controls()
except BaseException as exc:
    error = repr(exc)
finally:
    if active_wpt is not None:
        try:
            if wpt_cleanup_receipt is None:
                wpt_cleanup_receipt = wpt_cleanup.finish(active_process, active_wpt, active_role, policy, control)
                if wpt_cleanup_receipt['restoration_safe']:
                    owned.pop('wpt_wrapper', None)
                state.save(output / (active_role + '-RECOVERY-CLEANUP.json'), wpt_cleanup_receipt)
            assert wpt_cleanup_receipt['restoration_safe']
        except BaseException as exc:
            restoration_errors.append('WPT cleanup not certified: ' + repr(exc))
    if owned:
        restoration_errors.append('Owned process groups remain: ' + repr(owned))
    if not restoration_errors:
        try:
            unchanged_controls()
            ownership.write_owned(ROOT, source_claim, base)
            app_after = bundle.scan(app)
            extra_after = {n: bundle.entry(ROOT / n) if (ROOT / n).exists() or (ROOT / n).is_symlink() else None for n in extra_before}
            state.save(output / 'APP-BEFORE-RESTORE.json', app_after)
            state.save(output / 'EXTRA-BEFORE-RESTORE.json', extra_after)
            bundle.restore(app, app_before, app_after, backups / 'app', app_mapping)
            for name, old in extra_before.items():
                current_entry = extra_after[name]
                if current_entry is None or bundle.semantic({name: current_entry}) != bundle.semantic({name: old}):
                    bundle.restore_file(ROOT / name, current_entry, backups / 'extra' / extra_mapping[name], old, ROOT)
            assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_before)
            assert bundle.semantic({n: bundle.entry(ROOT / n) for n in extra_before}) == bundle.semantic(extra_before)
        except BaseException as exc:
            restoration_errors.append(repr(exc))
    state.save(output / 'RESTORATION.json', {'errors': restoration_errors, 'owned_processes': owned, 'source_sha256': sha(ROOT / source), 'backup_directory': str(backups)})
assert not restoration_errors, restoration_errors
unchanged_controls()
after_index = state.h.index_state(ROOT, ENV)
assert state.h.semantic_index(after_index) == epoch['semantic_index']
post_epoch = copy.deepcopy(epoch)
post_epoch['raw_index_observation']['current'] = after_index['raw_index']
after = guard.verify_current(state.h, ROOT, ENV, post_epoch)
assert after['nested_index'] == before['nested_index']
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert state.h.git(path, ENV, 'ls-files', '-v', '-z') == flags[name]
state.save(output / 'POST.json', after)
state.save(output / 'POST-OBSERVATION-EPOCH.json', post_epoch)
state.save(output / 'RAW-INDEX-OBSERVATION.json', {'before': observed['raw_index'], 'after': after_index['raw_index'], 'semantic_index_unchanged': True, 'cause': 'unknown' if observed['raw_index'] != after_index['raw_index'] else None, 'runtime_epoch_updated': False})
assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
cleanup_backups = error is None and not publication_errors and set(phase_results) == {'original', 'candidate'}
if cleanup_backups:
    assert bundle.scan(backups) == backup_snapshot
    shutil.rmtree(backups)
state.save(output / 'BACKUP-CLEANUP.json', {'removed': cleanup_backups and not backups.exists(), 'verified_original_restoration': True, 'owned_backup_bytes': backup_size, 'inventory_sha256': sha(output / 'BACKUPS.json'), 'retained_after_experiment_failure': not cleanup_backups})
lock.unlink()
state.save(output / 'RESULT.json', {'success': error is None and not publication_errors and set(phase_results) == {'original', 'candidate'}, 'error': error, 'publication_errors': publication_errors, 'phase_results': phase_results, 'restoration_verified': True, 'runtime_controls_unchanged': True, 'staged165_preserved': True, 'backups_removed_after_verification': not backups.exists(), 'native_fix_acceptance': False})
assert error is None and not publication_errors, error
print('Paired linked-browser experiment completed and original source/application restored', flush=True)
