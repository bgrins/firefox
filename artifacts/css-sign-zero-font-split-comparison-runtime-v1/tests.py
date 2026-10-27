import json
import os
import re
import signal
import subprocess
import time


def infrastructure_faults(events):
    faults = []
    for e in events:
        a = e.get('action')
        if a in ('crash', 'suite_abort', 'test_abort'):
            faults.append(e)
        elif a == 'log' and e.get('level', '').upper() in ('ERROR', 'CRITICAL'):
            faults.append(e)
        elif a == 'process_exit' and e.get('exitcode', e.get('returncode', 0)) != 0:
            faults.append(e)
        elif a == 'assertion_count' and not e.get('min_expected', 0) <= e['count'] <= e.get('max_expected', 0):
            faults.append(e)
        elif a in ('log', 'process_output') and any(t in e.get('message', '') + e.get('data', '')
                for t in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT')):
            faults.append(e)
    return faults


def run(wpt, phase, resources):
    c = dict(wpt.CONFIG)
    if phase == 'baseline':
        c['tests'] = c['baseline_tests']
        c['expected_subtests'] = c['baseline_expected_subtests']
    directory = wpt.HERE / ('wpt-' + phase)
    directory.mkdir()
    paths = sorted(set(resources) | set(c['guard_sources']) | set(wpt.BINARIES))
    before = wpt.pins(paths)
    wpt.need(all(before[n] == h for n, h in resources.items()), 'phase resources')
    command = ['./mach', 'wpt', '--headless', '--processes=1', '--log-raw=' + str(directory / 'raw.json'), *c['tests']]
    process = None
    cleanup = []
    try:
        with (directory / 'wpt.log').open('w') as log:
            process = subprocess.Popen(command, cwd=wpt.ROOT, env=wpt.ENV, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            code = process.wait(timeout=600)
    finally:
        if process is not None:
            try:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        break
                    time.sleep(0.2)
                process.wait(timeout=10)
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise RuntimeError('owned WPT process group remains')
            except BaseException as error:
                cleanup.append(repr(error))
        (directory / 'CLEANUP.json').write_text(json.dumps({'owned_group_absent': not cleanup, 'errors': cleanup}, indent=2) + '\n')
        wpt.need(not cleanup, 'WPT cleanup failed')
    raw = directory / 'raw.json'
    wpt.need(raw.is_file() and not raw.is_symlink() and raw.stat().st_size <= 128 * 1024 * 1024, 'invalid/oversized raw log')
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    faults = infrastructure_faults(events)
    expected = set(c['expected_subtests']) | set(c['reftests'])
    complete = (len(starts) == len(ends) == len(expected) and {e['test'] for e in starts} == expected
                and {e['test'] for e in ends} == expected and len({(r['test'], r['subtest']) for r in rows}) == len(rows)
                and all(r['test'] in c['expected_subtests'] and r['status'] in ('PASS', 'FAIL') for r in rows)
                and all(e['status'] in (('PASS', 'FAIL') if e['test'] in c['reftests'] else ('OK',)) for e in ends)
                and sum(e.get('action') == 'suite_start' for e in events) == 1
                and sum(e.get('action') == 'suite_end' for e in events) == 1 and not faults)
    for test, names in c['expected_subtests'].items():
        actual = [r['subtest'] for r in rows if r['test'] == test]
        complete = complete and len(actual) == len(names) == len(set(names)) and actual == names
    complete = complete and exit_matches_results(code, rows + ends)
    result = {'command': command, 'exit': code, 'before': before, 'after': wpt.pins(paths),
              'rows': rows, 'starts': starts, 'ends': ends, 'infrastructure_faults': faults, 'complete': complete}
    (directory / 'RUN.json').write_text(json.dumps(result, indent=2) + '\n')
    wpt.need(complete and result['before'] == result['after'], 'complete exact phase roster and stable source/binary/resources')
    return result


def exit_matches_results(code, events):
    unexpected = any(e['status'] != e.get('expected', e['status'])
                     and e['status'] not in e.get('known_intermittent', []) for e in events)
    return code == (1 if unexpected else 0)


def values(result):
    events = [(e['test'], e['subtest'], e) for e in result['rows']]
    events += [(e['test'], '<reftest>', e) for e in result['ends'] if e['status'] != 'OK']
    return {(test, name): {k: e.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')}
            for test, name, e in events}


def compare(wpt, baseline, candidate, phase, repair_basis):
    c = wpt.CONFIG
    old, new, basis = values(baseline), values(candidate), values(repair_basis)
    wpt.need(old.keys() == new.keys() == basis.keys(), 'paired exact roster')
    regressions = [key for key in old if old[key]['status'] == 'PASS' and new[key]['status'] != 'PASS']
    changed = [key for key in old if old[key]['status'] == new[key]['status'] == 'FAIL' and old[key] != new[key]]
    basis_regressions = [key for key in basis if basis[key]['status'] == 'PASS' and new[key]['status'] != 'PASS']
    basis_changed = [key for key in basis if basis[key]['status'] == new[key]['status'] == 'FAIL' and basis[key] != new[key]]
    repaired = [key for key in old if old[key]['status'] == 'FAIL' and new[key]['status'] == 'PASS']
    own_repaired = [key for key in basis if basis[key]['status'] == 'FAIL' and new[key]['status'] == 'PASS'
                    and key[0] in c['phase_repair_tests'][phase]]
    own_failures = [key for key in new if key[0] in c['phase_required_tests'][phase] and new[key]['status'] != 'PASS']
    result = {'status': 'PASSED' if not regressions and not changed and not basis_regressions and not basis_changed and not own_failures and own_repaired else 'REJECTED',
              'regressions': regressions, 'changed_failures': changed, 'repaired': repaired,
              'repair_basis_regressions': basis_regressions, 'repair_basis_changed_failures': basis_changed,
              'required_landing_failures': own_failures, 'own_repaired': own_repaired,
              'repair_basis': c['phase_repair_basis'][phase], 'native_acceptance': False}
    wpt.save(phase + '-COMPARISON.json', result)
    return result


def allowed_main_failure(name, message):
    import math
    from pathlib import Path
    policy = json.loads(Path(__file__).with_name('SEMANTIC-FAILURES.json').read_text())
    if name not in policy or not isinstance(message, str) or len(message.encode()) > 4096:
        return False
    number = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    match = re.fullmatch('assert_equals: (.+) expected (' + number + ') but got (' + number + ')', message)
    if not match:
        return False
    label, wanted, actual = match.groups()
    wanted, actual = float(wanted), float(actual)
    rule = policy[name]
    return (label in rule['assertions'] and math.isfinite(wanted) and math.isfinite(actual)
            and wanted == rule['assertions'][label] and actual != wanted
            and rule['actual_range'][0] <= actual <= rule['actual_range'][1])


def require_phase(wpt, phase, result):
    c = wpt.CONFIG
    expected = {(test, name) for test, names in c['expected_subtests'].items() for name in names}
    actual = [(r['test'], r['subtest']) for r in result['rows']]
    wpt.need(len(actual) == len(set(actual)) == len(expected) == c['expected_total']
             and set(actual) == expected, 'exact phase identities')
    ends = {e['test']: e for e in result['ends']}
    wpt.need(len(ends) == len(result['ends']) == c['files_expected_count']
             and set(ends) == set(c['expected_subtests']) and all(e['status'] == 'OK' for e in ends.values()),
             'exact complete harness identities')
    main = [r for r in result['rows'] if r['test'] in c['landing_tests']]
    wpt.need(len(main) == 19, 'exact19 landing cases')
    failures = [r for r in main if r['status'] == 'FAIL']
    wpt.save(phase + '-LANDING.json', {'counts': {s: sum(r['status'] == s for r in main) for s in ('PASS', 'FAIL')},
        'failures': failures, 'calibration_failure_rejected': any(not allowed_main_failure(r['subtest'], r.get('message')) for r in failures),
        'required_baseline_failure_count': None, 'later_semantic_assertions_after_failure': 'NOT_REACHED'})
    wpt.need(all(allowed_main_failure(r['subtest'], r.get('message')) for r in failures), 'landing calibration/control or malformed failure')
