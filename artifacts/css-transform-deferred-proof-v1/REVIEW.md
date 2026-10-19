# Review record

## Independent oracle

Web Animations computes each composed endpoint before interval interpolation. Accumulation of the underlying `translateX(50%)` into `scale(1)` and `scale(2)` yields translation equal to half the reference width at both endpoints, with scales 1 and 2. At progress 1/2, the scale is 3/2 and translation remains half the width. The concrete domain uses positive diagonal scale, so no quaternion, rotation, skew, or singular ambiguity is needed. Matrix multiplication is used for transform lists, while accumulation uses one-based scale addition; these are deliberately different operations.

The runtime record `artifacts/css-breadth-probes-round3-v1/transforms-baseline-v1.json` observed identity at widths 200 and 400, while pixel, matching-function, and no-effect controls passed. This contextual evidence is not replayed by the Lean gate and is not required to reconstruct this source companion. The local browser version in that record is not a release-impact claim.

## Manual mapping

| Native operation | Model | Boundary |
| --- | --- | --- |
| Generic `ToMatrix::to_3d_matrix` deferred arm returns `Err(())` | `eager` rejects `interpolate` and `accumulate` | Exact combined Rust arm pinned; error labels are model-only |
| List converter's `operation.to_3d_matrix(reference_box)?` | `eager` append propagation | Whole file pinned; numeric casts excluded |
| `matrix.then(&transform)` | ordered `compose` | Rational affine order controls; no Euclid numeric proof |
| `try_animate_mismatched_transforms_in_place` converts left/right with `None` | `attempt` conversion stage | Both operands pinned, no context supplied |
| `Matrix3D::animate(..., procedure)?` | abstract native operator | `OperatorSound` is an explicit premise, not proved from Rust |
| `animate_mismatched_transforms` retains `from_list`/`to_list` | `deferred` on failed attempt | Both operands and constructor parameter retained in model; f32 progress/count conversion outside scope |
| C++ recursive deferred evaluation | `evaluate` | Manual intended semantics; C++ code is reviewed separately, not authenticated or extracted by this gate |

The exact rational affine instantiation handles one reference-box dimension. Uniform 2D scale witnesses are projected onto that axis; symmetry of the other axis is used in the browser oracle, not proved here. The general matrix algebra can carry additional coordinates, but native conformance for those coordinates is not claimed.

## Review cautions

`partialEval` is a specification-side, more permissive partial evaluator. The patch does not recursively resolve deferred Rust nodes. The meaningful relationship is the induction from successful partial evaluation to independent context-indexed evaluation, followed by the conservative-eager refinement and caller theorem. Failure is deliberately not characterized as invalidity or necessary context dependence.

The native caller also wraps failed matrix operations in deferred nodes. The theorem's fallback is equality with the original deferred expression; it does not settle the separate question of whole-animation versus suffix-only singular fallback. Native distance evaluation now fails for deferred nodes instead of receiving identity; the independent native review documents this compatibility boundary. This proof contains no distance theorem.

`decide +kernel` reduces only closed rational examples; the arbitrary-tree and arbitrary-list results are induction proofs. Axiom output is checked exactly. Mutation diagnostics are pinned to theorem bodies so a malformed mutant cannot satisfy the negative gate merely by failing to parse.
