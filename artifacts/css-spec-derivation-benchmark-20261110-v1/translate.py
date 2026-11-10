import argparse
import hashlib
import html
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
SLOTS = ("first", "second", "third")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def plain(markup):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", markup)).split())


def span(source, start, end):
    return [len(source[:start].encode()), len(source[:end].encode())]


def section(source, anchor):
    headings = list(re.finditer(r'<h([2-6])\s+id=[\'"]([^\'"]+)[\'"]\s*>', source))
    matches = [m for m in headings if m[2] == anchor]
    if len(matches) != 1:
        raise ValueError("Expected exactly one algorithm heading")
    start = matches[0]
    end = next(m.start() for m in headings if m.start() > start.start() and int(m[1]) <= int(start[1]))
    body = source.index(f"</h{start[1]}>", start.end()) + len(f"</h{start[1]}>")
    return start.start(), body, end


def definitions(source):
    newline = re.search(r'<dt><dfn export>newline</dfn>\s*<dd>\s*U\+([0-9A-F]{4,6}) ([A-Z ]+)\.', source)
    digit = re.search(r'<dt><dfn export>digit</dfn>\s*<dd>\s*A <a>code point</a> between U\+([0-9A-F]{4,6}) [A-Z ]+ \(.\) and U\+([0-9A-F]{4,6}) [A-Z ]+ \(.\) inclusive\.', source)
    if not newline or not digit:
        raise ValueError("Unsupported referenced character definition")
    return {
        "newline": {"kind": "eq", "value": int(newline[1], 16), "source_bytes": span(source, *newline.span())},
        "digit": {"kind": "range", "low": int(digit[1], 16), "high": int(digit[2], 16), "source_bytes": span(source, *digit.span())},
    }


def atom(value, terms):
    match = re.fullmatch(r"the (first|second|third) code point is (not )?(?:a )?(.+)", value)
    if not match:
        raise ValueError("Unsupported condition: " + value)
    slot, negate, target = match.groups()
    literal = re.fullmatch(r"U\+([0-9A-F]{4,6}) [A-Z -]+ \(.\)", target)
    if literal:
        node = {"kind": "eq", "value": int(literal[1], 16)}
    elif target in terms:
        node = {k: v for k, v in terms[target].items() if k != "source_bytes"}
        node["resolved_term"] = target
    else:
        raise ValueError("Unsupported character class: " + target)
    return dict(node, slot=slot, negate=bool(negate))


def sequence(value, terms):
    nodes = []
    while value:
        conditional = re.match(r"(?:If|Otherwise, if) (.+?), return (true|false)\.\s*", value)
        terminal = re.fullmatch(r"(?:Return|Otherwise, return) (true|false)\.", value)
        if conditional:
            condition = {"kind": "and", "args": [atom(x, terms) for x in conditional[1].split(" and ")]}
            nodes.append({"condition": condition, "return": conditional[2] == "true"})
            value = value[conditional.end():]
        elif terminal:
            nodes.append({"condition": None, "return": terminal[1] == "true"})
            value = ""
        else:
            raise ValueError("Unsupported statement: " + value)
    if not nodes or nodes[-1]["condition"] is not None:
        raise ValueError("Missing terminal return")
    return {"kind": "sequence", "nodes": nodes}


def selection(markup, terms):
    matched = re.fullmatch(r"\s*<dl>\s*(.*?)\s*</dl>\s*", markup, re.S)
    if not matched:
        raise ValueError("Unsupported selection markup")
    content = matched[1]
    tokens = list(re.finditer(r"<(dt|dd)>", content))
    if not tokens or content[:tokens[0].start()].strip():
        raise ValueError("Unsupported selection prefix")
    cases, labels = [], []
    for i, token in enumerate(tokens):
        stop = tokens[i + 1].start() if i + 1 < len(tokens) else len(content)
        value = plain(content[token.end():stop])
        if token[1] == "dt":
            if value == "anything else":
                labels.append(None)
            else:
                labels.append(atom("the first code point is " + value, terms))
        else:
            if not labels or (None in labels and labels != [None]):
                raise ValueError("Unsupported or absent selection labels")
            cases.append({"condition": None if labels == [None] else {"kind": "or", "args": labels}, "body": sequence(value, terms)})
            labels = []
    if labels or not cases or [c["condition"] is None for c in cases] != [False] * (len(cases) - 1) + [True]:
        raise ValueError("Selection needs exactly one final default")
    return {"kind": "selection", "cases": cases}


