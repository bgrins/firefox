# Number lexical bridge

This capsule joins the accepted typed JSON number program to the earlier byte-oriented numeric lexical models. It does not change either implementation, either reference specification, or the canonical library.

## Composed contract

`DocumentBridge.admitted_bridge` quantifies over every finite byte list and both initial model-error values. Its caller premise requires every byte below 128, no NUL/CR/FF, and `NumericEntry.nativeStart = true`. It proves scalar `StartsNumber`, agreement with the independent `NumericLexical.reference` observation, positive consumed length, and exact prefix-plus-remainder cover.

The observation contains seven fields: consumed raw character codes, remaining character codes, integral digit run, fractional digit run, exponent digit run, explicit outer-sign presence, and the syntactic integer flag. Prefix text comes from the original input and the exact suffix length. It is not reconstructed by numeric serialization. Leading zeroes, explicit plus/minus and exponent spelling remain in the consumed prefix.

The proof chain is:

1. Accepted `number_fixture_decoded` establishes that the quoted actual JSON value decodes to `numberTree`.
2. Accepted `CssParserLowering.number_parts` connects the decoded program's backend to scalar `CssNumberSyntax.consume`, including exact input remainder and the pre-existing model-error Boolean.
3. New `scan_bridge`, `fraction_bridge`, `exponent_bridge` and `consume_bridge` connect structurally recursive scalar consumption to the independently preserved byte model. Failed fractional/exponent lookahead consumes nothing.
4. New `raw_parts_observation`, `prefix_from_suffix` and `lexical_observation` transfer all seven fields. Existing `NumericLexical.native_reference` changes the source-shaped byte model into its independently written declarative/reference model.
5. New `caller_domain` connects the scalar number-entry relation to the byte entry predicate. Existing lexical cover and positivity then give the admitted theorem.

The lower-level byte-lifting theorems hold for all 256 byte values interpreted as equally numbered Unicode scalars. This is a mathematical extension, not UTF-8 decoding. The public source interpretation is restricted to normalized ASCII; there, a byte, scalar and consumed code count coincide. The theorem does not assert that input preprocessing was actually run. NUL, CR, FF and non-ASCII source are refused by the experimental runtime wrapper; LF remains permitted. Runtime admission-wrapper correctness is checked by examples, not a new universal proof.

## Numeric core versus full token

`TokenBridge.fixed_document_token_component` identifies the JSON result with the numeric component of the already accepted full numeric-token reference. `admitted_full_token` additionally reuses that model's positive length, bound and exact full-token suffix. It does not equate the numeric-core and full-token remainders.

For `1e+`, the number consumer stops after `1`, leaving `e+`. The full token is a dimension with unit `e`, leaving `+`. For `1%x`, number consumption leaves `%x`; percentage-token consumption leaves `x`. These are kernel-checked cases. The existing name/escape composition is reused unchanged; this capsule does not introduce a second unit/name interpreter.

## Source and implementation boundaries

`SOURCE.json` and `CLAUSES.json` preserve accepted manual mappings to CSS Syntax revision `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`: [consume a number](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs), the ASCII-digit definition, and the starts-number caller obligation. The pinned URL is a source snapshot; the exact excerpt offsets and hashes, rather than a guessed line anchor, identify the clauses in `CLAUSES.json`. The inherited `SOURCE.json.file` points to the original capsule's full source; this small capsule includes its authenticated excerpts and provenance instead of another complete spec copy.

The prose-to-model interpretation remains manual. Source provenance does not prove that the interpreted relation is the only possible reading of the specification. This adds no CSS feature-coverage claim and does not serialize or newly lower the ordinary-Lean exact numeric projection.

`NumericLexical.native` and `NumericToken.native` are previously accepted source-shaped Lean models, not executions or verified extractions of Rust. Their names do not imply a native refinement theorem. Actual cssparser tokenizer entry, UTF-8 offsets, tokenizer reset/state, native floating-point conversion, integer payload saturation, CSSOM coercion and Stylo integration remain outside this capsule. Prior native differential work is recorded in `../css-number-native-boundary-plan-20261110-v1`; no new native harness is run here.

`fixed_document_suffix_and_error` preserves the **model's** input/error state. The error Boolean is not mapped to a native cssparser `ParserState` field or native parse-error behavior. The syntactic integer flag is lexical: `1e0` and `1.0` are non-integer tokens despite representing integral mathematical values. Sign presence means either `+` or `-` occurred; it is distinct from arithmetic negativity, including negative zero.

## JSON and runtime evidence

The existing kernel theorem applies to a quoted `Lean.Json` value. The checker binds its exact literal bytes to `number.json`. The actual-file `Runner` separately parses text, validates `NumberShape`, executes the returned parser through the proved generic lowering, and observes its returned parts/state. It never substitutes `numberTree` or imports the fixed fixture/correspondence modules. `ReferenceRunner` computes the independently preserved lexical reference on the same admitted input. Expected observations are finite explicit data, not a proof of native Rust behavior.

The changed valid document uses `+` as the exponent marker and consequently consumes all of `1+2`; the fixed document leaves `+2`. This runtime check demonstrates that execution depends on the supplied document. A well-typed `NumberShape` program need not implement the CSS algorithm. Generic JSON-value schema/codec proofs are reused; JSON text parsing, duplicate-key collapse, quotation and text serialization are not proved here.

## Validation controls

Three semantic mutants alter only the new observation adapter: erase sign presence, ignore exponent presence for integer classification, or consume one extra prefix character. Each must compile, fail the unchanged bridge law, and fail a specific previously passing actual-JSON witness with the exact false-proposition diagnostic. These are model-adapter mutants, not native mutations. Three separate provenance controls change a preserved lexical model, preserved number tree, and the actual JSON fixture; authentication must refuse each.

All copied modules retain their exact accepted bytes. `PRESERVED.json` binds their hashes and immutable Git origins; `ORIGINS.json` records the author's read-only object comparison. Kernel audits include the full named-theorem inventory of these dependencies and the new laws/cases. They permit only Lean's standard `propext`, `Quot.sound` and `Classical.choice`.

The accepted older `NumericDigits`, `Name` and `SemanticName` modules produce only unused-simp-argument style warnings under this newer pinned Lean. Their exact source bytes are preserved; the replay accepts only the exact known full output hashes for those three module builds, retaining their complete logs in `legacy-diagnostics/`. A changed diagnostic is rejected. All proof/error checks, axiom audits and diagnostics for newly written modules remain enabled.
