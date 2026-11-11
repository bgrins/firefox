# Owned animation property inputs

`snapshot.patch` is a two-file prerequisite on source basis `7382007a82b49e83e5399a31f47b598e0f260fe5`. It exposes an owned input snapshot and property computation from explicit inputs. Ordinary BuildProperties immediately uses that path. This is not a missing-pseudo CSSOM fix. No live source/test edits, builds, browser runs or Git mutations were performed.

The previous ComposeProperties extraction was tested and restored and remains artifact-only. It is not included here. This patch is independently applicable; eventual request-local composition requires both seams and the remaining boundaries below.

## Concrete change and preserved callers

PropertyInputSnapshot owns the specified-keyframe clone, the existing virtual GetComputedKeyframes output and its selection flag, an OwningAnimationTarget and effect composite. CapturePropertyInputs preserves the order: clone specified keys, invoke the existing virtual completion, then copy target/composite. It does not hoist those latter reads across dispatch.

BuildPropertiesFromInputs returns a fresh owned AnimationProperty array using the supplied style/timeline, the selected captured keyframe array and the same KeyframeUtils call. It initializes/forwards aReferencesAttributes without publishing mReferencesAttributes, mProperties, base values, EffectSet masks or restyle hints.

The renderer BuildProperties retains its style assertion, false attribute-output initialization and null-target return before cloning/generation. After computation it retains the debug specified-array comparison and unconditional move of the specified clone back into mKeyframes, including when property computation returned empty.

GetKeyframes and CSSAnimationKeyframeEffect::GetComputedKeyframes are byte-identical. The same virtual call occurs once; base false, CSS completion, and mIgnoreKeyframesGeneration after JS setKeyframes are preserved. Missing CSS endpoints retain the same default easing/composite choices and null declaration-block base-value sentinels. CSS generation parameters are captured through the completed result, not newly exposed independent parameter fields.

## Ownership and cost

The snapshot owns array storage and ordinary keyframe value fields/references. PropertyValuePair declaration blocks remain shared RefPtrs: no deep semantic immutability claim is made. OwningAnimationTarget retains the originating element and pseudo request, including a pseudo identifier reference where present. This extends target lifetime through conversion and snapshot destruction; it does not establish that the target remains current after reentrancy.

Style and timeline are borrowed only for the synchronous computation call. The caller must keep them alive and suitable for the captured target. The snapshot does not own an Animation, AnimationTimeline, ComputedStyle or computed-timing sample. A future request must retain those separately and establish coherence/no-reentrancy or explicitly reject a stale result.

Ordinary BuildProperties still performs exactly one full mKeyframes.Clone. The existing CSS override performs the same percentage/range array construction. Arrays move into the snapshot; the specified clone moves back into mKeyframes. GetKeyframes takes no snapshot and has no added clone. New ownership consists of the strong target/pseudo identifier references. No second operation arena or persistent cache is introduced. These are source observations, not a benchmark or performance-equivalence proof.

## Precise remaining boundaries

1. Captured mComputedOffset values and CSS-completed endpoints are not refreshed. A current timeline argument does not recompute offsets. A final query needs owned specified keys, captured timeline/attachment range and an explicit CSS generation-parameter seam, so ComputeMissingKeyframeOffsets can operate on the owned copy before missing-endpoint completion. Updating only the specified array while retaining already-completed CSS endpoints is invalid.
2. Fresh property computation requires a raw pseudo base excluding its own animation/transition rules while inheriting current ancestor effects. Animated custom-property/font/relative-unit providers cannot silently be evaluated against only the unanimated base. No provider-resolution algorithm is settled by this extraction; the untracked deferred-endpoint prototypes are not adopted or duplicated.
3. The request must own strong effect/animation/timeline references, target/order/level and one suitable timing sample. Animation::ComposeStyle's pending/unresolved behavior must be preserved without query-time ticking. Borrowed EffectSet iterators/frame/style borrows must not survive potentially reentrant preparation.
4. Base-value tables must be extracted from the explicit raw pseudo style. Masks must be derived from fresh property arrays with existing transition-underlying/skip semantics. UpdateProperties/UpdateCascadeResults cannot be used to publish query-local state.
5. CSSOM-only admission/cache bypass, separate animation/transition maps, pseudo-aware transient recascade with origin style, important/visited handling and request-local result lifetime remain unimplemented.

The snapshot is therefore useful for current-context value computation but is not a complete timing/cascade snapshot. The accepted [missing-pseudo design](../css-pseudo-animation-design-20261110-v1/REPORT.md) remains the integration contract.

## Verification and gate

check.py --check-git authenticates12 source pins, replays/reverses the two-file patch in scratch, verifies unchanged C++ outside the extracted region, checks the single specified clone and capture order, renderer admission/debug/move-back and helper argument forwarding. prepare.py regenerates the patch; FORMAT.json records byte-identical whole-file clang-format output. The independent [source review](../css-pseudo-animation-next-candidate-review-20261110-v1/REPORT.md) found no blocker for a build/preservation experiment.

No compiler/runtime acceptance follows from these source checks. TEST-PLAN.md selects existing CSS-generation, named-range and retained pseudo controls. Their fresh baseline results must be preserved exactly; no old expected-pass counts are invented. Debug remains required before accepting the final missing-pseudo repair because the earlier broad patch triggered a normal-traversal transform assertion. The clip-only debug scope decision does not relax that requirement.

No missing-pseudo failure metadata changes, new browser fix or catalogue increment is included. PRIOR-WORK-PRESERVATION.json records untouched, unused preexisting drafts.
