import json
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


def parse(path):
    inventory = strict_json((HERE / 'DRIVER-ASSERTIONS.json').read_text())
    plan = strict_json((HERE / 'RUN-PLAN.json').read_text())
    expected = {}
    order = []
    for task in inventory['tasks']:
        for assertion in task['assertions']:
            name = assertion['name']
            assert name not in expected
            expected[name] = {'task': task['name'], 'classification': assertion['classification']}
            order.append(name)
    assert len(order) == inventory['assertion_count'] == plan['driver_expected_assertions']
    starts = ends = suites = suite_ends = 0
    suite_active = test_active = False
    records, sequence, unexpected, errors = {}, [], [], []
    normalize = lambda name: name.removeprefix('/tests/').removeprefix('/')
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        action = row.get('action')
        if action == 'crash' or action == 'log' and row.get('level') in ['ERROR', 'CRITICAL']:
            errors.append({'reason': 'crash or harness error', 'row': row})
        if action == 'suite_start':
            assert not suite_active and suites == 0
            suite_active = True
            suites += 1
        elif action == 'test_start':
            assert suite_active and starts == 0 and not test_active
            assert normalize(row['test']) == plan['driver_test']
            starts += 1
            test_active = True
        elif action == 'test_status':
            assert suite_active and test_active and not ends
            assert normalize(row['test']) == plan['driver_test']
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
            record = dict(expected[name], name=name, status=row['status'], message=message,
                          expected=row.get('expected'), known_intermittent=row.get('known_intermittent'))
            record['passed'] = row['status'] == 'PASS' and row.get('expected', 'PASS') == 'PASS' and not row.get('known_intermittent')
            records[name] = record
            sequence.append(name)
        elif action == 'test_end':
            assert suite_active and test_active and ends == 0
            assert normalize(row['test']) == plan['driver_test']
            test_active = False
            ends += 1
            if row['status'] != 'PASS' or row.get('expected', 'PASS') != 'PASS' or row.get('known_intermittent'):
                errors.append({'reason': 'harness end not unconditional PASS', 'row': row})
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
                      'semantic_interpretation': 'invalid setup' if invalid else 'requires all diagnostics and result assertions; no defect attribution from this parser'})
    return {'gate_passed': not errors and not unexpected and not missing and not failures and sequence == order,
            'expected_assertions': len(order), 'observed_known_assertions': len(records),
            'exact_assertion_order': sequence == order, 'expected_tasks': len(tasks),
            'harness_end': 'PASS' if not errors else 'rejected',
            'missing_assertions': missing, 'failed_assertions': failures,
            'unexpected_callbacks': unexpected, 'integrity_errors': errors,
            'tasks': tasks, 'assertions': [records[name] for name in order if name in records],
            'classification_policy': 'Setup failure invalidates semantic interpretation. Every assertion and the full lifecycle must pass. Unknown exception/missing rows reject the run without assigning a native bug.'}
