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
    starts, ends, callbacks = {}, {}, {}
    suite_active = False
    suite_starts = suite_ends = 0
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        action = row.get('action')
        assert action != 'crash', row
        assert not (action == 'log' and row.get('level') in ['ERROR', 'CRITICAL']), row
        if action == 'suite_start':
            assert not suite_active and suite_starts == 0
            suite_active = True
            suite_starts += 1
        elif action == 'suite_end':
            assert suite_active and starts and set(starts) == set(ends)
            suite_active = False
            suite_ends += 1
        elif action == 'test_start':
            assert suite_active
            test = row['test']
            assert test not in starts, ('duplicate test_start', test)
            starts[test] = True
        elif action == 'test_status':
            test, name = row['test'], row['subtest']
            assert test in starts and test not in ends, ('unpaired callback', test)
            assert isinstance(name, str) or name is None
            key = (test, name)
            assert key not in callbacks, ('duplicate callback', key)
            assert row['status'] in ['PASS', 'FAIL'], row
            callbacks[key] = {k: row[k] for k in ['test', 'subtest', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
        elif action == 'test_end':
            test = row['test']
            assert test in starts and test not in ends, ('unpaired test_end', test)
            assert row['status'] == 'OK', row
            ends[test] = {k: row[k] for k in ['test', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
        elif action == 'assertion_count':
            assert row['min_expected'] <= row['count'] <= row['max_expected'], row
    assert suite_starts == suite_ends == 1, (suite_starts, suite_ends)
    assert starts and set(starts) == set(ends)
    plan = json.loads((HERE/'RUN-PLAN.json').read_text())
    expected_pages = {'/'+name.removeprefix('testing/web-platform/tests/') for name in plan['suites']}
    assert set(ends) == expected_pages, (set(ends), expected_pages)
    assert all(any(url == test for url, _ in callbacks) for test in ends)
    expected = {tuple(row) for row in json.loads((HERE / 'EXPECTED-CALLBACKS.json').read_text())}
    assert set(callbacks) == expected, ('callback inventory changed', set(callbacks) ^ expected)
    return {'subtests': [callbacks[key] for key in sorted(callbacks, key=repr)],
            'harness': [ends[test] for test in sorted(ends)],
            'subtest_count': len(callbacks), 'test_count': len(ends)}


def rows(result):
    output = {}
    for kind, field in [('assertion', 'subtests'), ('harness', 'harness')]:
        for row in result[field]:
            key = (kind, row['test'], row.get('subtest'))
            assert key not in output, ('duplicate comparison key', key)
            output[key] = row['status']
    return output


def compare(base, candidate):
    left, right = rows(base), rows(candidate)
    changes = [{'kind': key[0], 'test': key[1], 'subtest': key[2],
                'baseline': left.get(key), 'candidate': right.get(key)}
               for key in sorted(left.keys() | right.keys(), key=repr)
               if left.get(key) != right.get(key)]
    assert json.loads((HERE / 'EXPECTED-CHANGES.json').read_text()) == []
    def details(result):
        return {(kind, row['test'], row.get('subtest')):
                {field: row[field] for field in ['message', 'expected', 'known_intermittent'] if field in row}
                for kind, group in [('assertion', 'subtests'), ('harness', 'harness')]
                for row in result[group]}
    ld, rd = details(base), details(candidate)
    detail_changes = [key for key in sorted(ld.keys() | rd.keys(), key=repr)
                      if ld.get(key) != rd.get(key)]
    return {'accepted_changes_only': set(left) == set(right) and not changes and not detail_changes,
            'policy': 'zero changes', 'baseline_rows': len(left), 'candidate_rows': len(right),
            'identical_callback_statuses_and_inventory': set(left) == set(right) and not changes,
            'assertion_and_harness_kinds_distinct': True, 'changes': changes,
            'messages_and_expected_classifications_compared': True,
            'unexpected_detail_changes': detail_changes}
