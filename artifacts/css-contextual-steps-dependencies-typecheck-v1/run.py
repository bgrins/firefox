import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
PROPOSAL = ROOT / 'artifacts/css-contextual-steps-dependencies-prototype-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('retention_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
ownership = load('retention_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
builder = load('retention_builder', 'artifacts/css-registered-number-native-runtime-v1/phase.py')
control = load('retention_process', 'artifacts/css-registered-number-native-runtime-v1/process_control.py')
assert not any(os.environ.get(k) for k in ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER'])
ownership.authenticate(PROPOSAL, 'cbf862fb7e572fe4ced216db4bfda5033848b43a1b96b7360dddefe36dd6598b')
controls = {n:(RUNTIME / n).read_bytes() for n in ['CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json']}
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == 'd8bc423d8de5c7a5e5e0cbaa6083132ae1794dbf22d535b1d397d6f8751c89c8'
for name, body in controls.items():
    (HERE / ('PRE-' + name)).write_bytes(body)
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == '0197d1c8e8fd678680d78b212f6a2c0ae9d82d51'
assert epoch['staged_working'] == {}
ownership.quiescent(RUNTIME)
lock = RUNTIME / 'SOURCE-TRANSITION.lock'
assert not lock.exists()
before = state.a.verify_current(state.h, ROOT, ENV, epoch)
state.save(HERE / 'PRE.json', before)
names = list(read(PROPOSAL / 'SOURCE-ROLES.json'))
claims = {n:ownership.claim(ROOT, n, sha(PROPOSAL / 'base' / n)) for n in names}
assert all((ROOT / n).read_bytes() == (PROPOSAL / 'base' / n).read_bytes() for n in names)
sys.path[:0] = [str(ROOT / 'python/mozbuild'), str(ROOT / 'testing/mozbase/mozshellutil')]
from mozbuild.rust_commands import CargoInvocation, compose_env, compose_mach_cargo_argv, load_cargo_spec

spec_path = ROOT / 'objdir-full.noindex/toolkit/library/rust/.cargo-library-spec.json'
command, substs, src, obj = load_cargo_spec(read(spec_path))
assert src == str(ROOT) and obj == str(ROOT / 'objdir-full.noindex')
invocation = CargoInvocation.from_environ(ENV)
argv = compose_mach_cargo_argv(command, substs, invocation, 'check',
    extra_cli_flags=('--offline',), jobs=2, auto_args=True)
env = compose_env(command, substs, ENV, invocation, src, obj, ltoable=True, subcommand='check')
assert env['CARGO_TARGET_DIR'] == obj
state.save(HERE / 'COMMAND.json', {'argv':argv, 'cwd':command.working_directory,
    'configured_spec_sha256':sha(spec_path), 'composition_sha256':sha(ROOT / 'python/mozbuild/mozbuild/rust_commands.py'),
    'target_directory':obj, 'scope':'Configured Firefox Rust graph typecheck; not a linked browser build'})
cancelled = [False]
def stop(signum, frame):
    cancelled[0] = True
for signum in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(signum, stop)
owned, publication_errors = {}, []
error = None
restoration_errors = []
with lock.open('x') as stream:
    stream.write(json.dumps({'pid':os.getpid(), 'runtime':str(HERE.relative_to(ROOT))})+'\n')
lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
try:
    for n in names:
        ownership.write_owned(ROOT, claims[n], (PROPOSAL / 'candidate' / n).read_bytes())
    assert all((ROOT / n).read_bytes() == (PROPOSAL / 'candidate' / n).read_bytes() for n in names)
    state.save(HERE / 'INSTALLED.json', {n:sha(ROOT / n) for n in names})
    deadline = time.monotonic() + 1800
    builder.run(Path(command.working_directory), Path(obj), HERE, env,
        lambda: cancelled[0] or time.monotonic() >= deadline, owned, control, argv, publication_errors)
except BaseException as exc:
    error = repr(exc)
finally:
    if owned:
        restoration_errors.append('Owned compiler processes remain; source restoration deferred')
    else:
        for n in reversed(names):
            try:
                ownership.write_owned(ROOT, claims[n], (PROPOSAL / 'base' / n).read_bytes())
            except BaseException as exc:
                restoration_errors.append(n+': '+repr(exc))
    if not restoration_errors:
        assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
        lock.unlink()
    state.save(HERE / 'RESTORATION.json', {'errors':restoration_errors, 'owned_processes':owned,
        'source_hashes':{n:sha(ROOT / n) for n in names}})
assert not restoration_errors, restoration_errors
assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
observed = state.h.index_state(ROOT, ENV)
assert state.h.semantic_index(observed) == epoch['semantic_index']
current = copy.deepcopy(epoch)
current['raw_index_observation']['current'] = observed['raw_index']
drift = observed['raw_index'] != epoch['raw_index_observation']['current']
if drift:
    current['raw_index_observation']['prior_comparison_raw_drift_cause'] = 'unknown; semantic staging and working diff preserved after temporary source overlay'
state.save(HERE / 'RAW-INDEX-OBSERVATION.json', {'before':epoch['raw_index_observation']['current'],
    'after':observed['raw_index'], 'changed':drift, 'semantic_index_unchanged':True, 'cause':'not established' if drift else None})
after = state.a.verify_current(state.h, ROOT, ENV, current)
state.save(HERE / 'POST.json', after)
state.save(HERE / 'POST-EPOCH.json', current)
if drift:
    path = RUNTIME / 'CURRENT-EPOCH.json'
    claim = ownership.claim(ROOT, str(path.relative_to(ROOT)), hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest())
    ownership.write_owned(ROOT, claim, ownership.encoded(current))
assert all((RUNTIME / n).read_bytes() == controls[n] for n in ['ROLE.json', 'OWNED.json'])
state.save(HERE / 'RESULT.json', {'success':error is None and not publication_errors,
    'error':error, 'publication_errors':publication_errors, 'source_restored':True,
    'role_and_owned_unchanged':True, 'runtime_epoch_raw_index_updated':drift, 'preservation_verified':True,
    'browser_build_performed':False, 'browser_tests_performed':False,
    'new_target_directory_created':False})
print('Typecheck finished; sources and browser binary preserved', flush=True)
assert error is None and not publication_errors, error
