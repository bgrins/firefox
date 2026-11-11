import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = '/web-animations/animation-model/keyframe-effects/'
CONTROL = PREFIX + 'clip-auto-composition.html'
EXISTING = PREFIX + 'effect-value-iteration-composite-operation.html'
DIAGNOSTIC = PREFIX + 'svg-clip-auto-preservation-diagnostic.html'
CLIP = 'iteration composition of incompatible clip rects (accumulation skipped at 0%, allowed at 50%)'
NEW_FAILURES = {
    'Iteration composition: matching auto components accumulate',
    'Effect composition add: matching auto components combine',
    'Effect composition accumulate: matching auto components combine',
}
NEW_CONTROLS = NEW_FAILURES | {
    'Iteration composition: first iteration retains matching auto',
    'Iteration composition: numeric components accumulate',
    'Iteration composition: top-level auto remains auto',
    'Effect addition: numeric components combine',
    'Effect addition: mismatched component types retain the effect value',
    'Effect addition: top-level auto remains auto',
}
MARKER = 'CLIP_SMIL_OBSERVATION '


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result, ('duplicate JSON key', key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def diagnostic_inputs():
    expected = {}
    for kind, underlying in [('numeric', 'rect(3px, 7px, 11px, 13px)'),
                             ('mixed', 'rect(auto, 7px, 11px, 13px)')]:
        for accumulate in ['none', 'sum']:
            for time in [0.5, 2.5]:
                expected[f'repeat-{kind}-{accumulate}-{time}'] = (time, underlying)
        for mode in ['sandwich', 'by-only']:
            expected[f'{mode}-{kind}'] = (0.5, underlying)
    return expected


def observation(data, observations):
    assert data.count(MARKER) == 1, 'multiple diagnostic records in one output event'
    row = strict_json(data.split(MARKER, 1)[1])
    assert set(row) == {'schema', 'id', 'time', 'underlying', 'clip', 'paused'}
    assert type(row['schema']) is int and row['schema'] == 1
    assert row['id'] in diagnostic_inputs() and row['id'] not in observations
    time, underlying = diagnostic_inputs()[row['id']]
    assert type(row['time']) in [int, float] and row['time'] == time
    assert row['underlying'] == underlying
    assert type(row['paused']) is bool and row['paused']
    assert isinstance(row['clip'], str) and row['clip']
    observations[row['id']] = row


def parse(path, flavor):
    assert flavor in ['wpt', 'mochitest']
    starts, ends, callbacks, observations = {}, {}, [], {}
    occurrences = Counter()
    suite_starts = suite_ends = 0
    suite_active = False
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        action = row.get('action')
        assert action != 'crash', row
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
            key = (test, name)
            if flavor == 'wpt':
                assert occurrences[key] == 0, ('duplicate WPT callback', key)
            record = {k: row[k] for k in ['test', 'subtest', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
            record['occurrence'] = occurrences[key]
            occurrences[key] += 1
            callbacks.append(record)
        elif action == 'test_end':
            test = row['test']
            assert test in starts and test not in ends, ('unpaired test_end', test)
            ends[test] = {k: row[k] for k in ['test', 'status', 'message', 'expected', 'known_intermittent'] if k in row}
        elif action == 'process_output' and MARKER in row.get('data', ''):
            assert flavor == 'wpt'
            observation(row['data'], observations)
    assert suite_starts == suite_ends == 1, (suite_starts, suite_ends)
    assert starts and set(starts) == set(ends), 'incomplete test lifecycle'
    harness_status = 'OK' if flavor == 'wpt' else 'PASS'
    assert all(row['status'] == harness_status for row in ends.values()), ends
    if flavor == 'wpt':
        expected = {
            CONTROL: NEW_CONTROLS,
            EXISTING: {r['subtest'] for r in json.loads((HERE/'runtime-inputs/existing-iteration-callbacks.json').read_text())},
            DIAGNOSTIC: {'SMIL diagnostic numeric controls are active'},
        }
        assert set(ends) == set(expected), (set(ends), set(expected))
        for test, names in expected.items():
            actual = {r['subtest'] for r in callbacks if r['test'] == test}
            assert actual == names, (test, actual ^ names)
        assert set(observations) == set(diagnostic_inputs()), 'missing diagnostic observations'
    else:
        expected = set(json.loads((HERE/'RUN-PLAN.json').read_text())['mochitests'])
        normalized = {test: test.removeprefix('/tests/').removeprefix('/') for test in ends}
        assert set(normalized.values()) == expected, normalized
        assert all(any(r['test'] == test for r in callbacks) for test in ends)
        assert not observations
    return {'flavor': flavor, 'subtests': callbacks, 'harness': [ends[t] for t in sorted(ends)],
            'observations': observations, 'subtest_count': len(callbacks), 'test_count': len(ends)}


def baseline_check(results):
    wpt, mochi = results['wpt'], results['mochitest']
    expected = {(CONTROL, name): 'FAIL' if name in NEW_FAILURES else 'PASS' for name in NEW_CONTROLS}
    expected.update({(EXISTING, r['subtest']): r['status'] for r in json.loads((HERE/'runtime-inputs/existing-iteration-callbacks.json').read_text())})
    expected[DIAGNOSTIC, 'SMIL diagnostic numeric controls are active'] = 'PASS'
    observed = {(r['test'], r['subtest']): r['status'] for r in wpt['subtests']}
    assert observed == expected, 'baseline WPT differs from predicted gate; retain results for review'
    assert all(r['status'] in ['PASS', 'FAIL'] and r.get('expected', r['status']) == r['status'] for r in mochi['subtests']), 'unexpected baseline SMIL result; retain results for review'
    return {'predicted_wpt_statuses_observed': True, 'smil_callbacks_match_harness_expectations': True,
            'smil_status_counts': dict(Counter(r['status'] for r in mochi['subtests'])),
            'svg_observations_are_preservation_baseline_not_normative_assertions': True}


def compare(base, candidate):
    def rows(result):
        return {(flavor, row['test'], row.get('subtest'), row.get('occurrence', 0)): row['status']
                for flavor, data in result.items() for field in ['subtests', 'harness'] for row in data[field]}
    left, right = rows(base), rows(candidate)
    intended = {('wpt', CONTROL, name, 0) for name in NEW_FAILURES} | {('wpt', EXISTING, CLIP, 0)}
    changes = [{'key': key, 'baseline': left.get(key), 'candidate': right.get(key)}
               for key in sorted(left.keys() | right.keys(), key=repr) if left.get(key) != right.get(key)]
    actual = {tuple(row['key']) for row in changes}
    good = set(left) == set(right) and actual == intended and all(row['baseline'] == 'FAIL' and row['candidate'] == 'PASS' for row in changes)
    observations_equal = base['wpt']['observations'] == candidate['wpt']['observations']
    return {'expected_css_improvements_only': good, 'svg_observations_unchanged': observations_equal,
            'baseline_rows': len(left), 'candidate_rows': len(right), 'changes': changes,
            'svg_observation_count': len(candidate['wpt']['observations']),
            'messages_compared': False, 'gate_passed': good and observations_equal}
