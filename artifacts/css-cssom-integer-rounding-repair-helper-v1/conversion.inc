  auto toCSSPixels = [](nscoord aCoord) {
    constexpr int32_t scale = AppUnitsPerCSSPixel();
    const int64_t bias = aCoord >= 0 ? scale / 2 : -scale / 2;
    return int32_t((int64_t(aCoord) + bias) / scale);
  };
