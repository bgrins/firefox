COUNTER = '/css/css-contain/counter-scoping-append-invalidation.html'
QUOTE = '/css/css-contain/quote-scoping-append-invalidation.html'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def observation(row):
    return {key: row.get(key) for key in ('status', 'message', 'expected', 'known_intermittent')}


def values(result):
    rows = {(r['test'], r['subtest']): observation(r) for r in result['rows']}
    ends = {(r['test'], '<end>'): observation(r) for r in result['ends']}
    need(len(rows) == len(result['rows']) and len(ends) == len(result['ends']), 'unique observations')
    return rows | ends


def passed(row, status='PASS'):
    return row['status'] == status and row['expected'] in (None, status) and not row['known_intermittent']


def check(result, config, phase, captures, historical):
    need(phase in config['phases'] + ['failure-original'], 'known phase')
    current = values(result)
    names = {(t, n) for t, roster in config['expected_subtests'].items() for n in roster}
    counter = {key for key in names if key[0] == COUNTER}
    quote = {key for key in names if key[0] == QUOTE}
    ends = {(t, '<end>') for t in config['expected_subtests']} | {(t, '<end>') for t in config['expected_end_only']}
    need(len(counter) == 24 and len(quote) == 64 and len(names) == 88 and len(ends) == 10 and set(current) == names | ends, 'exact 88 rows and ten ends')
    for test, status in config['expected_end_only'].items():
        need(passed(current[test, '<end>'], status), 'eight existing expected regression ends')
    for test in config['expected_subtests']:
        need(passed(current[test, '<end>'], 'OK'), 'two successful harnesses')
    need(all(passed(current[k]) for k in quote), '64 quote controls PASS')
    old = {(r['test'], r['subtest']): observation(r) for r in historical['rows']}
    need(set(old) == counter and sum(r['status'] == 'FAIL' for r in old.values()) == 12
         and sum(r['status'] == 'PASS' for r in old.values()) == 12, 'actual historical 24 and 12 failures')
    original = phase in ('original-initial', 'original-restored', 'failure-original')
    if original:
        need(all(current[k] == old[k] for k in counter), 'original counter history exact')
    else:
        need(all(passed(current[k]) for k in counter), 'all 24 candidate counter PASS')
    if phase != 'original-initial':
        first = captures['original-initial']
        controls = quote | ends | {k for k in counter if old[k]['status'] == 'PASS'}
        need(all(current[k] == first[k] for k in controls), 'all controls, messages and optional fields exact')
        if original:
            need(current == first, 'repeated original exact')
    if phase == 'candidate-final':
        need(current == captures['candidate-first'], 'repeated candidate exact')
    return current
