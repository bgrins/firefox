#include <cmath>
#include <cstdint>
#include <cstdio>
#include <limits>
#include "mozilla/Assertions.h"
#include "constants.inc"

class SVGLength {
 public:
  static bool IsAbsoluteUnit(uint16_t);
  static float GetAbsUnitsPerAbsUnit(uint16_t, uint16_t);
};

#include "native.inc"

struct Oracle {
  const char* target;
  const char* source;
  uint16_t targetCode;
  uint16_t sourceCode;
  int numerator;
  int denominator;
};
#include "oracle.inc"

int main() {
  for (uint32_t code = 0; code <= UINT16_MAX; ++code) {
    const bool expected = code == 1 || (code >= 5 && code <= 11);
    if (SVGLength::IsAbsoluteUnit(static_cast<uint16_t>(code)) != expected) {
      return 2;
    }
  }
  for (const auto& row : kOracle) {
    const double expected = double(row.numerator) / row.denominator;
    const double actual = SVGLength::GetAbsUnitsPerAbsUnit(row.targetCode,
                                                         row.sourceCode);
    const double tolerance = 4 * std::numeric_limits<float>::epsilon() * expected;
    const bool match = std::isfinite(actual) &&
                       std::abs(actual - expected) <= tolerance;
    std::printf("{\"target\":\"%s\",\"source\":\"%s\",\"actual\":%.17g,"
                "\"expected\":%.17g,\"relative_error\":%.17g,"
                "\"tolerance\":%.17g,\"match\":%s}\n",
                row.target, row.source, actual, expected,
                std::abs(actual - expected) / expected, tolerance,
                match ? "true" : "false");
    if (row.targetCode == SVG_LENGTHTYPE_PX &&
        SVGLength::GetAbsUnitsPerAbsUnit(SVG_LENGTHTYPE_NUMBER, row.sourceCode) !=
            actual) {
      return 3;
    }
    if (row.sourceCode == SVG_LENGTHTYPE_PX &&
        SVGLength::GetAbsUnitsPerAbsUnit(row.targetCode, SVG_LENGTHTYPE_NUMBER) !=
            actual) {
      return 4;
    }
  }
  if (SVGLength::GetAbsUnitsPerAbsUnit(SVG_LENGTHTYPE_NUMBER,
                                      SVG_LENGTHTYPE_NUMBER) != 1.0f) {
    return 5;
  }
  return 0;
}
