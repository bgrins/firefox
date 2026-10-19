#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>

static_assert(std::numeric_limits<int32_t>::digits == 31);
static_assert(sizeof(int) == sizeof(int32_t));

struct SpacingFrame {
  int32_t spacing;
  int32_t GetColSpacing(int32_t col) const {
    (void)col;
    return spacing;
  }
};
