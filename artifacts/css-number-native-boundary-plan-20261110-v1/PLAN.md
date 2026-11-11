# Next connection: JSON number parsing to the native lexical boundary

**Recommendation:** join the new JSON execution path to the existing numeric-admission model, then extend its native differential harness. Do not build a second independent “first numeric harness.” The strongest immediate opportunity is exact lexical behavior and parser state transitions; numeric projection serialization can follow separately.

## What is already covered

- `css-tokenizer-numeric-admission-v1` proves entry/read guards, maximal numeric prefix, syntactic type/sign, numeric-token selection, decoded unit, count and suffix in its model. Its retained whole-cssparser replay compares **81 numeric cases on seven lexical fields**, plus nine scanner controls. Native/source correspondence remains an explicit admission, not a Rust proof.
- `css-tokenizer-numeric-repair-integration-v2` adds the actual saved-prefix capture, Rust decimal grammar admission and preservation of that lexical projection around the rare-value fallback. It records 84 instrumented captures, including three nonzero UTF-8 starts. It does not prove floating-point conversion correctness.
- The compensating-exponent defect is already fixed locally by `4391deb4751a8be2be98e838360f00c94808c5d5`. The pinned current tokenizer hash is exactly the candidate hash from that integration: `5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211`. Those old witnesses are regression controls, not new discoveries.
- The new JSON capsule proves actual-Json decoding/encoding and lowering, then reaches `NumericResult` through `numberTree`. Its 42-case corpus, each with both model error flags, does **not** compare native tokenization. `NumberTransfer.project` remains ordinary Lean after parser execution.
- `css-tokenizer-public-stream-scout-v1` already investigated pending-block cleanup, cache hits and observers. A new numeric restart experiment must remain narrower than an unrestricted public-parser/observer theorem.

## Smallest substantive formal addition

Start with normalized ASCII input, explicitly excluding NUL, CR and FF so preprocessing cannot change the byte/remainder comparison. Supply the existing `StartsNumber`/`nativeStart` caller premise. Prove an adapter theorem between the decoded fixed number program and `NumericLexical.native`:

1. Map ASCII bytes to scalar characters and prove the entry predicates agree.
2. Relate the three digit runs and guarded fraction/exponent selections, using the already independent reference grammars on both sides.
3. Prove equality of consumed raw prefix, remainder, integral/fraction/exponent digits, outer sign presence and syntactic integer flag. Derive raw prefix from the original input and exact remainder, not by serializing the numeric value: leading zeroes and E/e spelling have been discarded by value projection.
4. Compose the fixed-file decoding/lowering theorem with this bridge. Then reuse `NumericToken.native_reference` for percent/unit dispatch and the existing decoded-name semantics.

This removes a real unconnected-model boundary. It still does not turn finite native observations into a universal Rust refinement theorem. A later UTF-8/filtered-input bridge must explicitly connect scalar streams, native byte offsets and raw remainders; the older encoded-unit assumptions and the newer DOMString/streaming adapter are useful inputs but are not automatically that theorem.

## Native harness surface

Use the **complete pinned cssparser source**, with an isolated dependency/target directory, reusing the earlier direct-source build recipe. A new driver should emit structured records from `Parser::next_including_whitespace_and_comments`, clone the returned token before inspecting position, and retain byte-exact suffixes. The usual `next()` skips whitespace; pending blocks can also advance the cursor. Admit a numeric token boundary with no pending block or enclosing stop delimiter for the first experiment.

| Surface | Useful observation | Qualification |
| --- | --- | --- |
| Uninstrumented public Parser | Token kind, `has_sign`, `int_value.is_some()`, decoded Dimension unit, total end byte, raw suffix | This is the full numeric **token**, not just consume-number |
| Exact copied tokenizer with one removable trace before suffix dispatch | Numeric-core start/end and borrowed raw prefix | Pair with the uninstrumented run; instrumentation is not a production-equivalent performance experiment |
| Saved ParserState, reset, reread, then read suffix token | Same numeric lexical projection and subsequent token boundary at nonzero starts | Limit to numeric histories; do not claim general observer/cache correctness |
| Stylo/browser property acceptance | A minimized externally observable consequence of a native mismatch | Property grammar, clamping, calc and serialization can mask or add differences |

