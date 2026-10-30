import hashlib, json, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
source = (HERE / "candidate.cpp").read_text()
def body(start):
    first = source.index(start)
    opening = source.index("{", first)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[first:end]
helper = body("static mozilla::Maybe<bool> IsChineseOrJapanese")
updater = body("void nsLineBreaker::UpdateCurrentWordLanguage")
stubs = r"""
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
"""
tests = r"""
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
"""
program = stubs + helper + "\n" + updater + tests
(HERE / "STATE-EXTRACT.cpp").write_text(program)
mutants = {
 "failed-parse-becomes-false": program.replace("return mozilla::Nothing();", "return mozilla::Some(false);", 1),
 "failed-parse-retains-script": program.replace("if (script.isNothing()) {\n      mScriptIsChineseOrJapanese = false;", "if (script.isNothing()) {", 1),
 "null-inherits-cjk": program.replace("return mozilla::Some(false);", "return mozilla::Some(true);", 1),
 "success-cache-no-key": program.replace("sLastLanguage = aLanguage;", "sLastLanguage = nullptr;", 1),
}
records = []
with tempfile.TemporaryDirectory(prefix="language-state-") as tmp:
 root = Path(tmp)
 for name, code in [("actual-extracted", program)] + list(mutants.items()):
   file = root / (name + ".cpp"); exe = root / name; file.write_text(code)
   command = ["/usr/bin/clang++", "-std=c++17", str(file), "-o", str(exe)]
   subprocess.run(command, capture_output=True, check=True)
   run = subprocess.run([str(exe)], capture_output=True, text=True)
   assert (run.returncode == 0) == (name == "actual-extracted"), (name, run.stderr)
   records.append(dict(name=name, exit_code=run.returncode, stderr=run.stderr))
assert not root.exists()
result = dict(candidate_sha256=hashlib.sha256(source.encode()).hexdigest(), exact_helper_and_updater=True, stubbed_locale_and_maybe_not_native_typecheck=True, tests=records, scratch_absent=True)
(HERE / "STATE-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
