#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <new>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(...) assert(false)
#define MOZ_UNLIKELY(x) (x)
#define LOG_FONTLIST_ENABLED() false
#define LOG_FONTLIST(...) ((void)0)
#define MOZ_LOG_TEST(...) false
#define MOZ_LOG(...) ((void)0)
#define AUTO_PROFILER_LABEL_DYNAMIC_NSCSTRING(...) ((void)0)
struct nsACString : std::string {
  using std::string::string;
  const char* get() const { return c_str(); }
  void AppendFloat(float) {}
  void Append(const char*) {}
};
using nsCString = nsACString;
using nsAutoCString = nsCString;
using gfxFloat = double;
using LogModule = int;
enum class LogLevel { Debug };
enum class ThreadProfilingFeatures { Sampling, Markers };
int Combine(ThreadProfilingFeatures, ThreadProfilingFeatures) { return 0; }
bool profiler_thread_is_being_profiled(int) { return false; }
template<class... T> nsCString nsPrintfCString(T...) { return {}; }
int Compare(const nsCString& a, const nsCString& b) { return a.compare(b); }
namespace intl { enum class Script { Common }; struct UnicodeProperties {
  static Script GetScriptCode(uint32_t) { return Script::Common; }
}; }
using Script = intl::Script;
std::vector<std::string> events;
void note(const std::string& label, int id) { events.push_back(label + std::to_string(id)); }
template<class T> struct RefPtr {
  T* value = nullptr;
  RefPtr() = default;
  RefPtr(T* p) : value(p) {}
  operator T*() const { return value; }
  T* operator->() const { return value; }
  T& operator*() const { return *value; }
  T* get() const { return value; }
  T* forget() { return std::exchange(value, nullptr); }
  void swap(T*& p) { std::swap(value, p); }
};
template<class T> using already_AddRefed = T*;
template<class T> struct nsTArray : std::vector<T> {
  using std::vector<T>::vector;
  uint32_t Length() const { return this->size(); }
  bool IsEmpty() const { return this->empty(); }
  void AppendElement(T t) { this->push_back(t); }
  void Clear() { this->clear(); }
  void SetLength(size_t n) { this->resize(n); }
  template<class F> void RemoveElementsBy(F f) {
    this->erase(std::remove_if(this->begin(), this->end(), f), this->end());
  }
};
template<class T, size_t N> using AutoTArray = nsTArray<T>;
struct Lock {
  void AssertCurrentThreadIn() const {}
  bool LockedForWritingByCurrentThread() const { return true; }
};
struct AutoReadLock { explicit AutoReadLock(const Lock&) {} };
constexpr uint8_t kItalicMask = 2, kBoldMask = 1;
constexpr uint8_t kRegularFaceIndex = 0, kBoldFaceIndex = 1;
constexpr uint8_t kItalicFaceIndex = 2, kBoldItalicFaceIndex = 3;

std::vector<void*> allocations;


namespace mozilla {
#define SERVO_FIXED_POINT_HELPERS(T, RawT, FractionBits)                      \
  static constexpr RawT kPointFive = 1 << (FractionBits - 1);                 \
  static constexpr uint16_t kScale = 1 << FractionBits;                       \
  static constexpr float kInverseScale = 1.0f / kScale;                       \
  static T FromRaw(RawT aRaw) { return {{aRaw}}; }                            \
  static T FromFloat(float aFloat) { return FromRaw(RawT(aFloat * kScale)); } \
  static T FromInt(RawT aInt) { return FromRaw(RawT(aInt * kScale)); }        \
  RawT Raw() const { return _0.value; }                                       \
  uint16_t UnsignedRaw() const { return uint16_t(Raw()); }                    \
  float ToFloat() const { return Raw() * kInverseScale; }                     \
  RawT ToIntRounded() const { return (Raw() + kPointFive) >> FractionBits; }  \
  inline void ToString(nsACString&) const;

constexpr static const uint16_t StyleFONT_WEIGHT_FRACTION_BITS = 6;

constexpr static const uint16_t StyleFONT_WIDTH_FRACTION_BITS = 6;

constexpr static const uint16_t StyleFONT_STYLE_FRACTION_BITS = 8;

template<typename T, uint16_t FRACTION_BITS>
struct StyleFixedPoint {
  /// The actual representation.
  T value;

  bool operator==(const StyleFixedPoint& other) const {
    return value == other.value;
  }
  bool operator<(const StyleFixedPoint& other) const {
    return value < other.value;
  }
  bool operator<=(const StyleFixedPoint& other) const {
    return value <= other.value;
  }
  bool operator>(const StyleFixedPoint& other) const {
    return value > other.value;
  }
  bool operator>=(const StyleFixedPoint& other) const {
    return value >= other.value;
  }
};

using StyleFontWeightFixedPoint = StyleFixedPoint<uint16_t, StyleFONT_WEIGHT_FRACTION_BITS>;

/// A value for the font-weight property per:
///
/// https://drafts.csswg.org/css-fonts-4/#propdef-font-weight
///
struct StyleFontWeight {
  StyleFontWeightFixedPoint _0;

  bool operator==(const StyleFontWeight& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontWeight& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontWeight& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontWeight& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontWeight& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontWeight, uint16_t, StyleFONT_WEIGHT_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }

 inline bool IsBold() const;
 inline bool PreferBold() const;
  static const StyleFontWeight NORMAL;
  static const StyleFontWeight BOLD;
  static const StyleFontWeight BOLD_THRESHOLD;
  static const StyleFontWeight PREFER_BOLD_THRESHOLD;
};
/// The `normal` keyword.
constexpr inline const StyleFontWeight StyleFontWeight::NORMAL = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (400 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The `bold` value.
constexpr inline const StyleFontWeight StyleFontWeight::BOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (700 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The threshold from which we consider a font bold.
constexpr inline const StyleFontWeight StyleFontWeight::BOLD_THRESHOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (600 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};
/// The threshold above which CSS font matching prefers bolder faces
/// over lighter ones.
constexpr inline const StyleFontWeight StyleFontWeight::PREFER_BOLD_THRESHOLD = StyleFontWeight{
  /* ._0 = */ StyleFontWeightFixedPoint{
    /* .value = */ (500 << StyleFONT_WEIGHT_FRACTION_BITS)
  }
};

/// The computed representation of the above so Gecko and Servo can read them easily.
///
/// This one is needed because cbindgen doesn't know how to generate


using StyleFontWidthFixedPoint = StyleFixedPoint<uint16_t, StyleFONT_WIDTH_FRACTION_BITS>;

/// A value for the font-width property per:
///
/// https://drafts.csswg.org/css-fonts-4/#propdef-font-width
///
/// (Note that this property was formerly named font-stretch.)
///
struct StyleFontWidth {
  StyleFontWidthFixedPoint _0;

  bool operator==(const StyleFontWidth& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontWidth& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontWidth& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontWidth& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontWidth& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontWidth, uint16_t, StyleFONT_WIDTH_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }
  static const uint16_t FRACTION_BITS;
  static const uint16_t HALF;
  static const StyleFontWidth ULTRA_CONDENSED;
  static const StyleFontWidth EXTRA_CONDENSED;
  static const StyleFontWidth CONDENSED;
  static const StyleFontWidth SEMI_CONDENSED;
  static const StyleFontWidth NORMAL;
  static const StyleFontWidth SEMI_EXPANDED;
  static const StyleFontWidth EXPANDED;
  static const StyleFontWidth EXTRA_EXPANDED;
  static const StyleFontWidth ULTRA_EXPANDED;
};
/// The fraction bits, as an easy-to-access-constant.
constexpr inline const uint16_t StyleFontWidth::FRACTION_BITS = StyleFONT_WIDTH_FRACTION_BITS;
/// 0.5 in our floating point representation.
constexpr inline const uint16_t StyleFontWidth::HALF = (1 << (StyleFontWidth::FRACTION_BITS - 1));
/// The `ultra-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::ULTRA_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (50 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `extra-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXTRA_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((62 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (75 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `semi-condensed` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::SEMI_CONDENSED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((87 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `normal` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::NORMAL = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (100 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `semi-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::SEMI_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ ((112 << StyleFontWidth::FRACTION_BITS) + StyleFontWidth::HALF)
  }
};
/// The `expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (125 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `extra-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::EXTRA_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (150 << StyleFontWidth::FRACTION_BITS)
  }
};
/// The `ultra-expanded` keyword.
constexpr inline const StyleFontWidth StyleFontWidth::ULTRA_EXPANDED = StyleFontWidth{
  /* ._0 = */ StyleFontWidthFixedPoint{
    /* .value = */ (200 << StyleFontWidth::FRACTION_BITS)
  }
};

/// The computed representation of the above, so that Gecko and Servo can read them


using StyleFontStyleFixedPoint = StyleFixedPoint<int16_t, StyleFONT_STYLE_FRACTION_BITS>;

/// The computed value of `font-style`.
///
/// - Define angle of zero degrees as `normal`
/// - Define out-of-range value 100 degrees as `italic`
/// - Other values represent `oblique <angle>`
///
struct StyleFontStyle {
  StyleFontStyleFixedPoint _0;

