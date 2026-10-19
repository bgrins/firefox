#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>

using nscoord = int32_t;
#define MOZ_ASSERT_IF(condition, result) assert(!(condition) || (result))
constexpr nscoord NS_AUTOOFFSET = (1 << 30) - 1;
enum class LogicalAxis { Inline, Block };
enum class LogicalEdge { Start, End };
enum class LogicalSide { IStart, IEnd, BStart, BEnd };
LogicalSide MakeLogicalSide(LogicalAxis axis, LogicalEdge edge) {
  return LogicalSide(2 * int(axis) + int(edge));
}
struct WritingMode { int id; };
static std::array<int, 2> geometryReads;
using nsMargin = std::array<nscoord, 4>;
struct LogicalMargin {
  std::array<nscoord, 4> values{};
  nscoord Side(LogicalSide side, WritingMode) const { return values[int(side)]; }
  nscoord StartEnd(LogicalAxis axis, WritingMode) const {
    ++geometryReads[int(axis)];
    return values[2 * int(axis)] + values[2 * int(axis) + 1];
  }
  nscoord& IStart(WritingMode) { return values[0]; }
  nscoord& IEnd(WritingMode) { return values[1]; }
  nscoord& BStart(WritingMode) { return values[2]; }
  nscoord& BEnd(WritingMode) { return values[3]; }
  nsMargin GetPhysicalMargin(WritingMode wm) const {
    constexpr int mapping[6][4] = {{3,1,0,2},{1,3,0,2},{0,2,1,3},
                                   {2,0,1,3},{0,2,3,1},{2,0,3,1}};
    nsMargin result{};
    for (int side = 0; side < 4; ++side) { result[mapping[wm.id][side]] = values[side]; }
    return result;
  }
};
struct LogicalSize {
  std::array<nscoord, 2> values;
  nscoord Size(LogicalAxis axis, WritingMode) const {
    ++geometryReads[int(axis)];
    return values[int(axis)];
  }
};
struct nsIFrame;
struct ReflowInput;
struct AnchorPosResolutionCache {};
struct AnchorPosResolutionParams {
  static AnchorPosResolutionParams From(ReflowInput*) { return {}; }
  static AnchorPosResolutionParams From(nsIFrame*, AnchorPosResolutionCache*) { return {}; }
};
struct AnchorPosOffsetResolutionParams {
  const LogicalSize* cb;
  static AnchorPosOffsetResolutionParams ExplicitCBFrameSize(AnchorPosResolutionParams, const LogicalSize* size) {
    return {size};
  }
};
struct AutoValue {
  bool value = false;
  bool IsAuto() const { return value; }
};
struct StyleMargin {
  std::array<AutoValue, 4> tags;
  const AutoValue* GetMargin(LogicalSide side, WritingMode, AnchorPosResolutionParams) const {
    return &tags[int(side)];
  }
  bool HasInlineAxisAuto(WritingMode, AnchorPosResolutionParams) const { return tags[0].value || tags[1].value; }
  bool HasBlockAxisAuto(WritingMode, AnchorPosResolutionParams) const { return tags[2].value || tags[3].value; }
};
struct StylePosition {
  std::array<AutoValue, 4> resolved;
  mutable int requestedMask = 0;
  const AutoValue* GetAnchorResolvedInset(LogicalSide side, WritingMode, AnchorPosOffsetResolutionParams params) const {
    assert(params.cb);
    requestedMask |= 1 << int(side);
    return &resolved[int(side)];
  }
};
struct nsIFrame {
  StylePosition position;
  nsMargin used{};
  bool hasProperty = true;
  int propertyReads = 0;
  const struct StylePosition* StylePosition() const { return &position; }
  static int UsedMarginProperty() { return 7; }
  nsMargin* GetProperty(int key) { assert(key == 7); ++propertyReads; return hasProperty ? &used : nullptr; }
};
struct ReflowInput {
  ReflowInput* mParentReflowInput;
  const struct StyleMargin* mStyleMargin;
  nsIFrame* mFrame;
  WritingMode wm;
  LogicalMargin computed;
  int writes = 0;
  WritingMode GetWritingMode() const { return wm; }
  void SetComputedLogicalMargin(WritingMode, const LogicalMargin& margin) { computed = margin; ++writes; }
  static void ComputeAbsPosInlineAutoMargin(nscoord, WritingMode, bool, bool, LogicalMargin&);
  static void ComputeAbsPosBlockAutoMargin(nscoord, WritingMode, bool, bool, LogicalMargin&);
};
struct AbsoluteContainingBlock {
  void ResolveAutoMarginsAfterLayout(ReflowInput&, const LogicalSize&, const LogicalSize&,
                                    LogicalMargin&, const LogicalMargin& __FLAGS_DECL__);
  std::array<bool, 2> Caller(ReflowInput& kidReflowInput, const LogicalSize& cbSize,
                           const LogicalSize& kidSize, LogicalMargin& margin,
                           const LogicalMargin& offsets, nsIFrame* aKidFrame,
                           AnchorPosResolutionCache* aAnchorPosResolutionCache,
                           WritingMode outerWM);
};
