import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda name, value: (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
assert len(sys.argv) == 2 and sha(HERE / 'INPUTS.json') == sys.argv[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

c = read(HERE / 'CONFIG.json')
before = read(HERE / 'BEFORE.json')
phase_pins = read(HERE / 'PHASE-PINS.json')
owned = read(HERE / 'OWNED-TEST.json')
wpt = load('expanded_wpt', ROOT / c['helpers'] / 'run_wpt.py')
tests = load('expanded_tests', ROOT / c['tests_helper'])
wpt.HERE, wpt.CONFIG = HERE, c
wpt.ENV.update(MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
for name in ('MOZ_SAFE_MODE_RESTART', 'MOZ_ANCESTOR_CANCELLATION_TRACE', 'MOZ_NESTED_EDGE_TRACE'):
    wpt.ENV.pop(name, None)
assert read(HERE / 'STATE.json')['status'] == 'prepared'
assert sum(map(len, c['expected_subtests'].values())) == 15 and len(c['tests']) == 2
assert not (HERE / 'wpt-expanded').exists()

def verify(pins, include_new):
    for name, digest in read(HERE / 'INPUTS.json').items():
        assert sha(HERE / name) == digest, name
    for name, digest in read(HERE / 'REFERENCES.json').items():
        assert sha(ROOT / name) == digest, name
    assert wpt.snapshot() == before['snapshot']
    assert wpt.pins(list(pins)) == pins
    for name, digest in pins.items():
        if digest is None:
            assert not (ROOT / name).exists() and not (ROOT / name).is_symlink(), name
    identities = dict(c['installed_tests'])
    if include_new:
        identities[owned['path']] = owned
    for name, item in identities.items():
        path = ROOT / name
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode)
        assert [info.st_dev, info.st_ino] == item['identity'] and sha(path) == item['sha256']
    assert not wpt.git('ls-files', '--', *identities).strip()

state = {'status': 'starting', 'native_changes': False, 'complete': False,
         'expanded_test_installed': False, 'expanded_acceptance': False}
try:
    verify(phase_pins, True)
    state['lint_exit'] = wpt.command('fixture-lint', ['./mach', 'lint', '--linter', 'wpt', owned['path']])
    save('STATE.json', state)
    assert state['lint_exit'] == 0
    verify(phase_pins, True)
    result = tests.run(wpt, 'expanded', phase_pins)
    assert len(result['rows']) == 15 and all(row['status'] == 'PASS' for row in result['rows'])
    assert len(result['ends']) == 2 and all(row['status'] == 'OK' for row in result['ends'])
    verify(phase_pins, True)
    final = {'snapshot': wpt.snapshot(), 'pins': wpt.pins(list(phase_pins))}
    save('FINAL.json', final)
    save('TEST-INSTALLATION.json', {'before': before, 'after': final, 'owned_test': owned,
         'native_changes': False, 'counts': {'PASS': 15, 'FAIL': 0}, 'files_ok': 2})
    state.update(complete=True, expanded_test_installed=True, counts={'PASS': 15, 'FAIL': 0}, files_ok=2)
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    if not state['complete']:
        try:
            path = ROOT / owned['path']
            info = path.lstat()
            assert stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == owned['identity']
            path.unlink()
            verify(before['pins'], False)
            save('FINAL.json', {'snapshot': wpt.snapshot(), 'pins': wpt.pins(list(before['pins']))})
            state['restored'] = True
        except BaseException as error:
            state['preservation_failure'] = repr(error)
    state['status'] = 'terminal'
    save('STATE.json', state)
print(json.dumps(state, indent=2))
if not state['complete']:
    raise SystemExit(1)
