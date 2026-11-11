import json
from pathlib import Path

CONTROL20 = '/web-animations/interfaces/KeyframeEffect/pseudo-compose-cssom-lifetime.html'
CONTROL9 = '/web-animations/interfaces/KeyframeEffect/pseudo-compose-underlying.html'


def expected_controls():
    twenty = {
        f'Retained {label} pseudo computed style: {phase}'
        for label in ['generated', 'non-generated']
        for phase in ['before', 'half', 'seek', 'cancel', 'restart']
    } | {
        f'Retained {label} pseudo computed style after setKeyframes: {prop}'
        for label in ['generated', 'non-generated']
        for prop in ['marginLeft', 'opacity']
    } | {
        f'Retained {label} pseudo computed styles follow retargeting'
        for label in ['generated', 'non-generated']
    } | {
        f'Relative endpoints update in retained {label} pseudo computed style'
        for label in ['generated', 'non-generated']
    } | {
        f'Ordered replace and add effects compose for a {label} pseudo'
        for label in ['generated', 'non-generated']
    }
    nine = {
        text.format(label=label)
        for label in ['generated', 'non-generated']
        for text in [
            'Implicit starting keyframe uses the underlying {label} pseudo style',
            'Underlying style changes update a paused {label} pseudo animation',
            'Important style wins over the {label} pseudo animation',
            'Cancellation restores the underlying {label} pseudo style',
        ]
    } | {'Transform animation survives pseudo generation and removal after computed-style reads'}
    return {CONTROL20: twenty, CONTROL9: nine}


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
    for test, expected in expected_controls().items():
        actual = {name for (url, name) in callbacks if url == test}
        assert actual == expected, (test, actual ^ expected)
    target = '/web-animations/interfaces/KeyframeEffect/target.html'
    assert len([key for key in callbacks if key[0] == target]) == 24
    attribute = '/css/css-animations/keyframe-attribute-mutation.html'
    names = {f'Keyframe attr mutation: {mode}, {qualification}, {history}'
             for mode, qualification in [(m, 'unqualified') for m in ['CSS ordinary', 'CSS registered', 'WAAPI ordinary', 'WAAPI registered']]+[('CSS ordinary', 'qualified')]
             for history in ['retained', 'fresh']}
    names |= {f'Keyframe attr mutation: ordinary-style control, {qualification}' for qualification in ['qualified','unqualified']}
    assert {name for (url, name) in callbacks if url == attribute} == names
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
               for key in sorted(left.keys() | right.keys(), key=repr) if left.get(key) != right.get(key)]
    return {'identical_callback_statuses_and_inventory': not changes,
            'baseline_rows': len(left), 'candidate_rows': len(right),
            'assertion_and_harness_kinds_distinct': True,
            'changes': changes, 'messages_compared': False}
