# Finite scaled weights and ordered accumulation

All five clauses of the frozen `FullWeightTarget` pass Coq compilation and an independent combined `coqchk` replay. Six exact root audits use only the four standard Coq real/classical assumptions recorded by `validate.py`. The single generated rewrite hypothesis is replaced by a checked ring proof. No Lean axiom or existing target was changed.

## Bounds

The product theorem admits every real factor in `[0,2^128]` and base in `[0,2^31]`. The exact product and binary64-rounded product stay in `[0,2^159]`. These intervals include nonnegative finite binary32 factors and nonnegative signed32 bases; the extra endpoints are conservative overapproximations.

The addition theorem admits a current sum in `[0,2^192]` and weight in `[0,2^159]`. It proves that the exact sum and rounded next sum stay in `[0,2^193]`, and that the rounded next sum is no larger than the previous sum plus `2^160`.

The ordered accumulation theorem uses the actual left-fold order, starting at zero. For every list of at most 4,294,967,295 admitted weights, the computed sum is nonnegative and at most `length * 2^160`. The prefix theorem establishes `[0,2^192]` for every `firstn` prefix, including the empty and complete list. Its inductive invariant derives each next addition's input bound; no assumption bounds the final sum in advance. The factor-sum theorem applies the same ordered bound to factors in `[0,2^128]`.

These bounds are well below binary64 overflow. Gappa/Flocq's real-valued floating-point format does not impose a maximum exponent, so the explicit bounds on both exact intermediates and rounded results matter when relating the model to IEEE arithmetic.

## Native interpretation

The corrected `FlexItem::GetWeight` promotes the shrink factor before multiplication and returns double. The product theorem models that corrected arithmetic. It does not apply to the old binary32 multiplication whose overflow was confirmed in the separate browser regression artifact.

To apply the accumulation theorem to native execution, the caller must establish the ordered input list and its scalar bounds. Nonnegative bases must be established for active shrinking items, not assumed for all flex items: `FreezeItemsEarly(false)` freezes a base smaller than the hypothetical size, and valid hypothetical sizes are nonnegative. The caller proof campaign has checked the initial active-item version of that argument; history preservation and concrete source acquisition remain separate.

For grow weights and the flex-factor sum, native binary32 representation and computed-value rules still need to be tied to the admitted real factor interval. Exact promotion of the integer base/factor, source-to-model correspondence, runtime floating-point configuration and compiled-execution correspondence are not proved here. The source/object audit in the separate rounding artifact remains supporting inspection evidence.

The theorem concerns finite nonnegative inputs. Genuine infinite factors and their largest-weight fallback remain covered by separate caller/distribution obligations. This artifact does not prove the finite share ratio bound, nor silently assume that an arbitrary admitted real input already has binary64 representation. That distinction matters when proving rounded-sum monotonicity and share division next.

## Reproduction and evidence

`queries/Product.g` and `queries/Addition.g` are the two Gappa inputs. `generated` preserves the original certificates; `inputs/Addition.v` changes only the rewrite hypothesis into a ring lemma and adds the tactic import. `WeightTarget.v` fixes the five required results before proof checking. `Weights.v` proves the numerical interfaces and the ordered/prefix/factor accumulation results.

The first design expressed the 32-bit count limit as a unary `nat` literal. Before any compilation or proof check, the bound was restated as `Z.of_nat(length) <= 4294967295` to avoid expanding that large unary numeral. The admitted list lengths are unchanged. `design-1` and `DESIGN-REVISION.json` preserve this representation change and both hashes. Neither proof attempt altered the resulting target.

Attempt 1 failed on presentation of generated interval endpoints in the product wrapper. Attempt 2 passed four module compilations and the combined independent replay. Its container was removed, including all temporary compiled proof objects. `launch.py N` creates a fresh snapshot and checks the target hash before using the pinned isolated checker image; `validate.py` authenticates the accepted source, certificates, exact command roster and audits.

No new browser bug or native change is claimed. This is additional mathematical evidence for the existing finite-weight repair, not a replacement for its native correspondence review or WPT results.
