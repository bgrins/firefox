extern "C" {
void language_segment16(const char16_t*,uint32_t,uint8_t,uint8_t,bool,uint8_t*);
void language_segment8(const uint8_t*,uint32_t,uint8_t,uint8_t,bool,uint8_t*);
void* language_locale_parse(const char*,uint32_t,uint8_t*);
uint8_t language_locale_likely(void*);
const char* language_locale_script(void*,uint32_t*);
void language_locale_destroy(void*);
}
#include "enums.h"
namespace mozilla::intl {
static inline bool NS_IsSpace(char16_t u) {
  return u == 0x0020 || u == 0x0009 || u == 0x000D ||
         (0x2000 <= u && u <= 0x2006) || (0x2008 <= u && u <= 0x200B) ||
         u == 0x1361 || u == 0x1680 || u == 0x205F;
}
struct Result { bool bad; bool isErr() const { return bad; } };
struct ScriptTag {
  std::string s;
  bool Missing() const { return s.empty(); }
  bool EqualTo(const char* text) const { return s==text; }
};
struct Locale {
  void* native=nullptr;
  ScriptTag script;
  Locale()=default;
  Locale(const Locale&)=delete;
  ~Locale() { language_locale_destroy(native); }
  void refresh() { uint32_t n; auto s=language_locale_script(native,&n); script.s.assign(s,n); }
  const ScriptTag& Script() const { return script; }
  Result AddLikelySubtags() { auto e=language_locale_likely(native); if(!e) refresh(); return {e!=0}; }
};
struct LocaleParser {
  static Result TryParse(const std::string& text,Locale& out) {
    assert(!out.native); uint8_t error;
    out.native=language_locale_parse(text.data(),text.size(),&error);
    if(!error) out.refresh();
    return {error!=0};
  }
};
struct LineBreaker {
  static void ComputeBreakPositions(const nsTArray<char16_t>& text,WordBreakRule w,LineBreakRule l,bool cj,nsTArray<uint8_t>& out) {
    ComputeBreakPositions(std::span<const char16_t>(text.Elements(),text.Length()),w,l,cj,std::span<uint8_t>(out.Elements(),out.Length()));
  }
  template<class T> static void ComputeBreakPositions(std::span<const T> text,WordBreakRule w,LineBreakRule l,bool cj,std::span<uint8_t> out) {
    assert(text.size()==out.size());
    if constexpr(std::is_same_v<T,char16_t>) language_segment16(text.data(),text.size(),uint8_t(w),uint8_t(l),cj,out.data());
    else language_segment8(text.data(),text.size(),uint8_t(w),uint8_t(l),cj,out.data());
  }
};
}
