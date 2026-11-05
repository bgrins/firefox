import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    assert len(sys.argv) == 3 and sys.argv[1] == '--run'
    assert sha(HERE / 'CONFIG.json') == sys.argv[2]
    config = read(HERE / 'CONFIG.json')
    assert config['execution_enabled']
    for name, digest in config['helper_hashes'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in config['browser_hashes'].items():
        assert sha(ROOT / config['browser_directory'] / name) == digest, name
    baseline_build = ROOT / config['baseline_build']['path']
    assert sha(baseline_build) == config['baseline_build']['sha256']
    baseline_result = read(baseline_build)
    assert baseline_result['terminal_exit'] == 0
    assert baseline_result['sources'] == config['library_sources']
    assert baseline_result['head'] == config['baseline_build_revision']
    assert baseline_result['all_source_pins'] == config['baseline_sources']
    for name, digest in baseline_result['binaries'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in config['baseline_evidence'].items():
        assert sha(ROOT / name) == digest, name
    for path in config['baseline_observations']:
        assert path in config['baseline_evidence']
        baseline_observation = read(ROOT / path)
        assert baseline_observation['source_role'] == 'baseline'
        assert baseline_observation['complete_observation'] and baseline_observation['safe_to_continue']
        assert baseline_observation['supplemental_audit_passed'] and baseline_observation['all_pass']
    for name, digest in config['context_sources'].items():
        assert sha(ROOT / name) == digest, name
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
        'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC_WRAPPER'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
        MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZCONFIG=str(ROOT / 'mozconfig'),
        MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'), MOZ_HEADLESS='1')
    git = lambda *args: subprocess.check_output(
        ['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=env)
    roles = read(ROOT / config['source_roles'])
    assert git('rev-parse', 'HEAD').decode().strip() == config['expected_head']
    git('merge-base', '--is-ancestor', config['baseline_build_revision'], config['expected_head'])
    revision_range = config['baseline_build_revision'] + '..' + config['expected_head']
    intervening_paths = set(git('log', '--format=', '--name-only', revision_range).decode().splitlines()) - {''}
    intervening_paths.update(git('diff', '--name-only', config['baseline_build_revision'], config['expected_head']).decode().splitlines())
    assert all(name.startswith('artifacts/') for name in intervening_paths), intervening_paths
    native_changes = {n for n in git('diff', 'HEAD', '--name-only').decode().splitlines()
                      if not n.startswith('artifacts/')}
    assert native_changes == set(config['expected_initial_native_changes'])
    for name, digest in config['library_sources'].items():
        assert sha(ROOT / name) == digest, name
    originals = {name: (ROOT / name).read_bytes() for name in roles}
    identities = {}
    for name, role in roles.items():
        path = ROOT / name
        assert stat.S_ISREG(path.lstat().st_mode)
        assert sha(path) == role['base_sha256'], name
        assert sha(ROOT / role['candidate_capture']) == role['candidate_sha256']
        identities[name] = [path.stat().st_dev, path.stat().st_ino]
    unchanged_diff_args = ['diff', '--binary', '--', '.', *[':(exclude)' + n for n in roles]]
    before = {key: hashlib.sha256(git(*args)).hexdigest() for key, args in {
        'index_entries': ['ls-files', '--stage', '-z'],
        'cached_diff': ['diff', '--cached', '--binary'],
        'unrelated_working_diff': unchanged_diff_args,
    }.items()}
    lock = ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock'
    assert not lock.exists() and not lock.is_symlink()
    output = ROOT / config['output']
    assert output.parent == ROOT / 'artifacts' and not output.exists()
    output.mkdir()
    save(output / 'BEFORE.json', {'head':config['expected_head'], 'git':before,
        'sources':{n:sha(ROOT / n) for n in roles}, 'library_sources':config['library_sources'],
        'identities':identities, 'baseline_build_revision':config['baseline_build_revision'],
        'intervening_artifact_paths':sorted(intervening_paths),
        'config_sha256':sys.argv[2], 'runner_sha256':sha(Path(__file__))})
    bundle = load('local_bundle', config['helpers']['bundle_helper'])
    builder = load('local_builder', config['helpers']['phase_helper'])
    process_control = load('local_process_control', config['helpers']['process_helper'])
    browser = load('local_browser', config['browser_directory'] + '/run.py')
    app = ROOT / config['app_path']
    app_before = bundle.scan(app)
    extras = {n:bundle.entry(ROOT / n) for n in config['extra_paths']}
    size = sum(r['size'] for r in app_before.values() if r['kind'] == 'file') + sum(r['size'] for r in extras.values())
    fs = os.statvfs(ROOT)
    assert fs.f_bavail * fs.f_frsize - size >= 27 * 1024**3
    save(output / 'APP-BEFORE.json', app_before)
    save(output / 'EXTRAS-BEFORE.json', extras)
    backups = output / 'backups'
    backups.mkdir()
    app_map = bundle.backup(app, app_before, backups / 'app')
    extra_map = bundle.backup(ROOT, extras, backups / 'extra')
    backup_inventory = bundle.scan(backups)
    save(output / 'BACKUPS.json', {'app':app_map, 'extras':extra_map, 'inventory':backup_inventory, 'bytes':size})
    with lock.open('x') as stream:
        json.dump({'pid':os.getpid(), 'runtime':config['output'], 'operation':config['operation']}, stream)
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    stopped = [False]
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stopped.__setitem__(0, True))
    owned, errors, touched, written = {}, [], [], {}
    failure, result = None, None

    def verify_sources(candidate):
        for name, role in roles.items():
            path = ROOT / name
            assert [path.stat().st_dev, path.stat().st_ino] == identities[name]
            assert sha(path) == role['candidate_sha256' if candidate else 'base_sha256'], name
        for name, digest in config['library_sources'].items():
            assert sha(ROOT / name) == digest, name
        for name, digest in config['context_sources'].items():
            assert sha(ROOT / name) == digest, name
        assert git('rev-parse', 'HEAD').decode().strip() == config['expected_head']
        assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == before['index_entries']
        assert hashlib.sha256(git('diff', '--cached', '--binary')).hexdigest() == before['cached_diff']
        assert hashlib.sha256(git(*unchanged_diff_args)).hexdigest() == before['unrelated_working_diff']

    try:
        verify_sources(False)
        for name, role in roles.items():
            path = ROOT / name
            assert [path.stat().st_dev, path.stat().st_ino] == identities[name]
            assert sha(path) == role['base_sha256']
            touched.append(name)
            try:
                with path.open('wb') as stream:
                    stream.write((ROOT / role['candidate_capture']).read_bytes())
            finally:
                assert [path.stat().st_dev, path.stat().st_ino] == identities[name]
                written[name] = sha(path)
        verify_sources(True)
        build = output / 'build'
        build.mkdir()
        deadline = time.monotonic() + config['build_timeout_seconds']
        builder.run(ROOT, ROOT / 'objdir-full.noindex', build, env,
            lambda: stopped[0] or time.monotonic() >= deadline, owned, process_control,
            ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2'], errors)
        assert not owned and not errors
        verify_sources(True)
        binary_pins = {n:sha(ROOT / n) for n in config['browser_binary_paths']}
        xul = str(Path(config['browser_binary']).parent / 'XUL')
        assert binary_pins[xul] != baseline_result['binaries'][xul], 'Candidate XUL was not rebuilt'
        source_pins = {n:sha(ROOT / n) for n in roles} | config['library_sources'] | config['context_sources']
        pins = {'execution_enabled':True, 'source_role':config['browser_source_role'], 'repetitions':2, 'binary':config['browser_binary'],
            'build_revision':config['expected_head'], 'harness_revision':config['expected_head'],
            'files':binary_pins | source_pins}
        save(output / 'BUILT.json', {'sources':{n:sha(ROOT / n) for n in roles},
            'library_sources':config['library_sources'], 'binaries':binary_pins})
        result = browser.run(ROOT, output / 'browser', pins, lambda:stopped[0])
        verify_sources(True)
    except BaseException:
        failure = traceback.format_exc()
        save(output / 'FAILURE.json', {'traceback':failure})
    finally:
        assert not owned, 'Build process cleanup incomplete; leave source/app for recovery'
        assert not browser.active_processes(), 'Browser process cleanup incomplete; leave source/app for recovery'
        save(output / 'SOURCE-WRITES.json', written)
        for name in reversed(touched):
            path = ROOT / name
            assert [path.stat().st_dev, path.stat().st_ino] == identities[name]
            assert name in written and sha(path) == written[name]
            with path.open('wb') as stream:
                stream.write(originals[name])
        app_after = bundle.scan(app)
        bundle.restore(app, app_before, app_after, backups / 'app', app_map)
        for name, old in extras.items():
            path = ROOT / name
            current = bundle.entry(path) if path.exists() or path.is_symlink() else None
            if current is None or bundle.semantic({name:current}) != bundle.semantic({name:old}):
                bundle.restore_file(path, current, backups / 'extra' / extra_map[name], old, ROOT)
        verify_sources(False)
        assert bundle.semantic(bundle.scan(app)) == bundle.semantic(app_before)
        assert bundle.semantic({n:bundle.entry(ROOT / n) for n in extras}) == bundle.semantic(extras)
        assert [lock.stat().st_dev, lock.stat().st_ino] == lock_identity
        lock.unlink()
        assert bundle.scan(backups) == backup_inventory
        shutil.rmtree(backups)
        save(output / 'RESTORED.json', {'source_and_application_restored':True,
            'library_patch_preserved':True, 'staged_research_preserved':True,
            'backup_removed':True, 'backup_bytes':size, 'source_transition_lock_absent':True})
    save(output / 'RESULT.json', {'experiment':result, 'error':failure,
        'native_fix_acceptance':False, 'restoration_verified':True})
    if result is not None and not (result['complete_observation'] and result['validation_passed'] and result['safe_to_continue']):
        raise RuntimeError('Browser observation incomplete; original state restored; see RESULT.json')
    if failure:
        raise RuntimeError('Experiment failed; original state restored; see FAILURE.json')


if __name__ == '__main__':
    main()
