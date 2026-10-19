import itertools


def fixtures():
    result = []
    seen = set()

    def add(family, text):
        if text not in seen:
            seen.add(text)
            result.append({"family": family, "input": text})

    prefixes = ["a", "\\_a", "a\0", "é", "😀", "\\61", "a\\000061", "aé\\_"]
    spaces = [" ", "\t", "\n", "\r", "\r\n", "\f", " \r\n\t"]
    suffixes = [")tail", "", "plain", "é)tail", "😀)tail", "\0)tail", "(x)tail", "'x)tail", '"x)tail']
    suffixes += ["\\" * count + ")inside)tail" for count in range(1, 9)]
    suffixes += ["\\" + newline + ")tail" for newline in ["\n", "\r", "\r\n", "\f"]]
    suffixes += ["\\" + digits + ending for digits in ["0", "29", "5c", "000029", "1234567", "d800", "110000", "ffffff", "10ffff"] for ending in [")tail", " )tail", "\r\n)tail", ""]]
    for prefix, space, suffix in itertools.product(prefixes, spaces, suffixes):
        add("whitespace-handoff", "url(" + prefix + space + suffix)
    for initial in spaces:
        for prefix in prefixes:
            for end in [")tail", "", " )tail"]:
                add("leading-whitespace", "url(" + initial + prefix + end)
    for prefix in prefixes:
        for trigger in ['"', "'", "(", "\x01", "\x0b", "\x7f"]:
            for suffix in suffixes:
                add("other-bad-url-entry", "url(" + prefix + trigger + suffix)
        for suffix in suffixes:
            add("url-value", "url(" + prefix + suffix)
    for n in range(4):
        for chars in itertools.product(["\\", ")", "a", "2", " ", "\n", "é", "😀"], repeat=n):
            add("recovery-alphabet", "url(a " + "".join(chars) + ")tail")
    return result
