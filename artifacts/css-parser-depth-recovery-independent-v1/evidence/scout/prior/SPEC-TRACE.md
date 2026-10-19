# Current spec trace

The webspec-index command was unavailable (exit 127). Fresh primary CSS Syntax HTML and selected full sections are retained instead. Spec date: 16 October 2026; retrieval date: 19 October 2026. Anchors below were found in the retained document. Additional CSSOM and CSS Fonts primary sections were read with the web tool.

## String value and newline handling — REACHED

1. A CSS property value is tokenized by [consume a token](https://drafts.csswg.org/css-syntax-3/#consume-token); a quote invokes [consume a string token](https://drafts.csswg.org/css-syntax-3/#consume-string-token), using that quote as terminator.
2. [Input preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing) normalizes CR/CRLF/FF and replaces NUL/surrogates. Native Rust input is UTF-8; raw surrogate admission therefore lies at the external string conversion, not within these loops.
3. Matching quote returns the accumulated string; EOF returns it with a parse error. A backslash immediately before EOF adds nothing. A backslash before newline consumes that newline; other escapes invoke [consume an escaped code point](https://drafts.csswg.org/css-syntax-3/#consume-escaped-code-point).
4. An unescaped newline returns BadString while leaving the newline to be consumed again. Native byte position is already before that raw newline, which represents the same stream position.
5. For the probe's accepted strings, [font-family](https://drafts.csswg.org/css-fonts-4/#font-family-prop) admits string family names. Equal decoded strings must yield equal parsed-value serialization; the probe supplies a valid literal reference instead of requiring one quote spelling.

Rejected route: applying generic escaped-code-point EOF replacement directly to a string's final backslash. The string algorithm's explicit EOF branch precedes that helper invocation and adds nothing. Identifiers and URL consumers have different call paths.

## Comments — REACHED

[Consume comments](https://drafts.csswg.org/css-syntax-3/#consume-comments) consumes the first opening delimiter through the first closing delimiter, or EOF. Its CSS result is discarded. A comment separating numeric/identifier pieces does not merge those already separate tokens. The native preserving-comment API and source-map/sourceURL effects are additional implementation observers; ignoring CSS comments does not prove those observers irrelevant.

## Existing BadString recovery issue — REACHED for the specified token trace

Scenario A is literal LF in `text-decoration:'` followed by LF then `';color:green`. Scenario B omits the quote after LF.

1. [CSSStyleDeclaration.cssText](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-csstext) parses declarations.
2. [Consume a declaration](https://drafts.csswg.org/css-syntax-3/#consume-declaration) consumes a list of component values, stopping at a semicolon token, then validates the declaration.
3. In A, BadString reconsumes LF. The next quote starts a new string whose payload includes `;color:green` through EOF. Its internal semicolon is not a semicolon token. There is no separate color declaration to preserve.
4. In B, the unquoted semicolon is the stop token. The invalid first declaration is discarded and the next color declaration is parsed.

This trace supports the two distinct probe expectations. It does not adjudicate any historical browser version mentioned in issue 393 or prove Gecko's complete declaration-consumer implementation. The alleged browser difference remains separate from correctness of the quoted-string token loop.
