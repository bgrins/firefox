import collections
import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / 'artifacts/css-named-range-group-order-runtime-20261110-v1'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    assert not (HERE / 'BEFORE.json').exists()
    history = json.loads((ROOT / 'artifacts/css-keyframe-order-history-20261110-v1/RESULT.json').read_text())
    plan = json.loads((ROOT / 'artifacts/css-keyframe-order-history-20261110-v1/PLAN.json').read_text())
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head == history['new_head']
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    sources = {path: sha(ROOT / path) for path in plan['native_paths']}
    for path, digest in sources.items():
        assert hashlib.sha256(git('show', head + ':' + path)).hexdigest() == digest
        assert hashlib.sha256(git('show', plan['old_head'] + ':' + path)).hexdigest() == digest
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    index = hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest()
    config = sha(ROOT / 'mozconfig')
    manifest = json.loads((PRIOR / 'RUN-INPUTS.json').read_text())
    assert sha(PRIOR / 'process.py') == manifest['process.py']
    spec = importlib.util.spec_from_file_location('process', PRIOR / 'process.py')
    process = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(process)
    process.ROOT = ROOT
    save('BEFORE.json', {'head': head, 'sources': sources, 'index': index,
                         'mozconfig_sha256': config,
                         'untracked': untracked.decode().split('\0')[:-1],
                         'process_sha256': manifest['process.py'], 'runner_sha256': sha(Path(__file__))})
    env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZCONFIG=str(ROOT / 'mozconfig'),
               PYTHONDONTWRITEBYTECODE='1', MOZ_HEADLESS='1')
    build = process.run([PYTHON, './mach', 'build', 'binaries', '-j6'], HERE / 'build.log', env, 2400)
    save('BUILD.json', build)
    assert build['exit_code'] == 0 and build['group_absent']
    retained = json.loads((PRIOR / 'runtime-inputs/retained-build.json').read_text())
    binaries = {path: sha(ROOT / path) for path in retained['binaries']}
    app = ROOT / 'objdir-full.noindex/dist/Nightly.app'
    config_ini = configparser.ConfigParser()
    config_ini.read(app / 'Contents/Resources/application.ini')
    suites = ['testing/web-platform/tests/css/css-animations/KeyframeEffect-getKeyframes.tentative.html',
              'testing/web-platform/tests/scroll-animations/css/merge-timeline-offset-keyframes.html',
              'testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html']
    command = [PYTHON, './mach', 'wpt', '--headless', '--processes=1', '--manifest-update',
               '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3',
               '--binary=' + str(app / 'Contents/MacOS/firefox'),
               '--log-raw=' + str(HERE / 'wpt-raw.jsonl'), *suites]
    wpt = process.run(command, HERE / 'wpt.log', dict(env, STYLO_THREADS='1', MOZ_CRASHREPORTER_DISABLE='1'), 1200)
    save('WPT.json', wpt)
    assert wpt['exit_code'] == 0 and wpt['group_absent']
    rows = {}
    for line in (HERE / 'wpt-raw.jsonl').read_text().splitlines():
        event = json.loads(line)
        assert event['action'] not in ['crash', 'assertion_count']
        if event['action'] not in ['test_status', 'test_end']:
            continue
        key = (event['action'], event['test'], event.get('subtest', ''))
        assert key not in rows
        assert event['status'] == event.get('expected', event['status']), event
        rows[key] = event['status']
    selected = {'/' + path.split('/tests/', 1)[1] for path in suites}
    callbacks = json.loads((PRIOR / 'EXPECTED-CALLBACKS.json').read_text())
    expected = {('test_status', *pair) for pair in callbacks if pair[0] in selected}
    expected |= {('test_end', test, '') for test in selected}
    assert set(rows) == expected and len(rows) == 41
    assert collections.Counter(rows.values()) == {'PASS': 36, 'FAIL': 2, 'OK': 3}
    save('WPT-RESULTS.json', {'status': 'PASS', 'records': len(rows), 'counts': dict(collections.Counter(rows.values())),
                              'unexpected': 0, 'raw_sha256': sha(HERE / 'wpt-raw.jsonl')})
    assert git('rev-parse', 'HEAD').decode().strip() == head
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == index
    assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
    assert {path: sha(ROOT / path) for path in sources} == sources
    assert {path: sha(ROOT / path) for path in binaries} == binaries
    assert sha(ROOT / 'mozconfig') == config
    save('build-result.json', {'status': 'pass', 'head': head, 'build_exit': build['exit_code'],
                               'build_id': config_ini['App']['BuildID'], 'version': config_ini['App']['Version'],
                               'sources': sources, 'binaries': binaries, 'mozconfig_sha256': config,
                               'untracked_paths_preserved': len(untracked.split(b'\0')) - 1,
                               'untracked_status_entries_preserved': len(git('status', '--porcelain').splitlines()),
                               'tracked_tree_clean': True, 'left_installed_for_manual_testing': True,
                               'build_log_sha256': sha(HERE / 'build.log'),
                               'known_nonfatal_monitor_keyerrors': (HERE / 'build.log').read_text().count("KeyError: 'export'"),
                               'final_wpt_pending': False, 'final_wpt_results_sha256': sha(HERE / 'WPT-RESULTS.json')})


if __name__ == '__main__':
    main()
