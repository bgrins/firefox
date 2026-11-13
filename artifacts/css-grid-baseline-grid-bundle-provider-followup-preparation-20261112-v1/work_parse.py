import argparse
import collections
import io
import json
import re
from pathlib import Path

FIELDS = 'seq stage id phase call demand site frame dirty children subtree v0 v1 v2 v3 v4 v5'.split()
STAGES = {'call-begin', 'call-end', 'cache-absent', 'key-dirty', 'key-valid',
          'key-mismatch', 'demand-hit', 'demand-miss', 'cache-hit', 'measure-begin',
          'measure-end', 'store-update', 'store-create', 'query-begin', 'query-end',
          'capture-begin', 'capture-end', 'producer-reset', 'producer-complete'}
QUERY = {0: None, 1: (0, 0), 2: (0, 1), 3: (1, 0), 4: (1, 1), 5: (2, 0), 6: (2, 1)}

MAX_RECORDS = 4194304
MAX_LINE_BYTES = 512
MAX_ACTIVE = 4096
MAX_CALL_RECORDS = 32
REPRESENTATIVES = 256

def validate_legacy_call(c, records, version):
    summaries, switches = [], []
    assert records[-1]['stage'] == 'call-end'
    stages = [r['stage'] for r in records]
    assert stages[0] == 'call-begin'
    key = [r for r in records if r['stage'] in {'cache-absent', 'key-dirty', 'key-valid', 'key-mismatch'}]
    assert len(key) == 1
    key = key[0]
    reason = key['stage']
    if reason in {'key-valid', 'key-mismatch'}:
        assert ((key['v0'], key['v1']) == (key['v2'], key['v3'])) == (reason == 'key-valid')
    if reason == 'key-dirty':
        assert key['subtree'] == 1
    d = records[0]['demand']
    decisions = [r for r in records if r['stage'] in {'demand-hit', 'demand-miss'}]
    if version == 'old' or reason != 'key-valid':
        assert not decisions
        hit = reason == 'key-valid'
    else:
        assert len(decisions) == 1
        decision = decisions[0]
        assert decision['v0'] == d and decision['v1'] in QUERY
        hit = decision['stage'] == 'demand-hit'
        assert hit == (d == 0 or d == decision['v1'])
        if not hit:
            reason = 'demand-miss'
            switches.append({'call': c, 'id': records[0]['id'], 'phase': records[0]['phase'],
                             'frame': records[0]['frame'], 'from': decision['v1'], 'to': d,
                             'key': key, 'decision': decision})
    query_begin = [r for r in records if r['stage'] == 'query-begin']
    query_end = [r for r in records if r['stage'] == 'query-end']
    expected = QUERY[d] if version == 'old' or not hit else None
    assert len(query_begin) == len(query_end) == (0 if expected is None else 1)
    query_events = []
    if expected is not None:
        qb, qe = query_begin[0], query_end[0]
        assert (qb['v0'], qb['v1']) == (qe['v0'], qe['v1']) == expected
        assert qb['seq'] < qe['seq']
        assert all(0 <= qe[f'v{i}'] <= 1048576 for i in [2, 3, 4])
        assert qe['v4'] <= qe['v3']
        query_events = ['query-begin', 'query-end']
    lookup = [key['stage']] + ([decisions[0]['stage']] if decisions else [])
    if hit:
        core = lookup + ['cache-hit']
    else:
        store = [r['stage'] for r in records if r['stage'] in {'store-create', 'store-update'}]
        assert len(store) == 1
        core = lookup + ['measure-begin']
        if version == 'demand':
            core += query_events
        core += store + ['measure-end']
    if version == 'old':
        core += query_events
    assert stages == ['call-begin'] + core + ['call-end'], (c, stages, core)
    summaries.append({'call': c, 'id': records[0]['id'], 'phase': records[0]['phase'],
                      'frame': records[0]['frame'], 'demand': d, 'site': records[0]['site'], 'hit': hit, 'reason': reason,
                      'query': query_end[0] if query_end else None})
    return summaries[0], switches[0] if switches else None


def validate_call(c, records, version):
    if version != 'bundle':
        return validate_legacy_call(c, records, version)
    return validate_bundle_call(c, records)


