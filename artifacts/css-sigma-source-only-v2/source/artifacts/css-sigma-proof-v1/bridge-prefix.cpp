#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>
#include "mozilla/Utf16.h"
#include "unicode/uchar.h"
#undef MOZ_ASSERT
#define MOZ_ASSERT(x, ...) assert(x)
extern "C" UBool ucase_hasBinaryProperty_78(UChar32, UProperty);
namespace mozilla::intl {
struct String {
  static bool IsCased(char32_t cp) {
    return ucase_hasBinaryProperty_78(cp, UCHAR_CASED);
  }
  static bool IsCaseIgnorable(char32_t cp) {
    return ucase_hasBinaryProperty_78(cp, UCHAR_CASE_IGNORABLE);
  }
};
}
struct nsAString {
  std::u16string units;
  uint32_t Length() const { assert(units.size() <= UINT32_MAX); return units.size(); }
  char16_t CharAt(uint32_t i) const { return units.at(i); }
  const char16_t* BeginReading() const { return units.data(); }
};
struct Style { bool mMaskPassword; };
struct Styles {
  std::vector<Style> values;
  uint32_t Length() const { return values.size(); }
  const Style* operator[](uint32_t i) const { return &values.at(i); }
};
struct nsTransformedTextRun { nsAString mString; Styles mStyles; };
constexpr uint32_t GREEK_CAPITAL_LETTER_SIGMA = 0x03a3;
constexpr uint32_t GREEK_SMALL_LETTER_SIGMA = 0x03c3;
constexpr uint32_t GREEK_SMALL_LETTER_FINAL_SIGMA = 0x03c2;
