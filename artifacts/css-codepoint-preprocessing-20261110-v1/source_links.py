import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())["sources"]
    texts = {}
    for name, record in sources.items():
        raw = (HERE / record["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError("Pinned source changed: " + name)
        texts[name] = raw.decode()
    css = texts["css"]
    start = css.index('<h3 id="input-preprocessing">')
    end = css.index('<h2 id="tokenization">', start)
    (HERE / "input-preprocessing.bs").write_text(css[start:end])
    patterns = [
        ("css", "preprocess / Preprocess.crlf / Point.carriageReturn / Point.formFeed",
            r"Replace any U\+000D CARRIAGE RETURN \(CR\) <a>code points</a>,\s*U\+000C FORM FEED \(FF\) <a>code points</a>,\s*or pairs of U\+000D CARRIAGE RETURN \(CR\) followed by U\+000A LINE FEED \(LF\) in \|input\|\s*by a single U\+000A LINE FEED \(LF\) <a>code point</a>\."),
        ("css", "point / Point.null / Point.surrogate",
            r"Replace any U\+0000 NULL or <a>surrogate</a> <a>code points</a> in \|input\|\s*with U\+FFFD REPLACEMENT CHARACTER \(�\)\."),
        ("css", "Unmodeled DOMString conversion boundary",
            r"Note: The only way to produce a <a>surrogate</a> <a>code point</a> in CSS content is by directly assigning a <code>DOMString</code> with one in it via an OM operation\."),
        ("infra", "CodePoint / ofNat?",
            r'<p>A <dfn export lt="code point\|character">code point</dfn> is a Unicode code point and is\s*represented as "U\+" followed by four-to-six <a>ASCII upper hex digits</a>, in the range U\+0000 to\s*U\+10FFFF, inclusive\.'),
        ("infra", "Surrogate lower subrange",
            r"<p>A <dfn export>leading surrogate</dfn> is a <a>code point</a> that is in the range U\+D800 to\s*U\+DBFF, inclusive\."),
        ("infra", "Surrogate upper subrange",
            r"<p>A <dfn export>trailing surrogate</dfn> is a <a>code point</a> that is in the range U\+DC00 to\s*U\+DFFF, inclusive\."),
        ("infra", "Surrogate union",
            r"<p>A <dfn export>surrogate</dfn> is a <a>leading surrogate</a> or a <a>trailing surrogate</a>\."),
    ]
    clauses = []
    for source, model, pattern in patterns:
        text = texts[source]
        matches = list(re.finditer(pattern, text))
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous reviewed clause: " + model)
        match = matches[0]
        clauses.append({"source": source, "model": model, "source_bytes": [len(text[:match.start()].encode()), len(text[:match.end()].encode())], "markup": match[0]})
    (HERE / "CLAUSES.json").write_text(json.dumps({
        "interpretation": "Model/function links and semantic meanings are manually authored. Byte spans are mechanically located in pinned source; no prose-to-Lean correctness theorem is claimed.",
        "clauses": clauses,
    }, indent=2) + "\n")
    print(json.dumps({"matched_clauses": len(clauses), "all_sources_hash_checked": True}))


if __name__ == "__main__":
    main()
