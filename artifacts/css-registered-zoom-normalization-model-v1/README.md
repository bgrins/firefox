# Registered value zoom normalization contract

Research only. Four Lean theorems establish a conditional representation contract; three deliberately false arithmetic controls are rejected by the kernel. Replay passed with Lean 4.35.0-rc4. Each audited theorem uses only `propext`; there are no `sorry`, custom axioms, or native decision procedures. This is not a Rust refinement or a CSS conformance proof and adds no canonical coverage or accepted bug credit.

```
python3 -B artifacts/css-registered-zoom-normalization-model-v1/replay.py --output /private/tmp/registered-zoom-replay-UNUSED
```

The output directory must be absent. The runner authenticates the compiler, import, model sources and referenced captures, uses an owned temporary compilation directory, and deletes that compilation directory. Its three negative controls reject double application in substitution, double removal in CSSOM, and removal using a different scale from the one used to compute the value. The concrete controls use exactly divisible natural-number examples; they do not model CSS arithmetic.

`Scaling.cancel` assumes removal is a left inverse of application. `Evaluation.factors` assumes the raw computation factors into the same scale applied to the correct canonical value. These are explicit structure hypotheses, not proved implementation facts. The theorems show that normalizing each local result with its actual computation scale, copying already canonical initial/inherited values, and exporting the stored value consistently makes consumption apply its own scale once and makes storage independent of the computation scale.

Relative inputs are represented by arbitrary `Input`. Correct font, root font, line-height, viewport and container values, dependency readiness, and their zoom conversion are obligations of `Evaluation.factors`, not established here. CSS-wide selection of initial versus inherited values is outside this model. The `initial` and `inherited` constructors require already canonical values; recomputed initial values must pass through local normalization instead. An aggregate length representation can instantiate `Length` only after establishing the scale law for all its leaves. Positive/nonzero scales, floating-point rounding, clamping, animation interpolation, percentages and mixed-dimensional math are not discharged by these theorems.

See REPAIR-PLAN.md for the concrete source boundary and remaining implementation work. The paired browser experiment is owned by root. The baseline evidence is from the pre-A local branch binary; this package makes no upstream or release reproduction claim.
