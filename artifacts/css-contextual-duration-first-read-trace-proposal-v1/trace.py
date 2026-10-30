import argparse
import json
from pathlib import Path
import re

PREFIX = 'DURATION_FIRST_READ_TRACE '
FIELDS = 'v pid seq query parent window document page target role mode pseudo identifier compositor shell stage cascade state request servo pre refresh root traversal flags property flush animations need style throttle layout source count value valueLength valueTruncated'.split()
POINTERS = {'document', 'target', 'identifier', 'compositor', 'shell', 'root', 'traversal', 'source'}
STRINGS = POINTERS | {'page', 'role', 'mode', 'stage', 'value'}
STAGES = set('query-enter query-exit query-entry-state query-return-state snapshot-query-key snapshot-entry snapshot-end snapshot-truncated sources-enter sources-complete sources-no-document sources-disconnected sources-empty sources-no-shell sources-cached sources-unresolved style-needed style-not-needed flush-enter flush-exit shell-gate-type shell-gate-changes request-before request-state request-after post-enter post-no-element post-deferred-traversal post-deferred-refresh post-attempt forced-inspect pre-skip-throttled pre-skip-no-shell pre-skip-subtree pre-selected pre-remove-wrong-document pre-remove-no-effects pre-post-hint pre-will-compose pre-remove-consumed pre-clear'.split())


def parse_line(line):
    assert line.startswith(PREFIX)
    pairs = [part.split('=', 1) for part in line[len(PREFIX):].split()]
    assert all(len(pair) == 2 for pair in pairs), 'malformed field'
    assert len({pair[0] for pair in pairs}) == len(pairs), 'duplicate field'
    record = dict(pairs)
    if 'cap' in record:
        assert set(record) == {'v', 'pid', 'cap', 'seq'}
        assert record['v'] == '1' and record['cap'] in {'limit', 'bytes'}
        assert re.fullmatch(r'[1-9][0-9]*', record['pid'])
        assert re.fullmatch(r'0|[1-9][0-9]*', record['seq'])
        return {**record, 'pid': int(record['pid']), 'seq': int(record['seq'])}
    assert set(record) == set(FIELDS), 'field set'
    for name in set(FIELDS) - STRINGS:
        assert re.fullmatch(r'-?(0|[1-9][0-9]*)', record[name]), name
        record[name] = int(record[name])
    assert record['v'] == 1 and record['pid'] > 0 and 1 <= record['seq'] <= 16384
    for name in ['query', 'parent', 'window']:
        assert 0 <= record[name] < 2**64, name
    for name in POINTERS:
        assert re.fullmatch(r'0x[0-9a-fA-F]+|\(nil\)', record[name]), name
        record[name] = '0x0' if record[name] == '(nil)' else hex(int(record[name], 16))
    assert record['page'] in {'rem', 'lh', 'property'}
    assert record['role'] in {'none', 'root', 'parent', 'middle', 'child', 'other'}
    assert record['mode'] in {'unknown', 'literal', 'ordinary', 'animated'}
    assert record['stage'] in STAGES
    assert record['cascade'] in {-1, 0, 1}
    assert record['state'] in {-2, -1, 0, 1, 2}
    assert record['request'] in {-1, 0, 1, 2}
    assert record['servo'] in {0, 1}
    for name in ['pre', 'refresh', 'animations', 'need', 'style', 'throttle', 'layout']:
        assert record[name] in {-1, 0, 1}, name
    assert -1 <= record['pseudo'] <= 65535 and -1 <= record['property'] <= 65535
    assert -1 <= record['flush'] <= 32 and 0 <= record['flags'] < 2**32
    assert 0 <= record['count'] <= 65 and 0 <= record['valueLength'] < 2**32
    assert record['valueTruncated'] in {0, 1}
    value = record['value']
    assert value == '-' or re.fullmatch(r'(?:[0-9a-f]{2})+', value)
    encoded = b'' if value == '-' else bytes.fromhex(value)
    assert len(encoded) == min(record['valueLength'], 128)
    assert record['valueTruncated'] == int(record['valueLength'] > 128)
    if record['stage'] != 'query-exit':
        assert not encoded and record['valueLength'] == 0
    record['decoded_value'] = encoded.decode('utf-8', errors='replace')
    if record['stage'].startswith('shell-gate-'):
        assert record['need'] in {0, 1} and record['flush'] >= 0
    if record['stage'] in {'snapshot-query-key', 'snapshot-entry'}:
        assert record['cascade'] >= 0 and record['state'] >= -1
    return record


