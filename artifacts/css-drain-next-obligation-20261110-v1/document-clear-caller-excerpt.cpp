  const IntersectionInput input =
      DOMIntersectionObserver::ComputeInputForIframeThrottling(*el->OwnerDoc());
  const IntersectionOutput output = DOMIntersectionObserver::Intersect(
      input, *el, DOMIntersectionObserver::BoxToUse::Content);
  return !output.Intersects();
}

void Document::DeletePresShell() {
  mExternalResourceMap.HideViewers();
  mPendingFullscreenEvents.Clear();

  // When our shell goes away, request that all our images be immediately
  // discarded, so we don't carry around decoded image data for a document we
  // no longer intend to paint.
  for (imgIRequest* image : mTrackedImages.Keys()) {
    image->RequestDiscard();
  }

  // Now that we no longer have a shell, we need to forget about any FontFace
  // objects for @font-face rules that came from the style set. There's no need
  // to call EnsureStyleFlush either, the shell is going away anyway, so there's
  // no point on it.
  mFontFaceSetDirty = true;

  if (IsEditingOn()) {
    TurnEditingOff();
  }

  mPresShell = nullptr;

  ClearStaleServoData();
  AssertNoStaleServoDataIn(*this);

  mStyleSet->ShellDetachedFromDocument();
  mStyleSetFilled = false;
  mQuirkSheetAdded = false;
}

void Document::DisallowBFCaching(uint32_t aStatus) {
  NS_ASSERTION(!mBFCacheEntry, "We're already in the bfcache!");
  if (!mBFCacheDisallowed) {
    if (WindowGlobalChild* wgc = GetWindowGlobalChild()) {
