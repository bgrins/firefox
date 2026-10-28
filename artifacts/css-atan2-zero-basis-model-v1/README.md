# Signed-unit atan2 scale-zero witness

The pinned Lean4.35.0-rc4 kernel checked four declarations and rejected two false zero-fold claims (3b29f6/0). Only propext appears in the axiom audit. Owned temporary olean files were removed; no target directory or canonical library was changed.

This small model encodes the four unit-coefficient quadrants and the zero-input table as rotations modulo360. Nat basis represents an ideal nonnegative common scale; the signs represent independent positive/negative unit coefficients. Positive basis yields45/135/225/315 degrees, while zero basis yields0 or180 depending on the X sign. Negative180 and positive180, and the two signed angular zeros, are intentionally identified as equal rotations. This does not erase signed-zero distinctions in the native proposal.

The general theorem folding_exact_iff proves that coefficient-only folding matches this model exactly when the basis is nonzero, for all four sign pairs and every Nat basis. nonzero_basis_suffices exposes the necessary premise explicitly. zero_basis_differs and the sampled-context witness reject extrapolating from a positive-font observation to zero. The two negative controls fail by decisive kernel evaluation, not parsing/type errors.

The table's correspondence to the CSS atan2 definition is manual. There is no analytic real-valued atan2 theorem, arbitrary unequal-coefficient theorem, IEEE/underflow/infinity/NaN proof, Rust refinement, parser or integer-consumer proof. Native source inspection found the issue before formalization, and root's browser observation is separate evidence. Canonical coverage and accepted-bug credit remain zero.

Replay:

```
python3 -I -S -B artifacts/css-atan2-zero-basis-model-v1/replay.py --output /private/tmp/atan2-zero-basis-replay
```

The output directory must be absent. Replay pins compiler, Init import, source bodies and references, checks the four axiom reports, and removes owned compilation scratch. It retains logs in the requested output directory.
