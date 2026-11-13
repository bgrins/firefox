auto SetProp = [aGridItemInfo, aChild](LogicalAxis aGridAxis, Prop aProp) {
      auto state = aGridItemInfo->mState[aGridAxis];
      auto baselineAdjust = (state & ItemState::eContentBaseline)
                                ? aGridItemInfo->mBaselineOffset[aGridAxis]
                                : nscoord(0);
      if (baselineAdjust < nscoord(0)) {
        // This happens when the subtree overflows its track.
        // XXX spec issue? it's unclear how to handle this.
        baselineAdjust = nscoord(0);
      } else if (state & ItemState::eLastBaseline) {
        // FIXME: We're not setting the ItemState::eEndSideBaseline flag any
        // more as the new baseline sharing group calculation handles most of
        // the cases we need.  For non-masonry grids this flag was always set
        // for LAST_BASELINE items, so we're just mimicking that behavior here.
        // That said, masonry grids might not work 100% any more..
        baselineAdjust = -baselineAdjust;
      }
      if (baselineAdjust != nscoord(0)) {
        aChild->SetProperty(aProp, baselineAdjust);
      } else {
        aChild->RemoveProperty(aProp);
      }
    };
