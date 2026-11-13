import re


def records(text, names):
    result = {}
    for block in text.split("*** Dumping AST Record Layout\n")[1:]:
        head = re.match(r"\s*0 \| (?:struct|class) (.+)\n", block)
        footer = re.search(r"\[sizeof=(\d+), dsize=\d+, align=(\d+),", block)
        if head and footer:
            name = head.group(1)
            if name not in names:
                continue
            value = dict(size=int(footer.group(1)), align=int(footer.group(2)), record=block)
            if name in result:
                assert result[name] == value, name
            result[name] = value
    return result


def extract(text, types):
    parsed = records(text, set(types.values()) | {"GridBundleAbiFacts"})
    facts = parsed["GridBundleAbiFacts"]["record"]
    values = {}
    for key, name in types.items():
        record = parsed[name]
        for metric in ("size", "align"):
            matches = re.findall(r"char\[(\d+)\] " + key + "_" + metric + r"\n", facts)
            assert len(matches) == 1, (key, metric, matches)
            assert int(matches[0]) == record[metric], (key, metric)
        values[key] = record
    return values
