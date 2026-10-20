#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
using nscoord = int32_t;
template<class T> using Maybe = std::optional<T>;
constexpr nscoord NS_UNCONSTRAINEDSIZE = 1073741823;
#define MOZ_ASSERT(x, ...) assert(x)
struct FlexboxAxisTracker { bool column; bool IsColumnOriented() const { return column; } };
struct Frame { Maybe<nscoord> contained; Maybe<nscoord> ContainIntrinsicBSize() const { return contained; } };
struct ReflowInput {
  bool automatic; nscoord computed, lo, hi; Frame* mFrame;
  bool ShouldApplyAutomaticMinimumOnBlockAxis() const { return automatic; }
  nscoord ComputedBSize() const { return computed; }
  nscoord ComputedMinBSize() const { return lo; }
  nscoord ComputedMaxBSize() const { return hi; }
nscoord ApplyMinMaxBSize(nscoord aBSize, nscoord aConsumed = 0) const {
    aBSize += aConsumed;

    if (NS_UNCONSTRAINEDSIZE != ComputedMaxBSize()) {
      aBSize = std::min(aBSize, ComputedMaxBSize());
    }

    if (NS_UNCONSTRAINEDSIZE != ComputedMinBSize()) {
      aBSize = std::max(aBSize, ComputedMinBSize());
    }

    if (NS_UNCONSTRAINEDSIZE != ComputedMaxBSize()) aBSize = std::min(aBSize, ComputedMaxBSize()); return aBSize - aConsumed;
  }
};
class nsFlexContainerFrame { public:
  nscoord ComputeCrossSize(const ReflowInput&, const FlexboxAxisTracker&, nscoord, nscoord, bool*) const;
};
nscoord nsFlexContainerFrame::ComputeCrossSize(
    const ReflowInput& aReflowInput, const FlexboxAxisTracker& aAxisTracker,
    const nscoord aTentativeContentBoxCrossSize, nscoord aSumLineCrossSizes,
    bool* aIsDefinite) const {
  MOZ_ASSERT(aIsDefinite, "outparam pointer must be non-null");

  if (aAxisTracker.IsColumnOriented()) {
    // Column-oriented --> our cross axis is the inline axis, so our cross size
    // is our inline size (which should already be resolved).
    *aIsDefinite = true;
    // FIXME: Bug 1661847 - there are cases where aTentativeContentBoxCrossSize
    // (i.e. aReflowInput.ComputedISize()) might not be the right thing to
    // return here. Specifically: if our cross size is an intrinsic size, and we
    // have flex items that are flexible and have aspect ratios, then we may
    // need to take their post-flexing main sizes into account (multiplied
    // through their aspect ratios to get their cross sizes), in order to
    // determine their flex line's size & the flex container's cross size (e.g.
    // as `aSumLineCrossSizes`).
    return aTentativeContentBoxCrossSize;
  }

  const bool shouldApplyAutomaticMinimumOnBlockAxis =
      aReflowInput.ShouldApplyAutomaticMinimumOnBlockAxis();
  const nscoord computedBSize = aReflowInput.ComputedBSize();
  if (computedBSize != NS_UNCONSTRAINEDSIZE &&
      !shouldApplyAutomaticMinimumOnBlockAxis) {
    // Row-oriented case (cross axis is block-axis), with fixed BSize:
    *aIsDefinite = true;

    // Just use our fixed block-size because we always assume the available
    // block-size is unconstrained, and the reflow input has already done the
    // appropriate min/max-BSize clamping.
    return computedBSize;
  }

  // Row-oriented case, with size-containment in block axis:
  // Behave as if we had no content and just use our MinBSize.
  if (Maybe<nscoord> containBSize =
          aReflowInput.mFrame->ContainIntrinsicBSize()) {
    *aIsDefinite = true;
    return aReflowInput.ApplyMinMaxBSize(*containBSize);
  }

  // The cross size must not be definite in the following cases.
  *aIsDefinite = false;

  const nscoord contentBSize =
      aReflowInput.ApplyMinMaxBSize(aSumLineCrossSizes);
  // If the content block-size is larger than the effective computed
  // block-size, we extend the block-size to contain all the content.
  // https://drafts.csswg.org/css-sizing-4/#aspect-ratio-minimum
  if (shouldApplyAutomaticMinimumOnBlockAxis) {
    // Row-oriented case (cross axis is block-axis), with auto BSize which is
    // resolved by aspect-ratio or content size.
    return std::max(contentBSize, computedBSize);
  }

  // Row-oriented case (cross axis is block axis), with auto BSize:
  // Shrink-wrap our line(s), subject to our min-size / max-size
  // constraints in that (block) axis.
  return contentBSize;
}
int main() {
  int column, automatic, contained;
  int32_t computed, lo, hi;
  int64_t total;
  while (std::cin >> column >> automatic >> computed >> contained >> lo >> hi >> total) {
    Frame f{contained ? Maybe<nscoord>(3000) : std::nullopt};
    ReflowInput input{bool(automatic),computed,lo,hi,&f};
    bool definite=false;
    nscoord result=nsFlexContainerFrame().ComputeCrossSize(input, {bool(column)}, 8000,
      std::min<int64_t>(1073741823,total), &definite);
    std::cout << result << " " << definite << "\n";
  }
}
