#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstddef>
#define MOZ_ASSERT(condition, ...) assert(condition)
#define NS_ASSERTION(condition, ...) assert(condition)
using nscoord = int32_t;
constexpr nscoord nscoord_MAX = (1 << 30)-1;
constexpr nscoord nscoord_MIN = -nscoord_MAX;
namespace mozilla { constexpr int AppUnitsPerCSSPixel() { return 60; } }
extern "C" void capsule_trace(uint32_t, uint32_t, float, float);
struct StyleCSSPixelLength {
  float _0;
  static StyleCSSPixelLength FromPixels(float v) { return {v}; }
  float ToCSSPixels() const { return _0; }
  bool IsZero() const;
  void ScaleBy(float);
  StyleCSSPixelLength ScaledBy(float) const;
  nscoord ToAppUnits() const;
};
struct StyleLineHeight {
  uint32_t tag;
  float value;
  bool IsLength() const { return tag==0; }
  bool IsNumber() const { return tag==1; }
  bool IsNormal() const { return tag==2; }
  StyleCSSPixelLength AsLength() const { return {value}; }
  float AsNumber() const { return value; }
  static StyleLineHeight Normal() { return {2,0}; }
};
struct nsFont { StyleCSSPixelLength size; uint32_t owner; int32_t em, internal, external; };
struct nsAtom {};
struct nsStyleFont {
  StyleLineHeight mLineHeight;
  nsFont mFont;
  uint32_t mExplicitLanguage;
  nsAtom* GetLangAtom() const { capsule_trace(20,mFont.owner,mLineHeight.IsNormal() ? 0.0f : mLineHeight.value,mFont.size._0); return nullptr; }
};
struct nsIContent { bool control=false; };
namespace mozilla::dom {
struct Element : nsIContent {};
struct HTMLInputElement : Element {
  static const HTMLInputElement* FromNodeOrNull(const nsIContent* c) { return c && c->control ? static_cast<const HTMLInputElement*>(c) : nullptr; }
  bool IsSingleLineTextControl() const { return true; }
};
}
using mozilla::dom::HTMLInputElement;
struct nsFontMetrics {
  enum Orientation { eVertical,eHorizontal };
  struct Params { nsAtom* language; bool explicitLanguage; Orientation orientation; void* userFontSet; void* textPerf; void* featureValueLookup; };
  int32_t em, internal, external;
  nscoord ExternalLeading() { return external; }
  nscoord InternalLeading() { return internal; }
  nscoord EmHeight() { return em; }
};
template<class T> using RefPtr=T*;
struct nsPresContext {
  nsFontMetrics metrics;
  void* GetUserFontSet() { return nullptr; }
  void* GetTextPerfMetrics() { return nullptr; }
  void* GetFontFeatureValuesLookup() { return nullptr; }
  nsFontMetrics* GetMetricsFor(const nsFont& f, const nsFontMetrics::Params& p) {
    capsule_trace(21,f.owner,float(p.orientation),f.size._0);
    metrics={f.em,f.internal,f.external}; return &metrics;
  }
};
struct ReflowInput {
  static constexpr float kNormalLineHeightFactor=1.2f;
  static nscoord CalcLineHeight(const StyleLineHeight&,const nsStyleFont&,nsPresContext*,bool,const nsIContent*,float);
};
static int mutex;
static int* sServoFFILock=&mutex;
struct MutexAutoLock { explicit MutexAutoLock(int&) {} };
struct StyleZoom {
  float value;
  static const StyleZoom ONE;
  bool operator==(StyleZoom z) const { return value==z.value; }
  float ToFloat() const { return value; }
  float Unzoom(float) const;
};
const StyleZoom StyleZoom::ONE{1};
struct ComputedStyle {
  StyleZoom zoom;
  StyleZoom EffectiveZoom() const { return zoom; }
};
struct nsROCSSPrimitiveValue { float value=0; void SetPixels(float f) { value=f; } };
struct nsComputedDOMStyle { const ComputedStyle* mComputedStyle; void SetValueToPixels(nsROCSSPrimitiveValue*,float); };
extern "C" nscoord Gecko_CalcLineHeight(const StyleLineHeight*,const nsPresContext*,bool,const nsStyleFont*,const mozilla::dom::Element*);
#include "provider.inc"
extern "C" float capsule_cssom(float length,float zoom) {
  ComputedStyle style{{zoom}};
  nsComputedDOMStyle dom{&style};
  nsROCSSPrimitiveValue result;
  dom.SetValueToPixels(&result,length);
  return result.value;
}
extern "C" nsPresContext* capsule_context(bool present) {
  static nsPresContext context{};
  return present ? &context : nullptr;
}

static_assert(sizeof(StyleLineHeight)==8 && alignof(StyleLineHeight)==4);
static_assert(sizeof(nsFont)==20 && alignof(nsFont)==4);
static_assert(sizeof(nsStyleFont)==32 && alignof(nsStyleFont)==4);
static_assert(offsetof(nsStyleFont,mFont)==8 && offsetof(nsStyleFont,mExplicitLanguage)==28);
