"""Independent source-prefix and operation checks; no native state as oracle."""
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, json

MODULUS = 1 << 32
WS = {9, 10, 12, 13, 32}

def prefix_fields(source, end):
    encoded = source.encode('utf-8')
    assert 0 <= end <= len(encoded)
    offset = 0
    line = 0
    column = 1
    previous_cr = False
    for scalar in source:
        width = len(scalar.encode('utf-8'))
        if offset >= end:
            break
        if scalar == '\r':
            line += 1
            column = 1
        elif scalar == '\n':
            if not previous_cr:
                line += 1
                column = 1
        elif scalar == '\f':
            line += 1
            column = 1
        else:
            column += 2 if ord(scalar) > 0xffff else 1
        previous_cr = scalar == '\r'
        offset += width
    return [end, (end + 1 - column) % MODULUS, line * 4]

def check(cases, raw):
    rows = [[] for _ in cases]
    for line in raw.splitlines():
        parts = line.split('|')
        row = int(parts[0])
        assert 0 <= row < len(rows)
        rows[row].append(parts[1:])
    totals = {'cases': len(cases), 'seams': 0, 'helpers': 0, 'slices': 0, 'bulk': 0}
    for index, (case, events) in enumerate(zip(cases, rows)):
        source = case['input']
        data = source.encode('utf-8')
        enters = [e for e in events if e[0] == 'enter']
        exits = [e for e in events if e[0] == 'exit']
        tokens = [e for e in events if e[0] == 'token']
        assert len(tokens) == 1, (index, 'token cardinality')
        token = tokens[0]
        assert token[-2:] == ['none', 'none'], (index, 'Option annotation presence')
        assert len(enters) == len(exits) <= 1, (index, 'seam cardinality')
        if not enters:
            assert len(events) == 1, (index, 'events without URL call')
            continue
        totals['seams'] += 1
        entry = list(map(int, enters[0][1:4]))
        assert entry == prefix_fields(source, entry[0]), (index, 'entry fields')
        assert data[entry[0]-1] == 40
        start = entry[0]
        body = start
        while body < len(data) and data[body] in WS:
            body += 1
        exit_event = exits[0]
        exit_fields = list(map(int, exit_event[1:4]))
        assert exit_fields == prefix_fields(source, exit_fields[0]), (index, 'exit fields')
        if exit_event[4] == 'function':
            assert body < len(data) and data[body] in (34, 39)
            assert exit_fields == entry
            assert [e[0] for e in events] == ['enter', 'exit', 'token']
            assert list(map(int, token[1:4])) == [*entry[:2], entry[2] | 1]
        else:
            assert list(map(int, token[1:4])) == exit_fields
            assert token[4:6] == exit_event[4:6]
        for event in events:
            tag = event[0]
            if tag == 'step':
                totals['helpers'] += 1
                operation, argument = event[1], int(event[2])
                before, after = list(map(int, event[3:6])), list(map(int, event[6:9]))
                assert before == prefix_fields(source, before[0]), (index, operation, 'before', before)
                assert after == prefix_fields(source, after[0]), (index, operation, 'after', after)
                assert start <= before[0] < after[0] <= exit_fields[0]
                cursor, line_start, packed = before
                if operation == 'advance':
                    assert after == [cursor + argument, line_start, packed]
                elif operation in ('intro', 'continuation', 'known'):
                    byte = data[cursor]
                    if operation == 'intro':
                        assert 240 <= byte
                    elif operation == 'continuation':
                        assert 128 <= byte < 192
                    else:
                        assert argument == byte
                    delta = -1 if byte >= 240 else 1 if 128 <= byte < 192 else 0
                    assert after == [cursor + 1, (line_start + delta) % MODULUS, packed]
                elif operation == 'newline':
                    assert data[cursor] in (10, 12, 13)
                    length = 2 if data[cursor:cursor+2] == b'\r\n' else 1
                    assert after == [cursor + length, (cursor + length) % MODULUS, packed + 4]
                elif operation == 'character':
                    scalar = data[cursor:].decode('utf-8')[0]
                    assert argument == ord(scalar)
                    width = len(scalar.encode('utf-8'))
                    units = 2 if ord(scalar) > 0xffff else 1
                    assert after == [cursor + width, (line_start + width - units) % MODULUS, packed]
                else:
                    raise AssertionError((index, 'unrecognized helper', operation))
            elif tag == 'slice':
                totals['slices'] += 1
                slice_start = int(event[1])
                state = list(map(int, event[2:5]))
                assert slice_start == body, (index, 'preserved original body start')
                assert body <= state[0] <= exit_fields[0]
                assert state == prefix_fields(source, state[0])
                assert bytes.fromhex(event[5]) == data[slice_start:state[0]]
                data[slice_start:state[0]].decode('utf-8')
            elif tag == 'bulk':
                totals['bulk'] += 1
                native_start, count, last = map(int, event[1:4])
                moved = list(map(int, event[4:7]))
                assert native_start == start
                marks = [i for i, b in enumerate(data[start:body])
                         if b in (10, 12) or b == 13 and data[start+i+1:start+i+2] != b'\n']
                assert count == len(marks) and last == (marks[-1] if marks else 0)
                close = int(body < len(data) and data[body] == 41)
                assert moved == [body + close, entry[1], entry[2]]
        if exit_event[4] == 'bad-url':
            slices = [e for e in events if e[0] == 'slice']
            assert slices and slices[-1][5] == exit_event[5]
            end = int(slices[-1][2])
            assert end == exit_fields[0] or end + 1 == exit_fields[0]
            if end < exit_fields[0]:
                assert data[end] == 41
            else:
                assert end == len(data)
    return totals

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check(json.loads(args.cases.read_text()), args.raw.read_text())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
