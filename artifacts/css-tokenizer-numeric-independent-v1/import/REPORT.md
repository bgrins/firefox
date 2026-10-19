# Numeric intermediate-range repair proposal

Status: artifact-only candidate, not a native acceptance or a universal numeric proof. No live native/WPT, Git, Firefox build, or browser operation was performed. Parent owns integration and browser validation.

## Recommended change

`native-candidate.patch` changes only `consume_numeric` in `third_party/rust/cssparser/src/tokenizer.rs` and its vendored checksum. It preserves the existing lexical scan and records its numeric start. It requests reparsing when any of these intermediate computations loses normal range:

- The unsigned integral accumulator becomes nonfinite.
- The fractional decimal factor becomes subnormal or zero.
- The exponent power becomes subnormal, zero, or nonfinite.

At the existing numeric endpoint, before percentage or dimension consumption, the candidate reparses the borrowed numeric prefix with Rust's `f64::from_str`. The old numeric construction then continues. The fallback is triggered by intermediate range loss even when the final old value is finite. Merely checking `!value.is_finite()` is insufficient.

The fractional check is made after the loop's final factor multiplication, so it deliberately reparses some numbers one factor earlier than strictly necessary. There is no arbitrary decimal-length limit. The exponent check also reparses genuinely huge or tiny final values; those retain the existing f32 saturation/underflow behavior.

## Demonstrated payload differences

Here `zeros(n)` denotes exactly n ASCII zero digits; all expected values refer to the complete literal.

| Literal | Old f32 payload | Candidate/reference f32 payload |
|---|---:|---:|
| `5 + zeros(308) + e-309` | infinity | 0.5 |
| `5 + zeros(399) + e-400` | NaN | 0.5 |
| `0. + zeros(399) + 5e399` | NaN | 0.5 |
| `0. + zeros(323) + 5e308` | 0 | 5e-16 |
| `0. + zeros(322) + 5e308` | 4.9406564e-15 | 5e-15 |
| `1 + zeros(300) + e-323` | 9.881313e-24 | 1e-23 |
| `1 + zeros(300) + e-324` | 0 | 1e-24 |

The last four cases demonstrate finite intermediate underflow/inaccuracy. `DECIMAL.json` independently checks their mathematical values using complete decimal strings. The std-library reference is independent of the original multiply/add/pow schedule, but candidate and reference share the same trusted decimal conversion library. This is differential evidence, not an independent proof of that library.

Root's separately retained baseline reproduces the first three opacity discrepancies: 3 failures and 4 passing controls. Copies of the root result and oracle are in `context/`. The additional finite-underflow cases have source-only execution evidence here; no browser observation is claimed for them.

## Grammar and unchanged token behavior

The consumed prefix has an optional sign, digits and/or a decimal point followed by digits, and an optional exponent with optional sign and at least one digit. At least one significand digit is required by the existing caller admission. This is a subset of the documented Rust 1.92 `FromStr` grammar retained in `library/rust-1.92.0-dec2flt.rs`. Uppercase E, leading plus, leading decimal point, and leading zeros are admitted. An incomplete exponent remains outside the consumed numeric prefix. The parse's `unwrap()` relies on that lexical invariant and the library contract; it does not conceal an error by reverting to the known incorrect arithmetic.

The slice is captured before sign consumption and ends before `%` or the identifier suffix. Its bounds are ASCII token boundaries within the existing parser input. Actual `Parser::position`/`slice_from` use SourcePosition and checked debug assertions plus an unchecked slice; this candidate introduces no new cursor advancement. Their native bounds and compiler behavior remain external admission obligations.

Unchanged source controls the integer-versus-number flag, explicit-sign flag, i32 clamp, percentage division by 100 before f32 conversion, Number/Percentage/Dimension selection, and decoded unit consumption. The Rust harness uses the complete original and candidate numeric functions, actual digit helper and corrected identifier-start predicate, with an explicit bounds-checked Parser facade and an ASCII-only name facade. It does not admit the full name/escape provider. Every finite test compares token kind, consumed byte count, sign, i32 metadata, and suffix between versions and against independently specified case boundaries.

