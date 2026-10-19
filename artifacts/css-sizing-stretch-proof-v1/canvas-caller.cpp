nsHTMLCanvasFrame::ComputeSize(
    const SizeComputationInput& aSizingInput, WritingMode aWM,
    const LogicalSize& aCBSize, nscoord aAvailableISize,
    const LogicalSize& aMargin, const LogicalSize& aBorderPadding,
    const StyleSizeOverrides& aSizeOverrides, ComputeSizeFlags aFlags) {
  return {ComputeSizeWithIntrinsicDimensions(
              aSizingInput.mRenderingContext, aWM, GetIntrinsicSize(),
              GetAspectRatio(), aCBSize, aMargin, aBorderPadding,
              aSizeOverrides, aFlags),
          AspectRatioUsage::None};
}
