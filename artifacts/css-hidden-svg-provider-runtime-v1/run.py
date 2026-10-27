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
proposal = ROOT / settings['proposal']
assert (HERE / 'probe.html').read_bytes() == (proposal / 'probe.html').read_bytes()
assert (HERE / 'validate.py').read_bytes() == (proposal / 'validate.py').read_bytes()
epoch = ROOT / settings['epoch']
assert sha(epoch / 'FILES.json') == settings['epoch_manifest_sha256'] == '0bbbfcb6ee3eb5078b33b716336453beeef1eab1386c180af9ca1a10606db822'
authenticate(read(epoch / 'FILES.json'), epoch)
assert sha(epoch / 'ROOT-FINAL-CHECK.json') == settings['root_receipt_sha256']

def restored_epoch(epoch):
    expected, state_before = read(epoch / 'FINAL.json'), read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    assert state_before['status'] == 'terminal' and state_before['restored'] is True
    assert state_before['trace_complete'] is True and state_before['baseline_complete'] is True
    assert state_before['trace_build_exit'] == state_before['restore_build_exit'] == 0
    assert state_before['recovery_errors'] == [] and 'failure' not in state_before
    assert receipt['status'] == 'TRACE_AND_RESTORATION_VERIFIED' and receipt['exit'] == 0
    assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
    assert receipt['source_count'] == 49 and receipt['pin_count'] == 337
    assert receipt['staged_paths_preserved'] == 925 and receipt['native_modified_paths_preserved'] == 26
    assert receipt['installed112_source_and_test_ownership_preserved'] is True
    assert receipt['both_process_groups_cleaned'] is True and receipt['both_profiles_removed'] is True
    binaries = state_before['restored_binary_pins']
    assert binaries == receipt['restored_binary_pins'] == {
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox': 'a783e8f1cce2b4f3ca63e9a5dc1af4396e6af929669ac835e2171d96e76a5ee9',
        'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL': 'bce39299d0fe371e42177cc27fbebf75fb36ee7150f0f3fa0628403dace852ed'}
    assert expected == read(epoch / 'BEFORE.json')
    gate = load('svg_prior_installed_gate', epoch / 'epoch_gate.py')
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
    installed, installed_pins, _, config, installed_tests = gate.bind(
        ROOT, read(epoch / 'CONFIG.json'), read(epoch / 'EPOCH.json'), read, sha, authenticate, need)
    display = 'layout/painting/nsDisplayList.cpp'
    assert expected == {**installed, 'sources': {**installed['sources'],
                           display: '2af39c2e2b92d20891db704e6e60a7a6e56ef05158b3597b601074807862dea0'}}
    assert len(expected['sources']) == 49 and len(config['modified_native_paths']) == 26
    before_pins = read(epoch / 'BEFORE-PINS.json')
    assert before_pins == {**installed_pins, display: expected['sources'][display]}
    pins = read(epoch / 'FINAL-PINS.json')
    assert pins == {**before_pins, **binaries} and len(pins) == 337
    assert all(pins[n] == h for n, h in expected['sources'].items())
    config['guard_sources'] = sorted(expected['sources'])
    config['existing_tests'] = sorted(installed_tests)
    config['existing_test_pins'] = {n: item['sha256'] for n, item in installed_tests.items()}
    config['tracked_existing_tests'] = []
    config['install'] = {}
    return expected, pins, config, installed_tests

expected, pins, config, installed_tests = restored_epoch(epoch)
wpt = load('scroll_client_wpt', ROOT / settings['helpers'] / 'run_wpt.py')
bindings = load('scroll_client_bindings', ROOT / settings['helpers'] / 'bindings.py')
extras = load('scroll_client_capture', ROOT / settings['capture'])
cleanup = load('scroll_client_cleanup', ROOT / settings['cleanup'])
validator = load('scroll_client_validator', HERE / 'validate.py')
wpt.HERE, wpt.CONFIG = HERE, config
wpt.ENV.pop('MOZ_ANCESTOR_CANCELLATION_TRACE', None)
wpt.ENV.pop('MOZ_NESTED_EDGE_TRACE', None)

def verify():
    authenticate(draft, HERE)
    authenticate(refs, ROOT)
    assert wpt.snapshot() == expected
    assert wpt.pins(list(pins)) == pins
    assert [n for n in wpt.git('diff', '--name-only').decode().splitlines()
            if not n.startswith('artifacts/')] == config['modified_native_paths']
    for name, item in installed_tests.items():
        owned = ROOT / name
        info = owned.lstat()
        assert owned.is_file() and not owned.is_symlink() and sha(owned) == item['sha256']
        assert [info.st_dev, info.st_ino] == item['identity']
    assert not wpt.git('ls-files', '--', *installed_tests).strip()
    assert not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt')
    assert all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in config['must_be_absent'])

verify()
bindings.index_state(wpt)
wpt.save('BEFORE.json', {'snapshot': expected, 'pins': pins})
state = {'status': 'starting', 'complete': False, 'preserved': False, 'native_changes': False,
         'source_role': 'restored OOF trace epoch with expanded112 installed; no source changes by SVG probe', 'epoch': settings['epoch']}
wpt.save('STATE.json', state)
try:
    result = extras.capture(HERE, ROOT, wpt, cleanup, 'capture',
                            (HERE / 'probe.html').read_bytes(), verify, pins)
    assert result['status'] == 'terminal' and len(result['observations']) == 1
    assert result['process_cleanup']['terminal'] and result['process_cleanup']['noLiveGroup'] and result['profile_removed']
    assert not result['cleanup_errors'] and result['before'] == result['after'] == pins
    summary = validator.validate(result['observations'][0])
    summary['ordinary_controls_pass'] = all(row['matched'] for row in summary['rows']
                                             if not row['observations']['hidden'])
    summary['recovery_controls_pass'] = all(row['matches']['afterLayout'] and row['matches']['revealed']
                                           and row['bboxMatchesLocalShape'] for row in summary['rows'])
    wpt.save('SUMMARY.json', summary)
    assert summary['calibrated'] == summary['stable'] == 8
    assert summary['ordinary_controls_pass'] and summary['recovery_controls_pass']
    state.update(complete=True, calibrated=8, stable=8, matched=summary['matched'],
                 mismatched=summary['mismatched'], ordinary_controls_pass=True,
                 recovery_controls_pass=True)
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
