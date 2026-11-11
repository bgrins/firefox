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


def parse(path):
    starts, ends, callbacks = {}, {}, {}
    suite_starts = suite_ends = 0
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        action = row.get('action')
        if action == 'suite_start':
            suite_starts += 1
        elif action == 'suite_end':
            suite_ends += 1
        elif action == 'test_start':
            test = row['test']
            assert test not in starts, ('duplicate test_start', test)
            starts[test] = True
        elif action == 'test_status':
            test, name = row['test'], row['subtest']
            assert test in starts and test not in ends, ('unpaired callback', test)
            key = (test, name)
            assert key not in callbacks, ('duplicate callback', key)
            callbacks[key] = {k: row[k] for k in ['test', 'subtest', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
        elif action == 'test_end':
            test = row['test']
            assert test in starts and test not in ends, ('unpaired test_end', test)
            ends[test] = {k: row[k] for k in ['test', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
    assert suite_starts == suite_ends == 1, (suite_starts, suite_ends)
    assert starts and set(starts) == set(ends), 'incomplete test lifecycle'
    for test, expected in expected_controls().items():
        actual = {name for (url, name) in callbacks if url == test}
        assert actual == expected, (test, actual ^ expected)
        assert ends[test]['status'] == 'OK', ends[test]
    for test in ['/web-animations/interfaces/KeyframeEffect/target.html', '/web-animations/interfaces/Animation/commitStyles.html']:
        assert test in ends and ends[test]['status'] == 'OK', test
        assert any(url == test for url, _ in callbacks), test
    for prefix in ['/web-animations/animation-model/combining-effects/', '/web-animations/animation-model/keyframe-effects/']:
        assert any(test.startswith(prefix) for test in ends), prefix
    assert len([key for key in callbacks if key[0].endswith('/KeyframeEffect/target.html')]) == 24
    return {'subtests': [callbacks[key] for key in sorted(callbacks)], 'harness': [ends[test] for test in sorted(ends)], 'subtest_count': len(callbacks), 'test_count': len(ends)}


def compare(base, candidate):
    def rows(result):
        return {(row['test'], row.get('subtest')): row['status'] for field in ['subtests', 'harness'] for row in result[field]}
    left, right = rows(base), rows(candidate)
    changes = [{'test': key[0], 'subtest': key[1], 'baseline': left.get(key), 'candidate': right.get(key)} for key in sorted(left.keys() | right.keys(), key=lambda x: (x[0], x[1] or '')) if left.get(key) != right.get(key)]
    return {'identical_callback_statuses_and_inventory': not changes, 'baseline_rows': len(left), 'candidate_rows': len(right), 'changes': changes, 'messages_compared': False}
