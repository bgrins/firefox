#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <climits>
#include <iostream>
#include <iomanip>
#include <limits>
#include <memory>
#include <optional>
#include <string>
#include <vector>
using gfxFloat = double;
using nscoord = int32_t;
inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;
inline constexpr nscoord nscoord_MIN = -nscoord_MAX;
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define BIG_TEXT_NODE_SIZE 16
@@NUMERIC@@
static std::vector<std::vector<long long>> events;
static void event(long long code, long long a=0, long long b=0) { events.push_back({code,a,b}); }
static bool failRun=false, firstLetter=false;
static int letterModel=0;
struct Range { uint32_t start,end; Range(uint32_t a,uint32_t b):start(a),end(b){assert(a<=b);} uint32_t Length() const{return end-start;} };
template<class T> struct RefPtr {
  T* p=nullptr; RefPtr()=default; RefPtr(T* v):p(v){} operator T*() const{return p;}
  T* operator->() const {assert(p);return p;} RefPtr& operator=(T* v){p=v;return *this;}
};
template<class T> RefPtr(T*) -> RefPtr<T>;
template<class T> struct Maybe {
  std::optional<T> v; Maybe()=default; Maybe(T x):v(x){} explicit operator bool()const{return v.has_value();}
  T* operator->(){return &v.value();} const T* operator->()const{return &v.value();}
  T valueOr(T other)const{return v.value_or(other);}
  template<class F>T valueOrFrom(F f)const{return v?*v:f();}
};
template<class T> Maybe<T> Some(T x){return Maybe<T>(x);}
template<class T> struct nsTArray:std::vector<T> {
  uint32_t Length()const{return this->size();} void AppendElement(T x){this->push_back(x);}
  bool AppendElements(size_t n,int){this->resize(this->size()+n);return true;}
  T* Elements(){return this->data();}
};
template<class T,int N>using AutoTArray=nsTArray<T>;
constexpr int fallible=0;
namespace mozilla {
namespace dom {class CharacterDataBuffer { public:
 std::vector<char32_t> chars; uint32_t GetLength()const{return chars.size();} bool Is2b()const{return false;}
 char32_t ScalarValueAt(int i)const{assert(i>=0&&size_t(i)<chars.size());return chars[i];}
};}
struct TextAutospace {
 enum class CharClass {Other,CombiningMark,Ideograph};
 static CharClass GetCharClass(char32_t){return CharClass::Other;}
 bool ShouldApplySpacing(CharClass,CharClass)const{return false;} double InterScriptSpacing()const{return 0;}
};
template<class A>void BinarySearch(const A& a,size_t lo,size_t hi,uint32_t key,size_t* out){
 while(lo<hi){auto m=lo+(hi-lo)/2;if(a[m]<key)lo=m+1;else hi=m;}*out=lo;
}
namespace gfx {struct ShapedTextFlags {static constexpr int TEXT_ENABLE_HYPHEN_BREAKS=1;};}
}
using mozilla::dom::CharacterDataBuffer;
using TextAutospace=mozilla::TextAutospace;
namespace gfx=mozilla::gfx;
namespace intl {struct UnicodeProperties {static bool IsCursiveScript(char32_t){return false;}};}
namespace StaticPrefs {int layout_css_letter_spacing_model(){return letterModel;}}
struct gfxSkipCharsIterator {
 mutable uint32_t pos=0; bool IsInitialized()const{return true;}
 uint32_t GetSkippedOffset()const{return pos;} int32_t GetOriginalOffset()const{return pos;}
 void SetSkippedOffset(uint32_t x)const{pos=x;} void AdvanceOriginal(int32_t n){pos+=n;}
 uint32_t ConvertSkippedToOriginal(uint32_t n)const{return n;}
};
struct nsSkipCharsRunIterator {
 enum {LENGTH_UNSKIPPED_ONLY}; gfxSkipCharsIterator pos;uint32_t len;bool used=false;
 nsSkipCharsRunIterator(gfxSkipCharsIterator p,int,uint32_t n):pos(p),len(n){}
 bool NextRun(){if(used)return false;used=true;return len>0;}
 uint32_t GetSkippedOffset()const{return pos.pos;} int32_t GetOriginalOffset()const{return pos.pos;}
 int32_t GetRunLength()const{return len;} gfxSkipCharsIterator GetPos()const{return pos;}
};
struct Metrics {double zero=20,spaceWidth=20;double ZeroOrAveCharWidth()const{return zero;}};
struct Font {Metrics metrics;Metrics GetMetrics(int)const{event(21);return metrics;}};
struct gfxFontGroup {Font font;Font* GetFirstValidFont(char){event(20);return &font;}};
struct nsFontMetrics {
 enum {eHorizontal,eVertical};gfxFontGroup group;int32_t em=20;
 gfxFontGroup* GetThebesFontGroup(){return &group;} int32_t EmHeight()const{return em;}
};
static Metrics GetFirstFontMetrics(gfxFontGroup* g,bool){event(10);return g->font.metrics;}
struct gfxTextRun {
 using Range=::Range;enum class HyphenType {None};
 struct PropertyProvider {struct Spacing {double mBefore,mAfter;};virtual bool GetSpacing(Range,Spacing*)const=0;virtual ~PropertyProvider()=default;};
 struct CompressedGlyph {
  bool tab=false;uint32_t advance=0;static constexpr int FLAG_BREAK_TYPE_NORMAL=1;
  bool IsSimpleGlyph()const{return !tab;} bool IsSimpleGlyphNoBreakBefore()const{return !tab;}
  uint32_t GetSimpleAdvance()const{return advance;} bool CharIsTab()const{return tab;}
  bool CharIsNewline()const{return false;} bool IsClusterStart()const{return true;}
  bool IsLigatureGroupStart()const{return true;} bool CharIsFormattingControl()const{return false;}
  int CanBreakBefore()const{return 0;} uint32_t GetGlyphCount()const{return 0;}
 };
 struct Detail {int32_t mAdvance;};std::vector<CompressedGlyph> glyphs;uint32_t logicalLength=0;nsFontMetrics* fm=nullptr;
 uint32_t GetLength()const{return logicalLength;} const CompressedGlyph* GetCharacterGlyphs()const{return glyphs.data();}
 bool CharIsTab(uint32_t i)const{return glyphs.at(i).tab;} bool IsClusterStart(uint32_t i)const{assert(i<glyphs.size());return true;}
 const Detail* GetDetailedGlyphs(uint32_t,uint32_t)const{assert(false);return nullptr;}
 bool IsRightToLeft()const{return false;} bool IsVertical()const{return false;}
 gfxFontGroup* GetFontGroup()const{return &fm->group;} double GetAppUnitsPerDevUnit()const{return 1;}
 int GetFlags()const{return 0;} int GetFlags2()const{return std::any_of(glyphs.begin(),glyphs.begin()+logicalLength,[](auto g){return g.tab;})?1:0;}
 bool CanBreakLineBefore(uint32_t)const{return false;}
 static bool IsOptionalHyphenBreak(HyphenType){return false;}
 double GetAdvanceWidth(Range r,PropertyProvider* provider=nullptr)const{
  event(11,r.start,r.end);double value=0;std::vector<PropertyProvider::Spacing> spacing(r.Length());
  if(provider)provider->GetSpacing(r,spacing.data());
  for(auto i=r.start;i<r.end;i++){value+=glyphs.at(i).advance;if(provider)value+=spacing[i-r.start].mBefore+spacing[i-r.start].mAfter;}
  return value;
 }
 double GetMinAdvanceWidth(Range r,int)const {double v=0;for(auto i=r.start;i<r.end;i++)v=std::max(v,double(glyphs.at(i).advance));return v;}
};
namespace nsTextFrameUtils {struct Flags {static constexpr int HasTab=1,HasTrailingBreak=2;};}
struct nsIFrame;
enum class StyleHyphens {None,Auto,Manual};enum class StyleOverflowWrap {Normal,Anywhere};
struct SpacingValue {int value=0;int Resolve(int)const{return value;}};
struct TabSize {bool length=true;struct Length {struct Value {int value=0;int ToAppUnits()const{return value;}} _0;} lengthValue;
 struct Number {double _0=0;} number;bool IsLength()const{return length;}bool IsNumber()const{return !length;}
};
struct ActualTabSize {bool isLength=true;struct Length {struct V {int value=0;int ToAppUnits()const{return value;}} _0;} length;
 struct Number{double _0=0;}number;bool IsLength()const{return isLength;}bool IsNumber()const{return !isLength;}};
