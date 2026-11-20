/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef mozilla_Abs_h
#define mozilla_Abs_h

#include <cmath>
#include <type_traits>

namespace mozilla {

namespace detail {

template <typename T, typename = void>
struct AbsReturnType;

template <typename T>
struct AbsReturnType<
    T, std::enable_if_t<std::is_integral_v<T> && std::is_signed_v<T>>> {
  using Type = std::make_unsigned_t<T>;
};

template <typename T>
struct AbsReturnType<T, std::enable_if_t<std::is_floating_point_v<T>>> {
  using Type = T;
};

}  // namespace detail

template <typename T>
inline constexpr typename detail::AbsReturnType<T>::Type Abs(const T aValue) {
  using ReturnType = typename detail::AbsReturnType<T>::Type;
  return aValue >= 0 ? ReturnType(aValue) : ~ReturnType(aValue) + 1;
}

template <>
inline float Abs<float>(const float aFloat) {
  return std::fabs(aFloat);
}

template <>
inline double Abs<double>(const double aDouble) {
  return std::fabs(aDouble);
}

template <>
inline long double Abs<long double>(const long double aLongDouble) {
  return std::fabs(aLongDouble);
}

}  // namespace mozilla

#endif  // mozilla_Abs_h
