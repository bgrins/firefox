import argparse
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
import time
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def authenticate(policy, binaries=False):
    assert policy['root'] == str(ROOT)
    pins = [policy['manifest'], policy['process_helper'], *policy['resources'].values(),
            *policy['admission'].values(), *policy['harness_files'].values()]
    for pin in pins:
        path = ROOT / pin['path']
        assert path.is_file() and not path.is_symlink() and sha(path) == pin['sha256'], str(path)
    decision = json.loads((ROOT / policy['admission']['ADMISSION-DECISION.json']['path']).read_text())
    assert decision['publisher_signature_verified'] is False
    assert decision['initial_signature_requirement_revised'] is True
    for key in ['platform_security_settings_changed', 'quarantine_changed', 'resigned', 'sandbox_disabled']:
        assert decision[key] is False
    versions = json.loads((ROOT / policy['admission']['VERSIONS.json']['path']).read_text())
    owner = json.loads((ROOT / policy['admission']['OWNER.json']['path']).read_text())
    assert owner['version'] == policy['version']
    for name, pin in policy['binaries'].items():
        assert versions[name]['exit'] == 0 and policy['version'] in versions[name]['output']
        assert versions[name]['command'] == [pin['path'], '--version']
        assert versions[name]['binary_sha256'] == pin['sha256']
        assert Path(pin['path']).is_relative_to(owner['temporary_directory'])
        if binaries:
            path = Path(pin['path'])
            assert path.is_file() and not path.is_symlink() and sha(path) == pin['sha256']
    if binaries:
        info = Path(owner['temporary_directory']).lstat()
        assert [info.st_dev, info.st_ino] == owner['identity'] and stat.S_ISDIR(info.st_mode)
        assert info.st_uid == os.getuid()
    assert len(policy['resources']) == 6 and len(policy['record_kinds']) == 2


