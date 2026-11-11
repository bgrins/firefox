# Independent numeric execution evidence review

The completed isolated run supports its bounded lexical comparison claim. I independently replayed the frozen comparator and authenticated the source/build/log/model evidence before scratch cleanup. No blocking inconsistency was found in the actual observations. This adds finite native evidence to the prior Lean model bridge; it is not a native refinement theorem, production-feature parity, a floating-point correctness result, or a new Firefox bug.

## Authenticated execution

`audit.py`/`AUDIT.json` record the independent checks. All 64 materialized Git objects match both the source materialization and the two built source trees. The instrumented tokenizer differs by exactly the frozen seven insertion sites; all other materialized dependency bytes and the Rust driver match. The trace-generation function reverses to the original repaired tokenizer source. Its pin includes the prior compensated-exponent repair; historical broken payload expectations are not being asserted against current source.

Both variants have six successful direct-rustc commands (five libraries and the driver). I verified the 12 resulting output hashes, including both executable hashes in RESULT.json, and retained them in BUILD-ARTIFACTS.json. The compiler binary matches its pinned SHA. Commands use opt-level=1 and no feature cfg flags. Warnings, including the recorded SDK-discovery diagnostic, remain in the command receipts; all compile and execution exits are zero. These records do not pin every host linker/SDK/sysroot component or establish Gecko-build equivalence.

All 50 top-level command stdout/stderr hashes and exits match their retained logs. Forty-four model modules match the accepted source manifest and their exact accepted build-output hashes, including known preserved warnings. The actual command executes `Runner.lean` with the pinned number.json and generated model-input.json. The runner reads the supplied JSON program and executes its lowered parser, then observes returned parts/state; it does not substitute a precomputed reference row. The established theorem connects this fixed JSON value to the independent byte reference under its ASCII caller premise. The prose/spec interpretation and Rust-to-model mapping are still separate trusted/manual boundaries.

I did not rebuild or rerun either native binary, and did not mutate the original execution or scratch. The independent action was source/log authentication, comparator execution into this review directory, and in-memory record controls. All required original evidence is retained outside scratch; root was notified that scratch cleanup can proceed. The pre-cleanup audit script needs the original scratch to recheck binaries, whereas comparator replay needs only the retained logs and source protocol.

## Exact counts and meaning

| Evidence | Actual count | Scope |
| --- | ---: | --- |
| Cases | 196 | 84 inherited single reads plus 112 augmented histories. |
| Public records per native variant | 644 | 196 cold reads and 112 each cached, suffix, reparsed, suffix-replay reads. |
| Admitted JSON model inputs | 180 | 76 single cases and 104 history cases. |
| Native/model lexical comparisons | 284 | Every admitted cold read plus each admitted reparse. |
| Excluded model cases | 16 | Eight off-domain legacy tails, each retained as single and history; native transparency/reset controls only. |
| Nonzero UTF-8-prefix cases | 20 | Native absolute byte-start calibration; prefix is not passed to the ASCII model. |
| Numeric traces | 316 | 196 cold, zero cached, 112 reparsed, four suffix and four suffix-replay traces. |

The 284 modeled traces plus 24 off-domain cold/reparse traces plus eight numeric suffix traces account for all 316. Cold public tokens comprise 48 numbers, 136 dimensions and 12 percentages. Counts are per input/phase, not independent CSS features or bug findings. The old nine scanner controls are archived but are not part of this driver.

The seven exact comparisons are consumed numeric-core bytes, core remainder, integral/fraction/exponent digit runs, outer sign presence and lexical integer classification. Slice positions are checked against the actual source, and the numeric-core end is bounded by the whole-token end. This correctly keeps cases such as `1e+` separate: core remainder and dimension-token remainder differ. Full token kind/unit/value/location fields are compared across instrumentation and reset observations, not all against a new independent token oracle.

The histories genuinely force another successful token read before resetting. Trace counts show no numeric call on the cache hit and a new call on reparse. That is stronger than merely observing an unchanged cursor. It remains a bounded history under the specified initial boundary; hidden parser state, arbitrary nesting, stop delimiters and all observer histories are not formally verified.

## Comparator hardening gap, not an invalid actual run

Root flagged Python Boolean/integer equality as a prospective malformed-input issue. I independently verified all 180 actual model rows using exact types: outer list/string/Boolean fields, seven observation columns, five lists containing only exact int values in 0..127 (excluding bool), and two exact Boolean columns. Every observed row passes.

An independent in-memory control replacing the first model observation's Boolean with integer 0 is accepted by the current comparator. This is a protocol schema-hardening gap because Python equality identifies False with 0. It does not invalidate the pinned, correctly typed output used in this execution. Before treating the comparator as a reusable input-validation boundary, add explicit exact-type/range/shape validation and negative controls in a new protocol revision; replay the unchanged captured rows. No native rerun is needed merely to demonstrate that parser-only correction.

Eight other independent mutations of captured records were rejected: sign loss, wrong integer classification, missing model row, invented cached trace, missing cold trace, reset end change and either model-error Boolean becoming true. These are record-corruption controls, not compiled native mutants. The error flag belongs to the model; no corresponding native error Boolean was measured.

A control changing every corresponding public float-bits field to deadbeef remains accepted, as intended by the declared lexical scope. Instrumented/uninstrumented and reset bit equality demonstrate transparency, not correct numeric conversion. Actual mathematical sign, rounding, overflow/underflow, percentage scaling, integer saturation and property clamping still lack a new numerical oracle here. Debug token strings are also same-implementation observations, not an independent numeric specification.

## Practical next gates

1. Harden the comparator's model-row schema, then execute a few compiling native semantic mutants in new isolated outputs. Alter a real outer-sign or exponent-integer-classification operation and a real saved-prefix/reset boundary; require compilation, a specific affected witness and rejection by the appropriate comparison layer. Changing only log text or trace metadata is not an adequate native sensitivity test. Keep mutation failures separate from compiler errors, crashes and malformed instrumentation. The older compiled fallback-slice witness remains prior evidence, not a newly executed control for this driver.
2. Prepare the offline Cargo/default-feature experiment described by FEATURE-PLAN.json. Pin the dependency lock and every resolved source, enable fast_match_byte and fast_match_color, record the actual Cargo feature tree and compiler/target settings, and run paired plain/instrumented variants against the same 196 inputs and 180 model rows. Compare the new observations to this inherited no-feature run. Current commands deliberately bypass Cargo and disable those defaults, so equivalence cannot be inferred from this PASS.
3. Only after those gates, decide whether broader token/UTF-8 histories or numerical payload correctness is the more useful next target. Full Gecko parity additionally requires its actual feature union, optimization/LTO, target and runtime configuration; a default-feature standalone crate still is not a browser build. The exact lexical bridge does not automatically solve IEEE behavior.

No original artifact was changed. EVIDENCE-HASHES.json binds all retained execution files as reviewed; INPUTS.json and SOURCES.json bind protocol/model/materialized sources; BUILD-ARTIFACTS.json preserves compiled output hashes before cleanup. COMPARISON.json is the independent CLI replay result.
