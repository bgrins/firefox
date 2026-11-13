  // Clone existing FlexItem for its underlying frame's continuation.
  // @param aContinuation a continuation in our next-in-flow chain.
  FlexItem CloneFor(nsIFrame* const aContinuation) const {
    MOZ_ASSERT(Frame() == aContinuation->FirstInFlow(),
               "aContinuation should be in aItem's continuation chain!");
    FlexItem item(*this);
    item.mFrame = aContinuation;
    item.mHadMeasuringReflow = false;
    return item;
  }
