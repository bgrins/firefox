import copy
import json
import sys
from pathlib import Path
import trace

OUT = Path(__file__).resolve().parent


def event(stage, seq, **values):
    row = {name: -1 for name in trace.FIELDS if name not in trace.STRINGS}
    row.update({name: '0x0' for name in trace.POINTERS})
    row.update(v=1, pid=42, seq=seq, query=1, parent=0, window=300,
               document='0x100', target='0x200', compositor='0x300', shell='0x400',
               page='rem', role='child', mode='ordinary', pseudo=95,
               stage=stage, cascade=-1, state=-2, servo=0, pre=0, refresh=0,
               property=100, flags=0, count=0, value='-', valueLength=0,
               valueTruncated=0)
    row.update(values)
    return row


def encode(row):
    return trace.PREFIX + ' '.join(f'{name}={row[name]}' for name in trace.FIELDS)


def run(rows):
    return trace.analyze([encode(row) for row in rows])


def main():
    value = '0.428571'
    good = [event('query-enter', 1), event('snapshot-query-key', 2, cascade=0, state=1),
            event('shell-gate-type', 3, flush=3, animations=1, need=0, style=0, throttle=0, layout=0),
            event('query-exit', 4, value=value.encode().hex(), valueLength=len(value))]
    assert run(good)['closed_query_scopes']
    assert run(good)['queries'][0]['exit']['decoded_value'] == value
    nested = [event('query-enter', 1), event('query-enter', 2, query=2, parent=1),
              event('query-exit', 3, query=2, parent=1), event('query-exit', 4)]
    assert run(nested)['closed_query_scopes'] and len(run(nested)['queries'][1]['events']) == 4
    mozlog = [json.dumps({'action': 'process_output', 'data': encode(row)}) for row in good]
    assert trace.analyze(mozlog) == run(good)
    outside = [event('request-before', 1, query=0)]
    assert run(outside)['syntax_and_sequence_valid']
    negatives = []
    for field, value in [('seq', 7), ('state', 3), ('servo', -1), ('refresh', 2),
                         ('mode', 'guessed'), ('stage', 'composed'), ('window', -1),
                         ('query', 99), ('parent', 9), ('document', 'pointer'),
                         ('valueLength', 4), ('valueTruncated', 1), ('cascade', 2)]:
        bad = copy.deepcopy(good)
        bad[1][field] = value
        assert not run(bad)['syntax_and_sequence_valid'], field
        negatives.append(field)
    for line in [encode(good[0]) + ' seq=1', encode(good[0]).replace(' value=-', ''),
                 encode(good[0]).replace('v=1 ', 'v=2 ', 1)]:
        assert not trace.analyze([line])['syntax_and_sequence_valid']
        negatives.append('schema')
    assert not run(good[:-1])['closed_query_scopes']
    truncated = copy.deepcopy(good); truncated[1]['stage'] = 'snapshot-truncated'
    assert run(truncated)['syntax_and_sequence_valid'] and not run(truncated)['closed_query_scopes']
    missing_identity = copy.deepcopy(good)
    for row in missing_identity: row['window'] = 0
    assert not run(missing_identity)['closed_query_scopes']
    cap = f'{trace.PREFIX}v=1 pid=42 cap=limit seq=4'
    assert not trace.analyze([*[encode(row) for row in good], cap])['closed_query_scopes']
    after_cap = [*[encode(row) for row in good], cap, encode(event('request-before', 5, query=0))]
    assert not trace.analyze(after_cap)['syntax_and_sequence_valid']
    repeated = [*good, *[dict(row, seq=row['seq'] + 4) for row in good]]
    assert not run(repeated)['syntax_and_sequence_valid']
    changed_identity = copy.deepcopy(good); changed_identity[-1]['window'] = 301
    assert run(changed_identity)['syntax_and_sequence_valid'] and not run(changed_identity)['closed_query_scopes']
    result = {'positive_streams': 4, 'invalid_stream_negatives': len(negatives) + 2,
              'incomplete_or_ambiguous_streams': 5, 'native_trace_executed': False,
              'tests_preserve_separate_syntax_coverage_and_causality': True}
    if '--write' in sys.argv:
        (OUT / 'PARSER-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        assert result == json.loads((OUT / 'PARSER-CHECK.json').read_text())
    print(json.dumps(result))


if __name__ == '__main__':
    main()
