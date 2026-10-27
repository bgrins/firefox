static MeasuringReflowResult MeasuringReflow(
    nsIFrame* aChild, const ReflowInput* aReflowInput, gfxContext* aRC,
    const LogicalSize& aAvailableSize, const LogicalSize& aCBSize,
    nscoord aIMinSizeClamp = NS_MAXSIZE, nscoord aBMinSizeClamp = NS_MAXSIZE) {
  MOZ_ASSERT(aChild->IsGridItem(), "aChild should be a grid item!");
  auto wm = aChild->GetWritingMode();
  // NOTE: Reflowing or FinishReflowChild might invalidate the cache.
  if (const auto* cachedMeasurement =
          aChild->GetProperty(GridItemCachedBAxisMeasurement::Prop());
      cachedMeasurement && cachedMeasurement->IsValidFor(aChild, aCBSize)) {
    GRID_LOG(
        "[perf] MeasuringReflow accepted cached value=%d, child=%p, "
        "aCBSize.ISize=%d",
        cachedMeasurement->Result().mBSize, aChild, aCBSize.ISize(wm));
    return cachedMeasurement->Result();
  }

  auto* parent = static_cast<nsGridContainerFrame*>(aChild->GetParent());
  nsPresContext* pc = aChild->PresContext();
  Maybe<ReflowInput> dummyParentState;
  const ReflowInput* rs = aReflowInput;
  if (!aReflowInput) {
    MOZ_ASSERT(!parent->HasAnyStateBits(NS_FRAME_IN_REFLOW));
    dummyParentState.emplace(
        pc, parent, aRC,
        LogicalSize(parent->GetWritingMode(), 0, NS_UNCONSTRAINEDSIZE),
        ReflowInput::InitFlag::DummyParentReflowInput);
    rs = dummyParentState.ptr();
  }
#ifdef DEBUG
  // This will suppress various ABSURD_SIZE warnings for this reflow.
  parent->SetProperty(nsContainerFrame::DebugReflowingWithInfiniteISize(),
                      true);
#endif
  ComputeSizeFlags csFlags = ComputeSizeFlag::IsGridMeasuringReflow;
  // Shrink-wrap grid items that will be aligned (rather than stretched) in
  // their own inline axis.
  if (!parent->GridItemShouldStretch(aChild, LogicalAxis::Inline)) {
    csFlags += ComputeSizeFlag::ShrinkWrap;
  }
  if (aAvailableSize.ISize(wm) == INFINITE_ISIZE_COORD) {
    csFlags += ComputeSizeFlag::ShrinkWrap;
  }
  if (aIMinSizeClamp != NS_MAXSIZE) {
    csFlags += ComputeSizeFlag::IClampMarginBoxMinSize;
  }
  if (aBMinSizeClamp != NS_MAXSIZE) {
    csFlags += ComputeSizeFlag::BClampMarginBoxMinSize;
    aChild->SetProperty(nsIFrame::BClampMarginBoxMinSizeProperty(),
                        aBMinSizeClamp);
  } else {
    aChild->RemoveProperty(nsIFrame::BClampMarginBoxMinSizeProperty());
  }
  ReflowInput childRI(pc, *rs, aChild, aAvailableSize, Some(aCBSize), {}, {},
                      csFlags);

  // FIXME (perf): It would be faster to do this only if the previous reflow of
  // the child was not a measuring reflow, and only if the child does some of
  // the things that are affected by ComputeSizeFlag::IsGridMeasuringReflow.
  childRI.SetBResize(true);
  // Not 100% sure this is needed, but be conservative for now:
  childRI.SetBResizeForPercentages(true);

  ReflowOutput childSize(childRI);
  nsReflowStatus childStatus;
  const nsIFrame::ReflowChildFlags flags =
      nsIFrame::ReflowChildFlags::NoMoveFrame |
      nsIFrame::ReflowChildFlags::NoDeleteNextInFlowChild;

  parent->ReflowChild(aChild, pc, childSize, childRI, wm, LogicalPoint(wm),
                      nsSize(), flags, childStatus);
  nsContainerFrame::FinishReflowChild(aChild, pc, childSize, &childRI, wm,
                                      LogicalPoint(wm), nsSize(), flags);
#ifdef DEBUG
  parent->RemoveProperty(nsContainerFrame::DebugReflowingWithInfiniteISize());
#endif

  const MeasuringReflowResult result{
      childSize.BSize(wm),
      childSize.BSize(wm) -
          childRI.ComputedLogicalBorderPadding(wm).BStartEnd(wm)};
  if (GridItemCachedBAxisMeasurement* cachedMeasurement =
          aChild->GetProperty(GridItemCachedBAxisMeasurement::Prop())) {
    cachedMeasurement->Update(aChild, aCBSize, result);
    GRID_LOG(
        "[perf] MeasuringReflow rejected but updated cached value=%d, "
        "child=%p, aCBSize.ISize=%d",
        result.mBSize, aChild, aCBSize.ISize(wm));
  } else {
    cachedMeasurement =
        new GridItemCachedBAxisMeasurement(aChild, aCBSize, result);
    aChild->SetProperty(GridItemCachedBAxisMeasurement::Prop(),
                        cachedMeasurement);
    GRID_LOG(
        "[perf] MeasuringReflow created new cached value=%d, child=%p, "
        "aCBSize.ISize=%d",
        result.mBSize, aChild, aCBSize.ISize(wm));
  }

  return result;
}
