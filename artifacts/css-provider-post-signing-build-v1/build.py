import copy
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
CAPSULE = Path(__file__).resolve().parent
ROOT = CAPSULE.parents[1]
manifest, expected_epoch = sys.argv[1:]
policy = json.loads((CAPSULE / 'POLICY.json').read_text())
settings = json.loads((CAPSULE / 'BUILD-POLICY.json').read_text())
assert settings['execution_enabled'] is True, 'Disabled until sealed v5 transition and reviewed successor'
HERE = ROOT / policy['runtime']
spec = importlib.util.spec_from_file_location('staged_build_state', HERE / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ownership = s.load('build_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
ownership.authenticate(CAPSULE, manifest)
for name, pin in json.loads((CAPSULE / 'REFERENCES.json').read_text()).items():
    assert s.sha(ROOT / name) == pin
succession = s.load('provider_build_succession', str((CAPSULE / 'succession.py').relative_to(ROOT)))
OBJ = ROOT / 'objdir-full.noindex'
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(OBJ), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           PYTHONDONTWRITEBYTECODE='1')
assert all(not os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'))
label = settings['label']
assert label == 'provider-default-candidate-build-3'
controls = {n: ownership.body(HERE / n) for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
assert ownership.digest(controls['CURRENT-EPOCH.json']) == expected_epoch == settings['expected_epoch_sha256']
epoch = json.loads(controls['CURRENT-EPOCH.json'])
role = json.loads(controls['ROLE.json'])
assert role['role'] == 'candidate' and role['variant'] == settings['expected_variant'] and role['built'] is False
assert epoch['registered_number_transition']['variant'] == settings['expected_variant']
assert epoch['registered_number_transition']['compiled'] is False and epoch['registered_number_transition']['accepted'] is False
assert epoch['registered_number_transition']['last_phase'] == settings['expected_last_transition']
assert settings['source_pins'] and settings['source_pins'] == {n: epoch['pins'][n] for n in epoch['modified_native_paths']}
assert epoch['semantic_index']['head'] == policy['head']
transition = ROOT / settings['transition_output']
succession.validate(ROOT, CAPSULE, policy, epoch, s.h, env)
installed = json.loads((transition / 'RESULT.json').read_text())
assert installed['installed'] and installed['preservation_verified']
assert installed['compiled'] is False and installed['accepted'] is False
assert installed['native_changes'] == 2 and installed['modified_native_paths'] == 1 and installed['staged_paths'] == 36
assert installed['epoch_sha256'] == settings['transition_epoch_sha256']
assert epoch['staged_working'] == {}
assert ownership.digest(controls['ROLE.json']) == settings['role_sha256']
assert ownership.digest(controls['OWNED.json']) == settings['owned_sha256']
claims = {n: ownership.claim(ROOT, str((HERE/n).relative_to(ROOT)), ownership.digest(body)) for n, body in controls.items()}
ownership.quiescent(HERE)
assert not os.path.lexists(HERE / 'SOURCE-TRANSITION.lock')
before = s.a.verify_current(s.h, ROOT, env, epoch)
directory = HERE / label
assert not os.path.lexists(directory) and not HERE.is_symlink()
directory.mkdir()
s.save(directory / 'PRE.json', before)
for name, body in controls.items():
    (directory / ('PRE-' + name)).write_bytes(body)
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
builder = s.load('fallback_builder', str((HERE / 'phase.py').relative_to(ROOT)))
control = s.load('fallback_control', str((HERE / 'process_control.py').relative_to(ROOT)))
flags = {name: s.h.git(ROOT / name, env, 'ls-files', '-v', '-z') for name in ('.', 'artifacts/css-spec-lean')}
state, publication_errors = {}, []
stopped = [False]
def stop(signum, frame):
    stopped[0] = True
for sig in (signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, stop)
deadline = time.monotonic() + 1800
ownership.authenticate(CAPSULE, manifest)
succession.validate(ROOT, CAPSULE, policy, epoch, s.h, env)
assert s.a.verify_current(s.h, ROOT, env, epoch) == before
assert all(s.h.git(ROOT / name, env, 'ls-files', '-v', '-z') == body for name, body in flags.items())
for item in claims.values():
    ownership.claim(ROOT, item['path'], item['owned_sha256'], item['identity'])
ownership.quiescent(HERE)
assert not os.path.lexists(HERE / 'SOURCE-TRANSITION.lock')
error = None
try:
    s.save(directory / 'COMMAND.json', {'command': command, 'pid': os.getpid(), 'source_role': role['role']})
    builder.run(ROOT, OBJ, directory, env, lambda: stopped[0] or time.monotonic() >= deadline,
                state, control, command, publication_errors)
except BaseException as exc:
    error = repr(exc)
try:
    assert not state, 'Owned build group remains; do not mutate sources'
    assert all((HERE / n).read_bytes() == body for n, body in controls.items())
    current = copy.deepcopy(epoch)
    for name in ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
                 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
                 'objdir-full.noindex/dist/bin/gtest/XUL']:
        assert name in current['pins']
        current['pins'][name] = s.h.fingerprint(ROOT, name)
    index = s.h.index_state(ROOT, env)
    assert s.h.semantic_index(index) == epoch['semantic_index']
    current['raw_index_observation']['current'] = index['raw_index']
    after = s.a.verify_current(s.h, ROOT, env, current)
    assert all(s.h.git(ROOT / name, env, 'ls-files', '-v', '-z') == body for name, body in flags.items())
    success = error is None and not publication_errors
    current['registered_number_transition'] = {'role': role['role'], 'variant': role['variant'], 'compiled': success, 'last_phase': label, 'accepted': False}
    s.save(directory / 'POST.json', after)
    s.save(directory / 'EPOCH.json', current)
    ownership.write_owned(ROOT, claims['CURRENT-EPOCH.json'], ownership.encoded(current))
    role['built'] = success
    role['last_build'] = label
    ownership.write_owned(ROOT, claims['ROLE.json'], ownership.encoded(role))
    assert (HERE / 'OWNED.json').read_bytes() == controls['OWNED.json']
    assert s.a.verify_current(s.h, ROOT, env, current) == after
    s.save(directory / 'RESULT.json', {'command_success': success, 'error': error, 'publication_errors': publication_errors,
                                     'owned_processes': state, 'source_role': role['role'], 'preservation_verified': True})
except BaseException as publication_error:
    s.save(directory / 'PUBLICATION-FAILURE.json', {
        'error': repr(publication_error), 'command_error': error,
        'owned_processes': state, 'publication_errors': publication_errors,
        'manual_recovery_required': True, 'compiled_state_certified': False,
        'note': 'Do not restore old binary hashes; inspect saved controls and actual produced binaries.'})
    raise
print(label, 'success' if success else error, flush=True)
assert success