  bool operator==(const StyleFontStyle& other) const {
    return _0 == other._0;
  }
  bool operator<(const StyleFontStyle& other) const {
    return _0 < other._0;
  }
  bool operator<=(const StyleFontStyle& other) const {
    return _0 <= other._0;
  }
  bool operator>(const StyleFontStyle& other) const {
    return _0 > other._0;
  }
  bool operator>=(const StyleFontStyle& other) const {
    return _0 >= other._0;
  }
 SERVO_FIXED_POINT_HELPERS(StyleFontStyle, int16_t, StyleFONT_STYLE_FRACTION_BITS);
 bool IsNormal() const { return *this == NORMAL; }
 inline bool IsItalic() const;
 inline float ObliqueAngle() const;  // Not for use when IsItalic() is true
 inline float SlantAngle() const;  // Returns angle for any font-style, including
                                   // normal/italic as well as explicit oblique
  static const StyleFontStyle NORMAL;
  static const StyleFontStyle ITALIC;
  static const int16_t DEFAULT_OBLIQUE_DEGREES;
  static const StyleFontStyle OBLIQUE;
};
/// The `normal` keyword, equal to `oblique` with angle zero.
constexpr inline const StyleFontStyle StyleFontStyle::NORMAL = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (0 << StyleFONT_STYLE_FRACTION_BITS)
  }
};
/// The italic keyword.
constexpr inline const StyleFontStyle StyleFontStyle::ITALIC = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (100 << StyleFONT_STYLE_FRACTION_BITS)
  }
};
/// The default angle for `font-style: oblique`.
/// See also https://github.com/w3c/csswg-drafts/issues/2295
constexpr inline const int16_t StyleFontStyle::DEFAULT_OBLIQUE_DEGREES = 14;
/// The `oblique` keyword with the default degrees.
constexpr inline const StyleFontStyle StyleFontStyle::OBLIQUE = StyleFontStyle{
  /* ._0 = */ StyleFontStyleFixedPoint{
    /* .value = */ (StyleFontStyle::DEFAULT_OBLIQUE_DEGREES << StyleFONT_STYLE_FRACTION_BITS)
  }
};

/// The computed representation of the above, with angles in degrees stored as


inline bool StyleFontWeight::IsBold() const { return *this >= BOLD_THRESHOLD; }

inline bool StyleFontWeight::PreferBold() const {
  return *this > PREFER_BOLD_THRESHOLD;
}

inline bool StyleFontStyle::IsItalic() const { return *this == ITALIC; }

inline float StyleFontStyle::ObliqueAngle() const {
  MOZ_ASSERT(!IsItalic());
  return ToFloat();
}

inline float StyleFontStyle::SlantAngle() const {
  return IsNormal() ? 0 : IsItalic() ? DEFAULT_OBLIQUE_DEGREES : ObliqueAngle();
}

using FontSlantStyle = StyleFontStyle;
using FontWeight = StyleFontWeight;
using FontWidth = StyleFontWidth;

/**
 * Convenience type to hold a <min, max> pair representing a range of values.
 *
 * The min and max are both inclusive, so when min == max the range represents
 * a single value (not an empty range).
 */
template <class T, class Derived>
class FontPropertyRange {
  // This implementation assumes the underlying property type is a 16-bit value
  // (see FromScalar and AsScalar below).
  static_assert(sizeof(T) == 2, "FontPropertyValue should be a 16-bit type!");

 public:
  /**
   * Construct a range from given minimum and maximum values (inclusive).
   */
  FontPropertyRange(T aMin, T aMax) : mValues(aMin, aMax) {
    MOZ_ASSERT(aMin <= aMax);
  }

  /**
   * Construct a range representing a single value (min==max).
   */
  explicit FontPropertyRange(T aValue) : mValues(aValue, aValue) {}

  explicit FontPropertyRange(const FontPropertyRange& aOther) = default;
  FontPropertyRange& operator=(const FontPropertyRange& aOther) = default;

  T Min() const { return mValues.first; }
  T Max() const { return mValues.second; }

  /**
   * Clamp the given value to this range.
   */
  T Clamp(T aValue) const { return std::clamp(aValue, Min(), Max()); }

  /**
   * Return whether the range consists of a single unique value.
   */
  bool IsSingle() const { return Min() == Max(); }

  bool operator==(const FontPropertyRange& aOther) const {
    return mValues == aOther.mValues;
  }
  bool operator!=(const FontPropertyRange& aOther) const {
    return mValues != aOther.mValues;
  }

  /**
   * Conversion of the property range to/from a single 32-bit scalar value,
   * suitable for IPC serialization, hashing, caching.
   *
   * No assumptions should be made about the numeric value of the scalar.
   *
   * This depends on the underlying property type being a 16-bit value!
   */
  using ScalarType = uint32_t;

  ScalarType AsScalar() const {
    return (mValues.first.UnsignedRaw() << 16) | mValues.second.UnsignedRaw();
  }

  static Derived FromScalar(ScalarType aScalar) {
    static_assert(std::is_base_of_v<FontPropertyRange, Derived>);
    return Derived(T::FromRaw(aScalar >> 16), T::FromRaw(aScalar & 0xffff));
  }

 protected:
  std::pair<T, T> mValues;
};

class WeightRange : public FontPropertyRange<FontWeight, WeightRange> {
 public:
  WeightRange(FontWeight aMin, FontWeight aMax)
      : FontPropertyRange(aMin, aMax) {}

  explicit WeightRange(FontWeight aWeight) : FontPropertyRange(aWeight) {}

  WeightRange(const WeightRange& aOther) = default;

  void ToString(nsACString& aOutString, const char* aDelim = "..") const {
    aOutString.AppendFloat(Min().ToFloat());
    if (!IsSingle()) {
      aOutString.Append(aDelim);
      aOutString.AppendFloat(Max().ToFloat());
    }
  }
};

class WidthRange : public FontPropertyRange<FontWidth, WidthRange> {
 public:
  WidthRange(FontWidth aMin, FontWidth aMax) : FontPropertyRange(aMin, aMax) {}

  explicit WidthRange(FontWidth aWidth) : FontPropertyRange(aWidth) {}

  WidthRange(const WidthRange& aOther) = default;

  void ToString(nsACString& aOutString, const char* aDelim = "..") const {
    aOutString.AppendFloat(Min().ToFloat());
    if (!IsSingle()) {
      aOutString.Append(aDelim);
      aOutString.AppendFloat(Max().ToFloat());
    }
  }
};

class SlantStyleRange
    : public FontPropertyRange<FontSlantStyle, SlantStyleRange> {
 public:
  SlantStyleRange(FontSlantStyle aMin, FontSlantStyle aMax)
      : FontPropertyRange(aMin, aMax) {}

  explicit SlantStyleRange(FontSlantStyle aStyle) : FontPropertyRange(aStyle) {}

  SlantStyleRange(const SlantStyleRange& aOther) = default;

  void ToString(nsACString& aOutString, const char* aDelim = "..") const {
    Min().ToString(aOutString);
    if (!IsSingle()) {
      aOutString.Append(aDelim);
      Max().ToString(aOutString);
    }
  }
};

}
using namespace mozilla;


constexpr double kPresentationMismatch = 1.0e12;
constexpr double kWidthFactor = 1.0e8;
constexpr double kStyleFactor = 1.0e4;
constexpr double kWeightFactor = 1.0e0;

enum class StyleFontSynthesisStyle { Auto, ObliqueOnly };
enum class FontPresentation : uint8_t {
  // Character does not have the emoji property, so no special heuristics
  // apply during font selection.
  Any = 0,
  // Character is potentially emoji, but its default presentation is text.
  TextDefault,
  // Character is potentially emoji, but Text-style presentation has been
  // explicitly requested using VS15.
  TextExplicit,
  // Character has Emoji-style presentation by default (but an author-
  // provided webfont may be used even if it is not color).
  EmojiDefault,
  // Character explicitly requires Emoji-style presentation due to VS16 or
  // skin-tone codepoint.
  EmojiExplicit,
};
inline bool PrefersColor(FontPresentation aPresentation) {
  return aPresentation >= FontPresentation::EmojiDefault;
}
struct gfxFontStyle {
  StyleFontStyle style = StyleFontStyle::NORMAL;
  StyleFontWeight weight = StyleFontWeight::NORMAL;
  StyleFontWidth width = StyleFontWidth::NORMAL;
  StyleFontSynthesisStyle synthesisStyle = StyleFontSynthesisStyle::Auto;
  double size = 20;
  bool IsNormalStyle() const {
    return weight.IsNormal() && style.IsNormal() && width.IsNormal();
  }
};
struct gfxFont {
  int id = 0;
  bool color = false;
  bool HasColorGlyphFor(uint32_t, uint32_t) { note("color:", id); return color; }
};
struct RangeFlags { static constexpr int eAutoWeight = 1; };
struct gfxFontEntry {
  int id = 0;
  nsCString name;
  WidthRange mWidth{StyleFontWidth::NORMAL};
  WeightRange mWeight{StyleFontWeight::NORMAL};
  SlantStyleRange mStyle{StyleFontStyle::NORMAL};
  bool covered = true, skip = false, fontReady = true;
  gfxFont font;
  WidthRange Width() const { note("width:", id); return mWidth; }
  WeightRange Weight() const { note("weight:", id); return mWeight; }
  SlantStyleRange SlantStyle() const { note("style:", id); return mStyle; }
  const nsCString& Name() const { note("name:", id); return name; }
  bool IsItalic() const { return mStyle.Min().IsItalic(); }
  bool IsOblique() const { return !mStyle.Min().IsItalic() && !mStyle.Min().IsNormal(); }
  int mRangeFlags = 0;
  bool variableBold = false;
  bool HasBoldVariableWeight() { note("variable-bold:",id); return variableBold; }
  bool SupportsBold();
  bool SkipDuringSystemFallback() const { note("skip:", id); return skip; }
  bool HasCharacter(uint32_t) const { note("char:", id); return covered; }
  gfxFont* FindOrMakeFont(const gfxFontStyle*) { note("font:", id); return fontReady ? &font : nullptr; }
};
struct gfxFontFamily;
namespace mozilla::fontlist { struct Family; struct FontList; }
struct GlobalFontMatch {
  GlobalFontMatch(uint32_t aCharacter, uint32_t aNextCh,
                  const gfxFontStyle& aStyle, FontPresentation aPresentation)
      : mStyle(aStyle),
        mCh(aCharacter),
        mNextCh(aNextCh),
        mPresentation(aPresentation) {}