def prepare(policy, output, temporary):
    tests, metadata = output / 'tests', output / 'metadata'
    tests.mkdir()
    metadata.mkdir()
    for name, pin in policy['resources'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        target = tests / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / pin['path']).read_bytes())
    (tests / 'tools').symlink_to(ROOT / 'testing/web-platform/tests/tools', target_is_directory=True)
    save(tests / 'config.json', {'ports': {'http': ['auto', 'auto'], 'http-local': ['auto'],
        'http-public': ['auto'], 'https': [], 'https-local': [], 'https-public': [],
        'ws': ['auto'], 'wss': [], 'h2': [], 'webtransport-h3': [], 'dns': []}})
    (metadata / 'MANIFEST.json').write_bytes((ROOT / policy['manifest']['path']).read_bytes())
    (output / 'wptrunner.ini').write_text(
        '[web-platform-tests]\nremote_url = https://github.com/web-platform-tests/wpt.git\nbranch = master\n'
        f'sync_path = {temporary / "unused-sync"}\n[paths]\nrun_info = {metadata}\n'
        f'[manifest:upstream]\ntests = {tests}\nmetadata = {metadata}\nurl_base = /\nmanifest = {metadata / "MANIFEST.json"}\n')
    save(metadata / 'mozinfo.json', {'os': 'mac', 'processor': 'aarch64', 'bits': 64, 'debug': False})
    profile = temporary / 'profile'
    profile.mkdir(mode=0o700)
    return [f'--binary={policy["binaries"]["chrome"]["path"]}',
        f'--webdriver-binary={policy["binaries"]["chromedriver"]["path"]}',
        '--product=chrome', f'--browser-version={policy["version"]}', '--browser-channel=stable',
        '--headless', '--processes=1', '--no-enable-experimental', '--no-install-fonts',
        '--no-manifest-update', '--no-manifest-download', '--ssl-type=none',
        f'--config={output / "wptrunner.ini"}', f'--run-info={metadata}',
        f'--log-raw={output / "raw.jsonl"}', f'--include={policy["page"]}',
        f'--binary-arg=--user-data-dir={profile}']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    policy = json.loads((HERE / 'POLICY.json').read_text())
    authenticate(policy, binaries=args.run)
    if not args.run:
        print('Saved admission and fixture/harness pins authenticate; browser not executed.')
        return 0
    assert policy['execution_enabled'] is True, 'Root activation required'
    output = ROOT / policy['output']
    output.mkdir(mode=0o700)
    temporary = Path(tempfile.mkdtemp(prefix='css-chrome-wpt-', dir='/private/tmp'))
    identity = [temporary.stat().st_dev, temporary.stat().st_ino]
    save(output / 'TEMPORARY.json', {'path': str(temporary), 'identity': identity})
    save(output / 'POLICY.json', policy)
    control = load('chrome_owned_process_control', ROOT / policy['process_helper']['path'])
    assessor = load('chrome_assessor', HERE / 'assess.py')
    collector = load('chrome_records', HERE / 'records.py')
    process, error, code, cleanup, assessment, collection = None, None, None, None, None, None
    stopped = [False]
    def stop(_signal, _frame):
        stopped[0] = True
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop)
    try:
        arguments = prepare(policy, output, temporary)
        directory = output / 'progress-records'
        directory.mkdir(mode=0o700)
        info = directory.stat()
        binding = {'directory': str(directory), 'identity': [info.st_dev, info.st_ino], 'run_id': uuid.uuid4().hex}
        save(output / 'PROGRESS-BINDING.json', binding)
        command = [policy['python'], '-B', str(HERE / 'launch.py'), *arguments]
        save(output / 'COMMAND.json', command)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
                   DURATION_RUNNER_ROOT=str(ROOT), DURATION_CAPABILITIES=str(output / 'CAPABILITIES.jsonl'),
                   DURATION_PROGRESS_RECORD_DIR=str(directory), DURATION_PROGRESS_RUN_ID=binding['run_id'],
                   GIT_OPTIONAL_LOCKS='0', GIT_CEILING_DIRECTORIES=str(temporary))
        for name in ['PYTHONPATH', 'PYTHONHOME']:
            env.pop(name, None)
        with (output / 'wpt.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=temporary, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + policy['watchdog_seconds']
            while process.poll() is None:
                if stopped[0] or time.monotonic() >= deadline:
                    raise RuntimeError('External watchdog or cancellation')
                time.sleep(0.2)
            code = process.returncode
    except BaseException as exc:
        error = repr(exc)
    finally:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, signal.SIG_IGN)
        try:
            cleanup = control.terminate(process)
            assert cleanup['owned_group_absent']
            census = subprocess.run(['ps', '-axo', 'pid=,command='], check=True, capture_output=True, text=True, timeout=10)
            needles = [str(temporary / 'profile'), *[p['path'] for p in policy['binaries'].values()]]
            remaining = [line.strip() for line in census.stdout.splitlines() if any(needle in line for needle in needles)]
            cleanup['remaining_private_browser_commands'] = remaining
            assert not remaining, 'Private browser/driver process remains; retaining temporary profile'
            assert [temporary.stat().st_dev, temporary.stat().st_ino] == identity and not temporary.is_symlink()
            shutil.rmtree(temporary)
            cleanup['temporary_root_removed'] = True
        except BaseException as exc:
            cleanup = {'error': repr(exc), 'temporary_root_removed': False, 'owned_group_absent': False}
        save(output / 'CLEANUP.json', cleanup)
    try:
        assessment = assessor.assess(assessor.read(output / 'raw.jsonl'), policy, code)
        save(output / 'ASSESSMENT.json', assessment)
        if len(assessment['rows']) == 2 and {row.get('subtest') for row in assessment['rows']} == set(policy['expected_names']):
            collection = collector.collect(ROOT, directory, binding, policy, assessment)
            save(output / 'PROGRESS-RECORDS.json', collection)
            assert not collection['errors'], 'Invalid or missing PASS observation record'
        capability_records = [json.loads(line) for line in (output / 'CAPABILITIES.jsonl').read_text().splitlines() if line.strip()]
        assert capability_records, 'No effective Chrome capability receipt'
        launch = load('chrome_launch_filter', HERE / 'launch.py')
        for record in capability_records:
            options = record['effective_capabilities']['goog:chromeOptions']
            assert options['binary'] == policy['binaries']['chrome']['path']
            assert options['args'] == launch.filter_args(record['generated_args'])
            assert '--headless=new' in options['args']
            assert '--user-data-dir=' + str(temporary / 'profile') in options['args']
        authenticate(policy, binaries=True)
        for name, pin in policy['resources'].items():
            assert sha(output / 'tests' / name) == pin['sha256']
    except BaseException as exc:
        error = error or repr(exc)
    complete = error is None and bool(assessment and assessment['complete']) and bool(cleanup.get('owned_group_absent') and cleanup.get('temporary_root_removed'))
    save(output / 'RESULT.json', {'execution_complete': complete, 'browser_exit': code, 'error': error,
        'assessment_complete': bool(assessment and assessment['complete']),
        'records_complete': bool(collection and collection['complete']),
        'all_callbacks_pass': bool(assessment and assessment['all_callbacks_pass']),
        'ordinary_failures_preserved': True, 'publisher_signature_verified': False,
        'no_native_acceptance_or_normative_policy_claim': True})
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
