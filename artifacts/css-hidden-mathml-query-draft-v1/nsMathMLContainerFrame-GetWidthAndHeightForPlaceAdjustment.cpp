nsMathMLContainerFrame::GetWidthAndHeightForPlaceAdjustment(
    const PlaceFlags& aFlags) {
  WidthAndHeightForPlaceAdjustment sizes;
  if (aFlags.contains(PlaceFlag::DoNotAdjustForWidthAndHeight)) {
    return sizes;
  }
  const nsStylePosition* stylePos = StylePosition();
  const auto& width = stylePos->mWidth;
  // TODO: Resolve percentages.
  // https://github.com/w3c/mathml-core/issues/76
  if (width.ConvertsToLength()) {
    sizes.width = Some(width.ToLength());
  }
  if (!aFlags.contains(PlaceFlag::IntrinsicSize)) {
    // TODO: Resolve percentages.
    // https://github.com/w3c/mathml-core/issues/77
    const auto& height = stylePos->mHeight;
    if (height.ConvertsToLength()) {
      sizes.height = Some(height.ToLength());
    }
  }
  return sizes;
}
