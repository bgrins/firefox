enum class MeasuringReflowRequest : uint8_t {
  Geometry,
  NaturalFirst,
  NaturalLast,
  GridBlockFirst,
  GridBlockLast,
  GridInlineFirst,
  GridInlineLast
};

static bool IsGridMeasuringReflowRequest(MeasuringReflowRequest aRequest) {
  return aRequest == MeasuringReflowRequest::GridBlockFirst ||
         aRequest == MeasuringReflowRequest::GridBlockLast ||
         aRequest == MeasuringReflowRequest::GridInlineFirst ||
         aRequest == MeasuringReflowRequest::GridInlineLast;
}

struct MeasuringReflowGeometry {
  // The reported sizes and live geometry belong to the completed measurement.
  nscoord mBSize = 0;
  nscoord mContentBSize = 0;
  nsSize mPhysicalSize;
  nsMargin mUsedMargin;
};

struct MeasuringReflowResult : MeasuringReflowGeometry {
  Maybe<nscoord> mBaseline;
};

  struct Snapshot {
    MeasuringReflowGeometry mGeometry;
    PerLogicalAxis<PerBaseline<nscoord>> mBaselines{};
    MeasuringReflowRequest mRequest = MeasuringReflowRequest::Geometry;
    bool mHasBaseline = false;
    bool mHasGridBaselines = false;

    MeasuringReflowResult Project(MeasuringReflowRequest aRequest) const {
      MeasuringReflowResult result;
      static_cast<MeasuringReflowGeometry&>(result) = mGeometry;
      if (aRequest == MeasuringReflowRequest::Geometry) {
        return result;
      }
      if (mHasGridBaselines && IsGridMeasuringReflowRequest(aRequest)) {
        const auto axis =
            aRequest == MeasuringReflowRequest::GridBlockFirst ||
                    aRequest == MeasuringReflowRequest::GridBlockLast
                ? LogicalAxis::Block
                : LogicalAxis::Inline;
        const auto group =
            aRequest == MeasuringReflowRequest::GridBlockFirst ||
                    aRequest == MeasuringReflowRequest::GridInlineFirst
                ? BaselineSharingGroup::First
                : BaselineSharingGroup::Last;
        result.mBaseline.emplace(mBaselines[axis][group]);
      } else if (mHasBaseline) {
        result.mBaseline.emplace(
            mBaselines[LogicalAxis::Block][BaselineSharingGroup::First]);
      }
      return result;
    }

    Maybe<MeasuringReflowResult> Result(MeasuringReflowRequest aRequest) const {
      if (aRequest == MeasuringReflowRequest::Geometry || aRequest == mRequest ||
          (mHasGridBaselines && IsGridMeasuringReflowRequest(aRequest))) {
        return Some(Project(aRequest));
      }
      return Nothing();
    }
  };
