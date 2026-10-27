import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-keyframe-transition-endpoint-gtest-proposal-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_HEADLESS='1',
           MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
h = load('preserve', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', ROOT / 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
assert h.sha(PROPOSAL / 'FILES.json') == 'b2acf5dfd265f9990207f9064e9f5149db407a18a46be1e014fb7985f16570fe'
for name, expected in json.loads((PROPOSAL / 'FILES.json').read_text()).items():
    assert h.sha(PROPOSAL / name) == expected, name
epoch = json.loads((ROOT / 'artifacts/css-presentation-checkpoint-ledger-v1/CURRENT-EPOCH.json').read_text())
before = a.verify_current(h, ROOT, ENV, epoch)
save('BEFORE.json', before)
paths = ['layout/style/test/gtest/TestKeyframePresentation.cpp',
         'layout/style/test/gtest/rust/lib.rs',
         'layout/style/test/gtest/rust/endpoint_transition_cases.rs']
for path in paths:
    original = PROPOSAL / 'original' / path
    assert h.fingerprint(ROOT, path) == (h.sha(original) if original.exists() else None), path
with (HERE / 'apply.log').open('x') as stream:
    for extra in [['--check'], []]:
        subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'apply', *extra, str(PROPOSAL / 'tests.patch')], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
current = copy.deepcopy(epoch)
for path in paths:
    assert h.fingerprint(ROOT, path) == h.sha(PROPOSAL / 'candidate' / path)
    current['pins'][path] = h.fingerprint(ROOT, path)
current['modified_native_paths'] = sorted(set(current['modified_native_paths']) | {paths[0]})
current['untracked_native'] = sorted(set(current['untracked_native']) | {paths[2]})
current['semantic_index'] = h.semantic_index(h.index_state(ROOT, ENV))
for key, value in [('roles', 'pins'), ('native_modified_paths', 'modified_native_paths'), ('untracked_native', 'untracked_native')]:
    current['counts'][key] = len(current[value])
save('SOURCE-EPOCH.json', current)
save('APPLIED.json', {'paths': paths, 'native_correction_applied': False})
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'gtest', 'KeyframePresentation.*', '--jobs=1']
save('COMMAND.json', {'command': command, 'started': time.time()})
with (HERE / 'gtest.log').open('x') as stream:
    result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
save('EXECUTION.json', {'exit': result.returncode, 'finished': time.time(), 'log_sha256': h.sha(HERE / 'gtest.log')})
hosts = ['objdir-full.noindex/dist/bin/gtest/XUL', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL']
after_binaries = {p: h.fingerprint(ROOT, p) for p in hosts}
save('GTEST-BINARIES.json', {'before': {p: epoch['pins'][p] for p in hosts}, 'after': after_binaries})
current['pins'].update(after_binaries)
preservation = a.verify_current(h, ROOT, ENV, current)
save('PRESERVATION.json', preservation)
current['provenance']['transition_red_execution'] = {'path': str((HERE / 'EXECUTION.json').relative_to(ROOT)), 'sha256': h.sha(HERE / 'EXECUTION.json')}
save('CURRENT-EPOCH.json', current)
events = re.findall(r'TEST_(START|END): ([^\r\n]+)', (HERE / 'gtest.log').read_text(errors='replace'))
save('RESULT.json', {'status': 'CAPTURED_PENDING_OUTCOME_REVIEW', 'mach_exit': result.returncode, 'events': events, 'preservation': True})
print(json.dumps({'mach_exit': result.returncode, 'events': events, 'preservation': True}), flush=True)
