# Unit spelling is not a dimension token

## Verdict and boundary

The normative oracle is settled for this probe: a bare identifier, URL token, at-keyword or hash does not become a relative length merely because its decoded text matches a unit name. The source predicts seven failing rows and seven passing controls in `registered-unit-token-classification.html`. Browser execution is still pending.

This concerns the original declaration parser's unit classification. It does not depend on the proposed resolved-output scanner, attr-only graph collection, or the unresolved question about relative dimensions inside unused fallbacks. No native repair, binary correspondence, universal parser proof or novelty claim is supplied.

## Exact source chain

The complete local `custom_properties.rs`, `properties/cascade.rs` and `properties_and_values/value.rs` are retained under `native/`. Copy-before/after hashes were stable; `SOURCE-PINS.json` binds them. Searchfox discovery output locates the indexed token branch, but indexed bytes are not used as a replacement for these changed local files.

1. `parse_declaration_value_block` shares one match arm between Ident, AtKeyword, Hash, IDHash, UnquotedUrl and Dimension. It calls `ReferenceFlags::from_unit(value)` for every variant, before token-specific escaping/URL repair.
2. A decoded `em` or `EM` therefore produces FONT_UNITS even when the token is an identifier. `lh` produces both font and line flags. Unquoted URL content `em`, at-keyword `@em`, and ID hash `#em` trigger the same classification.
3. A registration containing a length alternative makes `find_non_custom_references` consult these flags, regardless of which syntax alternative will eventually parse the value.
4. With `font-size: var(--token-mixed)`, the retained declaration makes the reverse font-to-custom edge. The false custom-to-font edge closes a cycle before typed parsing can preserve the identifier or reject the invalid token.
5. SCC handling invalidates both the custom property and font-size. Non-inherited registrations use their initial value; font-size behaves as unset and inherits the parent's 23px.

The first four failing identifier rows expect their identifiers to remain intact, while the source predicts 11px. Font-size is 23px in both outcomes because identifiers such as em are not valid font-size values. Direct custom-property readback is essential to expose this difference.

For invalid @em and #em under a length-only registration, the custom property correctly ends at 11px under either path. The distinction is font-size: normal invalid-at-computed-value-time handling supplies the registered initial 11px to var(), so font-size must become 11px. The spurious cycle instead invalidates font-size itself, yielding inherited 23px. These are invalid input values with a settled fallback oracle, not claims that at-keywords or hashes satisfy the registered syntax.

## Primary specification trace

1. CSS Values 4 [custom identifiers](https://drafts.csswg.org/css-values-4/#custom-idents) are case-sensitive identifiers; em, EM and lh are not excluded keywords here. Its [dimension definition](https://drafts.csswg.org/css-values-4/#dimensions) requires a number followed by a unit identifier. CSS Syntax 3 separately tokenizes identifiers, dimensions, at-keywords, hashes and URLs. Escaping the letters of em changes neither its token category nor its decoded identifier.
2. Properties and Values API [computed-value rules](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) check registered syntax at computed-value time. Identifiers remain identifiers, while relative URLs resolve against their base. The [relative-unit dependency rule](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles) concerns units in length syntax, not arbitrary text whose spelling resembles a unit. With no dimension there is no font dependency to add.
3. CSS Values 5 [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) substitutes var() before the resulting font-size grammar is checked. Registered properties substitute computed values. Valid custom identifiers and URLs remain valid custom-property values even when they make the separate font-size declaration invalid. Invalid registered tokens reset to the registration's initial value; that valid 11px value can then set font-size.

Conclusion: REACHED for all asserted expectations. Unlike the unused-fallback timing issue, token category makes the distinction here: none of the candidate identifier/URL/at-keyword/hash values contains a dimension at any stage.

## Probe coverage and controls

| Family | Rows | Expected/predicted distinction |
| --- | ---: | --- |
| em, EM, escaped em, lh identifiers in a union with length | 4 | Expected preserved identifier; predicted 11px |
| Valid unquoted URL `url(em)` in a union with length | 1 | Expected resolved URL; predicted 11px |
| Invalid @em and #em in a length registration | 2 | Expected font 11px; predicted inherited 23px |
| Ordinary identifier, identifier-only registration | 2 | Both expected to pass |
| Real 1em cycle, absolute 13px | 2 | Preserve real cycle handling and ordinary length computation |
| Quoted URL, ordinary invalid hash | 2 | Distinguish URL tokenization and normal invalid-value fallback |
| em identifier without a font back edge | 1 | Confirms identifier parsing succeeds when the false edge cannot close a cycle |

Each row retains the specified custom declaration, uses a real parent calibrated to 23px, and reads both the computed custom property and font-size. The escaped identifier is expected to serialize as decoded `em`, while uppercase EM remains uppercase.

The URL case has no attr() source or attr taint. The grammar accepts `<url> | <length>`; both `url(em)` and `url("em")` denote the same relative resource. Expected CSSOM text is computed from `new URL("em", document.baseURI)` and standard quoted URL serialization. No image-consuming property is assigned: the only consumer is font-size, where URL syntax is invalid. The comparison does not depend on fetching the resource.

The hash probe specifically exercises the identifier-shaped hash #em (IDHash in this parser). It is not a valid color. No claim is made that an ordinary unrestricted Hash token can carry one of the unit-name strings while retaining that lexical category. The retained source's broader Hash arm is noted, not independently reproduced here.

## Packaging and verification

`CASES.json` records each oracle and static native prediction. The HTML contains identical case data. Run `python3 check.py` to authenticate all files/spec fetches/source pins and check case correspondence plus JavaScript syntax. It performs no browser or native execution. Fresh primary sources were retained with HTTP 200 fetch records on 2026-10-19.

A future minimal parser repair could restrict unit classification to Dimension tokens while preserving the shared escaping and URL-closing logic for all original variants. That is a repair direction only; no edit or correctness claim is made here.
