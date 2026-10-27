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
assert sha(epoch / 'FILES.json') == settings['epoch_manifest_sha256'] == settings['required_installation_manifest_sha256']
authenticate(read(epoch / 'FILES.json'), epoch)
assert sha(epoch / 'ROOT-FINAL-CHECK.json') == settings['root_receipt_sha256']
def installed_epoch(epoch):
    expected, state_before = read(epoch / 'FINAL.json'), read(epoch / 'STATE.json')
    receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
    before, installation = read(epoch / 'BEFORE.json'), read(epoch / 'INSTALLATION.json')
    config = read(epoch / 'CONFIG.json')
    native = 'dom/base/Element.cpp'
    candidate = '5770fd0f1134284626ed42152e4b1c1d054cf509ae99e2ebcaf08d5ae00c0913'
    owned = 'testing/web-platform/tests/css/cssom-view/offset-scroll-integer-precision.html'
    fixture_hash = '18c47e1acbf0a546a975fe5dc92c297a38a71e228a7b6ec576a58bc71c06078b'
    assert state_before['status'] == 'terminal' and state_before['installed'] is True and state_before['restored'] is False
    assert state_before['build_exit'] == state_before['lint_exit'] == 0 and state_before['recovery_errors'] == []
    assert 'failure' not in state_before and state_before['subtests'] == {'PASS': 32, 'FAIL': 0} and state_before['files_ok'] == 1
    assert receipt['status'] == 'INSTALLED_VERIFIED' and receipt['fix'] == 112 and receipt['exit'] == 0
    assert receipt['build_exit'] == receipt['lint_exit'] == 0 and receipt['existing_stage_paths'] == 925
    assert receipt['source_count'] == 47 and receipt['pin_count'] == 318
    assert all(receipt[n] is True for n in ['head_index_preserved', 'other_native_sources_preserved', 'owned_wpt_present', 'cleanup_verified'])
    assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
    assert receipt['installed_binary_pins'] == state_before['installed_binary_pins'] == installation['binary_pins']
    assert receipt['acceptance_sha256'] == state_before['acceptance_sha256'] == installation['acceptance_sha256'] == 'bf2e4f24e4ddc542346499f108e9510646db050aeec2893e3dbf506870b8d11c'
    assert installation['before'] == before and installation['after'] == expected
    assert len(expected['sources']) == len(before['sources']) == 47
    assert expected['sources'] == {**before['sources'], native: candidate}
    assert installation['installed_source_pins'] == {native: candidate}
    assert installation['original_source_pins'] == {native: before['sources'][native]}
    assert expected['head'] == config['head'] == '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
    assert all(expected[k] == before[k] for k in ['head', 'index_diff_sha256', 'index_entries_sha256'])
    assert config['source_pins'] == before['sources']
    assert len(config['modified_native_paths']) == 24 and native not in config['modified_native_paths']
    assert installation['owned_test'] == owned and installation['owned_test_sha256'] == fixture_hash
    assert config['install'] == {owned: 'fixture.html'} and sha(epoch / 'fixture.html') == fixture_hash
    pins = read(epoch / 'FINAL-PINS.json')
    assert len(pins) == 318 and pins == {**read(epoch / 'RESOURCES.json'), **expected['sources'],
                                       owned: fixture_hash, **state_before['installed_binary_pins']}
    config['guard_sources'] = sorted(expected['sources'])
    config['modified_native_paths'] = sorted([*config['modified_native_paths'], native])
    return expected, pins, config, installation

expected, pins, config, installation = installed_epoch(epoch)
wpt = load('scroll_client_wpt', ROOT / settings['helpers'] / 'run_wpt.py')
bindings = load('scroll_client_bindings', ROOT / settings['helpers'] / 'bindings.py')
extras = load('scroll_client_capture', ROOT / settings['capture'])
cleanup = load('scroll_client_cleanup', ROOT / settings['cleanup'])
validator = load('scroll_client_validator', HERE / 'validate.py')
wpt.HERE, wpt.CONFIG = HERE, config

def verify():
    authenticate(draft, HERE)
    authenticate(refs, ROOT)
    assert wpt.snapshot() == expected
    assert wpt.pins(list(pins)) == pins
    assert [n for n in wpt.git('diff', '--name-only').decode().splitlines()
            if not n.startswith('artifacts/')] == config['modified_native_paths']
    owned = ROOT / installation['owned_test']
    info = owned.lstat()
    assert owned.is_file() and not owned.is_symlink() and sha(owned) == installation['owned_test_sha256']
    assert [info.st_dev, info.st_ino] == installation['owned_test_identity']
    assert not wpt.git('ls-files', '--', installation['owned_test'])
    assert not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt')
    assert all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in config['must_be_absent'])

verify()
bindings.index_state(wpt)
wpt.save('BEFORE.json', {'snapshot': expected, 'pins': pins})
state = {'status': 'starting', 'complete': False, 'preserved': False, 'native_changes': False,
         'source_role': 'authenticated installed fix112 working epoch; no source changes by this probe', 'epoch': settings['epoch']}
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
