
#include <cassert>
#include <optional>
#include <string_view>
struct nsAtom { const char* name; };
static int parses = 0, shutdowns = 0;
namespace mozilla {
template<class T> struct Maybe : std::optional<T> {
  using std::optional<T>::optional;
  bool isNothing() const { return !this->has_value(); }
  T valueOr(T value) const { return this->value_or(value); }
};
template<class T> Maybe<T> Some(T value) { return Maybe<T>(value); }
inline std::nullopt_t Nothing() { return std::nullopt; }
template<class T> using StaticRefPtr = T*;
template<class T> void ClearOnShutdown(T*) { ++shutdowns; }
}
std::string_view nsAtomCString(nsAtom* atom) { return atom->name; }
struct Result { bool failed; bool isErr() const { return failed; } };
struct Locale {
 std::string_view lang;
 struct ScriptValue {
   std::string_view lang;
   bool Missing() const { return lang == "likely-failure"; }
   bool EqualTo(const char* script) const {
     return (lang == "ja" && std::string_view(script) == "Jpan") ||
            (lang == "zh" && std::string_view(script) == "Hans");
   }
 };
 ScriptValue Script() { return {lang}; }
 Result AddLikelySubtags() { return {true}; }
};
struct LocaleParser {
 static Result TryParse(std::string_view lang, Locale& value) {
   ++parses; value.lang = lang; return {lang == "!"};
 }
};
class nsLineBreaker {
 public:
 nsAtom* mCurrentWordLanguage = nullptr;
 bool mCurrentWordContainsMixedLang = false;
 bool mScriptIsChineseOrJapanese = false;
 void UpdateCurrentWordLanguage(nsAtom*);
};
static mozilla::Maybe<bool> IsChineseOrJapanese(nsAtom* aLanguage) {
  if (!aLanguage) {
    return mozilla::Some(false);
  }

  static mozilla::StaticRefPtr<nsAtom> sLastLanguage;
  static bool sLastScriptIsChineseOrJapanese = false;
  static bool sInit = false;

  if (!sInit) {
    mozilla::ClearOnShutdown(&sLastLanguage);
    sInit = true;
  }

  if (sLastLanguage == aLanguage) {
    return mozilla::Some(sLastScriptIsChineseOrJapanese);
  }

  Locale loc;
  if (LocaleParser::TryParse(nsAtomCString(aLanguage), loc).isErr() ||
      (loc.Script().Missing() && loc.AddLikelySubtags().isErr())) {
    return mozilla::Nothing();
  }

  sLastScriptIsChineseOrJapanese =
      loc.Script().EqualTo("Hans") || loc.Script().EqualTo("Hant") ||
      loc.Script().EqualTo("Jpan") || loc.Script().EqualTo("Hrkt");
  sLastLanguage = aLanguage;
  return mozilla::Some(sLastScriptIsChineseOrJapanese);
}
void nsLineBreaker::UpdateCurrentWordLanguage(nsAtom* aHyphenationLanguage) {
  if (mCurrentWordLanguage && mCurrentWordLanguage != aHyphenationLanguage) {
    mCurrentWordContainsMixedLang = true;
    mScriptIsChineseOrJapanese = false;
    return;
  }

  if (!mCurrentWordLanguage) {
    auto script = IsChineseOrJapanese(aHyphenationLanguage);
    if (script.isNothing()) {
      mScriptIsChineseOrJapanese = false;
      return;
    }
    mScriptIsChineseOrJapanese = *script;
  }
  mCurrentWordLanguage = aHyphenationLanguage;
}
int main() {
 nsAtom ja{"ja"}, zh{"zh"}, en{"en"}, invalid{"!"}, likely{"likely-failure"};
 assert(!IsChineseOrJapanese(nullptr).isNothing());
 assert(!*IsChineseOrJapanese(nullptr));
 assert(*IsChineseOrJapanese(&ja));
 int before = parses;
 assert(IsChineseOrJapanese(&invalid).isNothing());
 assert(*IsChineseOrJapanese(&ja));
 assert(parses == before + 1);
 assert(IsChineseOrJapanese(&likely).isNothing());
 assert(!*IsChineseOrJapanese(&en));
 assert(shutdowns == 1);
 for (nsAtom* lang : {static_cast<nsAtom*>(nullptr), &invalid, &likely}) {
   nsLineBreaker value;
   value.mScriptIsChineseOrJapanese = true;
   value.UpdateCurrentWordLanguage(lang);
   assert(!value.mScriptIsChineseOrJapanese);
   assert(value.mCurrentWordLanguage == nullptr);
   value.UpdateCurrentWordLanguage(&ja);
   assert(value.mCurrentWordLanguage == &ja);
   assert(value.mScriptIsChineseOrJapanese);
   assert(!value.mCurrentWordContainsMixedLang);
 }
 nsLineBreaker value;
 value.UpdateCurrentWordLanguage(&en);
 assert(value.mCurrentWordLanguage == &en && !value.mScriptIsChineseOrJapanese);
 value.UpdateCurrentWordLanguage(&ja);
 assert(value.mCurrentWordLanguage == &en && value.mCurrentWordContainsMixedLang);
 assert(!value.mScriptIsChineseOrJapanese);
}
