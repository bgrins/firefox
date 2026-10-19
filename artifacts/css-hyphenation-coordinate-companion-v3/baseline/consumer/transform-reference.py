import re


def reference(units, mode, incoming):
    text = ''.join(map(chr, units))
    shy = 173 in units
    flags = 2 if shy else 0
    if mode in (0, 3):
        keep = [c != 173 for c in units]
        out = [32 if mode == 3 and c in (9, 10) else c for c in units if c != 173]
        if mode == 0:
            flags |= int(9 in units) | (4 if 10 in units else 0)
        return out, keep, incoming & ~3, flags
    keep = [False] * len(units)
    out = []
    whitespace = bool(incoming & 1)
    for span in re.finditer(r'[ \t\n][ \t\n\xad]*|[^ \t\n]', text):
        contents = span.group()
        indices = list(range(span.start(), span.end()))
        if contents[0] not in ' \t\n':
            if contents != '\xad':
                out.append(ord(contents))
                keep[span.start()] = True
            whitespace = False
            continue
        newlines = [i for i in indices if units[i] == 10]
        selected = newlines if newlines and mode == 1 else ([] if whitespace else [newlines[0] if newlines else indices[0]])
        for i in selected:
            keep[i] = True
            out.append(10 if newlines and mode == 1 else 32)
        whitespace = not (newlines and mode == 1)
    return out, keep, (incoming & ~3) | int(whitespace), flags
