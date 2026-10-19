import json
import re
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
full=helper['full'];strip=helper['strip'];OUT=ROOT/'development-build/full'
base=(ROOT/'provider-bridge-v1/development-build/provider/range-types-native.hpp').read_text()
base=base.replace('namespace nsTextFrameUtils{struct Flags{enum{NoBreaks=1,IsTransformed=2,HasTrailingBreak=4};};}', '')
a=base.index('struct gfxSkipChars {');b=base.index('struct gfxTextRun{',a)
headers='\n'.join(strip((ROOT/'source/providers'/rel).read_text())for rel in ['mfbt/BinarySearch.h','gfx/thebes/gfxSkipChars.h','gfx/thebes/gfxSkipChars.cpp'])
base=base[:a]+'#define MOZ_STACK_CLASS\n#define MOZ_UNLIKELY(x) (x)\nstruct CriticalError {template<class T>CriticalError&operator<<(T value){std::cerr<<value;return *this;}};inline CriticalError gfxCriticalError(){return {};}\n'+headers+'\n#include "transform-class.hpp"\ninline uint32_t operator&(uint32_t a,TextFlags b){return a&uint16_t(b);}\n'+base[b:]
base=base.replace('uint32_t flags=2;', 'uint32_t flags=uint16_t(TextFlags::IsTransformed);')
base=base.replace('void ClearFlagBits(uint32_t f){flags&=~f;}void SetFlagBits(uint32_t f){flags|=f;}', 'void ClearFlagBits(TextFlags f){flags&=~uint16_t(f);}void SetFlagBits(TextFlags f){flags|=uint16_t(f);}')
base=base.replace('enum class StyleWordBreak{Normal,BreakAll,KeepAll};','namespace mozilla {enum class StyleWordBreak{Normal,BreakAll,KeepAll,BreakWord};enum class StyleWhiteSpaceCollapse{Collapse,Preserve,PreserveBreaks,PreserveSpaces,BreakSpaces};enum class StyleTextWrapMode{Wrap,NoWrap};}\nusing mozilla::StyleWordBreak;using mozilla::StyleWhiteSpaceCollapse;using mozilla::StyleTextWrapMode;\nstruct nsIFrame;')
base=base.replace('StyleWordBreak wordBreak=StyleWordBreak::Normal;','StyleWordBreak mWordBreak=StyleWordBreak::Normal;StyleWhiteSpaceCollapse mWhiteSpaceCollapse=StyleWhiteSpaceCollapse::Collapse;StyleTextWrapMode mTextWrapMode=StyleTextWrapMode::Wrap;')
a=base.index(' StyleWordBreak EffectiveWordBreak()const');b=base.index('\n};',a)
style=ROOT/'source/providers/layout/style/nsStyleStruct.h'
methods='\n'.join(full(style,marker)for marker in ['mozilla::StyleWordBreak EffectiveWordBreak() const','bool WhiteSpaceIsSignificant() const','bool NewlineIsSignificantStyle() const','bool WhiteSpaceCanWrapStyle() const'])
base=base[:a]+methods+'\nbool WhiteSpaceCanWrap(const nsIFrame*)const;'+base[b:]
base=base.replace('struct nsIFrame{nsStyleText style;', 'struct ComputedStyle{bool combined=false;bool IsTextCombined()const{return combined;}};\nstruct nsIFrame{nsStyleText style;ComputedStyle computed;bool svg=false;bool IsInSVGTextSubtree()const{return svg;}const ComputedStyle*Style()const{return &computed;}')
base=base.replace('struct CharacterDataBuffer{std::u16string units;', 'struct CharacterDataBuffer{std::u16string units;bool wide=true;bool Is2b()const{return wide;}char16_t CharAt(size_t i)const{return units.at(i);}const char16_t*Get2b()const{return units.data();}')
base=base.replace('struct nsTextFrame:nsIFrame{','struct nsTextFrame:nsIFrame{\n enum class TextRunType{Inflated};\n nsIFrame* GetParent(){return nullptr;}gfxTextRun*GetTextRun(TextRunType){return nullptr;}\n int32_t GetContentLength()const{return std::max(0,std::min(next?next->offset:buffer->GetLength(),buffer->GetLength())-std::min(offset,buffer->GetLength()));}')
a=base.index('inline bool IsTrimmableSpace(');b=base.index('\n',a);base=base[:a]+base[b:]
frame=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp'
bidi=(ROOT/'source/providers/intl/unicharutil/util/nsBidiUtils.h').read_text();bidi=bidi[bidi.index('#define LRM_CHAR'):bidi.index('/**',bidi.index('inline bool IsBidiControl(uint32_t'))]
unicode='namespace mozilla::unicode {\n'+full(ROOT/'source/providers/intl/unicharutil/util/nsUnicodeProperties.cpp','bool IsClusterExtenderExcludingJoiners(uint32_t aCh, uint8_t aCategory)')+'\n'+full(ROOT/'source/providers/intl/unicharutil/util/nsUnicodeProperties.h','inline bool IsClusterExtenderExcludingJoiners(uint32_t aCh)')+'\n}\nusing namespace mozilla::unicode;\n'
extra=full(ROOT/'source/providers/layout/style/nsStyleStructInlines.h','bool nsStyleText::WhiteSpaceCanWrap(')+'\n#include "transform-body.hpp"\nconstexpr char16_t kOghamSpaceMark=0x1680;\n'+full(frame,'static bool IsSpaceCombiningSequenceTail(const CharacterDataBuffer&')+'\n'+full(frame,'static bool IsTrimmableSpace(const CharacterDataBuffer&')+'\n'
(OUT/'range-types-adapted.hpp').write_text(base+'\n'+extra)
(OUT/'range-provider-extraction.json').write_text(json.dumps(helper['records'],indent=2)+'\n')
