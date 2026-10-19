ReflowInput::InitConstraints(
    nsPresContext* aPresContext, const Maybe<LogicalSize>& aContainingBlockSize,
    const Maybe<LogicalMargin>& aBorder, const Maybe<LogicalMargin>& aPadding,
    LayoutFrameType aFrameType) {
  WritingMode wm = GetWritingMode();
  LogicalSize cbSize = aContainingBlockSize.valueOr(
      LogicalSize(mWritingMode, NS_UNCONSTRAINEDSIZE, NS_UNCONSTRAINEDSIZE));

  // If this is a reflow root, then set the computed width and
  // height equal to the available space
  if (nullptr == mParentReflowInput || mFlags.mDummyParentReflowInput) {
    // XXXldb This doesn't mean what it used to!
    InitOffsets(wm, cbSize.ISize(wm), aFrameType, mComputeSizeFlags, aBorder,
                aPadding, mStyleDisplay);
    // Override mComputedMargin since reflow roots start from the
    // frame's boundary, which is inside the margin.
    SetComputedLogicalMargin(wm, LogicalMargin(wm));
    SetComputedLogicalOffsets(wm, LogicalMargin(wm));

    const auto borderPadding = ComputedLogicalBorderPadding(wm);
    SetComputedISize(
        std::max(0, AvailableISize() - borderPadding.IStartEnd(wm)),
        ResetResizeFlags::No);
    SetComputedBSize(
        AvailableBSize() != NS_UNCONSTRAINEDSIZE
            ? std::max(0, AvailableBSize() - borderPadding.BStartEnd(wm))
            : NS_UNCONSTRAINEDSIZE,
        ResetResizeFlags::No);

    mComputedMinSize.SizeTo(mWritingMode, 0, 0);
    mComputedMaxSize.SizeTo(mWritingMode, NS_UNCONSTRAINEDSIZE,
                            NS_UNCONSTRAINEDSIZE);
  } else {
    // Get the containing block's reflow input
    const ReflowInput* cbri = mCBReflowInput;
    MOZ_ASSERT(cbri, "no containing block");
    MOZ_ASSERT(mFrame->GetParent());

    // If we weren't given a containing block size, then compute one.
    if (aContainingBlockSize.isNothing()) {
      cbSize = ComputeContainingBlockRectangle(aPresContext, cbri);
    }

    // See if the containing block height is based on the size of its
    // content
    if (NS_UNCONSTRAINEDSIZE == cbSize.BSize(wm)) {
      // See if the containing block is a cell frame which needs
      // to use the mComputedHeight of the cell instead of what the cell block
      // passed in.
      // XXX It seems like this could lead to bugs with min-height and friends
      if (cbri->mParentReflowInput && cbri->mFrame->IsTableCellFrame()) {
        cbSize.BSize(wm) = cbri->ComputedSize(wm).BSize(wm);
      }
    }

    // XXX Might need to also pass the CB height (not width) for page boxes,
    // too, if we implement them.

    // For calculating positioning offsets, margins, borders and
    // padding, we use the writing mode of the containing block
    WritingMode cbwm = cbri->GetWritingMode();
    InitOffsets(cbwm, cbSize.ConvertTo(cbwm, wm).ISize(cbwm), aFrameType,
                mComputeSizeFlags, aBorder, aPadding, mStyleDisplay);

    // For calculating the size of this box, we use its own writing mode
    const auto blockSize =
        mStylePosition->BSize(wm, AnchorPosResolutionParams::From(this));

    // In quirks mode, get the containing block height using the special quirk
    // method for replaced inline frames, such as images.
    //
    // Bug 2075032: Merge the quirks mode logic below into
    // ComputeContainingBlockRectangle().
    if (aPresContext->CompatibilityMode() == eCompatibility_NavQuirks &&
        blockSize->HasPercent() && cbSize.BSize(wm) == NS_UNCONSTRAINEDSIZE &&
        mFlags.mIsReplaced && mStyleDisplay->IsInlineOutsideStyle() &&
        !wm.IsVertical() && !cbri->mFrame->IsTableCellFrame() &&
        !cbri->mFrame->IsFlexOrGridItem()) {
      cbSize.BSize(wm) = CalcQuirkContainingBlockHeight(cbri);
    }

    // Compute our offsets if the element is relatively positioned.  We
    // need the correct containing block inline-size and block-size
    // here, which is why we need to do it after all the quirks-n-such
    // above. (If the element is sticky positioned, we need to wait
    // until the scroll container knows its size, so we compute offsets
    // from StickyScrollContainer::UpdatePositions.)
    if (mStyleDisplay->IsRelativelyPositioned(mFrame)) {
      const LogicalMargin offsets =
          ComputeRelativeOffsets(cbwm, mFrame, cbSize.ConvertTo(cbwm, wm));
      SetComputedLogicalOffsets(cbwm, offsets);
    } else {
      // Initialize offsets to 0
      SetComputedLogicalOffsets(wm, LogicalMargin(wm));
    }

    // Calculate the computed values for min and max properties.  Note that
    // this MUST come after we've computed our border and padding.
    ComputeMinMaxValues(cbSize);

    // Calculate the computed inlineSize and blockSize.
    // This varies by frame type.

    if (IsInternalTableFrame()) {
      // Internal table elements. The rules vary depending on the type.
      // Calculate the computed isize
      bool rowOrRowGroup = false;
      const auto inlineSize =
          mStylePosition->ISize(wm, AnchorPosResolutionParams::From(this));
      bool isAutoISize = inlineSize->IsAuto();
      if ((StyleDisplay::TableRow == mStyleDisplay->mDisplay) ||
          (StyleDisplay::TableRowGroup == mStyleDisplay->mDisplay)) {
        // 'inlineSize' property doesn't apply to table rows and row groups
        isAutoISize = true;
        rowOrRowGroup = true;
      }

      // calc() with both percentages and lengths act like auto on internal
      // table elements
      if (isAutoISize || inlineSize->HasLengthAndPercentage()) {
        if (AvailableISize() != NS_UNCONSTRAINEDSIZE && !rowOrRowGroup) {
          // Internal table elements don't have margins. Only tables and
          // cells have border and padding
          SetComputedISize(
              std::max(0, AvailableISize() -
                              ComputedLogicalBorderPadding(wm).IStartEnd(wm)),
              ResetResizeFlags::No);
        } else {
          SetComputedISize(AvailableISize(), ResetResizeFlags::No);
        }
        NS_ASSERTION(ComputedISize() >= 0, "Bogus computed isize");

      } else {
        SetComputedISize(ComputeISizeValue(cbSize, *inlineSize),
                         ResetResizeFlags::No);
      }

      // Calculate the computed block size
      // 'blockSize' property doesn't apply to table columns and column groups
      const bool isAutoBSize =
          StyleDisplay::TableColumn == mStyleDisplay->mDisplay ||
          StyleDisplay::TableColumnGroup == mStyleDisplay->mDisplay ||
          nsLayoutUtils::IsAutoBSize(*blockSize, cbSize.BSize(wm));

      // calc() with both percentages and lengths acts like 'auto' on internal
      // table elements
      if (isAutoBSize || blockSize->HasLengthAndPercentage()) {
        SetComputedBSize(NS_UNCONSTRAINEDSIZE, ResetResizeFlags::No);
      } else {
        SetComputedBSize(
            ComputeBSizeValueHandlingStretch(
                cbSize.BSize(wm), mStylePosition->mBoxSizing, *blockSize),
            ResetResizeFlags::No);
      }

      // Doesn't apply to internal table elements
      mComputedMinSize.SizeTo(mWritingMode, 0, 0);
      mComputedMaxSize.SizeTo(mWritingMode, NS_UNCONSTRAINEDSIZE,
                              NS_UNCONSTRAINEDSIZE);
    } else if (mFrame->IsAbsolutelyPositioned(mStyleDisplay) &&
               // The absolute constraints are needed only for abspos
               // first-in-flow, not continuations.
               !mFrame->GetPrevInFlow()) {
      InitAbsoluteConstraints(cbri,
                              cbSize.ConvertTo(cbri->GetWritingMode(), wm));
    } else {
      AutoMaybeDisableFontInflation an(mFrame);

      auto* const alignCB = [&] {
        auto* cb = mFrame->GetParent();
        if (cb->IsTableWrapperFrame()) {
          auto* alignCBParent = cb->GetParent();
          if (alignCBParent && alignCBParent->IsGridContainerFrame()) {
            return alignCBParent;
          }
        }
        if (cb->Style()->GetPseudoType() ==
            PseudoStyleType::MozColumnSpanWrapper) {
          MOZ_ASSERT(mFrame->StyleColumn()->mColumnSpan !=
                     StyleColumnSpan::None);
          // Note(dshin, bug 2013429): `:-moz-column-span-wrapper` is a
          // non-inheriting anon box, so it doesn't inherit writing-mode either.
          auto* p = cb->GetParent();
          while (p) {
            if (p->Style()->GetPseudoType() !=
                PseudoStyleType::MozColumnSpanWrapper) {
              return p;
            }
            p = p->GetParent();
          }
          MOZ_ASSERT_UNREACHABLE("No parent above :-moz-column-span-wrapper?");
        }
        return cb;
      }();

      const bool isInlineLevel = [&] {
        if (mFrame->IsTableFrame()) {
          // An inner table frame is not inline-level, even if it happens to
          // have 'display:inline-table'. (That makes its table-wrapper frame be
          // inline-level, but not the inner table frame)
          return false;
        }
        if (mStyleDisplay->IsInlineOutsideStyle()) {
          return true;
        }
        if (mFlags.mIsReplaced && (mStyleDisplay->IsInnerTableStyle() ||
                                   mStyleDisplay->DisplayOutside() ==
                                       StyleDisplayOutside::TableCaption)) {
          // Internal table values on replaced elements behave as inline
          // https://drafts.csswg.org/css-tables-3/#table-structure
          //
          //     ... it is handled instead as though the author had declared
          //     either 'block' (for 'table' display) or 'inline' (for all
          //     other values)"
          //
          // FIXME(emilio): The only test that covers this is
          // table-anonymous-objects-211.xht, which fails on other browsers (but
          // differently to us, if you just remove this condition).
          return true;
        }
        if (mFrame->HasAnyStateBits(NS_FRAME_OUT_OF_FLOW) &&
            !mStyleDisplay->IsAbsolutelyPositionedStyle()) {
          // Floats are treated as inline-level and also shrink-wrap.
          return true;
        }
        return false;
      }();

      if (mParentReflowInput->mFlags.mOrthogonalCellFinalReflow) {
        // This is the "extra" reflow for the inner content of an orthogonal
        // table cell, after the row size has been determined; so we want to
        // respect the cell's size without further adjustment. Its rect may
        // not yet be correct, however, so we base our size on the parent
        // reflow input's available size, adjusted for border widths.
        MOZ_ASSERT(mFrame->GetParent()->IsTableCellFrame(),
                   "unexpected mOrthogonalCellFinalReflow flag!");
        cbSize = mParentReflowInput->AvailableSize().ConvertTo(
            wm, mParentReflowInput->GetWritingMode());
        cbSize -= mParentReflowInput->ComputedLogicalBorder(wm).Size(wm);
        SetAvailableISize(cbSize.ISize(wm));
      } else {
        const bool shouldShrinkWrap = [&] {
          if (isInlineLevel) {
            return true;
          }
          if (mFlags.mIsReplaced && !alignCB->IsFlexOrGridContainer()) {
            // Shrink-wrap replaced elements when in-flow (out of flows are
            // handled above). We exclude replaced elements in grid or flex
            // contexts, where we don't want to shrink-wrap unconditionally (so
            // that stretching can happen). When grid/flex explicitly want
            // shrink-wrapping, they can request it directly using the relevant
            // flag.
            return true;
          }
          if (!alignCB->IsGridContainerFrame() &&
              mWritingMode.IsOrthogonalTo(alignCB->GetWritingMode())) {
            // Shrink-wrap blocks that are orthogonal to their container (unless
            // we're in a grid?)
            return true;
          }
          return false;
        }();

        if (shouldShrinkWrap) {
          mComputeSizeFlags += ComputeSizeFlag::ShrinkWrap;
        }

        if (cbSize.ISize(wm) == NS_UNCONSTRAINEDSIZE) {
          // For orthogonal flows, where we found a parent orthogonal-limit for
          // AvailableISize() in Init(), we'll use the same here as well.
          cbSize.ISize(wm) = AvailableISize();
        }
      }

      auto size = mFrame->ComputeSize(*this, wm, cbSize, AvailableISize(),
                                      ComputedLogicalMargin(wm).Size(wm),
                                      ComputedLogicalBorderPadding(wm).Size(wm),
                                      mStyleSizeOverrides, mComputeSizeFlags);

      mComputedSize = size.mLogicalSize;
      NS_ASSERTION(ComputedISize() >= 0, "Bogus inline-size");
      NS_ASSERTION(
          ComputedBSize() == NS_UNCONSTRAINEDSIZE || ComputedBSize() >= 0,
          "Bogus block-size");

      mFlags.mIsBSizeSetByAspectRatio =
          size.mAspectRatioUsage == nsIFrame::AspectRatioUsage::ToComputeBSize;

      const bool shouldCalculateBlockSideMargins = [&]() {
        if (isInlineLevel) {
          return false;
        }
        if (mFrame->IsTableFrame()) {
          return false;
        }
        if (alignCB->IsFlexOrGridContainer()) {
          // Exclude flex and grid items.
          return false;
        }
        const auto pseudoType = mFrame->Style()->GetPseudoType();
        if (pseudoType == PseudoStyleType::Marker &&
            mFrame->GetParent()->StyleList()->mListStylePosition ==
                StyleListStylePosition::Outside) {
          // Exclude outside ::markers.
          return false;
        }
        if (pseudoType == PseudoStyleType::MozColumnContent) {
          // Exclude -moz-column-content since it cannot have any margin.
          return false;
        }
        return true;
      }();

      if (shouldCalculateBlockSideMargins) {
        CalculateBlockSideMargins();
      }
    }
  }

  // Save our containing block dimensions
  mContainingBlockSize = cbSize;
}
