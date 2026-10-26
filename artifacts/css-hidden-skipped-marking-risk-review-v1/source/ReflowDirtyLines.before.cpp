bool nsBlockFrame::ReflowDirtyLines(BlockReflowState& aState) {
  bool keepGoing = true;
  bool foundAnyClears = aState.mTrailingClearFromPIF != UsedClear::None;
  bool willReflowAgain = false;
  bool usedOverflowWrap = false;

#ifdef DEBUG
  if (gNoisyReflow) {
    IndentBy(stdout, gNoiseIndent);
    ListTag(stdout);
    printf(": reflowing dirty lines");
    printf(" computedISize=%d\n", aState.mReflowInput.ComputedISize());
  }
  AutoNoisyIndenter indent(gNoisyReflow);
#endif

  bool selfDirty = HasAnyStateBits(NS_FRAME_IS_DIRTY) ||
                   (aState.mReflowInput.IsBResize() &&
                    HasAnyStateBits(NS_FRAME_CONTAINS_RELATIVE_BSIZE));

  // Reflow our last line if our availableBSize has increased
  // so that we (and our last child) pull up content as necessary
  if (aState.mReflowInput.AvailableBSize() != NS_UNCONSTRAINEDSIZE &&
      GetNextInFlow() &&
      aState.mReflowInput.AvailableBSize() >
          GetLogicalSize().BSize(aState.mReflowInput.GetWritingMode())) {
    LineIterator lastLine = LinesEnd();
    if (lastLine != LinesBegin()) {
      --lastLine;
      lastLine->MarkDirty();
    }
  }
  // the amount by which we will slide the current line if it is not
  // dirty
  nscoord deltaBCoord = 0;

  // whether we did NOT reflow the previous line and thus we need to
  // recompute the carried out margin before the line if we want to
  // reflow it or if its previous margin is dirty
  bool needToRecoverState = false;
  // Float continuations were reflowed in ReflowPushedFloats
  bool reflowedFloat =
      HasFloats() && GetFloats()->FirstChild()->HasAnyStateBits(
                         NS_FRAME_IS_PUSHED_OUT_OF_FLOW);
  bool lastLineMovedUp = false;
  // We save up information about BR-clearance here
  UsedClear inlineFloatClearType = aState.mTrailingClearFromPIF;

  LineIterator line = LinesBegin(), line_end = LinesEnd();

  // Determine if children of this frame could have breaks between them for
  // page names.
  //
  // We need to check for paginated layout, the named-page pref, and if the
  // available block-size is constrained.
  //
  // Note that we need to check for paginated layout as named-pages are only
  // used during paginated reflow. We need to additionally check for
  // unconstrained block-size to avoid introducing fragmentation breaks during
  // "measuring" reflows within an overall paginated reflow, and to avoid
  // fragmentation in monolithic containers like 'inline-block'.
  //
  // Because we can only break for named pages using Class A breakpoints, we
  // also need to check that the block flow direction of the containing frame
  // of these items (which is this block) is parallel to that of this page.
  // See: https://www.w3.org/TR/css-break-3/#btw-blocks
  const nsPresContext* const presCtx = aState.mPresContext;
  const bool canBreakForPageNames =
      aState.mReflowInput.mFlags.mCanHaveClassABreakpoints &&
      aState.mReflowInput.AvailableBSize() != NS_UNCONSTRAINEDSIZE &&
      presCtx->GetPresShell()->GetRootFrame()->GetWritingMode().IsVertical() ==
          GetWritingMode().IsVertical();

  // ReflowInput.mFlags.mCanHaveClassABreakpoints should respect the named
  // pages pref and presCtx->IsPaginated, so we did not explicitly check these
  // above when setting canBreakForPageNames.
  if (canBreakForPageNames) {
    MOZ_ASSERT(presCtx->IsPaginated(),
               "canBreakForPageNames should not be set during non-paginated "
               "reflow");
  }

  // Reflow the lines that are already ours
  for (; line != line_end; ++line, aState.AdvanceToNextLine()) {
    DumpLine(aState, line, deltaBCoord, 0);
#ifdef DEBUG
    AutoNoisyIndenter indent2(gNoisyReflow);
#endif

    if (selfDirty) {
      line->MarkDirty();
    }

    // This really sucks, but we have to look inside any blocks that have clear
    // elements inside them.
    // XXX what can we do smarter here?
    if (!line->IsDirty() && line->IsBlock() &&
        line->mFirstChild->HasAnyStateBits(NS_BLOCK_HAS_CLEAR_CHILDREN) &&
        aState.FloatManager()->HasAnyFloats()) {
      line->MarkDirty();
    }

    nsIFrame* floatAvoidingBlock = nullptr;
    if (line->IsBlock() &&
        !nsBlockFrame::BlockCanIntersectFloats(line->mFirstChild)) {
      floatAvoidingBlock = line->mFirstChild;
    }

    // We have to reflow the line if it's a block whose clearance
    // might have changed, so detect that.
    if (!line->IsDirty() &&
        (line->HasFloatClearTypeBefore() || floatAvoidingBlock)) {
      nscoord curBCoord = aState.mBCoord;
      // See where we would be after applying any clearance due to
      // BRs.
      if (inlineFloatClearType != UsedClear::None) {
        std::tie(curBCoord, std::ignore) =
            aState.ClearFloats(curBCoord, inlineFloatClearType);
      }

      auto [newBCoord, result] = aState.ClearFloats(
          curBCoord, line->FloatClearTypeBefore(), floatAvoidingBlock);

      if (line->HasClearance()) {
        // Reflow the line if it might not have clearance anymore.
        if (result == ClearFloatsResult::BCoordNoChange
            // aState.mBCoord is the clearance point which should be the
            // block-start border-edge of the block frame. If sliding the
            // block by deltaBCoord isn't going to put it in the predicted
            // position, then we'd better reflow the line.
            || newBCoord != line->BStart() + deltaBCoord) {
          line->MarkDirty();
        }
      } else {
        // Reflow the line if the line might have clearance now.
        if (result != ClearFloatsResult::BCoordNoChange) {
          line->MarkDirty();
        }
      }
    }

    // We might have to reflow a line that is after a clearing BR.
    if (inlineFloatClearType != UsedClear::None) {
      std::tie(aState.mBCoord, std::ignore) =
          aState.ClearFloats(aState.mBCoord, inlineFloatClearType);
      if (aState.mBCoord != line->BStart() + deltaBCoord) {
        // SlideLine is not going to put the line where the clearance
        // put it. Reflow the line to be sure.
        line->MarkDirty();
      }
      inlineFloatClearType = UsedClear::None;
    }

    bool previousMarginWasDirty = line->IsPreviousMarginDirty();
    if (previousMarginWasDirty) {
      // If the previous margin is dirty, reflow the current line
      line->MarkDirty();
      line->ClearPreviousMarginDirty();
    } else if (aState.ContentBSize() != NS_UNCONSTRAINEDSIZE) {
      const nscoord scrollableOverflowBEnd =
          LogicalRect(line->mWritingMode, line->ScrollableOverflowRect(),
                      line->mContainerSize)
              .BEnd(line->mWritingMode);
      if (scrollableOverflowBEnd + deltaBCoord > aState.ContentBEnd()) {
        // Lines that aren't dirty but get slid past our available block-size
        // constraint must be reflowed.
        line->MarkDirty();
      }
    }

    if (!line->IsDirty()) {
      const bool isPaginated =
          aState.mReflowInput.IsInFragmentedContext() ||
          // Table can also be reflowed unconstrained during printing.
          aState.mPresContext->IsPaginated();
      if (isPaginated) {
        // We are in a paginated context, i.e. in columns or pages.
        const bool mayContainFloats =
            line->IsBlock() || line->HasFloats() || line->HadFloatPushed();
        if (mayContainFloats) {
          // The following if-else conditions check whether this line -- which
          // might have floats in its subtree, or has floats as direct children,
          // or had floats pushed -- needs to be reflowed.
          if (deltaBCoord != 0 || aState.mReflowInput.IsBResize()) {
            // The distance to the block-end edge might have changed. Reflow the
            // line both because the breakpoints within its floats may have
            // changed and because we might have to push/pull the floats in
            // their entirety.
            line->MarkDirty();
          } else if (HasPushedFloats()) {
            // We had pushed floats which haven't been drained by our
            // next-in-flow, which means our parent is currently reflowing us
            // again due to clearance without creating a next-in-flow for us.
            // Reflow the line to redo the floats split logic to correctly set
            // our reflow status.
            line->MarkDirty();
          } else if (aState.mReflowInput.mFlags.mMustReflowPlaceholders) {
            // Reflow the line (that may containing a float's placeholder frame)
            // if our parent tells us to do so.
            line->MarkDirty();
          } else if (aState.mReflowInput.mFlags.mMovedBlockFragments) {
            // Our parent's line containing us moved to a different fragment.
            // Reflow the line because the decision about whether the float fits
            // may be different in a different fragment.
            line->MarkDirty();
          }
        }
      }
    }

    if (!line->IsDirty()) {
      // See if there's any reflow damage that requires that we mark the
      // line dirty.
      PropagateFloatDamage(aState, line, deltaBCoord);
    }

    // If the container size has changed, reset mContainerSize. If the
    // line's writing mode is not ltr, or if the line is not left-aligned, also
    // mark the line dirty.
    if (aState.ContainerSize() != line->mContainerSize) {
      line->mContainerSize = aState.ContainerSize();

      const bool isLastLine = line == mLines.back() && !GetNextInFlow();
      const auto align = isLastLine ? StyleText()->TextAlignForLastLine()
                                    : StyleText()->mTextAlign;
      if (line->mWritingMode.IsVertical() || line->mWritingMode.IsBidiRTL() ||
          !IsAlignedLeft(align, StyleVisibility()->mDirection,
                         StyleTextReset()->mUnicodeBidi, this)) {
        line->MarkDirty();
      }
    }

    // Check for a page break caused by CSS named pages.
    //
    // We should break for named pages when two frames meet at a class A
    // breakpoint, where the first frame has a different end page value to the
    // second frame's start page value. canBreakForPageNames is true iff
    // children of this frame can form class A breakpoints, and that we are not
    // in a measurement reflow or in a monolithic container such as
    // 'inline-block'.
    //
    // We specifically do not want to cause a page-break for named pages when
    // we are at the top of a page. This would otherwise happen when the
    // previous sibling is an nsPageBreakFrame, or all previous siblings on the
    // current page are zero-height. The latter may not be per-spec, but is
    // compatible with Chrome's implementation of named pages.
    const nsAtom* nextPageName = nullptr;
    bool shouldBreakForPageName = false;
    if (canBreakForPageNames && (!aState.mReflowInput.mFlags.mIsTopOfPage ||
                                 !aState.IsAdjacentWithBStart())) {
      const nsIFrame* const frame = line->mFirstChild;
      if (!frame->IsPlaceholderFrame() && !frame->IsPageBreakFrame()) {
        nextPageName = frame->GetStartPageValue();
        // Walk back to the last frame that isn't a placeholder.
        const nsIFrame* prevFrame = frame->GetPrevSibling();
        while (prevFrame && prevFrame->IsPlaceholderFrame()) {
          prevFrame = prevFrame->GetPrevSibling();
        }
        if (prevFrame && prevFrame->GetEndPageValue() != nextPageName) {
          shouldBreakForPageName = true;
          line->MarkDirty();
        }
      }
    }

    if (needToRecoverState && line->IsDirty()) {
      // We need to reconstruct the block-end margin only if we didn't
      // reflow the previous line and we do need to reflow (or repair
      // the block-start position of) the next line.
      aState.ReconstructMarginBefore(line);
    }

    bool reflowedPrevLine = !needToRecoverState;
    if (needToRecoverState) {
      needToRecoverState = false;

      // Update aState.mPrevChild as if we had reflowed all of the frames in
      // this line.
      if (line->IsDirty()) {
        NS_ASSERTION(
            line->mFirstChild->GetPrevSibling() == line.prev()->LastChild(),
            "unexpected line frames");
        aState.mPrevChild = line->mFirstChild->GetPrevSibling();
      }
    }

    // Now repair the line and update |aState.mBCoord| by calling
    // |ReflowLine| or |SlideLine|.
    // If we're going to reflow everything again, then no need to reflow
    // the dirty line ... unless the line has floats, in which case we'd
    // better reflow it now to refresh its float cache, which may contain
    // dangling frame pointers! Ugh! This reflow of the line may be
    // incorrect because we skipped reflowing previous lines (e.g., floats
    // may be placed incorrectly), but that's OK because we'll mark the
    // line dirty below under "if (aState.mReflowInput.mDiscoveredClearance..."
    if (line->IsDirty() && (line->HasFloats() || !willReflowAgain)) {
      lastLineMovedUp = true;

      bool maybeReflowingForFirstTime =
          line->IStart() == 0 && line->BStart() == 0 && line->ISize() == 0 &&
          line->BSize() == 0;

      // Compute the dirty lines "before" BEnd, after factoring in
      // the running deltaBCoord value - the running value is implicit in
      // aState.mBCoord.
      nscoord oldB = line->BStart();
      nscoord oldBMost = line->BEnd();

      NS_ASSERTION(!willReflowAgain || !line->IsBlock(),
                   "Don't reflow blocks while willReflowAgain is true, reflow "
                   "of block abs-pos children depends on this");

      if (shouldBreakForPageName) {
        // Immediately fragment for page-name. It is possible we could break
        // out of the loop right here, but this should make it more similar to
        // what happens when reflow causes fragmentation.
        // Set the page name, so that PushTruncatedLine does not need to
        // recalculate the new page name.
        PresShell()->FrameConstructor()->SetNextPageContentFramePageName(
            nextPageName ? nextPageName : GetAutoPageValue());
        PushTruncatedLine(aState, line, &keepGoing,
                          ComputeNewPageNameIfNeeded::No);
      } else {
        // Reflow the dirty line. If it's an incremental reflow, then force
        // it to invalidate the dirty area if necessary
        usedOverflowWrap |= ReflowLine(aState, line, &keepGoing);
      }

      if (aState.mReflowInput.WillReflowAgainForClearance()) {
        line->MarkDirty();
        willReflowAgain = true;
        // Note that once we've entered this state, every line that gets here
        // (e.g. because it has floats) gets marked dirty and reflowed again.
        // in the next pass. This is important, see above.
      }

      if (line->HasFloats()) {
        reflowedFloat = true;
      }

      if (!keepGoing) {
        DumpLine(aState, line, deltaBCoord, -1);
        if (0 == line->GetChildCount()) {
          DeleteLine(aState, line, line_end);
        }
        break;
      }

      // Test to see whether the margin that should be carried out
      // to the next line (NL) might have changed. In ReflowBlockFrame
      // we call nextLine->MarkPreviousMarginDirty if the block's
      // actual carried-out block-end margin changed. So here we only
      // need to worry about the following effects:
      // 1) the line was just created, and it might now be blocking
      // a carried-out block-end margin from previous lines that
      // used to reach NL from reaching NL
      // 2) the line used to be empty, and is now not empty,
      // thus blocking a carried-out block-end margin from previous lines
      // that used to reach NL from reaching NL
      // 3) the line wasn't empty, but now is, so a carried-out
      // block-end margin from previous lines that didn't used to reach NL
      // now does
      // 4) the line might have changed in a way that affects NL's
      // ShouldApplyBStartMargin decision. The three things that matter
      // are the line's emptiness, its adjacency to the block-start edge of the
      // block, and whether it has clearance (the latter only matters if the
      // block was and is adjacent to the block-start and empty).
      //
      // If the line is empty now, we can't reliably tell if the line was empty
      // before, so we just assume it was and do
      // nextLine->MarkPreviousMarginDirty. This means the checks in 4) are
      // redundant; if the line is empty now we don't need to check 4), but if
      // the line is not empty now and we're sure it wasn't empty before, any
      // adjacency and clearance changes are irrelevant to the result of
      // nextLine->ShouldApplyBStartMargin.
      if (line.next() != LinesEnd()) {
        bool maybeWasEmpty = oldB == line.next()->BStart();
        bool isEmpty = line->CachedIsEmpty();
        if (maybeReflowingForFirstTime /*1*/ ||
            (isEmpty || maybeWasEmpty) /*2/3/4*/) {
          line.next()->MarkPreviousMarginDirty();
          // since it's marked dirty, nobody will care about |deltaBCoord|
        }
      }

      // If the line was just reflowed for the first time, then its
      // old mBounds cannot be trusted so this deltaBCoord computation is
      // bogus. But that's OK because we just did
      // MarkPreviousMarginDirty on the next line which will force it
      // to be reflowed, so this computation of deltaBCoord will not be
      // used.
      deltaBCoord = line->BEnd() - oldBMost;

      // Now do an interrupt check. We want to do this only in the case when we
      // actually reflow the line, so that if we get back in here we'll get
      // further on the reflow before interrupting.
      aState.mPresContext->CheckForInterrupt(this);
    } else {
      aState.mOverflowTracker->Skip(line->mFirstChild, aState.mReflowStatus);
      // Nop except for blocks (we don't create overflow container
      // continuations for any inlines atm), so only checking mFirstChild
      // is enough

      lastLineMovedUp = deltaBCoord < 0;

      if (deltaBCoord != 0) {
        SlideLine(aState, line, deltaBCoord);
      }

      NS_ASSERTION(!line->IsDirty() || !line->HasFloats(),
                   "Possibly stale float cache here!");
      if (willReflowAgain && line->IsBlock()) {
        // If we're going to reflow everything again, and this line is a block,
        // then there is no need to recover float state. The line may contain
        // other lines with floats, but in that case RecoverStateFrom would only
        // add floats to the float manager. We don't need to do that because
        // everything's going to get reflowed again "for real". Calling
        // RecoverStateFrom in this situation could be lethal because the
        // block's descendant lines may have float caches containing dangling
        // frame pointers. Ugh!
        // If this line is inline, then we need to recover its state now
        // to make sure that we don't forget to move its floats by deltaBCoord.
      } else {
        // XXX EVIL O(N^2) EVIL
        aState.RecoverStateFrom(line, deltaBCoord);
      }

      // Keep mBCoord up to date in case we're propagating reflow damage
      // and also because our final height may depend on it. If the
      // line is inlines, then only update mBCoord if the line is not
      // empty, because that's what PlaceLine does. (Empty blocks may
      // want to update mBCoord, e.g. if they have clearance.)
      if (line->IsBlock() || !line->CachedIsEmpty()) {
        aState.mBCoord = line->BEnd();
      }

      needToRecoverState = true;

      if (reflowedPrevLine && !line->IsBlock() &&
          aState.mPresContext->HasPendingInterrupt()) {
        // Need to make sure to pull overflows from any prev-in-flows
        for (nsIFrame* inlineKid = line->mFirstChild; inlineKid;
             inlineKid = inlineKid->PrincipalChildList().FirstChild()) {
          inlineKid->PullOverflowsFromPrevInFlow();
        }
      }
    }

    // Record if we need to clear floats before reflowing the next
    // line. Note that inlineFloatClearType will be handled and
    // cleared before the next line is processed, so there is no
    // need to combine break types here.
    if (line->HasFloatClearTypeAfter()) {
      inlineFloatClearType = line->FloatClearTypeAfter();
    }

    if (LineHasClear(line.get())) {
      foundAnyClears = true;
    }

    DumpLine(aState, line, deltaBCoord, -1);

    if (aState.mPresContext->HasPendingInterrupt()) {
      willReflowAgain = true;
      // Another option here might be to leave |line| clean if
      // !HasPendingInterrupt() before the CheckForInterrupt() call, since in
      // that case the line really did reflow as it should have.  Not sure
      // whether that would be safe, so doing this for now instead.  Also not
      // sure whether we really want to mark all lines dirty after an
      // interrupt, but until we get better at propagating float damage we
      // really do need to do it this way; see comments inside MarkLineDirty.
      MarkLineDirtyForInterrupt(line);
    }
  }

  // Handle BR-clearance from the last line of the block
  if (inlineFloatClearType != UsedClear::None) {
    std::tie(aState.mBCoord, std::ignore) =
        aState.ClearFloats(aState.mBCoord, inlineFloatClearType);
  }

  if (needToRecoverState) {
    // Is this expensive?
    aState.ReconstructMarginBefore(line);

    // Update aState.mPrevChild as if we had reflowed all of the frames in
    // the last line.
    NS_ASSERTION(line == line_end || line->mFirstChild->GetPrevSibling() ==
                                         line.prev()->LastChild(),
                 "unexpected line frames");
    aState.mPrevChild = line == line_end ? mFrames.LastChild()
                                         : line->mFirstChild->GetPrevSibling();
  }

  // We can skip trying to pull up the next line if our height is constrained
  // (so we can report being incomplete) and there is no next in flow or we
  // were told not to or we know it will be futile, i.e.,
  // -- the next in flow is not changing
  // -- and we cannot have added more space for its first line to be
  // pulled up into,
  // -- it's an incremental reflow of a descendant
  // -- and we didn't reflow any floats (so the available space
  // didn't change)
  // -- my chain of next-in-flows either has no first line, or its first
  // line isn't dirty.
  bool heightConstrained =
      aState.mReflowInput.AvailableBSize() != NS_UNCONSTRAINEDSIZE;
  bool skipPull = willReflowAgain && heightConstrained;
  if (!skipPull && heightConstrained && aState.mNextInFlow &&
      (aState.mReflowInput.mFlags.mNextInFlowUntouched && !lastLineMovedUp &&
       !HasAnyStateBits(NS_FRAME_IS_DIRTY) && !reflowedFloat)) {
    // We'll place lineIter at the last line of this block, so that
    // nsBlockInFlowLineIterator::Next() will take us to the first
    // line of my next-in-flow-chain.  (But first, check that I
    // have any lines -- if I don't, just bail out of this
    // optimization.)
    LineIterator lineIter = this->LinesEnd();
    if (lineIter != this->LinesBegin()) {
      lineIter--;  // I have lines; step back from dummy iterator to last line.
      nsBlockInFlowLineIterator bifLineIter(this, lineIter);

      // Check for next-in-flow-chain's first line.
      // (First, see if there is such a line, and second, see if it's clean)
      if (!bifLineIter.Next() || !bifLineIter.GetLine()->IsDirty()) {
        skipPull = true;
      }
    }
  }

  if (skipPull && aState.mNextInFlow) {
    NS_ASSERTION(heightConstrained, "Height should be constrained here\n");
    if (aState.mNextInFlow->IsTrueOverflowContainer()) {
      aState.mReflowStatus.SetOverflowIncomplete();
    } else {
      aState.mReflowStatus.SetIncomplete();
    }
  }

  if (!skipPull && aState.mNextInFlow) {
    // Pull data from a next-in-flow if there's still room for more
    // content here.
    while (keepGoing && aState.mNextInFlow) {
      // Grab first line from our next-in-flow
      nsBlockFrame* nextInFlow = aState.mNextInFlow;
      nsLineBox* pulledLine;
      nsFrameList pulledFrames;
      if (!nextInFlow->mLines.empty()) {
        RemoveFirstLine(nextInFlow->mLines, nextInFlow->mFrames, &pulledLine,
                        &pulledFrames);
        ClearLineCursors();
      } else {
        // Grab an overflow line if there are any
        FrameLines* overflowLines = nextInFlow->GetOverflowLines();
        if (!overflowLines) {
          aState.mNextInFlow =
              static_cast<nsBlockFrame*>(nextInFlow->GetNextInFlow());
          continue;
        }
        bool last =
            RemoveFirstLine(overflowLines->mLines, overflowLines->mFrames,
                            &pulledLine, &pulledFrames);
        if (last) {
          nextInFlow->DestroyOverflowLines();
        }
      }

      if (pulledFrames.IsEmpty()) {
        // The line is empty. Try the next one.
        NS_ASSERTION(
            pulledLine->GetChildCount() == 0 && !pulledLine->mFirstChild,
            "bad empty line");
        nextInFlow->FreeLineBox(pulledLine);
        continue;
      }

      if (nextInFlow->MaybeHasLineCursor()) {
        if (pulledLine == nextInFlow->GetLineCursorForDisplay()) {
          nextInFlow->ClearLineCursorForDisplay();
        }
        if (pulledLine == nextInFlow->GetLineCursorForQuery()) {
          nextInFlow->ClearLineCursorForQuery();
        }
      }
      ReparentFrames(pulledFrames, nextInFlow, this);
      pulledLine->SetMovedFragments();

      NS_ASSERTION(pulledFrames.LastChild() == pulledLine->LastChild(),
                   "Unexpected last frame");
      NS_ASSERTION(aState.mPrevChild || mLines.empty(),
                   "should have a prevchild here");
      NS_ASSERTION(aState.mPrevChild == mFrames.LastChild(),
                   "Incorrect aState.mPrevChild before inserting line at end");

      // Shift pulledLine's frames into our mFrames list.
      mFrames.AppendFrames(nullptr, std::move(pulledFrames));

      // Add line to our line list, and set its last child as our new prev-child
      line = mLines.before_insert(LinesEnd(), pulledLine);
      aState.mPrevChild = mFrames.LastChild();

      // Reparent floats whose placeholders are in the line.
      ReparentFloats(pulledLine->mFirstChild, nextInFlow, true);

      DumpLine(aState, pulledLine, deltaBCoord, 0);
#ifdef DEBUG
      AutoNoisyIndenter indent2(gNoisyReflow);
#endif

      if (aState.mPresContext->HasPendingInterrupt()) {
        MarkLineDirtyForInterrupt(line);
      } else {
        // Now reflow it and any lines that it makes during it's reflow
        // (we have to loop here because reflowing the line may cause a new
        // line to be created; see SplitLine's callers for examples of
        // when this happens).
        while (line != LinesEnd()) {
          usedOverflowWrap |= ReflowLine(aState, line, &keepGoing);

          if (aState.mReflowInput.WillReflowAgainForClearance()) {
            line->MarkDirty();
            keepGoing = false;
            // If we are going to be reflowed again by our ancestor due to a
            // clearance frame being discovered, reset the reflow completion
            // status. The current status does not matter to our parent frame
            // since we will reflow again anyway. This also prevents the false
            // assumption that we are incomplete when reflowing under an
            // unconstrained available block-size.
            aState.mReflowStatus.Reset();
            break;
          }

          DumpLine(aState, line, deltaBCoord, -1);
          if (!keepGoing) {
            if (0 == line->GetChildCount()) {
              DeleteLine(aState, line, line_end);
            }
            break;
          }

          if (LineHasClear(line.get())) {
            foundAnyClears = true;
          }

          if (aState.mPresContext->CheckForInterrupt(this)) {
            MarkLineDirtyForInterrupt(line);
            break;
          }

          // If this is an inline frame then its time to stop
          ++line;
          aState.AdvanceToNextLine();
        }
      }
    }

    if (aState.mReflowStatus.IsIncomplete()) {
      aState.mReflowStatus.SetNextInFlowNeedsReflow();
    }  // XXXfr shouldn't set this flag when nextinflow has no lines
  }

  // Handle an odd-ball case: a list-item with no lines
  nsIFrame* outsideMarker = GetOutsideMarker();
  if (outsideMarker && mLines.empty()) {
    ReflowOutput metrics(aState.mReflowInput);
    WritingMode wm = aState.mReflowInput.GetWritingMode();
    ReflowOutsideMarker(
        outsideMarker, aState, metrics,
        aState.mReflowInput.ComputedPhysicalBorderPadding().top);
    NS_ASSERTION(!MarkerIsEmpty(outsideMarker) || metrics.BSize(wm) == 0,
                 "empty ::marker frame took up space");

    if (!MarkerIsEmpty(outsideMarker)) {
      // There are no lines so we have to fake up some y motion so that
      // we end up with *some* height.
      // (Note: if we're layout-contained, we have to be sure to leave our
      // ReflowOutput's BlockStartAscent() (i.e. the baseline) untouched,
      // because layout-contained frames have no baseline.)
      if (!aState.mReflowInput.mStyleDisplay->IsContainLayout() &&
          metrics.BlockStartAscent() == ReflowOutput::ASK_FOR_BASELINE) {
        nscoord ascent;
        WritingMode wm = aState.mReflowInput.GetWritingMode();
        if (nsLayoutUtils::GetFirstLineBaseline(wm, outsideMarker, &ascent)) {
          metrics.SetBlockStartAscent(ascent);
        } else {
          metrics.SetBlockStartAscent(metrics.BSize(wm));
        }
      }

      RefPtr<nsFontMetrics> fm =
          nsLayoutUtils::GetInflatedFontMetricsForFrame(this);

      nscoord minAscent = nsLayoutUtils::GetCenteredFontBaseline(
          fm, aState.mMinLineHeight, wm.IsLineInverted());
      nscoord minDescent = aState.mMinLineHeight - minAscent;

      aState.mBCoord +=
          std::max(minAscent, metrics.BlockStartAscent()) +
          std::max(minDescent, metrics.BSize(wm) - metrics.BlockStartAscent());

      nscoord offset = minAscent - metrics.BlockStartAscent();
      if (offset > 0) {
        outsideMarker->SetRect(outsideMarker->GetRect() + nsPoint(0, offset));
      }
    }
  }

  if (LinesAreEmpty() && ShouldHaveLineIfEmpty()) {
    aState.mBCoord += aState.mMinLineHeight;
  }

  if (foundAnyClears) {
    AddStateBits(NS_BLOCK_HAS_CLEAR_CHILDREN);
  } else {
    RemoveStateBits(NS_BLOCK_HAS_CLEAR_CHILDREN);
  }

#ifdef DEBUG
  VerifyLines(true);
  VerifyOverflowSituation();
  if (gNoisyReflow) {
    IndentBy(stdout, gNoiseIndent - 1);
    ListTag(stdout);
    printf(": done reflowing dirty lines (status=%s)\n",
           ToString(aState.mReflowStatus).c_str());
  }
#endif

  return usedOverflowWrap;
}
