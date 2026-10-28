# Conditional reconstruction/projection argument

Let `a=|value|` and `b=|step|>0` be finite binary32 magnitudes. Supply the **truncating** remainder contract `a=q*b+r`, integer `q>=0`, `0<=r<b`, with the source remainder carrying the input sign. Existing exact remainder-capacity and binary32 decoder results supply mathematical remainder representability; this capsule does not establish that Rust `%` returns it. Write `RN64`, `RD64`, `RU64` for binary64 nearest-even, downward and upward rounding, and `P` for nearest-even binary32 projection with signed overflow. Binary32 promotion and multiplication by2 or2^-28 are exact within binary64's normal range; these justify the reference comparisons and threshold in the queries.

## Exhaustive domain accounting

1. **Zero input or any exact multiple:** the true truncating remainder is zero. The source returns the original input before reconstruction, preserving either input zero sign and every exact multiple. This assumes the actual remainder operation returns signed mathematical zero; its sign does not affect is_zero().
2. **Step larger than input magnitude, b>a>0:** q=0,r=a. This is included in the non-small branch below since a<=2^28*b. Exact bounds are0/b for positive input and -b/0 for negative input. The copysign call supplies +0 lower or -0 upper. Nearest compares2*a withb and selects the upper on equality; directed and toward-zero strategies select the expected bound. No small-quotient assumption is omitted.
3. **Remaining non-small step, b<=a and a<=2^28*b:** exact binary64 bound capacity and the distance lemmas below apply.
4. **Small step, 0<b<a/2^28:** both exact and reconstructed bounds project to the input, regardless of which bound nearest selects.

Equality at the relative threshold belongs to the non-small branch. Any subnormal input lies in that branch: a<=((2^23)-1)*2^-149 and every nonzero binary32 step is at least2^-149, so a<2^28*b. All relevant exact dyadic nonzero magnitudes are far above binary64 underflow. Final binary32 overflow is possible only in the non-small branch; it is the single correctly rounded cast of an exact selected bound, including signed infinity. Neither the enclosure argument nor the capacity argument assumes a fictitious finite neighbor beyond the largest binary32 value.

## Small relative step

Define:

```
Ldown = RD64(a-r)       Lup = RU64(a-r)
Udown = RD64(Ldown+b)   Uup = RU64(Lup+b)
```

`small-step-exact-enclosure.smt2` negates the claim that all four endpoints project to a, and that their negations project to -a. Z3 returns UNSAT over arbitrary finite positive binary32 a,b,r with0<r<b<a/2^28. Equality uses SMT `=`, not zero-sign-erasing fp.eq. The simpler native-reconstruction query also returns UNSAT.

Directed bounds enclose the exact rational multiples a-r and (a-r)+b. Monotonic projection and equal endpoint projections imply the exact values project toa. RNE reconstruction of a-r lies between Ldown/Lup; monotonicity and outward rounding place its subsequent RNE addition within Udown/Uup. Thus both computed and both exact bounds project to the input. Reflection gives the negative case, with endpoint roles exchanged; RNE symmetry is a standard IEEE premise, not a new Lean theorem. No intermediate selection agreement is required, consistent with the retained step5*2^-149 witness whose native nearest branch differs from the exact branch.

This directly checked enclosure implication replaces a missing quantitative error-bound instantiation. It includes all encoded exponents admitted by its strict premise. The small-step center is nonzero, so there is no hidden identification of +0 with -0.

## Non-small complement

Instantiate reviewed `RoundBoundedSignificand.adjacent_capacity` with its binade parameter equal toa and scale=2^28. The theorem only requires a<2*binade, not that the parameter is a real binade; positivity supplies this. Its stepLower hypothesis is exactly a<=2^28*b. The partition therefore leaves no numerical interval uncovered, including b>a.

That existing theorem derives q<2^29, q+1<=2^29 and both positive/negative adjacent step multiples with coefficient magnitude<2^53 on the common binary32 grid, exponent<=253. Its existing exponent-window result lies within binary64 normal range. Under the standard capacity-to-representability and correct-rounding premises, a-r=q*b and the second bound(q+1)*b are exact binary64 values. This applies existing results; it adds no theorem credit and is not a newly kernel-checked binary64 decoder.

Nearest selection still needs an ordering argument: one distance is the exactly representable remainder r, whereas the other is RN64(b-r), possibly inexact. The two new SMT implications are:

```
r < RN64(b-r)  iff  2*r < b
RN64(b-r) < r  iff  b < 2*r
```

Both negations are UNSAT for all finite positive binary32 b,r withr<b. Twice the remainder is exact in binary64. The first implication supplies the positive-input lower-bound comparison; the second supplies the negative-input comparison. Equality selects the upper bound. Up/down select their exact bound directly; to-zero selects the smaller absolute bound, the toward-zero multiple since q>=0 andb>0. Final narrowing performs one rounding of an exact selected bound, including overflow.

## Signed zero and remaining bridge

At q=0, toward-zero reconstruction is mathematical zero. The source applies copysign(wide_value): lower zero is +0 for positive input, upper zero is -0 for negative input. Together with the exact-input early return and upper-on-nearest-tie policy, this matches the reviewed finite-reference signed-zero convention. This is source/IEEE correspondence, not a new execution trace or signed-zero kernel proof.

The composition is conditional numerical evidence, not a single end-to-end machine-checked proof. External links remain: actual Rust truncating remainder and signed-zero behavior; exact input/type/provider resolution; binary64 capacity interpretation and correct IEEE operations; directed-enclosure/monotonicity/reflection principles; final cast and compiler/target behavior, including subnormal preservation. NaN, infinities and zero step are excluded. Parsing, typed CSS evaluation and browser acceptance are not covered. No query uses fp.rem: its nearest-quotient IEEE remainder differs from truncating fmod.
