import copy
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fallback_state', HERE / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
ROOT = s.ROOT
OBJ = ROOT / 'objdir-full.noindex'
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(OBJ), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           PYTHONDONTWRITEBYTECODE='1')
assert all(not os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'))
label, = sys.argv[1:]
assert '/' not in label
epoch = s.read(HERE / 'CURRENT-EPOCH.json')
role = s.read(HERE / 'ROLE.json')
before = s.a.verify_current(s.h, ROOT, env, epoch)
directory = HERE / label
directory.mkdir()
s.save(directory / 'PRE.json', before)
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
s.save(directory / 'COMMAND.json', {'command': command, 'pid': os.getpid(), 'source_role': role['role']})
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
current['raw_attribute_transition'] = {'role': role['role'], 'compiled': success, 'last_phase': label, 'accepted': False}
s.save(directory / 'POST.json', after)
s.save(directory / 'EPOCH.json', current)
(HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
role['built'] = success
role['last_build'] = label
(HERE / 'ROLE.json').write_text(json.dumps(role, indent=2) + '\n')
s.save(directory / 'RESULT.json', {'command_success': success, 'error': error, 'publication_errors': publication_errors,
                                 'owned_processes': state, 'source_role': role['role'], 'preservation_verified': True})
print(label, 'success' if success else error, flush=True)
assert success
