# Sticky finite-sentinel repair: independent design review

## Current assessment

The exact proposed DoComputePosition change is sound within its stated positional scope. Source candidate38d14faa60bfe3180e87904f5085fdbbee5aa47746a38df77f4edb50360af40c changes only that function relative to retained fe79e921b6309b75e8d7f7c9292521bb27182567695f74bc6245710cfc75a91f. It uses original computed-offset presence independently for each physical side and preserves the four existing clamp operations and their top/bottom/left/right order. No source-level blocker was found. Final runtime/packaging acceptance is recorded separately when available.

The exact pre-change function also matches freshly retrieved upstream. Replacing this complete body is source-independent of H1/H2 changes in ComputeStickyLimits. This is an in-memory source comparison, not an isolated-upstream build. Existing comments are retained.

## Normative basis

[CSS Positioned Layout sticky positioning](https://drafts.csswg.org/css-position-3/#stickypos-insets) explicitly preserves the laid-out coordinate when both insets on an axis are automatic. Its individual movement rule applies only to a side whose original inset is non-auto, subject to sticky-view and containing-block constraints. Auto-to-zero treatment during view-rectangle construction is a separate operation; it does not make an auto side a movement constraint.

This directly supports independent guards on all four original inset flags. It is stronger than merely returning early when both axes are all-auto: a top-only or left-only sticky item must not be clamped by the finite automatic opposite side either. The WPT includes exactly these one-active-edge cases.

## Why numeric sentinel checks are wrong

The initialized interval has low=-536870911 and high=536870912 app units. Both are finite inside the nscoord domain. With normal700000000, the old far clamp can move an otherwise unrestricted item to high. The browser's large spacer is a concrete route to this condition, avoiding the containment changes that a huge margin could introduce.

Conversely a real computed edge may equal either sentinel. Independent arithmetic challenge: scrollport100, box10, bottom inset-536870822 yields a non-auto bottom edge536870912 exactly. Normal700000000 with containment[0,900000000] must still clamp to that explicit edge. A rule that skips the clamp because the edge equals high is wrong. `CHALLENGES.json` retains this and a symmetric low-edge example, a top-only example, far-only control and operation-order example. These are exact-integer source-shaped calculations, not browser reachability or native compiler results.

The original NS_AUTOOFFSET encoding itself also aliases a reserved numeric value. This patch does not redesign that encoding. A numeric proof must explicitly exclude a purported explicit inset equal to that reserved code, rather than treating arbitrary Int optional insets as a lossless native representation.

## Complete positional caller chain

ComputeStickyOffsets resolves each physical side and stores ComputedOffsetProperty. ComputeStickyLimits reads that property, constructs containment from frame/continuation/margin geometry, calculates effective view insets, and updates stick edges only for original non-auto sides. The reviewed repair reads the same property and uses the same original-side mask. It does not use the adjusted effective inset or compare derived coordinates.

When the property is absent, ComputeStickyLimits already returns its initialized limits immediately. DoComputePosition now returns GetNormalPosition. Keeping the limits call before the property guard is therefore safe for this branch and preserves its existing assertion/call behavior; moving it is unnecessary. This path is a lifecycle safeguard, not the reachability argument for the reproduced fully reflowed all-auto defect.

ComputePosition passes current-scroll space. ComputePositionIgnoringScrolling passes zero-scroll space. ComputeTranslationIgnoringScrolling canonicalizes to the first continuation and subtracts its normal position. nsIFrame::GetPositionIgnoringScrollingAndSticky consumes that translation when reconstructing geometry. PositionContinuations first requires a stored normal position, then applies the first frame's common translation to every continuation. UpdatePositions recomputes offsets on reflow, orders ancestors before descendants, and tracks overflow changes. The missing-normal guard remains intact.

IsStuckInYDirection compares the computed and normal y positions. ScrollContainerFrame's header/footer heuristic uses that result when deriving page-scroll amount. The repair removes false stuck classifications on an automatic y axis; it does not alter the heuristic itself.

## Range, compositor and timeline boundaries

GetScrollRanges calls ComputeStickyLimits directly and still identifies absent constraints by numeric edge equality. Its output reaches nsDisplayStickyPosition::CalculateLayerScrollRanges and ClipManager's sticky spatial-node construction. It is unchanged by this repair; explicit-edge/sentinel collisions and extreme difference arithmetic remain open there.

GetStickyScrollRangesForAxis uses original inset flags and returns empty on all-auto axes, but asserts that active computed edges differ from sentinel values. That assertion is not a universal truth, as the collision witness shows. The function also forms coordinate differences. ViewTimeline::ComputeStickyDisplacement consumes those ranges and current frame displacement; multiple sticky ancestors are explicitly rejected by its current algorithm. The new positional result may flow through these callers, but no complete timeline/compositor/extreme-range repair follows.

For the simple all-auto regression, unchanged per-axis ranges are empty and unchanged two-dimensional ranges have matching inner/outer unconstrained edges. That is consistent with no sticky displacement. It does not establish universal asynchronous rendering equivalence. Candidate acceptance should include existing sticky, continuation and timeline regressions, with an explicit arithmetic/provider domain for any theorem.

## WPT oracle audit

The24 tests span physical horizontal/vertical axes; auto, near-only, far-only and both-sided insets; normal positions100,8000000,9000000; and scroll0/100 within each test. The container17000000, spacer size, target10 and exact requested scroll are asserted before the position oracle. The oracle independently starts from the spacer coordinate, applies only explicitly selected near/far limits, and permits2px CSSOM rounding. It does not read the engine's limit rectangle or derive expected positions from the observed target.

The root baseline has four failures: high-coordinate auto and near-only on both axes;20 matching tests. Root's separate42-row release/current probe preserves28 ordinary static/relative controls and establishes the threshold with near-boundary values. The old less-than-one-pixel tolerance had two false ordinary failures and remains historical; this review accepts the corrected <=2px comparison.

Limits: browser tests do not exercise missing-property lifecycle state, negative-coordinate sentinel collisions, arbitrary writing modes, malformed native offset codes, all continuation geometry, asynchronous rendering, or integer overflow. The both-sided fixture is consistent and does not establish semantics for contradictory limits. These belong in source/native/formal boundary checks rather than fabricated browser claims.
