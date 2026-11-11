import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / 'objdir-full.noindex/dist/Nightly.app'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
EXTRAS = ['objdir-full.noindex/dist/bin/gtest/XUL', 'objdir-full.noindex/build/application.ini', 'objdir-full.noindex/_tests/web-platform/wptrunner.local.ini']
sys.dont_write_bytecode = True


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


bundle, process, analyze = module('bundle'), module('process'), module('analyze')
process.ROOT = ROOT
sha = bundle.sha


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT)


def exists(path):
    return path.exists() or path.is_symlink()


def verify_test_inputs():
    for path, expected in json.loads((HERE / 'runtime-inputs/test-source-pins.json').read_text()).items():
        if expected is None:
            assert not exists(ROOT / path), ('unexpected test metadata', path)
        else:
            assert sha(ROOT / path) == expected, ('test input changed', path)


def main():
    assert sys.flags.isolated and not sys.flags.optimize, 'Run python -I, without -O'
    mode, name, *prior = sys.argv[1:]
    assert mode in ['baseline', 'candidate'] and len(prior) == (mode == 'candidate')
    assert all(Path(n).name == n and n not in ['.', '..'] for n in [name, *prior])
    for path, expected in json.loads((HERE / 'RUN-INPUTS.json').read_text()).items():
        assert sha(HERE / path) == expected, ('changed runner input', path)
    plan = json.loads((HERE / 'RUN-PLAN.json').read_text())
    roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())
    assert git('rev-parse', 'HEAD').decode().strip() == plan['head'], 'HEAD changed; review/re-pin'
    assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
    assert sha(ROOT / 'mozconfig') == plan['mozconfig_sha256']
    for path, role in roles.items():
        assert sha(ROOT / path) == sha(HERE / 'source' / path) == role['base']
        assert sha(HERE / 'candidate' / path) == role['candidate']
    retained = json.loads((HERE / 'runtime-inputs/retained-build.json').read_text())
    assert all(sha(ROOT / path) == expected for path, expected in retained['binaries'].items())
    fixtures = {ROOT / path: HERE / 'runtime-inputs' / filename for path, filename in plan['fixtures'].items()}
    verify_test_inputs()
    metadata = [ROOT / (str(p.relative_to(ROOT)).replace('/tests/', '/meta/', 1) + '.ini') for p in fixtures]
    assert all(not exists(p) for p in [*fixtures, *metadata])
    baseline = None
    if prior:
        previous = HERE / prior[0]
        receipt = json.loads((previous / 'RESULT.json').read_text())
        assert receipt['mode'] == 'baseline' and receipt['restoration_verified'] and receipt['error'] is None
        assert receipt['runner_inputs_sha256'] == sha(HERE / 'RUN-INPUTS.json')
        assert receipt['head'] == plan['head'] and receipt['sampled_binaries'] == retained['binaries']
        baseline = json.loads((previous / 'TEST-RESULTS.json').read_text())
    output = HERE / name
    output.mkdir()
    lock = HERE / 'runtime.lock'
    with lock.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        execute(mode, output, plan, roles, retained, fixtures, metadata, baseline)
    finally:
        if not process.ACTIVE:
            lock.unlink()


