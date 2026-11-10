import argparse
import hashlib
import html
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent


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
        raise ValueError("Expected one algorithm heading")
    start = matches[0]
    end = next(m.start() for m in headings if m.start() > start.start() and int(m[1]) <= int(start[1]))
    body = source.index(f"</h{start[1]}>", start.end()) + len(f"</h{start[1]}>")
    return start.start(), body, end


def definition(source, name):
    pattern = r'<dt><dfn export>' + re.escape(name) + r'</dfn>\s*<dd>\s*(.*?)(?=\s*<dt>|\s*</dl>)'
    match = re.search(pattern, source, re.S)
    if not match:
        raise ValueError("Missing definition: " + name)
    raw = re.sub(r"<wpt>.*?</wpt>|<span class='note'>.*?</span>", "", match[1], flags=re.S)
    return {"text": plain(raw), "source_bytes": span(source, *match.span())}


def require(pattern, text, label):
    match = re.fullmatch(pattern, text)
    if not match:
        raise ValueError("Unsupported " + label + ": " + text)
    return match


def dependencies(css, infra):
    definitions = {name: definition(css, name) for name in ["digit", "hex digit", "newline", "whitespace", "maximum allowed code point"]}
    cp = r"U\+([0-9A-F]{4,6}) [A-Z -]+ \(.\)"
    digit = require(r"A code point between " + cp + r" and " + cp + r" inclusive\.", definitions["digit"]["text"], "digit definition")
    hexadecimal = require(r"A digit, or a code point between " + cp + r" and " + cp + r" inclusive, or a code point between " + cp + r" and " + cp + r" inclusive\.", definitions["hex digit"]["text"], "hex definition")
    newline = require(r"U\+([0-9A-F]{4,6}) LINE FEED\.", definitions["newline"]["text"], "newline definition")
    whitespace = require(r"A newline, U\+([0-9A-F]{4,6}) CHARACTER TABULATION, or U\+([0-9A-F]{4,6}) SPACE\.", definitions["whitespace"]["text"], "whitespace definition")
    maximum = require(r"The greatest code point defined by Unicode: U\+([0-9A-F]{4,6})\.", definitions["maximum allowed code point"]["text"], "maximum scalar definition")
    ranges = []
    for name in ["leading surrogate", "trailing surrogate"]:
        pattern = r'<p>A <dfn export>' + name + r'</dfn> is a <a>code point</a> that is in the range U\+([0-9A-F]+) to\s*U\+([0-9A-F]+), inclusive\.'
        found = re.search(pattern, infra)
        if not found:
            raise ValueError("Unsupported Infra surrogate definition")
        ranges.append([int(found[1], 16), int(found[2], 16)])
        definitions[name] = {"text": plain(found[0]), "source": "infra", "source_bytes": span(infra, *found.span())}
    surrogate = re.search(r'<p>A <dfn export>surrogate</dfn> is a <a>leading surrogate</a> or a <a>trailing surrogate</a>\.', infra)
    if not surrogate or ranges[0][1] + 1 != ranges[1][0]:
        raise ValueError("Unsupported noncontiguous surrogate union")
    definitions["surrogate"] = {"text": plain(surrogate[0]), "source": "infra", "source_bytes": span(infra, *surrogate.span())}
    return {
        "digit_range": [int(digit[1], 16), int(digit[2], 16)],
        "upper_hex_range": [int(hexadecimal[1], 16), int(hexadecimal[2], 16)],
        "lower_hex_range": [int(hexadecimal[3], 16), int(hexadecimal[4], 16)],
        "whitespace": [int(newline[1], 16), int(whitespace[1], 16), int(whitespace[2], 16)],
        "surrogate_range": [ranges[0][0], ranges[1][1]],
        "maximum": int(maximum[1], 16),
        "definitions": definitions,
    }


