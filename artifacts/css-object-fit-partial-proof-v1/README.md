# Object-fit with partial natural dimensions

This companion connects optional natural-size rules to the repaired native dispatch. It supplies mathematical model proofs and a finite extracted-C++ bridge, not a proof of all image sizing or painting.

## Repair and source contract

Candidate `layout/base/nsLayoutUtils.cpp` SHA256: `4c8af5a446595014cbd2718436af2da40ac33721a24f987cb3ef0ea16a5fc6e1`.

The only allowed whole-file change removes `|| !aIntrinsicRatio` from `ComputeConcreteObjectSize`'s Fill fast path and removes its two associated explanatory comment lines. `ComputeMissingDimension`, `MaybeComputeObjectFitNoneSize`, the rest of `ComputeConcreteObjectSize`, and `ComputeObjectDestRect` are byte-preserved. The entire unchanged `nsImageRenderer.cpp` snapshot is authenticated separately.

Searchfox path-scoped discovery identified all four extracted definitions and their direct call sites. Native review found:

- `ComputeObjectDestRect` passes its content-box constraint, optional intrinsic size, ratio and object-fit to `ComputeConcreteObjectSize`, then positions the returned size separately.
- `MaybeComputeObjectFitNoneSize` returns an absent result only when neither natural dimension is supplied. Supplied zero is a present optional value.
- `ComputeMissingDimension` returns the corresponding default dimension when the ratio is absent. With a ratio, its existing ratio arithmetic is unchanged.
- `nsImageRenderer::ComputeConstrainedSize` already returns its constraint immediately when the ratio is absent. Thus removing the earlier shortcut safely reaches an existing no-ratio fallback for Contain/Cover and for None when no dimensions exist.

