void nsFlexContainerFrame::GenerateFlexLines(
    const ReflowInput& aReflowInput, const nscoord aTentativeContentBoxMainSize,
    const nscoord aTentativeContentBoxCrossSize,
    const nsTArray<StrutInfo>& aStruts, const FlexboxAxisTracker& aAxisTracker,
    nscoord aMainGapSize, nsTArray<nsIFrame*>& aPlaceholders,
    nsTArray<FlexLine>& aLines, bool& aHasCollapsedItems) {
  MOZ_ASSERT(aLines.IsEmpty(), "Expecting outparam to start out empty");

  auto ConstructNewFlexLine = [&aLines, aMainGapSize]() {
    return aLines.EmplaceBack(aMainGapSize);
  };

  // We have at least one FlexLine. Even an empty flex container has a single
  // (empty) flex line.
  FlexLine* curLine = ConstructNewFlexLine();

  nscoord wrapThreshold;
  if (IsSingleLine(aReflowInput.mFrame, aReflowInput.mStylePosition)) {
    // Not wrapping. Set threshold to sentinel value that tells us not to wrap.
    wrapThreshold = NS_UNCONSTRAINEDSIZE;
  } else {
    // Wrapping! Set wrap threshold to flex container's content-box main-size.
    wrapThreshold = aTentativeContentBoxMainSize;

    // If the flex container doesn't have a definite content-box main-size
    // (e.g. if main axis is vertical & 'height' is 'auto'), make sure we at
    // least wrap when we hit its max main-size.
    if (wrapThreshold == NS_UNCONSTRAINEDSIZE) {
      const nscoord flexContainerMaxMainSize =
          aAxisTracker.MainComponent(aReflowInput.ComputedMaxSize());
      wrapThreshold = flexContainerMaxMainSize;
    }
  }

  // Tracks the index of the next strut, in aStruts (and when this hits
  // aStruts.Length(), that means there are no more struts):
  uint32_t nextStrutIdx = 0;

  // Overall index of the current flex item in the flex container. (This gets
  // checked against entries in aStruts.)
  uint32_t itemIdxInContainer = 0;

  CSSOrderAwareFrameIterator iter(
      this, FrameChildListID::Principal,
      CSSOrderAwareFrameIterator::ChildFilter::IncludeAll,
      CSSOrderAwareFrameIterator::OrderState::Unknown,
      OrderingPropertyForIter(this));

  AddOrRemoveStateBits(NS_STATE_FLEX_NORMAL_FLOW_CHILDREN_IN_CSS_ORDER,
                       iter.ItemsAreAlreadyInOrder());

  const bool useMozBoxCollapseBehavior =
      StyleVisibility()->UseLegacyCollapseBehavior();

  for (; !iter.AtEnd(); iter.Next()) {
    nsIFrame* childFrame = *iter;
    // Don't create flex items / lines for placeholder frames:
    if (childFrame->IsPlaceholderFrame()) {
      aPlaceholders.AppendElement(childFrame);
      continue;
    }

    const bool collapsed = childFrame->StyleVisibility()->IsCollapse();
    aHasCollapsedItems = aHasCollapsedItems || collapsed;

    if (useMozBoxCollapseBehavior && collapsed) {
      // Legacy visibility:collapse behavior: make a 0-sized strut. (No need to
      // bother with aStruts and remembering cross size.)
      curLine->Items().EmplaceBack(childFrame, 0, aReflowInput.GetWritingMode(),
                                   aAxisTracker);
    } else if (nextStrutIdx < aStruts.Length() &&
               aStruts[nextStrutIdx].mItemIdx == itemIdxInContainer) {
      // Use the simplified "strut" FlexItem constructor:
      curLine->Items().EmplaceBack(childFrame,
                                   aStruts[nextStrutIdx].mStrutCrossSize,
                                   aReflowInput.GetWritingMode(), aAxisTracker);
      nextStrutIdx++;
    } else {
      GenerateFlexItemForChild(*curLine, childFrame, aReflowInput, aAxisTracker,
                               aTentativeContentBoxCrossSize);
    }

    // Check if we need to wrap the newly appended item to a new line, i.e. if
    // its outer hypothetical main size pushes our line over the threshold,
    // or the line already contains an oversized first item.
    // But we don't wrap if the line-length is unconstrained, nor do we wrap if
    // this was the first item on the line.
    if (wrapThreshold != NS_UNCONSTRAINEDSIZE &&
        curLine->Items().Length() > 1) {
      // If the line will be longer than wrapThreshold or at least as long as
      // nscoord_MAX because of the newly appended item, then wrap and move the
      // item to a new line.
      auto newOuterSize = curLine->TotalOuterHypotheticalMainSize();
      newOuterSize += curLine->Items().LastElement().OuterMainSize();

      // Account for gap between this line's previous item and this item.
      newOuterSize += aMainGapSize;

      if (curLine->TotalOuterHypotheticalMainSize() > wrapThreshold ||
          newOuterSize >= nscoord_MAX || newOuterSize > wrapThreshold) {
        curLine = ConstructNewFlexLine();

        // Get the previous line after adding a new line because the address can
        // change if nsTArray needs to reallocate a new space for the new line.
        FlexLine& prevLine = aLines[aLines.Length() - 2];

        // Move the item from the end of prevLine to the end of curLine.
        curLine->Items().AppendElement(prevLine.Items().PopLastElement());
      }
    }

    // Update the line's bookkeeping about how large its items collectively are.
    curLine->AddLastItemToMainSizeTotals();
    itemIdxInContainer++;
  }
}