def extract(css, infra, anchor):
    start, body, end = section(css, anchor)
    raw = css[body:end]
    paragraphs = list(re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", raw, re.S))
    intro = plain(paragraphs[0][0])
    expected = "This section describes how to consume an escaped code point. It assumes that the U+005C REVERSE SOLIDUS (\\) has already been consumed and that the next input code point has already been verified to be part of a valid escape. It will return a code point."
    if intro != expected:
        raise ValueError("Unsupported algorithm interface; only the reviewed scalar escape interface is admitted: " + intro)
    remainder = raw[paragraphs[0].end():]
    metadata = []
    for match in re.finditer(r"<span class='note'>.*?</span>|<wpt>.*?</wpt>", remainder, re.S):
        metadata.append({"text": plain(match[0]), "source_bytes": span(css, body + paragraphs[0].end() + match.start(), body + paragraphs[0].end() + match.end())})
    if [item["text"] for item in metadata] != ["Note that this means 1-6 hex digits have been consumed in total.", "escaped-eof.html"]:
        raise ValueError("Unreviewed note or test metadata")
    operative = plain(re.sub(r"<span class='note'>.*?</span>|<wpt>.*?</wpt>", "", remainder, flags=re.S))
    pattern = (
        r"Consume the next input code point\. hex digit "
        r"Consume as many hex digits as possible, but no more than ([0-9]+)\. "
        r"If the next input code point is whitespace, consume it as well\. "
        r"Interpret the hex digits as a hexadecimal number\. "
        r"If this number is zero, or is for a surrogate, or is greater than the maximum allowed code point, "
        r"return U\+([0-9A-F]{4,6}) REPLACEMENT CHARACTER \(�\)\. "
        r"Otherwise, return the code point with that value\. EOF "
        r"This is a parse error\. Return U\+([0-9A-F]{4,6}) REPLACEMENT CHARACTER \(�\)\. "
        r"anything else Return the current input code point\."
    )
    recognized = require(pattern, operative, "stateful body")
    return {
        "anchor": anchor, "source_bytes": span(css, start, end),
        "interface": {"text": intro, "return": "scalar", "input": "next unread scalars after backslash", "requires_valid_escape": True},
        "operative_text": operative,
        "body_source_bytes": span(css, body + paragraphs[0].end(), end),
        "metadata": metadata,
        "program": {"read_first": True, "hex_additional_limit": int(recognized[1]), "terminator_limit": 1, "base": 16,
            "zero_is_invalid": True, "surrogate_is_invalid": True, "maximum_is_inclusive": True,
            "invalid_replacement": int(recognized[2], 16), "eof_replacement": int(recognized[3], 16), "eof_error": True},
        "dependencies": dependencies(css, infra),
    }


def generate(ir):
    cfg, deps = ir["program"], ir["dependencies"]
    if cfg["read_first"] is not True:
        raise ValueError("Unsupported program without its required initial read")
    digit, upper, lower = (deps[key] for key in ["digit_range", "upper_hex_range", "lower_hex_range"])
    def range_test(bounds):
        return f"(Char.ofNat {bounds[0]} ≤ c && c ≤ Char.ofNat {bounds[1]})"
    hexadecimal = " || ".join(range_test(bounds) for bounds in [digit, upper, lower])
    whitespace = " || ".join(f"c == Char.ofNat {cp}" for cp in deps["whitespace"])
    bad = []
    if cfg["zero_is_invalid"]:
        bad.append("value = 0")
    if cfg["surrogate_is_invalid"]:
        bad.append(f"({deps['surrogate_range'][0]} ≤ value ∧ value ≤ {deps['surrogate_range'][1]})")
    bad.append(f"{deps['maximum']} {'<' if cfg['maximum_is_inclusive'] else '≤'} value")
    return f'''import StatefulIR

namespace CssDerivation

def isHex (c : Char) : Bool := {hexadecimal}
def isWhitespace (c : Char) : Bool := {whitespace}

def digitValue (c : Char) : Nat :=
  if c ≤ Char.ofNat {digit[1]} then c.toNat - {digit[0]}
  else if c ≤ Char.ofNat {upper[1]} then c.toNat - {upper[0] - 10}
  else c.toNat - {lower[0] - 10}

def magnitude (digits : List Char) : Nat :=
  digits.foldl (fun value c => value * {cfg['base']} + digitValue c) 0

def decode (value : Nat) : Char :=
  if {' ∨ '.join(bad)} then Char.ofNat {cfg['invalid_replacement']} else Char.ofNat value

def escape : Program Char :=
  .bind .read fun first =>
    match first with
    | none => .bind {'.raiseError' if cfg['eof_error'] else '(.pure ())'} fun _ => .pure (Char.ofNat {cfg['eof_replacement']})
    | some c => .branch (isHex c)
        (.bind (.scan {cfg['hex_additional_limit']} isHex) fun digits =>
          .bind (.scan {cfg['terminator_limit']} isWhitespace) fun _ =>
            .pure (decode (magnitude (c :: digits))))
        (.pure c)

end CssDerivation
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("anchor")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    texts = []
    for name in ["SOURCE.json", "INFRA.json"]:
        manifest = json.loads((HERE / name).read_text())
        raw = (HERE / manifest["file"]).read_bytes()
        if sha(raw) != manifest["sha256"]:
            raise ValueError("Pinned source changed; explicit review required: " + name)
        texts.append(raw.decode())
    ir = extract(*texts, args.anchor)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "algorithm.json").write_text(json.dumps(ir, indent=2) + "\n")
    (args.output / "GeneratedEscape.lean").write_text(generate(ir))
    begin, end = ir["source_bytes"]
    (args.output / "algorithm.bs").write_bytes(texts[0].encode()[begin:end])
    print(json.dumps({"generated": True, "anchor": args.anchor, "typed_result": "Program Char"}))


if __name__ == "__main__":
    main()
