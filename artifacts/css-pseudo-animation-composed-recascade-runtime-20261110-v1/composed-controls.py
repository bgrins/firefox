import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('composed_analyze', HERE / 'composed-analyze.py')
analyze = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze)
plan = json.loads((HERE / 'RUN-PLAN.json').read_text())
inventory = json.loads((HERE / 'COMPOSED-ASSERTIONS.json').read_text())
test = plan['composed_test']
base = [{'action': 'suite_start'}, {'action': 'test_start', 'test': test}]
for task in inventory['tasks']:
    base.append({'action': 'log', 'level': 'INFO', 'test': test, 'message': 'add_task | Entering ' + task['name']})
    base.extend({'action': 'test_status', 'test': test, 'subtest': None, 'status': 'PASS', 'message': a['name']} for a in task['assertions'])
    base.append({'action': 'log', 'level': 'INFO', 'test': test, 'message': 'add_task | Leaving ' + task['name']})
base += [{'action': 'test_end', 'test': test, 'status': 'PASS', 'message': 'Finished in 123ms'}, {'action': 'suite_end'}]
indices = [i for i, row in enumerate(base) if row['action'] == 'test_status']
probes = [i for i in indices if base[i]['message'].startswith('Probe: ')]
setup = next(i for i in indices if 'setup' in base[i]['message'])
result_index = next(i for i in indices if i != setup and not base[i]['message'].startswith('Probe: '))


def with_probes(count):
    rows = copy.deepcopy(base)
    for i in probes[:count]:
        rows[i].update(status='FAIL', expected='PASS', message=rows[i]['message'] + ' - got wrong, expected right')
    if count:
        rows[-2].update(status='FAIL', expected='PASS')
    return rows


controls = []
def control(name, change, start=None, exit_code=1):
    rows = copy.deepcopy(with_probes(3) if start is None else start)
    change(rows)
    controls.append((name, rows, exit_code))


control('setup-failure', lambda r: r[setup].update(status='FAIL'))
control('nonprobe-failure', lambda r: r[result_index].update(status='FAIL'))
control('missing-setup', lambda r: r.pop(setup))
control('missing-probe', lambda r: r.pop(probes[0]))
control('unknown-callback', lambda r: r[probes[0]].update(message='unknown failure'))
control('duplicate-callback', lambda r: r.insert(probes[0], copy.deepcopy(r[probes[0]])))
control('wrong-test', lambda r: r[probes[0]].update(test='wrong.html'))
control('named-subtest', lambda r: r[probes[0]].update(subtest='named'))
control('expected-todo', lambda r: r[probes[0]].update(expected='FAIL'))
control('explicit-null-expected', lambda r: r[probes[0]].update(expected=None))
control('intermittent-probe', lambda r: r[probes[0]].update(known_intermittent=['FAIL']))
control('unknown-status', lambda r: r[probes[0]].update(status='ERROR'))
control('harness-timeout', lambda r: r[-2].update(status='TIMEOUT', message='Test timed out'))
control('unexplained-harness-fail', lambda r: r[-2].update(status='FAIL'), start=base)
control('probe-fail-but-harness-pass', lambda r: r[-2].update(status='PASS'))
control('probe-fail-but-exit-zero', lambda r: None, exit_code=0)
control('exit-two', lambda r: None, exit_code=2)
control('exit-bool', lambda r: None, exit_code=True)
control('all-pass-but-exit-one', lambda r: None, start=base)
control('harness-failure-message', lambda r: r[-2].update(message='Harness cleanup failed'))
control('harness-expected-fail', lambda r: r[-2].update(expected='FAIL'))
control('harness-intermittent', lambda r: r[-2].update(known_intermittent=['FAIL']))
control('suite-missing', lambda r: r.pop())
control('end-missing', lambda r: r.pop(-2))
control('start-missing', lambda r: r.pop(1))
control('duplicate-suite', lambda r: r.insert(1, {'action': 'suite_start'}))
control('missing-task-entry', lambda r: r.pop(2))
control('wrong-task-name', lambda r: r[2].update(message='add_task | Entering other'))
control('missing-last-task-exit', lambda r: r.pop(-3))
control('duplicate-task-exit', lambda r: r.insert(-3, copy.deepcopy(r[-3])))
control('wrong-task-test', lambda r: r[2].update(test='wrong.html'))
control('assertion-order', lambda r: r.__setitem__(slice(indices[0], indices[0] + 2), list(reversed(r[indices[0]:indices[0] + 2]))))
control('after-end', lambda r: r.insert(-1, copy.deepcopy(r[indices[0]])))
control('crash', lambda r: r.insert(-2, {'action': 'crash'}))
control('ERROR', lambda r: r.insert(-2, {'action': 'log', 'level': 'ERROR', 'message': 'bad'}))
control('CRITICAL', lambda r: r.insert(-2, {'action': 'log', 'level': 'CRITICAL', 'message': 'bad'}))
control('browser-exit', lambda r: r.insert(-2, {'action': 'process_exit', 'exitcode': 1}))
control('browser-signal', lambda r: r.insert(-2, {'action': 'process_exit', 'exitcode': -9}))
control('leak', lambda r: r.insert(-2, {'action': 'mozleak_total', 'bytes': 32, 'threshold': 0}))
control('native-assertion', lambda r: r.insert(-2, {'action': 'assertion_count', 'min_expected': 0, 'max_expected': 0, 'count': 1}))

with tempfile.TemporaryDirectory(prefix='composed-parser-control-') as directory:
    path = Path(directory) / 'raw.jsonl'
    def parse(rows, code):
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        return analyze.parse(path, code)
    accepted = []
    for count in range(4):
        row = parse(with_probes(count), int(count > 0))
        assert row['investigation_valid'] and row['nonprobe_assertions_passed'] == 119
        assert row['all_assertions_passed'] == (count == 0)
        assert row['native_fix_acceptance'] is False and len(row['probe_failures']) == count
        accepted.append(count)
    rejected = []
    for name, rows, code in controls:
        try:
            result = parse(rows, code)
        except (AssertionError, KeyError, ValueError, TypeError):
            rejected.append(name)
            continue
        assert not result['investigation_valid'], name
        rejected.append(name)
    path.write_text('{"action":"suite_start","action":"suite_end"}\n')
    try:
        analyze.parse(path, 0)
    except AssertionError:
        rejected.append('duplicate-json-key')
    else:
        raise AssertionError('duplicate key accepted')
print(json.dumps({'status': 'PASS', 'accepted_probe_failure_counts': accepted,
                  'rejected_controls': rejected, 'assertions': 122, 'tasks': 5,
                  'native_execution': False}, indent=2))
