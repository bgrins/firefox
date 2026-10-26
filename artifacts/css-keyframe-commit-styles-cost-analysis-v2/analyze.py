import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import median

TEST = '/web-animations/interfaces/Animation/commit-styles-prefix-cost.html'
SUBTEST = 'commitStyles prefix cost: six calibrated cases, 54 raw timing rows'
SUCCESS = 'COMMIT_STYLES_COST_RESULT_V1 '
INCOMPLETE = 'COMMIT_STYLES_COST_INCOMPLETE_V1'
METRICS = ('apiMs', 'flushMs', 'totalMs')
CONFIG = dict(counts=[1, 8, 32], families=['literal', 'variable'], targets=16,
              warmups=2, measured=7, duration=1000, currentTime=500)
CASES = [f'{family}/{count}' for count in CONFIG['counts'] for family in CONFIG['families']]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(text):
    def invalid(value):
        raise ValueError('nonstandard JSON constant: ' + value)
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=invalid)


def exact(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(exact(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(exact(a, b) for a, b in zip(actual, expected))
    return actual == expected


def consistent_timings(api, flush, total):
    values = [float(value) for value in (api, flush, total)]
    exact_values = [Fraction.from_float(value) for value in values]
    # Each recorded subtraction has at most half an output ULP of rounding error.
    budget = sum(Fraction.from_float(math.ulp(value)) for value in values) / 2
    return abs(exact_values[0] + exact_values[1] - exact_values[2]) <= budget


def dataset(value):
    need(isinstance(value, dict) and set(value) == {
        'schema', 'config', 'caseOrder', 'rows', 'cleanup', 'valid', 'error', 'timingThresholds'},
        'exact dataset fields')
    need(value['schema'] == 'COMMIT_STYLES_COST_V1', 'dataset schema')
    need(exact(value['config'], CONFIG) and exact(value['caseOrder'], CASES), 'fixed configuration and cases')
    need(value['valid'] is True and value['error'] is None and value['timingThresholds'] is False,
         'complete calibrated dataset')
    need(isinstance(value['rows'], list) and len(value['rows']) == 54, '54 raw rows')
    need(isinstance(value['cleanup'], list) and len(value['cleanup']) == 54, '54 cleanup rows')
    row_fields = {'case', 'count', 'family', 'round', 'warmup', 'targets', 'calls',
                  'apiMs', 'flushMs', 'totalMs', 'correctness'}
    for index, (row, cleanup) in enumerate(zip(value['rows'], value['cleanup'])):
        round_ = index // 6
        case = CASES[(index % 6 + round_) % 6]
        family, count = case.split('/')
        need(isinstance(row, dict) and set(row) == row_fields, f'exact row fields {index}')
        expected = dict(case=case, count=int(count), family=family, round=round_,
                        warmup=round_ < 2, targets=16, calls=16, correctness='PASS')
        need(exact({k: row[k] for k in expected}, expected), f'row identity/calibration {index}')
        need(all(type(row[m]) in (int, float) and math.isfinite(row[m]) and row[m] >= 0
                 for m in METRICS), f'finite nonnegative timing {index}')
        need(consistent_timings(row['apiMs'], row['flushMs'], row['totalMs']),
             f'binary64 subtraction consistency {index}')
        need(exact(cleanup, dict(case=case, round=round_, removed=True, effectsCancelled=True)),
             f'cleanup {index}')
    return value


def parse_raw(text):
    events = []
    for line in text.splitlines():
        if not line.strip():
            continue
        event = decode(line)
        need(isinstance(event, dict) and isinstance(event.get('action'), str), 'structured raw event')
        events.append(event)
    need(events, 'nonempty raw log')
    groups = {action: [(i, e) for i, e in enumerate(events) if e['action'] == action]
              for action in ('suite_start', 'suite_end', 'test_start', 'test_status', 'test_end')}
    need(all(len(group) == 1 for group in groups.values()), 'one complete suite/test/subtest lifecycle')
    indexes = [groups[a][0][0] for a in groups]
    need(indexes[0] < indexes[2] < indexes[3] < indexes[4] < indexes[1], 'harness lifecycle ordering')
    for action in ('test_start', 'test_status', 'test_end'):
        need(groups[action][0][1].get('test') == TEST, 'exact selected test')
    for action, status in (('test_status', 'PASS'), ('test_end', 'OK')):
        event = groups[action][0][1]
        need(event.get('status') == status and event.get('expected', status) in (None, status),
             'actual and expected harness success')
        need(event.get('known_intermittent', []) == [], 'no intermittent metadata allowance')
        need(event.get('message') in (None, ''), 'no success message drift')
    need(groups['test_status'][0][1].get('subtest') == SUBTEST, 'exact calibration subtest')
    need(groups['suite_end'][0][1].get('status') in (None, 'OK'), 'suite success')
    results = []
    for i, event in enumerate(events):
        need(event['action'] != 'crash', 'no crash diagnostic')
        if event['action'] == 'assertion_count':
            need(all(type(event.get(k)) is int and event[k] == 0
                     for k in ('count', 'min_expected', 'max_expected')), 'no native assertions')
        if event['action'] == 'log':
            need(event.get('level') not in ('ERROR', 'CRITICAL', 'FATAL'), 'no infrastructure error')
        if event['action'] != 'process_output':
            continue
        data = event.get('data')
        need(isinstance(data, str), 'string process output')
        need(INCOMPLETE not in data, 'incomplete diagnostic reported')
        if SUCCESS.strip() not in data:
            continue
        need(groups['test_start'][0][0] < i, 'result after selected test start')
        need(data.startswith('console.log: '), 'known console envelope')
        message = decode(data[len('console.log: '):].rstrip('\r\n'))
        need(isinstance(message, str) and message.isascii() and message.startswith(SUCCESS),
             'ASCII success console string')
        process = event.get('process')
        need((type(process) is int and process > 0) or
             (isinstance(process, str) and process.isdecimal() and int(process) > 0), 'browser process identity')
        need(isinstance(event.get('command'), str) and event['command'].strip(), 'recorded browser command')
        results.append((dataset(decode(message[len(SUCCESS):])), dict(
            event_index=i, process=process, command=event['command'])))
    need(len(results) == 1, 'exactly one complete dataset')
    return results[0]


def summarize(value):
    output = {}
    for case in CASES:
        groups = {}
        for warmup in (True, False):
            rows = [r for r in value['rows'] if r['case'] == case and r['warmup'] is warmup]
            groups['warmup' if warmup else 'measured'] = {
                metric: dict(samples=[r[metric] for r in rows],
                             median=median(r[metric] for r in rows),
                             minimum=min(r[metric] for r in rows),
                             maximum=max(r[metric] for r in rows))
                for metric in METRICS}
        output[case] = groups
    return dict(status='VALIDATED_COST_DATASET', cases=output, raw_rows=54, warmup_rows=12,
                measured_rows=42, filtered_rows=0, descriptive_only=True,
                causal_claim=False, performance_acceptance=None, native_acceptance=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(args.output.is_absolute() and not args.output.exists() and not args.output.is_symlink(),
         'fresh absolute output directory')
    raw = args.raw.read_bytes()
    value, provenance = parse_raw(raw.decode('utf-8'))
    summary = summarize(value)
    summary['input_sha256'] = hashlib.sha256(raw).hexdigest()
    summary['console_event'] = provenance
    args.output.mkdir()
    (args.output / 'RAW.jsonl').write_bytes(raw)
    (args.output / 'DATASET.json').write_text(json.dumps(value, indent=2) + '\n')
    (args.output / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'cases'}))


if __name__ == '__main__':
    main()