The primary [CSS Images 3 sizing rules](https://drafts.csswg.org/css-images-3/#default-sizing) and [object-fit definition](https://drafts.csswg.org/css-images-3/#the-object-fit) are retained in `SPEC-v1.json` and the snapshot. Default sizing preserves each supplied natural dimension, filling a missing dimension from the default when no ratio exists. Contain/Cover use the constraint when there is no ratio. Fill also uses the constraint.

## Lean domain and results

`ObjectFit.lean` uses `Option Nat` for independently optional width/height and natural numbers for nonnegative constraints. None completes each absent dimension from the default. Presence is distinct from numerical zero. None's completion and Fill/Contain/Cover rules are stated for all optional patterns, including two supplied dimensions.

For **ScaleDown's ordered-choice theorem**, the explicit premise is `width = none OR height = none`. Then the None and Contain results share at least one axis. Their other axis is totally ordered, so componentwise minima equal one of the complete candidate rectangles and are no greater than either. This is the reason a minimum implementation realizes the normative choice in this domain; the proof is not merely a restatement of the C++ switch.

Fifteen audited theorems cover:

- None preserves width-only, height-only, and both-present dimensions.
- No natural dimensions give the constraint under every fit keyword.
- Fill, Contain and Cover return the constraint without a ratio.
- Partial natural dimensions make None/Contain comparable.
- Componentwise minima equal the ordered choice for comparable sizes.
- ScaleDown selects a whole candidate under the partial-dimension premise and is bounded by both candidates.
- Supplied zero width/height differs from absence when the corresponding default dimension is positive.
- The early-dispatch repair preserves every positive-ratio case for an arbitrary opaque unchanged continuation, and preserves Fill for either ratio state.
- A concrete two-present-dimension boundary violates the premise and makes componentwise minima differ from both candidates.

The boundary is constraint100×100, natural200×50, no ratio. None is200×50; Contain is100×100; componentwise minima are100×50. This package **does not claim** that result implements a whole-candidate ScaleDown choice. Removing the shortcut also changes that native input path; its real-world reachability depends on the image provider's relationship between natural dimensions and ratio. No universal unreachable-state claim is made. Zero×zero with absent ratio is another recorded operational boundary. None's direct two-dimension behavior is unambiguous; it is kept distinct from the ScaleDown restriction.

The positive-ratio theorem quantifies over an arbitrary continuation result rather than deriving ratio geometry. It says the deleted condition cannot change which continuation is selected when the ratio is present. It does not validate that continuation's sizing, ratio preservation, or rounding. This matters because the existing constrained helper has a less-than-one-CSS-pixel Contain adjustment.

## Native bridge

The complete definitions of `ComputeMissingDimension`, `MaybeComputeObjectFitNoneSize`, `ComputeConcreteObjectSize`, and `nsImageRenderer::ComputeConstrainedSize` are extracted with unchanged bodies. The native dimension enum is also copied verbatim. Before and candidate variants are compiled as separate executables.

Adapters supply `std::optional` for `Maybe`, two signed-32 size fields, the five named fit tags, assertions, and `AspectRatio`. The ratio adapter has an explicit presence flag and positive rational pair, integer truncation for its scalar ApplyTo, float multiplication for ApplyToFloat, and inversion. It counts arithmetic calls and asserts that no arithmetic is requested from an absent ratio. This is **not Gecko's actual AspectRatio rounding/saturation implementation**. For absent-ratio fixtures, zero ratio-arithmetic calls are part of every exact expected result, so the adapter's positive arithmetic is not used to establish those sizing results.

Positive-ratio fixtures compare before and after output and arithmetic-call counts. They are preservation checks with the same provider adapter, not a normative ratio oracle. Native optional presence, enum correspondence, size-field behavior and integer domain remain explicit bridge premises. The native source is not linked to Gecko.

The 2,355 fixtures comprise:

- 1,625 absent-ratio partial-size normative cases: all fits; constraint axes0,1,60,100,600; each present dimension0,1,40,100,140,600; at most one present dimension.
- Ten absent-ratio two-present-dimension boundary cases:200×50 and0×0 under all fits. ScaleDown results here are checked only against explicit operational expectations, excluded from normative claims.
- 720 positive-ratio before/after controls: four constraints, nine optional-size patterns, four positive ratios, and five fits.

Independent Python oracles use optional completion and componentwise minima; their ScaleDown normative classification is restricted as above. The original absent-ratio oracle is always the constraint. Candidate/original agreement with their own respective oracles and positive-ratio equivalence are separate gates. No browser evidence is inferred from these scalar fixtures.

Seven Lean semantic mutations, six Lean diagnostic guards, seven C++ semantic mutations, four compiler/runtime diagnostic guards, per-input source corruptions, and four whole-file-preservation mutations must be detected. Semantic native mutants must compile and execute cleanly before their changed outputs count as detection. Warning/error/runtime-output controls check the checker itself. Source preservation protects helper logic and the positioning caller as well as the early dispatch.

## Executed development result

The development checker exited0 with 14 audited theorems; an explicit both-present None theorem was then added for the final 15-theorem package. All 2,355 native fixtures passed their assigned oracle or preservation check. The original function had 380 counterexamples in the absent-ratio partial domain and two additional None counterexamples in the two-present domain. Two changed ScaleDown boundary cases are excluded from that normative count. All seven Lean semantic mutations, six Lean diagnostic guards, seven native semantic mutations, four native diagnostic guards, 16 source identities, and four whole-file preservation controls were detected. The final replay receipt and terminal producer status are authenticated in `PREPARATION-v1.json`.

## Reproduce and commit separation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-object-fit-partial-proof-v1/check.py --out artifacts/css-object-fit-partial-proof-v1/replay-new > artifacts/css-object-fit-partial-proof-v1/replay-new.log 2>&1
```

Use a fresh output directory. `RECEIPT-v1.json` records exact theorem axioms, native extraction hashes, fixture domains/hash, original counterexamples, excluded boundary changes, and all controls. Lean axiom audits allow only `propext` and `Quot.sound`; untrusted declarations and unexpected output are rejected. The compiler uses `-std=c++17 -O1 -Wall -Wextra -Werror -fsanitize=undefined,implicit-integer-truncation -fno-sanitize-recover=all`; executable identities and versions are pinned in `TOOLCHAIN-v1.json`.

`prepare.py` generates `SOURCE-v1.json` and the source-only `tooling-paths-v1.txt`; it is a preparation step, not a replay step. The tooling companion belongs before the separate native+WPT repair commit. Generated binaries, controls and replay logs remain artifacts. Final producer status and receipt identities are in `PREPARATION-v1.json`; independent replay is a separate acceptance gate.

## Explicit boundaries

No proof is provided for SVG intrinsic-size extraction, absence of a ratio for every possible resource, the consistency of two natural dimensions with a ratio, image loading/decode, CSS box constraints, object-position, viewport sizing, painting, pixel snapping, actual positive-ratio arithmetic, float saturation, or compiled-C++ semantics. Integer fixtures remain in a small representable nonnegative domain. Lean proves the abstract model universally over naturals; the C++ bridge tests a finite input set with adapters. Browser before/after WPT gates and independent normative/runtime review are recorded separately.
