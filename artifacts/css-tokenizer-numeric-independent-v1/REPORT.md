# Independent numeric repair v1 review

## Decision

The sealed two-file proposal is suitable as a correctness repair for the identified intermediate range-loss mechanisms, subject to the native/library admissions below. No source-level correctness blocker was found. Recommend revising its normal-path cost before integration: two extracted release benchmark runs show a repeatable overhead. Root has not applied this candidate and is preparing a separate v2. This review does not accept universal numeric correctness or browser performance.

Authenticated producer FREEZE 35e217b262d26fe09f3d74166f4d9a698dfdbbca085f750fef118d0a8e4a170d, INPUTS 2559cfe8afcc921c4ddb0acb0574af49e515a7e70b66dc133d02f65a99af40d1, 45 entries. The earlier draft snapshots used in initial independent checks exactly match final sealed inputs. No producer artifact was changed.

## Complete function and grammar

The full consume_numeric body, its calling guard/digit helper, actual position/slice helper definitions in the complete tokenizer, and the retained Rust 1.92 decimal-conversion entry were inspected. Searchfox discovery found its four dispatch call sites. The existing caller admits a significand containing a digit; optional sign, fractional digits and exponent digits are scanned with unchanged lookahead. The consumed prefix is ASCII and satisfies the documented Rust f64 FromStr grammar. Incomplete exponent text is excluded by the existing digit lookahead. Capturing start before sign and slicing at the numeric endpoint therefore supplies the full signed prefix without percent, unit or following punctuation. `unwrap` depends on these native admission and library contracts; it is not an independently proved Rust parser theorem.

The new guards change no cursor advancement or lexical metadata. Reparse precedes integer clamping and suffix selection. Syntactic integers retain Some(i32) with the original clamps; decimal/exponent syntax retains None. Explicit signs remain lexical. Signed zero is preserved by the trusted converter and subsequent conversions. Percentages divide the f64 value by 100 before f32 conversion; dimensions and numbers cast directly. The numeric correction does not bypass name decoding or change its separate provider semantics.

## Guard analysis

Integral overflow can occur before a negative exponent restores a representable value. Fractional decimal factors can become subnormal or zero before a positive exponent restores magnitude. Exponent powers can become subnormal or zero before multiplication by a large integral value. All three paths are guarded in v1. The post-loop fractional check conservatively triggers one factor earlier than necessary. The exponent guard also catches zero times infinity and huge finite mantissas times zero. Negative cases share the magnitude calculation and preserve sign.

Checking only the final value for nonfiniteness misses finite but wrong underflow results. The retained source mutants demonstrate that both subnormal checks matter. Final multiply overflow/underflow with two normal operands is not a compensated intermediate in this function: only percentage division remains. A value beyond f64 range remains beyond f32 range after dividing by 100, and a subnormal f64 final value is below f32 range. This argument does not prove rounding correctness. Normal arithmetic still has the existing rounding schedule; fallback can have f64-to-f32 double rounding. Library `powf`, decimal conversion, IEEE/compiler behavior, input bounds and heap remain trusted or conditional.

The proposed future length guard must independently bound significand magnitude under its threshold, fractional factor loss, and subnormal exponent compensation. A finite-final-value shortcut without those bounds is insufficient. No such replacement is approved in this v1 review.

## Independent executions

Fresh relocated producer replay passed: debug and release each 852 cases (300 changed payloads, 552 unchanged), exact patch apply/reverse, source/checksum binding, and three successfully compiled then rejected semantic mutants. Its 84 ordinary controls assert preservation, not correct rounding; candidate and reference share Rust FromStr on fallback cases.

The independent challenge adds 504 fixed cases spanning signed zero, positive/negative/explicit-plus values, normal and compensated long significands, extreme exponent cancellation, percentages, px, and incomplete exponent or punctuation suffixes. Expected numeric values come from complete-prefix FromStr; lexical cursor/kind/sign/None metadata and suffix boundaries are specified independently. All pass. This is bounded evidence, not universal floating-point proof.

Both runners retain complete numeric bodies. The bounds-checked Parser facade and ASCII-only consume_name replace the native providers. The independent runner removes that facade's assertion restricting trailing punctuation so e+, e-, and dot suffix controls can execute. It does not claim coverage of full Unicode/escaped name semantics, SourcePosition width, actual unsafe slicing, or arbitrary native initial states. No native Gecko build or browser was run by this reviewer. Root's three-failure/four-control browser baseline is separate retained evidence; expanded browser results were pending during this review.

## Release microbenchmark

Source-bound benchmark uses identical complete numeric bodies, an allocation-free wrapper, black-boxed inputs/results, noinline entry wrappers, alternating variant order, nine samples per group, and 2.4 million calls per sample. Medians exclude each variant's first sample. Exact inputs, compiler identity, generator and all raw samples are retained.

| Group | Run 1 original → candidate ns/token | Run 2 original → candidate ns/token |
|---|---:|---:|
| integers | 4.67 → 5.19 (+11.2%) | 7.18 → 7.78 (+8.3%) |
| fractions | 4.80 → 5.94 (+23.6%) | 7.15 → 8.52 (+19.1%) |
| exponents | 7.41 → 8.06 (+8.8%) | 7.95 → 8.46 (+6.4%) |

The repeated direction supports a normal-path cost in this isolated setup, roughly 0.5–1.4 ns/token. Absolute speed changed substantially between runs; this is not a confidence interval, a stable browser cost, or a whole parser throughput claim. CPU scheduling/frequency, instruction layout, simplified provider code and compilation settings limit extrapolation. Rust 1.92 release optimization on arm64 is pinned, without Gecko PGO/LTO. No thresholds turn these timings into a pass/fail gate.

## Primary sources and limits

CSS Syntax 3 [consume a number](https://drafts.csswg.org/css-syntax-3/#consume-number) and Rust [f64 FromStr](https://doc.rust-lang.org/std/primitive.f64.html#impl-FromStr-for-f64) were read on 2026-10-19. CSS consumes decimal components before interpreting their value; Rust admits the consumed grammar. The supported final value 0.5 supplies the clear regression oracle; intermediate overflow does not justify a different final value. Current Rust documentation is corroborative; the retained 1.92 source is the tested converter version. This review does not archive the current HTML or prove the library implementation.

The existing conditional model does not become a universal numeric proof through these tests. Precise claims here concern the source delta, its admitted grammar, bounded execution results, and measured isolated cost. No novelty or full tokenizer verification claim is made.
