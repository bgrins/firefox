# Independent final numeric v2 review

## Verdict

Approve the exact sealed v2 source proposal for root integration and browser/build gates under the stated native contracts. No correctness blocker was found in the guarded fallback or its 256-byte bound. This is source review plus checked rational bounds and bounded native execution, not a Lean proof of IEEE arithmetic, Rust conversion or complete numeric correctness. The known extracted normal-path cost remains a tradeoff; no new benchmark was run.

Producer FREEZE fa8cefc1a301a8ddca2231f495a8a90b04f80d83f6c7f741d01a0eaf902966ad and INPUTS1766f73914b19f56f0e3a5ae9c89300b7290a5ea1b81ee5e9831f9a9b966c516 authenticate51inputs. Native patch0591cb8c635623862cd392ffc1f2abb5aef769a4d433285bdc5b40138405656d changes only the complete numeric function and its checksum. The final function4621d5c7... differs from the timed4900531c... body only by the exact two comments; this was independently checked, not inferred from a diff label.

## Integral and fraction inductions

The short-prefix limit permits at most255 digits in either loop. Sign, point and exponent bytes only reduce these upper bounds. The proof need not assume equal integral/fraction lengths.

For u=2^-52 and hi=1+u, each nonzero integral step is bounded by (10*B+9)*hi²: the first factor covers multiplication and the second addition, with 9 the maximum admitted digit. Zero operations are exact. Monotonicity of positive arithmetic and nearest rounding transfers the max-digit recurrence to every admitted digit sequence. Intermediate exact values are far below overflow; nonzero integer operations cannot be subnormal. Thus applying the normal rounding envelope is not circular.

The factor bounds include both the rounded0.1 constant and each multiplication. The next exact product's lower bound exceeds minimum normal before applying its rounding envelope. The independent checker tests this prerequisite separately. Each nonzero digit-times-factor term is normal; zero terms are exact. A nonzero accumulated sum is at least a normal term, so addition also admits the envelope. Fractional sum upper bounds include both term and addition rounding and stay below2.

The producer recurrence and the independent closed geometric-series calculation agree. The independent checker derives B(n) and S(n) from their series formulas, verifies the step identities, monotonicity and exact-product bounds through255, then uses independent maxima B(255),S(255) for any unequal loop lengths. Their sum with final addition rounding is below2^853. This verifies finite arithmetic bound constants and finite index induction obligations; it does not mechanize the actual machine-rounding relation.

## Exponents and skipped fallback

A short prefix cannot lose integral range or fractional-factor normality. If the exponent power is normal and the product finite, v1 and v2 both preserve the original arithmetic. If the product is nonfinite, v2 reparses the complete prefix, covering infinity, NaN and zero times infinity. Reparse is identical to v1 where both trigger.

The only v1-only trigger on a short prefix is a nonnegative subnormal or zero exponent factor with finite product. The native rounded coefficient bound and a conservative absolute subnormal-rounding allowance give magnitude below2^-168, strictly below half the minimum f32 subnormal2^-150. This is about final output, not equal intermediate f64 values.

To establish that the complete-prefix parser also returns a value casting to zero, the proof explicitly assumes base-ten pow classification: nonnegative exponents do not yield zero/subnormal, and negative integer magnitudes0..307 yield normal powers. The exponent digit accumulator represents the small range exactly; a larger nonnegative integer cannot round down into it, using monotonic positive integer accumulation. Large exact integers may be rounded or become infinity, but cannot invalidate that coarse separation. Therefore any zero/subnormal power here corresponds to an exact exponent at most-308. The exact decimal coefficient is below10^255+1, giving the checked bound below2^-150 even after f64 rounding allowance.

Positive-base powers and ordinary IEEE signed operations preserve the literal sign, including signed zero. Rust's retained converter applies the parsed sign to its result. Division by100 cannot increase the magnitude of a nonnegative representable input under nearest rounding, and preserves zero sign. Thus Percentage as well as Number/Dimension reaches the same signed f32 zero. The untouched integer tag is None for exponent syntax; plain short integers cannot enter this subnormal-power case. This avoids any hidden i32 or percentage exception.

## Native and lexical review

Start capture precedes sign consumption. The guard computes forward cursor difference before percentage/name consumption; the ASCII prefix grammar is the same admitted subset of FromStr reviewed for v1. No cursor advance, suffix decoding, integer tag, sign flag, i32 clamp or percentage conversion was changed. The complete function and one-function patch/checksum binding were inspected. usize bounds and valid initial positions remain native admissions. An invalid direct call with no significand digit is outside the existing dispatch contract.

At least256 bytes always reparses, including some finite values v1 retained. This intentionally permits additional precision changes on long values; no all-input v1/v2 bit-equivalence claim is made. Ordinary multiply/add/pow rounding, f64→f32 double rounding and final range limits remain. The argument requires nearest IEEE arithmetic/casts, coarse libm power classification, correct full-prefix conversion, positive-base sign behavior and normal completion. The rational checker cannot prove those library/compiler premises.

## Replays and cost

Fresh relocated producer replay verifies all51inputs, whole function/checksum, exact patch apply/reverse, rational bounds, debug and release852cases (300 changed/552unchanged), and three compiled mutants rejected at runtime. The final commented body also passes the unchanged independent504challenge corpus. Those runners use explicit Parser/ASCII-name facades; they do not execute the full native provider/heap/caller graph.

The earlier v2 benchmark checkpoint was authenticated. Its two same-protocol runs showed integer overhead10.8%/13.6%, fractional15.2%/17.7%, exponent3.8%/4.8%, roughly0.3–0.85ns/token in that setup. The final source changes comments only. These are isolated arm64 Rust1.92 optimized-body measurements without Gecko PGO/LTO, not browser measurements or confidence bounds. The independent v1 and v2 artifacts remain immutable.

Root owns build/browser gates. This review neither claims those gates passed nor turns finite tests into complete numeric verification.
