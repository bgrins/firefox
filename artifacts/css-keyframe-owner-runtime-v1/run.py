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
PROPOSAL = ROOT / 'artifacts/css-keyframe-animation-rule-owner-host-combined-v2'
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
assert h.sha(PROPOSAL / 'FILES.json') == 'c06f256f9765fe37ee0abc239b31822034b1f50226b7f41c32e664cebeed2945'
for name, expected in read(PROPOSAL / 'FILES.json').items():
    assert h.sha(PROPOSAL / name) == expected, name
epoch = read(ROOT / 'artifacts/css-presentation-roadmap-commit-v1/CURRENT-EPOCH.json')
before = a.verify_current(h, ROOT, ENV, epoch)
save('BEFORE.json', before)
preimages = read(PROPOSAL / 'PREIMAGES.json')
postimages = read(PROPOSAL / 'POSTIMAGES.json')
preserved = read(PROPOSAL / 'PRESERVED-SOURCE-PINS.json')
assert len(preimages) == 17 and set(preimages) == set(postimages)
assert {p: h.fingerprint(ROOT, p) for p in preimages} == preimages
assert {p: h.fingerprint(ROOT, p) for p in preserved} == preserved
tracked = set(h.git(ROOT, ENV, 'ls-files', '--', *preimages).decode().splitlines())
with (HERE / 'apply.log').open('x') as stream:
    for extra in [['--check'], []]:
        subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'apply', *extra, str(PROPOSAL / 'native.patch')], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
assert {p: h.fingerprint(ROOT, p) for p in postimages} == postimages
assert {p: h.fingerprint(ROOT, p) for p in preserved} == preserved
current = copy.deepcopy(epoch)
current['pins'].update(postimages)
for path in set(preimages) & set(current['installed_identities']):
    info = (ROOT / path).stat()
    current['installed_identities'][path] = [info.st_dev, info.st_ino]
current['modified_native_paths'] = sorted(set(epoch['modified_native_paths']) | tracked)
current['untracked_native'] = sorted(set(epoch['untracked_native']) | (set(preimages) - tracked))
current['semantic_index'] = h.semantic_index(h.index_state(ROOT, ENV))
for key, value in [('roles', 'pins'), ('native_modified_paths', 'modified_native_paths'), ('untracked_native', 'untracked_native')]:
    current['counts'][key] = len(current[value])
save('SOURCE-EPOCH.json', current)
save('APPLIED.json', {'postimages': postimages, 'preserved': preserved, 'native_patch_sha256': h.sha(PROPOSAL / 'native.patch')})


def source_guard():
    assert {p: h.fingerprint(ROOT, p) for p in postimages} == postimages
    assert {p: h.fingerprint(ROOT, p) for p in preserved} == preserved
    assert h.fingerprint(ROOT, 'Cargo.lock') == current['pins']['Cargo.lock']
    assert h.semantic_index(h.index_state(ROOT, ENV)) == current['semantic_index']
    assert h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']


selection = read(PROPOSAL / 'GTEST-SELECTION.json')
assert len(selection['names']) == len(set(selection['names'])) == 17
python = '/Users/bgrins/venvs/firefox/bin/python'
commands = [
    ['metadata', ['/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo', '--config', str(ROOT / 'objdir-full.noindex/.cargo/config.toml'), 'metadata', '--format-version', '1', '--frozen', '--manifest-path', str(ROOT / 'toolkit/library/gtest/rust/Cargo.toml')]],
    ['export', [python, './mach', 'build', 'export', '-j2']],
    ['binaries', [python, './mach', 'build', 'binaries', '-j2']],
    ['gtest', [python, './mach', 'gtest', selection['filter'], '--jobs=1']]]
results = []
for name, command in commands:
    source_guard()
    save(name + '-COMMAND.json', {'command': command, 'started': time.time()})
    with (HERE / (name + '.log')).open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    record = {'phase': name, 'exit': result.returncode, 'finished': time.time(), 'log_sha256': h.sha(HERE / (name + '.log'))}
    save(name + '-EXECUTION.json', record)
    results.append(record)
    source_guard()
    print(name, 'exit', result.returncode, flush=True)
    if result.returncode:
        break
save('EXECUTION.json', results)
binaries = [p for p in epoch['pins'] if p.startswith('objdir-full.noindex/') and (p.endswith('/XUL') or p.endswith('/firefox'))]
assert len(binaries) == 4
after_binaries = {p: h.fingerprint(ROOT, p) for p in binaries}
save('BINARIES.json', {'before': {p: epoch['pins'][p] for p in binaries}, 'after': after_binaries})
current['pins'].update(after_binaries)
save('PRESERVATION.json', a.verify_current(h, ROOT, ENV, current))
current['provenance']['compact_owner_execution'] = {'path': str((HERE / 'EXECUTION.json').relative_to(ROOT)), 'sha256': h.sha(HERE / 'EXECUTION.json')}
save('CURRENT-EPOCH.json', current)
log = (HERE / 'gtest.log').read_text(errors='replace') if (HERE / 'gtest.log').exists() else ''
events = re.findall(r'TEST_(START|END): ([^\r\n]+)', log)
tests = []
paired = len(events) == 34
if paired:
    for start, end in zip(events[::2], events[1::2]):
        paired = paired and start[0] == 'START' and end == ('END', 'PASS')
        tests.append(start[1])
passed = paired and sorted(tests) == sorted(selection['names'])
passed = passed and len(results) == 4 and all(r['exit'] == 0 for r in results)
passed = passed and 'Ran 17 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).' in log
passed = passed and after_binaries['objdir-full.noindex/dist/bin/gtest/XUL'] == after_binaries['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL']
save('RESULT.json', {'status': 'COMPACT_OWNER_BUILD_AND_17_TESTS_PASS' if passed else 'INCOMPLETE_OR_FAILED', 'events': events, 'preservation': True, 'new_accepted_bugs': 0, 'memory_reporting_complete': False, 'servo_feature_compiled': False})
assert passed
print('PASS: compact owner build and all 17 named native tests.', flush=True)
