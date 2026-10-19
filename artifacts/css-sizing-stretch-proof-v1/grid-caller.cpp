nsGridContainerFrame::ReflowInFlowChild(
    nsIFrame* aChild, const GridItemInfo* aGridItemInfo, nsSize aContainerSize,
    const Maybe<nscoord>& aStretchBSize, const Fragmentainer* aFragmentainer,
    const GridReflowInput& aGridRI, const LogicalRect& aContentArea,
    ReflowOutput& aDesiredSize, nsReflowStatus& aStatus) {
  nsPresContext* pc = PresContext();
  ComputedStyle* containerSC = Style();
  WritingMode wm = aGridRI.mReflowInput->GetWritingMode();
  const bool isGridItem = !!aGridItemInfo;
  MOZ_ASSERT(isGridItem == !aChild->IsPlaceholderFrame());
  LogicalRect cb(wm);
  WritingMode childWM = aChild->GetWritingMode();
  bool isConstrainedBSize = false;
  nscoord toFragmentainerEnd;
  // The part of the child's grid area that's in previous container fragments.
  nscoord consumedGridAreaBSize = 0;
  if (MOZ_LIKELY(isGridItem)) {
    MOZ_ASSERT(aGridItemInfo->mFrame == aChild);
    const GridArea& area = aGridItemInfo->mArea;
    MOZ_ASSERT(area.IsDefinite());
    cb = aGridRI.ContainingBlockFor(area);
    if (aFragmentainer && !wm.IsOrthogonalTo(childWM)) {
      // |gridAreaBOffset| is the offset of the child's grid area in this
      // container fragment (if negative, that distance is the child CB size
      // consumed in previous container fragments).  Note that cb.BStart
      // (initially) and aState.mFragBStart are in "global" grid coordinates
      // (like all track positions).
      nscoord gridAreaBOffset = cb.BStart(wm) - aGridRI.mFragBStart;
      consumedGridAreaBSize = std::max(0, -gridAreaBOffset);
      cb.BStart(wm) = std::max(0, gridAreaBOffset);
      if (aFragmentainer->mToFragmentainerEnd != NS_UNCONSTRAINEDSIZE) {
        toFragmentainerEnd = aFragmentainer->mToFragmentainerEnd -
                             aGridRI.mFragBStart - cb.BStart(wm);
        toFragmentainerEnd = std::max(toFragmentainerEnd, 0);
        isConstrainedBSize = true;
      }
    }
    cb += aContentArea.Origin(wm);
    aGridRI.mRows.AlignBaselineSubtree(*aGridItemInfo);
    aGridRI.mCols.AlignBaselineSubtree(*aGridItemInfo);
    // Setup [align|justify]-content:[last ]baseline related frame properties.
    // These are added to the padding in SizeComputationInput::InitOffsets.
    // (a negative value signals the value is for 'last baseline' and should be
    //  added to the (logical) end padding)
    typedef const FramePropertyDescriptor<SmallValueHolder<nscoord>>* Prop;
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
    const bool isOrthogonal = wm.IsOrthogonalTo(childWM);
    SetProp(LogicalAxis::Block,
            isOrthogonal ? IBaselinePadProperty() : BBaselinePadProperty());
    SetProp(LogicalAxis::Inline,
            isOrthogonal ? BBaselinePadProperty() : IBaselinePadProperty());
  } else {
    // By convention, for frames that perform CSS Box Alignment, we position
    // placeholder children at the start corner of their alignment container,
    // and in this case that's usually the grid's content-box.
    // ("Usually" - the exception is when the grid *also* forms the
    // abs.pos. containing block. In that case, the alignment container isn't
    // the content-box -- it's some grid area instead.  But that case doesn't
    // require any special handling here, because we handle it later using a
    // special flag (ReflowInput::InitFlag::StaticPosIsCBOrigin) which will make
    // us ignore the placeholder's position entirely.)
    cb = aContentArea;
    aChild->AddStateBits(PLACEHOLDER_STATICPOS_NEEDS_CSSALIGN);
  }

  LogicalSize reflowSize(cb.Size(wm));
  if (isConstrainedBSize) {
    reflowSize.BSize(wm) = toFragmentainerEnd;
  }
  LogicalSize childCBSize = reflowSize.ConvertTo(childWM, wm);

  // Setup the ClampMarginBoxMinSize reflow flags and property, if needed.
  ComputeSizeFlags csFlags;
  if (aGridItemInfo) {
    const auto childIAxisInWM = childWM.ConvertAxisTo(LogicalAxis::Inline, wm);
    // Clamp during reflow if we're stretching in that axis.
    if (GridItemShouldStretch(aChild, LogicalAxis::Inline)) {
      if (aGridItemInfo->mState[childIAxisInWM] &
          ItemState::eClampMarginBoxMinSize) {
        csFlags += ComputeSizeFlag::IClampMarginBoxMinSize;
      }
    } else {
      csFlags += ComputeSizeFlag::ShrinkWrap;
    }

    const auto childBAxisInWM = GetOrthogonalAxis(childIAxisInWM);
    if (GridItemShouldStretch(aChild, LogicalAxis::Block) &&
        aGridItemInfo->mState[childBAxisInWM] &
            ItemState::eClampMarginBoxMinSize) {
      csFlags += ComputeSizeFlag::BClampMarginBoxMinSize;
      aChild->SetProperty(BClampMarginBoxMinSizeProperty(),
                          childCBSize.BSize(childWM));
    } else {
      aChild->RemoveProperty(BClampMarginBoxMinSizeProperty());
    }

    if ((aGridItemInfo->mState[childIAxisInWM] &
         ItemState::eContentBasedAutoMinSize)) {
      csFlags += ComputeSizeFlag::IApplyAutoMinSize;
    }
  }

  if (!isConstrainedBSize) {
    childCBSize.BSize(childWM) = NS_UNCONSTRAINEDSIZE;
  }
  LogicalSize percentBasis(cb.Size(wm).ConvertTo(childWM, wm));
  ReflowInput childRI(pc, *aGridRI.mReflowInput, aChild, childCBSize,
                      Some(percentBasis), {}, {}, csFlags);
  childRI.mFlags.mIsTopOfPage =
      aFragmentainer ? aFragmentainer->mIsTopOfPage : false;

  // FIXME (perf): It would be faster to do this only if the previous reflow of
  // the child was a measuring reflow, and only if the child does some of the
  // things that are affected by ComputeSizeFlag::IsGridMeasuringReflow.
  childRI.SetBResize(true);
  childRI.SetBResizeForPercentages(true);

  // If the child is stretching in its block axis, and we might be fragmenting
  // it in that axis, then setup a frame property to tell
  // nsBlockFrame::ComputeFinalSize the size.
  if (isConstrainedBSize && !wm.IsOrthogonalTo(childWM)) {
    const bool stretch =
        childRI.mStylePosition
            ->BSize(childWM, AnchorPosResolutionParams::From(&childRI))
            ->IsAuto() &&
        GridItemShouldStretch(aChild, LogicalAxis::Block);
    if (stretch) {
      aChild->SetProperty(FragStretchBSizeProperty(), *aStretchBSize);
    } else {
      aChild->RemoveProperty(FragStretchBSizeProperty());
    }
  }

  // We need the width of the child before we can correctly convert
  // the writing-mode of its origin, so we reflow at (0, 0) using a dummy
  // aContainerSize, and then pass the correct position to FinishReflowChild.
  ReflowOutput childSize(childRI);
  const nsSize dummyContainerSize;

  ReflowChild(aChild, pc, childSize, childRI, childWM, LogicalPoint(childWM),
              dummyContainerSize, ReflowChildFlags::Default, aStatus);

  // childPos here initially represents the position that the child would have
  // (expressed as an istart,bstart corner *in its own writing-mode*) if it
  // were placed at the cb origin:
  LogicalPoint childPos = cb.Origin(wm).ConvertRectOriginTo(
      childWM, wm, childSize.PhysicalSize(), aContainerSize);

  // Apply align/justify-self and reflow again if that affects the size.
  if (MOZ_LIKELY(isGridItem)) {
    LogicalSize size = childSize.Size(childWM);  // from the ReflowChild()
    auto applyItemSelfAlignment = [&](LogicalAxis aAxis, nscoord aCBSize) {
      auto align =
          childRI.mStylePosition->UsedSelfAlignment(aAxis, containerSC);
      auto state = aGridItemInfo->mState[aAxis];
      AlignJustifyFlags flags;
      if (IsMasonry(aAxis)) {
        // In a masonry axis, we inhibit applying 'stretch' and auto-margins
        // here since AlignJustifyTracksInMasonryAxis deals with that.
        // The only other {align,justify}-{self,content} values that have an
        // effect are '[last] baseline', the rest behave as 'start'.
        if (MOZ_LIKELY(!(state & ItemState::eSelfBaseline))) {
          align = {StyleAlignFlags::START};
        } else {
          auto group = (state & ItemState::eFirstBaseline)
                           ? BaselineSharingGroup::First
                           : BaselineSharingGroup::Last;
          auto itemStart = aGridItemInfo->mArea.LineRangeForAxis(aAxis).mStart;
          aCBSize = aGridRI.TracksFor(aAxis)
                        .mSizes[itemStart]
                        .mBaselineSubtreeSize[group];
        }
        flags += AlignJustifyFlag::IgnoreAutoMargins;
      } else if (state & ItemState::eContentBaseline) {
        align = {(state & ItemState::eFirstBaseline)
                     ? StyleAlignFlags::SELF_START
                     : StyleAlignFlags::SELF_END};
      }
      if (aAxis == LogicalAxis::Block) {
        AlignSelf(*aGridItemInfo, align, aCBSize, wm, childRI, size, flags,
                  &childPos);
      } else {
        JustifySelf(*aGridItemInfo, align, aCBSize, wm, childRI, size, flags,
                    &childPos);
      }
    };
    if (aStatus.IsComplete()) {
      applyItemSelfAlignment(LogicalAxis::Block,
                             cb.BSize(wm) - consumedGridAreaBSize);
    }
    applyItemSelfAlignment(LogicalAxis::Inline, cb.ISize(wm));
  }  // else, AbsoluteContainingBlock.cpp will handle align/justify-self.

  FinishReflowChild(aChild, pc, childSize, &childRI, childWM, childPos,
                    aContainerSize, ReflowChildFlags::ApplyRelativePositioning);
  ConsiderChildOverflow(aDesiredSize.mOverflowAreas, aChild);
}
