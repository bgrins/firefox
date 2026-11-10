import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def extract():
    sources = json.loads((ROOT / "SOURCES.json").read_text())["sources"]
    clauses = []

    def span(key, start, end, model, anchor):
        raw = (ROOT / sources[key]["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sources[key]["sha256"]:
            raise ValueError("Source drift: " + key)
        first, last = start.encode(), end.encode()
        if raw.count(first) != 1:
            raise ValueError("Unrecognized source marker: " + start)
        a = raw.index(first)
        b = raw.index(last, a + len(first))
        clauses.append({"source": key, "anchor": anchor, "model_or_boundary": model,
                        "start": a, "end": b, "sha256": hashlib.sha256(raw[a:b]).hexdigest(),
                        "markup": raw[a:b].decode()})

    span("webidl", '<h4 oldids="dom-DOMString"', '<h4 oldids="dom-ByteString"',
         "CodeUnit domain; nullable and coercion excluded", "idl-DOMString")
    span("webidl", '<div id="js-to-DOMString"', '</div>',
         "caller boundary: same units after successful ToString", "js-DOMString")
    span("webidl", '<h4 id="js-USVString"', '<h4 id="js-object"',
         "separate USVString conversion; not modeled as DOMString", "js-USVString")
    span("infra", '<h3 id=strings>', "<p>A <a>string</a>'s",
         "CodeUnit domain; interpretation delegates to ECMA", "string")
    span("infra", '<p>To <dfn export for="string,JavaScript string" id=javascript-string-convert>',
         '<div class=note>', "scalarize effect", "javascript-string-convert")
    span("ecma", '    <emu-clause id="sec-ecmascript-language-types-string-type"',
         '      <p>The function `String.prototype.normalize`',
         "Step rules; JavaScriptLength boundary", "sec-ecmascript-language-types-string-type")
    for a, b, model in [
        ("sec-utf16decodesurrogatepair", "sec-codepointat", "pairPoint; numeric Step.pair"),
        ("sec-codepointat", "sec-stringtocodepoints", "next; Step; exact count/suffix; no unpaired Boolean or arbitrary-index wrapper"),
        ("sec-stringtocodepoints", "sec-parsetext", "decode; Decoded"),
    ]:
        span("ecma", '    <emu-clause id="' + a + '"', '    <emu-clause id="' + b + '"', model, a)
    span("cssom", "CSSOMString {#cssomstring-type}", "<div class=note>",
         "implementation chooses DOMString or USVString", "cssomstring-type")
    span("cssom", "interface CSSStyleSheet : StyleSheet {",
         "dictionary CSSStyleSheetInit", "caller IDL; replaceSync explicitly USVString", "the-cssstylesheet-interface")
    span("cssom", "The <dfn method for=CSSStyleSheet>insertRule(", "<wpt>",
         "guarded normative call to parse a rule", "dom-cssstylesheet-insertrule")
    span("css", '\t<div algorithm="normalize into a list of tokens">', '\n\t</div>',
         "string branch invokes code-point filtering", "normalize-into-a-token-stream")
    span("css", '<h4 id="parse-rule">', '\n\t\t\t<li>\n\t\t\t\t[=token stream/Discard whitespace=]',
         "parse-rule normalizes input", "parse-rule")
    span("css", '<h3 id="input-preprocessing">', '<h2 id="tokenization">',
         "accepted CodePointInput model; preprocessing boundary", "input-preprocessing")
    return {"mapping": "manually selected and interpreted; byte extraction automatic, not a prose correctness theorem",
            "clauses": clauses}


if __name__ == "__main__":
    (ROOT / "CLAUSES.json").write_text(json.dumps(extract(), indent=2, ensure_ascii=False) + "\n")
