import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full'];changes=[]
def once(text,before,after,name):
 n=text.count(before);assert n==1,(name,n);changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
base=(OUT/'context-types.hpp').read_text()
base=once(base,'int mTextTransform=0;','TransformStyle mTextTransform;StyleTextSecurity mWebkitTextSecurity=StyleTextSecurity::None;StyleTextAlign mTextAlign=StyleTextAlign::Start,mTextAlignLast=StyleTextAlign::Start;bool HasEffectiveTextEmphasis()const{return false;}char16_t TextSecurityMaskChar()const{return 0;}', 'text-style font provider')
base=once(base,'struct nsStyleFont{','struct nsStyleFont{StyleMathVariant mMathVariant=StyleMathVariant::None;', 'font variant')
base=once(base,'struct ComputedStyle{bool combined=false;bool IsTextCombined()const{return combined;}};','struct ComputedStyle{bool combined=false;const nsStyleText*text=nullptr;const nsStyleFont*font=nullptr;bool IsTextCombined()const{return combined;}const nsStyleText*StyleText()const{return text;}const nsStyleFont*StyleFont()const{return font;}};', 'computed style')
base=once(base,'ComputedStyle computed;','mutable ComputedStyle computed;nsIFrame*parent=nullptr;nsIContent*content=nullptr;uint64_t state=0;nsIFrame*GetParent()const{return parent;}nsIContent*GetContent()const{return content;}bool HasAnyStateBits(uint64_t bits)const{return state&bits;}', 'frame tree provider')
base=once(base,'const ComputedStyle*Style()const{return &computed;}','ComputedStyle*Style()const{computed.text=&style;return &computed;}', 'style getter')
base=once(base,'struct CharacterDataBuffer{','struct CharacterDataBuffer{nsIContent content;', 'content identity')
base=once(base,'enum class TextRunType{Inflated};','enum class TextRunType{Inflated,NotInflated};static constexpr TextRunType eNotInflated=TextRunType::NotInflated;ComputedStyle*Style()const{auto*p=nsIFrame::Style();p->font=&font;return p;}nsIContent*GetContent()const{return &buffer->content;}gfx::ShapedTextFlags GetSpacingFlags()const{return {};}nsPresContext*PresContext()const{static nsPresContext pc;return &pc;}BidiLevel GetEmbeddingLevel()const{return {};}size_t CountGraphemeClusters()const{return GetContentLength();}', 'text frame providers')
base=once(base,'nsIFrame* GetParent(){return nullptr;}','nsIFrame* GetParent(){return parent;}', 'parent field')
base=once(base,'gfxSkipChars skip;','void*userData=nullptr;gfx::ShapedTextFlags shapeFlags{};gfx::ShapedTextFlags GetFlags()const{return shapeFlags;}void SetUserData(void*p){userData=p;}void*GetUserData()const{return userData;}gfxSkipChars skip;', 'run properties')
pre=(ROOT/'native/fresh-pre.hpp').read_text()
a=pre.index('enum class ShapedTextFlags');b=pre.index('};',a)+2
pre=pre[:a]+full(ROOT/'provider-bridge-v1/source/providers/gfx/thebes/gfxFont.h','enum class ShapedTextFlags : uint16_t',True)+pre[b:]
(OUT/'fresh-types.hpp').write_text(pre+base+(ROOT/'native/fresh-post.hpp').read_text())
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'context-{flavor}.cpp').read_text()
 text=once(text,'#include "context-types.hpp"','#include "fresh-types.hpp"',flavor+' types')
 text=once(text,'explicit already_AddRefed(T* value)','already_AddRefed(T* value)',flavor+' already ref transfer')
 text=once(text,'RefPtr& operator=(T*x){p=x;return *this;}','RefPtr& operator=(T*x){p=x;return *this;}T*forget(){return std::exchange(p,nullptr);}',flavor+' RefPtr forget facade')
 context_runner=(ROOT/'native/range-runner.cpp').read_text().replace('scanner.SetupBreakSinksForTextRun(&run,encoding==16?static_cast<const void*>(transformed.data()):static_cast<const void*>(bytes.data()));','assert(scanner.SetupLineBreakerContext(&run));')
 assert text.endswith(context_runner);text=text[:-len(context_runner)]
 members='\nbool mDoLineBreaking=true,mBidiEnabled=false;\nuint8_t mCurrentRunContextInfo=0;\nalready_AddRefed<gfxTextRun>BuildTextRunForFrames(void*);\nnsTextFrame*GetNextBreakBeforeFrame(uint32_t*i){return *i<mLineBreakBeforeFrames.Length()?mLineBreakBeforeFrames[(*i)++]:nullptr;}\nvoid AssignTextRun(gfxTextRun*,float){}\nvoid SetupTextEmphasisForTextRun(gfxTextRun*,const void*){}\n'
 text=once(text,'uint8_t mNextRunContextInfo=0;','uint8_t mNextRunContextInfo=0;'+members,flavor+' fresh members')
 source=ROOT/f'source/{flavor}/layout/generic/nsTextFrame.cpp'
 text+='\n'+full(source,'static bool IsLineBreakingWhiteSpace(')+'\n'+full(source,'static bool TextContainsLineBreakerWhiteSpace(')+'\n'+full(source,'already_AddRefed<gfxTextRun> BuildTextRunsScanner::BuildTextRunForFrames(')+'\n'
 runner=(ROOT/'native/range-runner.cpp').read_text().replace('run.','referenceRun.').replace('nsTransformedTextRun run;','nsTransformedTextRun referenceRun;')
 original='scanner.SetupBreakSinksForTextRun(&run,encoding==16?static_cast<const void*>(transformed.data()):static_cast<const void*>(bytes.data()));'
 replacement='std::vector<char16_t> buildBuffer(scanner.mMaxTextLength+1);auto*created=scanner.BuildTextRunForFrames(buildBuffer.data()).take();assert(created);auto&run=*static_cast<nsTransformedTextRun*>(created);'
 runner=once(runner,original,replacement,flavor+' full fresh constructor')
 a=runner.index('std::vector<unsigned> offsets;');runner=runner[:a]+runner[a:].replace('referenceRun.','run.')
 (OUT/f'fresh-{flavor}.cpp').write_text(text+runner)
(OUT/'fresh-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptations':changes,'status':'development opaque font/DOM/frame allocation effects; not full shaping or assignment refinement'},indent=2)+'\n')
