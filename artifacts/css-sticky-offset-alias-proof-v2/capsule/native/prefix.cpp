
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <utility>
using nscoord = int32_t;
inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;
inline constexpr nscoord NS_AUTOOFFSET = nscoord_MAX;
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
