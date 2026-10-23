  // Even if mCreatingExtraFrames is set, we may need to SetPrimaryFrame for
  // generated content that doesn't have one yet.  Note that we have to examine
  // the frame bit, because by this point mIsGeneratedContent has been cleared
  // on aItem.
  if ((!aState.mCreatingExtraFrames ||
       (aItem.mContent->IsRootOfNativeAnonymousSubtree() &&
        !aItem.mContent->GetPrimaryFrame())) &&
      !(bits & FCDATA_SKIP_FRAMESET)) {
    aItem.mContent->SetPrimaryFrame(primaryFrame);
    ActiveLayerTracker::TransferActivityToFrame(aItem.mContent, primaryFrame);
  }
}
