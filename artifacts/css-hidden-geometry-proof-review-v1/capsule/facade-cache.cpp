class nsFlexContainerFrame::CachedFlexItemData {
public:
  std::optional<CachedBAxisMeasurement> mBAxisMeasurement;
  CachedFlexItemData(const ReflowInput& in, const ReflowOutput& out,
                    FlexItemReflowType type) { Update(in, out, type); }
  void Update(const ReflowInput& in, const ReflowOutput& out, FlexItemReflowType) {
    mBAxisMeasurement.reset();
    mBAxisMeasurement.emplace(in, out);
  }
  static CachedFlexItemData* Prop() { return nullptr; }
};
