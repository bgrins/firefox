import copy
import json
from pathlib import Path
import analyze

HERE = Path(__file__).resolve().parent
value = dict(schema='COMMIT_STYLES_COST_V1', config=copy.deepcopy(analyze.CONFIG),
             caseOrder=analyze.CASES[:], rows=[], cleanup=[], valid=True,
             error=None, timingThresholds=False)
for index in range(54):
    round_ = index // 6
    case = analyze.CASES[(index % 6 + round_) % 6]
    family, count = case.split('/')
    value['rows'].append(dict(case=case, count=int(count), family=family, round=round_,
        warmup=round_ < 2, targets=16, calls=16, apiMs=round_ + 1, flushMs=int(count),
        totalMs=round_ + 1 + int(count), correctness='PASS'))
    value['cleanup'].append(dict(case=case, round=round_, removed=True, effectsCancelled=True))


def events(payload=None):
    payload = value if payload is None else payload
    return [dict(action='suite_start'), dict(action='test_start', test=analyze.TEST),
        dict(action='process_output', process='12345', command='/synthetic/A.app/firefox',
             data='console.log: ' + json.dumps(analyze.SUCCESS + json.dumps(payload))),
        dict(action='test_status', test=analyze.TEST, subtest=analyze.SUBTEST, status='PASS'),
        dict(action='test_end', test=analyze.TEST, status='OK'), dict(action='suite_end')]


def raw(items):
    return ''.join(json.dumps(item) + '\n' for item in items)


positives = []
parsed, _ = analyze.parse_raw(raw(events()))
assert parsed == value
summary = analyze.summarize(parsed)
assert summary['cases']['literal/1']['measured']['apiMs']['samples'] == [3, 4, 5, 6, 7, 8, 9]
assert summary['cases']['literal/1']['measured']['totalMs']['median'] == 7
positives.append('complete quoted dataset; exact sample retention and arithmetic')
delayed = events()
delayed.append(delayed.pop(2))
assert analyze.parse_raw(raw(delayed))[0] == value
positives.append('console reader delivery after suite_end retained')
zero = copy.deepcopy(value)
for row in zero['rows']:
    for metric in analyze.METRICS:
        row[metric] = 0
assert analyze.parse_raw(raw(events(zero)))[0] == zero
positives.append('zero durations accepted without thresholds')
large = copy.deepcopy(value)
large['rows'][-1].update(apiMs=1e20, flushMs=0, totalMs=1e20)
large_parsed, _ = analyze.parse_raw(raw(events(large)))
assert large_parsed == large
assert any(1e20 in c['measured']['apiMs']['samples'] for c in analyze.summarize(large_parsed)['cases'].values())
positives.append('large finite sample retained without filtering')
negative = {}


def reject(name, items):
    text = items if isinstance(items, str) else raw(items)
    try:
        analyze.parse_raw(text)
    except (ValueError, TypeError, KeyError) as error:
        negative[name] = str(error)
        return
    raise AssertionError('accepted false control: ' + name)


reject('missing dataset', [e for e in events() if e['action'] != 'process_output'])
duplicate = events()
duplicate.insert(3, copy.deepcopy(duplicate[2]))
reject('duplicate dataset', duplicate)
for name, data in {
    'incomplete envelope': 'console.log: ' + json.dumps(analyze.INCOMPLETE + ' {}'),
    'bare unquoted envelope': 'console.log: ' + analyze.SUCCESS + json.dumps(value),
    'wrong console prefix': 'console.warn: ' + json.dumps(analyze.SUCCESS + json.dumps(value)),
    'truncated envelope': 'console.log: "' + analyze.SUCCESS + '{',
    'nonstring console argument': 'console.log: ' + json.dumps(dict(marker=analyze.SUCCESS)),
    'duplicate payload key': 'console.log: ' + json.dumps(analyze.SUCCESS + '{"valid":true,"valid":true}'),
}.items():
    sample = events()
    sample[2]['data'] = data
    reject(name, sample)
for name, mutate in {
    'missing row': lambda x: x['rows'].pop(),
    'duplicate row': lambda x: x['rows'].__setitem__(1, copy.deepcopy(x['rows'][0])),
    'wrong row order': lambda x: x['rows'].reverse(),
    'wrong round': lambda x: x['rows'][0].update(round=1),
    'wrong warmup': lambda x: x['rows'][0].update(warmup=False),
    'wrong calls': lambda x: x['rows'][0].update(calls=15),
    'boolean count': lambda x: x['rows'][0].update(count=True),
    'pending calibration': lambda x: x['rows'][0].update(correctness='PENDING'),
    'false valid': lambda x: x.update(valid=False),
    'nonempty error': lambda x: x.update(error='failed'),
    'changed config': lambda x: x['config'].update(measured=8),
    'changed cases': lambda x: x['caseOrder'].reverse(),
    'missing cleanup': lambda x: x['cleanup'].pop(),
    'wrong cleanup identity': lambda x: x['cleanup'][0].update(case='variable/1'),
    'uncancelled effects': lambda x: x['cleanup'][0].update(effectsCancelled=False),
    'unremoved target': lambda x: x['cleanup'][0].update(removed=False),
    'negative timing': lambda x: x['rows'][0].update(apiMs=-1),
    'boolean timing': lambda x: x['rows'][0].update(apiMs=True),
    'NaN timing': lambda x: x['rows'][0].update(apiMs=float('nan')),
    'overflow float': lambda x: x['rows'][0].update(apiMs=float('inf')),
    'incorrect addition': lambda x: x['rows'][0].update(totalMs=99),
}.items():
    sample = copy.deepcopy(value)
    mutate(sample)
    reject(name, events(sample))
for action in ('suite_start', 'suite_end', 'test_start', 'test_status', 'test_end'):
    reject('missing ' + action, [e for e in events() if e['action'] != action])
sample = events()
sample[3]['status'] = 'FAIL'
reject('harness calibration FAIL', sample)
sample = events()
sample[3]['expected'] = 'FAIL'
reject('unexpected PASS metadata', sample)
sample = events()
sample[3]['known_intermittent'] = ['FAIL']
reject('intermittent metadata', sample)
sample = events()
sample[3]['subtest'] = 'other test'
reject('wrong harness name', sample)
sample = events()
sample[4]['status'] = 'ERROR'
reject('harness ERROR', sample)
sample = events()
sample[2].pop('command')
reject('missing browser command', sample)
sample = events()
sample[2]['process'] = True
reject('invalid process identity', sample)
reject('crash event', events() + [dict(action='crash')])
reject('infrastructure error', events() + [dict(action='log', level='ERROR')])
reject('duplicate raw key', '{"action":"suite_start","action":"suite_start"}\n')
check = dict(status='SYNTHETIC_COST_PARSER_CHECK_PASS', positives=positives,
             rejected_controls=negative, browser_evidence=False,
             actual_dataset_bound=False, performance_acceptance=None)
(HERE / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
print(json.dumps(dict(status=check['status'], positives=len(positives), negatives=len(negative))))
