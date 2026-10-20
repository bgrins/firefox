import re
def patch_text(original, patch, reverse=False):
    old = original.splitlines(keepends=True)
    out = []
    cursor = 0
    lines = patch.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
        if not match:
            i += 1
            continue
        a, ac, b, bc = [int(x) if x is not None else 1 for x in match.groups()]
        start, count, written = (b, bc, ac) if reverse else (a, ac, bc)
        pos = start - 1 if start else 0
        assert cursor <= pos <= len(old)
        out += old[cursor:pos]
        cursor = pos
        consumed = produced = 0
        i += 1
        while i < len(lines) and not lines[i].startswith(('@@ ', 'diff --git ')):
            line = lines[i]
            if line.startswith('\\'):
                raise AssertionError('unsupported no-newline marker')
            assert line[:1] in (' ', '+', '-')
            tag = line[0]
            if reverse:
                tag = {'+': '-', '-': '+', ' ': ' '}[tag]
            text = line[1:]
            if tag in (' ', '-'):
                assert cursor < len(old) and old[cursor] == text
                cursor += 1
                consumed += 1
            if tag in (' ', '+'):
                out.append(text)
                produced += 1
            i += 1
        assert (consumed, produced) == (count, written)
    out += old[cursor:]
    return ''.join(out)

