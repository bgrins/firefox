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
PROPOSAL = ROOT / 'artifacts/css-keyframe-compact-source-borrow-proposal-v2'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')


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
assert h.sha(PROPOSAL / 'FILES.json') == 'ca07be4a63eb3483baf3559083fe55a6e6a57e9c1de6bf1fce725f28f7b51c34'
for name, expected in read(PROPOSAL / 'FILES.json').items():
    assert h.sha(PROPOSAL / name) == expected, name
epoch = read(ROOT / 'artifacts/css-keyframe-owner-runtime-v1/CURRENT-EPOCH.json')
save('BEFORE.json', a.verify_current(h, ROOT, ENV, epoch))
preimages = read(PROPOSAL / 'PREIMAGES.json')
postimages = read(PROPOSAL / 'POSTIMAGES.json')
assert len(preimages) == 4 and set(preimages) == set(postimages)
assert {p: h.fingerprint(ROOT, p) for p in preimages} == preimages
with (HERE / 'apply.log').open('x') as stream:
    for extra in [['--check'], []]:
        subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', 'apply', *extra, str(PROPOSAL / 'native.patch')], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
assert {p: h.fingerprint(ROOT, p) for p in postimages} == postimages
current = copy.deepcopy(epoch)
current['pins'].update(postimages)
for path in set(preimages) & set(current['installed_identities']):
    info = (ROOT / path).stat()
    current['installed_identities'][path] = [info.st_dev, info.st_ino]
current['modified_native_paths'] = sorted(set(epoch['modified_native_paths']) | {'servo/components/servo_arc/lib.rs'})
current['semantic_index'] = h.semantic_index(h.index_state(ROOT, ENV))
current['counts']['roles'] = len(current['pins'])
current['counts']['native_modified_paths'] = len(current['modified_native_paths'])
save('SOURCE-EPOCH.json', current)
prior = read(ROOT / 'artifacts/css-keyframe-owner-runtime-v1/APPLIED.json')
composed = prior['postimages'] | postimages
assert len(composed) == 18
save('APPLIED.json', {'postimages': composed, 'preserved': prior['preserved'], 'owner_patch_sha256': prior['native_patch_sha256'], 'borrow_patch_sha256': h.sha(PROPOSAL / 'native.patch')})
target = HERE / 'cargo-target'
assert not target.exists()
unit_env = dict(ENV, CARGO_TARGET_DIR=str(target))
cargo = ['/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo', '--config', str(ROOT / 'objdir-full.noindex/.cargo/config.toml'), 'test', '--manifest-path', str(ROOT / 'servo/components/servo_arc/Cargo.toml'), '--frozen', '--no-default-features']
commands = [
    ('unit', cargo + ['--lib', 'compact_borrow_tests']),
    ('unit-track-alloc-size', cargo + ['--features', 'track_alloc_size', '--lib', 'compact_borrow_tests']),
    ('doctest', cargo + ['--doc', 'ArcUnionBorrowPtr', '--', '--show-output']),
]
results = []
for name, command in commands:
    save(name + '-COMMAND.json', {'command': command, 'started': time.time(), 'target': str(target)})
    with (HERE / (name + '.log')).open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, env=unit_env, stdout=stream, stderr=subprocess.STDOUT)
    record = {'phase': name, 'exit': result.returncode, 'finished': time.time(), 'log_sha256': h.sha(HERE / (name + '.log'))}
    save(name + '-EXECUTION.json', record)
    results.append(record)
    print(name, 'exit', result.returncode, flush=True)
    if result.returncode:
        break
save('EXECUTION.json', results)
save('PRESERVATION.json', a.verify_current(h, ROOT, ENV, current))
current['provenance']['compact_borrow_unit_execution'] = {'path': str((HERE / 'EXECUTION.json').relative_to(ROOT)), 'sha256': h.sha(HERE / 'EXECUTION.json')}
save('CURRENT-EPOCH.json', current)
passed = len(results) == 3 and all(r['exit'] == 0 for r in results)
for name in ['unit', 'unit-track-alloc-size']:
    path = HERE / (name + '.log')
    passed = passed and path.exists() and 'test result: ok. 5 passed; 0 failed;' in path.read_text()
doc = (HERE / 'doctest.log').read_text() if (HERE / 'doctest.log').exists() else ''
passed = passed and 'test result: ok. 3 passed; 0 failed;' in doc
save('RESULT.json', {'status': 'UNIT_AND_DOC_TESTS_PASS' if passed else 'INCOMPLETE_OR_FAILED', 'diagnostics': {'E0597': doc.count('error[E0597]'), 'E0277': doc.count('error[E0277]')}, 'preservation': True, 'gecko_build_complete': False, 'miri_run': False})
assert passed
print('PASS: five actual Arc tests in both configurations and three compile-fail doctests.', flush=True)
