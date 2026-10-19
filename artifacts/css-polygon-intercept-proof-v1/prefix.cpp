#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>

#define MOZ_ASSERT(condition, ...) assert(condition)
static_assert(std::numeric_limits<int32_t>::digits == 31);
static_assert(std::numeric_limits<int64_t>::digits == 63);
