# Structured CSS grammar derivation

This is a standalone, bounded prototype for an executable specification companion. It mechanically extracts the `justify-content` Value field and three referenced finite productions from pinned CSSWG Bikeshed source. It produces data-only instructions, source maps and a Lean-checkable data fixture. The runtime reads the actual JSON file and executes a generic grammar interpreter. It has no Stylo, Firefox, browser or canonical-library dependency. Its input domain is already decoded and ASCII-case-folded keyword tokens, not raw CSS strings; raw `SAFE LEFT` and CSS escapes are outside this layer.

The earlier derivation artifacts already recognize selected CSS Syntax algorithm prose and connect their typed programs to existing formal models. This prototype addresses a different input: the structured value-definition syntax already present in specification sources. It does not repeat that algorithm translator or claim to solve general English-to-Lean conversion. Inspected prior artifacts are hash-listed in RESEARCH-INPUTS.json.

## Reproduce

```
python3 -I check.py --lean /absolute/path/to/lean --out /new/check-output
python3 -I extract.py --out /new/generated-output
```

Use Lean 4.35.0-rc4. The checker compiles only the eleven included Lean modules in a fresh temporary directory, re-extracts the data, compares the generated fixture exactly, audits every named theorem, executes actual-file cases, and exercises text/JSON refusals and semantic mutations. It removes temporary compiled output on both success and failure. Reproduction needs no network, browser, native build or earlier research artifact. SOURCE-ONLY.json is the complete input allowlist; results and generated output are not needed to replay.

## Mechanical steps and human choices

| Layer | Mechanically performed | Explicit boundary |
| --- | --- | --- |
| Acquisition | Exact source revision and SHA checks | Choosing the source/version and normative context |
| Extraction | Unique property/production lookup, reviewed heading, dependency traversal and byte spans | This is a pinned Bikeshed subset, not Bikeshed preprocessing/includes or a normative/informative classifier |
| Restricted grammar | Lowercase keyword names, named references, grouping, alternation, juxtaposition and `?`; complete token consumption | Meaning and precedence of this supported notation are manually mapped from CSS Values |
| Data lowering | Inline finite dependencies, emit postfix instructions and JSON, quote the same data into Lean | Python extraction/quotation are not formally verified |
| Execution | Actual JSON decoding into typed grammar; structurally terminating interpreter | Raw JSON text parsing and the general JSON adapter are not newly proved here |
| Formal checking | Matching, finite-language and postfix laws; fixed quoted JSON decoding; exact fixture language | Kernel checking establishes these formal statements, not correspondence with English or layout behavior |

Unsupported operators (`&&`, `||`, repetitions, ranges and `#`), unknown markup, unresolved or cyclic references, duplicate definitions, missing anchors and incomplete/trailing grammar syntax refuse. The actual `justify-items` grammar is a refusal control because it contains `&&`; this is not a held-out transfer measurement. The recognized `pre` markup is deliberately narrow. It does not parse HTML comments or implement Bikeshed preprocessing/includes: a generic call to `extract()` over arbitrary documents is not a complete semantic Bikeshed extractor. The command-line entry point first requires the exact reviewed source hashes. Current selected blocks and their contexts were inspected; no claim is made that arbitrary matching markup elsewhere is normative.

Source maps distinguish each instruction's full expression span from its operator site. Juxtaposition has a separating span rather than an explicit operator character. Named reference edges retain their call sites; emitted instructions from dependencies point to their definition bytes. The complete property block, Value field, dependency blocks and ignored metadata remain available for review. Prose around the grammar, Applies-to conditions, computed values and layout effects are not translated.

## Checked semantic scope

`run_iff` proves that every remainder produced by the interpreter corresponds exactly to the independent inductive `Matches` relation, for every grammar and finite input list. `accepts_iff` requires full consumption. `remainder_suffix` preserves an exact consumed prefix and remainder. Independent finite-language soundness/completeness give `accepts_language`. Grammar recursion is structural; no arbitrary scan fuel is used.

`encode_execute` preserves any existing stack and following program when encoding a grammar; `decode_encode` proves roundtrip for every grammar. Neither law relies on the CSS fixture.

For the extracted fixture, `json_decodes` checks the actual quoted Lean.Json value against `extractedGrammar`. `extracted_language` checks that its language equals a separately authored enumeration, and `extracted_accepts` quantifies over arbitrary token lists. The checker regenerates both the Op data and Json quotation from the extracted program and checks exact equality with Fixture.lean. The runtime imports JsonInput only and reads its supplied file; it does not import the fixture or substitute a fixed grammar. The raw JSON text parser and Python quotation step remain outside the kernel theorem. The theorem is about the fixed quoted JSON value, not every runtime JSON document.

The independent oracle distinguishes 26 sequences: `normal`; four distribution keywords including `stretch`; seven bare positions; and `safe`/`unsafe` followed by each position. It rejects safety modifiers on `normal`/distribution keywords, reversed order and extra trailing tokens. A changed source grammar replacing `normal` with `ordinary` changes actual runtime acceptance, demonstrating that the JSON route is active.

Inputs are already decoded, normalized keyword-token spellings. The prototype does not tokenize CSS strings, decode escapes, lowercase identifiers, perform variable substitution or include CSS-wide keywords. In particular, `inherit` failing this narrow grammar does not imply an invalid CSS declaration. It models neither browser compatibility aliases nor any alignment/layout semantics. It adds no normative CSS coverage claim to the canonical library.

## Primary sources

The primary proof snapshot is historical: commit dated 2026-10-20, retrieved 2026-11-10. SOURCE.json pins CSSWG revision `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67` for [CSS Box Alignment](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-align-3/Overview.bs) and [CSS Values](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-values-4/Overview.bs). The property uses `align-justify-content` / rendered `propdef-justify-content`; dependencies are `content-position`, `content-distribution` and `overflow-position`. CSS Values' `component-combinators` and `mult-opt` supply the manually reviewed operator meanings; exact excerpts are retained in SEMANTIC-SOURCES.json.

The attempted webspec-index query failed because its database was read-only; diagnostics are retained. It reported version 0.14.0 with 0.15.0 available. No installed tool/configuration was changed. Read-only web pages and immutable primary source downloads were used instead. Verification uses the retained source snapshots.

## Observed current-spec drift

A comparison on 2026-11-10 Pacific (2026-11-11 UTC) found that the current Editor’s Draft, dated 2026-10-21, differs from the proof snapshot. Its latest css-align source commit was `3110cd02e77fa9e3869e433e1d40f615b6e611e4` (2026-10-21). `content-position` adds `flow-start` and `flow-end`; the selected property Value and other two productions retain their grammar. DRIFT-SOURCE.json pins that actual source and its commit metadata separately.

The unchanged extractor admits this newer grammar and emits 32 instructions. The runtime comparison confirms six added normalized sequences (bare and safe/unsafe-prefixed flow-start/flow-end), rejected by the historical grammar and accepted by the newer one. The 26-sequence kernel theorem still describes only the historical snapshot. CurrentFixture/CurrentReference separately check the current quoted Json decoding and prove its exact 32-sequence language for arbitrary normalized token lists, using the same generic laws and a separately enumerated reference. The historical fixture remains unchanged. This real dependency change is precisely why evolving alongside the spec requires following referenced productions, not checking the property Value field alone.
