import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / 'artifacts/css-contextual-duration-first-read-trace-browser-runtime-1'
JOIN = ROOT / 'artifacts/css-contextual-duration-first-read-trace-root-join-v1.json'
KEY = ('pid', 'window', 'document', 'compositor', 'target', 'pseudo', 'identifier', 'cascade')
BARRIERS = {'post-attempt', 'pre-post-hint', 'pre-will-compose', 'pre-remove-consumed',
            'pre-remove-no-effects', 'pre-remove-wrong-document', 'pre-clear'}
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(JOIN) == 'a3558422b63c7f5f39a9dd834351cdfdb4d47f0bee255092ff4a715e7d4fbdd3'
    assert sha(RUNTIME / 'FILES.json') == 'e4fd2432f89c2279b051cccce39f4d6a8facff4c9e95877b89f349f9cd5f07d4'
    report = read(RUNTIME / 'TRACE.json')
    assert report['syntax_and_sequence_valid'] and report['closed_query_scopes']
    assert not report['caps'] and not report['limitations'] and not report['errors']
    by_query = {(q['entry']['pid'], q['entry']['query']): q for q in report['queries']}
    rows = []
    for group in read(JOIN)['groups']:
        events = [row['event'] for row in group['first_child_query']['events']]
        query = by_query[group['identity']['pid'], group['first_child_query']['query_id']]
        assert events == query['events']
        for event in events:
            assert all(event[name] == group['identity'][name] for name in ('pid', 'window', 'document'))
        child = tuple(group['role_targets']['child'])
        is_child = lambda e: tuple(e[k] for k in ('target', 'pseudo', 'identifier')) == child
        snapshots = [e for e in events if e['stage'] == 'snapshot-query-key' and is_child(e) and e['cascade'] == 0]
        assert snapshots and snapshots[0]['state'] == -1
        key = tuple(snapshots[0][k] for k in KEY)
        matches = lambda e: tuple(e[k] for k in KEY) == key
        child_events = [e for e in events if matches(e)]
        pending = [e for e in child_events if e['stage'] == 'request-state' and e['state'] == 1]
        barriers = [e for e in events if e['stage'] in BARRIERS and
                    (matches(e) or (e['stage'] == 'pre-clear' and e['compositor'] == key[3] and e['cascade'] == key[-1]))]
        gates = [e for e in events if e['stage'].startswith('shell-gate-')]
        assert gates and all(e['need'] == 1 for e in gates)
        returned = [e for e in events if e['stage'] == 'query-return-state' and e['role'] == 'none']
        assert len(returned) == 1
        observation = read(RUNTIME / 'progress-records' / group['record'])['observation']
        first_read = [r for r in group['reads'] if r['phase'] == 'first-child-read']
        assert len(first_read) == 1 and first_read[0]['return_text'] == query['exit']['decoded_value']
        stale = group['page'] in ('lh', 'rem') and group['mode'] != 'literal'
        middle_consumed = [e for e in events if e['stage'] == 'pre-remove-consumed' and e['role'] == 'middle']
        if stale:
            assert query['exit']['decoded_value'] == '0.428571' and observation['samples'][0]['opacity'] == 0.428571
            assert len(middle_consumed) == 1 and pending and middle_consumed[0]['seq'] < pending[0]['seq']
            assert not barriers and snapshots[-1]['state'] == 1
            assert all(e['servo'] == e['refresh'] == 1 and e['pre'] == 0 for e in pending)
            assert any(e['stage'] == 'post-deferred-traversal' for e in child_events)
            assert (returned[0]['root'], returned[0]['style'], returned[0]['throttle'], returned[0]['layout']) == ('0x0', 0, 0, 1)
        else:
            assert query['exit']['decoded_value'] == ('56px' if group['page'] == 'property' else '0.545455')
            assert snapshots[-1]['state'] == -1
            if pending:
                assert any(e['stage'] == 'pre-remove-consumed' and e['seq'] > pending[0]['seq'] for e in barriers)
        rows.append({'page': group['page'], 'mode': group['mode'], 'query': query['entry']['query'],
                     'child_full_key': dict(zip(KEY, key)), 'role_targets': group['role_targets'],
                     'sequence_interval': [events[0]['seq'], events[-1]['seq']], 'event_count': len(events),
                     'entry_child_state': snapshots[0]['state'], 'return_child_state': snapshots[-1]['state'],
                     'returned_text': query['exit']['decoded_value'], 'samples': observation['samples'],
                     'shell_gates': [{k: e[k] for k in ('seq', 'flush', 'need', 'style', 'throttle', 'layout', 'root')} for e in gates],
                     'return_flags': {k: returned[0][k] for k in ('seq', 'root', 'style', 'throttle', 'layout')},
                     'middle_consumed_sequences': [e['seq'] for e in middle_consumed],
                     'child_request_and_barrier_events': [{k: e[k] for k in (*KEY, 'seq', 'stage', 'state', 'request', 'servo', 'pre', 'refresh')}
                                                          for e in child_events if e['stage'].startswith(('request-', 'post-', 'pre-'))],
                     'child_barrier_sequences': [e['seq'] for e in barriers], 'stale_first': stale})
    assert sum(row['stale_first'] for row in rows) == 4
    print(json.dumps({'runtime_manifest_sha256': sha(RUNTIME / 'FILES.json'), 'strict_join_sha256': sha(JOIN),
                      'all_first_query_events_checked': True, 'groups': rows,
                      'native_causality_or_composition_proved': False}, indent=2))


if __name__ == '__main__':
    main()
