from pathlib import Path
p=Path("layout/generic/nsContainerFrame.cpp")
s=p.read_text()
start=s.index("void nsContainerFrame::ReflowOverflowContainerChildren(")
end=s.index("\n}",start)+2
body=s[start:end]
anchor="""    // If the available block-size has changed, or the existing scrollable"""
log="""    const bool traceOverflow = IsFlexContainerFrame() && GetWritingMode().IsVerticalRL();
    if (traceOverflow) {
      const bool dirty = frame->IsSubtreeDirty();
      const int exceeds = !shouldReflowAllKids && !dirty
                              ? int(ScrollableOverflowExceedsAvailableBSize(frame))
                              : -1;
      fprintf(stderr, "OC_TRACE pre parent=%p frame=%p pif=%p oldC=%d newC=%d avail=%d all=%d dirty=%d exceeds=%d pd=%d ir=%d br=%d rel=%d balance=%d x=%d normal=%d w=%d\\n",
              static_cast<void*>(this), static_cast<void*>(frame),
              static_cast<void*>(frame->GetPrevInFlow()), GetSize().width,
              aContainerSize ? aContainerSize->width : -1,
              aReflowInput.AvailableBSize(), int(shouldReflowAllKids), int(dirty), exceeds,
              int(HasAnyStateBits(NS_FRAME_IS_DIRTY)), int(aReflowInput.IsIResize()),
              int(aReflowInput.IsBResize()), int(HasAnyStateBits(NS_FRAME_CONTAINS_RELATIVE_BSIZE)),
              int(aReflowInput.mFlags.mIsInLastColumnBalancingReflow),
              frame->GetPosition().x, frame->GetNormalPosition().x, frame->GetSize().width);
    }

"""
assert body.count(anchor)==1;body=body.replace(anchor,log+anchor)
anchor="""      nsIFrame* prevInFlow = frame->GetPrevInFlow();"""
assert body.count(anchor)==1;body=body.replace(anchor,"""      if (traceOverflow) fprintf(stderr, "OC_TRACE branch=reflow frame=%p\\n", static_cast<void*>(frame));
"""+anchor)
anchor="""      tracker.Skip(frame, aStatus);"""
assert body.count(anchor)==1;body=body.replace(anchor,"""      if (traceOverflow) fprintf(stderr, "OC_TRACE branch=skip frame=%p\\n", static_cast<void*>(frame));
"""+anchor)
anchor="""    ConsiderChildOverflow(aOverflowRects, frame, OverflowAreaUnionFlags::None);"""
assert body.count(anchor)==1;body=body.replace(anchor,"""    if (traceOverflow) fprintf(stderr, "OC_TRACE post frame=%p x=%d normal=%d w=%d\\n", static_cast<void*>(frame), frame->GetPosition().x, frame->GetNormalPosition().x, frame->GetSize().width);
"""+anchor)
p.write_text(s[:start]+body+s[end:])
