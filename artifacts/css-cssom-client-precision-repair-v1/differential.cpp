#include <cinttypes>
#include <climits>
#include <cmath>
#include <cstdio>

#include "mozilla/AppUnits.h"
#include "nsCoord.h"

using mozilla::AppUnitsPerCSSPixel;

#include "conversion.inc"

int main() {
  static_assert(AppUnitsPerCSSPixel() == 60);
  uint64_t checked = 0;
  uint64_t differences = 0;
  auto check = [&](int32_t value, bool preserve) {
    const int32_t remainder = value % 60;
    const int32_t reference = value / 60 + (remainder >= 30) - (remainder < -30);
    const int32_t result = AppUnitsToClientCSSPixels(value);
    const int32_t old = int32_t(std::floor(
        double(NSAppUnitsToFloatPixels(value, 60.0f)) + 0.5));
    ++checked;
    differences += result != old;
    if (result != reference || (preserve && result != old) ||
        (value % 60 == 0 && result != value / 60)) {
      std::printf("FAIL input=%" PRId32 " candidate=%" PRId32
                  " reference=%" PRId32 " old=%" PRId32 "\n",
                  value, result, reference, old);
      return false;
    }
    return true;
  };
  for (int32_t value = -1048576; value <= 1048576; ++value) {
    if (!check(value, true)) {
      return 1;
    }
  }
  const int64_t centers[] = {
      INT32_MIN, -1006633020, -1006632000, -16777216, -90, -30,
      0, 30, 90, 16777216, 1006632000, 1006633020, INT32_MAX};
  for (const int64_t center : centers) {
    for (int64_t delta = -120; delta <= 120; ++delta) {
      const int64_t value = center + delta;
      if (value >= INT32_MIN && value <= INT32_MAX &&
          !check(int32_t(value), value >= -16777216 && value <= 16777216)) {
        return 1;
      }
    }
  }
  if (AppUnitsToClientCSSPixels(1006633020) != 16777217 ||
      AppUnitsToClientCSSPixels(-30) != 0 ||
      AppUnitsToClientCSSPixels(-90) != -1 || !differences) {
    return 1;
  }
  std::printf("PASS checked=%" PRIu64 " changed_from_float=%" PRIu64 "\n",
              checked, differences);
  return 0;
}
