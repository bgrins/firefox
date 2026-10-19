# Numeric range fallback v2

Status: artifact-only optimization proposal. Sealed v1 remains unchanged. No live native/WPT, Git, Firefox build or browser operation was performed. Native acceptance remains with root.

## Change and scope

The v2 patch preserves the complete existing numeric scan and adds a single end-of-number decision: reparse the borrowed numeric prefix if its length is at least 256 bytes or its computed f64 value is nonfinite. It removes v1's integral, fractional-factor and exponent-factor classifications. Token metadata, percentage division, f32 conversion and unit/suffix dispatch remain unchanged. The exact candidate function is `numeric-candidate.rs`; `native-candidate.patch` contains only the tokenizer change and its checksum.

`BOUNDS.md` derives the256-byte bound with per-operation rounded accumulator envelopes, including fractional0.1 representation and subnormal-product rounding. `check_bounds.py` checks the exact-rational inequalities for every possible short-prefix digit count. For a shorter prefix, intermediate fractional factors stay normal and the rounded coefficient magnitude stays below 2^853. If the exponent factor underflows, both the original output and complete decimal conversion must round to f32 signed zero under the stated power/rounding premises. The argument includes Percentage's prior division by 100. It does not claim f64 intermediate equality.

This closes the finite-underflow hole in a final-nonfinite-only fallback without checking every intermediate in the common path. Long prefixes always use Rust decimal conversion, so some finite long values outside v1's fallback set can change rounding. Short ordinary paths keep their original arithmetic. All 852 v1 cases retain their v1 candidate results.

The borrowed prefix is parsed before `%` or dimension-name consumption. Its CSS grammar is a subset of Rust's documented f64 FromStr grammar, retained under `library/`; `unwrap()` relies on that source/caller invariant. No invalid-prefix recovery or complete tokenizer proof is claimed.

## Source-only verification

- Complete original and v2 numeric functions, actual digit helper and identifier-start predicate, isolated Parser/ASCII-name facades.
- Debug and release runs: 852 cases, 300 changes versus original and 552 unchanged, exactly matching v1. Independent token metadata/cursor checks pass. 768 payloads require the complete-prefix Rust reference; 84 ordinary precision controls require original equality.
- Three semantic mutants compile and fail runtime assertions: omit length guard, raise threshold to512, omit final-nonfinite guard.
- Exact zero-fuzz apply/reverse matches the retained two-file original/candidate sources.
- Exact-rational bounds include all digit counts 0..255 and rounding envelopes, not just exact mathematical coefficients.
- `DECIMAL.json` preserves independent complete-decimal goldens. Root's original browser witness is copied under `context/`; no browser execution of v2 is claimed here.

Run `python3 check.py --run --output /private/tmp/NEW-DIRECTORY` for fresh isolated source/checksum authentication, regeneration, patch apply/reverse, rational checks, debug/release comparison and mutants. Rust 1.92.0/aarch64-apple-darwin is the recorded toolchain.

## Cost evidence and decision

The ordinary path still adds numeric-start retention, a prefix-length comparison, a final nonfinite classification and a conditional branch. Rare inputs incur a second numeric parse. There is no performance-neutrality claim, no heap-allocation guarantee for the library and no browser throughput estimate.

The separate reviewer benchmark wraps the unchanged full functions in allocation-free noinline adapters, uses black_box, six inputs/group,400k loops, nine alternating samples and excludes the first sample. Root relayed its first v2 result for exact function SHA 4900531c70d9e034e02e2a002c569858843ce6e43f20f835b24be01128d04fb9: integers 4.82→5.34ns(+10.8%), fractions 4.78→5.51ns(+15.2%), exponents 7.48→7.76ns(+3.8%). This is preliminary extracted microbenchmark evidence, not Firefox measurement. Independent raw receipts/repeat belong to that reviewer's capsule; this report does not manufacture a local timing receipt.

V2 reduces the number of intermediate classifications and improves the relayed fraction/exponent costs relative to v1, but leaves measurable overhead. Root requested finishing this bounded proposal rather than pursuing unbounded optimization. The tradeoff remains a review decision; no recommendation to commit before accepting the residual cost is implied.

## Limits preserved

Rust decimal conversion, coarse libm integer-power classification, standard f64 rounding and f32 cast behavior remain admitted primitives. The numeric lexical/cursor invariant and complete name/escape/compiler correspondence remain external. Ordinary rounding, f64-to-f32 double rounding, final representability and percentage rounding are not universally proved. The exact-rational computation is not a Lean kernel proof or a native arithmetic proof. This package does not close full tokenizer/provider scope.

The patch base includes prior URL and escaped-newline corrections. Only the numeric body and checksum change here; upstream-clean checksum packaging and native/browser validation remain root-owned.

## Benchmark comment delta

At root’s request the final native guard has a two-line rationale. `BENCHMARK-DELTA.json` and the checker verify that removing exactly those comments reproduces the benchmarked function byte-for-byte. The final checksum/patch are updated; no timing is attributed to an unverified executable-source change. The final candidate replay uses the commented source. Public prior-art search was root-owned and does not establish novelty.
