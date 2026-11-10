    // alive.
    //
    // This can go away once
    // https://bugzilla.mozilla.org/show_bug.cgi?id=1620312 is fixed.
    uint32_t targetDepth =
        MOZ_KnownLive(observer)->BroadcastActiveObservations();
    if (targetDepth < shallowestTargetDepth) {
      shallowestTargetDepth = targetDepth;
    }
  }

  return shallowestTargetDepth;
}

bool Document::HasAnySkippedResizeObservations() const {
  for (const auto* observer : mResizeObservers) {
    if (observer->HasSkippedObservations()) {
      return true;
    }
  }
  return false;
}

bool Document::HasAnyActiveResizeObservations() const {
  for (const auto* observer : mResizeObservers) {
    if (observer->HasActiveObservations()) {
      return true;
    }
  }
  return false;
}

void Document::ClearStaleServoData() {
  DocumentStyleRootIterator iter(this);
  while (Element* root = iter.GetNextStyleRoot()) {
    RestyleManager::ClearServoDataFromSubtree(root);
  }
}

// https://drafts.csswg.org/css-view-transitions-1/#dom-document-startviewtransition
already_AddRefed<ViewTransition> Document::StartViewTransition(
    const ViewTransitionUpdateCallbackOrStartViewTransitionOptions& aOptions) {
  // Steps 1-3

  nsTArray<RefPtr<nsAtom>> types;
  ViewTransitionUpdateCallback* cb = nullptr;
  if (aOptions.IsViewTransitionUpdateCallback()) {
    cb = &aOptions.GetAsViewTransitionUpdateCallback();
  } else {
    MOZ_ASSERT(aOptions.IsStartViewTransitionOptions());
