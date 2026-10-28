import copy
import hashlib
import importlib.util
import json
import os
import re
import signal
import sys
import time
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
OBJ = ROOT / 'objdir-full.noindex'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(OBJ), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           PYTHONDONTWRITEBYTECODE='1')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


label, epoch_sha, manifest_sha = sys.argv[1:]
assert re.fullmatch(r'gtest-[1-9][0-9]*', label)


def authenticate():
    assert sha(HERE / 'FILES.json') == manifest_sha
    for name, pin in read(HERE / 'FILES.json').items():
        assert sha(HERE / name) == pin, name
    for name, pin in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / name) == pin, name


authenticate()
assert all(not os.environ.get(k) for k in (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS',
    'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS',
    'MOZ_ARTIFACT_BUILDS'))
epoch_path = RUNTIME / 'CURRENT-EPOCH.json'
assert sha(epoch_path) == epoch_sha
epoch = read(epoch_path)
transition = epoch['registered_number_transition']
assert transition['role'] == 'candidate'
assert transition['variant'] == 'prototype-overlay'
assert transition['compiled'] is True
for name, pin in read(HERE / 'SOURCE-PINS.json').items():
    assert sha(ROOT / name) == pin and epoch['pins'].get(name) == pin, name
state_helper = load('number_state', RUNTIME / 'state.py')
h, guard = state_helper.h, state_helper.a
builder = load('number_builder', RUNTIME / 'phase.py')
control = load('number_control', RUNTIME / 'process_control.py')
parser = load('number_gtest_assess', HERE / 'assess.py')
before = guard.verify_current(h, ROOT, ENV, epoch)
flags = {name: h.git(ROOT / name, ENV, 'ls-files', '-v', '-z')
         for name in ['.', 'artifacts/css-spec-lean']}
directory = HERE / label
directory.mkdir()
roster = read(HERE / 'ROSTER.json')['candidate_gtests']
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'gtest',
           ':'.join(roster), '--jobs=1']
save(directory / 'PRE.json', before)
save(directory / 'COMMAND.json', {'command': command, 'pid': os.getpid(),
     'epoch_sha256': epoch_sha, 'capsule_sha256': manifest_sha})
inflight = copy.deepcopy(epoch)
inflight['registered_number_transition']['compiled'] = False
inflight['registered_number_gtest'] = {'label': label, 'status': 'IN_FLIGHT', 'success': False}
save(directory / 'IN-FLIGHT-EPOCH.json', inflight)
epoch_path.write_text(json.dumps(inflight, indent=2, sort_keys=True) + '\n')
inflight_sha = sha(epoch_path)
owned, publication_errors = {}, []
stopped = [False]


def stop(signum, frame):
    stopped[0] = True


for sig in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(sig, stop)
deadline = time.monotonic() + 900
error = None
assessment = None
try:
    builder.run(ROOT, OBJ, directory, ENV,
                lambda: stopped[0] or time.monotonic() >= deadline,
                owned, control, command, publication_errors)
    assessment = parser.assess((directory / 'build.log').read_text(), roster)
except BaseException as exc:
    error = repr(exc)
assert not owned, 'Owned process group remains; do not mutate sources'
current = copy.deepcopy(inflight)
for name in [
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
    'objdir-full.noindex/dist/bin/gtest/XUL',
]:
    assert name in current['pins']
    current['pins'][name] = h.fingerprint(ROOT, name)
index = h.index_state(ROOT, ENV)
assert h.semantic_index(index) == epoch['semantic_index']
current['raw_index_observation']['current'] = index['raw_index']
after = guard.verify_current(h, ROOT, ENV, current)
assert all(h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') == value
           for name, value in flags.items())
assert sha(epoch_path) == inflight_sha
authenticate()
success = error is None and not publication_errors and assessment is not None
current['registered_number_transition']['compiled'] = success
current['registered_number_gtest'] = {
    'label': label, 'success': success, 'assessment': assessment,
    'normal_producer_enabled': False, 'standalone_native_acceptance': False,
}
save(directory / 'POST.json', after)
save(directory / 'EPOCH.json', current)
save(directory / 'RESULT.json', {
    'success': success, 'error': error, 'publication_errors': publication_errors,
    'owned_processes': owned, 'preservation_verified': True,
    'assessment': assessment, 'expected_source_pending_calls': 34,
    'dynamic_pending_call_trace_recorded': False,
    'standalone_native_acceptance': False,
})
epoch_path.write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
print(label, 'passed' if success else error, flush=True)
assert success