  RefPtr<gfxFontEntry> mBestMatch;       // current best match
  RefPtr<gfxFontFamily> mMatchedFamily;  // the family it belongs to
  mozilla::fontlist::Family* mMatchedSharedFamily = nullptr;
  const gfxFontStyle& mStyle;  // style to match
  const uint32_t mCh;          // codepoint to be matched
  const uint32_t mNextCh;      // following codepoint (or zero)
  FontPresentation mPresentation;
  uint32_t mCount = 0;               // number of fonts matched
  uint32_t mCmapsTested = 0;         // number of cmaps tested
  double mMatchDistance = INFINITY;  // metric indicating closest match
};
struct BitSet {
  int id = 0;
  bool covered = true;
  bool test(uint32_t) const { note("map:", id); return covered; }
};
struct gfxFontFamily {
  int id = 0;
  bool mHasStyles = true, mIsSimpleFamily = false;
  bool mFamilyCharacterMapInitialized = true, visible = true;
  nsCString mName;
  Lock mLock;
  BitSet mFamilyCharacterMap;
  nsTArray<RefPtr<gfxFontEntry>> mAvailableFonts;
  void FindStyleVariations() { note("variations:", id); mHasStyles = true; }
  bool TestCharacterMap(uint32_t c) { return mFamilyCharacterMap.test(c); }
  void ReadAllCMAPs() { note("readmaps:", id); mFamilyCharacterMapInitialized = true; }
  void FindAllFontsForStyle(const gfxFontStyle&, nsTArray<gfxFontEntry*>&, bool);
  void CheckForSimpleFamily();
  void FindFontForChar(GlobalFontMatch*);
  void SearchAllFontsForChar(GlobalFontMatch*);
};
namespace mozilla::fontlist {
using SharedBitSet = BitSet;
struct Pointer {
  void* p = nullptr;
  int id = -1;
  static Pointer Null() { return {}; }
  bool IsNull() const { return !p; }
  template<class T> T* ToArray(FontList* l, size_t) const { return ToPtr<T>(l); }
  template<class T> T* ToPtr(FontList*) const { note("pointer:", id); return static_cast<T*>(p); }
};
struct Face {
  struct InitData {
    int id;
    WeightRange mWeight;
    WidthRange mWidth;
    SlantStyleRange mStyle;
    BitSet* mCharMap;
    nsCString mDescriptor;
    unsigned mIndex = 0;
    gfxFontEntry* entry;
  };
  Face() = default;
  Face(FontList*, const InitData& d) : id(d.id), mWidth(d.mWidth), mWeight(d.mWeight), mStyle(d.mStyle), entry(d.entry) { note("construct-face:", id); }
  void SetCharacterMap(FontList*, BitSet* map, Family*) { mCharacterMap = {map,id}; note("setmap:",id); }
  int id = 0;
  WidthRange mWidth{StyleFontWidth::NORMAL};
  WeightRange mWeight{StyleFontWeight::NORMAL};
  SlantStyleRange mStyle{StyleFontStyle::NORMAL};
  uint16_t mSize = 0;
  bool valid = true;
  Pointer mCharacterMap;
  gfxFontEntry* entry = nullptr;
  bool HasValidDescriptor() const { note("descriptor:", id); return valid; }
};
struct Count { uint32_t value=0; operator uint32_t() const { return value; } void store(uint32_t v) { value=v; } };
struct DisplayString { nsCString value; const nsCString& AsString(FontList*) const { return value; } };
struct Family {
  Count mFaceCount;
  Pointer mFaces;
  DisplayString display;
  const DisplayString& DisplayName() const { return display; }
  void AddFaces(FontList*, const nsTArray<Face::InitData>&);
  int id = 0;
  bool initialized = true, fullyInitialized = true, visible = true;
  bool mIsSimple = false, facesAvailable = true, initializationSucceeds = true;
  Pointer mCharacterMap;
  Pointer initializedMap;
  std::vector<Pointer> faces;
  bool IsInitialized() const { note("initialized:", id); return initialized; }
  bool IsFullyInitialized() const { return fullyInitialized; }
  uint32_t NumFaces() const { return mFaceCount ? uint32_t(mFaceCount) : faces.size(); }
  Pointer* Faces(FontList*) const { note("faces:", id); return !facesAvailable ? nullptr : mFaceCount ? mFaces.ToPtr<Pointer>(nullptr) : const_cast<Pointer*>(faces.data()); }
  void SetupFamilyCharMap(FontList*) { note("setupmap:", id); mCharacterMap = initializedMap; }
  bool FindAllFacesForStyleInternal(FontList*, const gfxFontStyle&, nsTArray<Face*>&) const;
  void FindAllFacesForStyle(FontList*, const gfxFontStyle&, nsTArray<Face*>&, bool) const;
  void SearchAllFontsForChar(FontList*, GlobalFontMatch*);
};
struct FontList {
  Pointer Alloc(size_t bytes) { auto* p = std::calloc(1, bytes); assert(p); allocations.push_back(p); note("allocate:", bytes); return {p,-1}; }
  std::vector<Family> families;
  bool available = true;
  Family* Families() { return available ? families.data() : nullptr; }
  uint32_t NumFamilies() const { return families.size(); }
};
}
enum class FontVisibility { User };
struct FontVisibilityProvider { FontVisibility GetFontVisibility() { return FontVisibility::User; } };
struct FontFamily {
  mozilla::fontlist::Family* mShared = nullptr;
  gfxFontFamily* mUnshared = nullptr;
  FontFamily() = default;
  FontFamily(mozilla::fontlist::Family* p) : mShared(p) {}
  FontFamily(gfxFontFamily* p) : mUnshared(p) {}
};
struct FamilyMap {
  std::vector<RefPtr<gfxFontFamily>> families;
  const auto& Values() const { return families; }
};
bool parentProcess = true, asyncFallback = false;
bool XRE_IsParentProcess() { return parentProcess; }
struct StaticPrefs { static bool gfx_font_rendering_fallback_async() { return asyncFallback; } };
constexpr int eGfxLog_textrun = 0;
bool useCmapsPolicy = true;
struct gfxPlatform {
  static gfxPlatform* GetPlatform() { static gfxPlatform p; return &p; }
  static LogModule* GetLog(int) { return nullptr; }
  bool UseCmapsDuringSystemFallback() const { return useCmapsPolicy; }
};
struct gfxPlatformFontList {
  Lock mLock;
  FamilyMap mFontFamilies;
  mozilla::fontlist::FontList* shared = nullptr;
  gfxFontEntry* platformFace = nullptr;
  FontFamily platformFamily;
  bool whitelist = true;
  static gfxPlatformFontList* PlatformFontList() { static gfxPlatformFontList p; return &p; }
  bool InitializeFamily(mozilla::fontlist::Family* f, bool) {
    note("initialize:", f->id);
    if (f->initializationSucceeds) f->mCharacterMap = f->initializedMap;
    return f->initializationSucceeds;
  }
  gfxFontEntry* GetOrCreateFontEntry(mozilla::fontlist::Face* f, mozilla::fontlist::Family*) {
    note("entry:", f->id); return f->entry;
  }
  bool IsFontFamilyWhitelistActive() const { return whitelist; }
  mozilla::fontlist::FontList* SharedFontList() { return shared; }
  bool IsVisibleToCSS(const gfxFontFamily& f, FontVisibility) { note("visible:", f.id); return f.visible; }
  bool IsVisibleToCSS(const mozilla::fontlist::Family& f, FontVisibility) { note("visible:", f.id); return f.visible; }
  void StartCmapLoadingFromFamily(uint32_t i) { note("async:", i); }
  gfxFontEntry* PlatformGlobalFontFallback(FontVisibilityProvider*, uint32_t, Script,
                                           const gfxFontStyle*, FontFamily& family) {
    note("platform:", 0); family = platformFamily; return platformFace;
  }
  already_AddRefed<gfxFont> GlobalFontFallback(FontVisibilityProvider*, uint32_t,
      uint32_t, Script, FontPresentation, const gfxFontStyle*, uint32_t&, FontFamily&);
};


