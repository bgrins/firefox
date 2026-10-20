#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <optional>
#include <unordered_set>

using nscoord = int32_t;
constexpr uint32_t NS_FRAME_IS_DIRTY = 1;
constexpr uint32_t NS_FRAME_HAS_DIRTY_CHILDREN = 2;
constexpr uint32_t NS_FRAME_IN_REFLOW = 4;
constexpr uint32_t NS_FRAME_FIRST_REFLOW = 8;
constexpr uint32_t NS_FRAME_OWNS_ANON_BOXES = 16;
constexpr int NS_UNCONSTRAINEDSIZE = 1073741823;
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define FLEX_ITEM_LOG(...) ((void)0)
#define NS_FRAME_TRACE(...) ((void)0)

struct WritingMode { bool IsPhysicalRTL() const { return false; } };
struct LogicalSize {
  nscoord i = 0, b = 0;
  nscoord BSize(WritingMode) const { return b; }
  bool operator==(const LogicalSize&) const = default;
};
struct LogicalMargin {
  nscoord is = 0, ie = 0, bs = 0, be = 0;
  nscoord BStartEnd(WritingMode) const { return bs + be; }
  bool operator==(const LogicalMargin&) const = default;
};
struct nsSize { nscoord width = 0, height = 0; };
struct LogicalPoint { explicit LogicalPoint(WritingMode) {} };
struct LogicalRect {
  LogicalSize size;
  LogicalRect(WritingMode, LogicalPoint, LogicalSize s) : size(s) {}
};
struct nsPresContext { void ReflowedFrame() {} };
struct AnchorPosResolutionParams {
  template<class T> static int From(T) { return 0; }
};
struct StyleSize { bool HasPercent() const { return false; } };
struct StylePosition {
  const StyleSize* BSize(WritingMode, int) const { static StyleSize s; return &s; }
};
struct StyleRecord { bool IsAnonBox() const { return false; } };
struct ReflowInput;
struct PercentObserver { void NotifyPercentBSize(const ReflowInput&) {} };
struct nsIFrame;
struct ReflowInput {
  nsIFrame* mFrame = nullptr;
  LogicalSize computed, mContainingBlockSize;
  LogicalMargin bp;
  nscoord minB = 0, maxB = 1000, availableB = 1000;
  PercentObserver* mPercentBSizeObserver = nullptr;
  StylePosition* mStylePosition = nullptr;
  void* mStyleDisplay = nullptr;
  LogicalSize ComputedSize() const { return computed; }
  nscoord ComputedMinBSize() const { return minB; }
  nscoord ComputedMaxBSize() const { return maxB; }
  nscoord AvailableBSize() const { return availableB; }
  WritingMode GetWritingMode() const { return {}; }
  LogicalMargin ComputedLogicalBorderPadding(WritingMode) const { return bp; }
  LogicalMargin ComputedLogicalOffsets(WritingMode) const { return {}; }
  static void ApplyRelativePositioning(nsIFrame*, WritingMode, LogicalMargin,
                                      LogicalPoint*, nsSize) { assert(false); }
};
struct ReflowOutput {
  LogicalSize size;
  explicit ReflowOutput(const ReflowInput&) {}
  LogicalSize Size(WritingMode) const { return size; }
  nscoord BSize(WritingMode) const { return size.b; }
  nscoord BlockStartAscent() const { return 0; }
};
struct nsReflowStatus { bool IsComplete() const { return true; } };
class PresShell;
struct nsIFrame {
  enum class ReflowChildFlags { Default = 0, NoMoveFrame = 1, ApplyRelativePositioning = 2 };
  uint32_t state = 0;
  LogicalSize geometry;
  nsIFrame* parent = nullptr;
  ::PresShell* shell = nullptr;
  bool hidden = false;
  void* cache = nullptr;
  bool IsSubtreeDirty() const { return state & (NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN); }
  void AddStateBits(uint32_t bits) { state |= bits; }
  void RemoveStateBits(uint32_t bits) { state &= ~bits; }
  bool HasAnyStateBits(uint32_t bits) const { return state & bits; }
  nsIFrame* GetInFlowParent() const { return parent; }
  nsIFrame* GetNextContinuation() const { return nullptr; }
  nsIFrame* GetPrevInFlow() const { return nullptr; }
  bool HidesContent() const { return hidden; }
  bool HidesContentForLayout() const;
  bool IsHiddenByContentVisibilityOfInFlowParentForLayout() const;
  ::PresShell* PresShell() const { return shell; }
  const nsIFrame* GetContent() const { return this; }
  const StyleRecord* Style() const { static StyleRecord s; return &s; }
  void SetSize(WritingMode, LogicalSize size) { geometry = size; }
  void SetRect(WritingMode, LogicalRect rect, nsSize) { geometry = rect.size; }
  void SetHasBSizeChange(bool) {}
  void SetHasPaddingChange(bool) {}
  bool IsMathMLFrame() const { return false; }
  bool IsTableCellFrame() const { return false; }
  void FinishAndStoreOverflow(ReflowOutput*, void*) {}
  void DidReflow(nsPresContext*, const ReflowInput*);
  void Reflow(nsPresContext*, ReflowOutput&, const ReflowInput&);
  template<class T> T* GetProperty(T*) { return static_cast<T*>(cache); }
  template<class T> void SetProperty(T*, T* value) { cache = value; }
};
int operator&(nsIFrame::ReflowChildFlags a, nsIFrame::ReflowChildFlags b) {
  return int(a) & int(b);
}
bool operator!=(nsIFrame::ReflowChildFlags a, int b) { return int(a) != b; }
using ReflowChildFlags = nsIFrame::ReflowChildFlags;
namespace SVGObserverUtils { void InvalidateDirectRenderingObservers(nsIFrame*) {} }
class nsContainerFrame {
public:
  static void FinishReflowChild(nsIFrame*, nsPresContext*, const ReflowOutput&,
                               const ReflowInput*, const WritingMode&,
                               const LogicalPoint&, const nsSize&, ReflowChildFlags);
};
class nsFlexContainerFrame : public nsContainerFrame {
public:
  class CachedBAxisMeasurement;
  class CachedFlexItemData;
  struct FlexItem {
    nsIFrame* frame;
    nsIFrame* Frame() const { return frame; }
    void SetHadMeasuringReflow() {}
    void SetAscent(nscoord) {}
  };
  nsPresContext context;
  int reflows = 0;
  WritingMode GetWritingMode() const { return {}; }
  nsPresContext* PresContext() { return &context; }
  void MaybePropagateRelativeBSizeFlagFrom(FlexItem&) {}
  void ReflowChild(nsIFrame* f, nsPresContext* c, ReflowOutput& out,
                   ReflowInput& in, WritingMode, LogicalPoint, nsSize,
                   ReflowChildFlags, nsReflowStatus&) {
    ++reflows;
    f->Reflow(c, out, in);
  }
  const CachedBAxisMeasurement& MeasureBSizeForFlexItem(FlexItem&, ReflowInput&);
};
using CachedBAxisMeasurement = nsFlexContainerFrame::CachedBAxisMeasurement;
using CachedFlexItemData = nsFlexContainerFrame::CachedFlexItemData;
enum class FlexItemReflowType { Measuring };
enum class IntrinsicDirty { None };
enum class FlushType { Layout };
struct FrameSet {
  std::unordered_set<const nsIFrame*> values;
  bool IsEmpty() const { return values.empty(); }
  void Insert(const nsIFrame* p) { values.insert(p); }
  bool Contains(const nsIFrame* p) const { return values.contains(p); }
  void Clear() { values.clear(); }
};
struct Document {
  std::function<void()> flush;
  void FlushPendingNotifications(FlushType) { flush(); }
};
class PresShell {
public:
  FrameSet mHiddenContentInForcedLayout;
  Document* mDocument;
  int forces = 0;
  void FrameNeedsReflow(nsIFrame*, IntrinsicDirty, uint32_t) { ++forces; }
  void UpdateHiddenContentInForcedLayout(nsIFrame*);
  void EnsureReflowIfFrameHasHiddenContent(nsIFrame*);
  bool IsForcingLayoutForHiddenContent(const nsIFrame*) const;
  bool ReflowForHiddenContentIfNeeded();
};
int providerMode = 0;
LogicalSize Provider(const ReflowInput& in) {
  return {in.computed.i + in.bp.is + in.bp.ie + providerMode,
          std::max(in.minB, std::min(in.maxB, in.computed.b)) + in.bp.bs + in.bp.be + 2 * providerMode};
}
