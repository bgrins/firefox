import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('driver_analyze', HERE / 'recascade-analyze.py')
analyze = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze)
plan = json.loads((HERE / 'RUN-PLAN.json').read_text())
inventory = json.loads((HERE / 'RECASCADE-ASSERTIONS.json').read_text())
test = plan['recascade_test']
assertions = [a for task in inventory['tasks'] for a in task['assertions']]
base = [{'action': 'suite_start'}, {'action': 'test_start', 'test': test}]
base += [{'action': 'test_status', 'test': test, 'subtest': None, 'status': 'PASS', 'message': a['name']} for a in assertions]
base += [{'action': 'test_end', 'test': test, 'status': 'PASS'}, {'action': 'suite_end'}]
controls = []


def control(name, change):
    rows = copy.deepcopy(base)
    change(rows)
    controls.append((name, rows))


control('first-status', lambda r: r[2].update(status='FAIL'))
control('first-label', lambda r: r[2].update(message='wrong first callback'))
control('first-deletion', lambda r: r.pop(2))
control('first-duplicate', lambda r: r.insert(2, copy.deepcopy(r[2])))
control('wrong-test', lambda r: r[2].update(test='wrong.html'))
control('named-subtest', lambda r: r[2].update(subtest='named'))
control('expected-todo', lambda r: r[2].update(expected='FAIL'))
control('known-intermittent', lambda r: r[2].update(known_intermittent=['FAIL']))
control('harness-OK', lambda r: r[-2].update(status='OK'))
control('harness-FAIL', lambda r: r[-2].update(status='FAIL'))
control('suite-missing', lambda r: r.pop())
control('suite-duplicate', lambda r: r.insert(1, {'action': 'suite_start'}))
control('start-missing', lambda r: r.pop(1))
control('end-missing', lambda r: r.pop(-2))
control('after-end', lambda r: r.insert(-1, copy.deepcopy(r[2])))
control('order-swap', lambda r: r.__setitem__(slice(2, 4), list(reversed(r[2:4]))))
control('crash', lambda r: r.insert(-2, {'action': 'crash'}))
control('ERROR', lambda r: r.insert(-2, {'action': 'log', 'level': 'ERROR', 'message': 'bad'}))
control('native-assertions', lambda r: r.insert(-2, {'action': 'assertion_count', 'min_expected': 0, 'max_expected': 0, 'count': 1}))
control('uncaught-setup', lambda r: r[2].update(status='FAIL', message='add_task failed with an uncaught exception'))
setup_index = next(i + 2 for i, a in enumerate(assertions) if a['classification'] == 'setup')
control('setup-failure', lambda r: r[setup_index].update(status='FAIL', message=r[setup_index]['message'] + ' - got wrong, expected correct'))
control('setup-deletion', lambda r: r.pop(setup_index))
with tempfile.TemporaryDirectory(prefix='pseudo-query-driver-parser-') as directory:
    path = Path(directory) / 'raw.jsonl'
    def parse(rows):
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        return analyze.parse(path)
    assert parse(base)['gate_passed']
    rejected = []
    for name, rows in controls:
        try:
            result = parse(rows)
        except (AssertionError, KeyError, ValueError, TypeError):
            rejected.append(name)
            continue
        assert not result['gate_passed'], name
        if name in ['setup-failure', 'setup-deletion']:
            assert any(not task['setup_gates_passed'] for task in result['tasks'])
        rejected.append(name)
    path.write_text('{"action":"suite_start","action":"suite_end"}\n')
    try:
        analyze.parse(path)
    except AssertionError:
        rejected.append('duplicate-json-key')
    else:
        raise AssertionError('duplicate JSON accepted')
print(json.dumps({'status': 'PASS', 'positive_assertions': 100, 'rejected_controls': rejected,
                  'setup_failures_classified': True, 'native_execution': False}, indent=2))