double StyleDistance(const mozilla::SlantStyleRange& aRange,
                     const mozilla::StyleFontStyle& aTargetStyle,
                     bool aItalicToObliqueFallback) {
  const mozilla::FontSlantStyle minStyle = aRange.Min();
  const mozilla::FontSlantStyle maxStyle = aRange.Max();
  if (aTargetStyle == minStyle || aTargetStyle == maxStyle) {
    return 0.0;  // styles match exactly ==> 0
  }

  // bias added to angle difference when searching in the non-preferred
  // direction from a target angle
  const double kReverse = 100.0;

  // bias added when we've crossed from positive to negative angles or
  // vice versa
  const double kNegate = 200.0;

  // bias added for oblique faces when italic is requested, and only-oblique
  // font-synthesis-style is in effect
  const double kBadFallback = 400.0;

  if (aTargetStyle.IsNormal()) {
    if (minStyle.IsItalic() || maxStyle.IsItalic()) {
      // italic is the worst match (prefer any oblique; 0deg was requested)
      return kBadFallback + kNegate + kReverse;
    }
    const double minAngle = minStyle.ObliqueAngle();
    if (minAngle >= 0.0) {
      return minAngle;
    }
    const double maxAngle = maxStyle.ObliqueAngle();
    if (maxAngle >= 0.0) {
      // [min,max] range includes 0.0, so it's a perfect match
      return 0.0;
    }
    return kNegate - maxAngle;
  }

  const double kDefaultAngle = mozilla::FontSlantStyle::DEFAULT_OBLIQUE_DEGREES;

  if (aTargetStyle.IsItalic()) {
    MOZ_ASSERT(!minStyle.IsItalic());  // we checked for equality above
    double targetAngle = kDefaultAngle;
    double fallbackBias = 0.0;
    if (!aItalicToObliqueFallback) {
      // If 'font-style-synthesis: oblique-only' is applied, we should not use
      // oblique as a fallback for italic, so we add a large "fallback bias" to
      // all results here, and prefer an angle as close to zero as possible.
      targetAngle = 0.0;
      fallbackBias = kBadFallback;
    }
    const double minAngle = minStyle.ObliqueAngle();
    if (minAngle >= targetAngle) {
      // Add 1.0 to ensure italic vs non-italic never returns 0.0, even if the
      // angle matches.
      return fallbackBias + minAngle - targetAngle + 1.0;
    }
    const double maxAngle = maxStyle.ObliqueAngle();
    if (maxAngle >= targetAngle) {
      return fallbackBias + 1.0;
    }
    if (maxAngle > 0.0) {
      // wrong direction but still > 0, add bias of 100
      return fallbackBias + kReverse + (targetAngle - maxAngle);
    }
    // negative oblique angle, add bias of 300
    return fallbackBias + kReverse + kNegate + (targetAngle - maxAngle);
  }

  // target is oblique <angle>: four different cases depending on
  // the value of the <angle>, which determines the preferred direction
  // of search
  const double targetAngle = aTargetStyle.ObliqueAngle();

  // italic is a bad fallback if it was not requested
  if (minStyle.IsItalic() || maxStyle.IsItalic()) {
    return kBadFallback + kNegate + kReverse;
  }

  if (targetAngle >= kDefaultAngle) {
    const double minAngle = minStyle.ObliqueAngle();
    if (minAngle >= targetAngle) {
      return minAngle - targetAngle;
    }
    const double maxAngle = maxStyle.ObliqueAngle();
    if (maxAngle >= targetAngle) {
      return 0.0;
    }
    if (maxAngle > 0.0) {
      return kReverse + (targetAngle - maxAngle);
    }
    return kReverse + kNegate + (targetAngle - maxAngle);
  }

  if (targetAngle <= -kDefaultAngle) {
    const double maxAngle = maxStyle.ObliqueAngle();
    if (maxAngle <= targetAngle) {
      return targetAngle - maxAngle;
    }
    const double minAngle = minStyle.ObliqueAngle();
    if (minAngle <= targetAngle) {
      return 0.0;
    }
    if (minAngle < 0.0) {
      return kReverse + (minAngle - targetAngle);
    }
    return kReverse + kNegate + (minAngle - targetAngle);
  }

  if (targetAngle >= 0.0) {
    const double minAngle = minStyle.ObliqueAngle();
    if (minAngle > targetAngle) {
      return kReverse + (minAngle - targetAngle);
    }
    const double maxAngle = maxStyle.ObliqueAngle();
    if (maxAngle >= targetAngle) {
      return 0.0;
    }
    if (maxAngle > 0.0) {
      return targetAngle - maxAngle;
    }
    return kReverse + kNegate + (targetAngle - maxAngle);
  }

  // last case: (targetAngle < 0.0 && targetAngle > kDefaultAngle)
  const double maxAngle = maxStyle.ObliqueAngle();
  if (maxAngle < targetAngle) {
    return kReverse + (targetAngle - maxAngle);
  }
  const double minAngle = minStyle.ObliqueAngle();
  if (minAngle <= targetAngle) {
    return 0.0;
  }
  if (minAngle < 0.0) {
    return minAngle - targetAngle;
  }
  return kReverse + kNegate + (minAngle - targetAngle);
}

double WidthDistance(const mozilla::WidthRange& aRange,
                     const mozilla::StyleFontWidth& aTargetWidth) {
  const double kReverseDistance = 1000.0;

  mozilla::FontWidth minWidth = aRange.Min();
  mozilla::FontWidth maxWidth = aRange.Max();

  // The width value is a (non-negative) percentage; currently we support
  // values in the range 0 .. 1000. (If the upper limit is ever increased,
  // the kReverseDistance value used here may need to be adjusted.)
  // If aTargetWidth is >100, we prefer larger values if available;
  // if <=100, we prefer smaller values if available.
  if (aTargetWidth < minWidth) {
    if (aTargetWidth > mozilla::FontWidth::NORMAL) {
      return minWidth.ToFloat() - aTargetWidth.ToFloat();
    }
    return (minWidth.ToFloat() - aTargetWidth.ToFloat()) + kReverseDistance;
  }
  if (aTargetWidth > maxWidth) {
    if (aTargetWidth <= mozilla::FontWidth::NORMAL) {
      return aTargetWidth.ToFloat() - maxWidth.ToFloat();
    }
    return (aTargetWidth.ToFloat() - maxWidth.ToFloat()) + kReverseDistance;
  }
  return 0.0;
}

double WeightDistance(const mozilla::WeightRange& aRange,
                      const mozilla::StyleFontWeight& aTargetWeight) {
  const double kNotWithinCentralRange = 100.0;
  const double kReverseDistance = 600.0;

  mozilla::FontWeight minWeight = aRange.Min();
  mozilla::FontWeight maxWeight = aRange.Max();

  if (aTargetWeight >= minWeight && aTargetWeight <= maxWeight) {
    // Target is within the face's range, so it's a perfect match
    return 0.0;
  }

  if (aTargetWeight < mozilla::FontWeight::NORMAL) {
    // Requested a lighter-than-400 weight
    if (maxWeight < aTargetWeight) {
      return aTargetWeight.ToFloat() - maxWeight.ToFloat();
    }
    // Add reverse-search penalty for bolder faces
    return (minWeight.ToFloat() - aTargetWeight.ToFloat()) + kReverseDistance;
  }

  if (aTargetWeight > mozilla::FontWeight::FromInt(500)) {
    // Requested a bolder-than-500 weight
    if (minWeight > aTargetWeight) {
      return minWeight.ToFloat() - aTargetWeight.ToFloat();
    }
    // Add reverse-search penalty for lighter faces
    return (aTargetWeight.ToFloat() - maxWeight.ToFloat()) + kReverseDistance;
  }

  // Special case for requested weight in the [400..500] range
  if (minWeight > aTargetWeight) {
    if (minWeight <= mozilla::FontWeight::FromInt(500)) {
      // Bolder weight up to 500 is first choice
      return minWeight.ToFloat() - aTargetWeight.ToFloat();
    }
    // Other bolder weights get a reverse-search penalty
    return (minWeight.ToFloat() - aTargetWeight.ToFloat()) + kReverseDistance;
  }
  // Lighter weights are not as good as bolder ones within [400..500]
  return (aTargetWeight.ToFloat() - maxWeight.ToFloat()) +
         kNotWithinCentralRange;
}

static inline double WeightStyleWidthDistance(
    gfxFontEntry* aFontEntry, const gfxFontStyle& aTargetStyle) {
  double widthDist = WidthDistance(aFontEntry->Width(), aTargetStyle.width);
  double styleDist = StyleDistance(
      aFontEntry->SlantStyle(), aTargetStyle.style,
      aTargetStyle.synthesisStyle != StyleFontSynthesisStyle::ObliqueOnly);
  double weightDist = WeightDistance(aFontEntry->Weight(), aTargetStyle.weight);

  // Sanity-check that the distances are within the expected range
  // (update if implementation of the distance functions is changed).
  MOZ_ASSERT(widthDist >= 0.0 && widthDist <= 2000.0);
  MOZ_ASSERT(styleDist >= 0.0 && styleDist <= 900.0);
  MOZ_ASSERT(weightDist >= 0.0 && weightDist <= 1600.0);

  // weight/style/width priority: width >> style >> weight
  // so we multiply the width and style values to make them dominate
  // the result
  return widthDist * kWidthFactor + styleDist * kStyleFactor +
         weightDist * kWeightFactor;
}

