# Clamp simplification preparation

This is a compiled, independent semantic model prepared before the native repair is frozen. **It does not yet verify a native patch.** `check.py` always reports `live_native_verified: false`.

## Scope

`Clamp.lean` models NaN, positive and negative infinity, arbitrary rational finite values, and a separate negative zero. `finite 0` is positive zero. Scalar order is defined explicitly and its totality, transitivity, reflexivity, and antisymmetry are proved. Standard Lean axioms `propext`, `Classical.choice`, and `Quot.sound` occur; no admitted proof, native execution shortcut, or additional axiom is allowed.

The specification is strict nested maximum/minimum. Separate relational theorems characterize those operations by their greatest lower bound and least upper bound properties. Native-shaped comparison dispatch is proved equivalent. NaN is not censored inside the tree.

An inductive expression language contains canonical literals, arbitrary environment inputs, arbitrary unary operations, and nested clamp. The simplifier recursively simplifies children and folds a clamp only when all three children are context-independent literal values. Its denotation is proved equal for every finite expression and every environment/operator interpretation. Nonleaf operations may return NaN even with finite inputs. This is not restricted to a finite input table.

The old early-return counterexamples cover both a literal NaN upper bound and an unresolved nonleaf upper bound. The latter has different results under two environments and is retained by the safe simplifier. Additional controls cover all three NaN positions, infinities, and signed-zero ordering.

`finite_common_unit_clamp` and `common_unit_rewrite_sound` separately prove that strict clamp commutes with scaling finite coefficients by any finite nonnegative rational basis, including zero. Negative coefficients times zero preserve negative zero. Both infinities times zero produce NaN in the resolver. Counterexamples show why infinite relative coefficients at zero and negative percentage bases need separate treatment. Floating-point rounding, overflow, and underflow are outside this rational scaling theorem.

`guarded_early_return` makes the mixed-unit winner-selection obligation explicit: every child must be non-NaN in every permitted environment, and the reported greater-than comparison must be semantically valid there. It proves the lower-wins branch under those premises. It does not establish that native leaf classification or comparison meets the premises.

## Replay

From the repository root:

```
python3 artifacts/css-clamp-nan-proof-v1/check.py artifacts/css-clamp-nan-proof-v1/replay-NEW
```

The output directory must not exist. The pinned compiler is the bundled Lean 4.35.0-rc4. A successful run checks the exact axiom inventories, compiles seven deliberately incorrect variants and requires their reviewed theorem-local errors, rejects twelve poisoned result records, and rechecks all input hashes. The mutation diagnostics are checked in `expectations.py`; errors outside a theorem proof body are rejected.

## Native bridge still required

The proposed repair has evolved beyond the literal-only core simplifier. Before any native acceptance claim:

1. Freeze and review the exact native branch and typed-leaf helpers. Bind both original and repaired sources, not just this model.
2. Prove or explicitly admit the soundness of canonical-value conversion. Relative coefficients must never be labeled context-independent canonical values.
3. Bind the finite common-unit fast path to the scaling theorem. Check nonnegative bases and finite coefficients, preserve zero signs, and state the IEEE rounding/overflow limitation. Relative infinity with a possible zero basis must remain unresolved.
4. Bind percentage hint classification. A raw percentage may be compared as a number; a percentage with unresolved or possibly negative basis must not use the nonnegative scaling theorem.
5. Bind NaN detection before native comparison or arithmetic, without using normalized `NoCalcNumber::get()` for intermediate values. This model merges NaN signs and payloads; neither affects the specified result.
6. Audit the mixed-unit fallback against `AlwaysScalar` and `AlwaysGreater`. The lower-wins branch is proved conditionally. Other winner branches and all native comparison certificates are not yet mechanically connected.
7. Integrate common-unit folding and mixed-unit selection into the complete expression simplifier if claiming whole-candidate structural preservation. At this checkpoint, only the canonical literal folding policy has that structural theorem; unit folding is a separately proved local rewrite.
8. Review baseline/patched browser outcomes and existing serialization coverage independently. This package contains no browser execution or native build evidence.

The proof does not cover parsing, dimension/type inference, CSS `none` endpoints, root censoring, all CSS operators, native execution, or general Stylo conformance. It was developed after source/browser witnesses were known; it did not discover the observed bug.
