struct LineRange {
  LineRange(int32_t aStart, int32_t aEnd)
      : mUntranslatedStart(aStart), mUntranslatedEnd(aEnd) {
#ifdef DEBUG
    if (!IsAutoAuto()) {
      if (IsAuto()) {
        MOZ_ASSERT(aEnd >= kMinLine && aEnd <= kMaxLine, "invalid span");
      } else {
        MOZ_ASSERT(aStart >= kMinLine && aStart <= kMaxLine,
                   "invalid start line");
        MOZ_ASSERT(aEnd == int32_t(kAutoLine) ||
                       (aEnd >= kMinLine && aEnd <= kMaxLine),
                   "invalid end line");
      }
    }
#endif
  }
  bool IsAutoAuto() const { return mStart == kAutoLine && mEnd == kAutoLine; }
  bool IsAuto() const { return mStart == kAutoLine; }
  union {
    uint32_t mStart;
    int32_t mUntranslatedStart;
  };
  union {
    uint32_t mEnd;
    int32_t mUntranslatedEnd;
  };

};
