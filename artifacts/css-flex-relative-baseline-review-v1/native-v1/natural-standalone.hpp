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
#define HAS_HELPER 1
struct FlexLine{nsTArray<FlexItem> mItems;
Maybe<nscoord> NaturalBaselineBOffset(const FlexboxAxisTracker& aAxisTracker,
                                        BaselineSharingGroup aGroup,
                                        const nsSize& aContainerSize) const {
    const WritingMode wm = aAxisTracker.GetWritingMode();
    const bool last = aGroup == BaselineSharingGroup::Last;
    for (size_t i = 0; i < mItems.Length(); ++i) {
      const FlexItem& item = mItems[last ? mItems.Length() - i - 1 : i];
      if (item.IsStrut() || wm.IsOrthogonalTo(item.GetWritingMode())) {
        continue;
      }
      if (auto baseline = item.Frame()->GetNaturalBaselineBOffset(
              wm, aGroup, BaselineExportContext::Other)) {
        nscoord position =
            item.Frame()->GetLogicalNormalPosition(wm, aContainerSize).B(wm);
        if (last) {
          position = LogicalSize(wm, aContainerSize).BSize(wm) - position -
                     item.Frame()->BSize(wm);
        }
        return Some(position + *baseline);
      }
    }
    return Nothing();
  }
};
static Result fallback(const FlexItem& item,WritingMode flexWM,nsSize physical){
Result aFlr;const FlexItem* firstBaselineItem=&item;const FlexItem* lastBaselineItem=&item;LogicalSize desiredSizeInFlexWM(flexWM,physical);
aFlr.mAscent = item.Frame()
                       ->GetLogicalPosition(
                           flexWM, desiredSizeInFlexWM.GetPhysicalSize(flexWM))
                       .B(flexWM) +
                   item.ResolvedAscent(true);
const nscoord lastAscent =
        item.Frame()
            ->GetLogicalPosition(flexWM,
                                 desiredSizeInFlexWM.GetPhysicalSize(flexWM))
            .B(flexWM) +
        item.ResolvedAscent(false);

    aFlr.mAscentForLast = desiredSizeInFlexWM.BSize(flexWM) - lastAscent;
return aFlr;
}
