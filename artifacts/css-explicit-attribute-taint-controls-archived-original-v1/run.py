import argparse
import configparser
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
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pins():
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert sha(ROOT / name) == digest, name


def archive(snapshot, policy):
    app = Path(snapshot['application'])
    assert app == Path(policy['archive_application'])
    assert snapshot['source_role'] == policy['archive_role']
    assert snapshot['native_sources'] == policy['native_sources']
    assert not app.is_symlink() and not app.parent.is_symlink()
    actual = {}
    for path in app.rglob('*'):
        assert not path.is_symlink(), path
        if path.is_file():
            actual[str(path.relative_to(app))] = {
                'bytes': path.stat().st_size,
                'mode': stat.S_IMODE(path.stat().st_mode),
                'sha256': sha(path),
            }
    assert actual == snapshot['files'] and len(actual) == policy['archive_files']
    assert sum(record['bytes'] for record in actual.values()) == snapshot['bytes']
    assert sha(ROOT / snapshot['build_receipt']) == snapshot['build_receipt_sha256']
    receipt = json.loads((ROOT / snapshot['build_receipt']).read_text())
    assert receipt['browser_build_performed'] and receipt['command_success'] and receipt['preservation_verified']
    assert receipt['error'] is None
    assert receipt['native_sources'] == snapshot['native_sources']
    assert sha(app / 'Contents/Resources/application.ini') == receipt['application_metadata']['sha256']
    assert receipt['application_metadata']['source_role'] == policy['archive_role']
    assert receipt['application_metadata']['revision'] == policy['build_revision']
    return {'files': len(actual), 'bytes': snapshot['bytes'], 'application': str(app),
            'manifest_sha256': hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest()}


def regular_files(folder):
    return {str(path.relative_to(folder)): sha(path) for path in folder.rglob('*')
            if path.is_file() and not path.is_symlink()}


def prepare(output, policy):
    helper = load('isolated_wpt_inputs', ROOT / policy['wpt_helper'])
    config_path, capture = helper.prepare_inputs(ROOT, output, policy['settings'], policy['source_role'])
    assert capture is None
    shutil.copytree(HERE / 'support', output / 'support')
    run_info = output / 'run-info'
    run_info.mkdir()
    shutil.copyfile(HERE / 'support/mozinfo.json', run_info / 'mozinfo.json')
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)
    config['paths']['run_info'] = str(run_info)
    config['paths']['prefs'] = str(output / 'support/profiles')
    config['paths'].pop('ws_extra', None)
    with config_path.open('w') as stream:
        config.write(stream)
    expected_link = ROOT / 'testing/web-platform/tests/tools'
    assert (output / 'tests/tools').is_symlink()
    assert (output / 'tests/tools').resolve() == expected_link
    return config_path


def command(output, temporary, policy, snapshot):
    app = Path(snapshot['application'])
    args = [policy['python'], '-B', str(HERE / 'entry.py'), '--product=firefox',
            '--headless', '--processes=1', '--test-types=testharness',
            '--no-pause-after-test', '--no-preload-browser', '--no-manifest-update',
            '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3',
            '--no-enable-dns', '--binary=' + str(app / 'Contents/MacOS/firefox'),
            '--certutil-binary=' + str(app / 'Contents/MacOS/certutil'),
            '--specialpowers-path=' + str(output / 'support/specialpowers.xpi'),
            '--config=' + str(output / 'wptrunner.ini'),
            '--run-info=' + str(output / 'run-info'),
            '--prefs-root=' + str(output / 'support/profiles'), '--ssl-type=pregenerated',
            '--ca-cert-path=' + str(output / 'support/certs/cacert.pem'),
            '--host-key-path=' + str(output / 'support/certs/web-platform.test.key'),
            '--host-cert-path=' + str(output / 'support/certs/web-platform.test.pem'),
            '--log-raw=' + str(output / 'raw.jsonl')]
    args.extend('--include=' + page for page in json.loads((ROOT / policy['roster']).read_text()))
    env = dict(os.environ, TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
               PYTHONDONTWRITEBYTECODE='1', MOZ_DISABLE_SAFE_MODE_KEY='1',
               MOZ_DISABLE_UPDATE_PROCESSING='1')
    for name in ['MOZ_GMP_PATH', 'MOZ_LOG_FILE', 'MOZ_PROFILER_SHUTDOWN', 'XPCOM_MEM_BLOAT_LOG']:
        env.pop(name, None)
    return args, env


