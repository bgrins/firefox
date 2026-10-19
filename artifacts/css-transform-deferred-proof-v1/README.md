# Deferred transform conversion

This companion proves the successful-result contract needed by the local deferred-transform repair. It is a manually written Lean model, not extracted Rust or a formalization of all CSS transforms. The browser bug was found by source analysis and confirmed by an independent numeric browser oracle before this proof was built.

## Reproduce

From the Firefox root, using the bundled Lean 4.35.0-rc4 toolchain:

```sh
python3 artifacts/css-transform-deferred-proof-v1/check.py /tmp/deferred-proof-run --snapshots-only
```

The output directory must not exist. This mode reconstructs authenticated old/current native snapshots from parent `11482ee213bf63c749b6d205c2c7591d783bdaa8` and the exact intended patch. It works before the native fix is applied and records `live_native_verified: false`. Omit `--snapshots-only` to additionally require the live native files to match the repaired source. Nothing builds Firefox or edits native files. Generated snapshots, logs, and capsules are not companion source files.

## What is proved

`partial_sound` uses structural induction over arbitrary finite recursive trees, including lists, interpolation, and accumulation. Its compositional partial evaluator differs from the box-indexed evaluator: it must reject percentage dependencies, but can evaluate recursively context-independent deferred children. Every successful partial result equals evaluation at **every rational reference dimension**. The dimension is one axis of a reference box; arbitrary other matrix behavior is parameterized by an algebra.

`eager_refines_partial` shows that the conservative conversion matching the repair is a subset of that compositional evaluator. It rejects both deferred constructors, including ones that could theoretically be resolved without context. `eager_sound` derives its successful-result contract. `list_success_members` and `list_failure_propagates` prove that an unconvertible item anywhere in an arbitrarily long list prevents success, including after a converted prefix.

`attempt_sound` models the caller separately: successfully convert both operand lists and apply a native operator, or preserve both original lists in the appropriate deferred node. The theorem assumes explicitly that every successful native operator result agrees with the specified algebra (`OperatorSound`). It covers both interpolation and accumulation. The two fallback lemmas establish preservation of both operands when either conversion fails. The repair does not introduce the more powerful compositional evaluator.

The algebra is instantiated with exact rational one-dimensional affine matrices. Composition is ordered multiplication of affine transforms; interpolation is component interpolation; accumulation adds translation and performs one-based scale addition. Interpolation/accumulation accept only positive endpoint scales. This is the bounded domain of the concrete witnesses, not an assertion that CSS rejects all other scales. A singular example exercises the diagnostic distinction only.

Kernel-checked examples reproduce translation 100 at width 200 and 200 at width 400, with scale 3/2; demonstrate the old identity error independently for each deferred constructor and for their nested combination; and retain fixed-pixel, composition-order, and prefix controls. Generalized proofs do not enumerate or bound tree depth. Exact numeral examples supplement them.

## What remains assumed or excluded

Native primitive conversion, numeric casts, and native matrix arithmetic must satisfy the abstract operations for the model to describe native numerical behavior. The source bridge checks exact source bytes and selected control flow, not those numerical premises. No claim is made about all matrix decomposition, IEEE arithmetic, arbitrary rotations, skew, perspective, singular fallback scope, reference-box invalidation, animation matching/padding, compositor equivalence, distance computation, or recursion/resource limits.

The model separates `needsContext`, `unsupportedDeferred`, and `semanticFailure` so that a missing environment is not declared a semantic error. Rust currently reports all of these through `Err(())`; its caller preserves deferred operations after any eager failure. The proof does not claim Rust exposes these distinctions, nor that its singular-animation fallback conforms. The caller theorem establishes preservation relative to the model's deferred denotation under its stated operator premise.

## Checks and source bridge

The gate compiles 22 theorem axiom audits and eight independent semantic mutations: identity for each deferred constructor, ignoring list failure, reversing composition, dropping either fallback operand, swapping interpolation operands, and dropping percentage dependence. Negative cases must fail at the reviewed theorem proof locations with the expected diagnostics. Syntax/type errors outside proof bodies do not count. The accepted proof uses only `propext`, `Classical.choice`, and `Quot.sound`; there are no user axioms, `sorry`, or native-evaluation shortcuts.

Eight separate source tamper controls check authenticated snapshots. These are integrity checks, not additional semantic proofs. All companion files, snapshots, spec excerpts, Lean executable, and optional live native inputs are hashed before and after compilation. The gate stores actual compiler exits and complete logs. `freeze.py` verifies receipts and produces a local capsule; neither a hash nor a green gate establishes the excluded numerical premises.

`SOURCE-v1.json` records the exact old/current arm, parent, and file hashes. `SPEC-v1.json` records primary draft snapshots and complete relevant anchored section excerpts captured on 18 October 2026. Their interpretation is manual. `REVIEW.md` maps model definitions to control flow and states the concrete oracle independently.
