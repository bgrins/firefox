#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <memory>
#include <span>
#include <sstream>
#include <string>
#include <vector>
#include <variant>
#include <type_traits>
using nsresult = int;
constexpr int NS_OK=0, NS_ERROR_OUT_OF_MEMORY=1;
#define NS_FAILED(x) ((x)!=0)
#define NS_SUCCEEDED(x) ((x)==0)
#define NS_ASSERTION(x,m) assert(x)
#define MOZ_ASSERT(x,...) assert(x)
#define NS_WARNING(x) ((void)0)
#define MOZ_ASSERT_UNREACHABLE(x) assert(false)
static int gFailAt=-1, gAllocations=0;
static bool allocationFails(){return gFailAt>=0 && gAllocations++==gFailAt;}
namespace mozilla {
struct Fallible{}; inline constexpr Fallible fallible{};
template<class T> using Span=std::span<T>;
template<class T> class AutoRestore { T& ref;T old;public:explicit AutoRestore(T& x):ref(x),old(x){} ~AutoRestore(){ref=old;} };
template<class F> struct ScopeExit{F f;~ScopeExit(){f();}};
template<class F> auto MakeScopeExit(F f){return ScopeExit<F>{f};}
inline bool IsHighSurrogate(uint32_t c){return c>=0xd800&&c<=0xdbff;}
inline bool IsLowSurrogate(uint32_t c){return c>=0xdc00&&c<=0xdfff;}
inline bool IsSurrogatePair(uint32_t a,uint32_t b){return IsHighSurrogate(a)&&IsLowSurrogate(b);}
inline uint32_t SurrogateToUCS4(uint32_t a,uint32_t b){return 0x10000+((a-0xd800)<<10)+(b-0xdc00);}
inline bool IsInBMP(uint32_t c){return c<=0xffff;}
}
template<class T> class nsTArray {
  T* p=nullptr;size_t n=0,cap=0;
  bool grow(size_t size,bool fallible){
    if(fallible&&allocationFails())return false;
    if(size>cap){size_t c=std::max(size,cap*2+8);auto q=static_cast<T*>(::operator new(sizeof(T)*c));for(size_t i=0;i<n;i++){new(q+i)T(std::move(p[i]));p[i].~T();}::operator delete(p);p=q;cap=c;}return true;
  }
 public:
  nsTArray(){grow(8,false);}
  nsTArray(nsTArray&& other)noexcept:p(std::exchange(other.p,nullptr)),n(std::exchange(other.n,0)),cap(std::exchange(other.cap,0)){}
  nsTArray&operator=(nsTArray&&other)noexcept{if(this!=&other){Clear();::operator delete(p);p=std::exchange(other.p,nullptr);n=std::exchange(other.n,0);cap=std::exchange(other.cap,0);}return *this;}
  ~nsTArray(){Clear();::operator delete(p);}
  size_t Length()const{return n;}bool IsEmpty()const{return !n;}
  T* Elements(){return p;}const T* Elements()const{return p;}
  T* data(){return p;}const T* data()const{return p;}
  size_t size()const{return n;}
  T* begin(){return p;}T* end(){return p+n;}
  const T* begin()const{return p;}const T* end()const{return p+n;}
  T& operator[](size_t i){assert(i<n);return p[i];}const T& operator[](size_t i)const{assert(i<n);return p[i];}
  void Clear(){while(n)p[--n].~T();}
  T* AppendElements(size_t count,mozilla::Fallible){if(!grow(n+count,true))return nullptr;T* r=p+n;for(size_t i=0;i<count;i++)new(p+n++)T{};return r;}
  T* AppendElement(T x){grow(n+1,false);new(p+n)T(std::move(x));return p+n++;}
  bool SetLength(size_t count,mozilla::Fallible){if(!grow(count,true))return false;while(n>count)p[--n].~T();while(n<count)new(p+n++)T{};return true;}
  void SetLength(size_t count){grow(count,false);while(n>count)p[--n].~T();while(n<count)new(p+n++)T{};}
  T PopLastElement(){assert(n);T value=std::move(p[--n]);p[n].~T();return value;}
  operator std::span<const T>()const{return {p,n};}
  operator std::span<T>(){return {p,n};}
};
template<class T,size_t N> using AutoTArray=nsTArray<T>;
template<class T> class RefPtr{T* p=nullptr;public:RefPtr()=default;RefPtr(T* x):p(x){}operator T*()const{return p;}T* operator->()const{return p;}T* get()const{return p;}RefPtr& operator=(T*x){p=x;return *this;}};
#include <functional>
#include <thread>
extern "C" void language_trace(const char*);
template<class T> class already_AddRefed {
  T* p;
 public:
  explicit already_AddRefed(T* value):p(value){}
  T* take() { auto old=p;p=nullptr;return old; }
};
namespace mozilla {
template<class T> struct RefPtrTraits {
  static void AddRef(T* p) { p->AddRef(); }
  static void Release(T* p) { p->Release(); }
};
}
#define MOZ_ONLY_USED_TO_AVOID_STATIC_CONSTRUCTORS
#define MOZ_OWNING_REF
#include "static-ref-native.h"
static const auto mainThread=std::this_thread::get_id();
static std::vector<std::function<void()>> shutdownActions;
namespace mozilla {
template<class T> void ClearOnShutdown(T* pointer) {
  assert(std::this_thread::get_id()==mainThread);
  shutdownActions.emplace_back([pointer]{*pointer=nullptr;});
  language_trace("shutdown register");
}
}
struct nsAtom {
  std::string value;mutable std::u16string utf16;size_t GetLength()const{return value.size();}const char16_t*GetUTF16String()const{utf16.assign(value.begin(),value.end());return utf16.data();}
  unsigned refs=1;
  void AddRef() { ++refs; language_trace(("atom addref "+value+" "+std::to_string(refs)).c_str()); }
  void Release() { assert(refs>1); --refs; language_trace(("atom release "+value+" "+std::to_string(refs)).c_str()); }
};

inline std::string nsAtomCString(nsAtom* p){return p->value;}
struct nsAtomString{nsAtom*atom;explicit nsAtomString(nsAtom*p):atom(p){}bool Equals(nsAtomString b)const{return atom->value==b.atom->value;}};
struct nsAString{
  std::u16string s;nsAString()=default;nsAString(const char16_t*a,const char16_t*b):s(a,b){}
  size_t Length()const{return s.size();}const char16_t* BeginReading()const{return s.data();}const char16_t* get()const{return s.data();}char16_t operator[](size_t i)const{return s.at(i);}
};
using nsAutoString=nsAString;using nsDependentSubstring=nsAString;
struct nsDependentCSubstring{const char*a,*b;nsDependentCSubstring(const char*x,const char*y):a(x),b(y){}};
inline void CopyASCIItoUTF16(nsDependentCSubstring a,nsAutoString& out){for(auto p=a.a;p<a.b;p++)out.s.push_back(uint8_t(*p));}
struct nsAutoCString{std::string s;void Append(uint32_t c){s.push_back(char(c));}size_t Length()const{return s.size();}const char* BeginReading()const{return s.data();}uint8_t operator[](size_t i)const{return uint8_t(s.at(i));}};
extern "C" int8_t u_charType(int32_t);
extern "C" int32_t u_tolower(int32_t);
extern "C" int32_t uloc_addLikelySubtags(const char*,char*,int32_t,int32_t*);
extern "C" int32_t uloc_getScript(const char*,char*,int32_t,int32_t*);

#include "transform-unicode.hpp"
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
#include "range-types-adapted.hpp"
extern "C" int32_t mapped_hyph_find_hyphen_values_raw(const uint8_t*,uint32_t,const char*,uint32_t,uint8_t*,uint32_t);
extern "C" int32_t mapped_hyph_find_hyphen_values_dic(const void*,const char*,uint32_t,uint8_t*,uint32_t);
extern "C" bool mapped_hyph_is_valid_hyphenator(const uint8_t*,uint32_t);
struct HyphDic{};
template<class T>using UniquePtr=std::unique_ptr<T>;
template<class T,class...Args>auto MakeUnique(Args&&...args){return std::make_unique<T>(std::forward<Args>(args)...);}
namespace ipc{struct ReadOnlySharedMemoryHandle{};struct ReadOnlySharedMemoryMapping{template<class T>const T*DataAs(){return nullptr;}size_t Size(){return 0;}};}
struct Dictionary{
 std::vector<uint8_t> bytes;
 template<class A,class B,class C,class D>int match(A a,B,C,D){std::span<const uint8_t> s(bytes);return a(s);}
};
class nsHyphenator{
 public:Dictionary mDict;bool mHyphenateCapitalized=false;
 nsresult Hyphenate(const nsAString&,nsTArray<bool>&);
 void HyphenateWord(const nsAString&,uint32_t,uint32_t,nsTArray<bool>&);
};
static nsHyphenator gHyphenator;
class nsHyphenationManager{
 public:static nsHyphenationManager*Instance(){static nsHyphenationManager m;return &m;}
 nsHyphenator*GetHyphenator(nsAtom*a){return a&&(a->value=="en"||a->value=="en-US")?&gHyphenator:nullptr;}
};

using mozilla::Span;using mozilla::fallible;

#define HAS_CAPTURED_LIMITS 0

/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

#ifndef NSLINEBREAKER_H_
#define NSLINEBREAKER_H_


class nsAtom;
class nsHyphenator;

