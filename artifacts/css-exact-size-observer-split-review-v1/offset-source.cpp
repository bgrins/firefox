// aPosition should be a function that returns the position of a frame relative
// to its parent.
template <typename PositionGetter>
static nsPoint OffsetCalculator(const nsIFrame* aThis, const nsIFrame* aOther,
                                PositionGetter&& aPosition) {
  static_assert(std::is_invocable_r_v<nsPoint, PositionGetter, const nsIFrame*>,
                "aPosition must be callable as nsPoint(const nsIFrame*)");

  MOZ_ASSERT(aOther, "Must have frame for destination coordinate system!");

  NS_ASSERTION(aThis->PresContext() == aOther->PresContext(),
               "GetOffsetTo called on frames in different documents");

  nsPoint offset(0, 0);
  const nsIFrame* f;
  for (f = aThis; f != aOther && f; f = f->GetParent()) {
    offset += aPosition(f);
  }

  if (f != aOther) {
    // Looks like aOther wasn't an ancestor of |this|.  So now we have
    // the root-frame-relative position of |this| in |offset|.  Convert back
    // to the coordinates of aOther
    while (aOther) {
      offset -= aPosition(aOther);
      aOther = aOther->GetParent();
    }
  }

  return offset;
}

nsPoint nsIFrame::GetOffsetTo(const nsIFrame* aOther) const {
  return OffsetCalculator(this, aOther, [](const nsIFrame* aFrame) {
    return aFrame->GetPosition();
  });
}

