from pathlib import Path
import argparse
import configparser
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'artifacts/css-rollback-local-wpt-v1'
RUNNER_SHA256 = '49d0c29953b6f4667788efbf502f9045c4bcc675aeffe7ac88b40f047f8ad550'
CHECKS = ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py'
CHECKS_SHA256 = '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path, expected):
    assert sha(path) == expected
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def supplemental(events, pins, application):
    errors = []
    checks = load('rollback_fault_checks', CHECKS, CHECKS_SHA256)
    faults = checks.infrastructure_faults(events)
    if faults:
        errors.append('Infrastructure faults in raw stream')
    starts = [event for event in events if event.get('action') == 'suite_start']
    run_info = starts[0].get('run_info') if len(starts) == 1 else None
    if not isinstance(run_info, dict) or not {'os', 'debug'} <= set(run_info):
        errors.append('Exactly one suite with platform/build run_info required')
        run_info = {}
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(application.decode())
    build_id = config.get('App', 'BuildID')
    source_stamp = config.get('App', 'SourceStamp', fallback=None)
    if not build_id or run_info.get('browser_build_id') != build_id:
        errors.append('Browser BuildID differs from pinned application metadata')
    if run_info.get('revision') != pins['harness_revision']:
        errors.append('Harness revision differs from supplied harness binding')
    if source_stamp is not None and source_stamp != pins['build_revision']:
        errors.append('Application SourceStamp differs from supplied build binding')
    changeset = run_info.get('browser_changeset')
    if changeset is not None and changeset != pins['build_revision']:
        errors.append('Browser changeset differs from supplied build binding')
    setup_failures = [event for event in events if event.get('action') == 'test_status'
                      and event.get('status') == 'FAIL'
                      and any(token in (event.get('message') or '') for token in
                              ('Unhandled rejection', 'TypeError:', 'ReferenceError:', 'SyntaxError:', 'RangeError:'))]
    if setup_failures:
        errors.append('Fixture setup/runtime exception instead of a supported assertion observation')
    return {'errors': errors, 'infrastructure_faults': faults, 'fixture_setup_failures': setup_failures,
            'run_info': run_info, 'application_build_id': build_id, 'application_source_stamp': source_stamp,
            'browser_changeset': changeset, 'harness_revision_bound': run_info.get('revision') == pins['harness_revision'],
            'browser_build_id_bound': run_info.get('browser_build_id') == build_id,
            'source_revision_discovered_from_metadata': source_stamp is not None or changeset is not None,
            'source_revision_provenance': 'Caller completed-build receipt remains required; supplied pins are not a source revision discovered from application metadata.'}


def audit(runtime, pins):
    runtime = Path(runtime).resolve()
    assert read(runtime / 'PINS.json') == pins
    assert pins['source_role'] in ('baseline', 'candidate')
    package_files = read(PACKAGE / 'FILES.json')
    assert all(sha(PACKAGE / name) == digest for name, digest in package_files.items())
    runner = load('rollback_callback_replay', PACKAGE / 'run.py', RUNNER_SHA256)
    expected = read(PACKAGE / 'EXPECTED.json')
    roles = read(PACKAGE / 'SOURCE-ROLES.json')
    role_key = 'base_sha256' if pins['source_role'] == 'baseline' else 'candidate_sha256'
    assert all(pins['files'][name] == role[role_key] for name, role in roles.items())
    application_path = str(Path(pins['binary']).parent.parent / 'Resources/application.ini')
    application = (runtime / 'application.ini').read_bytes()
    assert hashlib.sha256(application).hexdigest() == pins['files'][application_path]
    before, after = read(runtime / 'PRE.json'), read(runtime / 'POST.json')
    assert before == after and before['files'] == pins['files'] and before['head'] == pins['harness_revision']
    cleanup = read(runtime / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    result = read(runtime / 'RESULT.json')
    assert result['complete_observation'] and result['safe_to_continue'] and result['preserved']
    assert not result['cancelled'] and not result['external_timeout'] and result['execution_error'] is None
    raw = runtime / 'raw.jsonl'
    events = [json.loads(line) for line in raw.read_bytes().splitlines()]
    assert all(isinstance(event, dict) for event in events)
    parsed = {'missing': False, 'errors': [], 'sha256': sha(raw)}
    assert read(runtime / 'RAW-PARSE.json') == parsed
    assessment = runner.assess(events, parsed, result['exit'], expected)
    assert assessment == read(runtime / 'ASSESSMENT.json')
    assert assessment['complete_observation'] and assessment['counts'] == result['counts']
    extra = supplemental(events, pins, application)
    signatures = [{
        'kind': event['action'], 'test': event['test'], 'subtest': event.get('subtest'),
        'status': event['status'], 'expected': event.get('expected', event['status']),
        'expected_field_present': 'expected' in event,
        'known_intermittent': event.get('known_intermittent', []),
        'intermittent_field_present': 'known_intermittent' in event,
        'message': event.get('message'), 'message_field_present': 'message' in event,
    } for event in events if event.get('action') in ('test_status', 'test_end')]
    signatures.sort(key=lambda row: (row['test'], row['kind'], row['subtest'] or ''))
    references = {str(path.relative_to(ROOT)): sha(path) for path in [
        PACKAGE / 'FILES.json', PACKAGE / 'run.py', PACKAGE / 'EXPECTED.json', CHECKS,
        *[runtime / name for name in ['PINS.json', 'PRE.json', 'POST.json', 'CLEANUP.json',
                                     'RESULT.json', 'ASSESSMENT.json', 'RAW-PARSE.json', 'application.ini', 'raw.jsonl']]]}
    return {'supplemental_audit_passed': not extra['errors'], 'source_role': pins['source_role'],
            'complete_observation': assessment['complete_observation'] and not extra['errors'],
            'all_pass': assessment['all_pass'] and not extra['errors'], 'counts': assessment['counts'],
            'supplemental': extra, 'signatures': signatures, 'references': references,
            'scope': 'Replay of recorded inputs and raw events; no fresh live application or process-restoration assertion.',
            'native_fix_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.runtime, read(args.pins))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('supplemental_audit_passed', 'source_role', 'complete_observation', 'all_pass', 'counts')}))
    raise SystemExit(0 if result['supplemental_audit_passed'] else 1)