struct nsStyleText {
 ActualTabSize mTabSize;SpacingValue mLetterSpacing,mWordSpacing;StyleHyphens mHyphens=StyleHyphens::None;bool wrap=false,significant=true;StyleOverflowWrap overflow=StyleOverflowWrap::Normal;
 bool WhiteSpaceCanWrap(nsIFrame*)const{return wrap;}bool WhiteSpaceIsSignificant()const{return significant;}
 bool NewlineIsSignificant(nsIFrame*)const{return significant;}bool WhiteSpaceCanHangOrVisuallyCollapse()const{return false;}
 bool WordCanWrap(nsIFrame*)const{return wrap;}bool TabIsSignificant()const{return significant;}
 StyleOverflowWrap EffectiveOverflowWrap()const{return overflow;}
};
struct ComputedStyle {bool combined=false;bool IsTextCombined()const{return combined;}};
struct PresContextValue {int AppUnitsPerDevPixel()const{return 1;}};
struct WritingMode {bool IsCentralBaseline()const{return false;}};
struct nsIFrame {
 nsStyleText text;ComputedStyle style;nsFontMetrics fm;PresContextValue pres;
 const nsStyleText* StyleText()const{return &text;}const void* StyleDisplay()const{return nullptr;}
 const nsIFrame* GetContainingBlock(int,const void*)const{return this;}
 nsIFrame* GetContainingBlock(){return this;}const ComputedStyle* Style()const{return &style;}
 const PresContextValue* PresContext()const{return &pres;}WritingMode GetWritingMode()const{return {};}
};
namespace nsLayoutUtils {nsFontMetrics* GetFontMetricsForFrame(const nsIFrame* f,float){event(22);return const_cast<nsFontMetrics*>(&f->fm);}}
struct gfxContext {void* GetDrawTarget(){return nullptr;}};
struct InlineData {
 nscoord mCurrentLine=0,mTrailingWhitespace=0;bool mAtStartOfLine=true,mLineIsEmpty=true,mSkipWhitespace=false;void* mLine=nullptr;
 nsIFrame* LineContainer(){return nullptr;}void OptionallyBreak(int=0){event(30);}void ForceBreak(){event(31);mCurrentLine=0;}
};
using InlineMinISizeData=InlineData;using InlinePrefISizeData=InlineData;
struct nsTextFrame:nsIFrame {
 enum TextRunType:uint8_t {eInflated,eNotInflated};struct TabWidthStore;
 gfxTextRun run;::CharacterDataBuffer buffer;uint32_t start=0,end=0;int contentOffset=0;TabWidthStore* property=nullptr;
 gfxTextRun* GetTextRun(TextRunType){return failRun?nullptr:&run;}
 const ::CharacterDataBuffer& CharacterDataBuffer()const{return buffer;}
 int GetContentLength()const{return run.logicalLength;}int GetInFlowContentLength()const{return run.logicalLength;}
 int GetContentOffset()const{return contentOffset;}bool IsInSVGTextSubtree()const{return false;}
 nsTextFrame* GetNextSibling()const{return nullptr;}nsTextFrame* GetPrevInFlow()const{return nullptr;}nsIFrame* GetParent(){return this;}
 nsFontMetrics* InflatedFontMetrics(){return &fm;}
 gfxSkipCharsIterator EnsureTextRun(TextRunType,void*,nsIFrame*,void*,uint32_t* limit){event(1,start,end);*limit=end;return {start};}
 void MaybeSplitFramesForFirstLetter(){event(2);}
 TabWidthStore* GetProperty(int){event(3);return property;}
 void SetProperty(int,TabWidthStore* p){event(4);property=p;}
 void RemoveProperty(int);
 class PropertyProvider:public gfxTextRun::PropertyProvider {
 public:
 using Spacing=gfxTextRun::PropertyProvider::Spacing;using HyphenType=gfxTextRun::HyphenType;
 PropertyProvider(gfxTextRun*,const nsStyleText*,const class CharacterDataBuffer&,nsTextFrame*,const gfxSkipCharsIterator&,int32_t,nsIFrame*,nscoord,TextRunType,bool);
 PropertyProvider(nsTextFrame*,const gfxSkipCharsIterator&,TextRunType,nsFontMetrics*);
 bool GetSpacing(Range,Spacing*)const override;bool GetSpacingInternal(Range,Spacing*,bool)const;
 void CalcTabWidths(Range,gfxFloat)const;gfxFloat MinTabAdvance()const;
 void InitTextAutospace(){event(5);}
 nsFontMetrics* GetFontMetrics()const{return &mFrame->fm;}
 void GetHyphenationBreaks(Range,HyphenType*)const{assert(false);}
 gfxFloat GetHyphenWidth()const{return 0;}
 @@ACCESSORS@@
 @@MEMBERS@@
 };
 void AddInlineMinISizeForFlow(gfxContext*,InlineMinISizeData*,TextRunType);
 void AddInlinePrefISizeForFlow(gfxContext*,InlinePrefISizeData*,TextRunType);
};
static int TabWidthProperty(){return 1;}
static int ResolveWordSpacing(nsTextFrame*,const nsStyleText& s){return s.mWordSpacing.value;}
static int ResolveLetterSpacing(nsTextFrame*,const nsStyleText& s){return s.mLetterSpacing.value;}
static bool IsInBounds(const gfxSkipCharsIterator& it,int length,Range r){return r.start>=it.pos&&(length==INT32_MAX||r.end<=it.pos+length);}
static void FindClusterStart(const gfxTextRun*,int,gfxSkipCharsIterator*){}
static void FindClusterEnd(const gfxTextRun*,int,gfxSkipCharsIterator*){}
static Maybe<TextAutospace::CharClass> LastNonMarkCharClass(gfxSkipCharsIterator&,int,const gfxTextRun*,const CharacterDataBuffer&){return {};}
static Maybe<TextAutospace::CharClass> GetPrecedingCharClassFromFrameTree(nsTextFrame*){return {};}
static Maybe<TextAutospace::CharClass> GetPrecedingCharClassFromMappedFlows(nsTextFrame*,const gfxTextRun*){return {};}
static bool HasCJKGlyphRun(const gfxTextRun*){return false;}
static bool IsCSSWordSpacingSpace(const CharacterDataBuffer&,int,nsTextFrame*,const nsStyleText*){return false;}
static uint32_t FindStartAfterSkippingWhitespace(nsTextFrame::PropertyProvider*,InlineData*,const nsStyleText*,gfxSkipCharsIterator* it,uint32_t end){event(6,it->pos,end);return it->pos;}
static uint32_t GetEndOfTrimmedText(const CharacterDataBuffer&,const nsStyleText*,uint32_t,uint32_t end,gfxSkipCharsIterator*,bool=false){return end;}
static bool IsTrimmableSpace(const CharacterDataBuffer&,int,const nsStyleText*){return false;}
static bool IsUnreflowedLetterFrame(nsIFrame*){return firstLetter;}
@@CORE@@
void nsTextFrame::RemoveProperty(int){event(7);delete property;property=nullptr;}
@@MAIN@@
