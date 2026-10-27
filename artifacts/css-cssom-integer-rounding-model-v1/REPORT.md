# Exact integer CSS-pixel conversion

This Lean model verifies the arithmetic in the sealed Element-local repair-v2 lambda. For a signed32 app-unit input `a`, the candidate promotes before addition, adds +30 for nonnegative input or -30 otherwise, divides by 60 using C++ truncation toward zero, then converts the quotient to signed32. The pinned `AppUnitsPerCSSPixel()` returns 60. No production or canonical-library code is changed.

`trunc60` explicitly implements sign/magnitude truncation; it does not accidentally use Lean's Euclidean division for negative C++ operands. `round` directly composes that division with the source bias. Independent `remainderOracle` decomposes the nonnegative magnitude into quotient and remainder and increments when the remainder is at least 30.

The 21 checked results include:

- `source_matches_remainder`: the source-shaped bias/division equals the independent remainder oracle for every mathematical integer.
- `bias_domain` and `bias_fits64`: every signed32 input gives a numerator in [-2147483678,2147483677], safely within signed64, including INT32_MIN.
- `quotient_domain` and `result_fits32`: every native input gives a quotient in [-35791394,35791394], making the final signed32 conversion representable.
- `integral_identity` and `native_integral_identity`: exact multiples of 60 are preserved; the latter includes source-domain and conversion-range obligations.
- `odd_symmetry` and `native_pair_symmetry`: mathematical sign symmetry, with explicit admissibility of both signed32 inputs for the native version. The mathematical negation of INT32_MIN is not silently treated as a native signed32 argument.
- Positive/negative remainder split and half-tie laws: remainder 30 rounds away from zero for either sign. `nearest_error` bounds error by 30 app units; `zero_band` and `monotone` cover the zero neighborhood and ordered inputs.
- Concrete witnesses return ±8388609 for supplied ±503316540au and ±8947880 for supplied ±536872800au. Endpoint witnesses cover both signed32 extremes and the promoted numerator.

The source correspondence remains explicit and limited: `nscoord` is the signed32 input, promotion and addition have the proved signed64 range, C++ signed division truncates toward zero with positive divisor 60, and the final cast receives the proved signed32 quotient. This is a manual semantic mapping of the actual pinned lambda, not extracted C++ or a compiler correctness proof. The separately sealed actual-header differential compiled and ran under UBSan/integer sanitizers; it corroborates the mapping over its tested inputs, but is not an exhaustive native or IEEE proof.

The target policy is nearest integer with ties away from zero. These theorems do not prove that the historical float implementation gives the same result everywhere, or settle CSS fractional-rounding policy. The candidate intentionally differs at float-induced misroundings. The helper's exhaustive ordinary-domain equality and sampled large-domain differences are separate finite evidence.

The proposed lambda is downstream of existing unzoom and geometry construction. The model exactly converts the signed32 values supplied there; it neither verifies nor repairs earlier zoom, origin addition, fragment union, overflow, offsetParent or shadow-retargeting operations. It does not assume that the browser logged the native input: the retained browser fixture establishes calibrated geometric and integer-observer values, while the native argument itself remains unlogged. The eight additional size cases in the landing WPT still need browser validation.

`check.py` authenticates the proposal, actual-header helper evidence, browser evidence and toolchain; runs Lean using the existing installation; and audits every theorem's axioms. The final replay has no warnings/errors, custom axioms, sorry proofs or compiler products. `lean-initial.log` retains the initial failed elaboration separately. No target directory, native build, browser run, index change or canonical-library edit occurs.
