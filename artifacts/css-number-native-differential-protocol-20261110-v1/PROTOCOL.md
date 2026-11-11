# Proposed native number comparison

Status: source and protocol prepared, not compiled or run. Root review is required before native execution. This capsule does not report a new native bug or a new native refinement proof.

## Source and model

The native source is pinned to Firefox `ec467c0219d3d5daf70f42fcc53677cf8a262173`. Its tokenizer SHA-256 remains `5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211`, including the already fixed compensated-exponent fallback. Searchfox discovery preceded local pinned-source reads; the indexed [numeric consumer](https://searchfox.org/firefox-main/rev/5a3f6397e61554eda92b0ec63ddd0ff752a22da2/third_party/rust/cssparser/src/tokenizer.rs#1048) predates that local fix. Exact Git objects govern this proposal, not the older indexed implementation.

`MODEL.json` pins the completed JSON-to-lexical Lean milestone. The seven compared columns are the **new numeric-core observation**, not the differently shaped seven-column full-token projection from the original numeric-admission harness:

| Native trace | JSON runner observation |
|---|---|
| Saved original number prefix bytes | `consumed` character codes |
| Source bytes after numeric core | `rest` character codes |
| Native integral-loop byte span | `integerDigits` |
| Native fraction-loop byte span | `fractionDigits` |
| Native exponent-loop byte span | `exponentDigits` |
| Native outer `has_sign` | `hasSign` |
| Native lexical `is_integer` | `isInteger` |

All seven compare exactly only for normalized ASCII **tails** admitted by the prior theorem. The optional earlier UTF-8 prefix is consumed as a quoted string plus whitespace by the native parser and is not passed through the ASCII Lean adapter. Its absolute UTF-8 byte length is checked separately. This supplies finite offset calibration, not a general UTF-8/UTF-16 representation theorem.

`Runner.lean` must receive the pinned actual `number.json` and `prepared/model-input.json`. It executes the decoded typed program through existing lowering. `prepared/model-ids.json` fixes row order; the model's initial and resulting error flags must both be false. There is no corresponding native error-Boolean column. Native token errors/panics make the run fail separately.

## Reuse and bounded new cases

`inputs/legacy-cases.json` retains the original 90 rows: 81 numeric and nine scanner controls. The new native driver uses all 81 numeric rows, plus the three original nonzero-UTF-8 capture cases, preserving the exact inherited 84-input baseline. The nine scanner controls remain archived; the driver deliberately does not extract Stylo custom-property scanning code or introduce its handwritten substitution-function shim.

Each inherited input also gets a distinct history case with the exact suffix ` ;q` appended. Both its native input and its model input include this suffix. The original baseline remains unchanged. There are 28 additional history cases for incomplete exponent/unit boundaries and total numeric-prefix lengths 254–257, each at zero and nonzero UTF-8 starts. All 196 cases, exact augmented strings and admission labels are materialized in `prepared/CASES.json`.

Eight inherited inputs contain non-ASCII, NUL, CR or FF suffixes. They remain as native-only baseline controls and native-only history controls, yielding 16 excluded rows. They are not silently normalized or passed to the new ASCII bridge. Thus 180 planned cases have JSON comparison rows; successful complete execution would make 284 core comparisons across cold/reparsed phases. These are planned counts, not runtime results.

Historical `payload_bits` expectations are preserved only as archival input metadata. In particular, an old overflow witness predates the local numeric repair. This proposal never treats those stale payload expectations as an oracle.

## Instrumentation and replay

`tokenizer-trace.patch` adds seven insertion sites within the existing `consume_numeric` function. It records positions at the native loop boundaries and emits one trace at the previously used saved-prefix capture point, before numeric fallback/value publication and unit/percent dispatch. It does not add a replacement numeric scanner or reparse the prefix with a regular expression. Reversing the insertions reproduces the entire original tokenizer exactly. The borrowed slices are checked against the recorded source and offsets by `compare.py`.

The driver clones the returned public token before inspecting parser position. A single case makes one `cold` call. A history case performs:

1. Save the parser state at the exact numeric boundary; read `cold`.
2. Reset that same parser to the saved state; read `cached`. Expect identical public token/state and **zero** calls to `consume_numeric` because the cached token can be reused.
3. Read exactly one `suffix` token, requiring successful forward progress. The appended sentinel prevents an EOF-only read from being mistaken for cache eviction.
4. Reset to the original saved state; read `reparsed`. Expect the original public result and one fresh numeric trace.
5. Read `suffix-replay`; expect the same following token/state as in step 3.

Every actual next-token call is bracketed by `CALL`/`END` stderr records. This associates traces with the correct phase even when the following token is also numeric. The comparator requires exactly one numeric trace for uncached numeric calls, none for cached calls, and none for other-token calls. It does not force a trace for a cache hit or infer re-execution from an unchanged cursor.

The initial numeric boundary has no pending block and no enclosing stop delimiter. The driver does not traverse arbitrary nested blocks or assert termination/correctness of unrestricted parser/observer histories. A following block opener is only observed once; resetting restores the pre-number state before replay.

## Public token and payload boundaries

Public rows include kind, decoded unit bytes, whole-token end/remainder, sign presence, `int_value.is_some()`, payload bits, token debug representation and source location. The **whole-token** end is not compared to the numeric-core end: `1e+` is a dimension with unit `e` while the numeric core ends after `1`. The native trace must remain within the public token's consumed interval.

The new comparison does not rerun the older unit-flag or custom-property-scanner contracts. Public token fields are compared between instrumented and uninstrumented builds and across reset phases. Previously proved token/name composition remains prior work; this protocol does not claim a new all-token native refinement theorem.

Float bits are recorded with no exact-rational or Lean floating-point oracle. Equality between two executions of the same native input checks instrumentation/reset transparency, not correct rounding. The synthetic protocol test intentionally changes all corresponding payload bits to `deadbeef` and still passes the lexical comparison. Percentage scaling, integer saturation and CSSOM/property clamping remain outside the seven-field contract.

## Build and feature gates

`materialize.py` copies only 64 hash-bound Git objects into a new isolated directory. `build.py` preserves the accepted direct-rustc dependency recipe and compiler hash, uses a separate output directory for each variant, and records every command. It has no network operations and does not execute the resulting binary. No source, objdir or dependency storage in the live Firefox checkout is modified.

This first recipe has `fast_match_byte` and `fast_match_color` disabled, exactly as the earlier standalone harness. It removes the unneeded scanner/bitflags layer. This mode is useful continuity evidence; it is not a default-feature or full Gecko build.

`FEATURE-PLAN.json` states the next required gate: an isolated offline Cargo workspace with a frozen dependency lock and default `fast_match_byte`/`fast_match_color` enabled, paired instrumented/uninstrumented runs, and exact lexical agreement against the same JSON observations and historical-mode rows. The source package declares these defaults, and Stylo's dependency does not disable them. The actual Gecko workspace feature union, target, LTO/optimization and allocator configuration must be recorded separately before claiming browser-build parity.

The default-feature Cargo recipe/lock is **not implemented or resolved here**. This is an explicit remaining integration gate, not inferred equivalence. The proposal is ready for review of the instrumentation, protocol and inherited build mode; it is not a claim that every planned build configuration is ready or tested.

## Proposed execution after review

First authenticate `PINS.json`, `MATERIALIZE.json`, `MODEL.json` and the source allowlist. Then materialize a fresh source directory and build two separate inherited-mode outputs, one with `--instrumented`. Feed each binary the identical `prepared/native-input.tsv`, retaining complete stdout/stderr and exit status. Do not filter either stream. Generate the 180 model rows with the pinned bridge runner and the exact model corpus, using a fresh owned Lean build closure.

Run `compare.py` with the prepared cases, both public outputs, both trace outputs and actual JSON-runner output. Require native exit zero, all expected rows/phases, exact instrumented/uninstrumented public equality, exact slice/source agreement, reset/suffix equality and the admitted model comparisons. Retain source hashes, command lines and outputs before deleting owned native/Lean build directories.

Before broadening input domains, compile and execute sensitivity controls for lost native sign/type, incorrect saved-prefix extent and changed reset/end behavior. Existing compiled fallback-slice failure is prior evidence, not a new executed control. Then complete the default-feature gate. Investigate any mismatch using the independent grammar/caller boundary before treating it as a Firefox bug or adding a WPT.

## Current validation only

`check.py` performs static Python parsing, input-hash authentication, exact instrumentation/patch reconstruction, deterministic corpus regeneration and synthetic protocol checks. Eight synthetic corruptions are refused, including a scalar-count substitution for a UTF-8 start and an invented numeric trace on a cache hit. Synthetic wire records roundtrip through the actual parsers, and payload bits have no numeric oracle. These controls test the protocol code; they are not compiled Rust mutants or native observations.

No Rust compiler, Cargo resolver, native binary, browser or new Lean model corpus has been run for this proposal. The full native build/execution and feature gates await review.