/**
 * A receiver of line break data.
 */
class nsILineBreakSink {
 public:
  /**
   * Sets the break data for a substring of the associated text chunk.
   * One or more of these calls will be performed; the union of all substrings
   * will cover the entire text chunk. Substrings may overlap (i.e., we may
   * set the break-before state of a character more than once).
   * @param aBreakBefore the break-before states for the characters in the
   * substring. These are enum values from gfxTextRun::CompressedGlyph:
   *    FLAG_BREAK_TYPE_NONE     - no linebreak is allowed here
   *    FLAG_BREAK_TYPE_NORMAL   - a normal (whitespace) linebreak
   *    FLAG_BREAK_TYPE_HYPHEN   - a hyphenation point
   */
  virtual void SetBreaks(uint32_t aStart, uint32_t aLength,
                         uint8_t* aBreakBefore) = 0;

  /**
   * Indicates which characters should be capitalized. Only called if
   * BREAK_NEED_CAPITALIZATION was requested.
   */
  virtual void SetCapitalization(uint32_t aStart, uint32_t aLength,
                                 bool* aCapitalize) = 0;
};

/**
 * A line-breaking state machine. You feed text into it via AppendText calls
 * and it computes the possible line breaks. Because break decisions can
 * require a lot of context, the breaks for a piece of text are sometimes not
 * known until later text has been seen (or all text ends). So breaks are
 * returned via a call to SetBreaks on the nsILineBreakSink object passed
 * with each text chunk, which might happen during the corresponding AppendText
 * call, or might happen during a later AppendText call or even a Reset()
 * call.
 *
 * The linebreak results MUST NOT depend on how the text is broken up
 * into AppendText calls.
 *
 * The current strategy is that we break the overall text into
 * whitespace-delimited "words". Then those words are passed to the LineBreaker
 * for deeper analysis if they might contain breakable characters.
 *
 * This class also handles detection of which characters should be capitalized
 * for text-transform:capitalize. This is a good place to handle that because
 * we have all the context we need.
 */
class nsLineBreaker {
 public:
  nsLineBreaker() = default;
  ~nsLineBreaker();

  static inline bool IsSpace(char16_t u) {
    return mozilla::intl::NS_IsSpace(u);
  }

  // Helper also used by nsCaseTransformTextRunFactory::TransformString.
  // aChar is the current character to be examined;
  // aCapitalizeNext is a state variable: initialize it to true at start-of-
  // text, then pass it back to this function as each successive character is
  // considered.
  static bool ShouldCapitalize(uint32_t aChar, bool& aCapitalizeNext);

  // Break opportunities exist at the end of each run of breakable whitespace
  // (see IsSpace above). Break opportunities can also exist between pairs of
  // non-whitespace characters, as determined by mozilla::intl::LineBreaker.
  // We pass a whitespace-
  // delimited word to LineBreaker if it contains at least one character
  // that has breakable line breaking classes.
  // We provide flags to control on a per-chunk basis where breaks are allowed.
  // At any character boundary, exactly one text chunk governs whether a
  // break is allowed at that boundary.
  //
  // We operate on text after whitespace processing has been applied, so
  // other characters (e.g. tabs and newlines) may have been converted to
  // spaces.

  /**
   * Flags passed with each chunk of text.
   */
  enum {
    /*
     * Do not introduce a break opportunity at the start of this chunk of text.
     */
    BREAK_SUPPRESS_INITIAL = 0x01,
    /**
     * Do not introduce a break opportunity in the interior of this chunk of
     * text. Also, whitespace in this chunk is treated as non-breakable.
     */
    BREAK_SUPPRESS_INSIDE = 0x02,
    /**
     * The sink currently is already set up to have no breaks in it;
     * if no breaks are possible, nsLineBreaker does not need to call
     * SetBreaks on it. This is useful when handling large quantities of
     * preformatted text; the textruns will never have any breaks set on them,
     * and there is no need to ever actually scan the text for breaks, except
     * at the end of textruns in case context is needed for following breakable
     * text.
     */
    BREAK_SKIP_SETTING_NO_BREAKS = 0x04,
    /**
     * We need to be notified of characters that should be capitalized
     * (as in text-transform:capitalize) in this chunk of text.
     */
    BREAK_NEED_CAPITALIZATION = 0x08,
    /**
     * Auto-hyphenation is enabled, so we need to get a hyphenator
     * (if available) and use it to find breakpoints.
     */
    BREAK_USE_AUTO_HYPHENATION = 0x10
  };

  /**
   * Append "invisible whitespace". This acts like whitespace, but there is
   * no actual text associated with it. Only the BREAK_SUPPRESS_INSIDE flag
   * is relevant here.
   */
  nsresult AppendInvisibleWhitespace(uint32_t aFlags);

  /**
   * Feed Unicode text into the linebreaker for analysis. aLength must be
   * nonzero.
   * @param aSink can be null if the breaks are not actually needed (we may
   * still be setting up state for later breaks)
   */
  nsresult AppendText(nsAtom* aHyphenationLanguage, const char16_t* aText,
                      uint32_t aLength, uint32_t aFlags,
                      nsILineBreakSink* aSink);
  /**
   * Feed 8-bit text into the linebreaker for analysis. aLength must be nonzero.
   * @param aSink can be null if the breaks are not actually needed (we may
   * still be setting up state for later breaks)
   */
  nsresult AppendText(nsAtom* aHyphenationLanguage, const uint8_t* aText,
                      uint32_t aLength, uint32_t aFlags,
                      nsILineBreakSink* aSink);
  /**
   * Reset all state. This means the current run has ended; any outstanding
   * calls through nsILineBreakSink are made, and all outstanding references to
   * nsILineBreakSink objects are dropped.
   * After this call, this linebreaker can be reused.
   * This must be called at least once between any call to AppendText() and
   * destroying the object.
   * @param aTrailingBreak this is set to true when there is a break opportunity
   * at the end of the text. This will normally only be declared true when there
   * is breakable whitespace at the end.
   */
  nsresult Reset(bool* aTrailingBreak);

  /*
   * Set word-break mode for line breaker. This is set by word-break property.
   */
  void SetWordBreak(mozilla::intl::WordBreakRule aMode) {
    // If current word is non-empty and mode is changing, flush the breaker.
    if (aMode != mWordBreak && !mCurrentWord.IsEmpty()) {
      nsresult rv = FlushCurrentWord();
      if (NS_FAILED(rv)) {
        NS_WARNING("FlushCurrentWord failed, line-breaks may be wrong");
      }
      // If previous mode was break-all, we should allow a break here.
      // XXX (jfkthame) css-text spec seems unclear on this, raised question in
      // https://github.com/w3c/csswg-drafts/issues/3897
      if (mWordBreak == mozilla::intl::WordBreakRule::BreakAll) {
        mBreakHere = true;
      }
    }
    mWordBreak = aMode;
  }

  /*
   * Set line-break rule strictness mode for line breaker. This is set by the
   * line-break property.
   */
  void SetStrictness(mozilla::intl::LineBreakRule aMode) {
    if (aMode != mLineBreak && !mCurrentWord.IsEmpty()) {
      nsresult rv = FlushCurrentWord();
      if (NS_FAILED(rv)) {
        NS_WARNING("FlushCurrentWord failed, line-breaks may be wrong");
      }
      // If previous mode was anywhere, we should allow a break here.
      if (mLineBreak == mozilla::intl::LineBreakRule::Anywhere) {
        mBreakHere = true;
      }
    }
    mLineBreak = aMode;
  }

  /**
   * Return whether the line-breaker has a buffered "current word" that may
   * be extended with additional word-forming characters.
   */
  bool InWord() const { return !mCurrentWord.IsEmpty(); }

  /**
   * Set the word-continuation state, which will suppress capitalization of
   * the next letter that might otherwise apply.
   */
  void SetWordContinuation(bool aContinuation) {
    mWordContinuation = aContinuation;
  }

  /**
   * Set the hyphenate-limit-chars values. Values are clamped to be <= 255.
   */
  void SetHyphenateLimitChars(uint32_t aWordLength, uint32_t aStartLength,
                              uint32_t aEndLength) {
    mHyphenateLimitWord = std::min(255u, aWordLength);
    mHyphenateLimitStart = std::min(255u, aStartLength);
    mHyphenateLimitEnd = std::min(255u, aEndLength);
  }

 public:
  // This is a list of text sources that make up the "current word" (i.e.,
  // run of text which does not contain any whitespace). All the mLengths
  // are are nonzero, these cannot overlap.
  struct TextItem {
    TextItem(nsILineBreakSink* aSink, uint32_t aSinkOffset, uint32_t aLength,
             uint32_t aFlags)
        : mSink(aSink),
          mSinkOffset(aSinkOffset),
          mLength(aLength),
          mFlags(aFlags) {}

    nsILineBreakSink* mSink;
    uint32_t mSinkOffset;
    uint32_t mLength;
    uint32_t mFlags;
  };

  // State for the nonwhitespace "word" that started in previous text and hasn't
  // finished yet.

  // When the current word ends, this computes the linebreak opportunities
  // *inside* the word (excluding either end) and sets them through the
  // appropriate sink(s). Then we clear the current word state.
  nsresult FlushCurrentWord();

  void UpdateCurrentWordLanguage(nsAtom* aHyphenationLanguage);