def trace_lines(lines):
    for line in lines:
        parts = [line.rstrip('\n')]
        if line.lstrip().startswith('{'):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                if PREFIX in line:
                    yield PREFIX + 'malformed_mozlog=1'
                continue
            if item.get('action') != 'process_output' or not isinstance(item.get('data'), str):
                continue
            parts = item['data'].splitlines()
        for part in parts:
            if PREFIX not in part:
                continue
            yield part[part.index(PREFIX):]


def key(event):
    return tuple(event[name] for name in ['pid', 'window', 'document', 'compositor', 'target', 'pseudo', 'identifier', 'cascade'])


def analyze(lines):
    events, caps, errors, limitations, queries = [], [], [], [], []
    sequences, sizes, stacks, active = {}, {}, {}, {}
    capped = set()
    seen_queries = set()
    for number, line in enumerate(trace_lines(lines), 1):
        try:
            event = parse_line(line)
            pid = event['pid']
            assert pid not in capped, 'record after cap'
            if 'cap' in event:
                assert event['seq'] == sequences.get(pid, 0), 'cap sequence'
                capped.add(pid)
                caps.append(event)
                continue
            assert event['seq'] == sequences.get(pid, 0) + 1, 'sequence gap or duplicate'
            sequences[pid] = event['seq']
            sizes[pid] = sizes.get(pid, 0) + len(line.encode()) + 1
            assert sizes[pid] <= 4 * 1024 * 1024, 'producer byte bound exceeded'
            stack = stacks.setdefault(pid, [])
            if event['stage'] == 'query-enter':
                assert event['query'] > 0 and event['parent'] == (stack[-1] if stack else 0)
                assert (pid, event['query']) not in seen_queries, 'duplicate query'
                seen_queries.add((pid, event['query']))
                stack.append(event['query'])
                active[pid, event['query']] = {'entry': event, 'events': []}
            assert event['query'] == (stack[-1] if stack else 0), 'query nesting'
            assert event['parent'] == (active[pid, event['query']]['entry']['parent'] if stack else 0), 'query parent'
            for query in stack:
                active[pid, query]['events'].append(event)
            if event['stage'] == 'query-exit':
                item = active.pop((pid, event['query']))
                item['exit'] = event
                queries.append(item)
                stack.pop()
                if any(item['entry'][name] != event[name] for name in ['window', 'document', 'target', 'pseudo', 'identifier', 'property']):
                    limitations.append({'query': event['query'], 'pid': pid, 'reason': 'query identity/property changed'})
            if event['window'] == 0 or event['stage'] == 'snapshot-truncated' or event['valueTruncated']:
                limitations.append({'pid': pid, 'seq': event['seq'], 'reason': 'missing identity or truncated capture'})
            events.append(event)
        except (AssertionError, ValueError, KeyError) as error:
            errors.append({'trace_line': number, 'error': str(error)})
    for (pid, query), item in active.items():
        limitations.append({'pid': pid, 'query': query, 'reason': 'unclosed query'})
    return {'syntax_and_sequence_valid': not errors, 'closed_query_scopes': bool(queries) and not (errors or caps or limitations),
            'errors': errors, 'caps': caps, 'limitations': limitations, 'events': events,
            'queries': queries, 'event_count': len(events), 'query_count': len(queries),
            'first_read_phase_alignment_established': False, 'semantic_query_coverage_verified': False,
            'native_causality_or_composition_proved': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    with args.input.open() as stream:
        result = analyze(stream)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['syntax_and_sequence_valid'] else 1)


if __name__ == '__main__':
    main()
