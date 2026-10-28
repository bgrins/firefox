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
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
HERE = ROOT / 'artifacts/css-page-selector-native-runtime-v1'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
spec = importlib.util.spec_from_file_location('fallback_state', RUNTIME / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = s.ROOT
OBJ = ROOT / 'objdir-full.noindex'
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(OBJ), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           PYTHONDONTWRITEBYTECODE='1')
assert all(not os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'))
label, expected_epoch, manifest = sys.argv[1:]
assert s.sha(RUNTIME / "CURRENT-EPOCH.json") == expected_epoch
assert '/' not in label
epoch = s.read(RUNTIME / 'CURRENT-EPOCH.json')
assert epoch['page_selector_transition']['role'] == 'candidate' and not epoch['page_selector_transition']['compiled']
assert epoch['semantic_index']['head'] == 'e543a02df7141b4899b9d113703cdc5b0c2ed2dd'
assert label == 'candidate-build-1'
role = {'role': 'candidate', 'variant': 'page-selector-name-filter'}
owner = s.load('page_build_ownership', 'artifacts/css-registered-number-source-transition-v4/transition.py')
owner.authenticate(PACKAGE, manifest)
policy = s.read(PACKAGE / 'POLICY.json')
assert epoch['page_selector_transition']['manifest_sha256'] == manifest
for name, record in policy['sources'].items(): assert epoch['pins'][name] == record['candidate_sha256']
for name, pin in policy['references'].items(): assert s.sha(ROOT/name) == pin
control_claims = {n:owner.claim(ROOT,str((RUNTIME/n).relative_to(ROOT)),s.sha(RUNTIME/n)) for n in ['ROLE.json','OWNED.json']}
owner.quiescent(RUNTIME)
epoch_claim = owner.claim(ROOT, str((RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), expected_epoch)
before = s.a.verify_current(s.h, ROOT, env, epoch)
directory = HERE / label
directory.mkdir()
s.save(directory / 'PRE.json', before)
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
s.save(directory / 'COMMAND.json', {'command': command, 'pid': os.getpid(), 'source_role': role['role']})
builder = s.load('fallback_builder', str((RUNTIME / 'phase.py').relative_to(ROOT)))
control = s.load('fallback_control', str((RUNTIME / 'process_control.py').relative_to(ROOT)))
flags = {name: s.h.git(ROOT / name, env, 'ls-files', '-v', '-z') for name in ('.', 'artifacts/css-spec-lean')}
state, publication_errors = {}, []
stopped = [False]
def stop(signum, frame):
    stopped[0] = True
for sig in (signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, stop)
deadline = time.monotonic() + 1800
error = None
try:
    builder.run(ROOT, OBJ, directory, env, lambda: stopped[0] or time.monotonic() >= deadline,
                state, control, command, publication_errors)
except BaseException as exc:
    error = repr(exc)
assert not state, 'Owned build group remains; do not mutate sources'
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
current['page_selector_transition'] = {'role': role['role'], 'variant': role['variant'], 'compiled': success, 'last_phase': label, 'accepted': False}
owner.authenticate(PACKAGE, manifest)
for name, pin in policy['references'].items(): assert s.sha(ROOT/name) == pin
for item in control_claims.values(): owner.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
s.save(directory / 'POST.json', after)
s.save(directory / 'EPOCH.json', current)
owner.write_owned(ROOT, epoch_claim, owner.encoded(current))
role['built'] = success
role['last_build'] = label
s.save(directory / 'ROLE.json', role)
s.save(directory / 'RESULT.json', {'command_success': success, 'error': error, 'publication_errors': publication_errors,
                                 'owned_processes': state, 'source_role': role['role'], 'preservation_verified': True})
print(label, 'success' if success else error, flush=True)
assert success
