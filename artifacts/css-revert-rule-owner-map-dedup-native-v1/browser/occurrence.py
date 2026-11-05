import argparse
from collections import Counter
import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

ADAPTER = Path(__file__).resolve().parent
HERE = ADAPTER.parents[2] / 'artifacts/css-revert-rule-occurrence-local-wpt-v1'
FIXTURE_SEAL = 'bf8cd5aa6a15022bdcb96f440489b4c1c47cf7bd5c1a2af4952409e33d5eda8d'
_owned = {}


def active_processes():
    return tuple(sorted(_owned))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def load_helpers(root):
    result = {}
    for name, row in json.loads((HERE / 'HELPERS.json').read_bytes()).items():
        path = root / row['path']
        assert sha(path) == row['sha256'], name
        spec = importlib.util.spec_from_file_location('rollback_' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result[name] = module
    return result


def assess(events, parsed, code, expected, policy, binding):
    errors, rows, opened, ended = [], [], set(), set()
    counts = Counter()
    suite_started = suite_ended = False
    for event in events:
        action = event.get('action')
        if action == 'suite_start':
            if suite_started or suite_ended:
                errors.append('Repeated/out-of-order suite_start')
            info = event.get('run_info')
            if not isinstance(info, dict) or not {'os', 'debug'} <= set(info):
                errors.append('Platform/build run_info required')
                info = {} if not isinstance(info, dict) else info
            if info.get('browser_build_id') != binding['build_id'] or info.get('revision') != binding['harness_revision']:
                errors.append('Suite run_info differs from pinned application/harness')
            if binding['source_stamp'] is not None and binding['source_stamp'] != binding['build_revision']:
                errors.append('Application SourceStamp differs from completed-build binding')
            if info.get('browser_changeset') is not None and info['browser_changeset'] != binding['build_revision']:
                errors.append('Browser changeset differs from completed-build binding')
            advertised = event.get('tests', {})
            if not isinstance(advertised, dict) or any(not isinstance(v, list) for v in advertised.values()):
                errors.append('Invalid suite test roster')
            elif Counter(test for group in advertised.values() for test in group) != Counter(expected.keys()):
                errors.append('Suite roster differs from selected pages')
            suite_started = True
        elif action == 'suite_end':
            if not suite_started or suite_ended or opened or ended != set(expected):
                errors.append('Invalid suite_end')
            suite_ended = True
        elif action in ('test_start', 'test_status', 'test_end'):
            test = event.get('test')
            if not suite_started or suite_ended or test not in expected:
                errors.append('Unexpected test or event outside suite: ' + str(test))
            if action == 'test_start':
                if test in opened or test in ended:
                    errors.append('Repeated test_start: ' + str(test))
                opened.add(test)
            elif action == 'test_status':
                if test not in opened:
                    errors.append('Subtest outside active page: ' + str(test))
                key = (test, event.get('subtest'))
                counts[key] += 1
                rows.append({k: event.get(k) for k in ('test', 'subtest', 'status', 'expected', 'message')})
                if event.get('status') not in ('PASS', 'FAIL'):
                    errors.append('Incomplete subtest: ' + str(key))
                if event.get('status') == 'FAIL' and any(token in (event.get('message') or '') for token in
                        ('Unhandled rejection', 'TypeError:', 'ReferenceError:', 'SyntaxError:', 'RangeError:',
                         'Loading occurrence-', 'Frame load timed out', 'revert-rule support is required')):
                    errors.append('Fixture setup/runtime exception instead of assertion observation')
            else:
                if test not in opened or event.get('status') != policy['test_end_statuses'].get(test):
                    errors.append('Invalid test_end: ' + str(test))
                opened.discard(test)
                ended.add(test)
        elif action == 'crash' or (action == 'log' and event.get('level', '').upper() in ('ERROR', 'CRITICAL')):
            errors.append('Harness error/crash')
        elif action in ('suite_abort', 'test_abort'):
            errors.append('Harness abort: ' + action)
        elif action == 'process_exit' and event.get('exitcode', event.get('returncode')) != 0:
            errors.append('Nonzero or missing process exit code')
        elif action == 'assertion_count':
            values = [event.get(k) for k in ('count', 'min_expected', 'max_expected')]
            if not all(type(v) is int for v in values) or not 0 <= values[1] <= values[0] <= values[2]:
                errors.append('Assertion count outside valid expected range')
        if action in ('log', 'process_output') and any(token in
                (event.get('message') or '') + (event.get('data') or '') for token in
                ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT')):
            errors.append('Infrastructure fault in process/log output')
    wanted = Counter((test, name) for test, names in expected.items() for name in names)
    if counts != wanted:
        errors.append('Missing, duplicate or unexpected callback names')
    if not suite_started or not suite_ended or opened or ended != set(expected):
        errors.append('Incomplete suite lifecycle')
    if parsed['missing'] or parsed['errors'] or code not in (0, 1):
        errors.append('Missing/malformed raw stream or abnormal process exit')
    historical = {(row['test'], row['subtest']): row for row in policy['rows'] if row['action'] == 'test_status'}
    deviations = []
    for row in rows:
        old = historical.get((row['test'], row['subtest']))
        if old is None or row['status'] != old['status'] or (old['status'] == 'FAIL' and row['message'] != old['message']):
            deviations.append(row)
    statuses_match = all((row['test'], row['subtest']) in historical and
                         row['status'] == historical[(row['test'], row['subtest'])]['status'] for row in rows)
    if not errors and code != (0 if statuses_match else 1):
        errors.append('Process exit inconsistent with explicit metadata expectations')
    signatures = [{'kind': event['action'], 'test': event['test'], 'subtest': event.get('subtest'),
                   'status': event.get('status'), 'expected': event.get('expected', event.get('status')),
                   'expected_field_present': 'expected' in event,
                   'known_intermittent': event.get('known_intermittent', []),
                   'intermittent_field_present': 'known_intermittent' in event,
                   'message': event.get('message'), 'message_field_present': 'message' in event}
                  for event in events if event.get('action') in ('test_status', 'test_end')]
    signatures.sort(key=lambda row: (row['test'], row['kind'], row['subtest'] or ''))
    return {'complete_observation': not errors, 'supplemental_audit_passed': not errors,
            'all_pass': not errors and all(row['status'] == 'PASS' for row in rows),
            'controls_unchanged': not errors and not deviations, 'deviations': deviations,
            'run_info_binding': binding, 'errors': errors, 'signatures': signatures,
            'diagnostic_events': [event for event in events if event.get('action') in
                                  ('suite_start', 'suite_abort', 'test_abort', 'process_exit', 'assertion_count')],
            'counts': dict(Counter(row['status'] for row in rows)), 'rows': rows}


def run(root, output, pins, cancelled):
    assert __debug__, 'Run without Python optimization'
    assert not _owned and not cancelled()
    assert pins.get('execution_enabled') is True
    assert not os.environ.get('CSS_OCCURRENCE_TRACE'), 'Diagnostic tracing must be off'
    root, output = Path(root).resolve(), Path(output).absolute()
    assert output.parent.resolve().is_relative_to(root / 'artifacts')
    assert not output.exists() and not output.is_symlink()
    assert pins['source_role'] in ('baseline', 'candidate')
    for revision in ('build_revision', 'harness_revision'):
        assert len(pins[revision]) == 40 and all(c in '0123456789abcdef' for c in pins[revision])
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'MOZ_PROFILE'))
    for name in pins['files']:
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
    assert not Path(pins['binary']).is_absolute() and '..' not in Path(pins['binary']).parts
    binary = root / pins['binary']
    application = binary.parent.parent / 'Resources/application.ini'
    required = {str(p.relative_to(root)) for p in (binary, binary.parent / 'XUL', application)}
    roles = json.loads((ADAPTER / 'SOURCE-ROLES.json').read_bytes())
    required.update(roles)
    assert required <= set(pins['files'])
    for name, row in roles.items():
        key = 'base_sha256' if pins['source_role'] == 'baseline' else 'candidate_sha256'
        assert pins['files'][name] == row[key], (name, pins['source_role'])
    helpers = load_helpers(root)
    settings = json.loads((HERE / 'SETTINGS.json').read_bytes())
    expected = json.loads((HERE / 'EXPECTED.json').read_bytes())
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    assert expected == settings['expected_subtests']
    assert sum(map(len, expected.values())) == policy['callback_count']
    assert len(expected) == policy['page_count']
    assert policy['lane'] in ('primary', 'controls')
    assert len(policy['expected_failures']) == (2 if policy['lane'] == 'controls' else 0)
    application_config = configparser.ConfigParser(interpolation=None)
    application_config.read(application)
    binding = {'build_id': application_config['App']['BuildID'], 'harness_revision': pins['harness_revision'],
               'source_stamp': application_config.get('App', 'SourceStamp', fallback=None),
               'build_revision': pins['build_revision']}
    assert binding['build_id']
    assert binding['source_stamp'] is None or binding['source_stamp'] == binding['build_revision']
    package = json.loads((HERE / 'FILES.json').read_bytes())
    fresh = {name: sha(root / name) for name in ('mozconfig', 'objdir-full.noindex/mozinfo.json', settings['wpt_config'])}
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
               MOZCONFIG=str(root / 'mozconfig'), MOZ_OBJDIR=str(root / 'objdir-full.noindex'),
               MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')

    def git(*args):
        return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=root, env=env)

    def snapshot():
        assert sha(HERE / 'FILES.json') == FIXTURE_SEAL
        assert all(sha(ADAPTER / name) == digest for name, digest in json.loads((ADAPTER / 'FILES.json').read_bytes()).items()), 'Adapter changed'
        assert all(sha(HERE / name) == digest for name, digest in package.items()), 'Package changed'
        assert all(sha(root / name) == digest for name, digest in fresh.items()), 'Harness config changed'
        for row in json.loads((HERE / 'HELPERS.json').read_bytes()).values():
            assert sha(root / row['path']) == row['sha256'], 'Helper changed'
        observed = {name: sha(root / name) for name in pins['files']}
        assert observed == pins['files'], 'Source/application inputs changed'
        head = git('rev-parse', 'HEAD').decode().strip()
        assert head == pins['harness_revision']
        return {'head': head, 'files': observed,
                'index_entries': hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest(),
                'index_flags': hashlib.sha256(git('ls-files', '-v', '-z')).hexdigest()}

    initial = snapshot()
    output.mkdir()
    save(output / 'PINS.json', pins)
    save(output / 'PRE.json', initial)
    save(output / 'HARNESS-INPUTS.json', fresh)
    save(output / 'EXPECTED.json', expected)
    save(output / 'POLICY.json', policy)
    save(output / 'RUN-INFO-BINDING.json', binding)
    (output / 'application.ini').write_bytes(application.read_bytes())
    config, capture = helpers['wpt'].prepare_inputs(root, output, settings, pins['source_role'])
    assert capture is None
    temporary = Path(tempfile.mkdtemp(prefix='css-rollback-c-', dir='/private/tmp'))
    identity = (temporary.stat().st_dev, temporary.stat().st_ino)
    command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1',
               '--no-manifest-update', '--no-manifest-download', '--no-install-fonts', '--no-enable-webtransport-h3',
               '--binary=' + str(binary), '--config=' + str(config),
               '--run-info=' + str(root / 'objdir-full.noindex'), '--prefs-root=' + str(root / 'testing/profiles'),
               '--log-raw=' + str(output / 'raw.jsonl')]
    command.extend('--setpref=' + name + '=' + json.dumps(value) for name, value in settings['prefs'].items())
    command.extend('--include=' + test for test in expected)
    process, code, error, cleanup = None, None, None, None
    timed_out = False
    try:
        if cancelled():
            raise InterruptedError('Cancelled before launch')
        assert snapshot() == initial
        save(output / 'COMMAND.json', {'command': command, 'timeout_seconds': settings['timeout_seconds'],
                                      'temporary_root': str(temporary), 'temporary_identity': identity})
        phase_env = dict(env, TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
                         MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
        with (output / 'wpt.log').open('x') as stream:
            process = subprocess.Popen(command, cwd=root, env=phase_env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            _owned[process.pid] = process
            save(output / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid})
            deadline = time.monotonic() + settings['timeout_seconds']
            while process.poll() is None:
                if cancelled():
                    raise InterruptedError('Cancelled')
                if time.monotonic() >= deadline:
                    timed_out = True
                    raise TimeoutError('External deadline')
                time.sleep(0.2)
            code = process.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = helpers['control'].terminate(process)
            assert cleanup['owned_group_absent']
            if process is not None:
                _owned.pop(process.pid)
            assert not temporary.is_symlink() and (temporary.stat().st_dev, temporary.stat().st_ino) == identity
            shutil.rmtree(temporary)
            cleanup['temporary_root_removed'] = True
        except BaseException as exc:
            cleanup = {'owned_group_absent': not _owned, 'error': repr(exc), 'temporary_root_removed': False}
            error = error or repr(exc)
        save(output / 'CLEANUP.json', cleanup)
    if process is not None and code is None:
        code = process.returncode
    try:
        after = snapshot()
        save(output / 'POST.json', after)
        staged = json.loads((output / 'STAGED-RESOURCES.json').read_bytes())
        preserved = after == initial and all(sha(output / name) == digest for name, digest in staged.items())
    except BaseException as exc:
        preserved = False
        save(output / 'POST-ERROR.json', {'error': repr(exc)})
    events, parsed = helpers['wpt'].read_events(output / 'raw.jsonl')
    assessment = assess(events, parsed, code, expected, policy, binding)
    save(output / 'RAW-PARSE.json', parsed)
    save(output / 'ASSESSMENT.json', assessment)
    safe = bool(preserved and cleanup.get('owned_group_absent') and cleanup.get('temporary_root_removed'))
    complete = safe and error is None and not cancelled() and assessment['complete_observation']
    result = {'lane': policy['lane'], 'source_role': pins['source_role'], 'exit': code, 'execution_error': error,
              'external_timeout': timed_out, 'cancelled': cancelled(), 'preserved': preserved,
              'safe_to_continue': safe and not cancelled(), 'complete_observation': complete,
              'supplemental_audit_passed': complete and assessment['supplemental_audit_passed'],
              'controls_unchanged': complete and assessment['controls_unchanged'],
              'all_pass': complete and assessment['all_pass'], 'counts': assessment['counts'],
              'native_fix_acceptance': False}
    save(output / 'RESULT.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('Supply --execute explicitly after reviewing fresh build/source pins')
    pins = json.loads(args.pins.read_bytes())
    pins['execution_enabled'] = True
    cancellation = {'requested': False}
    def cancel(signum, frame):
        cancellation['requested'] = True
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, cancel)
    result = run(HERE.parents[1], args.output, pins, lambda: cancellation['requested'])
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['complete_observation'] else 2)
