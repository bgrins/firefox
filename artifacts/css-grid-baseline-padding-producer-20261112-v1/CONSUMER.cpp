auto ApplyBaselinePadding = [this, wm, &needPaddingProp](LogicalAxis aAxis,
                                                           Prop aProp) {
    bool found;
    nscoord val = mFrame->GetProperty(aProp, &found);
    if (found) {
      NS_ASSERTION(val != nscoord(0), "zero in this property is useless");
      LogicalSide side;
      if (val > 0) {
        side = MakeLogicalSide(aAxis, LogicalEdge::Start);
      } else {
        side = MakeLogicalSide(aAxis, LogicalEdge::End);
        val = -val;
      }
      mComputedPadding.Side(side, wm) += val;
      needPaddingProp = true;
      if (aAxis == LogicalAxis::Block && val > 0) {
        // We have a baseline-adjusted block-axis start padding, so
        // we need this to mark lines dirty when mIsBResize is true:
        this->mFrame->AddStateBits(NS_FRAME_CONTAINS_RELATIVE_BSIZE);
      }
    }
  };
