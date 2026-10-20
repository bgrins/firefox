
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <utility>
using nscoord = int32_t;
inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;
inline constexpr nscoord nscoord_MIN = -nscoord_MAX;
inline constexpr nscoord NS_UNCONSTRAINEDSIZE = nscoord_MAX;
inline constexpr nscoord NS_AUTOOFFSET = NS_UNCONSTRAINEDSIZE;
static_assert(nscoord_MAX == 1073741823 && nscoord_MIN == -1073741823 && NS_AUTOOFFSET == nscoord_MAX);
enum Side { eSideTop, eSideRight, eSideBottom, eSideLeft };
enum class StylePositionProperty { Sticky };
struct AnchorPosOffsetResolutionParams {
  static AnchorPosOffsetResolutionParams UseCBFrameSize(std::pair<void*, StylePositionProperty> input) {
    assert(input.first == nullptr && input.second == StylePositionProperty::Sticky);
    return {};
  }
};
int queriedSide, queries, resolves;
nscoord seenBasis;
struct LengthPercentage { nscoord resolved; };
struct Inset {
  bool automatic;
  LengthPercentage value;
  bool IsAuto() const { return automatic; }
  const LengthPercentage& AsLengthPercentage() const { assert(!automatic); return value; }
};
struct nsStylePosition {
  Inset insets[4];
  const Inset* GetAnchorResolvedInset(Side side, AnchorPosOffsetResolutionParams) const {
    queriedSide = side;
    ++queries;
    return &insets[side];
  }
};
struct nsLayoutUtils {
  static nscoord ComputeCBDependentValue(nscoord basis, const LengthPercentage& value) {
    ++resolves;
    seenBasis = basis;
    return value.resolved;
  }
};
static nscoord ComputeStickySideOffset(Side aSide,
                                       const nsStylePosition& aPosition,
                                       nscoord aPercentBasis) {
  // Guaranteed to resolve any use of anchor function as invalid.
  const auto& side = aPosition.GetAnchorResolvedInset(
      aSide, AnchorPosOffsetResolutionParams::UseCBFrameSize(
                 {nullptr, StylePositionProperty::Sticky}));
  if (side->IsAuto()) {
    return NS_AUTOOFFSET;
  }
  // Reserve NS_AUTOOFFSET for actual auto insets.
  return std::min(
      NS_AUTOOFFSET - 2,
      nsLayoutUtils::ComputeCBDependentValue(aPercentBasis,
                                            side->AsLengthPercentage()));
}
int main() {
  int side, automatic;
  nscoord value, basis;
  while (std::cin >> side >> automatic >> value >> basis) {
    assert(side >= 0 && side < 4 && (automatic == 0 || automatic == 1));
    nsStylePosition position;
    for (int i = 0; i < 4; ++i) position.insets[i] = {false, {7 + i}};
    position.insets[side] = {automatic != 0, {value}};
    queriedSide = -1; queries = resolves = 0; seenBasis = -1;
    nscoord result = ComputeStickySideOffset(static_cast<Side>(side), position, basis);
    std::cout << result << ' ' << queriedSide << ' ' << queries << ' ' << resolves << ' ' << seenBasis << '\n';
  }
}
