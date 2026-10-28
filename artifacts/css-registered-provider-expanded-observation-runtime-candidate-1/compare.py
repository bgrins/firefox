import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'css-registered-provider-expanded-observation-runtime-baseline-1'

def collect(path):
    rows = {}
    ends = {}
    for line in path.read_text().splitlines():
        event = json.loads(line)
        if event.get('action') == 'test_status':
            key = (event['test'], event['subtest'])
            assert key not in rows
            rows[key] = {name: event.get(name) for name in ['status', 'expected', 'known_intermittent', 'message']}
        if event.get('action') == 'test_end':
            assert event['test'] not in ends
            ends[event['test']] = event['status']
    return rows, ends

before, before_ends = collect(BASE / 'raw.jsonl')
after, after_ends = collect(HERE / 'raw.jsonl')
assert before.keys() == after.keys() and len(after) == 775
assert before_ends == after_ends and len(after_ends) == 36
assert collections.Counter(after_ends.values()) == {'OK': 30, 'PASS': 6}
for directory in [BASE, HERE]:
    assessment = json.loads((directory / 'ASSESSMENT.json').read_text())
    assert assessment['complete'] and assessment['execution_preserved']
    assert not assessment['errors'] and not assessment['comparison_errors'] and not assessment['infrastructure_faults']
changes = []
for key in before:
    if before[key] != after[key]:
        item = {'test': key[0], 'subtest': key[1], 'before': before[key], 'after': after[key]}
        if 'registered-initial-color-context.html' in key[0]:
            for label, row in [('before_snapshots', before[key]), ('after_snapshots', after[key])]:
                message = row['message']
                snapshots, _ = json.JSONDecoder().raw_decode(message[message.index('[{'):])
                assert len(snapshots) == 3
                item[label] = snapshots
        changes.append(item)
transitions = collections.Counter((item['before']['status'], item['after']['status']) for item in changes)
assert transitions == {('FAIL', 'PASS'): 20, ('FAIL', 'FAIL'): 4}
family_counts = {}
for test in after_ends:
    family_counts[test] = {'before': dict(collections.Counter(row['status'] for key, row in before.items() if key[0] == test)), 'after': dict(collections.Counter(row['status'] for key, row in after.items() if key[0] == test))}
result = {'baseline_sha256': hashlib.sha256((BASE / 'raw.jsonl').read_bytes()).hexdigest(), 'candidate_sha256': hashlib.sha256((HERE / 'raw.jsonl').read_bytes()).hexdigest(), 'assertions': 775, 'unchanged_signatures': 751, 'baseline_statuses': dict(collections.Counter(x['status'] for x in before.values())), 'candidate_statuses': dict(collections.Counter(x['status'] for x in after.values())), 'changed_statuses': 20, 'same_status_changed_messages': 4, 'test_end_statuses_equal': True, 'harness_ends': 30, 'passing_reftests': 6, 'family_counts': family_counts, 'changes': changes, 'native_fix_accepted': False}
(HERE / 'COMPARISON.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({key: value for key, value in result.items() if key not in ['family_counts', 'changes']}, indent=2))
