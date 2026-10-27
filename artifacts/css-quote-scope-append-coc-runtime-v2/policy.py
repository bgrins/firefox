import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def observation(row):
    return {'status': row['status'], 'expected': row.get('expected') or row['status'],
            'message': row.get('message'), 'known_intermittent': row.get('known_intermittent') or []}


def values(result):
    rows = {(r['test'], r['subtest']): observation(r) for r in result['rows']}
    ends = {(r['test'], '<end>'): observation(r) for r in result['ends']}
    need(len(rows) == len(result['rows']) and len(ends) == len(result['ends']), 'unique observations')
    return rows | ends


def check(result, config, phase, first):
    need(phase in config['phases'], 'C/O/C phase')
    current = values(result)
    names = {(t, n) for t, roster in config['expected_subtests'].items() for n in roster}
    end_names = {(t, '<end>') for t in config['expected_subtests']} | {(t, '<end>') for t in config['expected_end_only']}
    need(len(names) == 64 and len(end_names) == 19 and set(current) == names | end_names, 'exact 64 plus 19 ends')
    for t, status in config['expected_end_only'].items():
        row = current[t, '<end>']
        need(row['status'] == row['expected'] == status and not row['known_intermittent'], '15 PASS and three expected FAIL regressions')
    for t in config['expected_subtests']:
        row = current[t, '<end>']
        need(row['status'] == row['expected'] == 'OK' and not row['known_intermittent'], 'one successful harness')
    if phase != 'scoped-original':
        need(all(current[k]['status'] == current[k]['expected'] == 'PASS' and not current[k]['known_intermittent'] for k in names), 'all 64 candidate PASS')
    if phase == 'scoped-original':
        historical = json.loads((HERE / 'HISTORICAL-OBSERVATIONS.json').read_text())['original']
        old = {(r['test'], r['subtest']): observation(r) for r in historical}
        need(set(old) == names and sum(r['status'] == 'FAIL' for r in old.values()) == 12, 'historical 12 identities')
        need(all(current[k] == old[k] for k in names), 'original calibrated 52 PASS / 12 failures exact')
        need(first is not None and all(current[k] == first[k] for k in names if old[k]['status'] == 'PASS'), '52 current controls exact')
        need(all(current[k] == first[k] for k in end_names), 'all current regression and harness observations exact')
    if phase == 'candidate-restored':
        need(first is not None and current == first, 'both candidate observations exact')
    return current
