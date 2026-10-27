nscoord nsMathMLContainerFrame::ApplyAdjustmentForWidthAndHeight(
    const PlaceFlags& aFlags, const WidthAndHeightForPlaceAdjustment& aSizes,
    ReflowOutput& aReflowOutput, nsBoundingMetrics& aBoundingMetrics) {
  nscoord shiftX = 0;
  if (aSizes.width) {
    MOZ_ASSERT(!aFlags.contains(PlaceFlag::DoNotAdjustForWidthAndHeight));
    auto width = *aSizes.width;
    auto oldWidth = aReflowOutput.Width();
    if (IsMathContentBoxHorizontallyCentered()) {
      shiftX = (width - oldWidth) / 2;
    } else if (GetWritingMode().IsBidiRTL()) {
      shiftX = width - oldWidth;
    }
    aBoundingMetrics.leftBearing = 0;
    aBoundingMetrics.rightBearing = width;
    aBoundingMetrics.width = width;
    aReflowOutput.mBoundingMetrics = aBoundingMetrics;
    aReflowOutput.Width() = width;
  }
  if (aSizes.height) {
    MOZ_ASSERT(!aFlags.contains(PlaceFlag::DoNotAdjustForWidthAndHeight));
    MOZ_ASSERT(!aFlags.contains(PlaceFlag::IntrinsicSize));
    auto height = *aSizes.height;
    aReflowOutput.Height() = height;
  }
  return shiftX;
}
