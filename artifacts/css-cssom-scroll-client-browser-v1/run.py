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

def authenticate(mapping, root):
    for name, digest in mapping.items():
        path = root / name
        assert path.is_file() and not path.is_symlink() and sha(path) == digest, name

assert len(sys.argv) == 2 and sha(HERE / 'DRAFT-FILES.json') == sys.argv[1]
draft, refs, settings = read(HERE / 'DRAFT-FILES.json'), read(HERE / 'REFERENCES.json'), read(HERE / 'CONFIG.json')
authenticate(draft, HERE)
authenticate(refs, ROOT)
assert settings['ready_for_execution'] is True
assert all(settings[n] for n in ['epoch', 'epoch_manifest_sha256', 'root_receipt_sha256'])
assert not any((HERE / n).exists() or (HERE / n).is_symlink() for n in ['STATE.json', 'capture', 'BEFORE.json', 'FINAL.json', 'SUMMARY.json'])
epoch = ROOT / settings['epoch']
assert sha(epoch / 'FILES.json') == settings['epoch_manifest_sha256']
authenticate(read(epoch / 'FILES.json'), epoch)
assert sha(epoch / 'ROOT-FINAL-CHECK.json') == settings['root_receipt_sha256']
expected, state_before = read(epoch / 'FINAL.json'), read(epoch / 'STATE.json')
receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
assert state_before['status'] == 'terminal' and state_before['restored'] is True
assert state_before['restore_build_exit'] == 0 and state_before['recovery_errors'] == []
assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
assert receipt['restored_binary_pins'] == state_before['restored_binary_pins']
assert expected == read(epoch / 'BEFORE.json')
pins = read(epoch / 'FINAL-PINS.json')
assert pins == {**read(epoch / 'RESOURCES.json'), **expected['sources'], **state_before['restored_binary_pins']}
wpt = load('scroll_client_wpt', ROOT / settings['helpers'] / 'run_wpt.py')
bindings = load('scroll_client_bindings', ROOT / settings['helpers'] / 'bindings.py')
extras = load('scroll_client_capture', ROOT / settings['capture'])
cleanup = load('scroll_client_cleanup', ROOT / settings['cleanup'])
validator = load('scroll_client_validator', HERE / 'validate.py')
config = read(epoch / 'CONFIG.json')
config['guard_sources'] = sorted(expected['sources'])
wpt.HERE, wpt.CONFIG = HERE, config

def verify():
    authenticate(draft, HERE)
    authenticate(refs, ROOT)
    assert wpt.snapshot() == expected
    assert wpt.pins(list(pins)) == pins
    assert [n for n in wpt.git('diff', '--name-only').decode().splitlines()
            if not n.startswith('artifacts/')] == config['modified_native_paths']
    assert not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt')
    assert all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in config['must_be_absent'])

verify()
bindings.index_state(wpt)
wpt.save('BEFORE.json', {'snapshot': expected, 'pins': pins})
state = {'status': 'starting', 'complete': False, 'preserved': False, 'native_changes': False,
         'source_role': 'authenticated restored working epoch; no candidate source installation', 'epoch': settings['epoch']}
wpt.save('STATE.json', state)
try:
    result = extras.capture(HERE, ROOT, wpt, cleanup, 'capture',
                            (HERE / 'probe.html').read_bytes(), verify, pins)
    assert result['status'] == 'terminal' and len(result['observations']) == 1
    assert result['process_cleanup']['terminal'] and result['process_cleanup']['noLiveGroup'] and result['profile_removed']
    assert not result['cleanup_errors'] and result['before'] == result['after'] == pins
    summary = validator.validate(result['observations'][0])
    summary['phase_outcomes'] = {
        phase: {metric: {label: sum(row['phases'][phase][metric] is value for row in summary['rows'])
                        for label, value in [('PASS', True), ('FAIL', False), ('UNCALIBRATED', None)]}
                for metric in ['scroll_matches', 'client_matches', 'client_origin_matches']}
        for phase in validator.PHASES}
    wpt.save('SUMMARY.json', summary)
    assert summary['calibrated'] == summary['repeat_stable'] == summary['restored_stable'] == 8
    assert summary['phase_calibrated'] == 32
    state.update(complete=True, calibrated=8, phase_calibrated=32, repeat_stable=8,
                 restored_stable=8, phase_outcomes=summary['phase_outcomes'])
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    try:
        verify()
        bindings.index_state(wpt)
        wpt.save('FINAL.json', {'snapshot': wpt.snapshot(), 'pins': wpt.pins(list(pins))})
        state['preserved'] = True
    except BaseException as error:
        state['preservation_failure'] = repr(error)
    state['status'] = 'terminal'
    wpt.save('STATE.json', state)
print(json.dumps(state, indent=2))
if not state['complete'] or not state['preserved']:
    raise SystemExit(1)
