import hashlib


def definition(source, marker, trailing_semicolon=False):
    offset = 0
    while True:
        start = source.find(marker, offset)
        assert start >= 0, marker
        opening = source.find("{", start)
        semicolon = source.find(";", start)
        if semicolon != -1 and semicolon < opening:
            offset = start + len(marker)
            continue
        break
    index, depth, state = opening, 0, "code"
    while index < len(source):
        ch, pair = source[index], source[index:index+2]
        if state == "line":
            if ch == "\n": state = "code"
        elif state == "comment":
            if pair == "*/": state = "code"; index += 1
        elif state in ("string", "character"):
            if ch == "\\": index += 1
            elif ch == ('"' if state == "string" else "'"): state = "code"
        elif pair == "//": state = "line"; index += 1
        elif pair == "/*": state = "comment"; index += 1
        elif ch == '"': state = "string"
        elif ch == "'": state = "character"
        elif ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                if trailing_semicolon:
                    assert source[end:end+1] == ";"
                    end += 1
                return source[start:end]
        index += 1
    raise AssertionError(marker)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()