void gfxFontFamily::FindAllFontsForStyle(
    const gfxFontStyle& aFontStyle, nsTArray<gfxFontEntry*>& aFontEntryList,
    bool aIgnoreSizeTolerance) {
  if (!mHasStyles) {
    FindStyleVariations();  // collect faces for the family, if not already
                            // done
  }

  AutoReadLock lock(mLock);

  NS_ASSERTION(mAvailableFonts.Length() > 0, "font family with no faces!");
  NS_ASSERTION(aFontEntryList.IsEmpty(), "non-empty fontlist passed in");

  gfxFontEntry* fe = nullptr;

  // If the family has only one face, we simply return it; no further
  // checking needed
  uint32_t count = mAvailableFonts.Length();
  if (count == 1) {
    fe = mAvailableFonts[0];
    aFontEntryList.AppendElement(fe);
    return;
  }

  // Most families are "simple", having just Regular/Bold/Italic/BoldItalic,
  // or some subset of these. In this case, we have exactly 4 entries in
  // mAvailableFonts, stored in the above order; note that some of the entries
  // may be nullptr. We can then pick the required entry based on whether the
  // request is for bold or non-bold, italic or non-italic, without running the
  // more complex matching algorithm used for larger families with many weights
  // and/or widths.

  if (mIsSimpleFamily) {
    // Family has no more than the "standard" 4 faces, at fixed indexes;
    // calculate which one we want.
    // Note that we cannot simply return it as not all 4 faces are necessarily
    // present.
    bool wantBold = aFontStyle.weight >= FontWeight::FromInt(600);
    bool wantItalic = !aFontStyle.style.IsNormal();
    uint8_t faceIndex =
        (wantItalic ? kItalicMask : 0) | (wantBold ? kBoldMask : 0);

    // if the desired style is available, return it directly
    fe = mAvailableFonts[faceIndex];
    if (fe) {
      aFontEntryList.AppendElement(fe);
      return;
    }

    // order to check fallback faces in a simple family, depending on requested
    // style
    static const uint8_t simpleFallbacks[4][3] = {
        {kBoldFaceIndex, kItalicFaceIndex,
         kBoldItalicFaceIndex},  // fallbacks for Regular
        {kRegularFaceIndex, kBoldItalicFaceIndex, kItalicFaceIndex},  // Bold
        {kBoldItalicFaceIndex, kRegularFaceIndex, kBoldFaceIndex},    // Italic
        {kItalicFaceIndex, kBoldFaceIndex, kRegularFaceIndex}  // BoldItalic
    };
    const uint8_t* order = simpleFallbacks[faceIndex];

    for (uint8_t trial = 0; trial < 3; ++trial) {
      // check remaining faces in order of preference to find the first that
      // actually exists
      fe = mAvailableFonts[order[trial]];
      if (fe) {
        aFontEntryList.AppendElement(fe);
        return;
      }
    }

    // this can't happen unless we have totally broken the font-list manager!
    MOZ_ASSERT_UNREACHABLE("no face found in simple font family!");
  }

  // Pick the font(s) that are closest to the desired weight, style, and
  // width. Iterate over all fonts, measuring the weight/style distance.
  // Because of unicode-range values, there may be more than one font for a
  // given but the 99% use case is only a single font entry per
  // weight/style/width distance value. To optimize this, only add entries
  // to the matched font array when another entry already has the same
  // weight/style/width distance and add the last matched font entry. For
  // normal platform fonts with a single font entry for each
  // weight/style/width combination, only the last matched font entry will
  // be added.

  double minDistance = INFINITY;
  gfxFontEntry* matched = nullptr;
  // Iterate in reverse order so that faces like 'Bold' are matched before
  // matching style-distance faces such as 'Bold Outline' (see bug 1185812;
  // note that faces are sorted with "standard" faces later in the list.
  for (uint32_t i = count; i > 0;) {
    fe = mAvailableFonts[--i];
    // weight/style/width priority: width >> style >> weight
    double distance = WeightStyleWidthDistance(fe, aFontStyle);
    if (distance < minDistance) {
      matched = fe;
      if (!aFontEntryList.IsEmpty()) {
        aFontEntryList.Clear();
      }
      minDistance = distance;
    } else if (distance == minDistance) {
      if (matched && matched != fe) {
        aFontEntryList.AppendElement(matched);
      }
      matched = fe;
    }
  }

  NS_ASSERTION(matched, "didn't match a font within a family");

  if (matched) {
    aFontEntryList.AppendElement(matched);
  }
}

void gfxFontFamily::CheckForSimpleFamily() {
  MOZ_ASSERT(mLock.LockedForWritingByCurrentThread());
  // already checked this family
  if (mIsSimpleFamily) {
    return;
  }

  uint32_t count = mAvailableFonts.Length();
  if (count > 4 || count == 0) {
    return;  // can't be "simple" if there are >4 faces;
             // if none then the family is unusable anyway
  }

  if (count == 1) {
    mIsSimpleFamily = true;
    return;
  }

  WidthRange firstWidth = mAvailableFonts[0]->Width();
  if (!firstWidth.IsSingle()) {
    return;  // family with variation fonts is not considered "simple"
  }

  gfxFontEntry* faces[4] = {nullptr};
  for (uint8_t i = 0; i < count; ++i) {
    gfxFontEntry* fe = mAvailableFonts[i];
    if (fe->Width() != firstWidth || fe->IsOblique()) {
      // simple families don't have varying font-width or oblique
      return;
    }
    if (!fe->Weight().IsSingle() || !fe->SlantStyle().IsSingle()) {
      return;  // family with variation fonts is not considered "simple"
    }
    uint8_t faceIndex = (fe->IsItalic() ? kItalicMask : 0) |
                        (fe->SupportsBold() ? kBoldMask : 0);
    if (faces[faceIndex]) {
      return;  // two faces resolve to the same slot; family isn't "simple"
    }
    faces[faceIndex] = fe;
  }

  // we have successfully slotted the available faces into the standard
  // 4-face framework
  mAvailableFonts.SetLength(4);
  for (uint8_t i = 0; i < 4; ++i) {
    if (mAvailableFonts[i].get() != faces[i]) {
      mAvailableFonts[i].swap(faces[i]);
    }
  }

  mIsSimpleFamily = true;
}

inline bool gfxFontEntry::SupportsBold() {
  // bold == weights 600 and above
  // We return true if the face has a max weight descriptor >= 600,
  // OR if it's a user font with auto-weight (no descriptor) and has
  // a weight axis that supports values >= 600
  return Weight().Max().IsBold() ||
         ((mRangeFlags & RangeFlags::eAutoWeight) == RangeFlags::eAutoWeight &&
          HasBoldVariableWeight());
}

void gfxFontFamily::FindFontForChar(GlobalFontMatch* aMatchData) {
  gfxPlatformFontList::PlatformFontList()->mLock.AssertCurrentThreadIn();

  {
    AutoReadLock lock(mLock);
    if (mFamilyCharacterMapInitialized && !TestCharacterMap(aMatchData->mCh)) {
      // none of the faces in the family support the required char,
      // so bail out immediately
      return;
    }
  }

  nsCString charAndName;
  if (profiler_thread_is_being_profiled(
          Combine(ThreadProfilingFeatures::Sampling,
                  ThreadProfilingFeatures::Markers))) {
    charAndName = nsPrintfCString("\\u%x %s", aMatchData->mCh, mName.get());
  }
  AUTO_PROFILER_LABEL_DYNAMIC_NSCSTRING("gfxFontFamily::FindFontForChar",
                                        LAYOUT, charAndName);

  AutoTArray<gfxFontEntry*, 4> entries;
  FindAllFontsForStyle(aMatchData->mStyle, entries,
                       /*aIgnoreSizeTolerance*/ true);
  if (entries.IsEmpty()) {
    return;
  }

  gfxFontEntry* fe = nullptr;
  float distance = INFINITY;

  for (auto* e : entries) {
    if (e->SkipDuringSystemFallback()) {
      continue;
    }

    aMatchData->mCmapsTested++;
    if (e->HasCharacter(aMatchData->mCh)) {
      aMatchData->mCount++;

      LogModule* log = gfxPlatform::GetLog(eGfxLog_textrun);

      if (MOZ_UNLIKELY(MOZ_LOG_TEST(log, LogLevel::Debug))) {
        intl::Script script =
            intl::UnicodeProperties::GetScriptCode(aMatchData->mCh);
        MOZ_LOG(log, LogLevel::Debug,
                ("(textrun-systemfallback-fonts) char: u+%6.6x "
                 "script: %d match: [%s]\n",
                 aMatchData->mCh, int(script), e->Name().get()));
      }

      fe = e;
      distance = WeightStyleWidthDistance(fe, aMatchData->mStyle);
      if (aMatchData->mPresentation != FontPresentation::Any) {
        RefPtr<gfxFont> font = fe->FindOrMakeFont(&aMatchData->mStyle);
        if (!font) {
          continue;
        }
        bool hasColorGlyph =
            font->HasColorGlyphFor(aMatchData->mCh, aMatchData->mNextCh);
        if (hasColorGlyph != PrefersColor(aMatchData->mPresentation)) {
          distance += kPresentationMismatch;
        }
      }
      break;
    }
  }

  if (!fe && !aMatchData->mStyle.IsNormalStyle()) {
    // If style/weight/width was not Normal, see if we can
    // fall back to a next-best face (e.g. Arial Black -> Bold,
    // or Arial Narrow -> Regular).
    GlobalFontMatch data(aMatchData->mCh, aMatchData->mNextCh,
                         aMatchData->mStyle, aMatchData->mPresentation);
    SearchAllFontsForChar(&data);
    if (!data.mBestMatch) {
      return;
    }
    fe = data.mBestMatch;
    distance = data.mMatchDistance;
  }

  if (!fe) {
    return;
  }

  if (distance < aMatchData->mMatchDistance ||
      (distance == aMatchData->mMatchDistance &&
       Compare(fe->Name(), aMatchData->mBestMatch->Name()) > 0)) {
    aMatchData->mBestMatch = fe;
    aMatchData->mMatchedFamily = this;
    aMatchData->mMatchDistance = distance;
  }
}

void gfxFontFamily::SearchAllFontsForChar(GlobalFontMatch* aMatchData) {
  if (!mFamilyCharacterMapInitialized) {
    ReadAllCMAPs();
  }
  AutoReadLock lock(mLock);
  if (!mFamilyCharacterMap.test(aMatchData->mCh)) {
    return;
  }
  uint32_t numFonts = mAvailableFonts.Length();
  for (uint32_t i = numFonts; i > 0;) {
    gfxFontEntry* fe = mAvailableFonts[--i];
    if (fe && fe->HasCharacter(aMatchData->mCh)) {
      float distance = WeightStyleWidthDistance(fe, aMatchData->mStyle);
      if (aMatchData->mPresentation != FontPresentation::Any) {
        RefPtr<gfxFont> font = fe->FindOrMakeFont(&aMatchData->mStyle);
        if (!font) {
          continue;
        }
        bool hasColorGlyph =
            font->HasColorGlyphFor(aMatchData->mCh, aMatchData->mNextCh);
        if (hasColorGlyph != PrefersColor(aMatchData->mPresentation)) {
          distance += kPresentationMismatch;
        }
      }
      if (distance < aMatchData->mMatchDistance ||
          (distance == aMatchData->mMatchDistance &&
           Compare(fe->Name(), aMatchData->mBestMatch->Name()) > 0)) {
        aMatchData->mBestMatch = fe;
        aMatchData->mMatchedFamily = this;
        aMatchData->mMatchDistance = distance;
      }
    }
  }
}

