import hashlib
import re

STANDARD = {"propext", "Quot.sound", "Classical.choice"}
IDENT = r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
RECORD = re.compile(r"'(" + IDENT + r")' (?:does not depend on any axioms|depends on axioms: \[(" + IDENT + r"(?:, " + IDENT + r")*)\])")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def parse(raw):
    require(isinstance(raw, bytes), "byte input required")
    require(raw.endswith(b"\n") and b"\r" not in raw, "canonical final newline required")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError("non-ASCII audit text") from error
    records = []
    names = set()
    for line in text[:-1].split("\n"):
        match = RECORD.fullmatch(line)
        require(match is not None, "unparsed audit line")
        name = match[1]
        axes = match[2].split(", ") if match[2] else []
        require(name not in names, "duplicate declaration")
        require(len(set(axes)) == len(axes), "duplicate axiom")
        require(set(axes) <= STANDARD, "forbidden axiom")
        names.add(name)
        records.append([name, axes])
    return records


def validate(raw, expected):
    actual = parse(raw)
    require(actual == expected, "exact ordered audit mismatch")
    return actual


def validate_types(raw, expected_sha256):
    require(hashlib.sha256(raw).hexdigest() == expected_sha256, "printed type bytes changed")


def validate_warning(raw, expected):
    require(raw == expected, "exact four warning blocks changed")
