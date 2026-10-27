void nsIFrame::GetChildLists(nsTArray<ChildList>* aLists) const {
  if (const auto* absCB = GetAbsoluteContainingBlock()) {
    const nsFrameList& absoluteList = absCB->GetChildList();
    absoluteList.AppendIfNonempty(aLists, FrameChildListID::Absolute);
    const nsFrameList& pushedAbsoluteList = absCB->GetPushedChildList();
    pushedAbsoluteList.AppendIfNonempty(aLists,
                                        FrameChildListID::PushedAbsolute);
  }
}
