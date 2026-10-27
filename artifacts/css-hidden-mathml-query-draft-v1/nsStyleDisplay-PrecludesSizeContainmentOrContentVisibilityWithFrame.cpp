bool nsStyleDisplay::PrecludesSizeContainmentOrContentVisibilityWithFrame(
    const nsIFrame& aFrame) const {
  // The spec says that in the case of SVG, the contain property only applies
  // to <svg> elements that have an associated CSS layout box.
  // https://drafts.csswg.org/css-contain/#contain-property
  // Internal SVG elements do not use the standard CSS box model, and wouldn't
  // be affected by size containment. By disabling it we prevent them from
  // becoming query containers for size features.
  if (aFrame.HasAnyStateBits(NS_FRAME_SVG_LAYOUT)) {
    return true;
  }

  // Note: The spec for size containment says it should have no effect
  // - on non-atomic, inline-level boxes.
  // - on internal ruby boxes.
  // - if inner display type is table.
  // - on internal table boxes.
  // https://drafts.csswg.org/css-contain/#containment-size
  bool isNonReplacedInline = aFrame.IsLineParticipant() && !aFrame.IsReplaced();
  return isNonReplacedInline || IsInternalRubyDisplayType() ||
         DisplayInside() == mozilla::StyleDisplayInside::Table ||
         IsInnerTableStyle();
}
