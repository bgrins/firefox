import collections
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def raw(name):
    events = [json.loads(line) for line in (HERE / name).read_text().splitlines()]
    rows = {}
    for event in events:
        assert event['action'] not in ('crash', 'assertion_count')
        if event['action'] not in ('test_status', 'test_end'):
            continue
        key = (event['action'], event['test'], event.get('subtest', ''))
        assert key not in rows
        rows[key] = (event['status'], event.get('message') or '')
    expected = {('test_status', *pair) for pair in read('EXPECTED-CALLBACKS.json')}
    expected |= {('test_end', pair[0], '') for pair in read('EXPECTED-CALLBACKS.json')}
    assert set(rows) == expected and len(rows) == 99
    assert all(value[0] == 'OK' for key, value in rows.items() if key[0] == 'test_end')
    return rows


baseline = raw('baseline1/wpt-raw.jsonl')
candidate = raw('candidate1/wpt-raw.jsonl')
improvements = {('test_status', row['test'], row['subtest']) for row in read('EXPECTED-CHANGES.json')}
assert len(improvements) == 3
for key in baseline:
    if key in improvements:
        assert baseline[key][0] == 'FAIL' and candidate[key][0] == 'PASS'
    else:
        assert baseline[key] == candidate[key], key

counts = {}
for name, rows, expected in [('baseline1', baseline, {'PASS': 77, 'FAIL': 12, 'OK': 10}),
                             ('candidate1', candidate, {'PASS': 80, 'FAIL': 9, 'OK': 10})]:
    counts[name] = dict(collections.Counter(value[0] for value in rows.values()))
    assert counts[name] == expected
    result = read(name + '/RESULT.json')
    assert result['error'] is None and result['restoration_verified']
    assert result['restoration_errors'] == []
    assert result['commands']['lint']['exit_code'] == 0
    assert result['commands']['wpt']['exit_code'] in (0, 1)
    assert all(command.get('group_absent', True) for command in result['commands'].values())
    assert not (HERE / name / 'backups').exists()
assert read('candidate1/BUILD.json')['command_result']['exit_code'] == 0
assert not (HERE / 'runtime.lock').exists()
paths = ['baseline1/wpt-raw.jsonl', 'candidate1/wpt-raw.jsonl',
         'baseline1/RESULT.json', 'candidate1/RESULT.json', 'candidate1/build.log']
report = {
    'status': 'PASS', 'raw_counts': counts, 'exact_improvements': 3,
    'other_statuses_and_messages_identical': True,
    'source_and_full_app_restoration': 'Runner receipts; independent live audit recorded separately',
    'nonfatal_build_monitor_keyerrors': (HERE / 'candidate1/build.log').read_text().count("KeyError: 'export'"),
    'sha256': {path: hashlib.sha256((HERE / path).read_bytes()).hexdigest() for path in paths},
}
(HERE / 'ROOT-RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
