int main() {
  int id = 0;
  for (int hidden = 0; hidden < 2; ++hidden)
  for (int dirty = 0; dirty < 2; ++dirty)
  for (int cacheMode = 0; cacheMode < 3; ++cacheMode)
  for (int sizeMode = 0; sizeMode < 2; ++sizeMode)
  for (int border = 0; border < 2; ++border)
  for (int provider = 0; provider < 2; ++provider)
  for (int forceKeyMode = 0; forceKeyMode < 2; ++forceKeyMode) {
    providerMode = provider;
    Document document;
    PresShell shell;
    shell.mDocument = &document;
    nsIFrame parent, frame;
    parent.hidden = hidden;
    parent.shell = frame.shell = &shell;
    frame.parent = &parent;
    frame.state = dirty ? NS_FRAME_IS_DIRTY : 0;
    ReflowInput current;
    current.mFrame = &frame;
    current.computed = sizeMode ? LogicalSize{17, 13} : LogicalSize{24, 32};
    current.mContainingBlockSize = {320, 0};
    current.bp = {border, border * 2, border * 3, border * 4};
    ReflowInput cached = current;
    if (cacheMode == 2) cached.mContainingBlockSize.b = 32;
    ReflowOutput prior(cached);
    prior.size = Provider(cached);
    frame.geometry = prior.size;
    if (cacheMode) frame.cache = new CachedFlexItemData(cached, prior, FlexItemReflowType::Measuring);
    nsFlexContainerFrame container;
    nsFlexContainerFrame::FlexItem item{&frame};
    const nscoord measured = container.MeasureBSizeForFlexItem(item, current).BSize();
    const LogicalSize after = frame.geometry;
    const bool afterDirty = frame.IsSubtreeDirty();
    const bool reused = container.reflows == 0;
    ReflowInput forced = current;
    forced.mContainingBlockSize.b = forceKeyMode ? 32 : 0;
    document.flush = [&] { container.MeasureBSizeForFlexItem(item, forced); };
    shell.EnsureReflowIfFrameHasHiddenContent(&frame);
    const LogicalSize queried = frame.geometry;
    const bool queryDirty = frame.IsSubtreeDirty();
    const int forces = shell.forces;
    shell.EnsureReflowIfFrameHasHiddenContent(&frame);
    std::cout << id++ << ',' << after.i << ',' << after.b << ',' << afterDirty
              << ',' << measured << ',' << reused << ',' << queried.i << ','
              << queried.b << ',' << queryDirty << ',' << forces << ','
              << frame.geometry.i << ',' << frame.geometry.b << ','
              << frame.IsSubtreeDirty() << ',' << shell.forces << '\n';
    delete static_cast<CachedFlexItemData*>(frame.cache);
  }
}
