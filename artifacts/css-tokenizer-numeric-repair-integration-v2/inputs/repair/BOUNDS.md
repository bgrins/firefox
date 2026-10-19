# Why 256 bytes is conservative

This is a source-matched range argument with exact-rational checked numerical bounds. It is not a theorem about arbitrary native floating-point implementations or universally correct decimal rounding.

The fallback runs if the consumed numeric prefix has at least 256 bytes or the final f64 value is nonfinite. Thus only prefixes shorter than 256 bytes can skip v1's fallback. A prefix has at most 255 integral digits and at most 255 fractional digits; counting the sign, decimal point and exponent can only reduce these bounds. The source guard counts bytes, and these consumed numeric characters are ASCII. Position subtraction assumes the existing forward cursor/bounds invariant.

## Rounded significand bounds

Use the conservative relative rounding envelope u=2^-52, lo=1-u and hi=1+u for normal finite f64 operations, round to nearest. The conventional unit roundoff is smaller; this envelope has slack. Zero integral operations are exact.

For the integral loop use B(0)=0 and B(n+1)=(10*B(n)+9)*hi². This accounts for both multiplication and addition rounding and the maximum admitted digit 9. Inductively it bounds every digit sequence of length n. `check_bounds.py` verifies every n=0..255, including the intermediate magnitude needed to justify finite normal arithmetic, stays far below f64 overflow.

For the fractional loop, the initial floating 0.1 lies between lo/10 and hi/10. After n factor updates, the exact-rational lower bound is 10^-(n+1)*lo^(2n+1), and the upper bound is 10^-(n+1)*hi^(2n+1). Each update accounts for both the rounded0.1 constant and multiplication rounding. Every lower bound through n=255 exceeds 2^-1022, so none of these factors is subnormal or zero. Multiplying a nonzero digit by the factor remains normal. Zero digits multiply exactly to zero.

The fractional sum is bounded by S(0)=0 and S(n+1)=(S(n)+9*F_hi(n)*hi)*hi, including both term and addition rounding. The rational checker verifies S(n)<2 and `(B(n)+S(n))*hi < 2^853` throughout n=0..255. Independent upper bounds for both loops at 255 also cover any unequal smaller lengths by monotonicity. Applying the sign is exact. This deliberately loose bound covers the rounded accumulators, not merely the mathematical coefficient.

Consequently, a short prefix cannot trigger v1's integral-infinity or fractional-subnormal checks. Its only remaining v1-only trigger is a non-normal exponent factor.

## Exponent cases and output conversion

An infinite or NaN factor produces an infinite or NaN final product (including zero times infinity), so the v2 final-nonfinite guard reparses it. Both versions then use identical Rust f64 parsing and output conversion.

For a zero/subnormal nonnegative factor, the old rounded significand has magnitude below 2^853 and the factor is below 2^-1022. Include relative and absolute subnormal rounding slack: `2^853 * 2^-1022 * hi + 2^-1074 < 2^-168`. This is strictly below half the minimum f32 subnormal,2^-150. Conversion therefore gives signed zero. Division by 100 before conversion cannot increase the nonnegative magnitude; it also gives signed zero for Percentage. This argument explicitly uses the f32 output domain, not equality of intermediate f64 values.

For the robust-parser result, retain the native power classification premise: `powf(10,e)` cannot be zero/subnormal for a nonnegative exponent, and `powf(10,-e)` is normal for integer e=0..307. The existing exponent accumulator represents these small integers exactly; larger decimal exponents cannot round down into that small range. Thus the only remaining case has mathematical exponent at most-308. The exact decimal significand is below 10^255+1, so even with f64 conversion rounding its magnitude is below 2^-150, checked rationally. The same f32 signed-zero result follows, with or without percentage division.

These pow classification and standard IEEE rounding/cast properties are explicit native-library premises. The rational checker does not execute or prove libm, Rust's decimal parser, native cursor arithmetic, or the compiler. It verifies the numerical bounds used to transfer those premises. A libm implementation violating the coarse integer-power classification is outside this argument; ordinary pow approximation/rounding remains an existing boundary.

## Additional reparsing and scope

For prefixes at least 256 bytes, v2 always uses the complete-prefix Rust parser. It may therefore reparse a long finite value which v1 left on the original arithmetic path. The resulting extra precision/rounding changes are intentional; universal v1/v2 bit equality on all long inputs is not claimed. All 852 retained v1 challenges agree with v1's observed candidate results. Short prefixes which neither v1 nor v2 reparses retain exactly the original arithmetic schedule.

The threshold is chosen well inside the above bounds, not inferred solely from the three browser failures or from maximum decimal length of f64. In particular a threshold 512 is unsafe: the retained finite-underflow witnesses would skip reparsing. A compiled512 mutant fails those assertions.
