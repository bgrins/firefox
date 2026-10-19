# Normalized zero-prefix fold: prepared bounded model

This is a research model prepared before the native zero-prefix patch. It has no native source binding and is not a frozen accepted proof capsule. No browser result is asserted by this directory.

`Fold.lean` uses Lean 4.35.0-rc4, `Std`, and core `Rat` arithmetic; no mathlib or additional axioms. Closed rational witnesses use kernel reduction (`decide +kernel`), not `native_decide`. All 17 audits report only Lean's standard `propext`, `Classical.choice`, and `Quot.sound` axioms.

## Contract

For an arbitrary color type and arbitrary compatible weighted/progress interpolation functions, a native-shaped left fold equals an independently defined stack reduction for every finite nonempty input list with nonnegative rational weights. The stack interpreter combines its first two items and pushes their result back. It uses progress `b / (a + b)` when the sum is positive, otherwise one half. The native loop independently selects equal weights only for normalized zero sums, otherwise divides both accumulated weights. The proof establishes the complementary ratio identity and preserves nonnegative accumulated weight before inducting on the rest of the list.

The theorem starts after conversion into the interpolation space and weight normalization. At a positive total it models the internal loop of color-mix. It does not model the implementation's all-zero-total early return. Its mathematical list theorem also applies to all-zero lists; that stronger mathematical fact does not assert native behavior through the excluded early return.

The generic theorem has an explicit interpolation compatibility hypothesis. The concrete `Option Rat` channel model discharges it: independent spec channel interpolation copies a sole present component or evaluates `x + (y-x)*p`, while the native channel function copies missing operands and forms `x*wa + y*wb`. This models an opaque rectangular color component, or alpha itself. It does not model varying-alpha premultiplication of color coordinates; full color interpolation remains an explicit assumption of the generic fold theorem.

Exact kernel witnesses cover forward and reversed zero prefixes followed by a missing channel, numeric final channels, repeated zero prefixes, missing alpha, and an initially missing prefix. The two old-fold witnesses return red 1 and 0 where the specified fold returns 1/2. Repeated prefixes return 1/4, making the ordered-fold interpretation observable. No associativity or uniform-average claim is made.

`raw_step_unchanged` and `raw_fold_unchanged` prove preservation of the old branch and weight arguments for arbitrary signed rational weights when normalization is off. `raw_cancellation` exercises sum-zero signed weights. These results preserve behavior; they do not prove the old behavior conformant for animation or gradients, and do not establish an IEEE signed-zero/NaN theorem.

## Scope and next source binding

Excluded: binary floating point rounding, underflow, overflow, nonfinite values, parser normalization and omitted weights, conversion numerics/missing-mask transformation, interpolation helpers, hue, gamut mapping, final alpha scaling/rounding, serialization, style scheduling, and compositor behavior.

After the preceding RGB patch is committed and the native loop is changed, bind the exact parent/current loop and NORMALIZE_WEIGHTS flag. Check the old unconditional skip, new conditional raw skip, equal-weight branch, unchanged positive branch, accumulated-weight assignment, and unchanged helper invocation. Authenticate the entire final file at that point. Do not use this preparatory model's successful compilation as evidence that extraction has happened.

Primary normative sources already archived in `../css-breadth-audit-round2-v1/colors/`: CSS Color 5 `#color-mix-result` stack algorithm and issue 14013 (June 2026 zero-denominator correction), CSS Color 4 `#interpolation-missing` channel carry-forward. `../css-color-zero-prefix-review-v1/DESIGN.md` records the shared-caller analysis and targeted native design. These sources were read for this model; their hashes appear in `PREPARATION.json`.

## Replay

Run `python3 artifacts/css-color-zero-prefix-proof-v1/check.py NEW_OUTPUT_DIRECTORY`. It compiles all audits in a fresh directory, compiles four semantic mutations, requires exact theorem-owned diagnostic inventories, rejects malformed evidence, and checks pre/post input hashes. Deliberately invalid mutants can report `sorryAx` after Lean's failed theorem elaboration; they are required to exit 1 and never accepted as proofs. Their diagnostics are proof-rejection evidence, not independently compiled counterexamples. Development and discovery logs are retained separately.

The semantic mutations restore unconditional skipping, replace equal interpolation weights with zero, incorrectly assign accumulated weight one, and apply normalization to a raw cancellation. The last mutation also breaks some proof simplification in the normalized branch; its meaningful rejection is independently required at both the universal raw preservation theorem and the concrete raw-cancellation witness.
