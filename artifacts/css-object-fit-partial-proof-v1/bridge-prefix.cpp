#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>

#define MOZ_ASSERT(condition) assert(condition)
#define MOZ_ASSERT_UNREACHABLE(message) assert(false && message)
#define MOZ_LIKELY(condition) (condition)
using nscoord = int32_t;
template<class T> using Maybe = std::optional<T>;
struct nsSize {
  nscoord width = 0, height = 0;
  nsSize() = default;
  nsSize(nscoord w, nscoord h) : width(w), height(h) {}
};
struct IntrinsicSize { Maybe<nscoord> width, height; };
enum class StyleObjectFit { Fill, Contain, Cover, None, ScaleDown };
static int ratioCalls = 0;
struct AspectRatio {
  bool present;
  int numerator, denominator;
  explicit operator bool() const { return present; }
  nscoord ApplyTo(nscoord value) const {
    assert(present && numerator > 0 && denominator > 0);
    ++ratioCalls;
    return nscoord(int64_t(value) * numerator / denominator);
  }
  float ApplyToFloat(nscoord value) const {
    assert(present && numerator > 0 && denominator > 0);
    ++ratioCalls;
    return float(value) * float(numerator) / float(denominator);
  }
  AspectRatio Inverted() const {
    assert(present);
    return {present, denominator, numerator};
  }
};
static int AppUnitsPerCSSPixel() { return 60; }
struct nsImageRenderer {
  enum FitType { CONTAIN, COVER };
  static nsSize ComputeConstrainedSize(const nsSize&, const AspectRatio&, FitType);
};
