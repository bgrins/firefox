StyleContentVisibility nsStyleDisplay::ContentVisibility(
    const nsIFrame& aFrame) const {
  if (MOZ_LIKELY(mContentVisibility == StyleContentVisibility::Visible)) {
    return StyleContentVisibility::Visible;
  }
  // content-visibility applies to elements for which size containment applies.
  // https://drafts.csswg.org/css-contain/#content-visibility
  if (PrecludesSizeContainmentOrContentVisibilityWithFrame(aFrame)) {
    return StyleContentVisibility::Visible;
  }
  // If we're in print/print-preview, or being used as an image, we should
  // always treat `auto` as `visible`.
  if (mContentVisibility == StyleContentVisibility::Auto &&
      (aFrame.PresContext()->IsPrintingOrPrintPreview() ||
       aFrame.PresContext()->Document()->IsBeingUsedAsImage())) {
    return StyleContentVisibility::Visible;
  }
  return mContentVisibility;
}
