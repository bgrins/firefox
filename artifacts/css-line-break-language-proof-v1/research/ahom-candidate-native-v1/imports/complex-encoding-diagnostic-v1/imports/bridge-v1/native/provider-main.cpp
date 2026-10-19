#include "provider-prefix.h"
#include "icu4x/diplomat_runtime.hpp"
#include "icu4x/LineBreakIteratorLatin1.hpp"
#include "icu4x/LineBreakIteratorUtf16.hpp"
#include "icu4x/LineSegmenter.hpp"
#include "icu4x/Locale.hpp"
#include "hash.h"
#include "mru.h"
#include "enums.h"
#include "cache.h"
#include "breaker.h"
mozilla::StaticAutoPtr<mozilla::intl::LineBreakCache> mozilla::intl::LineBreakCache::sBreakCache;
#include "breaker.cpp"
int main() {
  using namespace mozilla::intl;
  unsigned width, word, line, script, count;
  while (std::cin >> width >> word >> line >> script >> count) {
    std::vector<char16_t> wide(count);
    std::vector<uint8_t> narrow(count), output(count);
    for (unsigned i=0,x; i<count; ++i) {
      std::cin >> x;
      assert(x <= 65535 && (width == 16 || x <= 255));
      wide[i]=x; narrow[i]=x;
    }
    assert(count && count <= INT32_MAX && word <= 2 && line <= 4 && script <= 1);
    if (width == 16) LineBreaker::ComputeBreakPositions(mozilla::Span<const char16_t>(wide.data(),count),WordBreakRule(word),LineBreakRule(line),script,mozilla::Span<uint8_t>(output.data(),count));
    else { assert(width == 8); LineBreaker::ComputeBreakPositions(mozilla::Span<const uint8_t>(narrow.data(),count),WordBreakRule(word),LineBreakRule(line),script,mozilla::Span<uint8_t>(output.data(),count)); }
    for (auto b:output) std::cout << unsigned(b);
    std::cout << '\n';
  }
  LineBreaker::Shutdown();
}