def assess(events, roster, code=None):
    assert len(roster) == 4 and sum(map(len, roster.values())) == 47
    assert all(len(names) == len(set(names)) for names in roster.values())
    expected = {(page, name) for page, names in roster.items() for name in names}
    statuses = [e for e in events if e.get('action') == 'test_status']
    endings = [e for e in events if e.get('action') == 'test_end']
    counts = {}
    for event in statuses:
        counts[event['status']] = counts.get(event['status'], 0) + 1
    complete = (len(statuses) == 47
                and {(e['test'], e['subtest']) for e in statuses} == expected
                and all(e['status'] in ['PASS', 'FAIL'] for e in statuses)
                and len(endings) == 4 and {e['test'] for e in endings} == set(roster)
                and all(e['status'] == 'OK' for e in endings)
                and sum(e.get('action') == 'suite_start' for e in events) == 1
                and sum(e.get('action') == 'suite_end' for e in events) == 1)
    checks = load('archived_wpt_checks', ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py')
    complete = complete and checks.lifecycle(events, {'expected_subtests': {page: [] for page in roster}, 'reftests': []})
    complete = complete and not checks.infrastructure_faults(events)
    complete = complete and all(sum(e.get('action') == 'test_start' and e.get('test') == page for e in events) == 1 for page in roster)
    complete = complete and sum(e.get('action') == 'test_start' for e in events) == 4
    complete = complete and not any(e.get('action') == 'crash' for e in events)
    if code is not None:
        complete = complete and checks.exit_matches_results(code, statuses + endings)
    return {'complete': bool(complete), 'counts': counts, 'subtests': statuses, 'endings': endings,
            'all_47_pass': bool(complete and all(e['status'] == 'PASS' for e in statuses)),
            'prediction': None, 'prediction_is_acceptance_gate': False,
            'native_fix_acceptance': False}


def run(policy):
    assert policy['execution_enabled'], 'disabled preparation'
    assert not policy['pending_binding']
    assert policy['source_role'] in ('archived-original','archived-candidate')
    assert policy['prior_owner_terminal'] and policy['prior_owner_audit']
    pins()
    for key in ('prior_owner_terminal','prior_owner_audit'):
        record = policy[key]
        assert sha(ROOT / record['path']) == record['sha256']
    terminal = json.loads((ROOT / policy['prior_owner_terminal']['path']).read_text())
    audit = json.loads((ROOT / policy['prior_owner_audit']['path']).read_text())
    assert terminal['terminal'] and terminal['exit'] in (0,1)
    assert audit['independent_live_restoration_verified']
    assert audit['owner_result_sha256'] == terminal['result_sha256']
    assert sha(ROOT / policy['snapshot']) == policy['snapshot_sha256']
    snapshot = json.loads((ROOT / policy['snapshot']).read_text())
    before = archive(snapshot, policy)
    output = ROOT / policy['runtime']
    assert output.parent == ROOT / 'artifacts' and not output.exists() and not output.is_symlink()
    output.mkdir()
    save(output / 'ARCHIVE-PRE.json', before)
    prepare(output, policy)
    staged = regular_files(output)
    staged_trees = {name: regular_files(output / name) for name in
                    ['tests', 'metadata', 'mozilla-tests', 'mozilla-metadata', 'support', 'run-info']}
    save(output / 'STAGED.json', staged)
    save(output / 'STAGED-TREES.json', staged_trees)
    temporary = Path(tempfile.mkdtemp(prefix='css-explicit-taint-controls-' + policy['archive_role'] + '-', dir='/private/tmp'))
    identity = (temporary.stat().st_dev, temporary.stat().st_ino)
    args, env = command(output, temporary, policy, snapshot)
    save(output / 'COMMAND.json', {'command': args, 'temporary': str(temporary),
                                  'identity': identity, 'timeout_seconds': policy['timeout_seconds']})
    control = load('isolated_wpt_control', ROOT / policy['control_helper'])
    process, code, error, cleanup = None, None, None, None
    def cancelled(signum, frame):
        raise InterruptedError(signum)
    signal.signal(signal.SIGTERM, cancelled)
    signal.signal(signal.SIGINT, cancelled)
    try:
        with (output / 'wpt.log').open('x') as stream:
            process = subprocess.Popen(args, cwd=output, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            code = process.wait(timeout=policy['timeout_seconds'])
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
            assert not temporary.is_symlink() and (temporary.stat().st_dev, temporary.stat().st_ino) == identity
            shutil.rmtree(temporary)
            cleanup['temporary_root_removed'] = not temporary.exists()
        except BaseException as exc:
            error = error or repr(exc)
        save(output / 'CLEANUP.json', cleanup)
    result = {'exit': code, 'execution_error': error, 'success': False,
              'source_role': policy['source_role'], 'native_fix_acceptance': False}
    try:
        after = archive(snapshot, policy)
        save(output / 'ARCHIVE-POST.json', after)
        assert before == after
        pins()
        assert all(sha(output / name) == digest for name, digest in staged.items())
        assert all(regular_files(output / name) == files for name, files in staged_trees.items())
        assert (output / 'tests/tools').is_symlink()
        assert (output / 'tests/tools').resolve() == ROOT / 'testing/web-platform/tests/tools'
        events = [json.loads(line) for line in (output / 'raw.jsonl').read_text().splitlines()]
        assessment = assess(events, json.loads((ROOT / policy['roster']).read_text()), code)
        save(output / 'ASSESSMENT.json', assessment)
        result.update(archive_preserved=True, staged_preserved=True,
                      success=bool(error is None and code in (0, 1) and assessment['complete']
                                   and cleanup and cleanup.get('temporary_root_removed')))
    except BaseException as exc:
        result['verification_error'] = repr(exc)
    save(output / 'RESULT.json', result)
    assert result['success'], result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true', required=True)
    parser.add_argument('--role', choices=['original'], required=True)
    args = parser.parse_args()
    run(json.loads((HERE / ('POLICY-' + args.role + '.json')).read_text()))
