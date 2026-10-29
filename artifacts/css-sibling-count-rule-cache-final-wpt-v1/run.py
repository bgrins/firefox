import importlib.util
import json
import os
import signal
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
           MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 2
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    assert policy['execution_enabled'] is True
    owned = load('final_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    owned.authenticate(HERE, sys.argv[1])
    for name, pin in policy['references'].items():
        assert owned.digest((ROOT / name).read_bytes()) == pin
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    state = owned.load_state(RUNTIME)
    controls = {n: (RUNTIME / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert {n: owned.digest(b) for n, b in controls.items()} == policy['controls']
    assert owned.digest(controls['CURRENT-EPOCH.json']) == policy['epoch_sha256']
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == policy['head']
    transition = epoch['sibling_count_rule_cache_transition']
    assert transition['role'] == 'candidate' and transition['compiled'] and not transition['accepted']
    assert transition['manifest_sha256'] == policy['promotion_manifest_sha256']
    owned.authenticate(ROOT / policy['promotion_capsule'], policy['promotion_manifest_sha256'])
    for marker, expected in policy['preserved_markers'].items():
        assert epoch[marker] == expected
    assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs', policy['source']['path']])
    assert epoch['staged_working'] == {}
    installed = ROOT / policy['promotion_runtime'] / 'INSTALL-RESULT.json'
    assert owned.digest(installed.read_bytes()) == policy['installed_result_sha256']
    installation = owned.read(installed)
    assert installation['installed'] and installation['preservation_verified'] and not installation['accepted']
    build = ROOT / policy['build_directory']
    assert owned.read(build / 'EPOCH.json') == epoch
    assert transition['variant'] == 'sibling-count-rule-cache'
    assert transition['last_phase'] == build.name
    assert owned.read(build / 'APPLICATION-METADATA.json') == policy['application_metadata']
    assert owned.digest((build / 'RESULT.json').read_bytes()) == policy['build_result_sha256']
    built, inner = owned.read(build / 'RESULT.json'), owned.read(build / 'build-RESULT.json')
    assert built['command_success'] and built['preservation_verified'] and built['error'] is None and built['publication_errors'] == [] and built['owned_processes'] == {}
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['error'] is None and inner['stop_reason'] is None and inner['cleanup_errors'] == []
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        owned.group_absent(owned.read(build / name)['pgid'])
    owned.authenticate(ROOT / policy['original_runtime'], policy['original_manifest_sha256'])
    owned.quiescent(RUNTIME)
    assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
    claims = []
    pins = {policy['source']['path']: policy['source']['candidate_sha256'], **{name: item['sha256'] for name, item in policy['tests'].items()}}
    for name, record in policy['accepted_current_payloads'].items():
        assert epoch['pins'][name] == record['sha256'] and epoch['installed_identities'][name] == record['identity']
        claims.append(owned.claim(ROOT, name, record['sha256'], record['identity']))
    for name, pin in pins.items():
        assert epoch['pins'][name] == pin
        claims.append(owned.claim(ROOT, name, pin, epoch['installed_identities'][name]))
    metadata = load('final_metadata', ROOT / policy['wpt']['metadata_helper'])
    assert metadata.application_metadata(ROOT / policy['wpt']['application_ini'], policy['head']) == policy['application_metadata']
    flags = {name: state.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') for name in ('.', 'artifacts/css-spec-lean')}
    before = state.a.verify_current(state.h, ROOT, ENV, epoch)
    def verify():
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        for claim in claims:
            owned.claim(ROOT, claim['path'], claim['owned_sha256'], claim['identity'])
        assert all(state.h.git(ROOT / name, ENV, 'ls-files', '-v', '-z') == body for name, body in flags.items())
        current = state.a.verify_current(state.h, ROOT, ENV, epoch)
        assert current == before
        return current
    runner = load('final_focused_wpt', ROOT / policy['runner_capsule'] / 'wpt.py')
    output = ROOT / policy['output']
    assert not output.exists() and not output.is_symlink()
    stopped = [False]
    def stop(signum, frame):
        stopped[0] = True
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    owned_processes = {}
    error = None
    try:
        runner.run(ROOT, HERE, output, 'candidate', policy, ENV, verify, owned_processes, lambda: stopped[0], original=ROOT / policy['original_wpt'])
    except BaseException as caught:
        error = repr(caught)
    preservation_error = None
    try:
        assert owned_processes == {}, 'Owned WPT process registry not empty after cleanup'
        verify()
    except BaseException as caught:
        preservation_error = repr(caught)
    if output.exists():
        state.save(output / 'FINAL-DRIVER.json', {'success': error is None and preservation_error is None, 'error': error, 'preservation_error': preservation_error, 'owned_processes': owned_processes, 'native_acceptance': False})
    assert error is None and preservation_error is None, (error, preservation_error)
    print('Installed focused WPT validation passed; no acceptance or canonical mutation')


if __name__ == '__main__':
    main()
