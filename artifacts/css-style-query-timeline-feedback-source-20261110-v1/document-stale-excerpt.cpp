  }

  // https://drafts.csswg.org/scroll-animations-1/#stale-timelines
  // After the resize observer loop, sample any timelines that haven't yet had
  // their current time updated this frame, and run an additional style and
  // layout pass so the new sample is reflected before paint.
  //
  // Bug 2040244 - Move this into RO loop.
  // https://github.com/whatwg/html/pull/11613
  if (auto* pc = GetPresContext()) {
    pc->AnimationManager()->UpdateDeferredTimelineChanges();
  }
  if (mTimelinesController.UpdateStaleTimelines()) {
    FlushPendingNotifications(ctf);
  }

  // Step 17: For each doc of docs, if the focused area of doc is not a
  // focusable area, then run the focusing steps for doc's viewport, and set
  // doc's relevant global object's navigation API's focus changed during
  // ongoing navigation to false.
  //
  // We do it here rather than a separate walk over the docs for convenience,
  // and because I don't think there's a strong reason for it to be a separate
  // walk altogether, see https://github.com/whatwg/html/issues/11211
  const bool fixedUpFocus = ps->FixUpFocus();
  if (fixedUpFocus) {
    FlushPendingNotifications(ctf);
  }