def validate_bundle_call(c, records):
    stages = [row['stage'] for row in records]
    assert stages[0] == 'call-begin' and stages[-1] == 'call-end'
    entry = records[0]
    d = entry['demand']
    keys = [row for row in records if row['stage'] in {'cache-absent', 'key-dirty', 'key-valid', 'key-mismatch'}]
    assert len(keys) == 1
    key = keys[0]
    reason = key['stage']
    if reason in {'key-valid', 'key-mismatch'}:
        assert ((key['v0'], key['v1']) == (key['v2'], key['v3'])) == (reason == 'key-valid')
    if reason == 'key-dirty':
        assert key['subtree'] == 1
    decisions = [row for row in records if row['stage'] in {'demand-hit', 'demand-miss'}]
    hit, switch = False, None
    lookup_state = None
    lookup = [reason]
    if reason == 'key-valid':
        assert len(decisions) == 1
        decision = decisions[0]
        assert decision['v0'] == d and decision['v1'] in QUERY
        stored, bundle, present = decision['v1'], decision['v2'], decision['v3']
        assert bundle in (0, 1) and present in (0, 1)
        assert not bundle or (stored >= 3 and present)
        assert stored != 0 or (not bundle and not present)
        hit = decision['stage'] == 'demand-hit'
        assert hit == (d == 0 or d == stored or (bundle and d >= 3))
        lookup.append(decision['stage'])
        lookup_state = dict(stored=stored, bundle=bundle, present=present, requested=d, hit=hit)
        if not hit:
            reason = 'demand-miss'
            switch = dict(call=c, id=entry['id'], phase=entry['phase'], frame=entry['frame'],
                          **{'from': stored, 'to': d}, key=key, decision=decision)
    else:
        assert not decisions
    qb = [row for row in records if row['stage'] == 'query-begin']
    qe = [row for row in records if row['stage'] == 'query-end']
    producer = [row for row in records if row['stage'].startswith('producer-')]
    begins = [row for row in records if row['stage'] == 'capture-begin']
    ends = [row for row in records if row['stage'] == 'capture-end']
    store = [row for row in records if row['stage'] in {'store-create', 'store-update'}]
    capture = None
    if hit:
        assert not qb and not qe and not producer and not begins and not ends and not store
        core = lookup + ['cache-hit']
    else:
        assert len(begins) == len(ends) == len(store) == 1
        begin, end = begins[0], ends[0]
        assert begin['v0'] == end['v0'] == d
        grid, produced, dirty = begin['v1'], begin['v2'], begin['v3']
        assert all(value in (0, 1) for value in (grid, produced, dirty, end['v1'], end['v2']))
        assert d < 3 or grid
        expected_bundle = bool(d >= 3 and grid and produced and not dirty)
        assert bool(end['v2']) == expected_bundle
        assert d != 0 or end['v1'] == 0
        assert d < 3 or end['v1'] == 1
        if grid:
            assert [row['stage'] for row in producer] == ['producer-reset'] + (['producer-complete'] if produced else [])
            assert producer[0]['v0'] == 0
            if produced:
                assert producer[1]['v0'] == 1
        else:
            assert not producer
        expected_queries = [(1, 0), (1, 1), (2, 0), (2, 1)] if expected_bundle else ([] if QUERY[d] is None else [QUERY[d]])
        assert len(qb) == len(qe) == len(expected_queries)
        for before, after, expected in zip(qb, qe, expected_queries):
            assert (before['v0'], before['v1']) == (after['v0'], after['v1']) == expected
            assert before['seq'] < after['seq']
            assert all(0 <= after[f'v{i}'] <= 1048576 for i in (2, 3, 4))
            assert after['v4'] <= after['v3']
            if expected[0] != 0:
                assert all(after[f'v{i}'] == 0 for i in (2, 3, 4))
        assert tuple(store[0][f'v{i}'] for i in (0, 1, 2)) == tuple(end[f'v{i}'] for i in (0, 1, 2))
        core = lookup + ['measure-begin'] + [row['stage'] for row in producer] + ['capture-begin']
        core += ['query-begin', 'query-end'] * len(expected_queries)
        core += ['capture-end', store[0]['stage'], 'measure-end']
        capture = dict(grid=grid, produced=produced, dirty=dirty, bundle=int(expected_bundle),
                       present=end['v1'], request=d)
    assert stages == ['call-begin'] + core + ['call-end'], (c, stages, core)
    return dict(call=c, id=entry['id'], phase=entry['phase'], frame=entry['frame'],
                demand=d, site=entry['site'], hit=hit, reason=reason,
                query=qe[0] if len(qe) == 1 else None, queries=qe, capture=capture,
                lookup=lookup_state), switch


