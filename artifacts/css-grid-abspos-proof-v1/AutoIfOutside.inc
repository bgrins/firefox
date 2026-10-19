  static int32_t AutoIfOutside(int32_t aLine, int32_t aMin, int32_t aMax) {
    MOZ_ASSERT(aMin <= aMax);
    if (aLine < aMin || aLine > aMax) {
      return kAutoLine;
    }
    return aLine;
  }