The old harness already has the first two surfaces. Reuse them before adding another extraction. It compiles without `fast_match_byte` and uses a handwritten substitution-kind shim for whole-scanner controls. Numeric direct observations do not need that shim. A new public-token-only driver can omit the scanner entirely. Add a production-feature Cargo build only when dependencies are isolated/pinned; default cssparser features include `fast_match_byte` and `fast_match_color`. Keep the existing dispatch-correspondence qualification if that variant is deferred.

## Avoid false discrepancies

- **Core versus token:** `1e+` leaves `e+` after consume-number, but full tokenization can return Dimension(unit=`e`) and leave `+`. `1px` and `1%` consume suffixes after the numeric core. Escaped units can consume more source bytes than their decoded spelling. Compose the existing token/name model before comparing full cursor positions.
- **Type versus value:** `1`, `1.0` and `1e0` have different syntactic integer flags despite equal values. Compare `int_value.is_some()`, not whether the float is mathematically integral. The actual integer payload saturates to i32 limits; defer its numeric equality.
- **Sign:** native `has_sign` reports only explicit-sign presence. The model's `+` versus `-` character is visible in the raw source prefix, but that alone does not check the native arithmetic sign. Retain small exact/negative-zero payload sentinels separately; do not infer a universal sign/rounding theorem from lexical agreement.
- **Representation:** native positions count UTF-8 bytes; model lists count scalars; source-location columns count UTF-16 units. A non-ASCII prefix requires an explicit offset relation. NUL/CRLF/FF preprocessing and escaped-name normalization belong in a second tier with that relation.
- **Payload noise:** Percentage divides before f32 publication; integer saturation, f64/f32 rounding, overflow and CSS property clamping are distinct from lexical fidelity. Record payload bits without treating every exact-rational difference as a bug. Do not use CSSOM serialization as a raw-prefix oracle.
- **State:** the Lean model's incoming error Boolean is not a cssparser ParserState field. Its preservation theorem remains internal; the native projection must not invent an equivalent error flag.

## Corpus and acceptance gates

`CORPUS.json` gives proposed seed families and generation recipes; it is a plan, not an executed result. Carry forward the existing 81 numeric cases and compensated-exponent controls. New emphasis: EOF after each guard prefix; incomplete exponents immediately followed by units/escapes; trailing-token visibility; reset/replay at nonzero UTF-8 starts; and lengths around the existing 256-byte fallback boundary. Use bounded deterministic generation followed by grammar-preserving shrinking. Do not materialize 10 raised to enormous exponents just to compare lexical fields.

The first deliverable should contain: the universal ASCII model bridge; exact-source native observations for the old corpus and new histories; separate numeric-core and full-token columns; and compiling sensitivity controls for lost sign presence, lost exponent type, one-byte prefix overrun and bad reset/end position. A mismatch must survive an independent grammar check and source-boundary audit before browser work. Then add a focused WPT with an actual property consumer and control; browser serialization alone is insufficient evidence.

The existing WPT `css/css-syntax/decimal-points-in-numbers.html` checks decimal-point admission through line-height/width setters. It does not expose all native token metadata. No WPT status or new browser result was measured in this investigation.

## Alternatives ranked

1. **Model bridge plus expanded native differential checks:** highest near-term bug-finding/refinement value; reuses the prior native and lexical proof investment and connects the new data route to it.
2. **Serialize the exact numeric projection:** useful tooling work, but needs typed products/options and signed integer/result assembly beyond the current FirstOrder base expression types. It would reduce the fixed postprocessor boundary, not establish native rounding or validate CSS prose. It is not a prerequisite for lexical comparison.
3. **Mechanical prose extraction:** addresses a different, larger trust boundary. The earlier frozen escape translator correctly refused consume-number; the later manually extended number IR does not reverse that held-out refusal. A future extractor should retain clause provenance, explicit unsupported constructs and independent held-out interfaces, rather than treating source hashes or roundtrips as interpretation proofs.

Searchfox was used first; its indexed tokenizer predates our local repair. The source pin and exact local excerpts therefore govern this plan. `PINS.json` records the Searchfox permalink, immutable local Git files, earlier evidence hashes, and tool/cache limitations. The normative excerpts are from the already accepted CSS Syntax revision `c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67`, not a newly claimed latest-spec validation. No native build, browser run, canonical edit or Git mutation was performed.
