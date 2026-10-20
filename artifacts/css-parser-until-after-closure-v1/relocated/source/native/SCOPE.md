# Native/model calibration contract

This harness compiles the complete retained cssparser crate plus its actual dtoa, dtoa-short, itoa and smallvec dependencies with the pinned rustc. It does not translate `parse_until_after`, `parse_until_before`, block recovery, or tokenization into a Rust facade. The appended wrapper supplies restricted callbacks and exposes private state; it is not a compiled Firefox caller. Ordinary byte-dispatch builds run in debug and release; optional fast-match, serde and malloc feature variants are not covered.

## Source correspondence

`BINDINGS.json` records exact complete bodies at byte spans in pinned source files, with separately retained copies. The ten named operations are `parse_until_after`, `parse_until_before`, `consume_until_end_of_block`, `parse_entirely`, `expect_exhausted`, `Parser::reset`, `Parser::advance`, `Parser::next_byte`, `Parser::next_unchecked`, and `Parser::skip_block_at_start`. The checker verifies body bytes and full source hashes. This is a source-identity gate, not an automatic Rust-to-Lean translation proof.

`UntilAfter.native` invokes the accepted `NestedControl.untilBefore`, retains Stop/error exactly, then advances requested-only delimiters and invokes the accepted raw stack on `{`. The independent reference and general proof remain root-owned in UntilAfter.lean. AfterDriver executes this model using the source-derived ByteLex composition. Numeric/string/hash/at-keyword providers are unsupported and emit a fatal-to-comparison diagnostic; whitespace is one maximal nativeWhitespace run and only `!`, `,`, `;` use the width-one punctuation provider. Braces, parentheses, square brackets, colon, comments, identifiers/functions and their accepted helpers take their corresponding explicit model branches. The corpus has no numeric/string/hash/at-keyword token requiring an omitted provider. A runtime diagnostic is rejected even if Lean returns status zero.

## Fixture admission and observations

The 27 histories use immutable valid UTF-8 strings. Requested masks contain only `{`, `;`, `!`, `,`; outer masks may also contain the three closing delimiters. Mask lists are canonical sets. The wrapper sets admitted outer control bits directly to represent enclosing parsers; this does not prove a Firefox caller constructs every such history. Each callback makes zero or one actual `next()` call, propagates its error, and otherwise either returns success or a custom failure. Model acceptance checks the same required call result, then models the native parse-entirely exhaustion lookahead. No arbitrary callback, panic/unwind, reentrant host mutation or provider lifetime theorem follows.

Saved states come from that same parser. `save` replaces the single retained state, and `reset` uses it; no forged position or cross-parser reset is admitted. `enable` tracks exactly var/env/attr and occurs before relevant tokens in these histories. Limit/depth controls are finite u8 values; they are observed unchanged through until-after, not used to claim arbitrary recursive callers terminate.

Every snapshot compares result success (or the projected returned token), byte position, pending opener, cache key/token/end-position/pending, tracking mode, sourceURL, sourceMappingURL, outer mask, depth, and limit. It omits line/column and packed token metadata, exact error variant/payload, returned borrowed lifetimes, allocation/heap effects, and future scheduling. Token kind projection collapses other token payloads, although functions/comments and block kinds retain the data this contract observes. No byte-list theorem alone discharges machine integer bounds, UTF-8 codec, source immutability, native compiler or memory safety. Progress and DelimiterLaw remain explicit universal premises; this finite match does not prove those providers for all strings.

## Discrimination

Native mutants are applied only inside the exact complete `parse_until_after` body, with a unique old-text match. All six must compile and run successfully, preserve the exact 138-row identity/arity roster, and differ semantically from the model. Mutants run in release so violating an intentional native debug assertion is not mistaken for discrimination. The retained row differences distinguish outer ownership, missing direct advance, missing curly stack cleanup, ignored Stop/error, cache clearing, and suppressed curly URL writes. Parent capsule theorem mutants/axiom audits are separate.

`RENDERER-CORRECTION.json` retains the predecessor's swapped `)`/`}` bit projection and omitted `{` bit. Both authenticated 91-row predecessor debug/release traces have only zero outer masks, so the old finite claim was unaffected. The new renderer follows actual native constants and exercises nonzero enclosing masks. No frozen predecessor or mathematical byte-list theorem was edited.

## Replay

Run `python3 -I -S native/check.py --output ABSENT_EXTERNAL_DIRECTORY` after authenticating the enclosing capsule. The child runner rejects unsafe Python modes before nonbuiltin imports; the root capsule owns closed-manifest authentication. The runner checks exact fixture transfer, full/body source bindings, toolchain hashes, row identity/arity, debug/release model equality, six compiled semantic mutants, and four unsupported provider diagnostics. It does not freeze or modify root-owned proof files.
