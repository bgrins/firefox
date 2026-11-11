import argparse
import json
from pathlib import Path

PHASES = ['cold', 'cached', 'suffix', 'reparsed', 'suffix-replay']


def boolean(value):
    if value not in ('true', 'false'):
        raise ValueError('Not a Boolean')
    return value == 'true'


def public_rows(text):
    result = {}
    for line in text.splitlines():
        f = line.split('\t')
        if len(f) != 14 or f[0] != 'PUBLIC':
            raise ValueError('Bad public record')
        key = (f[1], f[2])
        if key in result:
            raise ValueError('Duplicate public record')
        result[key] = dict(start=int(f[3]), end=int(f[4]), kind=f[5], unit=bytes.fromhex(f[6]),
            has_sign=boolean(f[7]), is_integer=boolean(f[8]), float_bits=f[9],
            remaining=bytes.fromhex(f[10]), debug=bytes.fromhex(f[11]), line=int(f[12]), column=int(f[13]))
        if len(f[9]) != 8 or any(c not in '0123456789abcdef' for c in f[9]):
            raise ValueError('Bad payload bits')
    return result


def trace_rows(text):
    result = {}
    current = None
    for line in text.splitlines():
        f = line.split('\t')
        if f[0] == 'CALL' and len(f) == 3:
            if current is not None or (f[1], f[2]) in result:
                raise ValueError('Duplicate or nested call')
            current = (f[1], f[2])
            result[current] = []
        elif f[0] == 'END' and len(f) == 3:
            if current != (f[1], f[2]):
                raise ValueError('Unmatched end')
            current = None
        elif f[0] == 'TRACE' and len(f) == 16 and current is not None:
            result[current].append(dict(positions=[int(x) for x in f[1:9]],
                slices=[bytes.fromhex(x) for x in f[9:14]], has_sign=boolean(f[14]), is_integer=boolean(f[15])))
        else:
            raise ValueError('Unexpected trace output')
    if current is not None:
        raise ValueError('Unclosed call')
    return result


def core_observation(case, public, trace):
    source = (case['prefix'] + case['tail']).encode()
    start, end, i0, i1, f0, f1, e0, e1 = trace['positions']
    if not (start == public['start'] and start <= i0 <= i1 <= f0 <= f1 <= e0 <= e1 == end <= public['end'] <= len(source)):
        raise ValueError('Invalid core positions')
    expected = [source[start:end], source[end:], source[i0:i1], source[f0:f1], source[e0:e1]]
    if trace['slices'] != expected or any(any(not 48 <= b <= 57 for b in run) for run in expected[2:]):
        raise ValueError('Slice/source mismatch')
    if trace['has_sign'] != public['has_sign'] or trace['is_integer'] != public['is_integer']:
        raise ValueError('Public/core classification mismatch')
    return [list(value) for value in expected] + [trace['has_sign'], trace['is_integer']]


def compare(cases, plain, instrumented, plain_trace, trace, model):
    if plain != instrumented:
        raise ValueError('Instrumentation changed public observation')
    expected_keys = {(c['id'], phase) for c in cases for phase in (PHASES if c['mode'] == 'history' else ['cold'])}
    if set(plain) != expected_keys or set(trace) != expected_keys or set(plain_trace) != expected_keys:
        raise ValueError('Missing or extra case/phase')
    if any(plain_trace.values()):
        raise ValueError('Trace present in uninstrumented source')
    admitted = [c for c in cases if c['bridge_eligible']]
    if len(model) != len(admitted):
        raise ValueError('Wrong model row count')
    models = {}
    for c, row in zip(admitted, model):
        if len(row) != 4 or row[0] != c['tail'] or row[1] is not False or row[3] is not False or len(row[2]) != 7:
            raise ValueError('Bad model row/domain/state')
        models[c['id']] = row[2]
    comparisons = []
    for c in cases:
        source = (c['prefix'] + c['tail']).encode()
        phases = PHASES if c['mode'] == 'history' else ['cold']
        first = plain[(c['id'], 'cold')]
        if first['start'] != c['prefix_utf8_bytes'] or first['kind'] not in ('number', 'percentage', 'dimension'):
            raise ValueError('Wrong numeric boundary')
        for phase in phases:
            key = (c['id'], phase)
            public = plain[key]
            if public['remaining'] != source[public['end']:] or not public['start'] < public['end'] <= len(source):
                raise ValueError('Wrong full-token position/remainder')
            expected_count = 0 if phase == 'cached' or public['kind'] == 'other' else 1
            if len(trace[key]) != expected_count:
                raise ValueError('Wrong tokenizer invocation count')
            if trace[key]:
                observation = core_observation(c, public, trace[key][0])
                if phase in ('cold', 'reparsed') and c['bridge_eligible']:
                    if observation != models[c['id']]:
                        raise ValueError('Native/JSON lexical mismatch: ' + str(key))
                    comparisons.append(key)
        if c['mode'] == 'history':
            if first != plain[(c['id'], 'cached')] or first != plain[(c['id'], 'reparsed')]:
                raise ValueError('Reset changed numeric token/state')
            suffix = plain[(c['id'], 'suffix')]
            if suffix['start'] != first['end'] or suffix != plain[(c['id'], 'suffix-replay')]:
                raise ValueError('Reset changed following token/state')
    return dict(cases=len(cases), public_rows=len(plain), admitted_json_cases=len(admitted),
        lexical_comparisons=len(comparisons), excluded_legacy_cases=len(cases)-len(admitted),
        float_comparison_to_exact_model=False, native_refinement_proved=False)


def main():
    p = argparse.ArgumentParser()
    for name in ['cases', 'plain', 'instrumented', 'plain-trace', 'trace', 'model', 'out']:
        p.add_argument('--' + name, required=True, type=Path)
    a = p.parse_args()
    result = compare(json.loads(a.cases.read_text()), public_rows(a.plain.read_text()),
        public_rows(a.instrumented.read_text()), trace_rows(a.plain_trace.read_text()),
        trace_rows(a.trace.read_text()), [json.loads(line) for line in a.model.read_text().splitlines()])
    a.out.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
