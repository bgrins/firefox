#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
#include <string>
#define MOZ_ASSERT(condition, ...) assert(condition)
#define NS_ASSERTION(condition, ...) assert(condition)
#define CHECK_WRITING_MODE(mode)
using nscoord = int32_t;
constexpr nscoord NS_UNCONSTRAINEDSIZE = 1073741823;
struct nsPoint {
  nscoord x, y;
  nsPoint(nscoord a = 0, nscoord b = 0) : x(a), y(b) {}
  nsPoint& operator+=(nsPoint other) { x += other.x; y += other.y; return *this; }
};
nsPoint operator+(nsPoint a, nsPoint b) { a += b; return a; }
struct nsSize {
  nscoord width, height;
  nsSize(nscoord w = 0, nscoord h = 0) : width(w), height(h) {}
};
nsSize operator-(nsSize a, nsSize b) { return {a.width-b.width, a.height-b.height}; }
struct nsMargin { nscoord left, top, right, bottom; };
struct nsRect {
  nscoord x,y,width,height;
  nsRect(nscoord a, nscoord b, nscoord c, nscoord d) : x(a),y(b),width(c),height(d) {}
};
struct WritingMode {
  bool vertical, lr, reversed;
  bool IsVertical() const { return vertical; }
  bool IsVerticalLR() const { return lr; }
  bool IsInlineReversed() const { return reversed; }
  bool IsPhysicalRTL() const { return vertical ? !lr : reversed; }
};
namespace mozilla {
using ::WritingMode;
struct LogicalPoint {
  nsPoint mPoint;
  LogicalPoint(WritingMode, nscoord i, nscoord b) : mPoint(i,b) {}
  LogicalPoint(WritingMode aWritingMode, const nsPoint& aPoint,
               const nsSize& aContainerSize)
#ifdef DEBUG
      : mWritingMode(aWritingMode)
#endif
  {
    if (aWritingMode.IsVertical()) {
      I() = aWritingMode.IsInlineReversed() ? aContainerSize.height - aPoint.y
                                            : aPoint.y;
      B() = aWritingMode.IsVerticalLR() ? aPoint.x
                                        : aContainerSize.width - aPoint.x;
    } else {
      I() = aWritingMode.IsInlineReversed() ? aContainerSize.width - aPoint.x
                                            : aPoint.x;
      B() = aPoint.y;
    }
  }
  nscoord& I() { return mPoint.x; }
  nscoord& B() { return mPoint.y; }
  nscoord I() const { return mPoint.x; }
  nscoord B() const { return mPoint.y; }
  nscoord I(WritingMode) const { return I(); }
  nsPoint GetPhysicalPoint(WritingMode aWritingMode,
                           const nsSize& aContainerSize) const {
    CHECK_WRITING_MODE(aWritingMode);
    if (aWritingMode.IsVertical()) {
      return nsPoint(
          aWritingMode.IsVerticalLR() ? B() : aContainerSize.width - B(),
          aWritingMode.IsInlineReversed() ? aContainerSize.height - I() : I());
    } else {
      return nsPoint(
          aWritingMode.IsInlineReversed() ? aContainerSize.width - I() : I(),
          B());
    }
  }
};
}
using mozilla::LogicalPoint;
struct LogicalSize { nsSize physical; };
struct LogicalMargin {
  nsMargin physical;
  nsMargin GetPhysicalMargin(WritingMode) const { return physical; }
};
struct LogicalRect {
  nscoord mIStart,mBStart,mISize,mBSize;
  LogicalRect(WritingMode w, LogicalPoint p, LogicalSize s)
      : mIStart(p.I()), mBStart(p.B()),
        mISize(w.IsVertical() ? s.physical.height : s.physical.width),
        mBSize(w.IsVertical() ? s.physical.width : s.physical.height) {}
  nscoord IStart() const { return mIStart; }
  nscoord BStart() const { return mBStart; }
  nscoord ISize() const { return mISize; }
  nscoord BSize() const { return mBSize; }
  nscoord IEnd() const { return mIStart + mISize; }
  nscoord BEnd() const { return mBStart + mBSize; }
  nsRect GetPhysicalRect(WritingMode aWritingMode,
                         const nsSize& aContainerSize) const {
    CHECK_WRITING_MODE(aWritingMode);
    if (aWritingMode.IsVertical()) {
      return nsRect(aWritingMode.IsVerticalLR() ? BStart()
                                                : aContainerSize.width - BEnd(),
                    aWritingMode.IsInlineReversed()
                        ? aContainerSize.height - IEnd()
                        : IStart(),
                    BSize(), ISize());
    } else {
      return nsRect(aWritingMode.IsInlineReversed()
                        ? aContainerSize.width - IEnd()
                        : IStart(),
                    BStart(), ISize(), BSize());
    }
  }
};

