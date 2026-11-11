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
    baseline = json.loads((HERE / 'EXPECTED-BASELINE.json').read_text())
    events = [{'action': 'suite_start'}]
    for test in sorted({r['test'] for r in baseline['harness']}):
        events.append({'action': 'test_start', 'test': test})
        events += [dict(r, action='test_status') for r in baseline['subtests'] if r['test'] == test]
        events += [dict(r, action='test_end') for r in baseline['harness'] if r['test'] == test]
    events.append({'action': 'suite_end'})
    rejected = []
    def rejects(label, operation):
        try:
            operation()
        except (AssertionError, ValueError, TypeError, KeyError):
            rejected.append(label)
        else:
            raise ValueError('Malformed control accepted: ' + label)
    with tempfile.TemporaryDirectory(prefix='owned-generation-parser-') as directory:
        def parse(rows):
            path = Path(directory) / 'raw.jsonl'
            path.write_text(''.join((r if isinstance(r, str) else json.dumps(r)) + '\n' for r in rows))
            return a.parse(path)
        parsed = parse(events)
        assert a.compare(baseline, parsed)['accepted_changes_only']
        assert a.compare(parsed, parsed)['accepted_changes_only']
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
            ('critical-log', events + [{'action': 'log', 'level': 'CRITICAL'}]),
            ('assertion-count', events + [{'action': 'assertion_count', 'count': 1, 'min_expected': 0, 'max_expected': 0}]),
            ('duplicate-json-key', ['{"action":"suite_start","action":"suite_start"}'] + events[1:]),
            ('callback-after-end', events + [events[callback]]),
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
            mutated = copy.deepcopy(parsed)
            mutated[field].append(copy.deepcopy(mutated[field][0]))
            rejects('duplicate-parsed-' + field, lambda mutated=mutated: a.compare(parsed, mutated))
        for status, replacement in [('PASS', 'FAIL'), ('FAIL', 'PASS')]:
            mutated = copy.deepcopy(parsed)
            next(r for r in mutated['subtests'] if r['status'] == status)['status'] = replacement
            assert not a.compare(parsed, mutated)['accepted_changes_only']
            rejected.append('unexpected-' + status + '-to-' + replacement)
        for group in ['subtests', 'harness']:
            mutated = copy.deepcopy(parsed)
            mutated[group].pop(0)
            assert not a.compare(parsed, mutated)['accepted_changes_only']
            rejected.append('lost-' + group)
            for field, value in [('message', 'changed diagnostic'), ('expected', 'changed classification'), ('known_intermittent', ['FAIL'])]:
                mutated = copy.deepcopy(parsed)
                mutated[group][0][field] = value
                assert not a.compare(parsed, mutated)['accepted_changes_only']
                rejected.append(group + '-' + field + '-change')
        collision = {'subtests': [{'test': '/collision', 'subtest': None, 'status': 'PASS'}], 'harness': [{'test': '/collision', 'status': 'OK'}]}
        assert len(a.rows(collision)) == 2 and a.compare(collision, collision)['accepted_changes_only']
        changed = copy.deepcopy(collision)
        changed['subtests'][0]['status'] = 'FAIL'
        assert not a.compare(collision, changed)['accepted_changes_only']
        rejected.append('callback-harness-key-collision')
    assert len(rejected) == len(set(rejected))
    return {'status': 'pass', 'synthetic_only': True, 'callback_count': len(parsed['subtests']), 'rejected_controls': rejected, 'builds_or_browser_tests_executed': False}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
