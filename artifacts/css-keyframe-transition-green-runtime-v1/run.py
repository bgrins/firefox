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
RED = ROOT / 'artifacts/css-keyframe-transition-red-runtime-v1'
PROPOSAL = ROOT / 'artifacts/css-keyframe-transition-endpoint-gtest-proposal-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_HEADLESS='1',
           MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
h = load('preserve', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', ROOT / 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
assert h.sha(PROPOSAL / 'FILES.json') == 'b2acf5dfd265f9990207f9064e9f5149db407a18a46be1e014fb7985f16570fe'
for name, expected in read(PROPOSAL / 'FILES.json').items():
    assert h.sha(PROPOSAL / name) == expected, name
red_log = (RED / 'gtest.log').read_text()
assert h.sha(RED / 'gtest.log') == read(RED / 'EXECUTION.json')['log_sha256']
assert read(RED / 'EXECUTION.json')['exit'] == 1
assert read(RED / 'RESULT.json')['events'] == [
    ['START', 'KeyframePresentation.LiteralOpacity'], ['END', 'PASS'],
    ['START', 'KeyframePresentation.TransitionConcreteEndpoint'],
    ['END', 'Test FAIL, expected PASS. Subtests passed 0/1. Unexpected 1']]
assert 'current.mFromEndpoint' in red_log
assert 'Ran 2 test(s) from 1 test suite(s) (0 disabled), with 1 failure(s).' in red_log
assert 'TransitionConcreteEndpoint failed 1 check(s):' in red_log
epoch = read(RED / 'CURRENT-EPOCH.json')
before = a.verify_current(h, ROOT, ENV, epoch)
save('BEFORE.json', before)
native = 'dom/animation/KeyframeEffect.cpp'
assert h.fingerprint(ROOT, native) == h.sha(PROPOSAL / 'original' / native)
with (HERE / 'apply.log').open('x') as stream:
    for extra in [['--check'], []]:
        subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'apply', *extra, str(PROPOSAL / 'native.patch')], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
assert h.fingerprint(ROOT, native) == h.sha(PROPOSAL / 'candidate' / native)
current = copy.deepcopy(epoch)
current['pins'][native] = h.fingerprint(ROOT, native)
current['semantic_index'] = h.semantic_index(h.index_state(ROOT, ENV))
save('SOURCE-EPOCH.json', current)
commands = [
    ['build', ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries']],
    ['gtest', ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'gtest', 'KeyframePresentation.*', '--jobs=1']]]
results = []
for name, command in commands:
    save(name + '-COMMAND.json', {'command': command, 'started': time.time()})
    with (HERE / (name + '.log')).open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    record = {'phase': name, 'exit': result.returncode, 'finished': time.time(), 'log_sha256': h.sha(HERE / (name + '.log'))}
    save(name + '-EXECUTION.json', record)
    results.append(record)
    if result.returncode:
        break
save('EXECUTION.json', results)
binaries = [p for p in epoch['pins'] if p.startswith('objdir-full.noindex/') and (p.endswith('/XUL') or p.endswith('/firefox'))]
assert len(binaries) == 4
after_binaries = {p: h.fingerprint(ROOT, p) for p in binaries}
save('BINARIES.json', {'before': {p: epoch['pins'][p] for p in binaries}, 'after': after_binaries})
current['pins'].update(after_binaries)
save('PRESERVATION.json', a.verify_current(h, ROOT, ENV, current))
current['provenance']['transition_green_execution'] = {'path': str((HERE / 'EXECUTION.json').relative_to(ROOT)), 'sha256': h.sha(HERE / 'EXECUTION.json')}
save('CURRENT-EPOCH.json', current)
log = (HERE / 'gtest.log').read_text(errors='replace') if (HERE / 'gtest.log').exists() else ''
events = re.findall(r'TEST_(START|END): ([^\r\n]+)', log)
passed = events == [('START', 'KeyframePresentation.LiteralOpacity'), ('END', 'PASS'), ('START', 'KeyframePresentation.TransitionConcreteEndpoint'), ('END', 'PASS')]
passed = passed and len(results) == 2 and all(r['exit'] == 0 for r in results)
passed = passed and 'Ran 2 test(s) from 1 test suite(s) (0 disabled), with 0 failure(s).' in log
passed = passed and after_binaries['objdir-full.noindex/dist/bin/gtest/XUL'] == after_binaries['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL']
save('RESULT.json', {'status': 'TRANSITION_DESCRIPTOR_GREEN' if passed else 'INCOMPLETE_OR_FAILED', 'events': events, 'preservation': True, 'new_accepted_bugs': 0})
assert passed
print('PASS: one-line correction clears stale descriptor; both native tests pass.', flush=True)