namespace mozilla::fontlist {
void Family::AddFaces(FontList* aList, const nsTArray<Face::InitData>& aFaces) {
  MOZ_ASSERT(XRE_IsParentProcess());
  if (mFaceCount > 0) {
    // Already initialized!
    return;
  }

  uint32_t count = aFaces.Length();
  bool isSimple = false;
  // A family is "simple" (i.e. simplified style selection may be used instead
  // of the full CSS font-matching algorithm) if there is at maximum one normal,
  // bold, italic, and bold-italic face; in this case, they are stored at known
  // positions in the mFaces array.
  const Face::InitData* slots[4] = {nullptr, nullptr, nullptr, nullptr};
  if (count >= 2 && count <= 4) {
    // Check if this can be treated as a "simple" family
    isSimple = true;
    for (const auto& f : aFaces) {
      if (!f.mWeight.IsSingle() || !f.mWidth.IsSingle() ||
          !f.mStyle.IsSingle()) {
        isSimple = false;
        break;
      }
      if (!f.mWidth.Min().IsNormal()) {
        isSimple = false;
        break;
      }
      // Figure out which slot (0-3) this face belongs in
      size_t slot = 0;
      static_assert((kBoldMask | kItalicMask) == 0b11, "bad bold/italic bits");
      if (f.mWeight.Min().IsBold()) {
        slot |= kBoldMask;
      }
      if (!f.mStyle.Min().IsNormal()) {
        slot |= kItalicMask;
      }
      if (slots[slot]) {
        // More than one face mapped to the same slot - not a simple family!
        isSimple = false;
        break;
      }
      slots[slot] = &f;
    }
    if (isSimple) {
      // Ensure all 4 slots will exist, even if some are empty.
      count = 4;
    }
  }

  // Allocate space for the face records, and initialize them.
  // coverity[suspicious_sizeof]
  Pointer p = aList->Alloc(count * sizeof(Pointer));
  auto* facePtrs = p.ToArray<Pointer>(aList, count);
  for (size_t i = 0; i < count; i++) {
    if (isSimple && !slots[i]) {
      facePtrs[i] = Pointer::Null();
    } else {
      const auto* initData = isSimple ? slots[i] : &aFaces[i];
      Pointer fp = aList->Alloc(sizeof(Face));
      auto* face = fp.ToPtr<Face>(aList);
      (void)new (face) Face(aList, *initData);
      facePtrs[i] = fp;
      if (initData->mCharMap) {
        face->SetCharacterMap(aList, initData->mCharMap, this);
      }
    }
  }

  mIsSimple = isSimple;
  mFaces = p;
  mFaceCount.store(count);

  if (LOG_FONTLIST_ENABLED()) {
    const nsCString& fam = DisplayName().AsString(aList);
    for (unsigned j = 0; j < aFaces.Length(); j++) {
      nsAutoCString weight, style, width;
      aFaces[j].mWeight.ToString(weight);
      aFaces[j].mStyle.ToString(style);
      aFaces[j].mWidth.ToString(width);
      LOG_FONTLIST(
          ("(shared-fontlist) family (%s) added face (%s) index %u, weight "
           "%s, style %s, width %s",
           fam.get(), aFaces[j].mDescriptor.get(), aFaces[j].mIndex,
           weight.get(), style.get(), width.get()));
    }
  }
}
}

namespace mozilla::fontlist {
static double WSSDistance(const Face* aFace, const gfxFontStyle& aStyle) {
  double widthDist = WidthDistance(aFace->mWidth, aStyle.width);
  double styleDist = StyleDistance(
      aFace->mStyle, aStyle.style,
      aStyle.synthesisStyle != StyleFontSynthesisStyle::ObliqueOnly);
  double weightDist = WeightDistance(aFace->mWeight, aStyle.weight);

  // Sanity-check that the distances are within the expected range
  // (update if implementation of the distance functions is changed).
  MOZ_ASSERT(widthDist >= 0.0 && widthDist <= 2000.0);
  MOZ_ASSERT(styleDist >= 0.0 && styleDist <= 900.0);
  MOZ_ASSERT(weightDist >= 0.0 && weightDist <= 1600.0);

  // weight/style/width priority: width >> style >> weight
  // so we multiply the width and style values to make them dominate
  // the result
  return widthDist * kWidthFactor + styleDist * kStyleFactor +
         weightDist * kWeightFactor;
}
}

namespace mozilla::fontlist {
bool Family::FindAllFacesForStyleInternal(FontList* aList,
                                          const gfxFontStyle& aStyle,
                                          nsTArray<Face*>& aFaceList) const {
  MOZ_ASSERT(aFaceList.IsEmpty());
  if (!IsInitialized()) {
    return false;
  }

  Pointer* facePtrs = Faces(aList);
  if (!facePtrs) {
    return false;
  }

  // Depending on the kind of family, we have to do varying amounts of work
  // to figure out what face(s) to use for the requested style properties.

  // If the family has only one face, we simply use it; no further style
  // checking needed. (However, for bitmap fonts we may still need to check
  // whether the size is acceptable.)
  if (NumFaces() == 1) {
    MOZ_ASSERT(!facePtrs[0].IsNull());
    auto* face = facePtrs[0].ToPtr<Face>(aList);
    if (face && face->HasValidDescriptor()) {
      aFaceList.AppendElement(face);
#ifdef MOZ_WIDGET_GTK
      if (face->mSize) {
        return true;
      }
#endif
    }
    return false;
  }

  // Most families are "simple", having just Regular/Bold/Italic/BoldItalic,
  // or some subset of these. In this case, we have exactly 4 entries in
  // mAvailableFonts, stored in the above order; note that some of the entries
  // may be nullptr. We can then pick the required entry based on whether the
  // request is for bold or non-bold, italic or non-italic, without running
  // the more complex matching algorithm used for larger families with many
  // weights and/or widths.

  if (mIsSimple) {
    // Family has no more than the "standard" 4 faces, at fixed indexes;
    // calculate which one we want.
    // Note that we cannot simply return it as not all 4 faces are necessarily
    // present.
    bool wantBold = aStyle.weight.PreferBold();
    bool wantItalic = !aStyle.style.IsNormal();
    uint8_t faceIndex =
        (wantItalic ? kItalicMask : 0) | (wantBold ? kBoldMask : 0);

    // If the desired style is available, use it directly.
    auto* face = facePtrs[faceIndex].ToPtr<Face>(aList);
    if (face && face->HasValidDescriptor()) {
      aFaceList.AppendElement(face);
#ifdef MOZ_WIDGET_GTK
      if (face->mSize) {
        return true;
      }
#endif
      return false;
    }

    // Order to check fallback faces in a simple family, depending on the
    // requested style.
    static const uint8_t simpleFallbacks[4][3] = {
        {kBoldFaceIndex, kItalicFaceIndex,
         kBoldItalicFaceIndex},  // fallback sequence for Regular
        {kRegularFaceIndex, kBoldItalicFaceIndex, kItalicFaceIndex},  // Bold
        {kBoldItalicFaceIndex, kRegularFaceIndex, kBoldFaceIndex},    // Italic
        {kItalicFaceIndex, kBoldFaceIndex, kRegularFaceIndex}  // BoldItalic
    };
    const uint8_t* order = simpleFallbacks[faceIndex];

    for (uint8_t trial = 0; trial < 3; ++trial) {
      // check remaining faces in order of preference to find the first that
      // actually exists
      face = facePtrs[order[trial]].ToPtr<Face>(aList);
      if (face && face->HasValidDescriptor()) {
        aFaceList.AppendElement(face);
#ifdef MOZ_WIDGET_GTK
        if (face->mSize) {
          return true;
        }
#endif
        return false;
      }
    }

    // We can only reach here if we failed to resolve the face pointer, which
    // can happen if we're on a stylo thread and caught the font list being
    // updated; in that case we just fail quietly and let font fallback do
    // something for the time being.
    return false;
  }

  // Pick the font(s) that are closest to the desired weight, style, and
  // width. Iterate over all fonts, measuring the weight/style distance.
  // Because of unicode-range values, there may be more than one font for a
  // given but the 99% use case is only a single font entry per
  // weight/style/width distance value. To optimize this, only add entries
  // to the matched font array when another entry already has the same
  // weight/style/width distance and add the last matched font entry. For
  // normal platform fonts with a single font entry for each
  // weight/style/width combination, only the last matched font entry will
  // be added.
  double minDistance = INFINITY;
  Face* matched = nullptr;
  // Keep track of whether we've included any non-scalable font resources in
  // the selected set.
  bool anyNonScalable = false;
  for (uint32_t i = 0; i < NumFaces(); i++) {
    auto* face = facePtrs[i].ToPtr<Face>(aList);
    if (face) {
      // weight/style/width priority: width >> style >> weight
      double distance = WSSDistance(face, aStyle);
      if (distance < minDistance) {
        matched = face;
        if (!aFaceList.IsEmpty()) {
          aFaceList.Clear();
        }
        minDistance = distance;
      } else if (distance == minDistance) {
        if (matched) {
          aFaceList.AppendElement(matched);
#ifdef MOZ_WIDGET_GTK
          if (matched->mSize) {
            anyNonScalable = true;
          }
#endif
        }
        matched = face;
      }
    }
  }

  MOZ_ASSERT(matched, "didn't match a font within a family");
  if (matched) {
    aFaceList.AppendElement(matched);
#ifdef MOZ_WIDGET_GTK
    if (matched->mSize) {
      anyNonScalable = true;
    }
#endif
  }

  return anyNonScalable;
}
}

