# CSS mod/rem with an infinite divisor

Preparatory proof companion, 18 October 2026. No native repair, WPT, browser run,
build, or commit is performed by this package. The defect was found by source
inspection and confirmed by root's separate browser probe before this proof.

Run from the Firefox checkout:

```
python3 artifacts/css-mod-rem-infinity-proof-v1/check.py /tmp/mod-rem-proof-new
```

The output directory must not already exist. Lean 4.35.0-rc4 is expected at the
existing local tool location named in `check.py`. The package has no Mathlib
dependency. The checker records compiler commands, actual child exit codes,
stdout/stderr, an object file for the successful model, input/output hashes,
four compiled mutation controls, and thirteen corrupt-record rejection checks.

## Claim

`dispatch_refinement` proves agreement between an independently written CSS
exception table and a native-shaped ordered dispatch for both operations and
every classified pair of operands. Values include both signed zeros, finite
nonzero values of arbitrary sign and opaque magnitude, both infinities, and NaN.
The magnitude type is universally quantified: this is not a finite sample of
floating-point values.

Two explicit hypotheses delimit the theorem:

1. The existing native finite arithmetic backend agrees with the chosen CSS
   finite arithmetic backend when the dividend is finite and the divisor is
   finite and nonzero. This includes finite rounding, underflow, overflow, and
   the native formula's final zero-sign adjustment; those are not proved here.
2. `FormulaContract` states that the existing formula and its zero-sign
   adjustment return NaN for all remaining operand categories. This abstraction
   is manually justified by the exceptional arithmetic table in `REVIEW.md`;
   it is not a machine proof of Rust or IEEE arithmetic.

The proposed repair leaves that backend unchanged. It returns the finite
dividend for an infinite divisor, after applying mod's opposite-sign exception.
The theorem proves the dispatch is correct under the two hypotheses. Separate
theorems expose signed-zero preservation, invalid input precedence, NaN
propagation, and old-implementation counterexamples for every nonzero finite
magnitude, both dividend signs, and both divisor signs where applicable.

The NaN constructor collapses payload and sign. Equality here means equality of
abstract semantic results; it is not IEEE `NaN == NaN`. Both zero signs remain
distinct. A theorem mentions generated negative zero because the value-level
model makes no assertion about parsing literal `-0`.

## Source and specification boundary

`old-dispatch.rs` captures the exact local `impl ModRemOp` inspected after
Searchfox discovery. `proposed-dispatch.rs` contains only the proposed finite
dividend / infinite divisor identity guard. `SOURCE-v1.json` records their
hashes and the complete source hash and HEAD at capture. The live checker
accepts either exact helper, identifying which one it found. An old-helper run
explicitly reports `live_candidate_verified: false`.

`SPEC-v1.json` binds two excerpts to the independent review's archived primary
CSS Values 4 document and fetch time. The CSS table uses the mod/rem exception
rules and the general NaN propagation rule. The primary source's valid
infinite-divisor identity note agrees with the defining nearest-multiple
semantics. No automated prose-to-Lean translation is claimed.

This model excludes native parser behavior, unit typing, root censoring,
serialization, actual `f32` bits and arithmetic correctness, WPT execution, and
the literal-negative-zero history. It does not verify other math functions or
claim a browser fix has landed. The source correspondence is manual and must
be reviewed again if the helper changes beyond the proposed exact fragment.
