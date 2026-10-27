#include <cinttypes>
#include <climits>
#include <cstdio>

#include "mozilla/AppUnits.h"
#include "nsCoord.h"

using mozilla::AppUnitsPerCSSPixel;

int main() {
#include "conversion.inc"
  static_assert(AppUnitsPerCSSPixel() == 60);
  uint64_t checked = 0;
  uint64_t differences = 0;
  auto check = [&](int32_t value, bool preserve) {
    const int32_t remainder = value % 60;
    const int32_t reference = value / 60 + (remainder >= 30) - (remainder <= -30);
    const int32_t result = toCSSPixels(value);
    const int32_t old = NSAppUnitsToIntPixels(value, 60.0f);
    ++checked;
    differences += result != old;
    if (result != reference || (preserve && result != old) ||
        (value != INT32_MIN && result != -toCSSPixels(-value)) ||
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
      INT32_MIN, -536872800, -503316540, -503316000, -16777216,
      -60, 0, 60, 16777216, 503316000, 503316540, 536872800, INT32_MAX};
  for (const int64_t center : centers) {
    for (int64_t delta = -120; delta <= 120; ++delta) {
      const int64_t value = center + delta;
      if (value >= INT32_MIN && value <= INT32_MAX &&
          !check(int32_t(value), value >= -16777216 && value <= 16777216)) {
        return 1;
      }
    }
  }
  if (toCSSPixels(503316540) != 8388609 ||
      toCSSPixels(-503316540) != -8388609 || !differences) {
    return 1;
  }
  std::printf("PASS checked=%" PRIu64 " changed_from_float=%" PRIu64 "\n",
              checked, differences);
  return 0;
}