  void FindHyphenationPoints(nsHyphenator* aHyphenator,
                             const char16_t* aTextStart,
                             const char16_t* aTextLimit, uint8_t* aBreakState);

  inline constexpr bool IsSegmentSpace(char16_t u) const {
    return u == 0x0020 ||  // SPACE u
           u == 0x0009 ||  // CHARACTER TABULATION
           u == 0x000D;    // CARRIAGE RETURN
  }

  AutoTArray<char16_t, 100> mCurrentWord;
  // All the items that contribute to mCurrentWord
  AutoTArray<TextItem, 2> mTextItems;
  nsAtom* mCurrentWordLanguage = nullptr;

  // Constraints from CSS `hyphenate-limit-chars` property, to block the use of
  // auto-hyphenation if the word is too short, or at positions too near the
  // beginning/end of the word.
  // (Note that per CSS Text spec, these counts ignore combining marks, etc.,
  // so they are not purely codepoint or character counts.)
  // (Zero values would have no effect; but text-frame code will update the
  // values from CSS before calling the line-breaker.)
  uint8_t mHyphenateLimitWord = 0;   // Min word length to auto-hyphenate
  uint8_t mHyphenateLimitStart = 0;  // Min number of chars before the break
  uint8_t mHyphenateLimitEnd = 0;    // Min number of chars after the break

  bool mCurrentWordContainsMixedLang = false;
  bool mCurrentWordMightBeBreakable = false;
  bool mScriptIsChineseOrJapanese = false;

  // True if the previous character was breakable whitespace
  bool mAfterBreakableSpace = false;
  // True if a break must be allowed at the current position because
  // a run of breakable whitespace ends here
  bool mBreakHere = false;
  // Break rules for letters from the "word-break" property.
  mozilla::intl::WordBreakRule mWordBreak =
      mozilla::intl::WordBreakRule::Normal;
  // Line breaking strictness from the "line-break" property.
  mozilla::intl::LineBreakRule mLineBreak = mozilla::intl::LineBreakRule::Auto;
  // Should the text be treated as continuing a word-in-progress (for purposes
  // of initial capitalization)? Normally this is set to false whenever we
  // start using a linebreaker, but it may be set to true if the line-breaker
  // has been explicitly flushed mid-word.
  bool mWordContinuation = false;
};

#endif /*NSLINEBREAKER_H_*/

class BreakSink final : public nsILineBreakSink {
   public:
    BreakSink(gfxTextRun* aTextRun, DrawTarget* aDrawTarget,
              uint32_t aOffsetIntoTextRun)
        : mTextRun(aTextRun),
          mDrawTarget(aDrawTarget),
          mOffsetIntoTextRun(aOffsetIntoTextRun) {}

    void SetBreaks(uint32_t aOffset, uint32_t aLength,
                   uint8_t* aBreakBefore) final {
      gfxTextRun::Range range(aOffset + mOffsetIntoTextRun,
                              aOffset + mOffsetIntoTextRun + aLength);
      if (mTextRun->SetPotentialLineBreaks(range, aBreakBefore)) {
        // Be conservative and assume that some breaks have been set
        mTextRun->ClearFlagBits(nsTextFrameUtils::Flags::NoBreaks);
      }
    }

    void SetCapitalization(uint32_t aOffset, uint32_t aLength,
                           bool* aCapitalize) final {
      MOZ_ASSERT(mTextRun->GetFlags2() & nsTextFrameUtils::Flags::IsTransformed,
                 "Text run should be transformed!");
      if (mTextRun->GetFlags2() & nsTextFrameUtils::Flags::IsTransformed) {
        nsTransformedTextRun* transformedTextRun =
            static_cast<nsTransformedTextRun*>(mTextRun.get());
        transformedTextRun->SetCapitalization(aOffset + mOffsetIntoTextRun,
                                              aLength, aCapitalize);
      }
    }

    void Finish(gfxMissingFontRecorder* aMFR) {
      if (mTextRun->GetFlags2() & nsTextFrameUtils::Flags::IsTransformed) {
        nsTransformedTextRun* transformedTextRun =
            static_cast<nsTransformedTextRun*>(mTextRun.get());
        transformedTextRun->FinishSettingProperties(mDrawTarget, aMFR);
      }
    }

    RefPtr<gfxTextRun> mTextRun;
    DrawTarget* mDrawTarget;
    uint32_t mOffsetIntoTextRun;
  };
nsresult nsHyphenator::Hyphenate(const nsAString& aString,
                                 nsTArray<bool>& aHyphens) {
  if (!aHyphens.SetLength(aString.Length(), fallible)) {
    return NS_ERROR_OUT_OF_MEMORY;
  }
  memset(aHyphens.Elements(), false, aHyphens.Length() * sizeof(bool));

  bool inWord = false;
  uint32_t wordStart = 0, wordLimit = 0;
  uint32_t chLen;
  for (uint32_t i = 0; i < aString.Length(); i += chLen) {
    uint32_t ch = aString[i];
    chLen = 1;

    if (mozilla::IsHighSurrogate(ch)) {
      if (i + 1 < aString.Length() && mozilla::IsLowSurrogate(aString[i + 1])) {
        ch = mozilla::SurrogateToUCS4(ch, aString[i + 1]);
        chLen = 2;
      } else {
        NS_WARNING("unpaired surrogate found during hyphenation");
      }
    }

    nsUGenCategory cat = unicode::GetGenCategory(ch);
    if (cat == nsUGenCategory::kLetter || cat == nsUGenCategory::kMark) {
      if (!inWord) {
        inWord = true;
        wordStart = i;
      }
      wordLimit = i + chLen;
      if (i + chLen < aString.Length()) {
        continue;
      }
    }

    if (inWord) {
      HyphenateWord(aString, wordStart, wordLimit, aHyphens);
      inWord = false;
    }
  }

  return NS_OK;
}
void nsHyphenator::HyphenateWord(const nsAString& aString, uint32_t aStart,
                                 uint32_t aLimit, nsTArray<bool>& aHyphens) {
  // Convert word from aStart and aLimit in aString to utf-8 for mapped_hyph,
  // lowercasing it as we go so that it will match the (lowercased) patterns
  // (bug 1105644).
  nsAutoCString utf8;
  const char16_t* cur = aString.BeginReading() + aStart;
  const char16_t* end = aString.BeginReading() + aLimit;
  bool firstLetter = true;
  while (cur < end) {
    uint32_t ch = *cur++;

    if (mozilla::IsHighSurrogate(ch)) {
      if (cur < end && mozilla::IsLowSurrogate(*cur)) {
        ch = mozilla::SurrogateToUCS4(ch, *cur++);
      } else {
        return;  // unpaired surrogate: bail out, don't hyphenate broken text
      }
    } else if (mozilla::IsLowSurrogate(ch)) {
      return;  // unpaired surrogate
    }

    // XXX What about language-specific casing? Consider Turkish I/i...
    // In practice, it looks like the current patterns will not be
    // affected by this, as they treat dotted and undotted i similarly.
    uint32_t origCh = ch;
    ch = ToLowerCase(ch);

    if (ch != origCh) {
      // Avoid hyphenating capitalized words (bug 1550532) unless explicitly
      // allowed by prefs for the language in use.
      // Also never auto-hyphenate a word that has internal caps, as it may
      // well be an all-caps acronym or a quirky name like iTunes.
      if (!mHyphenateCapitalized || !firstLetter) {
        return;
      }
    }
    firstLetter = false;

    if (ch < 0x80) {  // U+0000 - U+007F
      utf8.Append(ch);
    } else if (ch < 0x0800) {  // U+0100 - U+07FF
      utf8.Append(0xC0 | (ch >> 6));
      utf8.Append(0x80 | (0x003F & ch));
    } else if (ch < 0x10000) {  // U+0800 - U+D7FF,U+E000 - U+FFFF
      utf8.Append(0xE0 | (ch >> 12));
      utf8.Append(0x80 | (0x003F & (ch >> 6)));
      utf8.Append(0x80 | (0x003F & ch));
    } else {
      utf8.Append(0xF0 | (ch >> 18));
      utf8.Append(0x80 | (0x003F & (ch >> 12)));
      utf8.Append(0x80 | (0x003F & (ch >> 6)));
      utf8.Append(0x80 | (0x003F & ch));
    }
  }

  AutoTArray<uint8_t, 200> hyphenValues;
  hyphenValues.SetLength(utf8.Length());
  int32_t result = mDict.match(
      [&](Span<const uint8_t>& span) {
        return mapped_hyph_find_hyphen_values_raw(
            span.data(), span.size(), utf8.BeginReading(), utf8.Length(),
            hyphenValues.Elements(), hyphenValues.Length());
      },
      [&](ipc::ReadOnlySharedMemoryHandle& shm) {
        // Only the parent process can have a handle stored. We should never
        // get to this point with just a handle.
        MOZ_ASSERT_UNREACHABLE("Unexpected HyphenateWord with only a handle");
        return 0;
      },
      [&](ipc::ReadOnlySharedMemoryMapping& shm) {
        return mapped_hyph_find_hyphen_values_raw(
            shm.DataAs<uint8_t>(), shm.Size(), utf8.BeginReading(),
            utf8.Length(), hyphenValues.Elements(), hyphenValues.Length());
      },
      [&](UniquePtr<const HyphDic>& hyph) {
        return mapped_hyph_find_hyphen_values_dic(
            hyph.get(), utf8.BeginReading(), utf8.Length(),
            hyphenValues.Elements(), hyphenValues.Length());
      });
  if (result > 0) {
    // We need to convert UTF-8 indexing as used by the hyphenation lib into
    // UTF-16 indexing of the aHyphens[] array for Gecko.
    uint32_t utf16index = 0;
    for (uint32_t utf8index = 0; utf8index < utf8.Length();) {
      // We know utf8 is valid, so we only need to look at the first byte of
      // each character to determine its length and the corresponding UTF-16
      // length to add to utf16index.
      const uint8_t leadByte = utf8[utf8index];
      if (leadByte < 0x80) {
        utf8index += 1;
      } else if (leadByte < 0xE0) {
        utf8index += 2;
      } else if (leadByte < 0xF0) {
        utf8index += 3;
      } else {
        utf8index += 4;
      }
      // The hyphenation value of interest is the one for the last code unit
      // of the utf-8 character, and is recorded on the last code unit of the
      // utf-16 character (in the case of a surrogate pair).
      utf16index += leadByte >= 0xF0 ? 2 : 1;
      if (utf16index > 0 && (hyphenValues[utf8index - 1] & 0x01)) {
        aHyphens[aStart + utf16index - 1] = true;
      }
    }
  }
}
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */



using mozilla::AutoRestore;
using mozilla::Span;
using mozilla::intl::LineBreaker;
using mozilla::intl::LineBreakRule;
using mozilla::intl::Locale;
using mozilla::intl::LocaleParser;
using mozilla::intl::UnicodeProperties;
using mozilla::intl::WordBreakRule;

// There is no break opportunity between any pair of characters that has line
// break class of either AI (Ambiguous), AL (Alphabetic), IS (Infix Numeric
// Separator), NU (Numeric), or QU (Quotation). This is based on UAX #14,
// Unicode Version 15.1.0. See
// https://www.unicode.org/Public/15.1.0/ucd/LineBreak.txt for Unicode code
// point and line break class mapping. If upgrading ICU4X, we have to match
// with Unicode version.
//
// TODO(m_kato):
// We should generate this table by a script (Bug 2081587).
static constexpr uint8_t kNonBreakableLatin1[] = {
    // clang-format off
// 0x20-0x2f
0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0,
// 0x30-0x3f
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
// 0x40-0x4f
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
// 0x50-0x5f
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1,
// 0x60-0x6f
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
// 0x70-0x7f
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0,
// 0x80-0x8f
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
// 0x90-0x9f
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
// 0xa0-0xaf
0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1,
// 0xb0-0xbf
0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
// 0xc0-0xcf
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
// 0xd0-0xdf
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
// 0xe0-0xef
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
// 0xf0-0xff
1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    // clang-format on
};

template <typename T>
static constexpr bool IsNonBreakableChar(T aChar) {
  if (aChar < 0x20 || aChar > 0xff) {
    return false;
  }
  return !!kNonBreakableLatin1[aChar - 0x20];
}

nsLineBreaker::~nsLineBreaker() {
  NS_ASSERTION(mCurrentWord.Length() == 0,
               "Should have Reset() before destruction!");
}

/* static */
bool nsLineBreaker::ShouldCapitalize(uint32_t aChar, bool& aCapitalizeNext) {
  using mozilla::intl::GeneralCategory;
  auto category = UnicodeProperties::CharType(aChar);
  switch (category) {
    case GeneralCategory::Uppercase_Letter:
    case GeneralCategory::Lowercase_Letter:
    case GeneralCategory::Titlecase_Letter:
    case GeneralCategory::Modifier_Letter:
    case GeneralCategory::Other_Letter:
    case GeneralCategory::Decimal_Number:
    case GeneralCategory::Letter_Number:
    case GeneralCategory::Other_Number:
      if (aCapitalizeNext) {
        aCapitalizeNext = false;
        return true;
      }
      break;
    case GeneralCategory::Space_Separator:
    case GeneralCategory::Line_Separator:
    case GeneralCategory::Paragraph_Separator:
    case GeneralCategory::Dash_Punctuation:
    case GeneralCategory::Initial_Punctuation:
      /* These punctuation categories are excluded, for examples like
       *   "what colo[u]r" -> "What Colo[u]r?" (rather than "What Colo[U]R?")
       * and
       *   "snake_case" -> "Snake_case" (to match word selection behavior)
      case GeneralCategory::Open_Punctuation:
      case GeneralCategory::Close_Punctuation:
      case GeneralCategory::Connector_Punctuation:
       */
      aCapitalizeNext = true;
      break;
    case GeneralCategory::Final_Punctuation:
      /* Special-case: exclude Unicode single-close-quote/apostrophe,
         for examples like "Lowe’s" etc. */
      if (aChar != 0x2019) {
        aCapitalizeNext = true;
      }
      break;
    case GeneralCategory::Other_Punctuation:
      /* Special-case: exclude ASCII apostrophe, for "Lowe's" etc.,
         and MIDDLE DOT, for Catalan "l·l". */
      if (aChar != '\'' && aChar != 0x00B7) {
        aCapitalizeNext = true;
      }
      break;
    default:
      break;
  }
  return false;
}

static void SetupCapitalization(const char16_t* aWord, uint32_t aLength,
                                bool* aCapitalization) {
  // Capitalize the first alphanumeric character after a space or punctuation.
  bool capitalizeNextChar = true;
  for (uint32_t i = 0; i < aLength; ++i) {
    uint32_t ch = aWord[i];
    if (i + 1 < aLength && mozilla::IsSurrogatePair(ch, aWord[i + 1])) {
      ch = mozilla::SurrogateToUCS4(ch, aWord[i + 1]);
    }
    aCapitalization[i] =
        nsLineBreaker::ShouldCapitalize(ch, capitalizeNextChar);

    if (!mozilla::IsInBMP(ch)) {
      ++i;
    }
  }
}

nsresult nsLineBreaker::FlushCurrentWord() {
  auto cleanup = mozilla::MakeScopeExit([&] {
    mCurrentWord.Clear();
    mTextItems.Clear();
    mCurrentWordMightBeBreakable = false;
    mCurrentWordContainsMixedLang = false;
    mCurrentWordLanguage = nullptr;
    mWordContinuation = false;
  });

  uint32_t length = mCurrentWord.Length();
  AutoTArray<uint8_t, 4000> breakState;
  if (!breakState.AppendElements(length, mozilla::fallible)) {
    return NS_ERROR_OUT_OF_MEMORY;
  }

  if (mLineBreak == LineBreakRule::Anywhere) {
    memset(breakState.Elements(),
           gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NORMAL,
           length * sizeof(uint8_t));
  } else if (!mCurrentWordMightBeBreakable &&
             mWordBreak != WordBreakRule::BreakAll) {
    // word-break: normal or keep-all has no break opportunity if the word
    // is non-breakable. (See the comment of kNonBreakableASCII).
    memset(breakState.Elements(),
           gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NONE,
           length * sizeof(uint8_t));
  } else {
    LineBreaker::ComputeBreakPositions(mCurrentWord, mWordBreak, mLineBreak,
                                       mScriptIsChineseOrJapanese, breakState);
  }

  bool autoHyphenate = mCurrentWordLanguage && !mCurrentWordContainsMixedLang;
  uint32_t i;
  for (i = 0; autoHyphenate && i < mTextItems.Length(); ++i) {
    TextItem* ti = &mTextItems[i];
    if (!(ti->mFlags & BREAK_USE_AUTO_HYPHENATION)) {
      autoHyphenate = false;
    }
  }
  if (autoHyphenate) {
    RefPtr<nsHyphenator> hyphenator =
        nsHyphenationManager::Instance()->GetHyphenator(mCurrentWordLanguage);
    if (hyphenator) {
      FindHyphenationPoints(hyphenator, mCurrentWord.Elements(),
                            mCurrentWord.Elements() + length,
                            breakState.Elements());
    }
  }

  nsTArray<bool> capitalizationState;
  uint32_t offset = 0;
  for (i = 0; i < mTextItems.Length(); ++i) {
    TextItem* ti = &mTextItems[i];
    NS_ASSERTION(ti->mLength > 0, "Zero length word contribution?");

    if ((ti->mFlags & BREAK_SUPPRESS_INITIAL) && ti->mSinkOffset == 0) {
      breakState[offset] = gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NONE;
    }
    if (ti->mFlags & BREAK_SUPPRESS_INSIDE) {
      uint32_t exclude = ti->mSinkOffset == 0 ? 1 : 0;
      memset(breakState.Elements() + offset + exclude,
             gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NONE,
             (ti->mLength - exclude) * sizeof(uint8_t));
    }

    // Don't set the break state for the first character of the word, because
    // it was already set correctly earlier and we don't know what the true
    // value should be.
    uint32_t skipSet = i == 0 ? 1 : 0;
    if (ti->mSink) {
      ti->mSink->SetBreaks(ti->mSinkOffset + skipSet, ti->mLength - skipSet,
                           breakState.Elements() + offset + skipSet);

      if (!mWordContinuation && (ti->mFlags & BREAK_NEED_CAPITALIZATION)) {
        if (capitalizationState.Length() == 0) {
          if (!capitalizationState.AppendElements(length, mozilla::fallible)) {
            return NS_ERROR_OUT_OF_MEMORY;
          }
          memset(capitalizationState.Elements(), false, length * sizeof(bool));
          SetupCapitalization(mCurrentWord.Elements(), length,
                              capitalizationState.Elements());
        }
        ti->mSink->SetCapitalization(ti->mSinkOffset, ti->mLength,
                                     capitalizationState.Elements() + offset);
      }
    }

    offset += ti->mLength;
  }

  return NS_OK;
}

