import argparse
import hashlib
import html
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ANCHOR = "starts-with-a-valid-escape"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(markup):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", markup)).split())


def section(source):
    headings = list(re.finditer(r'<h([2-6])\s+id=[\'"]([^\'"]+)[\'"]\s*>', source))
    matches = [m for m in headings if m[2] == ANCHOR]
    if len(matches) != 1:
        raise ValueError("Expected exactly one algorithm heading")
    start = matches[0]
    end = next(m.start() for m in headings if m.start() > start.start() and int(m[1]) <= int(start[1]))
    body = source.index("</h4>", start.end()) + len("</h4>")
    return start.start(), body, end


def extract(source):
    start, body, end = section(source)
    newline = re.search(r'<dt><dfn export>newline</dfn>\s*<dd>\s*U\+([0-9A-F]{4,6}) ([A-Z ]+)\.', source)
    if newline is None:
        raise ValueError("Unsupported newline definition")
    paragraphs = []
    for match in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", source[body:end], re.S):
        begin = body + match.start()
        finish = body + match.end()
        paragraphs.append({"text": text(match[0]), "source_bytes": [len(source[:begin].encode()), len(source[:finish].encode())]})
    if len(paragraphs) != 5:
        raise ValueError("Unsupported paragraph inventory; nothing is silently skipped")
    if not paragraphs[0]["text"].startswith("This section describes how to check if two code points are a valid escape."):
        raise ValueError("Unexpected algorithm introduction")
    if paragraphs[1]["text"] != "Note: This algorithm will not consume any additional code point.":
        raise ValueError("Unexpected observational note")
    branches = []
    for paragraph in paragraphs[2:]:
        value = paragraph["text"]
        literal = re.fullmatch(r"If the (first|second) code point is (not )?U\+([0-9A-F]{4,6}) [A-Z ]+ \(.\), return (true|false)\.", value)
        named = re.fullmatch(r"Otherwise, if the (first|second) code point is a newline, return (true|false)\.", value)
        default = re.fullmatch(r"Otherwise, return (true|false)\.", value)
        if literal:
            node = {"kind": "if", "slot": literal[1], "comparison": "ne" if literal[2] else "eq", "code_point": int(literal[3], 16), "return": literal[4] == "true"}
        elif named:
            node = {"kind": "if", "slot": named[1], "comparison": "eq", "code_point": int(newline[1], 16), "return": named[2] == "true", "resolved_term": "newline"}
        elif default:
            node = {"kind": "return", "return": default[1] == "true"}
        else:
            raise ValueError("Unsupported statement: " + value)
        branches.append(dict(node, source_bytes=paragraph["source_bytes"]))
    if [n["kind"] for n in branches] != ["if", "if", "return"]:
        raise ValueError("Unsupported control-flow shape")
    return {
        "anchor": ANCHOR,
        "source_bytes": [len(source[:start].encode()), len(source[:end].encode())],
        "paragraphs": paragraphs,
        "newline_definition": {"code_point": int(newline[1], 16), "source_bytes": [len(source[:newline.start()].encode()), len(source[:newline.end()].encode())]},
        "branches": branches,
        "manual_interpretations": [
            "The first/second slots are supplied observations, not a mutable input stream.",
            "Option Char represents a Unicode scalar or EOF; none denotes EOF.",
            "Otherwise means ordered fallthrough; source prose operators have their conventional meanings.",
            "A named newline comparison is false for EOF; decoding and preprocessing remain caller obligations.",
            "The introduction and non-consumption note are retained but are not mechanically given semantics."
        ]
    }


def generate(ir):
    body = []
    for node in ir["branches"]:
        result = str(node["return"]).lower()
        if node["kind"] == "return":
            body.append("  " + result)
        else:
            op = "!=" if node["comparison"] == "ne" else "=="
            body.append(f"  if {node['slot']} {op} some (Char.ofNat {node['code_point']}) then {result} else")
    return "import Lean\n\nnamespace CssDerivation\n\ndef validEscape (first second : Option Char) : Bool :=\n" + "\n".join(body) + "\n\nend CssDerivation\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    raw = (HERE / manifest["file"]).read_bytes()
    if digest(raw) != manifest["sha256"]:
        raise ValueError("Pinned source changed; review the new snapshot first")
    ir = extract(raw.decode())
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "algorithm.json").write_text(json.dumps(ir, indent=2) + "\n")
    (args.output / "Generated.lean").write_text(generate(ir))
    begin, end = ir["source_bytes"]
    (args.output / "algorithm.bs").write_bytes(raw[begin:end])
    print(json.dumps({"source_sha256": digest(raw), "ir_sha256": digest((args.output / "algorithm.json").read_bytes()), "generated_sha256": digest((args.output / "Generated.lean").read_bytes()), "recognized_statements": len(ir["branches"]), "unrecognized_statements": 0}, indent=2))


if __name__ == "__main__":
    main()
