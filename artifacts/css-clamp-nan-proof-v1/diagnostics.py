import re


def errors(source, path, output):
    lines = source.splitlines()
    declarations = [(i, line) for i, line in enumerate(lines, 1)
                    if re.match(r"^(theorem|def|structure|inductive|end|#print) ", line)]
    found = []
    headers = re.findall(r"^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$", output, re.M)
    if len(re.findall(r"\berror(?:\([^\n)]*\))?:", output)) != len(headers):
        raise ValueError("Unlocated compiler diagnostic")
    for filename, line, message in headers:
        if filename != str(path):
            raise ValueError("Foreign diagnostic")
        owner = max(i for i, (start, _) in enumerate(declarations) if start <= int(line))
        start, text = declarations[owner]
        if not text.startswith("theorem "):
            raise ValueError("Diagnostic outside theorem")
        end = declarations[owner + 1][0]
        body = [i for i in range(start, end) if ":= by" in lines[i - 1]]
        if not body or int(line) < body[0]:
            raise ValueError("Diagnostic outside proof body")
        found.append([text.split()[1], message])
    return found