// If the aFlags parameter to AppendText has all these bits set,
// then we don't need to worry about finding break opportunities
// in the appended text.
#define NO_BREAKS_NEEDED_FLAGS                      \
  (BREAK_SUPPRESS_INITIAL | BREAK_SUPPRESS_INSIDE | \
   BREAK_SKIP_SETTING_NO_BREAKS)

nsresult nsLineBreaker::AppendText(nsAtom* aHyphenationLanguage,
                                   const char16_t* aText, uint32_t aLength,
                                   uint32_t aFlags, nsILineBreakSink* aSink) {
 {std::ostringstream event;event<<"caller append 16 "<<aFlags<<" "<<(aSink?1:0)<<" "<<aLength;for(uint32_t i=0;i<aLength;++i)event<<" "<<unsigned(aText[i]);language_trace(event.str().c_str());}

  NS_ASSERTION(aLength > 0, "Appending empty text...");

  uint32_t offset = 0;

  // Continue the current word
  if (mCurrentWord.Length() > 0) {
    NS_ASSERTION(!mAfterBreakableSpace && !mBreakHere,
                 "These should not be set");

    while (offset < aLength && !IsSegmentSpace(aText[offset])) {
      mCurrentWord.AppendElement(aText[offset]);
      if (!mCurrentWordMightBeBreakable &&
          !IsNonBreakableChar<char16_t>(aText[offset])) {
        mCurrentWordMightBeBreakable = true;
      }
      UpdateCurrentWordLanguage(aHyphenationLanguage);
      ++offset;
    }

    if (offset > 0) {
      mTextItems.AppendElement(TextItem(aSink, 0, offset, aFlags));
    }

    if (offset == aLength) {
      return NS_OK;
    }

    // We encountered whitespace, so we're done with this word
    nsresult rv = FlushCurrentWord();
    if (NS_FAILED(rv)) {
      return rv;
    }
  }

  AutoTArray<uint8_t, 4000> breakState;
  if (aSink) {
    if (!breakState.AppendElements(aLength, mozilla::fallible)) {
      return NS_ERROR_OUT_OF_MEMORY;
    }
  }

  bool noCapitalizationNeeded = true;
  nsTArray<bool> capitalizationState;
  if (aSink && (aFlags & BREAK_NEED_CAPITALIZATION)) {
    if (!capitalizationState.AppendElements(aLength, mozilla::fallible)) {
      return NS_ERROR_OUT_OF_MEMORY;
    }
    memset(capitalizationState.Elements(), false, aLength * sizeof(bool));
    noCapitalizationNeeded = false;
  }

  uint32_t start = offset;
  bool noBreaksNeeded =
      !aSink || ((aFlags & NO_BREAKS_NEEDED_FLAGS) == NO_BREAKS_NEEDED_FLAGS &&
                 !mBreakHere && !mAfterBreakableSpace);
  if (noBreaksNeeded && noCapitalizationNeeded) {
    // Skip to the space before the last word, since either the break data
    // here is not needed, or no breaks are set in the sink and there cannot
    // be any breaks in this chunk; and we don't need to do word-initial
    // capitalization. All we need is the context for the next chunk (if any).
    offset = aLength;
    while (offset > start) {
      --offset;
      if (IsSegmentSpace(aText[offset])) {
        break;
      }
    }
  }
  uint32_t wordStart = offset;
  bool wordMightBeBreakable = false;

  RefPtr<nsHyphenator> hyphenator;
  if ((aFlags & BREAK_USE_AUTO_HYPHENATION) &&
      !(aFlags & BREAK_SUPPRESS_INSIDE) && aHyphenationLanguage) {
    hyphenator =
        nsHyphenationManager::Instance()->GetHyphenator(aHyphenationLanguage);
  }

  for (;;) {
    char16_t ch = aText[offset];
    bool isSpace = IsSegmentSpace(ch);
    bool isBreakableSpace = isSpace && !(aFlags & BREAK_SUPPRESS_INSIDE);

    if (aSink && !noBreaksNeeded) {
      breakState[offset] =
          mBreakHere || (mAfterBreakableSpace && !isBreakableSpace) ||
                  mWordBreak == WordBreakRule::BreakAll ||
                  mLineBreak == LineBreakRule::Anywhere
              ? gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NORMAL
              : gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NONE;
    }
    mBreakHere = false;
    mAfterBreakableSpace = isBreakableSpace;

    if (isSpace || ch == '\n') {
      if (offset > wordStart && aSink) {
        if (!(aFlags & BREAK_SUPPRESS_INSIDE)) {
          if (mLineBreak == LineBreakRule::Anywhere) {
            memset(breakState.Elements() + wordStart,
                   gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NORMAL,
                   offset - wordStart);
          } else if (wordMightBeBreakable) {
            // Save current start-of-word state because ComputeBreakPositions()
            // will set it to false.
            AutoRestore<uint8_t> saveWordStartBreakState(breakState[wordStart]);
            LineBreaker::ComputeBreakPositions(
                Span<const char16_t>(aText + wordStart, offset - wordStart),
                mWordBreak, mLineBreak, mScriptIsChineseOrJapanese,
                Span<uint8_t>(breakState.Elements() + wordStart,
                              offset - wordStart));
          }
          if (hyphenator) {
            FindHyphenationPoints(hyphenator, aText + wordStart, aText + offset,
                                  breakState.Elements() + wordStart);
          }
        }
        if (!mWordContinuation && !noCapitalizationNeeded) {
          SetupCapitalization(aText + wordStart, offset - wordStart,
                              capitalizationState.Elements() + wordStart);
        }
      }
      wordMightBeBreakable = false;
      mWordContinuation = false;
      ++offset;
      if (offset >= aLength) {
        break;
      }
      wordStart = offset;
      continue;
    }

    if (!wordMightBeBreakable && !IsNonBreakableChar<char16_t>(ch)) {
      wordMightBeBreakable = true;
    }
    ++offset;
    if (offset >= aLength) {
      // Save this word
      mCurrentWordMightBeBreakable = wordMightBeBreakable;
      uint32_t len = offset - wordStart;
      char16_t* elems = mCurrentWord.AppendElements(len, mozilla::fallible);
      if (!elems) {
        return NS_ERROR_OUT_OF_MEMORY;
      }
      memcpy(elems, aText + wordStart, sizeof(char16_t) * len);
      mTextItems.AppendElement(TextItem(aSink, wordStart, len, aFlags));
      // Ensure that the break-before for this word is written out
      offset = wordStart + 1;
      UpdateCurrentWordLanguage(aHyphenationLanguage);
      break;
    }
  }

  if (aSink) {
    if (!noBreaksNeeded) {
      aSink->SetBreaks(start, offset - start, breakState.Elements() + start);
    }
    if (!noCapitalizationNeeded) {
      aSink->SetCapitalization(start, offset - start,
                               capitalizationState.Elements() + start);
    }
  }
  return NS_OK;
}

void nsLineBreaker::FindHyphenationPoints(nsHyphenator* aHyphenator,
                                          const char16_t* aTextStart,
                                          const char16_t* aTextLimit,
                                          uint8_t* aBreakState) {
  // Early-return for words that are definitely too short to hyphenate.
  if (aTextLimit - aTextStart < mHyphenateLimitWord) {
    return;
  }

  nsDependentSubstring string(aTextStart, aTextLimit);
  AutoTArray<bool, 200> hyphens;
  if (NS_FAILED(aHyphenator->Hyphenate(string, hyphens))) {
    return;
  }

  // Keep track of the length seen so far, in terms of characters that are
  // countable for hyphenate-limit-chars purposes.
  uint32_t length = 0;
  // When setting a potential break in aBreakState, we record the previous
  // value in case we need to restore it because the position turns out to
  // be too close to the end of the word.
  struct BreakInfo {
    uint32_t mPosition;
    uint32_t mLength;
    uint8_t mState;
  };
  AutoTArray<BreakInfo, 16> oldBreaks;
  // Don't consider setting any breaks where i >= endLimit, as they will
  // definitely be too near the end of the word to be accepted.
  uint32_t endLimit =
      string.Length() - std::max<uint32_t>(1u, mHyphenateLimitEnd);
  for (uint32_t i = 0; i < string.Length(); ++i) {
    // Get current character, converting surrogate pairs to UCS4 for char
    // category lookup.
    uint32_t ch = string[i];
    if (mozilla::IsHighSurrogate(ch) && i + 1 < string.Length() &&
        mozilla::IsLowSurrogate(string[i + 1])) {
      ch = mozilla::SurrogateToUCS4(ch, string[i + 1]);
    }

    // According to CSS Text, "Nonspacing combining marks (Unicode General
    // Category Mn) and intra-word punctuation (Unicode General Category P*)
    // do not count towards the minimum."
    // (https://drafts.csswg.org/css-text-4/#hyphenate-char-limits)
    // We also don't count Control or Format categories.
    using mozilla::intl::GeneralCategory;
    switch (UnicodeProperties::CharType(ch)) {
      case GeneralCategory::Nonspacing_Mark:
      case GeneralCategory::Dash_Punctuation:
      case GeneralCategory::Open_Punctuation:
      case GeneralCategory::Close_Punctuation:
      case GeneralCategory::Connector_Punctuation:
      case GeneralCategory::Other_Punctuation:
      case GeneralCategory::Initial_Punctuation:
      case GeneralCategory::Final_Punctuation:
      case GeneralCategory::Control:
      case GeneralCategory::Format:
      case GeneralCategory::Surrogate:
        break;
      default:
        ++length;
        break;
    }

    // Don't accept any breaks until we're far enough into the word, or if
    // we're too near the end for it to possibly be accepted. (Note that the
    // check against endLimit is just an initial worst-case check that assumes
    // all the remaining characters are countable; if there are combining
    // marks, etc., in the trailing part of the word we may need to reset the
    // potential break later, after we've fully counted length.)
    if (hyphens[i] && length >= mHyphenateLimitStart && i < endLimit) {
      // Keep track of hyphen position and "countable" length of the word.
      oldBreaks.AppendElement(BreakInfo{i + 1, length, aBreakState[i + 1]});
      aBreakState[i + 1] = gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_HYPHEN;
    }

    // If the character was outside the BMP, skip past the low surrogate.
    if (!mozilla::IsInBMP(ch)) {
      ++i;
    }
  }

  if (length < mHyphenateLimitWord) {
    // After discounting combining marks, punctuation, controls, etc., the word
    // was too short for hyphenate-limit-chars. If we've set any hyphen breaks,
    // forget them.
    while (!oldBreaks.IsEmpty()) {
      auto lastBreak = oldBreaks.PopLastElement();
      aBreakState[lastBreak.mPosition] = lastBreak.mState;
    }
  } else {
    // Check if trailing fragment is too short; if so, remove the last hyphen
    // break(s) that we set, until the fragment will be long enough.
    while (!oldBreaks.IsEmpty()) {
      auto lastBreak = oldBreaks.PopLastElement();
      if (length - lastBreak.mLength >= mHyphenateLimitEnd) {
        break;
      }
      aBreakState[lastBreak.mPosition] = lastBreak.mState;
    }
  }
}

