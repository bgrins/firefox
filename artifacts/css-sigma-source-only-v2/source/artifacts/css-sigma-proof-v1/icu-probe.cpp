#include <cstdint>
#include <cstdio>
#include "unicode/uchar.h"
extern "C" UBool ucase_hasBinaryProperty_78(UChar32, UProperty);
int main() {
  for (int32_t cp = 0; cp <= 0x10ffff; ++cp) {
    uint8_t p = bool(ucase_hasBinaryProperty_78(cp, UCHAR_CASED)) |
      (bool(ucase_hasBinaryProperty_78(cp, UCHAR_CASE_IGNORABLE)) << 1);
    if (std::fwrite(&p, 1, 1, stdout) != 1) return 2;
  }
}
