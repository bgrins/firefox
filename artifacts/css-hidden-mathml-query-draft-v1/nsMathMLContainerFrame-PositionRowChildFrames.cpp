void nsMathMLContainerFrame::PositionRowChildFrames(nscoord aOffsetX,
                                                    nscoord aBaseline,
                                                    bool aAddOperatorSpacing) {
  PlaceFlags flags;
  RowChildFrameIterator child(this, flags, aAddOperatorSpacing);
  while (child.Frame()) {
    nscoord dx = aOffsetX + child.X() + child.Margin().left;
    nscoord dy = aBaseline - child.Ascent();
    FinishReflowChild(child.Frame(), PresContext(), child.GetReflowOutput(),
                      nullptr, dx, dy, ReflowChildFlags::Default);
    ++child;
  }
}
