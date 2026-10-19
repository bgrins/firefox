#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
using nscoord = int32_t;
#define NS_ASSERTION(condition, message) assert(condition)
struct WritingMode {};
struct LogicalSize {};
struct nsPresContext {};
static std::vector<std::pair<char, int>> trace;
static int constructed = 0;
static int destroyed = 0;
struct LogicalMargin {
  nscoord start, end;
  int id;
  bool record;
  nscoord BStart(WritingMode) const {
    if (record) trace.emplace_back('S', id);
    return start;
  }
  nscoord BEnd(WritingMode) const {
    if (record) trace.emplace_back('E', id);
    return end;
  }
};
enum class StyleClear { None, Both };
struct Display { StyleClear mClear = StyleClear::None; };
struct nsIFrame {
  int id = -1;
  bool block = true, selfEmpty = true, empty = true, hidden = false;
  bool marginRoot = false, intersect = true;
  nscoord start = 0, end = 0, paddingStart = 0, paddingEnd = 0;
  nscoord preferred = 0, minimum = 0;
  nsIFrame* parent = nullptr;
  nsIFrame* descend = nullptr;
  nsIFrame* next = nullptr;
  Display display;
  WritingMode GetWritingMode() const { return {}; }
  nsPresContext* PresContext() { static nsPresContext context; return &context; }
  nsIFrame* GetParent() const { return parent; }
  nsIFrame* GetNextInFlow() const { return next; }
  bool IsSelfEmpty() const { trace.emplace_back('I', id); return selfEmpty; }
  bool IsEmpty() const { trace.emplace_back('F', id); return empty; }
  bool IsHiddenByContentVisibilityOfInFlowParentForLayout() const { return hidden; }
  const Display* StyleDisplay() const { return &display; }
};
struct Line {
  int id;
  bool inlined, empty, clearance;
  int dirty = 0;
  nsIFrame* mFirstChild = nullptr;
  bool HasClearance() const { return clearance; }
  void ClearHasClearance() { clearance = false; }
  void SetHasClearance() { clearance = true; }
  void MarkDirty() { ++dirty; }
  bool IsInline() const { trace.emplace_back('L', id); return inlined; }
  bool IsEmpty() const { return empty; }
};
using nsLineList = std::vector<Line>;
struct nsBlockFrame : nsIFrame {
  using LineIterator = nsLineList::iterator;
  struct FrameLines { nsLineList mLines; };
  nsLineList normal;
  FrameLines overflow;
  bool hasOverflow = false;
  LineIterator LinesBegin() { return normal.begin(); }
  LineIterator LinesEnd() { return normal.end(); }
  FrameLines* GetOverflowLines() { return hasOverflow ? &overflow : nullptr; }
  void IsMarginRoot(bool* startRoot, bool* endRoot) const {
    *startRoot = marginRoot;
    *endRoot = false;
  }
  static bool BlockCanIntersectFloats(nsIFrame* frame) { return frame->intersect; }
};
static nsBlockFrame* do_QueryFrame(nsIFrame* frame) {
  return frame->block ? static_cast<nsBlockFrame*>(frame) : nullptr;
}
static nsIFrame* DescendIntoBlockLevelFrame(nsIFrame* frame) {
  return frame->descend ? frame->descend : frame;
}
struct ReflowInput {
  nsIFrame* mFrame;
  bool counted = false;
  explicit ReflowInput(nsIFrame* frame) : mFrame(frame) {}
  ReflowInput(nsPresContext*, const ReflowInput&, nsIFrame* frame, LogicalSize)
      : mFrame(frame), counted(true) { ++constructed; }
  ~ReflowInput() { if (counted) ++destroyed; }
  WritingMode GetWritingMode() const { return {}; }
  LogicalSize ComputedSize(WritingMode) const { return {}; }
  LogicalMargin ComputedLogicalMargin(WritingMode) const {
    return {mFrame->start, mFrame->end, mFrame->id, true};
  }
  LogicalMargin ComputedLogicalBorderPadding(WritingMode) const {
    return {mFrame->paddingStart, mFrame->paddingEnd, mFrame->id, false};
  }
  nscoord ComputedBSize() const { return mFrame->preferred; }
  nscoord ComputedMinBSize() const { return mFrame->minimum; }
};
struct Metrics { WritingMode GetWritingMode() const { return {}; } };
