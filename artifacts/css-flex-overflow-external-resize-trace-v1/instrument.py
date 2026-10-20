from pathlib import Path
p=Path("layout/generic/nsContainerFrame.cpp")
s=p.read_text()
start=s.index("void nsContainerFrame::ReflowOverflowContainerChildren(")
end=s.index("\n}",start)+2
body=s[start:end]
anchor="""    // If the available block-size has changed, or the existing scrollable"""
log="""    const bool traceOverflow = IsFlexContainerFrame() && GetWritingMode().IsVerticalRL();
    if (traceOverflow) {
      fprintf(stderr, "OC_ANCESTRY flex=%p parent=%p\\n", static_cast<void*>(this), static_cast<void*>(GetParent()));
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

p = Path("layout/generic/nsColumnSetFrame.cpp")
s = p.read_text()
retained = Path("artifacts/css-flex-fragment-abspos-observer-review-v1/sources/base-nsColumnSetFrame.cpp")
assert p.read_bytes() == retained.read_bytes()
anchor = "    if (!reflowNext && !reflowChild) {"
assert s.count(anchor) == 1
s = s.replace(anchor, '''    if (wm.IsVerticalRL()) {
      fprintf(stderr, "COLUMN_TRACE gate set=%p child=%p next=%d childReflow=%d count=%d colB=%d\\n",
              static_cast<void*>(this), static_cast<void*>(child), int(reflowNext),
              int(reflowChild), int(colData.mColCount), aConfig.mColBSize);
    }
''' + anchor)
anchor = "      if (reflowNext) {\n        child->MarkSubtreeDirty();"
assert s.count(anchor) == 1
s = s.replace(anchor, '''      if (reflowNext) {
        if (wm.IsVerticalRL()) {
          fprintf(stderr, "COLUMN_TRACE mark set=%p child=%p pif=%p dirty=%d count=%d colB=%d\\n",
                  static_cast<void*>(this), static_cast<void*>(child),
                  static_cast<void*>(child->GetPrevInFlow()), int(child->HasAnyStateBits(NS_FRAME_IS_DIRTY)),
                  int(colData.mColCount), aConfig.mColBSize);
        }
        child->MarkSubtreeDirty();''')
anchor = "      reflowNext = aStatus.NextInFlowNeedsReflow();"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + '''
      if (wm.IsVerticalRL()) {
        fprintf(stderr, "COLUMN_TRACE after set=%p child=%p next=%d incomplete=%d overflowIncomplete=%d\\n",
                static_cast<void*>(this), static_cast<void*>(child), int(reflowNext),
                int(aStatus.IsIncomplete()), int(aStatus.IsOverflowIncomplete()));
      }
''')
p.write_text(s)
