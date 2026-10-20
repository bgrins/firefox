# Relative positioning of overflow continuations: proposal

Status: PROPOSED, NOT BUILT OR BROWSER-ACCEPTED. The exact native and WPT patch is proposal.patch; source identities are in SOURCES.json and PATCH.json. Its native scope is independent of the earlier flex final-size retiming patch: only nsContainerFrame.cpp changes, and the standalone WPT excludes vertical-rl flex fixtures that still depend on the separate final-size repair.

## Source cause and proposed repair

All six indexed callers of ReflowOverflowContainerChildren pass ReflowChildFlags::Default: fieldset, block, canvas, flex, grid and table wrapper. Full retained source snapshots cover each call. The helper constructs child-writing-mode position from predecessor used IStart and block zero. FinishReflowChild invokes ApplyRelativePositioning only when its explicit flag is present. Thus the initial OC route neither applies a new relative block offset nor initializes NormalPositionProperty there. Predecessor used inline translation is inherited once.

For frame->IsRelativelyPositioned() only, the proposal reads predecessor GetLogicalNormalPosition(...).I(wm) and enables ApplyRelativePositioning when calling FinishReflowChild. This predicate matches ReflowInput's frame-aware offset producer, avoiding style-only applicability assumptions. Nonrelative and sticky frames use the original predecessor position and flags. ReflowChild still receives the original flags and a normal position; FinishReflowChild sets the new size before converting/storing normal position and applying computed offsets. The existing inline header is already included.

The paired changes are necessary: enabling the flag while retaining used IStart double-counts an inherited inline shift; normalizing IStart without enabling the flag loses all relative translation. FinishReflowChild's actual offset provider is the current continuation's computed offsets, not an assumed copy of predecessor offsets. The model permits different current offsets and different actual child sizes. Source conversions use the same passed container-size argument as before; unrelated temporary/final-frame correctness is not assumed or repaired.

## Normal-position lifetime and dynamic updates

ApplyRelativePositioning stores physical NormalPositionProperty on a relative frame before adding its physical computed offsets. RestyleManager::RecomputePosition loops continuations, obtains GetNormalPosition, initializes the property if absent, then adds new offsets directly. GetNormalPosition otherwise falls back to used GetPosition. This explains why zero-first dynamic positioning can appear correct while an initially nonzero overflow continuation is wrong, and predicts corrupt normal-cache initialization when a pre-shifted inline continuation is updated. The new helper initializes the property on its actual reflow route, so later updates use the stored normal coordinate.

No claim is made that every frame is reflowed on every update. The skipped-OC branch remains unchanged, as do continuation-list and eligibility logic. Existing correctly initialized relative OCs retain their normal properties. Proving every dirty/skip/style transition maintains the property is a broader lifecycle obligation; the WPT explicitly tests initial layout, zero-first updates, nonzero-to-double updates and returning to zero.

## Current browser evidence and standalone oracle

Root reports identical release/shared initial-versus-dynamic observations: horizontal and vertical-lr fixed-size overflow subjects lose initial block offsets on successors, while normal auto-size controls and zero-first dynamic updates pass. These results are source-consistent; browser-local normal-property values have not been traced. The earlier vertical-rl flex calibration failures belong to the separate final-size bug and are excluded from this standalone WPT. Root retains all raw evidence separately; this proposal has not independently authenticated those new runtime capsules yet.

The 140-subtest WPT uses 70 ordinary-size configurations: horizontal/vertical-lr row-flex, column-flex and block, plus vertical-rl block; fixed80px overflow and auto-size normal subjects; zero/±17 block/±17 inline offsets. Its zero geometry is independently checked against four 100×160px descendants. Fresh offsets are set before any layout read. Initial and subsequent shifts are compared with genuine zero-origin geometry, including dimensions, other items and restoration. It does not accept agreement with an uncalibrated block-reference implementation. Candidate results remain pending.

## Preliminary formal results and limits

RelativeOverflow.lean models normal and used coordinates separately, proves the paired repair, per-continuation offset application, update/initial equivalence and return to zero, and preserves counterexamples for flag-only doubling, missing block offset and missing-property update. Physical conversion lemmas explicitly account for reversed axes and unequal predecessor/current frame sizes. A small-domain lemma bounds every displayed subtraction/addition in that conversion chain within signed32; its numeric bounds are sufficient premises, not proved CSS/native provider guarantees.

These twelve kernel results do not prove allocation/cache lifecycle, actual computed-offset resolution, every caller's container-size validity, percentage/auto offsets, sticky positioning, orthogonal frame mode transitions, all native arithmetic, arbitrary descendants, or full CSS fragmentation. The full copied source is available for review; there is no claim that a small Point model faithfully instantiates every native method. Any complete companion must join actual frame applicability, returned sizes, normal-property ownership, computed physical margins, conversion intermediates, status/list/overflow consumers and skipped paths at its declared scope.

## Validation and packaging

Exact retained-base patch application and reversal passed and recovered the expected byte identities. JavaScript parses. Root owns native build/browser/lint/format validation. Initial style-only predicate and initial failed Lean attempt are retained as development history; use current PATCH.json and successful final logs for authoritative roles. No production source, WPT tree, index, browser or build was modified by this agent.
