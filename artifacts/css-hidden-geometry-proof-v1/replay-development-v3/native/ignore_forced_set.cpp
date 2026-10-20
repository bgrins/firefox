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

class nsFlexContainerFrame::CachedBAxisMeasurement {
  struct Key {
    const LogicalSize mComputedSize;
    const LogicalSize mContainingBlockSize;
    const LogicalMargin mBorderPadding;
    const nscoord mComputedMinBSize;
    const nscoord mComputedMaxBSize;
    const nscoord mAvailableBSize;

    explicit Key(const ReflowInput& aRI)
        : mComputedSize(aRI.ComputedSize()),
          mContainingBlockSize(aRI.mContainingBlockSize),
          mBorderPadding(
              aRI.ComputedLogicalBorderPadding(aRI.GetWritingMode())),
          mComputedMinBSize(aRI.ComputedMinBSize()),
          mComputedMaxBSize(aRI.ComputedMaxBSize()),
          mAvailableBSize(aRI.AvailableBSize()) {}

    bool operator==(const Key& aOther) const = default;
  };

  const Key mKey;

  // This could/should be const, but it's non-const for now just because it's
  // assigned via a series of steps in the constructor body:
  nscoord mBSize;

 public:
  CachedBAxisMeasurement(const ReflowInput& aReflowInput,
                         const ReflowOutput& aReflowOutput)
      : mKey(aReflowInput) {
    // To get content-box bsize, we have to subtract off border & padding
    // (and floor at 0 in case the border/padding are too large):
    WritingMode itemWM = aReflowInput.GetWritingMode();
    nscoord borderBoxBSize = aReflowOutput.BSize(itemWM);
    mBSize =
        borderBoxBSize -
        aReflowInput.ComputedLogicalBorderPadding(itemWM).BStartEnd(itemWM);
    mBSize = std::max(0, mBSize);
  }

  /**
   * Returns true if this cached flex item measurement is valid for (i.e. can
   * be expected to match the output of) a measuring reflow whose input
   * parameters are given via aReflowInput.
   */
  bool IsValidFor(const ReflowInput& aReflowInput) const {
    return mKey == Key(aReflowInput);
  }

  nscoord BSize() const { return mBSize; }
};
class nsFlexContainerFrame::CachedFlexItemData {
public:
  std::optional<CachedBAxisMeasurement> mBAxisMeasurement;
  CachedFlexItemData(const ReflowInput& in, const ReflowOutput& out,
                    FlexItemReflowType type) { Update(in, out, type); }
  void Update(const ReflowInput& in, const ReflowOutput& out, FlexItemReflowType) {
    mBAxisMeasurement.reset();
    mBAxisMeasurement.emplace(in, out);
  }
  static CachedFlexItemData* Prop() { return nullptr; }
};

void nsIFrame::Reflow(nsPresContext*, ReflowOutput& aMetrics, const ReflowInput& aReflowInput) {
if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      !GetNextContinuation()) {
    FinishAndStoreOverflow(&aMetrics, aReflowInput.mStyleDisplay);
    return;
  }
 aMetrics.size = Provider(aReflowInput);
}

