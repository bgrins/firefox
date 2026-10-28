# Ordinary-property random index speculation

Source verdict: REACHED for two ordinary-property rollback paths. Browser observation is pending; this package does not claim a new accepted bug. These share the registered-alternative random-count root cause and should be managed as one rollback family, with separate reached entry points rather than inflated counts.

## Decisive paths

1. `PropertyDeclaration::parse_into` enters `ParserContext::with_property_declaration` once for the ordinary property. The counter starts at zero and remains shared across internal parse attempts.
2. `Opacity::parse` calls `NumberOrPercentage::parse_with_clamping_mode`. That method speculatively tries Percentage, then parses Number. For `opacity: random(property-index-scoped, 0, 1)`, the percentage attempt enters `MathFunction::Random`, increments the counter, and only afterward `into_percentage` rejects the Number result. `cssparser::Parser::try_parse` restores its cursor, not the external counter. The successful Number attempt allocates index 2. The selected value contains one random function and requires index 1.
3. Independently, `LineHeight::parse` tries `parse_line_height_number` before `NonNegativeLengthPercentage`. For `line-height: random(property-index-scoped, 10px, 90px)`, the first attempt allocates index 1, then `into_number` rejects the Length result. The accepted LengthPercentage retry allocates index 2. Number line-height is the first successful alternative and is a preservation control.

Both chains are present in indexed upstream discovery and exact local captures. SOURCE-PINS records all differences; LOCAL-DELTA shows the relevant parser/random/type-rejection blocks are unaffected by local font quantization, accepted numeric calculation fixes, or the substitution-module relocation upstream. No release-built-source equivalence is asserted.

## Oracle: authored ua keys are valid and share generated keys

[Values5 random-key grammar](https://drafts.csswg.org/css-values-5/#random-caching) includes `<random-ua-ident>` as a cache-key choice. The prose says it “isn’t intended to be specified by authors”, but gives a validity condition (custom-ident starting `ua-`), not an author-parse prohibition. The cache tuple includes that ident plus document/name/element identity. [Simplification](https://drafts.csswg.org/css-values-5/#random-simplify) substitutes exactly `ua-PROPERTY-INDEX`, with the index from the selected parsed value. Authored `ua-opacity-1` and a first indexed opacity function therefore have the same cache tuple when neither adds an element identifier or dashed name. Same tuple gives the same base; [evaluation](https://drafts.csswg.org/css-values-5/#randomness) with identical bounds gives the same result. Different keys may coincidentally yield equal samples, so no inequality assertion is used.

[Inline line-height](https://drafts.csswg.org/css-inline-3/#line-height-property) admits nonnegative numbers and lengths. The tiny probe uses positive px bounds, avoiding font metrics for the failing length case. The number control fixes font-size to 10px.

## Tiny root-executed observation

Load `observe.js` in an owned browser document and call `await observeOrdinaryRandomIndexes()`. It makes/removes one same-origin iframe, changes no preferences, registers no custom properties, and returns eight rows with every target/reference specified and computed value plus support flags. No browser has been launched by this audit.

- Two source-predicted failures: opacity Number and line-height Length.
- Two index-1 preservation controls: opacity Percentage and line-height Number.
- Two named-key sharing controls.
- Two fixed-.25 controls against literal .25 opacity and 30px line-height.

Each row retains explicit ua-PROPERTY-1 and ua-PROPERTY-2 references. `matchesExpected` is an observation, not a harness acceptance gate. Unsupported rows have null comparisons. Fixed/named controls need not match either indexed reference. CSSOM specified serialization can additionally expose the generated index even if computed samples coincide. Each reference stays on the same property, so computed serialization and length rounding are comparable. Node syntax check c7daa1/0 passed; browser execution remains root-owned.

## Other meaningful boundaries and repair scope

| Boundary | Assessment |
|---|---|
| NumberOrPercentage in opacity; also filter factors / border-image-slice | Same shared union path. Opacity is the smallest decisive witness; callers are not separate bugs. |
| LineHeight Number then LengthPercentage | Second reached ordinary union, independent of registered syntax Parser. |
| AngleOrPercentage Percentage then Angle, used by conic-gradient stop positions | Same static counter leak is reachable in that union; whole gradient parser has further speculation, so no exact final index/browser claim here. |
| Registered syntax alternatives | Existing confirmed workstream. Whole-alternative rollback remains needed for trailing-token/list failures; ordinary paths never enter it. |
| Random key optional parsing / optional numeric arguments | Not automatically a defect: many failed attempts make the whole value invalid. A successful fallback consuming the affected text is required before reporting another witness. |

A focused extension can reuse the existing counter-only rollback helper around the failed Percentage attempt in NumberOrPercentage and failed Number attempt in LineHeight. Preserve the entry count (not zero) and keep every successful increment. Do not silently broaden the current patch: root owns scope and review. A lower-level generic numeric-entry repair may cover more callers but still needs the registered complete-alternative boundary and careful nested success/failure accounting. This audit does not propose global ParserContext rollback or claim every speculative parser is pure.

## Provenance and limitations

Searchfox identifier/text discovery preceded all source capture. Initial get-file requests failed sandbox DNS; authorized read-only Searchfox retries succeeded. An attempted obsolete shorthand path returned404; its empty output was removed. No missing CLI bootstrap or source mutation was required. Exact local reads were limited to discovered files for upstream/branch comparison. `cssparser::try_parse` source was captured too. Current Values5 (27 October2026) and Inline3 (14 October2026) were read through the web tool; the existing pinned Values5 capture is referenced rather than rewritten. No automated webspec graph proof, native compilation, browser execution, Lean theorem, ledger change, or production repair is claimed.
