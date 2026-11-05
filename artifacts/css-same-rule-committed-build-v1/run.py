import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def load(name, path, expected):
    assert sha(ROOT / path) == expected
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

expected_head = '0f18d294fbacd5eb2fdb3b8cea07f8fe4a7e831b'
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
           MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZCONFIG=str(ROOT / 'mozconfig'),
           MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))
git = lambda *args: subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=env)
assert git('rev-parse', 'HEAD').decode().strip() == expected_head
assert not git('diff', 'HEAD', '--name-only')
selected = json.loads((ROOT / 'artifacts/css-revert-rule-production-validation-v1/SELECTION.json').read_bytes())['after']
for name, digest in selected.items():
    assert sha(ROOT / name) == digest
before = {name: hashlib.sha256(git(*args)).hexdigest() for name, args in
          {'index': ['ls-files', '--stage', '-z'], 'diff': ['diff', 'HEAD', '--binary']}.items()}
save('BEFORE.json', {'head': expected_head, 'selected': selected, 'git': before})
builder = load('committed_builder', 'artifacts/css-shadow-move-promotion-v1/phase.py', '3efbd1f65bdfd3e1815e4f42339bda10a06047dd936544de290a2ec888cc266a')
control = load('committed_process_control', 'artifacts/css-registered-number-native-runtime-v1/process_control.py', 'b57e5e2506b89d48e30c958b2aa04e375e853e3ec68386afe3071a349c1d969a')
owned, errors, stopped = {}, [], [False]
for signum in (signal.SIGINT, signal.SIGTERM):
    signal.signal(signum, lambda *_: stopped.__setitem__(0, True))
lock = ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock'
with lock.open('x') as stream:
    json.dump({'pid': os.getpid(), 'operation': 'build-committed-same-rule-fix'}, stream)
lock_identity = (lock.stat().st_dev, lock.stat().st_ino)
output = HERE / 'build'
output.mkdir()
deadline = time.monotonic() + 2400
try:
    builder.run(ROOT, ROOT / 'objdir-full.noindex', output, env,
                lambda: stopped[0] or time.monotonic() >= deadline, owned, control,
                ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2'], errors)
    assert not owned and not errors
    assert git('rev-parse', 'HEAD').decode().strip() == expected_head
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == before['index']
    assert hashlib.sha256(git('diff', 'HEAD', '--binary')).hexdigest() == before['diff']
    assert all(sha(ROOT / name) == digest for name, digest in selected.items())
    names = ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
             'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
             'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini']
    binaries = {name: sha(ROOT / name) for name in names}
    assert binaries[names[1]] != 'bad0ea68441fd160e1df7ef7a1bdc91670434405f78fc137f4ae437b0a212173'
    save('RESULT.json', {'head': expected_head, 'selected_sources_and_tests': selected,
                        'binaries': binaries, 'build_succeeded': True,
                        'source_and_index_preserved': True, 'owned_groups_absent': True,
                        'application_intentionally_left_at_committed_fix': True})
finally:
    assert not owned, 'Build process cleanup incomplete; keep lock for recovery'
    assert (lock.stat().st_dev, lock.stat().st_ino) == lock_identity
    lock.unlink()
