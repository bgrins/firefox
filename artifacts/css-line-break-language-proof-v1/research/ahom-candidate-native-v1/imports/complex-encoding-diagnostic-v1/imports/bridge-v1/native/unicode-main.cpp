#include "unicode-native.h"
#include <cassert>
#include <cstdio>
extern "C" void u_getVersion(uint8_t*);
int main() {
  uint8_t version[4]; u_getVersion(version);
  unsigned letters=0, marks=0;
  for (uint32_t ch=0; ch<=0x10ffff; ++ch) {
    unsigned cat=unsigned(mozilla::intl::UnicodeProperties::CharType(ch));
    auto general=mozilla::unicode::GetGenCategory(ch);
    assert(cat<30);
    assert((general==nsUGenCategory::kLetter)==(cat>=1 && cat<=5));
    assert((general==nsUGenCategory::kMark)==(cat>=6 && cat<=8));
    assert(ToLowerCase(ch)==uint32_t(u_tolower(ch)));
    letters+=general==nsUGenCategory::kLetter; marks+=general==nsUGenCategory::kMark;
  }
  printf("icu=%u.%u.%u.%u scalars_and_surrogates=1114112 letters=%u marks=%u\n",version[0],version[1],version[2],version[3],letters,marks);
}