enum class StylePositionProperty { Static, Relative, Sticky };
struct nsStyleDisplay { StylePositionProperty mPosition; };
using StyleDisplayValue = nsStyleDisplay;
struct nsPresContext {};
struct ReflowInput;
struct nsIFrame {
  struct Rect {
    nsPoint position;
    nsSize size;
    nsSize Size() const { return size; }
  } mRect;
  enum class ReflowChildFlags : uint32_t {
    Default = 0, NoMoveFrame = 1, NoDeleteNextInFlowChild = 2, ApplyRelativePositioning = 4
  };
  std::optional<nsPoint> normal;
  StyleDisplayValue display{StylePositionProperty::Relative};
  bool svg = false;
  unsigned didReflowCalls = 0;
  static int NormalPositionProperty() { return 0; }
  bool HasProperty(int) const { return normal.has_value(); }
  nsPoint GetProperty(int, bool* present) const { *present=normal.has_value(); return normal.value_or(nsPoint{}); }
  void SetProperty(int, nsPoint p) { normal = p; }
  void AddProperty(int, nsPoint p) { assert(!normal); normal = p; }
  void SetPosition(nsPoint p) { mRect.position = p; }
  nsPoint GetPosition() const { return mRect.position; }
  nsSize GetSize() const { return mRect.size; }
  const StyleDisplayValue* StyleDisplay() const { return &display; }
  bool IsRelativelyPositioned() const { return display.mPosition == StylePositionProperty::Relative && !svg; }
  bool IsRelativelyOrStickyPositioned() const { return display.mPosition != StylePositionProperty::Static && !svg; }
  bool IsMathMLFrame() const { return false; }
  bool IsTableCellFrame() const { return false; }
  nsPoint GetNormalPosition(bool* aHasProperty = nullptr) const;
  LogicalPoint GetLogicalNormalPosition(WritingMode aWritingMode, const nsSize& aContainerSize) const;
  nscoord IStart(WritingMode w, nsSize c) const { return LogicalPoint(w, GetPosition(), c-GetSize()).I(w); }
  void SetSize(WritingMode, LogicalSize s) { mRect.size = s.physical; }
  void SetRect(WritingMode w, LogicalRect r, nsSize c) {
    const nsRect physical = r.GetPhysicalRect(w,c);
    mRect.size = {physical.width,physical.height};
    mRect.position = {physical.x,physical.y};
  }
  void DidReflow(nsPresContext*, const ReflowInput*) { ++didReflowCalls; }
};
using ReflowChildFlags = nsIFrame::ReflowChildFlags;
ReflowChildFlags operator|(ReflowChildFlags a, ReflowChildFlags b) {
  return static_cast<ReflowChildFlags>(static_cast<unsigned>(a)|static_cast<unsigned>(b));
}
struct FlagBits {
  ReflowChildFlags bits;
  explicit operator bool() const { return static_cast<unsigned>(bits) != 0; }
  operator ReflowChildFlags() const { return bits; }
};
FlagBits operator&(ReflowChildFlags a, ReflowChildFlags b) {
  return {static_cast<ReflowChildFlags>(static_cast<unsigned>(a)&static_cast<unsigned>(b))};
}
struct ReflowOutput {
  nsSize actual;
  LogicalSize Size(WritingMode) const { return {actual}; }
};
struct ReflowInput {
  nsIFrame* mFrame;
  nsMargin offsets;
  LogicalMargin ComputedLogicalOffsets(WritingMode) const { return {offsets}; }
  static void ApplyRelativePositioning(nsIFrame*, const nsMargin&, nsPoint*);
  static void ApplyRelativePositioning(nsIFrame*, WritingMode, const LogicalMargin&, LogicalPoint*, const nsSize&);
};
struct nsContainerFrame {
  static void FinishReflowChild(nsIFrame*, nsPresContext*, const ReflowOutput&, const ReflowInput*,
                               const WritingMode&, const LogicalPoint&, const nsSize&, ReflowChildFlags);
};
nsPoint nsIFrame::GetNormalPosition(bool* aHasProperty) const {
  bool hasProperty;
  nsPoint normalPosition = GetProperty(NormalPositionProperty(), &hasProperty);
  if (aHasProperty) {
    *aHasProperty = hasProperty;
  }
  return hasProperty ? normalPosition : GetPosition();
}
mozilla::LogicalPoint nsIFrame::GetLogicalNormalPosition(
    mozilla::WritingMode aWritingMode, const nsSize& aContainerSize) const {
  // Subtract the size of this frame from the container size to get
  // the correct position in rtl frames where the origin is on the
  // right instead of the left
  return mozilla::LogicalPoint(aWritingMode, GetNormalPosition(),
                               aContainerSize - mRect.Size());
}
void ReflowInput::ApplyRelativePositioning(nsIFrame* aFrame,
                                           const nsMargin& aComputedOffsets,
                                           nsPoint* aPosition) {
  if (!aFrame->IsRelativelyOrStickyPositioned()) {
    MOZ_ASSERT(!aFrame->HasProperty(nsIFrame::NormalPositionProperty()),
               "Only a relatively or sticky positioned frame should have a "
               "stored normal position.");
    return;
  }

  // Store the normal position
  aFrame->SetProperty(nsIFrame::NormalPositionProperty(), *aPosition);

  const nsStyleDisplay* display = aFrame->StyleDisplay();
  if (StylePositionProperty::Relative == display->mPosition) {
    *aPosition += nsPoint(aComputedOffsets.left, aComputedOffsets.top);
  }
  // For sticky positioned elements, we'll leave them until the scroll container
  // reflows and calls StickyScrollContainer::UpdatePositions() to update their
  // positions.
}
void ReflowInput::ApplyRelativePositioning(
    nsIFrame* aFrame, WritingMode aWritingMode,
    const LogicalMargin& aComputedOffsets, LogicalPoint* aPosition,
    const nsSize& aContainerSize) {
  // Subtract the size of the frame from the container size that we
  // use for converting between the logical and physical origins of
  // the frame. This accounts for the fact that logical origins in RTL
  // coordinate systems are at the top right of the frame instead of
  // the top left.
  nsSize frameSize = aFrame->GetSize();
  nsPoint pos =
      aPosition->GetPhysicalPoint(aWritingMode, aContainerSize - frameSize);
  ApplyRelativePositioning(
      aFrame, aComputedOffsets.GetPhysicalMargin(aWritingMode), &pos);
  *aPosition = LogicalPoint(aWritingMode, pos, aContainerSize - frameSize);
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

static void sourceHelper(nsIFrame* frame, nsIFrame* prevInFlow, WritingMode wm,
                         nsSize containerSize, nsSize actual, nsMargin offset) {
  nsPresContext* aPresContext = nullptr;
  ReflowInput reflowInput{frame,offset};
  ReflowOutput desiredSize{actual};
  ReflowChildFlags aFlags = ReflowChildFlags::Default;
      const bool isRelative = frame->IsRelativelyPositioned();
      const nscoord inlineStart =
          isRelative
              ? prevInFlow->GetLogicalNormalPosition(wm, containerSize).I(wm)
              : prevInFlow->IStart(wm, containerSize);
      const LogicalPoint pos(wm, inlineStart, 0);

  using Container = nsContainerFrame;
  auto FinishReflowChild = Container::FinishReflowChild;
      FinishReflowChild(
          frame, aPresContext, desiredSize, &reflowInput, wm, pos, containerSize,
          isRelative ? aFlags | ReflowChildFlags::ApplyRelativePositioning
                     : aFlags);
}
static void sourceUpdate(nsIFrame& frame, nsPoint offsets) {
  nsIFrame* cont = &frame;
  nsMargin newOffsets{offsets.x, offsets.y, 0, 0};
        bool hasProperty;
        nsPoint normalPosition = cont->GetNormalPosition(&hasProperty);
        if (!hasProperty) {
          cont->AddProperty(nsIFrame::NormalPositionProperty(), normalPosition);
        }
        cont->SetPosition(normalPosition +
                          nsPoint(newOffsets.left, newOffsets.top));
}

int main(int argc, char** argv) {
  if (argc != 18) return 2;
  int32_t a[17];
  for (int i=0;i<17;i++) a[i]=std::stoi(argv[i+1]);
  WritingMode wm{bool(a[0]),bool(a[1]),bool(a[2])};
  nsIFrame previous, current;
  previous.mRect.size={a[5],a[6]}; previous.mRect.position={a[7],a[8]};
  if (a[9]) previous.normal=nsPoint{a[10],a[11]};
  current.display.mPosition=static_cast<StylePositionProperty>(a[16]);
  if (a[16]!=1) previous.normal.reset();
  sourceHelper(&current,&previous,wm,{a[3],a[4]},{a[12],a[13]}, {a[14],a[15],0,0});
  auto print=[&]() { std::cout << current.mRect.position.x << ' ' << current.mRect.position.y << ' '
    << current.mRect.size.width << ' ' << current.mRect.size.height << ' '
    << current.normal.has_value() << ' ' << current.normal.value_or(nsPoint{}).x << ' '
    << current.normal.value_or(nsPoint{}).y << ' ' << current.didReflowCalls << '\n'; };
  print();
  if (a[16]==1) {
    sourceUpdate(current,nsPoint{a[14]*2,a[15]*2});print();
    sourceUpdate(current,nsPoint{0,0});print();
  }
}
