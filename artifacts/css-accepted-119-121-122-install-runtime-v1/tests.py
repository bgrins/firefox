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
    complete = complete and lifecycle(events, c) and exit_matches_results(code, rows + ends)
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


def lifecycle(events, c):
    active, started, ended = None, False, False
    seen = set()
    expected = set(c['expected_subtests']) | set(c['reftests'])
    for e in events:
        action = e.get('action')
        if action == 'suite_start':
            if started or ended: return False
            started = True
        elif action == 'test_start':
            name = e.get('test')
            if not started or ended or active is not None or name not in expected or name in seen: return False
            active = name
            seen.add(name)
        elif action in ('test_status', 'test_end'):
            if not started or ended or active is None or e.get('test') != active: return False
            if action == 'test_end': active = None
        elif action == 'suite_end':
            if not started or ended or active is not None or seen != expected: return False
            ended = True
    return started and ended and active is None and seen == expected
