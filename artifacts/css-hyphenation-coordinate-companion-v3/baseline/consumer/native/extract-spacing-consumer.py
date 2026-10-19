import hashlib,json,runpy,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'development-build/full'
TARGET=OUT/'spacing-consumer'
TARGET.mkdir(parents=True,exist_ok=True)
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
full=helper['full']
tab=runpy.run_path(str(ROOT/'imports/tab-zero-v2-source/extract.py'))
source=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp'
header=ROOT/'source/providers/layout/generic/nsTextFrame.h'
changes=[]
def once(text,old,new,name):
 assert text.count(old)==1,(name,text.count(old))
 changes.append(dict(name=name,before=old,after=new))
 return text.replace(old,new)
# Whole provider bodies are taken from candidate4, including its existing tab repair.
adapter=(ROOT/'imports/tab-zero-v2-source/adapter.cpp').read_text()
start=adapter.index('namespace mozilla {')
adapter=adapter[start:]
start=adapter.index('struct gfxSkipCharsIterator {')
end=adapter.index('struct Metrics {',start)
adapter=adapter[:start]+adapter[end:]
start=adapter.index('struct gfxTextRun {')
end=adapter.index('namespace nsTextFrameUtils {',start)
metrics=(OUT/'metric-providers/metric-declarations.hpp').read_text()
metrics=once(metrics,'struct DrawTarget{};','struct DrawTarget{};','draw target retained')
extra='\n bool IsRightToLeft()const{return rtl;}bool IsVertical()const{return vertical;}\n bool rtl=false,vertical=false;gfxFontGroup*group=nullptr;\n gfxFontGroup*GetFontGroup()const{assert(group);return group;}\n double GetAppUnitsPerDevUnit()const{return 1;}\n bool CharIsTab(uint32_t i)const{return glyphs.at(i).CharIsTab();}\n bool IsClusterStart(uint32_t i)const{return glyphs.at(i).IsClusterStart();}\n gfx::ShapedTextFlags GetFlags()const{return mFlags;}\n nsTextFrameUtils::Flags GetFlags2()const{return hasTab?nsTextFrameUtils::Flags::HasTab:nsTextFrameUtils::Flags{};}\n bool hasTab=false;\n double GetAdvanceWidth(Range range,PropertyProvider*provider=nullptr)const{\n  std::vector<PropertyProvider::Spacing> spacing(range.Length());if(provider)provider->GetSpacing(range,spacing.data());\n  double value=0;for(auto i=range.start;i<range.end;i++)value+=GetAdvanceForGlyph(i,provider?provider->LetterSpacing():0)+spacing[i-range.start].mBefore+spacing[i-range.start].mAfter;return value;\n }\n double GetAdvanceWidth()const{return GetAdvanceWidth(Range(0,GetLength()));}\n'
metrics=once(metrics,' uint32_t GetLength()const{return glyphs.size();}',extra+' uint32_t GetLength()const{return glyphs.size();}','spacing run provider surface')
metrics=once(metrics,'  uint32_t mValue=0;',full(ROOT/'provider-bridge-v1/source/providers/gfx/thebes/gfxFont.h','bool CharIsFormattingControl() const')+'\n  uint32_t mValue=0;','formatting flag accessor')
adapter=adapter[:start]+metrics+adapter[end:]
start=adapter.index('namespace nsTextFrameUtils {struct Flags')
end=adapter.index('struct nsIFrame;',start)
adapter=adapter[:start]+adapter[end:]
adapter=once(adapter,'enum class StyleHyphens {None,Auto,Manual};','', 'actual hyphens enum')
adapter=once(adapter,'namespace gfx {struct ShapedTextFlags {static constexpr int TEXT_ENABLE_HYPHEN_BREAKS=1;};}','', 'actual shaped flags')
adapter=once(adapter,'using gfx=mozilla::gfx;','using gfx=mozilla::gfx;','unused marker') if 'using gfx=mozilla::gfx;' in adapter else adapter
assert adapter.count('namespace gfx=mozilla::gfx;')==2
adapter=adapter.replace('namespace gfx=mozilla::gfx;','',1)
adapter=once(adapter,'namespace intl {struct UnicodeProperties {static bool IsCursiveScript(char32_t){return false;}};}','', 'actual Unicode namespace')
old=tab['complete'](adapter,'class CharacterDataBuffer {',True)[0]
char=full(ROOT/'source/providers/dom/base/CharacterDataBuffer.h','[[nodiscard]] char16_t CharAt(')
new='class CharacterDataBuffer {public: struct {bool mIs2b=true;uint32_t mLength=0;}mState; const char16_t*m2b=nullptr;const char*m1b=nullptr;uint32_t GetLength()const{return mState.mLength;}bool Is2b()const{return mState.mIs2b;}const char16_t*Get2b()const{assert(Is2b());return m2b;}'+char+'char32_t ScalarValueAt(int i)const{auto c=CharAt(i);if(mozilla::IsHighSurrogate(c)&&i+1<int(GetLength())&&mozilla::IsLowSurrogate(CharAt(i+1)))return mozilla::SurrogateToUCS4(c,CharAt(i+1));return c;}};'
adapter=once(adapter,old,new,'content storage and scalar boundary')
adapter=once(adapter,'struct nsIFrame;\nenum class StyleOverflowWrap', 'struct nsIFrame;\nenum class StyleOverflowWrap','style order retained')
adapter=once(adapter,' bool WhiteSpaceCanWrap(nsIFrame*)const{return wrap;}', ' mozilla::StyleTextWrapMode mTextWrapMode=mozilla::StyleTextWrapMode::Wrap; bool WhiteSpaceCanWrap(const nsIFrame*)const;'+full(ROOT/'source/providers/layout/style/nsStyleStruct.h','bool WhiteSpaceCanWrapStyle() const'), 'actual wrap providers')
adapter=once(adapter,'struct ComputedStyle {', 'struct ComputedStyle {','computed style retained')
adapter=once(adapter,' nsStyleText text;ComputedStyle style;', ' nsStyleText text;ComputedStyle style;bool svg=false;uint64_t state=0;bool IsInSVGTextSubtree()const{return svg;}bool HasAnyStateBits(uint64_t b)const{return state&b;}', 'svg and frame state')
adapter=once(adapter,' gfxTextRun run;::CharacterDataBuffer buffer;', ' gfxTextRun run;::CharacterDataBuffer buffer;', 'frame stores retained')
adapter=once(adapter,'int GetContentLength()const{return run.logicalLength;}int GetInFlowContentLength()const{return run.logicalLength;}', 'int GetContentLength()const{return buffer.GetLength()-contentOffset;}int GetInFlowContentLength()const{return GetContentLength();}', 'explicit content range')
adapter=once(adapter,'bool IsInSVGTextSubtree()const{return false;}','bool IsInSVGTextSubtree()const{return svg;}', 'svg forwarding')
start=adapter.index(' gfxSkipCharsIterator EnsureTextRun(');end=adapter.index('\n',start);adapter=adapter[:start]+adapter[end:]
adapter=once(adapter,' void GetHyphenationBreaks(Range,HyphenType*)const{assert(false);}', ' void GetHyphenationBreaks(Range,HyphenType*)const override;','complete hyphen provider declaration')
adapter=once(adapter,' gfxFloat GetHyphenWidth()const{return 0;}', ' gfxFloat GetHyphenWidth()const override{return 1+mLetterSpacing;}\n gfx::ShapedTextFlags GetShapedTextFlags()const override{return {};}already_AddRefed<DrawTarget>GetDrawTarget()const override{return {};}uint32_t GetAppUnitsPerDevUnit()const override{return 1;}StyleHyphens GetHyphensOption()const override{return mTextStyle->mHyphens;}','remaining metric provider boundary')
adapter=once(adapter,' PropertyProvider(nsTextFrame*,const gfxSkipCharsIterator&,TextRunType,nsFontMetrics*);', ' PropertyProvider(nsTextFrame*,const gfxSkipCharsIterator&,TextRunType,nsFontMetrics*);\n PropertyProvider(gfxTextRun*r,nsTextFrame*f,const class CharacterDataBuffer&b,const gfxSkipCharsIterator&s,int32_t n):PropertyProvider(r,f->StyleText(),b,f,s,n,nullptr,0,eInflated,false){}','fixed fixture adapter entry')
# Keep unresolved autospace/frame-tree/font helpers explicitly supplied; full spacing body still executes.
start=adapter.index('static uint32_t FindStartAfterSkippingWhitespace(');end=adapter.index('@@CORE@@',start);adapter=adapter[:start]+adapter[end:]
adapter=once(adapter,'static bool IsInBounds(const gfxSkipCharsIterator& it,int length,Range r){return r.start>=it.pos&&(length==INT32_MAX||r.end<=it.pos+length);}',full(source,'static bool IsInBounds('),'actual bounds helper')
adapter=once(adapter,'@@NUMERIC@@','', 'numeric old marker') if '@@NUMERIC@@' in adapter else adapter
numeric='\n'.join(full(ROOT/'imports/tab-zero-v2-source/source'/name,marker) for name,markers in tab['NUMERIC'].items() for marker in markers)
accessors='\n'.join(full(header,marker) for marker in tab['ACCESSORS'])
h=header.read_text();i=h.index('    const RefPtr<gfxTextRun> mTextRun;');j=h.index('\n  };',i);members=h[i:j]
core='\n'.join(full(source,marker,semi) for marker,semi in tab['FUNCTIONS'] if 'AddInline' not in marker)
core+='\n'+full(source,'static inline bool IS_HYPHEN(')+'\n'+full(source,'void nsTextFrame::PropertyProvider::GetHyphenationBreaks(')
for marker,value in [('@@ACCESSORS@@',accessors),('@@MEMBERS@@',members),('@@CORE@@',core),('@@MAIN@@','')]:adapter=once(adapter,marker,value,marker)
adapter=once(adapter,'static void FindClusterStart(const gfxTextRun*,int,gfxSkipCharsIterator*){}',full(source,'static void FindClusterStart('),'complete cluster start')
adapter=once(adapter,'static void FindClusterEnd(const gfxTextRun*,int,gfxSkipCharsIterator*){}',full(source,'static void FindClusterEnd('),'complete cluster end')
adapter=once(adapter,' bool IsClusterStart(uint32_t i)const{return glyphs.at(i).IsClusterStart();}', ' bool IsClusterStart(uint32_t i)const{return glyphs.at(i).IsClusterStart();}bool IsLigatureGroupStart(uint32_t i)const{return glyphs.at(i).IsLigatureGroupStart();}','ligature metadata')
adapter=once(adapter,'static bool IsCSSWordSpacingSpace(const CharacterDataBuffer&,int,nsTextFrame*,const nsStyleText*){return false;}',full(source,'static bool IsSpaceCombiningSequenceTail(')+'\n'+full(source,'static bool IsCSSWordSpacingSpace('),'complete word space admission')
adapter=once(adapter,'char32_t ScalarValueAt(int i)const{auto c=CharAt(i);if(mozilla::IsHighSurrogate(c)&&i+1<int(GetLength())&&mozilla::IsLowSurrogate(CharAt(i+1)))return mozilla::SurrogateToUCS4(c,CharAt(i+1));return c;}',full(ROOT/'source/providers/dom/base/CharacterDataBuffer.h','inline char32_t ScalarValueAt('),'complete scalar decoder')
adapter=once(adapter,'struct SpacingValue {int value=0;int Resolve(int)const{return value;}};', 'struct SpacingValue {int value=0;int Resolve(int)const{return value;}template<class F>int Resolve(F)const{return value;}};','resolved style value provider')
adapter=once(adapter,' const nsStyleText* StyleText()const{return &text;}', ' struct StyleFontValue{struct Size{int ToAppUnits()const{return 20;}}mSize;}fontStyle;const StyleFontValue*StyleFont()const{return &fontStyle;}\n const nsStyleText* StyleText()const{return &text;}','font-size provider')
adapter=once(adapter,'static int ResolveWordSpacing(nsTextFrame*,const nsStyleText& s){return s.mWordSpacing.value;}', 'static double GetSVGFontSizeScaleFactor(nsIFrame*){return 1;}\n'+full(source,'static nscoord ResolveWordSpacing('),'complete word spacing resolution')
adapter=once(adapter,'static int ResolveLetterSpacing(nsTextFrame*,const nsStyleText& s){return s.mLetterSpacing.value;}',full(source,'static nscoord ResolveLetterSpacing('),'complete letter spacing resolution')
adapter=once(adapter,'struct gfxFontGroup {Font font;Font* GetFirstValidFont(char){event(20);return &font;}};', 'struct gfxFontGroup {Font font;Font* GetFirstValidFont(char){event(20);return &font;}template<class P>double GetHyphenWidth(P*)const{return 1;}};','font hyphen width fixture boundary')
adapter=once(adapter,'struct nsStyleText {', 'struct nsStyleText {struct HyphenateChar{bool IsAuto()const{return true;}}mHyphenateCharacter;','hyphenate character fixture boundary')
adapter=once(adapter,' gfxFloat GetHyphenWidth()const override{return 1+mLetterSpacing;}', ' gfxFloat GetHyphenWidth()const override;gfxFontGroup*GetFontGroup()const{return mTextRun->GetFontGroup();}','native hyphen width declaration')
adapter+='\nstatic RefPtr<gfxTextRun>GetHyphenTextRun(nsTextFrame*,void*){assert(false);return nullptr;}\n'+full(source,'gfxFloat nsTextFrame::PropertyProvider::GetHyphenWidth(')+'\n'
prefix='#include <utility>\n#include <limits>\n#include <optional>\n#include <cmath>\n#include <climits>\n#define DEBUG 1\n#include "transform-native.hpp"\ninline constexpr int32_t nscoord_MAX=(1<<30)-1;\ninline constexpr int32_t nscoord_MIN=-nscoord_MAX;\nusing nscoord=int32_t;\nusing gfxFloat=double;\nstatic void event(long long,long long=0,long long=0){}\nstatic int letterModel=0;static bool failRun=false;\nnamespace mozilla {enum class StyleTextWrapMode{Wrap,NoWrap};}\ntemplate<class T> struct Maybe {std::optional<T>v;Maybe()=default;Maybe(T x):v(x){}explicit operator bool()const{return v.has_value();}T*operator->(){return &v.value();}const T*operator->()const{return &v.value();}T valueOr(T x)const{return v.value_or(x);}template<class F>T valueOrFrom(F f)const{return v?*v:f();}};\ntemplate<class T>Maybe<T>Some(T x){return Maybe<T>(x);}\n'
transform=(OUT/'transform-native.hpp').read_text()
transform=once(transform,'class UnicodeProperties { public:', 'class UnicodeProperties { public:\n'+full(ROOT/'source/providers/intl/components/src/UnicodeProperties.h','static bool IsCursiveScript('),'complete cursive script provider')
(TARGET/'transform-spacing.hpp').write_text(transform)
prefix=prefix.replace('#include "transform-native.hpp"','#include "transform-spacing.hpp"')
bit=re.search(r'FRAME_STATE_BIT\(Text,\s*(\d+),\s*TEXT_START_OF_LINE\)',(ROOT/'source/providers/layout/generic/nsFrameStateBits.h').read_text())[1]
prefix+='constexpr uint64_t TEXT_START_OF_LINE=uint64_t(1)<<'+bit+';\n'
prefix+='template<class A,class B>A AssertedCast(B x){assert(x>=0&&uint64_t(x)<=std::numeric_limits<A>::max());return A(x);}\n'
prefix+='inline nsTextFrameUtils::Flags operator&(nsTextFrameUtils::Flags a,nsTextFrameUtils::Flags b){return nsTextFrameUtils::Flags(uint32_t(a)&uint32_t(b));}inline bool operator!(nsTextFrameUtils::Flags a){return uint32_t(a)==0;}\n'
adapter=once(adapter,'bool NewlineIsSignificant(nsIFrame*)const','bool NewlineIsSignificant(const nsIFrame*)const','const style frame parameter')
prefix+='constexpr char16_t CH_NBSP=0x00a0;\n'
prefix+='inline bool IsSurrogate(uint32_t c){return mozilla::IsHighSurrogate(c)||mozilla::IsLowSurrogate(c); }\n'
prefix+=numeric+'\n'+full(ROOT/'source/providers/layout/generic/nsTextFrameUtils.h','class nsSkipCharsRunIterator {',True)+'\n'+full(ROOT/'source/providers/layout/generic/nsTextFrameUtils.cpp','bool nsSkipCharsRunIterator::NextRun(')+'\n'
prefix+='using Range = PLACEHOLDER;\n' if False else ''
# Complete measurement uses the same actual compressed glyph fields and detailed advances.
metric=(OUT/'metric-providers/hyphen-consumer.hpp').read_text();start=metric.index('gfxTextRun::LigatureData gfxTextRun::ComputeLigatureData(')
measurement=metric[start:]
adapter=once(adapter,'struct nsIFrame;\nenum class StyleOverflowWrap','using Range=gfxTextRun::Range;\nstruct nsIFrame;\nenum class StyleOverflowWrap','shared range alias')
wrap=full(ROOT/'source/providers/layout/style/nsStyleStructInlines.h','bool nsStyleText::WhiteSpaceCanWrap(')
(TARGET/'spacing.hpp').write_text(prefix+adapter+'\n'+wrap+'\n'+measurement)
runner=(ROOT/'native/hyphen-consumer-runner.cpp').read_text().replace('frame.style.','frame.text.').replace('frame.computed.','frame.style.')
runner=once(runner,'CharacterDataBuffer data;', 'run.group=&frame.fm.group;run.hasTab=!!(flags&nsTextFrameUtils::Flags::HasTab);CharacterDataBuffer data;','font and tab metadata fixture association')
runner=once(runner,"g.SetCanBreakBefore(mask==\"-\"?0:mask.at(i)-'0');", "g.SetCanBreakBefore(mask==\"-\"?0:mask.at(i)-'0');run.SetFixtureAdvance(i,1);",'complete detailed advance fixture')
(TARGET/'spacing.cpp').write_text('#include "spacing.hpp"\n'+runner)
(TARGET/'EXTRACTION.json').write_text(json.dumps({'records':helper['records'],'adaptations':changes,'status':'development full spacing integration; helper/font admission pending'},indent=2)+'\n')