Negative zero remains signed through fallback and f32 conversion. Syntactic integers still get an i32 value even when saturated; fractional/exponent syntax still gets None. No attempt is made to change that API or token-level precision.

## Numeric contract and remaining limits

The proposed scope is avoiding separately rounded intermediate range loss for a complete numeric literal whose final payload is representable. CSS Syntax interprets the complete base-ten number; CSS Values allows implementation-defined range/precision. The original three literals are exactly 0.5, which is supported, so overflow of an internal significand does not justify infinity/NaN for their final value. This range-rule application is an explicit inference, retained with primary-source links in `context/static-SPEC-TRACE.md`.

The fallback library documents nearest-representable f64 conversion. Normal-path arithmetic is intentionally unchanged. This proposal does **not** promise universally correctly rounded decimal-to-f32 conversion: ordinary multiply/add rounding, f64-to-f32 double rounding, final range limits, and percentage rounding remain. It does not prove all compiler/platform arithmetic, all native callers, numeric consumer behavior, or the complete tokenizer. The trusted library's implementation is inspected at its entry/dispatch layer, not proved. Its `parse_number`, Eisel-Lemire conversion, and long-mantissa implementation remain external dependencies.

Final multiplication can itself overflow or underflow without activating these guards when both operands are normal. There is no later scale compensation except percentage division by 100: a value beyond f64 range remains far beyond f32 even after that division; an f64-subnormal final value is already below f32 range. This is a payload-domain argument, not a claim of an exact intermediate f64 result. Ordinary rounding near representable boundaries is outside the repair contract.

## Cost and alternatives

The ordinary path keeps its digit-loop arithmetic and pow call. It adds a start-position capture, an integral finiteness check, a fractional threshold check when applicable, an exponent-normality check when applicable, and a final conditional branch. Rare inputs are scanned a second time by `FromStr`; the slice itself borrows existing input and the proposal introduces no new dependency. No allocation, throughput, code-size, or performance-neutrality guarantee is claimed for the library or compiled tokenizer. Typical-input benchmark and platform review remain root decisions before acceptance.

Always parsing the complete numeric substring would simplify conversion and give one consistent f64 conversion policy, but would rescan every number and change normal-path rounding. Parsing all exponent-bearing numbers would also catch these compensated cases, but unnecessarily changes every scientific literal. A final-nonfinite-only fallback demonstrably misses the finite underflow cases. A decimal-length threshold is less directly tied to the arithmetic failure and would need its own conservative bound argument. The proposed structural guards keep current common conversion behavior while covering the identified range-loss mechanisms.

## Evidence and integration boundaries

- Debug and optimized extracted Rust runs: 852 cases each, 300 changed payloads and 552 unchanged; all metadata/boundary assertions pass. Cases cover signed values, percentage and px/em suffixes, i32 boundaries, signed zero, huge exponents, large leading/trailing runs, and ordinary controls.
- For 768 cases the expected payload is the separate complete-prefix Rust parser followed by the unchanged output conversions. The 84 normal-path precision controls instead require exact original/candidate equality; they are not claimed correctly rounded.
- Three semantic mutants compile successfully and fail runtime assertions: final-nonfinite-only guard, missing fractional-subnormal detection, and missing exponent-subnormal detection.
- Exact zero-fuzz patch apply and reverse reproduce the retained two-file candidate and original bytes.
- `check.py --run --output /private/tmp/NEW-DIRECTORY` authenticates, regenerates the harness in isolation, applies/reverses the patch, compiles/runs debug and release, and checks the mutants. Default mode only authenticates and checks source/checksum binding.

This patch is against the current retained tokenizer containing prior URL and escaped-newline corrections. The numeric body is disjoint from those changes, but this package does not claim an upstream-clean checksum patch or an isolated upstream build. Root must produce any standalone upstream checksum variant and final WPT. The frozen static audit and its roadmap remain unchanged; full numeric-provider admission is open.
