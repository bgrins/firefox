
struct GridBundleAbiFacts {
  char frame_size[sizeof(nsGridContainerFrame)];
  char frame_align[alignof(nsGridContainerFrame)];
  char cache_size[sizeof(nsGridContainerFrame::CachedBAxisMeasurement)];
  char cache_align[alignof(nsGridContainerFrame::CachedBAxisMeasurement)];
  char result_size[sizeof(MeasuringReflowResult)];
  char result_align[alignof(MeasuringReflowResult)];
};
static_assert(sizeof(GridBundleAbiFacts) > 0);
