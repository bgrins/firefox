import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, ('duplicate JSON key', key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs)


def parse(path, exit_code):
    inventory = strict_json((HERE / 'COMPOSED-ASSERTIONS.json').read_text())
    plan = strict_json((HERE / 'RUN-PLAN.json').read_text())
    expected = {}
    order = []
    for task in inventory['tasks']:
        for assertion in task['assertions']:
            name = assertion['name']
            assert name not in expected
            expected[name] = {'task': task['name'], 'classification': assertion['classification']}
            order.append(name)
    assert len(order) == inventory['assertion_count'] == plan['composed_expected_assertions']
    assert type(exit_code) is int
    task_names = [task["name"] for task in inventory["tasks"]]
    task_active = None
    entered, left = [], []
    harness = None
    starts = ends = suites = suite_ends = 0
    suite_active = test_active = False
    records, sequence, unexpected, errors = {}, [], [], []
    normalize = lambda name: name.removeprefix('/tests/').removeprefix('/')
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        action = row.get('action')
        if action == 'crash' or action == 'log' and row.get('level') in ['ERROR', 'CRITICAL']:
            errors.append({'reason': 'crash or harness error', 'row': row})
        if action == 'process_exit' and (type(row.get('exitcode')) is not int or row['exitcode'] != 0):
            errors.append({'reason': 'browser process exit', 'row': row})
        if action in ['valgrind_error', 'lsan_leak'] or action == 'mozleak_total' and row.get('bytes', 0) > row.get('threshold', 0):
            errors.append({'reason': 'memory diagnostic', 'row': row})
        if action == 'log' and row.get('message', '').startswith('add_task | '):
            assert suite_active and test_active and not ends
            assert normalize(row['test']) == plan['composed_test'] and row['level'] == 'INFO'
            message = row['message']
            if message.startswith('add_task | Entering '):
                name = message.removeprefix('add_task | Entering ')
                assert task_active is None and len(entered) < len(task_names)
                assert name == task_names[len(entered)]
                task_active = name
                entered.append(name)
            else:
                assert message.startswith('add_task | Leaving ')
                name = message.removeprefix('add_task | Leaving ')
                assert task_active == name
                assert all(a['name'] in records for task in inventory['tasks'] if task['name'] == name for a in task['assertions'])
                task_active = None
                left.append(name)
        if action == 'suite_start':
            assert not suite_active and suites == 0
            suite_active = True
            suites += 1
        elif action == 'test_start':
            assert suite_active and starts == 0 and not test_active
            assert normalize(row['test']) == plan['composed_test']
            starts += 1
            test_active = True
        elif action == 'test_status':
            assert suite_active and test_active and not ends
            assert normalize(row['test']) == plan['composed_test']
            assert row.get('subtest') is None, ('unexpected named Mochitest subtest', row)
            assert row['status'] in ['PASS', 'FAIL']
            message = row.get('message')
            assert isinstance(message, str)
            names = [name for name in expected if message == name or row['status'] == 'FAIL' and message.startswith(name + ' - ')]
            if len(names) != 1:
                unexpected.append(row)
                continue
            name = names[0]
            assert name not in records, ('duplicate assertion', name)
            assert task_active == expected[name]['task'], ('assertion outside its task', name)
            record = dict(expected[name], name=name, status=row['status'], message=message,
                          expected=row.get('expected', 'PASS'), known_intermittent=row.get('known_intermittent'))
            record['passed'] = row['status'] == 'PASS' and row.get('expected', 'PASS') == 'PASS' and not row.get('known_intermittent')
            records[name] = record
            sequence.append(name)
        elif action == 'test_end':
            assert suite_active and test_active and ends == 0
            assert normalize(row['test']) == plan['composed_test']
            test_active = False
            ends += 1
            assert task_active is None
            harness = row
            if row.get('expected', 'PASS') != 'PASS' or row.get('known_intermittent'):
                errors.append({'reason': 'harness expected/intermittent override', 'row': row})
        elif action == 'suite_end':
            assert suite_active and not test_active and ends == 1
            suite_active = False
            suite_ends += 1
        elif action == 'assertion_count':
            if not row['min_expected'] <= row['count'] <= row['max_expected']:
                errors.append({'reason': 'native assertion count', 'row': row})
    assert suites == suite_ends == starts == ends == 1 and not suite_active and not test_active
    missing = [name for name in order if name not in records]
    failures = [record for record in records.values() if not record['passed']]
    tasks = []
    for task in inventory['tasks']:
        names = [a['name'] for a in task['assertions']]
        setup = [a['name'] for a in task['assertions'] if a['classification'] == 'setup']
        invalid = [name for name in setup if name not in records or not records[name]['passed']]
        tasks.append({'task': task['name'], 'setup_gates_passed': not invalid,
                      'failed_or_missing_setup': invalid,
                      'all_assertions_passed': all(name in records and records[name]['passed'] for name in names),
                      'semantic_interpretation': 'invalid setup' if invalid else 'requires all non-probe assertions; interpretation probes remain separately reported'})
    probes = [r for r in records.values() if r['classification'] == 'probe']
    failed_probes = [r for r in probes if r['status'] == 'FAIL' and r['expected'] == 'PASS' and not r['known_intermittent']]
    invalid_nonprobes = [r for r in failures if r['classification'] != 'probe']
    invalid_probe_metadata = [r for r in probes if r['expected'] != 'PASS' or r['known_intermittent']]
    all_passed = not failures
    aggregate_status = 'FAIL' if failed_probes else 'PASS'
    normal_aggregate_end = harness['status'] == aggregate_status and bool(re.fullmatch(r'Finished in [0-9]+ms', harness.get('message', '')))
    if not normal_aggregate_end:
        errors.append({'reason': 'not the normal assertion-correlated aggregate ending', 'row': harness})
    expected_exit = 1 if failed_probes else 0
    if exit_code != expected_exit:
        errors.append({'reason': 'command exit does not match complete assertion result', 'actual': exit_code, 'expected': expected_exit})
    exact_tasks = entered == left == task_names and task_active is None
    assert len(order) == 122 and sum(r['classification'] == 'probe' for r in expected.values()) == 3
    valid = not errors and not unexpected and not missing and not invalid_nonprobes and not invalid_probe_metadata and sequence == order and exact_tasks and len(probes) == 3
    return {'investigation_valid': valid, 'all_assertions_passed': valid and all_passed,
            'native_fix_acceptance': False,
            'expected_assertions': len(order), 'observed_known_assertions': len(records),
            'expected_nonprobe_assertions': 119, 'nonprobe_assertions_passed': sum(r['classification'] != 'probe' and r['passed'] for r in records.values()),
            'expected_probe_assertions': 3, 'probe_failures': failed_probes,
            'probe_results': probes, 'exact_assertion_order': sequence == order,
            'expected_tasks': len(tasks), 'entered_tasks': entered, 'completed_tasks': left,
            'exact_task_lifecycle': exact_tasks, 'harness_end': harness,
            'command_exit': exit_code, 'required_command_exit': expected_exit,
            'missing_assertions': missing, 'failed_assertions': failures,
            'unexpected_callbacks': unexpected, 'integrity_errors': errors,
            'tasks': tasks, 'assertions': [records[name] for name in order if name in records],
            'classification_policy': 'Only the three named interpretation probes may fail in a valid investigation. All 119 non-probe checks, five task scopes and complete lifecycle are required. Normal aggregate FAIL and command exit1 are accepted only when explained by those probe rows; they never imply native fix acceptance.'}
