static Maybe<nsRect> GetUntransformedRectToAncestor(
    const nsIFrame* aFrame, const nsRect& aRect, const nsIFrame* aAncestor) {
  if (!aAncestor || aRect.width < 0 || aRect.height < 0 ||
      aRect.width > nscoord_MAX || aRect.height > nscoord_MAX) {
    return Nothing();
  }
  CheckedInt<nscoord> x = aRect.x;
  CheckedInt<nscoord> y = aRect.y;
  for (const nsIFrame* frame = aFrame; frame != aAncestor;
       frame = frame->GetParent()) {
    if (!frame || frame->PresContext() != aAncestor->PresContext() ||
        frame->IsTransformed() || frame->IsInSVGTextSubtree() ||
        frame->HasAnyStateBits(NS_FRAME_SVG_LAYOUT)) {
      return Nothing();
    }
    x += frame->GetPosition().x;
    y += frame->GetPosition().y;
    if (!x.isValid() || !y.isValid()) {
      return Nothing();
    }
  }
  const auto right = x + aRect.width;
  const auto bottom = y + aRect.height;
  if (!right.isValid() || !bottom.isValid() || x.value() < nscoord_MIN ||
      y.value() < nscoord_MIN || right.value() > nscoord_MAX ||
      bottom.value() > nscoord_MAX) {
    return Nothing();
  }
  return Some(nsRect(x.value(), y.value(), aRect.width, aRect.height));
}