nsresult nsLineBreaker::AppendText(nsAtom* aHyphenationLanguage,
                                   const uint8_t* aText, uint32_t aLength,
                                   uint32_t aFlags, nsILineBreakSink* aSink) {
 {std::ostringstream event;event<<"caller append 8 "<<aFlags<<" "<<(aSink?1:0)<<" "<<aLength;for(uint32_t i=0;i<aLength;++i)event<<" "<<unsigned(aText[i]);language_trace(event.str().c_str());}

  NS_ASSERTION(aLength > 0, "Appending empty text...");

  if (aFlags & (BREAK_NEED_CAPITALIZATION | BREAK_USE_AUTO_HYPHENATION)) {
    // Defer to the Unicode path if capitalization or hyphenation is required
    nsAutoString str;
    const char* cp = reinterpret_cast<const char*>(aText);
    CopyASCIItoUTF16(nsDependentCSubstring(cp, cp + aLength), str);
    return AppendText(aHyphenationLanguage, str.get(), aLength, aFlags, aSink);
  }

  uint32_t offset = 0;

  // Continue the current word
  if (mCurrentWord.Length() > 0) {
    NS_ASSERTION(!mAfterBreakableSpace && !mBreakHere,
                 "These should not be set");

    while (offset < aLength && !IsSegmentSpace(aText[offset])) {
      mCurrentWord.AppendElement(aText[offset]);
      if (!mCurrentWordMightBeBreakable &&
          !IsNonBreakableChar<uint8_t>(aText[offset])) {
        mCurrentWordMightBeBreakable = true;
      }
      ++offset;
    }

    if (offset > 0) {
      mTextItems.AppendElement(TextItem(aSink, 0, offset, aFlags));
    }

    if (offset == aLength) {
      // We did not encounter whitespace so the word hasn't finished yet.
      return NS_OK;
    }

    // We encountered whitespace, so we're done with this word
    nsresult rv = FlushCurrentWord();
    if (NS_FAILED(rv)) {
      return rv;
    }
  }

  AutoTArray<uint8_t, 4000> breakState;
  if (aSink) {
    if (!breakState.AppendElements(aLength, mozilla::fallible)) {
      return NS_ERROR_OUT_OF_MEMORY;
    }
  }

  uint32_t start = offset;
  bool noBreaksNeeded =
      !aSink || ((aFlags & NO_BREAKS_NEEDED_FLAGS) == NO_BREAKS_NEEDED_FLAGS &&
                 !mBreakHere && !mAfterBreakableSpace);
  if (noBreaksNeeded) {
    // Skip to the space before the last word, since either the break data
    // here is not needed, or no breaks are set in the sink and there cannot
    // be any breaks in this chunk; all we need is the context for the next
    // chunk (if any)
    offset = aLength;
    while (offset > start) {
      --offset;
      if (IsSegmentSpace(aText[offset])) {
        break;
      }
    }
  }
  uint32_t wordStart = offset;
  bool wordMightBeBreakable = false;

  for (;;) {
    uint8_t ch = aText[offset];
    bool isSpace = IsSegmentSpace(ch);
    bool isBreakableSpace = isSpace && !(aFlags & BREAK_SUPPRESS_INSIDE);

    if (aSink) {
      // Consider word-break style.  Since the break position of CJK scripts
      // will be set by nsILineBreaker, we don't consider CJK at this point.
      breakState[offset] =
          mBreakHere || (mAfterBreakableSpace && !isBreakableSpace) ||
                  mWordBreak == WordBreakRule::BreakAll ||
                  mLineBreak == LineBreakRule::Anywhere
              ? gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NORMAL
              : gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NONE;
    }
    mBreakHere = false;
    mAfterBreakableSpace = isBreakableSpace;

    if (isSpace) {
      if (offset > wordStart && aSink && !(aFlags & BREAK_SUPPRESS_INSIDE)) {
        if (mLineBreak == LineBreakRule::Anywhere) {
          memset(breakState.Elements() + wordStart,
                 gfxTextRun::CompressedGlyph::FLAG_BREAK_TYPE_NORMAL,
                 offset - wordStart);
        } else if (wordMightBeBreakable) {
          // Save current start-of-word state because ComputeBreakPositions()
          // will set it to false.
          AutoRestore<uint8_t> saveWordStartBreakState(breakState[wordStart]);
          LineBreaker::ComputeBreakPositions(
              Span<const uint8_t>(aText + wordStart, offset - wordStart),
              mWordBreak, mLineBreak, mScriptIsChineseOrJapanese,
              Span<uint8_t>(breakState.Elements() + wordStart,
                            offset - wordStart));
        }
      }

      wordMightBeBreakable = false;
      mWordContinuation = false;
      ++offset;
      if (offset >= aLength) {
        break;
      }
      wordStart = offset;
      continue;
    }

    if (!wordMightBeBreakable && !IsNonBreakableChar<uint8_t>(ch)) {
      wordMightBeBreakable = true;
    }
    ++offset;
    if (offset >= aLength) {
      // Save this word
      mCurrentWordMightBeBreakable = wordMightBeBreakable;
      uint32_t len = offset - wordStart;
      char16_t* elems = mCurrentWord.AppendElements(len, mozilla::fallible);
      if (!elems) {
        return NS_ERROR_OUT_OF_MEMORY;
      }
      uint32_t i;
      for (i = wordStart; i < offset; ++i) {
        elems[i - wordStart] = aText[i];
      }
      mTextItems.AppendElement(TextItem(aSink, wordStart, len, aFlags));
      // Ensure that the break-before for this word is written out
      offset = wordStart + 1;
      break;
    }
  }

  if (!noBreaksNeeded) {
    aSink->SetBreaks(start, offset - start, breakState.Elements() + start);
  }
  return NS_OK;
}

void nsLineBreaker::UpdateCurrentWordLanguage(nsAtom* aHyphenationLanguage) {
  if (mCurrentWordLanguage && mCurrentWordLanguage != aHyphenationLanguage) {
    mCurrentWordContainsMixedLang = true;
    mScriptIsChineseOrJapanese = false;
    return;
  }

  if (aHyphenationLanguage && !mCurrentWordLanguage) {
    static mozilla::StaticRefPtr<nsAtom> sLastHyphenationLanguage;
    static bool sLastScriptIsChineseOrJapanese = false;
    static bool sInit = false;

    if (!sInit) {
      mozilla::ClearOnShutdown(&sLastHyphenationLanguage);
      sInit = true;
    }

    if (sLastHyphenationLanguage == aHyphenationLanguage) {
      MOZ_ASSERT(nsAtomString(sLastHyphenationLanguage)
                     .Equals(nsAtomString(aHyphenationLanguage)));
      mScriptIsChineseOrJapanese = sLastScriptIsChineseOrJapanese;
    } else {
      Locale loc;
      auto result =
          LocaleParser::TryParse(nsAtomCString(aHyphenationLanguage), loc);

      if (result.isErr()) {
        return;
      }
      if (loc.Script().Missing() && loc.AddLikelySubtags().isErr()) {
        return;
      }
      mScriptIsChineseOrJapanese =
          loc.Script().EqualTo("Hans") || loc.Script().EqualTo("Hant") ||
          loc.Script().EqualTo("Jpan") || loc.Script().EqualTo("Hrkt");

      sLastHyphenationLanguage = aHyphenationLanguage;
      sLastScriptIsChineseOrJapanese = mScriptIsChineseOrJapanese;
    }
  }
  mCurrentWordLanguage = aHyphenationLanguage;
}

