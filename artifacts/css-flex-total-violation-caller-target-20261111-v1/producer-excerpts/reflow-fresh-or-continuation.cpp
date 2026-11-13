  FlexLayoutResult flr;
  PerFragmentFlexData fragmentData;
  const nsIFrame* prevInFlow = GetPrevInFlow();
  if (!prevInFlow) {
    const LogicalSize tentativeContentBoxSize = aReflowInput.ComputedSize();
    const nscoord tentativeContentBoxMainSize =
        axisTracker.MainComponent(tentativeContentBoxSize);
    const nscoord tentativeContentBoxCrossSize =
        axisTracker.CrossComponent(tentativeContentBoxSize);

    // Calculate gap sizes for main and cross axis. We only need them in
    // DoFlexLayout in the first-in-flow, so no need to worry about consumed
    // block-size.
    //
    // NOTE: tentativeContentBoxSize might be definite but gapPercentageBasis
    // indefinite, due to e.g. mTreatBSizeAsIndefinite.
    LogicalSize gapPercentageBasis = tentativeContentBoxSize;
    gapPercentageBasis.BSize(wm) =
        aReflowInput.ComputedBSizeAsPercentageBasis();
    const auto& mainGapStyle =
        axisTracker.IsRowOriented() ? stylePos->mColumnGap : stylePos->mRowGap;
    const auto& crossGapStyle =
        axisTracker.IsRowOriented() ? stylePos->mRowGap : stylePos->mColumnGap;
    const nscoord mainGapSize = nsLayoutUtils::ResolveGapToLength(
        mainGapStyle, axisTracker.MainComponent(gapPercentageBasis));
    const nscoord crossGapSize = nsLayoutUtils::ResolveGapToLength(
        crossGapStyle, axisTracker.CrossComponent(gapPercentageBasis));

    // When fragmenting a flex container, we run the flex algorithm without
    // regards to pagination in order to compute the flex container's desired
    // content-box size. https://drafts.csswg.org/css-flexbox-1/#pagination-algo
    //
    // Note: For a multi-line column-oriented flex container, the sample
    // algorithm suggests we wrap the flex line at the block-end edge of a
    // column/page, but we do not implement it intentionally. This brings the
    // layout result closer to the one as if there's no fragmentation.
    AutoTArray<StrutInfo, 1> struts;
    flr = DoFlexLayout(aReflowInput, tentativeContentBoxMainSize,
                       tentativeContentBoxCrossSize, axisTracker, mainGapSize,
                       crossGapSize, struts, containerInfo);

    if (!struts.IsEmpty()) {
      // We're restarting flex layout, with new knowledge of collapsed items.
      flr.mLines.Clear();
      flr.mPlaceholders.Clear();
      flr = DoFlexLayout(aReflowInput, tentativeContentBoxMainSize,
                         tentativeContentBoxCrossSize, axisTracker, mainGapSize,
                         crossGapSize, struts, containerInfo);
    }
  } else {
    flr = GenerateFlexLayoutResult();
    auto* fragmentDataProp =
        prevInFlow->GetProperty(PerFragmentFlexData::Prop());
    MOZ_ASSERT(fragmentDataProp,
               "PerFragmentFlexData should be set in our prev-in-flow!");
    fragmentData = *fragmentDataProp;
  }
