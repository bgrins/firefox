import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent


def main():
    source = (HERE / "prior/inputs/css-syntax-3.bs").read_bytes()
    expected = json.loads((HERE / "prior/SOURCE.json").read_text())["sha256"]
    if hashlib.sha256(source).hexdigest() != expected:
        raise ValueError("Pinned CSS source changed")
    ast = json.loads((HERE / "generated/escape.json").read_text())
    begin, end = ast["source_map"]["algorithm"]["source_bytes"]
    section = source[begin:end].decode()
    links = [
        ("/program", r"Consume the <a>next input code point</a>\."),
        ("/program/args/1/args/1", r"Consume as many <a>hex digits</a> as possible, but no more than 5\."),
        ("/program/args/1/args/1/args/2", r"If the <a>next input code point</a> is\s*<a>whitespace</a>,\s*consume it as well\."),
        ("/definitions/magnitudeExpr", r"Interpret the <a>hex digits</a> as a hexadecimal number\."),
        ("/definitions/decodeExpr", r"If this number is zero,.*?Otherwise, return the <a>code point</a> with that value\."),
        ("/program/args/0", r"This is a <a>parse error</a>\.\s*Return U\+FFFD REPLACEMENT CHARACTER \(�\)\."),
        ("/program/args/1/args/2", r"Return the <a>current input code point</a>\."),
    ]
    result = []
    for pointer, pattern in links:
        found = list(re.finditer(pattern, section, re.S))
        if len(found) != 1:
            raise ValueError("Ambiguous/missing source clause: " + pointer)
        target = ast
        for segment in pointer.strip("/").split("/"):
            target = target[int(segment)] if isinstance(target, list) else target[segment]
        match = found[0]
        result.append({"ast_pointer": pointer, "source_bytes": [begin + len(section[:match.start()].encode()), begin + len(section[:match.end()].encode())], "source_markup": match[0]})
    (HERE / "CLAUSES.json").write_text(json.dumps({
        "origin": "AST-to-prose links are manually chosen; unique source byte spans are extracted mechanically. This is traceability, not a proved semantic mapping.",
        "source_file": "prior/inputs/css-syntax-3.bs", "source_sha256": expected,
        "ast_file": "generated/escape.json", "clauses": result,
    }, indent=2) + "\n")
    print(json.dumps({"clause_links": len(result), "all_pointers_and_spans_valid": True}))


if __name__ == "__main__":
    main()