nsresult nsLineBreaker::AppendInvisibleWhitespace(uint32_t aFlags) {
  nsresult rv = FlushCurrentWord();
  if (NS_FAILED(rv)) {
    return rv;
  }

  bool isBreakableSpace = !(aFlags & BREAK_SUPPRESS_INSIDE);
  if (mAfterBreakableSpace && !isBreakableSpace) {
    mBreakHere = true;
  }
  mAfterBreakableSpace = isBreakableSpace;
  mWordContinuation = false;
  return NS_OK;
}

nsresult nsLineBreaker::Reset(bool* aTrailingBreak) {
  nsresult rv = FlushCurrentWord();
  if (NS_FAILED(rv)) {
    return rv;
  }

  *aTrailingBreak = mBreakHere || mAfterBreakableSpace;
  mBreakHere = false;
  mAfterBreakableSpace = false;
  return NS_OK;
}

class BuildTextRunsScanner { public:
struct MappedFlow {
    nsTextFrame* mStartFrame;
    nsTextFrame* mEndFrame;
    // When we consider breaking between elements, the nearest common
    // ancestor of the elements containing the characters is the one whose
    // CSS 'white-space' property governs. So this records the nearest common
    // ancestor of mStartFrame and the previous text frame, or null if there
    // was no previous text frame on this line.
    nsIFrame* mAncestorControllingInitialBreak;