namespace mozilla::fontlist {
void Family::FindAllFacesForStyle(FontList* aList, const gfxFontStyle& aStyle,
                                  nsTArray<Face*>& aFaceList,
                                  bool aIgnoreSizeTolerance) const {
#ifdef MOZ_WIDGET_GTK
  bool anyNonScalable =
#else
  (void)
#endif
      FindAllFacesForStyleInternal(aList, aStyle, aFaceList);

#ifdef MOZ_WIDGET_GTK
  // aFaceList now contains whatever faces are the best style match for
  // the requested style. If specifically-sized bitmap faces are supported,
  // we need to additionally filter the list to choose the appropriate size.
  //
  // It would be slightly more efficient to integrate this directly into the
  // face-selection algorithm above, but it's a rare case that doesn't apply
  // at all to most font families.
  //
  // Currently we only support pixel-sized bitmap font faces on Linux/Gtk (i.e.
  // when using the gfxFcPlatformFontList implementation), so this filtering is
  // not needed on other platforms.
  //
  // (Note that color-bitmap emoji fonts like Apple Color Emoji or Noto Color
  // Emoji don't count here; they package multiple bitmap sizes into a single
  // OpenType wrapper, so they appear as a single "scalable" face in our list.)
  if (anyNonScalable) {
    uint16_t best = 0;
    gfxFloat dist = 0.0;
    for (const auto& f : aFaceList) {
      if (f->mSize == 0) {
        // Scalable face; no size distance to compute.
        continue;
      }
      gfxFloat d = fabs(gfxFloat(f->mSize) - aStyle.size);
      if (!aIgnoreSizeTolerance && (d * 5.0 > f->mSize)) {
        continue;  // Too far from the requested size, ignore.
      }
      // If we haven't found a "best" bitmap size yet, or if this is a better
      // match, remember it.
      if (!best || d < dist) {
        best = f->mSize;
        dist = d;
      }
    }
    // Discard all faces except the chosen "best" size; or if no pixel size was
    // chosen, all except scalable faces.
    // This may eliminate *all* faces in the family, if all were bitmaps and
    // none was a good enough size match, in which case we'll fall back to the
    // next font-family name.
    aFaceList.RemoveElementsBy([=](const auto& e) { return e->mSize != best; });
  }
#endif
}
}

namespace mozilla::fontlist {
void Family::SearchAllFontsForChar(FontList* aList,
                                   GlobalFontMatch* aMatchData) {
  auto* charmap = mCharacterMap.ToPtr<const SharedBitSet>(aList);
  if (!charmap) {
    // If the face list is not yet initialized, or if character maps have
    // not been loaded, go ahead and do this now (by sending a message to the
    // parent process, if we're running in a child).
    // After this, all faces should have their mCharacterMap set up, and the
    // family's mCharacterMap should also be set; but in the code below we
    // don't assume this all succeeded, so it still checks.
    if (!gfxPlatformFontList::PlatformFontList()->InitializeFamily(this,
                                                                   true)) {
      return;
    }
    charmap = mCharacterMap.ToPtr<const SharedBitSet>(aList);
  }
  if (charmap && !charmap->test(aMatchData->mCh)) {
    return;
  }

  uint32_t numFaces = NumFaces();
  uint32_t charMapsLoaded = 0;  // number of faces whose charmap is loaded
  Pointer* facePtrs = Faces(aList);
  if (!facePtrs) {
    return;
  }
  for (uint32_t i = 0; i < numFaces; i++) {
    auto* face = facePtrs[i].ToPtr<Face>(aList);
    if (!face) {
      continue;
    }
    MOZ_ASSERT(face->HasValidDescriptor());
    // Get the face's character map, if available (may be null!)
    charmap = face->mCharacterMap.ToPtr<const SharedBitSet>(aList);
    if (charmap) {
      ++charMapsLoaded;
    }
    // Check style distance if the char is supported, or if charmap not known
    // (so that we don't trigger cmap-loading for faces that would be a worse
    // match than what we've already found).
    if (!charmap || charmap->test(aMatchData->mCh)) {
      double distance = WSSDistance(face, aMatchData->mStyle);
      if (distance < aMatchData->mMatchDistance) {
        // It's a better style match: get a fontEntry, and if we haven't
        // already checked character coverage, do it now (note that
        // HasCharacter() will trigger loading the fontEntry's cmap, if
        // needed).
        RefPtr<gfxFontEntry> fe =
            gfxPlatformFontList::PlatformFontList()->GetOrCreateFontEntry(face,
                                                                          this);
        if (!fe) {
          continue;
        }
        if (!charmap && !fe->HasCharacter(aMatchData->mCh)) {
          continue;
        }
        if (aMatchData->mPresentation != FontPresentation::Any) {
          RefPtr<gfxFont> font = fe->FindOrMakeFont(&aMatchData->mStyle);
          if (!font) {
            continue;
          }
          bool hasColorGlyph =
              font->HasColorGlyphFor(aMatchData->mCh, aMatchData->mNextCh);
          if (hasColorGlyph != PrefersColor(aMatchData->mPresentation)) {
            distance += kPresentationMismatch;
            if (distance >= aMatchData->mMatchDistance) {
              continue;
            }
          }
        }
        aMatchData->mBestMatch = fe;
        aMatchData->mMatchDistance = distance;
        aMatchData->mMatchedSharedFamily = this;
      }
    }
  }
  if (mCharacterMap.IsNull() && charMapsLoaded == numFaces) {
    SetupFamilyCharMap(aList);
  }
}
}

already_AddRefed<gfxFont> gfxPlatformFontList::GlobalFontFallback(
    FontVisibilityProvider* aFontVisibilityProvider, uint32_t aCh,
    uint32_t aNextCh, Script aRunScript, FontPresentation aPresentation,
    const gfxFontStyle* aMatchStyle, uint32_t& aCmapCount,
    FontFamily& aMatchedFamily) {
  bool useCmaps = IsFontFamilyWhitelistActive() ||
                  gfxPlatform::GetPlatform()->UseCmapsDuringSystemFallback();
  FontVisibility level = aFontVisibilityProvider
                             ? aFontVisibilityProvider->GetFontVisibility()
                             : FontVisibility::User;
  if (!useCmaps) {
    // Allow platform-specific fallback code to try and find a usable font
    gfxFontEntry* fe = PlatformGlobalFontFallback(
        aFontVisibilityProvider, aCh, aRunScript, aMatchStyle, aMatchedFamily);
    if (fe) {
      if (aMatchedFamily.mShared) {
        if (IsVisibleToCSS(*aMatchedFamily.mShared, level)) {
          RefPtr<gfxFont> font = fe->FindOrMakeFont(aMatchStyle);
          if (font) {
            if (aPresentation == FontPresentation::Any) {
              return font.forget();
            }
            bool hasColorGlyph = font->HasColorGlyphFor(aCh, aNextCh);
            if (hasColorGlyph == PrefersColor(aPresentation)) {
              return font.forget();
            }
          }
        }
      } else {
        if (IsVisibleToCSS(*aMatchedFamily.mUnshared, level)) {
          RefPtr<gfxFont> font = fe->FindOrMakeFont(aMatchStyle);
          if (font) {
            if (aPresentation == FontPresentation::Any) {
              return font.forget();
            }
            bool hasColorGlyph = font->HasColorGlyphFor(aCh, aNextCh);
            if (hasColorGlyph == PrefersColor(aPresentation)) {
              return font.forget();
            }
          }
        }
      }
    }
  }

  // otherwise, try to find it among local fonts
  GlobalFontMatch data(aCh, aNextCh, *aMatchStyle, aPresentation);
  if (SharedFontList()) {
    fontlist::Family* families = SharedFontList()->Families();
    if (families) {
      for (uint32_t i = 0; i < SharedFontList()->NumFamilies(); i++) {
        fontlist::Family& family = families[i];
        if (!IsVisibleToCSS(family, level)) {
          continue;
        }
        if (!family.IsFullyInitialized() &&
            StaticPrefs::gfx_font_rendering_fallback_async() &&
            !XRE_IsParentProcess()) {
          // Start loading all the missing charmaps; but this is async,
          // so for now we just continue, ignoring this family.
          StartCmapLoadingFromFamily(i);
        } else {
          family.SearchAllFontsForChar(SharedFontList(), &data);
          if (data.mMatchDistance == 0.0) {
            // no better style match is possible, so stop searching
            break;
          }
        }
      }
      if (data.mBestMatch) {
        aMatchedFamily = FontFamily(data.mMatchedSharedFamily);
        return data.mBestMatch->FindOrMakeFont(aMatchStyle);
      }
    }
  } else {
    // iterate over all font families to find a font that support the
    // character
    for (const RefPtr<gfxFontFamily>& family : mFontFamilies.Values()) {
      if (!IsVisibleToCSS(*family, level)) {
        continue;
      }
      // evaluate all fonts in this family for a match
      family->FindFontForChar(&data);
      if (data.mMatchDistance == 0.0) {
        // no better style match is possible, so stop searching
        break;
      }
    }

    aCmapCount = data.mCmapsTested;
    if (data.mBestMatch) {
      aMatchedFamily = FontFamily(data.mMatchedFamily);
      return data.mBestMatch->FindOrMakeFont(aMatchStyle);
    }
  }

  return nullptr;
}

