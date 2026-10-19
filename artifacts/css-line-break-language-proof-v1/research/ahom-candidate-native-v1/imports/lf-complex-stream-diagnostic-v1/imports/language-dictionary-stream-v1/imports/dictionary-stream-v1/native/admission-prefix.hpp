#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>
#define MOZ_ASSERT(c,...) assert(c)
#define NS_ASSERTION(c,...) assert(c)
#define MOZ_ASSERT_UNREACHABLE(...) assert(false)
using nscoord=int;
template<class T,class U>T AssertedCast(U x){return static_cast<T>(x);}
enum class Side{Top,Right,Bottom,Left};
enum class LogicalSide{IStart,IEnd};
enum class StyleUnicodeBidi{Normal,Isolate,IsolateOverride};
enum class StyleAlignmentBaseline{Baseline,Other};
enum class StyleTextJustify{Auto,InterCharacter};
enum class StyleMozControlCharacterVisibility{Visible,Hidden};
enum class StyleTextRendering{Auto,Optimizespeed,Other};
enum class StyleWritingModeProperty{HorizontalTb,VerticalLr,VerticalRl,SidewaysLr,SidewaysRl};
enum class StyleTextOrientation{Mixed,Upright,Sideways};
struct nsIFrame;struct nsTextFrame;
struct Value{int value=0;bool converts=true,keyword=false;bool ConvertsToLength()const{return converts;}const Value&AsLengthPercentage()const{return *this;}int ToLength()const{return value;}bool IsKeyword()const{return keyword;}const Value&AsLength()const{return *this;}bool IsDefinitelyZero()const{return value==0;}template<class F>int Resolve(F)const{return value;}};
struct Sides{Value values[4];const Value&Get(Side s)const{return values[int(s)];}};
struct AnchorPosResolutionParams{static int From(const nsIFrame*){return 0;}};
struct nsStyleMargin{Sides values;const Value*GetMargin(Side s,int)const{return &values.Get(s);}};
struct nsStylePadding{Sides mPadding;};
struct nsStyleBorder{int values[4]{};int GetComputedBorderWidth(Side s)const{return values[int(s)];}};
struct nsStyleDisplay{StyleAlignmentBaseline mAlignmentBaseline=StyleAlignmentBaseline::Baseline;Value mBaselineShift;};
struct nsStyleTextReset{StyleUnicodeBidi mUnicodeBidi=StyleUnicodeBidi::Normal;};
struct nsStyleVisibility{StyleWritingModeProperty mWritingMode=StyleWritingModeProperty::HorizontalTb;StyleTextOrientation mTextOrientation=StyleTextOrientation::Mixed;};
struct nsStyleText{int mTextTransform=0,wordBreak=0,mLineBreak=0;int hyphenLimit=5;bool newline=false;Value mLetterSpacing;StyleTextJustify mTextJustify=StyleTextJustify::Auto;StyleMozControlCharacterVisibility mMozControlCharacterVisibility=StyleMozControlCharacterVisibility::Visible;StyleTextRendering mTextRendering=StyleTextRendering::Auto;int EffectiveWordBreak()const{return wordBreak;}bool NewlineIsSignificantStyle()const{return newline;}bool NewlineIsSignificant(const nsTextFrame*)const;};
struct Size{int value=16;float ToCSSPixels()const{return value;}int ToAppUnits()const{return value*60;}bool operator==(const Size&)const=default;};
struct Font{Size size;int identity=0;bool operator==(const Font&)const=default;};
struct nsStyleFont{Font mFont;Size mSize;int mLanguage=0;};
struct ComputedStyle{nsStyleText text;nsStyleFont font;nsStyleVisibility visibility;nsStyleMargin margin;nsStylePadding padding;nsStyleBorder border;nsStyleDisplay display;nsStyleTextReset reset;bool rtl=false,combined=false;const nsStyleText*StyleText()const{return &text;}const nsStyleFont*StyleFont()const{return &font;}const nsStyleVisibility*StyleVisibility()const{return &visibility;}const nsStyleMargin*StyleMargin()const{return &margin;}const nsStylePadding*StylePadding()const{return &padding;}const nsStyleBorder*StyleBorder()const{return &border;}const nsStyleTextReset*StyleTextReset()const{return &reset;}bool IsTextCombined()const{return combined;}};
struct WritingMode{const ComputedStyle*style;explicit WritingMode(const ComputedStyle*s):style(s){}bool operator!=(const WritingMode&o)const{return style->visibility.mWritingMode!=o.style->visibility.mWritingMode||style->rtl!=o.style->rtl;}bool IsBidiLTR()const{return !style->rtl;}Side PhysicalSide(LogicalSide s)const{bool end=s==LogicalSide::IEnd;bool rtl=style->rtl;if(style->visibility.mWritingMode==StyleWritingModeProperty::HorizontalTb)return end!=rtl?Side::Right:Side::Left;bool reverse=style->visibility.mWritingMode==StyleWritingModeProperty::SidewaysLr;return (end!=rtl)!=reverse?Side::Bottom:Side::Top;}};
struct nsPresContext{float DevPixelsToFloatCSSPixels(float v)const{return v;}};
namespace StaticPrefs{inline int browser_display_auto_quality_min_font_size(){return 20;}}
struct FrameBidiData{int embeddingLevel=0,precedingControl=-1;};
constexpr int kBidiLevelNone=-1;
struct BidiLevel{int level=0;bool IsRTL()const{return level%2;}};
struct CharacterDataBuffer{std::u16string text;char16_t CharAt(unsigned i)const{return text.at(i);}};
struct nsIFrame{nsIFrame*parent=nullptr;ComputedStyle*style=nullptr;uintptr_t content=0;bool block=false,svg=false;float svgScale=1;nsIFrame*GetParent()const{return parent;}ComputedStyle*Style()const{return style;}uintptr_t GetContent()const{return content;}bool IsBlockFrameOrSubclass()const{return block;}bool IsInSVGTextSubtree()const{return svg;}const nsStyleDisplay*StyleDisplay()const{return &style->display;}const nsStyleFont*StyleFont()const{return style->StyleFont();}};
struct nsTextFrame:nsIFrame{nsTextFrame*next=nullptr;FrameBidiData bidi;::CharacterDataBuffer*buffer=nullptr;unsigned start=0,end=0;bool suppress=false;nsPresContext*context=nullptr;FrameBidiData GetBidiData()const{return bidi;}BidiLevel GetEmbeddingLevel()const{return {bidi.embeddingLevel};}const nsStyleText*StyleText()const{return style->StyleText();}nsTextFrame*GetNextInFlow()const{return next;}nsPresContext*PresContext()const{return context;}unsigned GetContentLength()const{return end-start;}unsigned GetContentEnd()const{return end;}const ::CharacterDataBuffer&CharacterDataBuffer()const{return *buffer;}bool ShouldSuppressLineBreak()const{return suppress;}};
inline float GetSVGFontSizeScaleFactor(nsIFrame*f){return f->svgScale;}
class BuildTextRunsScanner{public:bool mBidiEnabled=false;bool ContinueTextRunAcrossFrames(nsTextFrame*,nsTextFrame*);};
