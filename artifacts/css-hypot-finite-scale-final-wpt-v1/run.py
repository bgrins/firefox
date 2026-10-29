import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 2
    assert sha(HERE / 'FILES.json') == sys.argv[1]
    policy = read(HERE / 'POLICY.json')
    assert policy['execution_enabled'] and policy['activation_pending'] == []
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'MOZ_ARTIFACT_BUILDS', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_PROFILE'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    owner = load('final_owner', policy['ownership_helper'])
    state = load('final_state', policy['state_helper'])
    owner.authenticate(HERE, sys.argv[1])
    assert policy['baseline_receipts'] and policy['build_receipts']
    references = {**policy['references'], **policy['baseline_receipts'], **policy['build_receipts']}
    for name, pin in references.items():
        assert sha(ROOT / name) == pin, name
    for directory, pin in policy['packages'].items():
        owner.authenticate(ROOT / directory, pin)
    owner.authenticate(ROOT / policy['installation_package'], policy['installation_manifest'])
    owner.authenticate(ROOT / policy['build_package'], policy['build_manifest'])
    controls = {n: (RUNTIME / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}
    assert {n: hashlib.sha256(body).hexdigest() for n, body in controls.items()} == policy['controls']
    epoch = json.loads(controls['CURRENT-EPOCH.json'])
    assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
    source = policy['source']
    transition = epoch['hypot_finite_scale_transition']
    assert transition['compiled'] and not transition['accepted'] and transition['role'] == 'candidate'
    assert transition['manifest_sha256'] == policy['installation_manifest']
    assert transition['source_sha256'] == source['candidate_sha256']
    assert epoch['modified_native_paths'] == sorted(['servo/components/style/custom_properties.rs', source['path']])
    for name, expected in policy['accepted_preservation_markers'].items():
        assert epoch[name] == expected
    for name, expected in policy['accepted_transitions'].items():
        assert epoch[name] == expected
    for name, record in policy['accepted_current_payloads'].items():
        expected = source['candidate_sha256'] if name == source['path'] else record['sha256']
        assert epoch['pins'][name] == expected
        owner.claim(ROOT, name, expected, record['identity'])
    assert len(policy['accepted_current_payloads']) == 27
    for name, record in policy['tests'].items():
        assert epoch['pins'][name] == record['sha256']
        owner.claim(ROOT, name, record['sha256'], epoch['installed_identities'][name])
        assert json.loads(controls['OWNED.json'])[name]['owned_sha256'] == record['sha256']
    build = ROOT / policy['build_runtime']
    result, inner = read(build / 'RESULT.json'), read(build / 'build-RESULT.json')
    assert result['command_success'] and result['preservation_verified'] and result['error'] is None
    assert not result['publication_errors'] and not result['owned_processes'] and not result['accepted']
    assert inner['exit'] == 0 and inner['owned_group_absent'] and not inner['cleanup_errors']
    assert inner['error'] is None and inner['stop_reason'] is None
    assert (build / 'EPOCH.json').read_bytes() == controls['CURRENT-EPOCH.json']
    for name in ('build-PROCESS.json', 'WAKE-PROCESS.json'):
        owner.group_absent(read(build / name)['pgid'])
    baseline = ROOT / policy['baseline_runtime']
    base_result = read(baseline / 'BASELINE-RESULT.json')
    assert base_result['success'] and base_result['preservation_verified'] and not base_result['canonical_updated']
    original = baseline / 'original-wpt'
    assert read(original / 'RESULT.json')['success'] and read(original / 'RESULT.json')['preservation_verified']
    assert read(original / 'PRE.json') == read(original / 'POST.json')
    assert read(original / 'CLEANUP.json')['owned_group_absent'] and read(original / 'CLEANUP.json')['temporary_root_removed']
    owner.group_absent(read(original / 'PROCESS.json')['pgid'])
    original_settings = read(original / 'ASSESSMENT-POLICY.json')
    for key, expected in policy['wpt'].items():
        if key == 'resources':
            changed = dict(original_settings[key])
            fixture = 'css/css-values/hypot-finite-scale.html'
            assert changed[fixture]['sha256'] == expected[fixture]['sha256']
            changed[fixture] = expected[fixture]
            assert changed == expected
        else:
            assert original_settings[key] == expected, key
    fixture = 'css/css-values/hypot-finite-scale.html'
    installed = ROOT / policy['wpt']['resources'][fixture]['path']
    assert installed.read_bytes() == (original / 'tests' / fixture).read_bytes()
    assert sha(installed) == '0be27ef03f09ea3429ec27f0d6ea3906b6112689cf92b81db19ccad92269f0fc'
    assert policy['wpt']['harness_revision'] == policy['head']
    assert read(original / 'APPLICATION-METADATA.json')['harness_revision'] == policy['head']
    assert read(build / 'APPLICATION-METADATA.json')['revision'] == policy['head']
    for name in policy['rebuilt_binaries']:
        assert sha(ROOT / name) == epoch['pins'][name]
    owner.quiescent(RUNTIME)
    assert not os.path.lexists(RUNTIME / 'SOURCE-TRANSITION.lock')
    flags = {name: state.h.git(path, env, 'ls-files', '-v', '-z') for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]}
    def verify():
        owner.authenticate(HERE, sys.argv[1])
        assert all((RUNTIME / n).read_bytes() == body for n, body in controls.items())
        assert all(sha(ROOT / n) == pin for n, pin in references.items())
        for name in policy['preserved_absent_metadata']:
            assert not os.path.lexists(ROOT / name) and epoch['pins'][name] is None
        assert sha(installed) == policy['wpt']['resources'][fixture]['sha256']
        for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
            assert state.h.git(path, env, 'ls-files', '-v', '-z') == flags[name]
        return state.a.verify_current(state.h, ROOT, env, epoch)
    before = verify()
    output = ROOT / policy['runtime_output']
    assert output.parent == ROOT / 'artifacts' and not os.path.lexists(output)
    output.mkdir()
    state.save(output / 'PRE.json', before)
    state.save(output / 'BINDINGS.json', {'controls': policy['controls'], 'baseline_receipts': policy['baseline_receipts'], 'build_receipts': policy['build_receipts'], 'source': source, 'fixture_sha256': sha(installed)})
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    lint = output / 'lint'
    lint.mkdir()
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'lint', '--linter', 'wpt', '--include-third-party', str(installed.relative_to(ROOT))]
    state.save(lint / 'COMMAND.json', {'command': command, 'timeout_seconds': policy['lint_timeout_seconds']})
    process, code, error, cleanup = None, None, None, None
    control = load('final_lint_control', policy['wpt']['control_helper'])
    try:
        with (lint / 'output.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            state.save(lint / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + policy['lint_timeout_seconds']
            while process.poll() is None:
                assert not stopped[0] and time.monotonic() < deadline, 'Lint cancelled or timed out'
                time.sleep(0.2)
            code = process.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
        except BaseException as exc:
            error = error or repr(exc)
        state.save(lint / 'CLEANUP.json', cleanup)
    preserved = verify() == before
    state.save(lint / 'RESULT.json', {'exit': code, 'error': error, 'preservation_verified': preserved, 'success': code == 0 and error is None and preserved})
    assert code == 0 and error is None and preserved and cleanup['owned_group_absent']
    runner = load('final_wpt', str((HERE / 'wpt.py').relative_to(ROOT)))
    owned = {}
    phase = runner.run(ROOT, HERE, output / 'candidate-wpt', 'candidate', policy, env, verify, owned, lambda: stopped[0], original=original)
    assert not owned and verify() == before
    state.save(output / 'POST.json', before)
    state.save(output / 'RESULT.json', {'success': True, 'phase': phase, 'preservation_verified': True, 'owned_processes': owned, 'lint_passed': True, 'native_fix_acceptance': False, 'canonical_updated': False})
    print('Installed corrected WPT lint and final227 comparison complete; acceptance remains separate', flush=True)


if __name__ == '__main__':
    main()
