#define DEBUG 1
#define mozilla language_locale_mozilla
#include "locale-prefix.h"
#include "locale-glue.h"
#include "gecko-locale.h"
#include "locale.cpp"
#include "locale-generated.cpp"
extern "C" void language_trace(const char*);
extern "C" void* language_locale_parse(const char* text, uint32_t length, uint8_t* error) {
  auto result=std::make_unique<mozilla::intl::Locale>();
  auto parsed=mozilla::intl::LocaleParser::TryParse(mozilla::Span<const char>(text,length),*result);
  language_trace((std::string("locale parse ")+std::string(text,length)+(parsed.isErr()?" error":" ok")).c_str());
  *error=parsed.isErr()?uint8_t(parsed.unwrapErr())+1:0;
  return parsed.isErr()?nullptr:result.release();
}
extern "C" uint8_t language_locale_likely(void* locale) {
  auto result=static_cast<mozilla::intl::Locale*>(locale)->AddLikelySubtags();
  language_trace(result.isErr()?"locale likely error":"locale likely ok");
  return result.isErr()?uint8_t(result.unwrapErr())+1:0;
}
extern "C" const char* language_locale_script(void* locale, uint32_t* length) {
  auto script=static_cast<mozilla::intl::Locale*>(locale)->Script().Span();
  *length=script.size(); return script.data();
}
extern "C" void language_locale_destroy(void* locale) { delete static_cast<mozilla::intl::Locale*>(locale); }