def extract(source, anchor):
    start, body, end = section(source, anchor)
    raw = source[body:end]
    paras = list(re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", raw, re.S))
    if len(paras) < 3:
        raise ValueError("Unsupported paragraph inventory")
    intro, note = plain(paras[0][0]), plain(paras[1][0])
    if not intro.startswith("This section describes how to "):
        raise ValueError("Unsupported algorithm introduction")
    if not re.fullmatch(r"Note: This algorithm will not consume any additional code points?\.", note):
        raise ValueError("Unsupported input effect: expected a non-consumption note; observed " + note)
    terms = definitions(source)
    remaining = raw[paras[2].start():].strip()
    if remaining.startswith("Look at the first <a>code point</a>:"):
        tree = selection(remaining.removeprefix("Look at the first <a>code point</a>:"), terms)
    else:
        tree = sequence(plain(remaining), terms)
    return {
        "anchor": anchor,
        "source_bytes": span(source, start, end),
        "introduction": {"text": intro, "translated": False, "source_bytes": span(source, body + paras[0].start(), body + paras[0].end())},
        "effect": {"kind": "preserve-supplied-list", "text": note, "source_bytes": span(source, body + paras[1].start(), body + paras[1].end())},
        "body_source_bytes": span(source, body + paras[2].start(), end),
        "definitions": terms,
        "tree": tree,
    }


def condition(node):
    kind = node["kind"]
    if kind in ("and", "or"):
        return "(" + (" && " if kind == "and" else " || ").join(condition(x) for x in node["args"]) + ")"
    slot = node["slot"]
    if kind == "eq":
        result = f"({slot} == some (Char.ofNat {node['value']}))"
    elif kind == "range":
        result = f"({slot}.any (fun c => Char.ofNat {node['low']} ≤ c && c ≤ Char.ofNat {node['high']}))"
    else:
        raise ValueError("Unknown condition kind")
    return f"(!{result})" if node["negate"] else result


def expression(tree):
    if tree["kind"] == "sequence":
        result = str(tree["nodes"][-1]["return"]).lower()
        for node in reversed(tree["nodes"][:-1]):
            result = f"(if {condition(node['condition'])} then {str(node['return']).lower()} else {result})"
        return result
    if tree["kind"] == "selection":
        result = expression(tree["cases"][-1]["body"])
        for case in reversed(tree["cases"][:-1]):
            result = f"(if {condition(case['condition'])} then {expression(case['body'])} else {result})"
        return result
    raise ValueError("Unknown expression kind")


def generate(ir, name):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
        raise ValueError("Invalid Lean name")
    if ir["effect"]["kind"] != "preserve-supplied-list":
        raise ValueError("Unsupported state effect")
    return (
        "import Lean\n\nnamespace CssDerivation\n\n"
        f"def {name} (first second third : Option Char) : Bool :=\n  {expression(ir['tree'])}\n\n"
        f"def observe{name[0].upper() + name[1:]} (source : List Char) : Bool × List Char :=\n"
        f"  ({name} source.head? source.tail.head? source.tail.tail.head?, source)\n\n"
        "end CssDerivation\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("anchor")
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    raw = (HERE / manifest["file"]).read_bytes()
    if sha(raw) != manifest["sha256"]:
        raise ValueError("Pinned source changed; explicit review required")
    ir = extract(raw.decode(), args.anchor)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "algorithm.json").write_text(json.dumps(ir, indent=2) + "\n")
    (args.output / ("Generated" + args.name[0].upper() + args.name[1:] + ".lean")).write_text(generate(ir, args.name))
    begin, end = ir["source_bytes"]
    (args.output / "algorithm.bs").write_bytes(raw[begin:end])
    print(json.dumps({"anchor": args.anchor, "generated": True, "source_sha256": sha(raw)}, indent=2))


if __name__ == "__main__":
    main()
