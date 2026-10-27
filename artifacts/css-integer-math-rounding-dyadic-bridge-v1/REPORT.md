# A narrow kernel-checked dyadic bridge

This capsule strengthens the mathematical explanation of the reviewed widening expression without introducing an IEEE implementation in Lean. Six support theorems cover exact rational encoding, coefficient capacity and preservation of the zero floor cell under a bounded rounding error. Nothing is integrated into the canonical library, and the earlier nearest-interval theorem is referenced rather than copied or recounted.

For signed mantissa m with |m|≤2^24−1, the central exponent split is:

| Source representation | Exact representation after adding1/2 | Bounds |
| --- | --- | --- |
| m×2^e,0≤e≤7 | (2m×2^e+1)/2 | coefficient magnitude below2^53; denominator2 |
| m/2^k,1≤k≤24 | (m+2^(k−1))/2^k | coefficient magnitude below2^53; denominator at most2^24 |

Both rational equalities are proved for arbitrary exponents; the bounded coefficient theorems quantify over signed mantissas and the respective finite exponent ranges. `central_half_small_dyadic` combines them into an existential rational encoding with a53-bit coefficient and denominator exponent≤24. This is a mathematical sufficient representation, not a Lean floating-point type. Converting this representation to exact binary64 and concluding that correctly rounded addition returns it require the external binary64 encoding/rounding contract. The constructed nonzero values are well inside its normal exponent range.

For normalized binary32 inputs with1/2≤|x|<2^31, the actual decoder supplies precisely such a signed24-bit mantissa and exponent−24…7. That decoder-to-rational correspondence is an explicit premise, not proved here. Central addition is consequently supported by a kernel-checked capacity argument. The endpoint−1/2 is in this case and rounds to0 under positive-infinity ties; anonymous checks retain both signed half ties and the observed±8388609 values. Signed zeros coincide mathematically at the integer boundary; their distinct IEEE encodings are outside the rational representation.

For |x|<1/2, exact addition is intentionally NOT claimed. The capsule proves an exact rational counterexample showing2^−149+1/2 differs from1/2. Binary64 may lose that tiny addend while still producing the correct integer. `zero_cell_error_bound` proves that an approximation whose error is smaller than the distance to either cell boundary remains strictly within(0,1), hence has floor0. Its concrete supplied-premise example uses common scale2^150, gap2^125 and error2^97: real gap2^−25 and error2^−53. The corresponding IEEE facts—binary32 strict-half neighbor gap, representing both sums on that scale and a binary64 rounding-error bound—are not formalized here. This preserves the final floor rather than pretending every addition is exact.

For |x|≥2^31, final signed32 saturation is the relevant boundary. This capsule does not prove that widened addition/floor stays in the required saturation basin. That obligation remains in the separately reviewed all-finite SMT result and its manual source mapping. NaN/infinity normalization, Rust execution/compiler behavior, parser and style-provider wiring remain excluded. No all-finite Lean IEEE proof or new accepted browser fix follows.

Final validation uses the existing Lean4.35.0-rc4 binary with LEAN_NUM_THREADS=2 and a55-second subprocess limit; RESULT records exact command/source/tool/log hashes. All six axiom reports contain only standard logical axioms. Three false controls reject unbounded-mantissa capacity and the wrong positive/negative half-tie answers. Development logs are retained as failed/intermediate attempts, not final proof evidence. No new target directories, native/index/browser or canonical edits; temporary negative-source files are removed.

A full kernel-checked all-finite theorem would additionally need binary32 decoding, binary64 representability and correct-rounding semantics, error bounds, saturation-basin lemmas and their composition. That is substantial IEEE formalization beyond this small support module. The existing Z3 result remains useful independently and is not promoted to a Lean certificate.