def bounded_lines(stream, maximum):
    while True:
        line = stream.readline(maximum + 1)
        if not line:
            return
        assert len(line.encode('utf-8')) <= maximum, 'Oversized log line'
        yield line


def parse_lines(lines, version):
    assert version in {'old', 'demand', 'bundle'}
    active, stack = {}, []
    sequence = 0
    latest_call = 0
    reasons, queries, requests, sites, transitions = [collections.Counter() for _ in range(5)]
    phases, dimensions = {}, collections.Counter()
    representatives, misses = [], []
    totals = dict(calls=0, hits=0, measures=0, block_provider_calls=0,
                  block_line_visits=0, block_child_descents=0)
    maximum_active = 0
    capture_modes = collections.Counter()
    capture_dimensions = collections.Counter()
    bundle_reuses = collections.Counter()
    bundle_totals = dict(captures=0, captured_requested_exports=0, captured_present_answers=0,
                         bundled_captures=0, grid_scalar_reads=0, natural_query_calls=0)
    for line in lines:
        assert len(line.encode('utf-8')) <= MAX_LINE_BYTES
        assert 'TRUNCATED' not in line and line.startswith('GRIDWORK ')
        pairs = [part.split('=', 1) for part in line[len('GRIDWORK '):].split()]
        assert all(len(p) == 2 for p in pairs) and [p[0] for p in pairs] == FIELDS
        row = dict(pairs)
        for key in set(FIELDS) - {'stage', 'id', 'phase', 'site', 'frame'}:
            assert re.fullmatch(r'-?\d+', row[key])
            row[key] = int(row[key])
        sequence += 1
        assert sequence <= MAX_RECORDS and row['seq'] == sequence and row['call'] > 0
        assert row['stage'] in STAGES and row['demand'] in QUERY
        assert row['site'] in {'content', 'baseline'}
        assert row['site'] != 'content' or row['demand'] == 0
        assert re.fullmatch(r'gsw-(?:leaf|(?:level|peer)-(?:[0-9]|1[01]))', row['id'])
        assert re.fullmatch(r'seed|finished|prime[0-3]|sample[0-2]-toggle[0-7]', row['phase'])
        assert re.fullmatch(r'0x[0-9a-f]+', row['frame'])
        assert all(row[k] in [0, 1] for k in ['dirty', 'children', 'subtree'])
        call = row['call']
        if row['stage'] == 'call-begin':
            assert call > latest_call, 'Reused/out-of-order call identity'
            latest_call = call
            assert len(active) < MAX_ACTIVE
            active[call] = []
            stack.append(call)
            maximum_active = max(maximum_active, len(active))
        assert stack and stack[-1] == call, 'misnested call context'
        assert call in active
        records = active[call]
        assert len(records) < MAX_CALL_RECORDS
        if records:
            assert all(row[k] == records[0][k] for k in ['id', 'phase', 'demand', 'site', 'frame'])
        records.append(row)
        if row['stage'] != 'call-end':
            continue
        summary, miss = validate_call(call, records, version)
        phase = summary['phase']
        if version == 'bundle' and summary['capture'] is not None:
            cap = summary['capture']
            mode = str((cap['request'], cap['grid'], cap['produced'], cap['dirty'], cap['bundle'], cap['present']))
            capture_modes[mode] += 1
            capture_dimensions[(phase, summary['id'], summary['site'], mode)] += 1
        aggregate = phases.setdefault(phase, dict(calls=0, hits=0, measures=0,
            reasons=collections.Counter(), requests=collections.Counter(), sites=collections.Counter(),
            query_groups=collections.Counter(), demand_misses=collections.Counter(),
            block_provider_calls=0, block_line_visits=0, block_child_descents=0))
        if version == 'bundle':
            counts = dict(captures=int(summary['capture'] is not None), captured_requested_exports=0,
                          captured_present_answers=0, bundled_captures=0, grid_scalar_reads=0,
                          natural_query_calls=0)
            if summary['capture'] is not None:
                cap = summary['capture']
                counts.update(captured_requested_exports=int(cap['request'] != 0),
                              captured_present_answers=cap['present'], bundled_captures=cap['bundle'])
            lookup = summary['lookup']
            if lookup and lookup['hit'] and lookup['bundle'] and lookup['requested'] >= 3 and lookup['stored'] != lookup['requested']:
                direction = str((lookup['stored'], lookup['requested']))
                bundle_reuses[direction] += 1
                aggregate.setdefault('bundle_switch_hits', collections.Counter())[direction] += 1
            counts['grid_scalar_reads'] = sum(q['v0'] != 0 for q in summary['queries'])
            counts['natural_query_calls'] = sum(q['v0'] == 0 for q in summary['queries'])
            for name, value in counts.items():
                bundle_totals[name] += value
                aggregate[name] = aggregate.get(name, 0) + value
        for key, value in [('calls', 1), ('hits', int(summary['hit'])), ('measures', int(not summary['hit']))]:
            totals[key] += value
            aggregate[key] += value
        reasons[summary['reason']] += 1
        requests[str(summary['demand'])] += 1
        sites[summary['site']] += 1
        aggregate['reasons'][summary['reason']] += 1
        aggregate['requests'][str(summary['demand'])] += 1
        aggregate['sites'][summary['site']] += 1
        dimensions[(phase, summary['id'], summary['site'], summary['demand'], summary['reason'])] += 1
        for q in summary.get('queries', [summary['query']] if summary['query'] else []):
            group = str((q['v0'], q['v1']))
            queries[group] += 1
            aggregate['query_groups'][group] += 1
            for key, field in [('block_provider_calls', 'v2'), ('block_line_visits', 'v3'), ('block_child_descents', 'v4')]:
                totals[key] += q[field]
                aggregate[key] += q[field]
        summary['begin_seq'], summary['end_seq'] = records[0]['seq'], row['seq']
        if len(representatives) < REPRESENTATIVES:
            representatives.append(summary)
        if miss:
            transition = str((miss['from'], miss['to']))
            transitions[transition] += 1
            aggregate['demand_misses'][transition] += 1
            if len(misses) < REPRESENTATIVES:
                miss['begin_seq'], miss['end_seq'] = records[0]['seq'], row['seq']
                misses.append(miss)
        del active[call]
        stack.pop()
    assert sequence and totals['calls'] and not active and not stack
    return dict(status='PARSED complete tagged work stream', version=version, records=sequence,
        **totals, reasons=dict(reasons), query_groups=dict(queries), requests=dict(requests), sites=dict(sites),
        phase_totals=phases, exact_demand_miss_totals=dict(transitions),
        dimensions=[dict(phase=k[0], id=k[1], site=k[2], demand=k[3], reason=k[4], count=v) for k,v in sorted(dimensions.items())],
        details=representatives, demand_switch_misses=misses,
        representative_limit=REPRESENTATIVES, details_complete=totals['calls'] <= REPRESENTATIVES,
        miss_details_complete=sum(transitions.values()) <= REPRESENTATIVES,
        maximum_active_calls=maximum_active, timing_or_universal_bound_claim=False,
        **({'capture_modes': dict(capture_modes), 'bundle_totals': bundle_totals,
            'exact_bundle_switch_hits': dict(bundle_reuses),
            'capture_dimensions': [dict(phase=k[0], id=k[1], site=k[2], mode=k[3], count=v)
                                   for k,v in sorted(capture_dimensions.items())]} if version == 'bundle' else {}))


def parse(text, version):
    return parse_lines(io.StringIO(text), version)


def parse_file(path, version):
    with Path(path).open() as stream:
        return parse_lines(bounded_lines(stream, MAX_LINE_BYTES), version)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('version', choices=['old', 'demand', 'bundle'])
    p.add_argument('trace', type=Path)
    p.add_argument('out', type=Path)
    a = p.parse_args()
    a.out.write_text(json.dumps(parse_file(a.trace, a.version), indent=2) + '\n')