def execute(mode, output, plan, roles, retained, fixtures, metadata, baseline):
    index = hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest()
    app_before = bundle.scan(APP)
    extras = {p: bundle.entry(ROOT / p) for p in EXTRAS}
    assert all(row['kind'] == 'file' for row in extras.values())
    backup_size = sum(row.get('size', 0) for row in app_before.values()) + sum(row['size'] for row in extras.values())
    assert shutil.disk_usage(ROOT).free - backup_size > 10 * 1024**3
    backups = output / 'backups'
    backups.mkdir()
    app_map = bundle.backup(APP, app_before, backups / 'app')
    extra_map = bundle.backup(ROOT, extras, backups / 'extras')
    save(output / 'BEFORE.json', {'head': plan['head'], 'index': index, 'sources': roles, 'app': app_before, 'extras': extras, 'backup_bytes': backup_size, 'retained_build': retained})
    save(output / 'BACKUPS.json', {'app': app_map, 'extras': extra_map})
    env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZCONFIG=str(ROOT / 'mozconfig'), PYTHONDONTWRITEBYTECODE='1', MOZ_HEADLESS='1')
    touched, installed, results = {}, {}, {}
    failure = None
    restore_errors = []
    binaries = comparison = None

    def cancel(*_):
        raise KeyboardInterrupt('Diagnostic cancelled')

    signal.signal(signal.SIGTERM, cancel)
    try:
        if mode == 'candidate':
            for path, role in roles.items():
                assert sha(ROOT / path) == role['base']
                try:
                    (ROOT / path).write_bytes((HERE / 'candidate' / path).read_bytes())
                finally:
                    touched[path] = sha(ROOT / path)
        for path, fixture in fixtures.items():
            assert not exists(path)
            try:
                with path.open('xb') as stream:
                    stream.write(fixture.read_bytes())
            finally:
                if exists(path):
                    installed[path] = sha(path)
        if mode == 'candidate':
            try:
                results['build'] = process.run([PYTHON, './mach', 'build', 'binaries', '-j6'], output / 'build.log', env, 2400)
            finally:
                save(output / 'BUILD.json', {'command_result': results.get('build'), 'head': plan['head'], 'source_sha256': {p: sha(ROOT / p) for p in roles}, 'mozconfig_sha256': sha(ROOT / 'mozconfig'), 'binaries': {p: sha(ROOT / p) for p in retained['binaries'] if (ROOT / p).is_file()}, 'debug_gate': plan['debug_gate']})
            assert results['build']['exit_code'] == 0, 'candidate build failed'
        else:
            results['build'] = {'skipped': True, 'reason': 'Retained baseline binary; no rebuild', 'retained_build_receipt': retained}
            save(output / 'BUILD.json', results['build'])
        binaries = {p: sha(ROOT / p) for p in retained['binaries']}
        save(output / 'SAMPLED-BINARIES.json', binaries)
        command = [PYTHON, './mach', 'wpt', '--headless', '--processes=1', '--manifest-update', '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3', f'--binary={APP / "Contents/MacOS/firefox"}', f'--log-raw={output / "wpt-raw.jsonl"}', *plan['suites']]
        results['wpt'] = process.run(command, output / 'wpt.log', dict(env, STYLO_THREADS='1', MOZ_CRASHREPORTER_DISABLE='1'), 1800)
        save(output / 'WPT.json', results['wpt'])
        assert results['wpt']['exit_code'] in (0, 1)
        assert {p: sha(ROOT / p) for p in binaries} == binaries
        parsed = analyze.parse(output / 'wpt-raw.jsonl')
        save(output / 'TEST-RESULTS.json', parsed)
        if baseline is not None:
            comparison = analyze.compare(baseline, parsed)
            save(output / 'COMPARISON.json', comparison)
            assert comparison['identical_callback_statuses_and_inventory'], 'baseline/candidate callbacks differ'
    except BaseException:
        failure = traceback.format_exc()
        save(output / 'FAILURE.json', {'traceback': failure})
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        restore(mode, output, plan, roles, retained, fixtures, metadata, touched, installed, app_before, extras, backups, app_map, extra_map, index, backup_size, restore_errors)
    save(output / 'RESULT.json', {'mode': mode, 'head': plan['head'], 'runner_inputs_sha256': sha(HERE / 'RUN-INPUTS.json'), 'sampled_binaries': binaries, 'commands': results, 'error': failure, 'restoration_verified': not restore_errors, 'restoration_errors': restore_errors, 'comparison': comparison, 'native_fix_acceptance': False, 'debug_gate': plan['debug_gate']})
    if failure or restore_errors:
        raise RuntimeError('Diagnostic incomplete; inspect failure/restoration receipts')


def restore(mode, output, plan, roles, retained, fixtures, metadata, touched, installed, app_before, extras, backups, app_map, extra_map, index, backup_size, errors):
    if process.ACTIVE:
        errors.append('Owned process group not quiescent; restoration deferred and backups retained')
    else:
        def step(label, operation):
            try:
                operation()
            except BaseException:
                errors.append(label + ': ' + traceback.format_exc())

        for path, written in touched.items():
            def restore_source(path=path, written=written):
                assert sha(ROOT / path) == written, 'concurrent source edit'
                (ROOT / path).write_bytes((HERE / 'source' / path).read_bytes())
            step(path, restore_source)
        for path, written in installed.items():
            def remove_fixture(path=path, written=written):
                assert sha(path) == written, 'concurrent fixture edit'
                path.unlink()
            step(str(path), remove_fixture)
        def restore_app():
            if not exists(APP):
                APP.mkdir()
            bundle.restore(APP, app_before, bundle.scan(APP), backups / 'app', app_map)
        step('application', restore_app)
        for path, original in extras.items():
            def restore_extra(path=path, original=original):
                current = bundle.entry(ROOT / path) if exists(ROOT / path) else None
                if current is None or bundle.semantic({path: current}) != bundle.semantic({path: original}):
                    bundle.restore_file(ROOT / path, current, backups / 'extras' / extra_map[path], original, ROOT)
            step(path, restore_extra)
        def verify():
            assert bundle.semantic(bundle.scan(APP)) == bundle.semantic(app_before)
            assert bundle.semantic({p: bundle.entry(ROOT / p) for p in extras}) == bundle.semantic(extras)
            assert all(not exists(p) for p in [*fixtures, *metadata])
            assert git('rev-parse', 'HEAD').decode().strip() == plan['head']
            assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == index
            assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
            assert all(sha(ROOT / p) == role['base'] for p, role in roles.items())
            assert {p: sha(ROOT / p) for p in retained['binaries']} == retained['binaries']
            assert sha(ROOT / 'mozconfig') == plan['mozconfig_sha256']
            verify_test_inputs()
        step('verification', verify)
    if not errors:
        try:
            shutil.rmtree(backups)
            save(output / 'RESTORED.json', {'source_and_application_restored': True, 'index_preserved': True, 'temporary_fixtures_removed': True, 'backup_removed': True, 'backup_bytes': backup_size})
        except BaseException:
            errors.append('backup cleanup/receipt: ' + traceback.format_exc())
    if errors:
        save(output / 'RESTORATION-FAILURE.json', {'errors': errors, 'backups_retained': str(backups)})


if __name__ == '__main__':
    main()
