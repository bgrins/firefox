import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert len(sys.argv) == 2 and sha(HERE / 'DRAFT-FILES.json') == sys.argv[1]
draft = read(HERE / 'DRAFT-FILES.json')
refs = read(HERE / 'REFERENCES.json')
assert not any((HERE / n).exists() for n in ['STATE.json', 'capture', 'BEFORE.json'])
epoch = ROOT / 'artifacts/css-baseline-nested-font-trace-runtime-v2'
assert sha(epoch / 'FILES.json') == 'b24cc1d5af9268eb4dc5485faa51721ee6cd514773c2fddc191b6f4e9ebb5ec6'
for name, digest in read(epoch / 'FILES.json').items():
    assert sha(epoch / name) == digest, name
expected = read(epoch / 'FINAL.json')
pins = read(epoch / 'FINAL-PINS.json')
state_before = read(epoch / 'STATE.json')
assert state_before['status'] == 'terminal' and state_before['restored']
assert state_before['restore_build_exit'] == 0 and not state_before['recovery_errors']
wpt = load('cancellation_wpt', ROOT / 'artifacts/css-hidden-mathml-integration-runtime-v1/run_wpt.py')
extras = load('cancellation_capture', ROOT / 'artifacts/css-flex-fragment-composed-extras-controller-v2/extras.py')
cleanup = load('cancellation_cleanup', ROOT / 'artifacts/css-flex-fragment-composed-extras-controller-v2/cleanup.py')
validator = load('cancellation_validator', HERE / 'validate.py')
config = read(ROOT / 'artifacts/css-exact-synthesis-compile-runtime-v1/CONFIG.json')
config['guard_sources'] = sorted(set(config['guard_sources']) | {'layout/generic/nsLineLayout.cpp'})
wpt.HERE, wpt.CONFIG = HERE, config


def verify():
    for name, digest in draft.items():
        assert sha(HERE / name) == digest, name
    for name, digest in refs.items():
        assert sha(ROOT / name) == digest, name
    assert wpt.snapshot() == expected
    assert wpt.pins(list(pins)) == pins
    changed = [name for name in wpt.git('diff', '--name-only').decode().splitlines()
               if not name.startswith('artifacts/')]
    assert changed == config['modified_native_paths']


verify()
wpt.save('BEFORE.json', {'snapshot': expected, 'pins': pins})
state = {'status': 'starting', 'complete': False, 'preserved': False,
         'native_changes': False, 'source_role': 'restored working tree with accepted106-111'}
wpt.save('STATE.json', state)
try:
    result = extras.capture(HERE, ROOT, wpt, cleanup, 'capture',
                            (HERE / 'probe.html').read_bytes(), verify, pins)
    assert result['process_cleanup']['noLiveGroup'] and result['profile_removed']
    assert not result['cleanup_errors'] and result['before'] == result['after'] == pins
    summary = validator.validate(result['observations'][0])
    wpt.save('SUMMARY.json', summary)
    state.update(complete=True, calibrated=summary['calibrated'],
                 stable=summary['stable'], matching=summary['matching'])
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    try:
        verify()
        wpt.save('FINAL.json', {'snapshot': wpt.snapshot(), 'pins': wpt.pins(list(pins))})
        state['preserved'] = True
    except BaseException as error:
        state['preservation_failure'] = repr(error)
    state['status'] = 'terminal'
    wpt.save('STATE.json', state)
print(json.dumps(state, indent=2))
if not state['complete'] or not state['preserved']:
    raise SystemExit(1)
