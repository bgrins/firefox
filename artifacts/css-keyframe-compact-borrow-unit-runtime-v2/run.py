import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


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
epoch = read(ROOT / 'artifacts/css-keyframe-compact-borrow-unit-runtime-v1/CURRENT-EPOCH.json')
save('BEFORE.json', a.verify_current(h, ROOT, ENV, epoch))
crate = HERE / 'crate'
crate.mkdir()
source = ROOT / 'servo/components/servo_arc'
pins = {str((source / n).relative_to(ROOT)): h.sha(source / n) for n in ['Cargo.toml', 'lib.rs']}
for name in ['Cargo.toml', 'lib.rs']:
    shutil.copyfile(source / name, crate / name)
save('CRATE-SOURCE.json', pins)
target = HERE / 'cargo-target'
assert not target.exists()
unit_env = dict(ENV, CARGO_TARGET_DIR=str(target))
cargo = ['/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo', '--config', str(ROOT / 'objdir-full.noindex/.cargo/config.toml')]
with (HERE / 'lock.log').open('x') as stream:
    result = subprocess.run(cargo + ['generate-lockfile', '--offline', '--manifest-path', str(crate / 'Cargo.toml')], cwd=ROOT, env=unit_env, stdout=stream, stderr=subprocess.STDOUT)
save('LOCK-EXECUTION.json', {'exit': result.returncode, 'log_sha256': h.sha(HERE / 'lock.log')})
assert result.returncode == 0
resolved = tomllib.loads((crate / 'Cargo.lock').read_text())['package']
main_packages = tomllib.loads((ROOT / 'Cargo.lock').read_text())['package']
for package in resolved:
    if package['name'] == 'servo_arc':
        continue
    candidates = [p for p in main_packages if p['name'] == package['name'] and p['version'] == package['version']]
    assert len(candidates) == 1, package
    assert all(package.get(k) == candidates[0].get(k) for k in ['source', 'checksum']), package
save('DEPENDENCIES.json', {'packages': resolved, 'locked_subset_of_gecko': True, 'lock_sha256': h.sha(crate / 'Cargo.lock')})
test = cargo + ['test', '--manifest-path', str(crate / 'Cargo.toml'), '--frozen', '--no-default-features']
commands = [
    ('unit', test + ['--lib', 'compact_borrow_tests']),
    ('unit-track-alloc-size', test + ['--features', 'track_alloc_size', '--lib', 'compact_borrow_tests']),
    ('doctest', test + ['--doc', 'ArcUnionBorrowPtr', '--', '--show-output']),
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
assert {p: h.fingerprint(ROOT, p) for p in pins} == pins
assert all(h.sha(source / n) == h.sha(crate / n) for n in ['Cargo.toml', 'lib.rs'])
save('PRESERVATION.json', a.verify_current(h, ROOT, ENV, epoch))
epoch['provenance']['compact_borrow_unit_execution'] = {'path': str((HERE / 'EXECUTION.json').relative_to(ROOT)), 'sha256': h.sha(HERE / 'EXECUTION.json')}
save('CURRENT-EPOCH.json', epoch)
passed = len(results) == 3 and all(r['exit'] == 0 for r in results)
for name in ['unit', 'unit-track-alloc-size']:
    path = HERE / (name + '.log')
    passed = passed and path.exists() and 'test result: ok. 5 passed; 0 failed;' in path.read_text()
doc = (HERE / 'doctest.log').read_text() if (HERE / 'doctest.log').exists() else ''
passed = passed and 'test result: ok. 3 passed; 0 failed;' in doc
save('RESULT.json', {'status': 'UNIT_AND_DOC_TESTS_PASS' if passed else 'INCOMPLETE_OR_FAILED', 'diagnostics': {'E0597': doc.count('error[E0597]'), 'E0277': doc.count('error[E0277]')}, 'preservation': True, 'gecko_build_complete': False, 'miri_run': False})
assert passed
print('PASS: five exact-source Arc tests in both configurations and three compile-fail doctests.', flush=True)
