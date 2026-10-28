import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'], 'Disabled pending independent execution review'
assert len(sys.argv) == 2 and sys.argv[1] == policy['runtime_epoch_sha256']
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER'))
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin, name


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('typecheck_state', ROOT / 'artifacts/css-registered-number-native-runtime-v1/state.py')
ownership = load('typecheck_ownership', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
builder = load('typecheck_builder', ROOT / 'artifacts/css-registered-number-native-runtime-v1/phase.py')
control = load('typecheck_process', ROOT / 'artifacts/css-registered-number-native-runtime-v1/process_control.py')
guard = load('typecheck_staged_guard', HERE / 'epoch.py')
projection = load('typecheck_projection', HERE / 'projection.py')
for package, pin in policy['packages'].items():
    ownership.authenticate(ROOT / package, pin)
roles = read(HERE / 'SOURCE-ROLES.json')
assert len(roles) == 4
base = {n: (ROOT / r['base']).read_bytes() for n, r in roles.items()}
candidate = {n: (ROOT / r['candidate']).read_bytes() for n, r in roles.items()}
assert all(hashlib.sha256(base[n]).hexdigest() == r['base_sha256'] and hashlib.sha256(candidate[n]).hexdigest() == r['candidate_sha256'] for n, r in roles.items())
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {n: (runtime / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == policy['runtime_epoch_sha256']
assert hashlib.sha256(controls['ROLE.json']).hexdigest() == policy['role_sha256']
assert hashlib.sha256(controls['OWNED.json']).hexdigest() == policy['owned_sha256']
original = json.loads(controls['CURRENT-EPOCH.json'])
assert original['semantic_index']['head'] == policy['head']
staging = read(HERE / 'STAGING.json')
observed = state.h.index_state(ROOT, ENV)
epoch = projection.derive(original, observed, state.h.git(ROOT, ENV, 'ls-files', '--stage', '-z'), staging)
before = guard.verify_current(state.h, ROOT, ENV, epoch)
assert before['nested_index'] == read(ROOT / 'artifacts/css-local-signing-20261028-v33/BEFORE.json')['nested_index']
flags = {n: state.h.git(path, ENV, 'ls-files', '-v', '-z') for n, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
claims = {n: ownership.claim(ROOT, n, r['base_sha256']) for n, r in roles.items()}
wpt_claims = {n: ownership.claim(ROOT, n, r['sha256'], r['identity']) for n, r in policy['installed_wpt'].items()}
for n, r in policy['installed_wpt'].items():
    assert sha(ROOT / r['source']) == r['sha256']
    assert not state.h.git(ROOT, ENV, 'ls-files', '--stage', '--', n)
control_claims = {n: ownership.claim(ROOT, str((runtime / n).relative_to(ROOT)), hashlib.sha256(body).hexdigest()) for n, body in controls.items()}
output = ROOT / policy['runtime_output']
assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
lock = runtime / 'SOURCE-TRANSITION.lock'
assert not lock.exists() and not lock.is_symlink()
sys.path[:0] = [str(ROOT / 'python/mozbuild'), str(ROOT / 'testing/mozbase/mozshellutil')]
from mozbuild.rust_commands import CargoInvocation, compose_env, compose_mach_cargo_argv, load_cargo_spec
spec_path = ROOT / 'objdir-full.noindex/toolkit/library/rust/.cargo-library-spec.json'
assert sha(spec_path) == policy['configured_spec_sha256']
assert sha(ROOT / 'python/mozbuild/mozbuild/rust_commands.py') == policy['cargo_composition_sha256']
command, substs, src, obj = load_cargo_spec(read(spec_path))
assert src == str(ROOT) and obj == str(ROOT / 'objdir-full.noindex')
invocation = CargoInvocation.from_environ(ENV)
argv = compose_mach_cargo_argv(command, substs, invocation, 'check', extra_cli_flags=('--offline',), jobs=2, auto_args=True)
env = compose_env(command, substs, ENV, invocation, src, obj, ltoable=True, subcommand='check')
assert env['CARGO_TARGET_DIR'] == obj
assert os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize >= 35 * 1024**3
ownership.quiescent(runtime)
assert guard.verify_current(state.h, ROOT, ENV, epoch) == before
for claim in list(claims.values()) + list(wpt_claims.values()) + list(control_claims.values()):
    ownership.claim(ROOT, claim['path'], claim['owned_sha256'], claim['identity'])
assert all((runtime / n).read_bytes() == body for n, body in controls.items())
output.mkdir()
state.save(output / 'PRE.json', before)
state.save(output / 'OBSERVATION-EPOCH.json', epoch)
for name, body in controls.items():
    (output / ('PRE-' + name)).write_bytes(body)
state.save(output / 'COMMAND.json', {'argv': argv, 'cwd': command.working_directory, 'configured_spec_sha256': sha(spec_path), 'composition_sha256': policy['cargo_composition_sha256'], 'target_directory': obj, 'scope': policy['execution_scope']})
cancelled = [False]
def stop(signum, frame):
    cancelled[0] = True
for signum in (signal.SIGTERM, signal.SIGINT):
    signal.signal(signum, stop)
owned, publication_errors, restoration_errors = {}, [], []
error = None
with lock.open('x') as stream:
    stream.write(json.dumps({'pid': os.getpid(), 'runtime': str(output.relative_to(ROOT))}) + '\n')
lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
try:
    assert guard.verify_current(state.h, ROOT, ENV, epoch) == before
    for n in roles:
        ownership.write_owned(ROOT, claims[n], candidate[n])
    state.save(output / 'INSTALLED.json', {n: sha(ROOT / n) for n in roles})
    assert all(sha(ROOT / n) == r['candidate_sha256'] for n, r in roles.items())
    assert state.h.git(ROOT, ENV, 'diff', '--cached', '--binary', '--full-index', policy['head']) == (ROOT / 'artifacts/css-local-signing-20261028-v33/random-staged.patch').read_bytes()
    deadline = time.monotonic() + policy['timeout_seconds']
    builder.run(Path(command.working_directory), Path(obj), output, env, lambda: cancelled[0] or time.monotonic() >= deadline, owned, control, argv, publication_errors)
except BaseException as exc:
    error = repr(exc)
finally:
    if owned:
        restoration_errors.append('Owned compiler groups remain; restoration deferred')
    else:
        for n in reversed(roles):
            try:
                ownership.write_owned(ROOT, claims[n], base[n])
            except BaseException as exc:
                restoration_errors.append(n + ': ' + repr(exc))
    state.save(output / 'RESTORATION.json', {'errors': restoration_errors, 'owned_processes': owned, 'source_hashes': {n: sha(ROOT / n) for n in roles}})
assert not restoration_errors, restoration_errors
assert all((runtime / n).read_bytes() == body for n, body in controls.items())
after_index = state.h.index_state(ROOT, ENV)
assert state.h.semantic_index(after_index) == epoch['semantic_index']
post_epoch = copy.deepcopy(epoch)
post_epoch['raw_index_observation']['current'] = after_index['raw_index']
after = guard.verify_current(state.h, ROOT, ENV, post_epoch)
assert after['nested_index'] == before['nested_index']
for n, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert state.h.git(path, ENV, 'ls-files', '-v', '-z') == flags[n]
for claim in list(claims.values()) + list(wpt_claims.values()) + list(control_claims.values()):
    ownership.claim(ROOT, claim['path'], claim['owned_sha256'], claim['identity'])
assert all(sha(ROOT / n) == r['base_sha256'] for n, r in roles.items())
state.save(output / 'POST.json', after)
state.save(output / 'POST-OBSERVATION-EPOCH.json', post_epoch)
state.save(output / 'RAW-INDEX-OBSERVATION.json', {'before': observed['raw_index'], 'after': after_index['raw_index'], 'changed': observed['raw_index'] != after_index['raw_index'], 'semantic_index_unchanged': True, 'runtime_epoch_updated': False, 'signing_resume_requires_fresh_guard': True})
assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
lock.unlink()
state.save(output / 'RESULT.json', {'success': error is None and not publication_errors, 'error': error, 'publication_errors': publication_errors, 'source_restored': True, 'preservation_verified': True, 'staged165_preserved': True, 'nested_index_and_flags_preserved': True, 'runtime_controls_unchanged': True, 'browser_build_performed': False, 'browser_tests_performed': False, 'new_target_directory_created': False, 'owned_processes': owned})
print('Configured Rust typecheck completed; four sources restored and staged research preserved', flush=True)
assert error is None and not publication_errors, error
