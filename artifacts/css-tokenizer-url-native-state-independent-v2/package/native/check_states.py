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

HEX = b'0123456789abcdefABCDEF'
NEWLINE = {10, 12, 13}
ARITY = {'enter': 4, 'exit': 6, 'token': 8, 'step': 9, 'slice': 6, 'bulk': 7}


def reference_trace(source):
    """Generate call-site observations from input alone; never read native rows."""
    data = source.encode('utf-8')
    size = len(data)
    position = 0
    events = []
    active = False

    def fields(at):
        return list(map(str, prefix_fields(source, at)))

    def step(operation, argument, length):
        nonlocal position
        before = position
        position += length
        assert 0 <= before < position <= size
        if active:
            events.append(['step', operation, str(argument), *fields(before), *fields(position)])

    def advance():
        step('advance', 1, 1)

    def newline():
        assert data[position] in NEWLINE
        step('newline', 0, 2 if data[position:position+2] == b'\r\n' else 1)

    def escape():
        if position == size:
            return '\ufffd'.encode()
        if data[position] in HEX:
            start = position
            for _ in range(6):
                if position == size or data[position] not in HEX:
                    break
                advance()
            scalar = int(data[start:position], 16)
            if position < size and data[position] in WS:
                if data[position] in NEWLINE:
                    newline()
                else:
                    advance()
            return chr(scalar if 0 < scalar <= 0x10ffff and not 0xd800 <= scalar <= 0xdfff else 0xfffd).encode()
        if data[position] == 0:
            advance()
            return '\ufffd'.encode()
        scalar = data[position:].decode()[0]
        step('character', ord(scalar), len(scalar.encode()))
        return scalar.encode()

    name = bytearray()
    while position < size:
        b = data[position]
        if b == 92 and (position+1 == size or data[position+1] not in NEWLINE):
            advance()
            name.extend(escape())
        elif b == 0 or b >= 128 or b in (45, 95) or 48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122:
            # This entry corpus begins with an identifier-like token. Name start
            # admission remains in the separately checked native/Lean caller.
            name.extend('\ufffd'.encode() if b == 0 else bytes([b]))
            position += 1
        else:
            break
    decoded_name = bytes(name)
    assert decoded_name, 'expected identifier-like first token in fixed corpus'
    function = position < size and data[position] == 40
    if function:
        position += 1
    if not function or decoded_name.lower() != b'url':
        state = prefix_fields(source, position)
        state[2] |= int(function)
        return [['token', *map(str, state), 'function' if function else 'ident', decoded_name.hex(), 'none', 'none']]

    active = True
    start = position
    events.append(['enter', *fields(start)])
    body = start
    while body < size and data[body] in WS:
        body += 1
    if body < size and data[body] in (34, 39):
        events.append(['exit', *fields(start), 'function', ''])
        state = prefix_fields(source, start)
        state[2] |= 1
        events.append(['token', *map(str, state), 'function', decoded_name.hex(), 'none', 'none'])
        return events

    marks = [i for i in range(start, body) if data[i] in (10, 12) or
             data[i] == 13 and data[i+1:i+2] != b'\n']
    position = body + int(body < size and data[body] == 41)
    before_bulk = [position, *prefix_fields(source, start)[1:]]
    events.append(['bulk', str(start), str(len(marks)), str(marks[-1]-start if marks else 0), *map(str, before_bulk)])

    def capture():
        value = data[body:position]
        value.decode('utf-8')
        events.append(['slice', str(body), *fields(position), value.hex()])
        return value

    def bad():
        while position < size:
            b = data[position]
            if b == 41:
                value = capture()
                advance()
                return 'bad-url', value
            if b == 92:
                advance()
                if position < size and data[position] in (41, 92):
                    advance()
            elif b in NEWLINE:
                newline()
            else:
                step('known', b, 1)
        return 'bad-url', capture()

    def end(value):
        while position < size:
            b = data[position]
            if b == 41:
                advance()
                break
            if b in (9, 32):
                advance()
            elif b in NEWLINE:
                newline()
            else:
                return bad()
        return 'url', value

    def content():
        owned = False
        value = bytearray()
        while position < size:
            b = data[position]
            if not owned and b in (0, 92):
                capture()
                owned = True
            if b in WS:
                if not owned:
                    capture()
                return end(bytes(value))
            if b == 41:
                if not owned:
                    capture()
                advance()
                return 'url', bytes(value)
            if b in (34, 39, 40, 127) or 1 <= b <= 8 or b == 11 or 14 <= b <= 31:
                advance()
                return bad()
            if b == 92:
                advance()
                if position < size and data[position] in NEWLINE:
                    return bad()
                value.extend(escape())
            elif b == 0:
                advance()
                value.extend('\ufffd'.encode())
            else:
                step('intro' if b >= 240 else 'continuation' if 128 <= b < 192 else 'advance',
                     0 if b >= 240 or 128 <= b < 192 else 1, 1)
                value.append(b)
        if not owned:
            capture()
        return 'url', bytes(value)

    kind, value = ('url', b'') if body == size or data[body] == 41 else content()
    events.append(['exit', *fields(position), kind, value.hex()])
    events.append(['token', *fields(position), kind, value.hex(), 'none', 'none'])
    return events


def expected_lines(cases):
    return ['|'.join([str(index), *event]) for index, case in enumerate(cases)
            for event in reference_trace(case['input'])]


def check(cases, raw):
    lines = raw.splitlines()
    for line in lines:
        parts = line.split('|')
        assert len(parts) >= 2, ('missing tag', line)
        assert parts[0].isascii() and parts[0].isdecimal() and str(int(parts[0])) == parts[0], ('row encoding', line)
        assert 0 <= int(parts[0]) < len(cases), ('row range', line)
        event = parts[1:]
        assert event[0] in ARITY, ('unknown tag', event[0])
        assert len(event) == ARITY[event[0]], ('arity', event[0], len(event))
    expected = expected_lines(cases)
    assert lines == expected, ('ordered input-derived trace mismatch',
        next(((i, a, b) for i, (a, b) in enumerate(zip(lines, expected)) if a != b),
             ('length', len(lines), len(expected))))
    totals = {'cases': len(cases), 'seams': 0, 'helpers': 0, 'slices': 0, 'bulk': 0}
    counts = {'enter': 'seams', 'step': 'helpers', 'slice': 'slices', 'bulk': 'bulk'}
    for line in expected:
        tag = line.split('|')[1]
        if tag in counts:
            totals[counts[tag]] += 1
    return {**totals, 'ordered_events': len(expected), 'complete_trace_equal': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check(json.loads(args.cases.read_text()), args.raw.read_text())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