    int32_t GetContentEnd() const {
      int32_t bufferLen = mStartFrame->CharacterDataBuffer().GetLength();
      return mEndFrame ? std::min(bufferLen, mEndFrame->GetContentOffset())
                       : bufferLen;
    }
  };
AutoTArray<MappedFlow, 10> mMappedFlows;
AutoTArray<nsTextFrame*, 50> mLineBreakBeforeFrames;
AutoTArray<UniquePtr<BreakSink>, 10> mBreakSinks;
nsLineBreaker mLineBreaker;
RefPtr<gfxTextRun> mCurrentFramesAllSameTextRun;
DrawTarget* mDrawTarget=nullptr;
nsIFrame* mLineContainer=nullptr;
nsTextFrame* mLastFrame=nullptr;
nsIFrame* mCommonAncestorWithLastFrame=nullptr;
gfxMissingFontRecorder* mMissingFonts=nullptr;
uint32_t mMaxTextLength=0;
bool mDoubleByteText=false;
bool mStartOfLine=true;
bool mSkipIncompleteTextRuns=false;
nsTextFrame::TextRunType mWhichTextRun=nsTextFrame::TextRunType::Inflated;
void AccumulateRunInfo(nsTextFrame*);
void SetupBreakSinksForTextRun(gfxTextRun*,const void*);
void FlushLineBreaks(gfxTextRun*);

};
void BuildTextRunsScanner::AccumulateRunInfo(nsTextFrame* aFrame) {
  if (mMaxTextLength != UINT32_MAX) {
    NS_ASSERTION(mMaxTextLength < UINT32_MAX - aFrame->GetContentLength(),
                 "integer overflow");
    if (mMaxTextLength >= UINT32_MAX - aFrame->GetContentLength()) {
      mMaxTextLength = UINT32_MAX;
    } else {
      mMaxTextLength += aFrame->GetContentLength();
    }
  }
  mDoubleByteText |= aFrame->CharacterDataBuffer().Is2b();
  mLastFrame = aFrame;
  mCommonAncestorWithLastFrame = aFrame->GetParent();

  MappedFlow* mappedFlow = &mMappedFlows[mMappedFlows.Length() - 1];
  NS_ASSERTION(mappedFlow->mStartFrame == aFrame ||
                   mappedFlow->GetContentEnd() == aFrame->GetContentOffset(),
               "Overlapping or discontiguous frames => BAD");
  mappedFlow->mEndFrame = aFrame->GetNextContinuation();
  if (mCurrentFramesAllSameTextRun != aFrame->GetTextRun(mWhichTextRun)) {
    mCurrentFramesAllSameTextRun = nullptr;
  }

  if (mStartOfLine) {
    mLineBreakBeforeFrames.AppendElement(aFrame);
    mStartOfLine = false;
  }

  // Default limits used by `hyphenate-limit-chars` for `auto` components, as
  // suggested by the CSS Text spec.
  // TODO: consider making these sensitive to the context, e.g. increasing the
  // values for long line lengths to reduce the tendency to hyphenate too much.
  const uint32_t kDefaultHyphenateTotalWordLength = 5;
  const uint32_t kDefaultHyphenatePreBreakLength = 2;
  const uint32_t kDefaultHyphenatePostBreakLength = 2;

  const auto& hyphenateLimitChars = aFrame->StyleText()->mHyphenateLimitChars;
  uint32_t pre =
      hyphenateLimitChars.pre_hyphen_length.IsAuto()
          ? kDefaultHyphenatePreBreakLength
          : std::max(0, hyphenateLimitChars.pre_hyphen_length.AsNumber());
  uint32_t post =
      hyphenateLimitChars.post_hyphen_length.IsAuto()
          ? kDefaultHyphenatePostBreakLength
          : std::max(0, hyphenateLimitChars.post_hyphen_length.AsNumber());
  uint32_t total =
      hyphenateLimitChars.total_word_length.IsAuto()
          ? kDefaultHyphenateTotalWordLength
          : std::max(0, hyphenateLimitChars.total_word_length.AsNumber());
  total = std::max(total, pre + post);
  mLineBreaker.SetHyphenateLimitChars(total, pre, post);
}
static bool HasCompressedLeadingWhitespace(
    nsTextFrame* aFrame, const nsStyleText* aStyleText,
    int32_t aContentEndOffset, const gfxSkipCharsIterator& aIterator) {
  if (!aIterator.IsOriginalCharSkipped()) {
    return false;
  }

  gfxSkipCharsIterator iter = aIterator;
  int32_t frameContentOffset = aFrame->GetContentOffset();
  const CharacterDataBuffer& characterDataBuffer =
      aFrame->CharacterDataBuffer();
  while (frameContentOffset < aContentEndOffset &&
         iter.IsOriginalCharSkipped()) {
    if (IsTrimmableSpace(characterDataBuffer, frameContentOffset, aStyleText)) {
      return true;
    }
    ++frameContentOffset;
    iter.AdvanceOriginal(1);
  }
  return false;
}
void BuildTextRunsScanner::SetupBreakSinksForTextRun(gfxTextRun* aTextRun,
                                                     const void* aTextPtr) {
  using mozilla::intl::LineBreakRule;
  using mozilla::intl::WordBreakRule;

  // textruns have uniform language
  const nsStyleFont* styleFont = mMappedFlows[0].mStartFrame->StyleFont();
  // We should only use a language for hyphenation if it was specified
  // explicitly.
  nsAtom* hyphenationLanguage =
      styleFont->mExplicitLanguage ? styleFont->GetLangAtom() : nullptr;
  // We keep this pointed at the skip-chars data for the current mappedFlow.
  // This lets us cheaply check whether the flow has compressed initial
  // whitespace...
  gfxSkipCharsIterator iter(aTextRun->GetSkipChars());

  for (uint32_t i = 0; i < mMappedFlows.Length(); ++i) {
    MappedFlow* mappedFlow = &mMappedFlows[i];
    // The CSS word-break value may change within a word, so we reset it for
    // each MappedFlow. The line-breaker will flush its text if the property
    // actually changes.
    const auto* styleText = mappedFlow->mStartFrame->StyleText();
    auto wordBreak = styleText->EffectiveWordBreak();
    switch (wordBreak) {
      case StyleWordBreak::BreakAll:
        mLineBreaker.SetWordBreak(WordBreakRule::BreakAll);
        break;
      case StyleWordBreak::KeepAll:
        mLineBreaker.SetWordBreak(WordBreakRule::KeepAll);
        break;
      case StyleWordBreak::Normal:
      default:
        MOZ_ASSERT(wordBreak == StyleWordBreak::Normal);
        mLineBreaker.SetWordBreak(WordBreakRule::Normal);
        break;
    }
    switch (styleText->mLineBreak) {
      case StyleLineBreak::Auto:
        mLineBreaker.SetStrictness(LineBreakRule::Auto);
        break;
      case StyleLineBreak::Normal:
        mLineBreaker.SetStrictness(LineBreakRule::Normal);
        break;
      case StyleLineBreak::Loose:
        mLineBreaker.SetStrictness(LineBreakRule::Loose);
        break;
      case StyleLineBreak::Strict:
        mLineBreaker.SetStrictness(LineBreakRule::Strict);
        break;
      case StyleLineBreak::Anywhere:
        mLineBreaker.SetStrictness(LineBreakRule::Anywhere);
        break;
    }

    uint32_t offset = iter.GetSkippedOffset();
    gfxSkipCharsIterator iterNext = iter;
    iterNext.AdvanceOriginal(mappedFlow->GetContentEnd() -
                             mappedFlow->mStartFrame->GetContentOffset());

    UniquePtr<BreakSink>* breakSink = mBreakSinks.AppendElement(
        MakeUnique<BreakSink>(aTextRun, mDrawTarget, offset));

    uint32_t length = iterNext.GetSkippedOffset() - offset;
    uint32_t flags = 0;
    nsIFrame* initialBreakController =
        mappedFlow->mAncestorControllingInitialBreak;
    if (!initialBreakController) {
      initialBreakController = mLineContainer;
    }
    if (!initialBreakController->StyleText()->WhiteSpaceCanWrap(
            initialBreakController)) {
      flags |= nsLineBreaker::BREAK_SUPPRESS_INITIAL;
    }
    nsTextFrame* startFrame = mappedFlow->mStartFrame;
    const nsStyleText* textStyle = startFrame->StyleText();
    if (!textStyle->WhiteSpaceCanWrap(startFrame)) {
      flags |= nsLineBreaker::BREAK_SUPPRESS_INSIDE;
    }
    if (aTextRun->GetFlags2() & nsTextFrameUtils::Flags::NoBreaks) {
      flags |= nsLineBreaker::BREAK_SKIP_SETTING_NO_BREAKS;
    }
    if (textStyle->mTextTransform & StyleTextTransform::CAPITALIZE) {
      flags |= nsLineBreaker::BREAK_NEED_CAPITALIZATION;
    }
    if (textStyle->mHyphens == StyleHyphens::Auto &&
        textStyle->mLineBreak != StyleLineBreak::Anywhere) {
      flags |= nsLineBreaker::BREAK_USE_AUTO_HYPHENATION;
    }

    if (HasCompressedLeadingWhitespace(startFrame, textStyle,
                                       mappedFlow->GetContentEnd(), iter)) {
      mLineBreaker.AppendInvisibleWhitespace(flags);
    }

    if (length > 0) {
      BreakSink* sink = mSkipIncompleteTextRuns ? nullptr : (*breakSink).get();
      if (mDoubleByteText) {
        const char16_t* text = reinterpret_cast<const char16_t*>(aTextPtr);
        mLineBreaker.AppendText(hyphenationLanguage, text + offset, length,
                                flags, sink);
      } else {
        const uint8_t* text = reinterpret_cast<const uint8_t*>(aTextPtr);
        mLineBreaker.AppendText(hyphenationLanguage, text + offset, length,
                                flags, sink);
      }
    }

    iter = iterNext;
  }
}
void BuildTextRunsScanner::FlushLineBreaks(gfxTextRun* aTrailingTextRun) {
  // If the line-breaker is buffering a potentially-unfinished word,
  // preserve the state of being in-word so that we don't spuriously
  // capitalize the next letter.
  bool inWord = mLineBreaker.InWord();
  bool trailingLineBreak;
  nsresult rv = mLineBreaker.Reset(&trailingLineBreak);
  mLineBreaker.SetWordContinuation(inWord);
  // textRun may be null for various reasons, including because we constructed
  // a partial textrun just to get the linebreaker and other state set up
  // to build the next textrun.
  if (NS_SUCCEEDED(rv) && trailingLineBreak && aTrailingTextRun) {
    aTrailingTextRun->SetFlagBits(nsTextFrameUtils::Flags::HasTrailingBreak);
  }

  for (uint32_t i = 0; i < mBreakSinks.Length(); ++i) {
    // TODO cause frames associated with the textrun to be reflowed, if they
    // aren't being reflowed already!
    mBreakSinks[i]->Finish(mMissingFonts);
  }
  mBreakSinks.Clear();
}
static std::string traceCase;
extern "C" void language_trace(const char* event){std::cout<<traceCase<<" EVENT "<<event<<"\n";}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 std::ifstream dict(argv[1],std::ios::binary);gHyphenator.mDict.bytes.assign(std::istreambuf_iterator<char>(dict),{});
 if(!mapped_hyph_is_valid_hyphenator(gHyphenator.mDict.bytes.data(),gHyphenator.mDict.bytes.size()))return 3;
 nsAtom atoms[]={{"en-US"},{"en"},{"ja"},{"zh"},{"bad_tag"}};std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream in(line);std::string id;unsigned encoding,skip,nflows;int tag;unsigned strictness,word;in>>id>>encoding>>skip>>nflows>>tag>>strictness>>word;nsAtom& language=atoms[tag<0?0:tag];traceCase=id;
  nsIFrame container;BuildTextRunsScanner scanner;scanner.mLineContainer=&container;scanner.mSkipIncompleteTextRuns=skip;scanner.mDoubleByteText=encoding==16;
  nsTransformedTextRun run;std::vector<std::unique_ptr<CharacterDataBuffer>> buffers;std::vector<std::vector<nsTextFrame>> frames;std::vector<std::unique_ptr<nsIFrame>> ancestors;
  std::vector<char16_t> transformed;std::vector<uint8_t> bytes;uint8_t incoming=0;
  for(unsigned flow=0;flow<nflows;flow++){
   unsigned n,nframes,ancestorWrap,accumulate;in>>n>>nframes>>ancestorWrap>>accumulate;
   auto buffer=std::make_unique<CharacterDataBuffer>();buffer->wide=encoding==16;
   for(unsigned i=0;i<n;i++){unsigned unit;in>>unit;buffer->units.push_back(unit);}
   for(unsigned i=0;i<n;i++){unsigned skipped;in>>skipped;if(accumulate<2){if(skipped)run.skip.SkipChar();else run.skip.KeepChar();if(!skipped){transformed.push_back(buffer->units[i]);bytes.push_back(buffer->units[i]);}}}
   if(accumulate>=2){
    nsTextFrameUtils::Flags flags{};auto compression=nsTextFrameUtils::CompressionMode(accumulate-2);
    if(encoding==16){std::vector<char16_t> output(n+1);auto end=nsTextFrameUtils::TransformText(buffer->units.data(),n,output.data(),compression,&incoming,&run.skip,&flags,&language);transformed.insert(transformed.end(),output.data(),end);}
    else{std::vector<uint8_t> input(buffer->units.begin(),buffer->units.end()),output(n+1);auto end=nsTextFrameUtils::TransformText(input.data(),n,output.data(),compression,&incoming,&run.skip,&flags,&language);bytes.insert(bytes.end(),output.data(),end);for(auto p=output.data();p!=end;++p)transformed.push_back(*p);}
   }
   auto ancestor=std::make_unique<nsIFrame>();ancestor->style.wrap=ancestorWrap;ancestor->style.mTextWrapMode=ancestorWrap?StyleTextWrapMode::Wrap:StyleTextWrapMode::NoWrap;
   frames.emplace_back(nframes);auto& group=frames.back();
   for(unsigned i=0;i<nframes;i++){
    int offset,total,pre,post;unsigned flags;in>>offset>>total>>pre>>post>>flags;
    auto& f=group[i];f.offset=offset;f.buffer=buffer.get();f.font.language=&language;f.font.mExplicitLanguage=tag>=0;f.next=i+1<nframes?&group[i+1]:nullptr;
    f.style.mHyphenateLimitChars={{total},{pre},{post}};f.style.wrap=!(flags&1);f.style.mTextWrapMode=(flags&1)?StyleTextWrapMode::NoWrap:StyleTextWrapMode::Wrap;f.style.mTextTransform=(flags&2)?1:0;f.style.mHyphens=(flags&4)?StyleHyphens::None:(flags&8)?StyleHyphens::Manual:StyleHyphens::Auto;
    StyleLineBreak lines[]={StyleLineBreak::Auto,StyleLineBreak::Loose,StyleLineBreak::Normal,StyleLineBreak::Strict,StyleLineBreak::Anywhere};f.style.mLineBreak=lines[strictness];StyleWordBreak words[]={StyleWordBreak::Normal,StyleWordBreak::BreakAll,StyleWordBreak::KeepAll};f.style.mWordBreak=words[word];
    if(accumulate>=2){StyleWhiteSpaceCollapse modes[]={StyleWhiteSpaceCollapse::Preserve,StyleWhiteSpaceCollapse::PreserveBreaks,StyleWhiteSpaceCollapse::Collapse,StyleWhiteSpaceCollapse::PreserveSpaces};f.style.mWhiteSpaceCollapse=modes[accumulate-2];}
   }
   scanner.mMappedFlows.AppendElement({&group[0],nullptr,ancestor.get()});
   if(accumulate)for(auto& frame:group)scanner.AccumulateRunInfo(&frame);
   buffers.push_back(std::move(buffer));ancestors.push_back(std::move(ancestor));
  }
  assert(in);run.SetLength(transformed.size());
  for(size_t i=0;i<transformed.size();i++)if(transformed[i]==32)run.glyphs[i].mValue|=gfxTextRun::CompressedGlyph::FLAG_CHAR_IS_SPACE;
  scanner.SetupBreakSinksForTextRun(&run,encoding==16?static_cast<const void*>(transformed.data()):static_cast<const void*>(bytes.data()));
  std::vector<unsigned> offsets;for(auto&sink:scanner.mBreakSinks)offsets.push_back(sink->mOffsetIntoTextRun);
  scanner.FlushLineBreaks(&run);
  std::cout<<id<<" SINKS";for(auto offset:offsets)std::cout<<' '<<offset;
  std::cout<<" GLYPHS ";for(auto&glyph:run.glyphs)std::cout<<unsigned(glyph.CanBreakBefore());
  std::cout<<" FINISHES "<<run.finishes<<" NEEDS_REBUILD "<<run.needsRebuild<<" MAXLENGTH "<<scanner.mMaxTextLength<<"\n";
 }
 traceCase="shutdown";for(auto& action:shutdownActions)action();for(auto& atom:atoms)assert(atom.refs==1);
}
