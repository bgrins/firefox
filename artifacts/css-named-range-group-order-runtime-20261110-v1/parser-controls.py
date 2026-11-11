import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('analysis', HERE / 'analyze.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def main():
    expected = json.loads((HERE / 'EXPECTED-CALLBACKS.json').read_text())
    changes = json.loads((HERE / 'EXPECTED-CHANGES.json').read_text())
    improving = {(r['test'], r['subtest']) for r in changes}
    expected_baseline = json.loads((HERE / 'EXPECTED-BASELINE.json').read_text())
    baseline_statuses = {(r['test'], r['subtest']): r['status'] for r in expected_baseline['subtests']}
    events = [{'action': 'suite_start'}]
    for test in sorted({r[0] for r in expected}):
        events.append({'action': 'test_start', 'test': test})
        for url, name in expected:
            if url == test:
                events.append({'action': 'test_status', 'test': test, 'subtest': name,
                               'status': baseline_statuses[(test, name)]})
        events.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    events.append({'action': 'suite_end'})
    rejected = []

    def rejects(label, operation):
        try:
            operation()
        except (AssertionError, ValueError, TypeError, KeyError):
            rejected.append(label)
        else:
            raise ValueError('Malformed control accepted: ' + label)

    with tempfile.TemporaryDirectory(prefix='keyframe-order-parser-') as directory:
        def parse(rows):
            path = Path(directory) / 'raw.jsonl'
            path.write_text(''.join((r if isinstance(r, str) else json.dumps(r)) + '\n' for r in rows))
            return a.parse(path)

        baseline = parse(events)
        assert a.rows(baseline) == a.rows(expected_baseline)
        wrong_baseline = copy.deepcopy(baseline)
        next(r for r in wrong_baseline['subtests'] if r['status'] == 'FAIL' and (r['test'], r['subtest']) not in improving)['status'] = 'PASS'
        assert a.rows(wrong_baseline) != a.rows(expected_baseline)
        rejected.append('changed-known-baseline-failure')
        candidate_events = copy.deepcopy(events)
        for row in candidate_events:
            if row['action'] == 'test_status' and (row['test'], row['subtest']) in improving:
                row['status'] = 'PASS'
        candidate = parse(candidate_events)
        assert a.compare(baseline, candidate)['accepted_changes_only']
        assert not a.compare(baseline, baseline)['accepted_changes_only']
        assert not a.compare(candidate, candidate)['accepted_changes_only']
        rejected += ['missing-improvements', 'already-passing-baseline']
        callback = next(i for i, r in enumerate(events) if r['action'] == 'test_status')
        ending = next(i for i, r in enumerate(events) if r['action'] == 'test_end')
        for label, mutated in [
            ('duplicate-callback', events[:callback] + [events[callback]] + events[callback:]),
            ('duplicate-harness', events[:ending] + [events[ending]] + events[ending:]),
            ('missing-callback', events[:callback] + events[callback + 1:]),
            ('missing-harness', events[:ending] + events[ending + 1:]),
            ('missing-suite-end', events[:-1]),
            ('early-suite-end', [events[0], events[-1]] + events[1:-1]),
            ('duplicate-test-start', events[:1] + [events[1]] + events[1:]),
            ('crash', events + [{'action': 'crash'}]),
            ('error-log', events + [{'action': 'log', 'level': 'ERROR'}]),
            ('assertion-count', events + [{'action': 'assertion_count', 'count': 1, 'min_expected': 0, 'max_expected': 0}]),
            ('duplicate-json-key', ['{"action":"suite_start","action":"suite_start"}'] + events[1:]),
        ]:
            rejects(label, lambda mutated=mutated: parse(mutated))
        for label, index, field, value in [
            ('timeout', callback, 'status', 'TIMEOUT'),
            ('wrong-harness-kind', ending, 'status', 'PASS'),
            ('wrong-name', callback, 'subtest', 'wrong callback'),
            ('null-name', callback, 'subtest', None),
        ]:
            mutated = copy.deepcopy(events)
            mutated[index][field] = value
            rejects(label, lambda mutated=mutated: parse(mutated))
        for field in ['subtests', 'harness']:
            mutated = copy.deepcopy(candidate)
            mutated[field].append(copy.deepcopy(mutated[field][0]))
            rejects('duplicate-parsed-' + field, lambda mutated=mutated: a.compare(baseline, mutated))
        for label, edit in [
            ('unexpected-regression', lambda d: next(r for r in d['subtests'] if (r['test'], r['subtest']) not in improving).update(status='FAIL')),
            ('lost-assertion', lambda d: d['subtests'].pop()),
            ('lost-harness', lambda d: d['harness'].pop()),
            ('partial-improvement', lambda d: next(r for r in d['subtests'] if (r['test'], r['subtest']) in improving).update(status='FAIL')),
        ]:
            mutated = copy.deepcopy(candidate)
            edit(mutated)
            assert not a.compare(baseline, mutated)['accepted_changes_only'], label
            rejected.append(label)
        mutated = copy.deepcopy(candidate)
        next(r for r in mutated['subtests'] if (r['test'], r['subtest']) not in improving)['message'] = 'changed diagnostic'
        assert not a.compare(baseline, mutated)['accepted_changes_only']
        rejected.append('unexpected-message-change')
        mutated = copy.deepcopy(candidate)
        next(r for r in mutated['subtests'] if (r['test'], r['subtest']) in improving)['message'] = 'intentional improvement'
        assert a.compare(baseline, mutated)['accepted_changes_only']
        collision = {'subtests': [{'test': '/collision', 'subtest': None, 'status': 'PASS'}],
                     'harness': [{'test': '/collision', 'status': 'OK'}]}
        assert len(a.rows(collision)) == 2
        mutated = copy.deepcopy(collision)
        mutated['subtests'][0]['status'] = 'FAIL'
        assert a.rows(collision) != a.rows(mutated)
        rejected.append('callback-harness-key-collision')
    return {'status': 'pass', 'synthetic_only': True, 'callback_count': len(expected),
            'rejected_controls': rejected, 'builds_or_browser_tests_executed': False}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
