void nsMathMLContainerFrame::SaveReflowAndBoundingMetricsFor(
    nsIFrame* aFrame, const ReflowOutput& aReflowOutput,
    const nsBoundingMetrics& aBoundingMetrics) {
  ReflowOutput* reflowOutput = new ReflowOutput(aReflowOutput);
  reflowOutput->mBoundingMetrics = aBoundingMetrics;
  aFrame->SetProperty(HTMLReflowOutputProperty(), reflowOutput);
}
