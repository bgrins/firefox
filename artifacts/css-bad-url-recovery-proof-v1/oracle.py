HEX = frozenset("0123456789abcdefABCDEF")
WHITESPACE = frozenset(" \t\n")


def point(text, index):
    char = text[index]
    finish = index + 1
    if char == "\r":
        if finish < len(text) and text[finish] == "\n":
            finish += 1
        return "\n", finish
    if char == "\f":
        return "\n", finish
    if char == "\0":
        return "\ufffd", finish
    return char, finish


def escape(text, index):
    if index == len(text):
        return "\ufffd", index
    char, finish = point(text, index)
    if char not in HEX:
        return char, finish
    digits = char
    index = finish
    while len(digits) < 6 and index < len(text):
        char, finish = point(text, index)
        if char not in HEX:
            break
        digits += char
        index = finish
    if index < len(text):
        char, finish = point(text, index)
        if char in WHITESPACE:
            index = finish
    value = int(digits, 16)
    return ("\ufffd" if value == 0 or value > 0x10FFFF or 0xD800 <= value <= 0xDFFF else chr(value)), index


def remnants(text, index):
    while index < len(text):
        start = index
        char, index = point(text, index)
        if char == ")":
            return index, start
        if char == "\\" and (index == len(text) or point(text, index)[0] != "\n"):
            _, index = escape(text, index)
    return index, index


def location(text):
    line, column, index = 0, 1, 0
    while index < len(text):
        char, index = point(text, index)
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 2 if ord(char) > 0xFFFF else 1
    return line, column


def first_url(text):
    assert text.startswith("url(")
    index = 4
    while index < len(text):
        char, finish = point(text, index)
        if char not in WHITESPACE:
            break
        index = finish
    payload_start = index
    value = []
    kind = "url"
    while index < len(text):
        char, finish = point(text, index)
        if char == ")":
            index = finish
            break
        if char in WHITESPACE:
            index = finish
            while index < len(text) and point(text, index)[0] in WHITESPACE:
                _, index = point(text, index)
            if index == len(text):
                break
            if point(text, index)[0] == ")":
                _, index = point(text, index)
                break
            kind = "bad-url"
            index, payload_end = remnants(text, index)
            break
        if char in "\"'(" or 1 <= ord(char) <= 8 or ord(char) in (11, 127) or 14 <= ord(char) <= 31:
            kind = "bad-url"
            index, payload_end = remnants(text, finish)
            break
        if char == "\\":
            if finish < len(text) and point(text, finish)[0] == "\n":
                kind = "bad-url"
                index, payload_end = remnants(text, finish)
                break
            decoded, index = escape(text, finish)
            value.append(decoded)
        else:
            value.append(char)
            index = finish
    payload = text[payload_start:payload_end] if kind == "bad-url" else "".join(value)
    line, column = location(text[:index])
    return {"kind": kind, "payload": payload, "suffix": text[index:], "position": len(text[:index].encode("utf-8")), "line": line, "column": column}
