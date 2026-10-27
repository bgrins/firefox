import json
import os
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
    expected = set(c['expected_subtests'])
    complete = (len(starts) == len(ends) == len(expected) and {e['test'] for e in starts} == expected
                and {e['test'] for e in ends} == expected and len({(r['test'], r['subtest']) for r in rows}) == len(rows)
                and all(r['test'] in c['expected_subtests'] and r['status'] in ('PASS', 'FAIL') for r in rows)
                and all(e['status'] == 'OK' for e in ends)
                and sum(e.get('action') == 'suite_start' for e in events) == 1
                and sum(e.get('action') == 'suite_end' for e in events) == 1 and not faults)
    for test, names in c['expected_subtests'].items():
        actual = [r['subtest'] for r in rows if r['test'] == test]
        complete = complete and len(actual) == len(names) == len(set(names)) and set(actual) == set(names)
    complete = complete and (code == 0 or (code == 1 and any(r['status'] == 'FAIL' for r in rows + ends)))
    result = {'command': command, 'exit': code, 'before': before, 'after': wpt.pins(paths),
              'rows': rows, 'starts': starts, 'ends': ends, 'infrastructure_faults': faults, 'complete': complete}
    (directory / 'RUN.json').write_text(json.dumps(result, indent=2) + '\n')
    wpt.need(complete and result['before'] == result['after'], 'complete exact phase roster and stable source/binary/resources')
    return result


def compare(wpt, baseline, candidate):
    def values(result):
        selected = result['rows']
        return {(e['test'], e.get('subtest')): {k: e.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')} for e in selected}
    old, new = values(baseline), values(candidate)
    wpt.need(old.keys() == new.keys(), 'paired roster')
    regressions = [key for key in old if old[key]['status'] == 'PASS' and new[key]['status'] != 'PASS']
    changed = [key for key in old if old[key]['status'] == new[key]['status'] == 'FAIL' and old[key] != new[key]]
    repaired = [key for key in old if old[key]['status'] == 'FAIL' and new[key]['status'] == 'PASS']
    wpt.save('COMPARISON.json', {'regressions': regressions, 'changed_failures': changed, 'repaired': repaired, 'native_acceptance': False})
    wpt.need(not regressions and not changed, 'paired preservation failed')
    main = set(wpt.CONFIG['main_tests'])
    selected = [r for r in candidate['rows'] if r['test'] in main]
    wpt.need(len(selected) == 8 and all(r['status'] == 'PASS' for r in selected), 'candidate8 matrix oracle failed')


def require_phase(wpt, phase, result):
    main = set(wpt.CONFIG['main_tests'])
    selected = [r for r in result['rows'] if r['test'] in main]
    wpt.need(len(selected) == 8, 'eight main identities')
    for row in selected:
        allowed_hidden = row['subtest'] in (
            'getCTM: viewBox, hidden viewport resize',
            'getScreenCTM: viewBox, hidden viewport resize')
        if phase == 'baseline' and allowed_hidden and row['status'] == 'FAIL':
            wpt.need('first matrix after viewport resize' in (row.get('message') or ''), 'unexpected baseline first failure')
        else:
            wpt.need(row['status'] == 'PASS', 'matrix calibration/control/candidate failure: ' + row['subtest'])
    controls = [r for r in result['rows'] + result['ends'] if r['test'] not in main]
    unexpected = [r for r in controls if r['status'] != r.get('expected', r['status'])
                  and r['status'] not in r.get('known_intermittent', [])]
    wpt.need(not unexpected, 'unexpected existing control results')
