# Central complement finite range

There is an exact int32 API-level counterexample to unconditional safety, but no browser-reachable counterexample was established. The ordinary literal-margin path has a useful source-backed conditional safety proof. Do not treat `nscoord_MAX` as a bound on every frame size or cached margin.

Let `E` be BSize, `s` the margin selected by the existing raw branch, `e` the opposite margin, `T=E+s+e`, and `h=trunc(T/2)+T%2`. Assuming the old arithmetic is defined, the new complement has the exact identity:

`E - (h-s) = trunc(T/2) - e`.

Four Lean declarations compile: this identity, the signed-int32 quotient bounds, the bounded-opposite-margin result, and a concrete counterexample. The model is integer arithmetic, not executed C++ or a reachability proof.

## Counterexample and its missing reachability

Take `E=2147483647`, selected margin `s=2147483647`, opposite margin `e=-2147483647`. Every old central-helper operation is defined: the margin sum is zero, total is 2147483647, half is 1073741824, unary negation is -2147483647, and raw offset is -1073741823. The new complement is 3221225470, outside int32. Swap logical start/end to select this case in the inverted branch. In particular, inverted First can newly execute the overflowing complement where the old First logical query needed no complement.

This witness does not follow from a huge CSS literal: literal margin conversion cannot produce its margins. Nor was a frame with these three values demonstrated. `BSize` reads the frame's logical rect size; `SetSize` forwards to `SetRect`, so neither accessor establishes the tempting universal `BSize <= nscoord_MAX` premise. That absence alone is not proof that this BSize and these margins coexist.

## Source-backed bounded domain

HEAD `gfx/src/nsCoord.h` defines `nscoord_MAX=1073741823` and `nscoord_MIN=-1073741823`. `nsStyleMargin::GetMargin` accepts length-only values and calls `LengthPercentage::ToLength`, which calls `StyleCSSPixelLength::ToAppUnits`. `DefaultLengthToAppUnits` explicitly clamps to those bounds. `nsIFrame::GetUsedMargin` uses this path when no UsedMarginProperty exists. The small empty-inline-block fixture has fixed literal block margins; its parallel inline-level layout also skips `CalculateBlockSideMargins`.

For **any** defined int32 total T, its truncating half lies in [-1073741824,1073741823]. If only the **opposite** margin e lies in [-1073741823,1073741823], the complement lies in [-2147483647,2147483646]. `literal_margin_range` proves this without assuming E is at most nscoord_MAX, or even assuming E nonnegative. It covers both groups/orientations when both literal margins remain on the direct style path. It excludes preexisting overflow while computing T or the raw offset.

The same margin bound cannot be applied to all synthesis calls without additional evidence. `GetUsedMargin` prioritizes a cached UsedMarginProperty. `SizeComputationInput::InitOffsets` records computed values and explicitly delegates later auto-margin adjustment. `CalculateBlockSideMargins`, flex final placement, and absolute-position resolution can write adjusted margins. In particular, `ComputeAbsPosBlockAutoMargin` assigns its supplied remaining-space nscoord directly to a single auto side, without a nscoord_MAX clamp. These are concrete reasons the literal conversion bound is not a global cached-margin invariant; they do not show the API witness reaches a baseline consumer. The negative-overconstraint early-return branch in `CalculateBlockSideMargins` also does **not** update that property, so using its local negative margin as an observed cached witness would be incorrect.

Border-box synthesis has zero additions. Padding/content synthesis uses negated used border/padding contributions and needs its own producer bounds; this audit does not silently substitute literal margin bounds for those contributions.

## Narrow response to the remaining obligation

For the small literal-margin experiment, the source-backed conditional range proof is sufficient to rule out a newly overflowing complement. For general adoption, either establish the required producer constraints across the affected synthesis callers, or make the new subtraction checked. A minimal admission policy could compute the complement in int64 and return it only when int32-representable, retaining the old raw result otherwise. That preserves old helper behavior on the explicitly unsupported range, rather than introducing new signed-overflow UB; it deliberately does **not** repair origin correctness there. Such a policy would need to be stated in the patch and tested, and would not remove preexisting overflow in earlier operations or downstream old callers.

Do not silently clamp to nscoord_MAX: it would change already-representable larger results. Saturating to int32 bounds also loses the exact midpoint and needs a separately justified fallback policy. This capsule recommends no native edit and does not claim the unrestricted patch safe or the API witness reachable. No native/browser/index activity occurred; source identities are pinned HEAD objects in SOURCE-PINS.json.
