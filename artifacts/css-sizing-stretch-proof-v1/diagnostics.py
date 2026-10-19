import re


def negative(source, path, code, stdout, stderr, expected):
    if code != 1 or stderr:
        raise RuntimeError('Wrong negative terminal')
    lines = source.splitlines()
    decls = [(i, line) for i, line in enumerate(lines, 1) if re.match(r'^(theorem |def |instance |structure |#print|end )', line)]
    spans = {}
    for j, (start, line) in enumerate(decls[:-1]):
        if line.startswith('theorem '):
            end = decls[j + 1][0]
            bodies = [i for i in range(start, end) if ':= by' in lines[i - 1]]
            if not bodies:
                raise RuntimeError('Ambiguous proof body')
            spans[line.split()[1]] = (bodies[0], end)
    headers = re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$', stdout, re.M)
    if len(re.findall(r'\berror(?:\([^\n)]*\))?:', stdout)) != len(headers):
        raise RuntimeError('Unlocated diagnostic')
    found = []
    for filename, line, message in headers:
        owners = [n for n, (a, b) in spans.items() if a <= int(line) < b]
        if filename != str(path) or len(owners) != 1:
            raise RuntimeError('Foreign diagnostic')
        found.append((owners[0], message))
    if found != expected:
        raise RuntimeError('Wrong failing theorem inventory: ' + repr(found))
    return found

