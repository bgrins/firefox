void nsIFrame::MarkPrincipalChildrenDirty() {
  for (nsIFrame* childFrame : PrincipalChildList()) {
    childFrame->MarkSubtreeDirty();
  }
}
