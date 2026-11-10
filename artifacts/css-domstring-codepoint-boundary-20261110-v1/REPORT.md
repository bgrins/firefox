# DOMString code-unit interpretation before CSS filtering

The missing boundary is well-defined: interpreting a DOMString/Infra string as
code points combines adjacent leading/trailing surrogate pairs and preserves
unmatched surrogates. CSS input preprocessing subsequently replaces the remaining
surrogate code points. The adapter and its composition theorem are checked here.

Caller qualification matters. CSSOM permits each implementation to define
`CSSOMString` as either `DOMString` or `USVString`; `replace` and `replaceSync`
explicitly take `USVString`. This artifact does not assume that every CSSOM call
preserves unmatched surrogates or establish which representation Firefox uses.

## Normative chain and domain

The source snapshots were selected by the latest commit touching each source
path at acquisition on 2026-11-10. `SOURCES.json` records immutable URLs, full-file
SHA-256 hashes, revisions and acquisition time. `CLAUSES.json` retains 15 exact
byte spans and manually authored model/boundary labels. `extract.py` locates those
spans mechanically and refuses any full-source hash drift. It does not translate
the prose or prove the correctness of the labels.

| Boundary | Normative source | Modeled / remaining obligation |
| --- | --- | --- |
| DOMString domain | [WebIDL DOMString](https://webidl.spec.whatwg.org/#idl-DOMString) corresponds to Infra strings | Finite `List (Fin 0x10000)`; no null or general JavaScript value domain |
| JavaScript conversion | [WebIDL conversion](https://webidl.spec.whatwg.org/#js-DOMString) preserves the units of the successful `ToString` result | Starts after coercion; its exceptions, side effects and LegacyNullToEmptyString branch are excluded |
| Units interpreted as points | [Infra strings](https://infra.spec.whatwg.org/#string) delegates to [ECMAScript String Type](https://tc39.es/ecma262/#sec-ecmascript-language-types-string-type) | Ordinary/unpaired units retain numeric value; a valid pair yields the specified supplementary value |
| Executable iteration | [CodePointAt](https://tc39.es/ecma262/#sec-codepointat), [StringToCodePoints](https://tc39.es/ecma262/#sec-stringtocodepoints) | Head/suffix adapter, exact one/two-unit consumption and finite iteration; arbitrary-index wrapper and IsUnpairedSurrogate return field are not exposed |
| CSS caller example | [CSSOMString choice](https://drafts.csswg.org/cssom/#cssomstring-type), [CSSStyleSheet.insertRule](https://drafts.csswg.org/cssom/#dom-cssstylesheet-insertrule) | Conditional DOMString route after origin-clean and disallow-modification guards; USVString remains a distinct allowed route |
| Parser entry | [Parse a rule](https://drafts.csswg.org/css-syntax-3/#parse-rule) normalizes input; normalization's string branch filters code points before tokenization | Manually traced call chain, not a Lean CSSOM/parser state machine |
| Filtering | [CSS input preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing) | Exact composition with accepted `CodePointInput` relation; tokenizer and resulting CSS rule are outside this artifact |

The conditional call-chain verdict is **REACHED** for a successful DOMString
conversion passed to `insertRule` in the DOMString definition of CSSOMString,
after both pre-parse guards permit the call. No assumption that the rule will
parse successfully is needed to reach filtering. This is a reviewed normative
trace, not an end-to-end theorem or observed browser result. `replaceSync` cannot
serve as a DOMString example because its signature explicitly says USVString.

Immutable source versions are:

- [WebIDL 0d862c6573d0ecca327b7ba00210e7c051c988b3](https://github.com/whatwg/webidl/blob/0d862c6573d0ecca327b7ba00210e7c051c988b3/index.bs)
- [Infra c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs)
- [ECMAScript 828d35d00f8584c4a0fbcac7742b57c7b959c3f3](https://github.com/tc39/ecma262/blob/828d35d00f8584c4a0fbcac7742b57c7b959c3f3/spec.html)
- [CSSOM 5823c7a7c3401c6b434dbf3ef88077ea45e30303](https://github.com/w3c/csswg-drafts/blob/5823c7a7c3401c6b434dbf3ef88077ea45e30303/cssom-1/Overview.bs)
- [CSS Syntax c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs)

`webspec-index` was attempted but its cache was read-only; the failed command is
retained in `webspec-infra.log`. No tool update or cache mutation was performed.
The raw primary snapshots, rather than that failed index lookup, support this trace.

## Checked artifact

`DomString.lean` defines `CodeUnit`, checked natural-number admission, `next` and
`decode`. The independent `Step` relation specifies the output's numeric value,
pairing priority and exact original suffix. `Decoded` relates complete finite
inputs to output lists through these steps; it does not call the decoder.

`Correctness.lean` establishes:

- `next_iff`: exact code point and remaining unit sequence agree with `Step`.
- `Step.exact_suffix` / `Step.progress`: exactly one or two original units are
  consumed, with the pair's order, ranges and numeric equation retained.
- `next_none_iff`: an admitted input returns EOF exactly when empty.
- `decode_iff` and uniqueness: complete executable/declarative correspondence.
- `Decoded.length_bounds`: output length is at most input length and input length
  is at most twice output length.
- `preprocess_iff`: composing the adapter with accepted CSS filtering agrees with
  independently related intermediate code points and final scalars.
- Output normalization/nonexpansion and explicit unmatched-surrogate preservation
  before filtering, followed by replacement during filtering.

The two copied `CodePointInput` modules are byte-identical to standalone library
commit `06893e4890871614f763dc8c955100852ebdd5ac`; `LIBRARY.json` pins them.
No canonical library files were changed.

`ScalarChoice.lean` proves `filter_scalarize` for every finite code-point list:
replacing surrogate code points with U+FFFD before CSS filtering leaves the final
filtered scalar list unchanged. `choice_filter_equivalent` specializes this to
decoded code units. This describes the scalar-conversion effect at the filtering
boundary; it does not model a USVString's re-encoding or prove equality of API
exceptions, source storage, serialization, indexing, object state or all later
behavior. Intermediate DOMString interpretation is still different, as the
unmatched-surrogate examples show. Consequently, final CSS-filter output alone
cannot detect an incorrectly early replacement in this adapter.

All prose-to-model choices remain manually reviewed. The relations share the
reviewed leading/trailing range predicates with the executable functions; the
kernel cannot establish that those shared predicates match English requirements.

## Checks and controls

The final receipt is `review-verification/report.json`: 46 audited declarations
(28 new and 18 copied), 34 ordered executable observations and 11 controls.
The same Lean sources also compile three anonymous examples distinguishing the
intermediate surrogate result, its final filtering equivalence, and the failure
of stateless pair splitting. Only the standard admitted axioms are allowed.

The 34 observations include minimum/maximum pairs, supplementary values, exact
pair arithmetic, isolated/reversed/truncated surrogates, overlapping candidate
pairs, full suffix preservation, CRLF before and after interpretation, NUL/FF,
and invalid unit admission. Four executable-only mutations typecheck but fail
unchanged correspondence proofs and exact direct false-witness diagnostics:
early surrogate replacement, omitted pair combination, lost suffix unit and
incorrect pair arithmetic. Proof-rejection logs may include secondary tactic
warnings caused by the altered program; witness controls admit only the single
intended `decide`-proved-false diagnostic, without unrelated errors or warnings.

A fifth semantic control changes the shared leading-surrogate lower boundary.
Correspondence still proves against the jointly altered relation and algorithm;
the independently expected minimum-pair example fails. This is deliberate
evidence of the manual vocabulary boundary, not a purported proof failure.
The remaining controls reject an out-of-range unit construction and drift in
each of the five pinned specification sources.

The final checker runs under optimized Python with explicit rejection guards.
Output must be a fresh directory. Input hashes are checked before and after;
temporary object files are removed. Earlier unsuccessful harness attempts remain
as development logs: an unused mutation binder and secondary proof-failure
warnings were rejected before their control handling was corrected. The
successful model's semantics were not changed to accommodate a mutation.

`clean-verification/report.json` and `clean-replay.log` reproduce the same result
from exactly the 17 allowed source files in a temporary directory. That directory
and the earlier owned development build directory were removed after success.

## Exact limits and next step

Inputs are finite lists of already acquired 16-bit units. The internal theorems
cover arbitrary finite lengths, a mathematical superset of ECMAScript strings;
`JavaScriptLength` separately expresses its 2^53−1 maximum. Numeric admission
validates individual units, not that length bound. Values above 0xFFFF, including
valid supplementary code-point numbers, are rejected as individual units.
`Fin` literals can wrap, so external numeric admission uses `unitOfNat?`.

No byte decoder, endianness, BOM handling, DOM conversion implementation,
normalization form, browser memory layout, streaming/chunk adapter or CSSOM
state machine is modeled. Stateless chunking can split a valid surrogate pair;
CSS filtering additionally needs CRLF boundary handling. A streaming extension
would need a pending leading-surrogate unit as well as the filtering layer's
pending CR contract. That is a separate proof obligation.

This is a complete finite-list adapter result with an explicit conditional caller
trace. The next useful decision is whether to integrate it as a library input
module or first add a small proved unit-to-scalar encoding round trip to make
the USVString re-encoding boundary explicit. It does not justify claiming a
verified DOM API or full CSS parser.

## Source-only replay

`SOURCE-ONLY.json` lists 17 hashed source inputs. Copy only those paths to a new
directory and run from there, using the existing pinned Lean toolchain:

```sh
python3 -O check.py \
  --lean /Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out /private/tmp/css-domstring-independent-result
```

The output directory must not exist. No network, Lake cache, canonical library
checkout or installed package is needed. `fetch.py` is acquisition history and
is not part of replay; do not run it to validate this frozen source version.