int main() {
  int id, operation, target, allow, presentation, count;
  while (std::cin >> id >> operation >> target >> allow >> presentation >> count) {
    assert(count >= 0 && count <= 16);
    events.clear();
    gfxFontStyle style;
    style.style = target == 30000 ? StyleFontStyle::OBLIQUE : StyleFontStyle::FromRaw(target);
    style.synthesisStyle = allow ? StyleFontSynthesisStyle::Auto : StyleFontSynthesisStyle::ObliqueOnly;
    int targetWeight, targetWidth, flags;
    std::cin >> targetWeight >> targetWidth >> flags;
    style.weight = StyleFontWeight::FromRaw(targetWeight);
    style.width = StyleFontWidth::FromRaw(targetWidth);
    std::array<gfxFontEntry, 16> entries;
    std::array<mozilla::fontlist::Face, 16> sharedFaces;
    std::array<BitSet, 16> maps;
    gfxFontFamily family;
    family.id = 100;
    family.mFamilyCharacterMap.id = 100;
    mozilla::fontlist::FontList list;
    list.families.resize(1);
    auto& shared = list.families[0];
    shared.id = 100;
    BitSet familyMap{100, true};
    shared.mCharacterMap = {&familyMap, 100};
    shared.initializedMap = shared.mCharacterMap;
    std::vector<int> scores;
    for (int i = 0; i < count; ++i) {
      int lo, hi, wl, wh, xl, xh, coverage, skip, ready, color, known, valid, present, size;
      std::cin >> lo >> hi >> wl >> wh >> xl >> xh >> coverage >> skip >> ready >> color >> known >> valid >> present >> size;
      assert((-23040 <= lo && lo <= hi && hi <= 23040) || (lo == 25600 && hi == 25600));
      assert(64 <= wl && wl <= wh && wh <= 64000);
      assert(0 <= xl && xl <= xh && xh <= 64000);
      auto& e = entries[i];
      e.id = i;
      e.name = nsCString(std::string(1, char('A' + i)).c_str());
      e.mStyle = SlantStyleRange(StyleFontStyle::FromRaw(lo), StyleFontStyle::FromRaw(hi));
      e.mWeight = WeightRange(StyleFontWeight::FromRaw(wl), StyleFontWeight::FromRaw(wh));
      e.mWidth = WidthRange(StyleFontWidth::FromRaw(xl), StyleFontWidth::FromRaw(xh));
      e.covered = coverage;
      e.skip = skip;
      e.fontReady = ready;
      e.font = {i, bool(color)};
      family.mAvailableFonts.AppendElement(&e);
      auto& f = sharedFaces[i];
      f.id = i;
      f.mStyle = e.mStyle;
      f.mWeight = e.mWeight;
      f.mWidth = e.mWidth;
      f.mSize = size;
      f.valid = valid;
      f.entry = present ? &e : nullptr;
      maps[i] = {i, bool(coverage)};
      f.mCharacterMap = {known ? &maps[i] : nullptr, i};
      shared.faces.push_back({present == 2 ? nullptr : &f, i});
      double distance = StyleDistance(e.mStyle, style.style, allow);
      assert(std::isfinite(distance) && distance * 256 == std::trunc(distance * 256));
      scores.push_back(int(distance * 256));
    }
    if (flags & 128) for (int i=0; i<count; ++i) entries[i].name = nsCString(std::string(1, char('Z'-i)).c_str());
    if ((flags & 256) && count > 1) {
      family.mAvailableFonts.back() = &entries[0];
      shared.faces.back() = shared.faces.front();
    }
    shared.initialized = !(flags & 1);
    shared.facesAvailable = !(flags & 2);
    if (flags & 4) shared.mCharacterMap = {nullptr, 100};
    if (flags & 16384) shared.initializedMap = {nullptr, 100};
    shared.initializationSucceeds = !(flags & 8);
    family.mFamilyCharacterMap.covered = familyMap.covered = !(flags & 16);
    family.mFamilyCharacterMapInitialized = !(flags & 32);
    shared.mIsSimple = flags & 64;
    events.clear();
    std::vector<int> selected;
    uint32_t globalCmaps = 0;
    GlobalFontMatch match(88, 0, style, FontPresentation(presentation));
    auto* platform = gfxPlatformFontList::PlatformFontList();
    platform->shared = nullptr;
    platform->whitelist = !(flags & 512);
    platform->platformFace = count ? &entries[0] : nullptr;
    platform->platformFamily = FontFamily(&family);
    useCmapsPolicy = !(flags & 512);
    parentProcess = !(flags & 2048);
    asyncFallback = flags & 2048;
    platform->mFontFamilies.families.clear();
    platform->mFontFamilies.families.push_back(&family);
    if (operation == 13) {
      selected = {int(sizeof(mozilla::fontlist::Pointer)), int(sizeof(mozilla::fontlist::Face))};
    } else if (operation == 1) {
      nsTArray<gfxFontEntry*> result;
      family.FindAllFontsForStyle(style, result, true);
      for (auto* e : result) selected.push_back(e->id);
    } else if (operation == 2) {
      nsTArray<mozilla::fontlist::Face*> result;
      shared.FindAllFacesForStyle(&list, style, result, false);
      for (auto* f : result) selected.push_back(f->id);
    } else if (operation == 3) {
      family.SearchAllFontsForChar(&match);
    } else if (operation == 4) {
      shared.SearchAllFontsForChar(&list, &match);
    } else if (operation == 5) {
      family.FindFontForChar(&match);
    } else if (operation == 6 || operation == 7 || operation == 10 || operation == 11) {
      std::array<gfxFontFamily,16> singleFamilies;
      if (operation >= 10) {
        platform->mFontFamilies.families.clear();
        list.families.clear();
        list.families.resize(count);
        for (int i=0; i<count; ++i) {
          auto& uf = singleFamilies[i];
          uf.id = 100+i;
          uf.mFamilyCharacterMap.id = 100+i;
          uf.mAvailableFonts.AppendElement(&entries[i]);
          uf.visible = !(i == 0 && (flags & 1024));
          platform->mFontFamilies.families.push_back(&uf);
          auto& sf = list.families[i];
          sf.id = 100+i;
          sf.faces.push_back({&sharedFaces[i],i});
          sf.mCharacterMap = sf.initializedMap = {&maps[i],i};
          sf.visible = uf.visible;
          sf.fullyInitialized = !(i == 0 && (flags & 2048));
        }
      }
      list.available = !(flags & 4096);
      if (operation == 7 || operation == 11) platform->shared = &list;
      FontFamily chosen;
      uint32_t cmapCount = 0;
      auto* font = platform->GlobalFontFallback(nullptr, 88, 0, Script::Common,
          FontPresentation(presentation), &style, cmapCount, chosen);
      globalCmaps = cmapCount;
      if (font) selected.push_back(font->id);
    } else if (operation == 8) {
      for (int raw = -23040; raw <= 23040; ++raw) {
        auto value = StyleFontStyle::FromRaw(raw);
        assert(value.Raw() == raw);
        assert(value.ToFloat() * 256 == raw);
        assert(StyleFontStyle::FromFloat(value.ToFloat()).Raw() == raw);
        SlantStyleRange range(value);
        assert(SlantStyleRange::FromScalar(range.AsScalar()) == range);
      }
      for (unsigned raw=0; raw<=64000; ++raw) {
        auto width = StyleFontWidth::FromRaw(raw);
        assert(width.Raw() == raw && width.ToFloat() * 64 == raw);
        assert(StyleFontWidth::FromFloat(width.ToFloat()).Raw() == raw);
        WidthRange range(width);
        assert(WidthRange::FromScalar(range.AsScalar()) == range);
        if (raw >= 64) {
          auto weight = StyleFontWeight::FromRaw(raw);
          assert(weight.Raw() == raw && weight.ToFloat() * 64 == raw);
          assert(StyleFontWeight::FromFloat(weight.ToFloat()).Raw() == raw);
          WeightRange weights(weight);
          assert(WeightRange::FromScalar(weights.AsScalar()) == weights);
        }
      }
      assert(StyleFontStyle::ITALIC.Raw() == 25600);
      assert(StyleFontStyle::OBLIQUE.Raw() == StyleFontStyle::DEFAULT_OBLIQUE_DEGREES * 256);
      selected.push_back(StyleFontStyle::OBLIQUE.Raw());
      selected.push_back(StyleFontStyle::DEFAULT_OBLIQUE_DEGREES);
    } else if (operation == 12) {
      nsTArray<mozilla::fontlist::Face::InitData> init;
      for (int i=0; i<count; ++i) init.AppendElement({i,entries[i].mWeight,entries[i].mWidth,entries[i].mStyle,&maps[i],entries[i].name,0,&entries[i]});
      shared.AddFaces(&list,init);
      selected.push_back(shared.mIsSimple);
      nsTArray<mozilla::fontlist::Face*> result;
      shared.FindAllFacesForStyle(&list,style,result,false);
      for (auto* f : result) selected.push_back(f->id);
    } else if (operation == 9) {
      family.CheckForSimpleFamily();
      selected.push_back(family.mIsSimpleFamily);
      nsTArray<gfxFontEntry*> result;
      family.FindAllFontsForStyle(style, result, true);
      for (auto* e : result) selected.push_back(e->id);
    }
    if (operation >= 3 && operation <= 5 && match.mBestMatch)
      selected.push_back(match.mBestMatch->id);
    std::cout << id << '|';
    for (size_t i = 0; i < scores.size(); ++i) std::cout << (i ? "," : "") << scores[i];
    std::cout << '|';
    for (size_t i = 0; i < selected.size(); ++i) std::cout << (i ? "," : "") << selected[i];
    std::cout << '|' << match.mCount << ',' << match.mCmapsTested << ',' << globalCmaps << '|';
    for (size_t i = 0; i < events.size(); ++i) std::cout << (i ? "," : "") << events[i];
    std::cout << '\n';
    for (auto* p : allocations) std::free(p);
    allocations.clear();
  }
}