bool nsIFrame::HidesContentForLayout() const {
  return HidesContent() && !PresShell()->IsForcingLayoutForHiddenContent(this);
}
bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const {
  const auto* parent = GetInFlowParent();
  // The anonymous children owned by parent are important for properly sizing
  // their parents.
  return parent && parent->HidesContentForLayout() &&
         !(parent->HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES) &&
           Style()->IsAnonBox());
}
void nsIFrame::DidReflow(nsPresContext* aPresContext,
                         const ReflowInput* aReflowInput) {
  NS_FRAME_TRACE(NS_FRAME_TRACE_CALLS, ("nsIFrame::DidReflow"));

  if (IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
    RemoveStateBits(NS_FRAME_IN_REFLOW);
    return;
  }

  SVGObserverUtils::InvalidateDirectRenderingObservers(this);

  RemoveStateBits(NS_FRAME_IN_REFLOW | NS_FRAME_FIRST_REFLOW |
                  NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN);

  // Clear bits that were used in ReflowInput::InitResizeFlags (see
  // comment there for why we can't clear it there).
  SetHasBSizeChange(false);
  SetHasPaddingChange(false);

  // Notify the percent bsize observer if there is a percent bsize.
  // The observer may be able to initiate another reflow with a computed
  // bsize. This happens in the case where a table cell has no computed
  // bsize but can fabricate one when the cell bsize is known.
  if (aReflowInput && aReflowInput->mPercentBSizeObserver && !GetPrevInFlow()) {
    const auto bsize = aReflowInput->mStylePosition->BSize(
        aReflowInput->GetWritingMode(),
        AnchorPosResolutionParams::From(aReflowInput));
    if (bsize->HasPercent()) {
      aReflowInput->mPercentBSizeObserver->NotifyPercentBSize(*aReflowInput);
    }
  }

  aPresContext->ReflowedFrame();
}
void nsContainerFrame::FinishReflowChild(
    nsIFrame* aKidFrame, nsPresContext* aPresContext,
    const ReflowOutput& aDesiredSize, const ReflowInput* aReflowInput,
    const WritingMode& aWM, const LogicalPoint& aPos,
    const nsSize& aContainerSize, nsIFrame::ReflowChildFlags aFlags) {
  MOZ_ASSERT(!aReflowInput || aReflowInput->mFrame == aKidFrame);
  MOZ_ASSERT(aReflowInput || aKidFrame->IsMathMLFrame() ||
                 aKidFrame->IsTableCellFrame(),
             "aReflowInput should be passed in almost all cases");

  if (aWM.IsPhysicalRTL()) {
    NS_ASSERTION(aContainerSize.width != NS_UNCONSTRAINEDSIZE,
                 "FinishReflowChild with unconstrained container width!");
  }

  const LogicalSize convertedSize = aDesiredSize.Size(aWM);
  LogicalPoint pos(aPos);

  if (aFlags & ReflowChildFlags::ApplyRelativePositioning) {
    MOZ_ASSERT(aReflowInput, "caller must have passed reflow input");
    // ApplyRelativePositioning in right-to-left writing modes needs to know
    // the updated frame width to set the normal position correctly.
    aKidFrame->SetSize(aWM, convertedSize);

    const LogicalMargin offsets = aReflowInput->ComputedLogicalOffsets(aWM);
    ReflowInput::ApplyRelativePositioning(aKidFrame, aWM, offsets, &pos,
                                          aContainerSize);
  }

  if (ReflowChildFlags::NoMoveFrame !=
      (aFlags & ReflowChildFlags::NoMoveFrame)) {
    aKidFrame->SetRect(aWM, LogicalRect(aWM, pos, convertedSize),
                       aContainerSize);
  } else {
    aKidFrame->SetSize(aWM, convertedSize);
  }

  aKidFrame->DidReflow(aPresContext, aReflowInput);
}
void PresShell::UpdateHiddenContentInForcedLayout(nsIFrame* aFrame) {
  if (!aFrame || !aFrame->IsSubtreeDirty()) {
    return;
  }

  nsIFrame* topmostFrameWithContentHidden = nullptr;
  for (nsIFrame* cur = aFrame->GetInFlowParent(); cur;
       cur = cur->GetInFlowParent()) {
    if (cur->HidesContent()) {
      topmostFrameWithContentHidden = cur;
      mHiddenContentInForcedLayout.Insert(cur->GetContent());
    }
  }

  if (mHiddenContentInForcedLayout.IsEmpty()) {
    return;
  }

  // Queue and immediately flush a reflow for this node.
  MOZ_ASSERT(topmostFrameWithContentHidden);
  FrameNeedsReflow(topmostFrameWithContentHidden, IntrinsicDirty::None,
                   NS_FRAME_IS_DIRTY);
}
void PresShell::EnsureReflowIfFrameHasHiddenContent(nsIFrame* aFrame) {
  MOZ_ASSERT(mHiddenContentInForcedLayout.IsEmpty());

  UpdateHiddenContentInForcedLayout(aFrame);
  ReflowForHiddenContentIfNeeded();
}
bool PresShell::IsForcingLayoutForHiddenContent(const nsIFrame* aFrame) const {
  return false;
}
bool PresShell::ReflowForHiddenContentIfNeeded() {
  if (mHiddenContentInForcedLayout.IsEmpty()) {
    return false;
  }
  mDocument->FlushPendingNotifications(FlushType::Layout);
  mHiddenContentInForcedLayout.Clear();
  return true;
}
const CachedBAxisMeasurement& nsFlexContainerFrame::MeasureBSizeForFlexItem(
    FlexItem& aItem, ReflowInput& aChildReflowInput) {
  auto* cachedData = aItem.Frame()->GetProperty(CachedFlexItemData::Prop());

  if (cachedData && cachedData->mBAxisMeasurement) {
    if (!aItem.Frame()->IsSubtreeDirty() &&
        cachedData->mBAxisMeasurement->IsValidFor(aChildReflowInput)) {
      FLEX_ITEM_LOG(aItem.Frame(),
                    "[perf] Accepted cached measurement: block-size %d",
                    cachedData->mBAxisMeasurement->BSize());
      return *(cachedData->mBAxisMeasurement);
    }
    FLEX_ITEM_LOG(aItem.Frame(),
                  "[perf] Rejected cached measurement: block-size %d",
                  cachedData->mBAxisMeasurement->BSize());
  } else {
    FLEX_ITEM_LOG(aItem.Frame(), "[perf] No cached measurement");
  }

  if (aItem.Frame()->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
    aItem.Frame()->AddStateBits(NS_FRAME_IS_DIRTY);
  }

  // CachedFlexItemData is stored in item's writing mode, so we pass
  // aChildReflowInput into ReflowOutput's constructor.
  ReflowOutput childReflowOutput(aChildReflowInput);
  nsReflowStatus childStatus;

  const ReflowChildFlags flags = ReflowChildFlags::NoMoveFrame;
  const WritingMode outerWM = GetWritingMode();
  const LogicalPoint dummyPosition(outerWM);
  const nsSize dummyContainerSize;

  // We use NoMoveFrame, so the position and container size used here are
  // unimportant.
  ReflowChild(aItem.Frame(), PresContext(), childReflowOutput,
              aChildReflowInput, outerWM, dummyPosition, dummyContainerSize,
              flags, childStatus);
  aItem.SetHadMeasuringReflow();
  MaybePropagateRelativeBSizeFlagFrom(aItem);

  // We always use unconstrained available block-size to measure flex items,
  // which means they should always complete.
  MOZ_ASSERT(childStatus.IsComplete(),
             "We gave flex item unconstrained available block-size, so it "
             "should be complete");

  // Tell the child we're done with its initial reflow.
  // (Necessary for e.g. GetBaseline() to work below w/out asserting)
  FinishReflowChild(aItem.Frame(), PresContext(), childReflowOutput,
                    &aChildReflowInput, outerWM, dummyPosition,
                    dummyContainerSize, flags);

  aItem.SetAscent(childReflowOutput.BlockStartAscent());

  // Update (or add) our cached measurement, so that we can hopefully skip this
  // measuring reflow the next time around:
  if (cachedData) {
    cachedData->Update(aChildReflowInput, childReflowOutput,
                       FlexItemReflowType::Measuring);
  } else {
    cachedData = new CachedFlexItemData(aChildReflowInput, childReflowOutput,
                                        FlexItemReflowType::Measuring);
    aItem.Frame()->SetProperty(CachedFlexItemData::Prop(), cachedData);
  }
  return *(cachedData->mBAxisMeasurement);
}
int main() {
  int id = 0;
  for (int hidden = 0; hidden < 2; ++hidden)
  for (int dirty = 0; dirty < 2; ++dirty)
  for (int cacheMode = 0; cacheMode < 3; ++cacheMode)
  for (int sizeMode = 0; sizeMode < 2; ++sizeMode)
  for (int border = 0; border < 2; ++border)
  for (int provider = 0; provider < 2; ++provider)
  for (int forceKeyMode = 0; forceKeyMode < 2; ++forceKeyMode) {
    providerMode = provider;
    Document document;
    PresShell shell;
    shell.mDocument = &document;
    nsIFrame parent, frame;
    parent.hidden = hidden;
    parent.shell = frame.shell = &shell;
    frame.parent = &parent;
    frame.state = dirty ? NS_FRAME_IS_DIRTY : 0;
    ReflowInput current;
    current.mFrame = &frame;
    current.computed = sizeMode ? LogicalSize{17, 13} : LogicalSize{24, 32};
    current.mContainingBlockSize = {320, 0};
    current.bp = {border, border * 2, border * 3, border * 4};
    ReflowInput cached = current;
    if (cacheMode == 2) cached.mContainingBlockSize.b = 32;
    ReflowOutput prior(cached);
    prior.size = Provider(cached);
    frame.geometry = prior.size;
    if (cacheMode) frame.cache = new CachedFlexItemData(cached, prior, FlexItemReflowType::Measuring);
    nsFlexContainerFrame container;
    nsFlexContainerFrame::FlexItem item{&frame};
    const nscoord measured = container.MeasureBSizeForFlexItem(item, current).BSize();
    const LogicalSize after = frame.geometry;
    const bool afterDirty = frame.IsSubtreeDirty();
    const bool reused = container.reflows == 0;
    ReflowInput forced = current;
    forced.mContainingBlockSize.b = forceKeyMode ? 32 : 0;
    document.flush = [&] { container.MeasureBSizeForFlexItem(item, forced); };
    shell.EnsureReflowIfFrameHasHiddenContent(&frame);
    const LogicalSize queried = frame.geometry;
    const bool queryDirty = frame.IsSubtreeDirty();
    const int forces = shell.forces;
    shell.EnsureReflowIfFrameHasHiddenContent(&frame);
    std::cout << id++ << ',' << after.i << ',' << after.b << ',' << afterDirty
              << ',' << measured << ',' << reused << ',' << queried.i << ','
              << queried.b << ',' << queryDirty << ',' << forces << ','
              << frame.geometry.i << ',' << frame.geometry.b << ','
              << frame.IsSubtreeDirty() << ',' << shell.forces << '\n';
    delete static_cast<CachedFlexItemData*>(frame.cache);
  }
}
