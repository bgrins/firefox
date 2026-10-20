#include "facade.hpp"
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
#define HAS_HELPER 0
struct FlexLine{nsTArray<FlexItem> mItems;

};
static Result fallback(const FlexItem& item,WritingMode flexWM,nsSize physical){
Result aFlr;const FlexItem* firstBaselineItem=&item;const FlexItem* lastBaselineItem=&item;LogicalSize desiredSizeInFlexWM(flexWM,physical);
aFlr.mAscent = item.Frame()
                       ->GetLogicalNormalPosition(
                           flexWM, desiredSizeInFlexWM.GetPhysicalSize(flexWM))
                       .B(flexWM) +
                   item.ResolvedAscent(true);
const nscoord lastAscent =
        item.Frame()
            ->GetLogicalNormalPosition(
                flexWM, desiredSizeInFlexWM.GetPhysicalSize(flexWM))
            .B(flexWM) +
        item.ResolvedAscent(false);

    aFlr.mAscentForLast = desiredSizeInFlexWM.BSize(flexWM) - lastAscent;
return aFlr;
}
