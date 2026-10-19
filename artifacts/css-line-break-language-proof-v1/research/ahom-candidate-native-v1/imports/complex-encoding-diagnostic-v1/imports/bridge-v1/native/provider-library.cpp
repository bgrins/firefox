#define mozilla language_provider_mozilla
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
#include "provider-trace.h"
#include "breaker-observed.cpp"
extern "C" void language_segment16(const char16_t* text, uint32_t length, uint8_t word, uint8_t line, bool script, uint8_t* output) {
  using namespace mozilla;
  intl::LineBreaker::ComputeBreakPositions(Span<const char16_t>(text,length),intl::WordBreakRule(word),intl::LineBreakRule(line),script,Span<uint8_t>(output,length));
}
extern "C" void language_segment8(const uint8_t* text, uint32_t length, uint8_t word, uint8_t line, bool script, uint8_t* output) {
  using namespace mozilla;
  intl::LineBreaker::ComputeBreakPositions(Span<const uint8_t>(text,length),intl::WordBreakRule(word),intl::LineBreakRule(line),script,Span<uint8_t>(output,length));
}
extern "C" void language_segment_cache_clear() { mozilla::intl::LineBreakCache::Cache()->Clear(); }
