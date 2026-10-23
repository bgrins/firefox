  nsIFrame* primaryFrame;
  ComputedStyle* const computedStyle = aItem.mComputedStyle;
  const nsStyleDisplay* display = computedStyle->StyleDisplay();
  if (bits & FCDATA_FUNC_IS_FULL_CTOR) {
    newFrame = (this->*(data->mFunc.mFullConstructor))(
        aState, aItem, aParentFrame, display, aFrameList);
    MOZ_ASSERT(newFrame, "Full constructor failed");
    primaryFrame = newFrame;
  } else {
    newFrame = (*data->mFunc.mCreationFunc)(mPresShell, computedStyle);

