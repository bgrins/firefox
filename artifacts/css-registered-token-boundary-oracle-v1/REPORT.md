# Registered-value token boundary: independent oracle

## Verdict

**REACHED:** a registered `<length-percentage>` whose computed value is `20px`, substituted into `font:var(--lp)serif`, supplies a dimension token followed by an ident token. The resulting font size is20px and family isserif. This is the same token-level declaration as `font:20px/**/serif`, and does not depend on an installed font or glyph metrics. A string-based implementation must preserve this boundary; `20pxserif` is a different dimension with unitpxserif and cannot represent this substitution.

This is a normative/source review. No browser run was performed here; root owns runtime evidence. No novelty claim is made.

## Independent normative chain

1. [Properties and Values §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) computes a length literal in `<length-percentage>` to its canonical-unit value. Literal20px stays20px; no percentage base, relative-font cycle, animation, or registration mutation is involved.
2. [§2.7](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) requires replacement by the token sequence obtained from serialization and tokenization of that computed value. It does not concatenate its text into surrounding token spelling. The supplied dimension is20px; the existing serif ident survives independently.
3. [Syntax §9](https://drafts.csswg.org/css-syntax-3/#serialization) requires token-preserving serialization and specifically marks dimension followed by ident as requiring an intervening comment. Comments do not become whitespace tokens, so this also supplies an explicit comment-separated reference without relying on whitespace insertion.
4. [Fonts §2.7](https://drafts.csswg.org/css-fonts-4/#font-prop) accepts font-size followed by font-family. The separate20px andserif tokens satisfy those productions. Earlier valid font declarations must not be used as the expected fallback: a failure during substitution is computed-value invalidity, not parse-time removal.

The four current primary documents and exact retrieval identities are retained in SOURCES.json. Anchors above were checked against retained HTML; section extracts are for reading, not an alternate source. The missing optional webspec-index helper was previously reported/bootstrap-attempted; direct primary retrieval was used.

## Distinguishing cases for root's fixture

| Case | Expected | Purpose |
|---|---|---|
| Registered `<length-percentage>`20px, `font:var(--lp)serif` | size20px/familyserif | Main boundary |
| Same value, explicit `/**/` before family | Same | Token-preserving reference |
| Same value, ordinary space before family | Same | Positive parser/provider control |
| Registered `<length>`20px | Same | Alternate registration path |
| Unregistered20px | Same | Existing token-stream path |
| Registered `<length-percentage>`25%, parent size80px | size20px/familyserif | Percentage does not merge with following ident |
| Registered mixedcalc, thenserif | Compare explicit serialized-token reference | Closing parenthesis is a separate lexical boundary |
| Raw literal `20pxserif` | Invalid font grammar | Detect accidental textual-concatenation oracle |

Use a parent with an explicit distinct inherited font size/family, assert custom computed serialization first, and compare the target's individual font-size/family to the comment-separated reference. A CSS.supports call containingvar() alone does not establish successful computed substitution.

## Source boundary, after deriving the oracle

Searchfox identified `properties_and_values/value.rs::serialization_types` and `custom_properties.rs::VariableValue::push`. Exact local fullfiles are copied and hashed in NATIVE-TEST-INPUTS.json; these contain existing project repairs and are not pristine upstream snapshots.

The component classifier assigns both ends of LengthPercentage the Percentage class, irrespective of whether its actual computed serialization is a dimension, percentage, or function. `Value::to_variable_value` passes those supplied classes to the untyped value. `VariableValue::push` trusts the prior last and next first classes when deciding whether to append/**/. Thus a correct separator algorithm can receive false boundary information. This review does not propose changing global token separation rules.

List metadata also derives both ends from the first component. A future general repair should account for the actual first and last serialized tokens, not merely repair the scalar20px example. For homogeneous variant lists, the concrete emitted lexical class can still differ across `<length-percentage>` components. A percentage-first/dimension-last list followed by an ident is a useful reduced token-stream case; bind a real consuming grammar before calling it an additional browser defect.

## Strings, comments and other variants

`OwnedStr::to_css` calls serialize_string; `String` uses Other metadata. Properly quoted strings do not merge with neighboring ident/number/string tokens, so Other is appropriate for these normal boundaries. Comment-looking text inside a string is string content, not a comment requiring boundary insertion. This source inspection does not establish complete escaping/EOF correctness, which belongs to a different provider proof.

Color/Image/Transform variants are classified as Function/Other without consulting the serialized value. Keyword serialization, if admitted by that variant (for example a transform-list none), would instead end in an ident and may merge with a following ident. This is a targeted follow-up hypothesis, not an accepted defect: first establish actual registration acceptance/computed serialization and a valid consuming grammar. Color keyword support or currentColor resolution cannot be inferred from the generic variant tag. `<url>` normally serializes with an explicit closing parenthesis; no analogous trailing merge is established here.

## Existing coverage and known-issue limits

Retained `registered-property-initial.html` covers computed-value substitution for many registrations, includingcalc length-percentage, but substitutes an entire value without a trailing ident. No metadata file was found at its exact expected path; no local run is claimed.

Retained `serialize-consecutive-tokens.html` has an extensive unregistered token-pair matrix, including dimension/ident, plus string/comment and empty-fallback cases. Its current metadata includes three known comment-preservation failures and an Android timeout condition; copied metadata records them. It does not exercise the registered computed-value metadata producer. This is a precise coverage gap, not a claim that all other WPTs lack coverage. Searchfox searches were bounded to the relevant two WPT directories.

Bounded public searches for registered length-percentage/token serialization found no exact matching issue. Related prior art: [bug2029558](https://bugzilla.mozilla.org/show_bug.cgi?id=2029558), synchronizing [WPT PR58996](https://github.com/web-platform-tests/wpt/pull/58996), concerns URL token serialization; it is not evidence of this dimension/ident issue. Search absence does not establish novelty.

## Next useful formal contract

For every admitted computed valuev, its boundary summary must equal the first/last token serialization classes of tokenizing serialize(v), with an explicit empty-value policy. Separately, concatenating two admitted token streams using the existing separator table preserves their concatenation modulo permitted whitespace normalization. Compose those results across arbitrary finite substitutions. Typed variants and lists must discharge the summary premise; assuming caller-supplied summaries correct would miss this lead. String escaping, tokenizer correctness, valid computed-value serialization and actual native/source correspondence remain separate obligations.
