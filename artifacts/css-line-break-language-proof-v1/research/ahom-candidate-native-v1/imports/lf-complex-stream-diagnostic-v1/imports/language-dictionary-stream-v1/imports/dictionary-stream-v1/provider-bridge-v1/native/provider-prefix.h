#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <span>
#include <string>
#include <type_traits>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(...) assert(false)
#define MOZ_ALWAYS_INLINE inline
#define MOZ_NO_SANITIZE_UNSIGNED_OVERFLOW
#define MFBT_API
#define NS_DECL_ISUPPORTS
#define NS_DECL_NSIOBSERVER
struct nsIObserver {};
extern "C" {
void u_getVersion(uint8_t*);
int32_t uscript_getScript(int32_t, int32_t*);
int8_t u_charType(int32_t);
int32_t u_tolower(int32_t);
}
struct nsString : std::u16string {
  using std::u16string::u16string;
  bool IsEmpty() const { return empty(); }
  bool Equals(const nsString& rhs) const { return *this == rhs; }
};
using nsDependentSubstring = nsString;
template<class T> struct nsTArray : std::vector<T> {
  using std::vector<T>::vector;
  nsTArray(const T* p, size_t n) : std::vector<T>(p, p+n) {}
};
#include "script-codes.h"
namespace mozilla {
template<class T> class Span : public std::span<T> {
 public:
  using std::span<T>::span;
  size_t Length() const { return this->size(); }
  T* Elements() const { return this->data(); }
};
template<class T> using Maybe = std::optional<T>;
template<class T> struct StaticAutoPtr : std::unique_ptr<T> {
  using std::unique_ptr<T>::unique_ptr;
  operator T*() const { return this->get(); }
  StaticAutoPtr& operator=(T* p) { this->reset(p); return *this; }
};
template<class T> struct CheckedInt {
  uint64_t raw;
  template<class U> CheckedInt(U x) : raw(x) {}
  bool isValid() const { return raw <= uint64_t(std::numeric_limits<T>::max()); }
  T value() const { assert(isValid()); return T(raw); }
};
template<class T> constexpr T WrappingMultiply(T a,T b) { return T(a*b); }
template<class T> constexpr T WrappingAdd(T a,T b) { return T(a+b); }
template<class T> constexpr T RotateLeft(T a, uint8_t n) { return std::rotl(a,n); }
constexpr uint32_t CeilingLog2(size_t n) { return std::bit_width(n-1); }
constexpr uint32_t byteswap(uint32_t n) { return __builtin_bswap32(n); }
namespace intl {
class UnicodeProperties {
 public:
  static inline Script GetScriptCode(uint32_t aCh) {
    int32_t err = 0;
    return Script(uscript_getScript(aCh, &err));
  }
  static bool IsScriptioContinua(char16_t aChar) {
    Script sc = GetScriptCode(aChar);
    return sc == Script::THAI || sc == Script::MYANMAR || sc == Script::KHMER ||
           sc == Script::JAVANESE || sc == Script::BALINESE ||
           sc == Script::SUNDANESE || sc == Script::LAO;
  }
};
}
}
