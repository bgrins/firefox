import json,re,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full'];changes=[]
def once(text,before,after,name):
 n=text.count(before);assert n==1,(name,n);changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
source=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp'
bits=(ROOT/'source/providers/layout/generic/nsFrameStateBits.h').read_text()
constants='using nsFrameState=uint64_t;template<class T>using DebugOnly=T;\n#define NS_ERROR(x) assert(false)\n'
for name in ['TEXT_HAS_FONT_INFLATION','TEXT_IN_TEXTRUN_USER_DATA','TEXT_IN_UNINFLATED_TEXTRUN_USER_DATA']:
 bit=re.search(r'FRAME_STATE_BIT\(Text, (\d+), '+name+r'\)',bits)[1]
 constants+=f'constexpr nsFrameState {name}=uint64_t(1)<<{bit};\n'
base=(OUT/'fresh-types.hpp').read_text()
base=constants+base
base=once(base,'static constexpr TextRunType eNotInflated=TextRunType::NotInflated;','static constexpr TextRunType eNotInflated=TextRunType::NotInflated,eInflated=TextRunType::Inflated;', 'inflated aliases')
base=once(base,'gfxTextRun*GetTextRun(TextRunType){return nullptr;}', 'gfxTextRun*mTextRun=nullptr;gfxTextRun*uninflated=nullptr;void*mFontMetrics=nullptr;float inflation=1;\ngfxTextRun*GetTextRun(TextRunType t)const{return t==eInflated||!HasFontSizeInflation()?mTextRun:uninflated;}\nbool HasFontSizeInflation()const{return HasAnyStateBits(TEXT_HAS_FONT_INFLATION);}\nvoid SetFontSizeInflation(float f){inflation=f;if(f==1)state&=~TEXT_HAS_FONT_INFLATION;else state|=TEXT_HAS_FONT_INFLATION;}\nstatic int UninflatedTextRunProperty(){return 0;}gfxTextRun*GetProperty(int)const{return uninflated;}void SetProperty(int,gfxTextRun*r){uninflated=r;}void RemoveProperty(int){uninflated=nullptr;}\nvoid AddStateBits(nsFrameState bits){state|=bits;}void RemoveStateBits(nsFrameState bits){state&=~bits;}bool IsTextFrame()const{return true;}\nvoid SetTextRun(gfxTextRun*,TextRunType,float);bool RemoveTextRun(gfxTextRun*);void ClearTextRun(nsTextFrame*,TextRunType);\n', 'frame lifecycle field facade')
base=once(base,'void*userData=nullptr;','uint32_t refs=1;void AddRef(){++refs;}void*userData=nullptr;', 'run reference boundary')
start=base.index('struct TextRunMappedFlow{');end=base.index('struct TextEditor{',start)
structs='\n'.join(full(source,m,True)for m in ['struct TextRunMappedFlow {','struct TextRunUserData {'])
structs+='\nstruct GlyphObserver{};struct SimpleTextRunUserData{nsTextFrame*mFrame;};\n'+full(source,'struct ComplexTextRunUserData :',True).replace('UniquePtr<','std::unique_ptr<')
structs+='\ninline void*moz_xmalloc(size_t n){auto*p=malloc(n);if(!p)std::abort();return p;}\n'
helpers='\n'.join(full(source,m)for m in ['static TextRunUserData* CreateUserData(','static void DestroyUserData(','static void DestroyComplexUserData(','static void DestroyTextRunUserData(','static TextRunMappedFlow* GetMappedFlows(','static nsTextFrame* GetFrameForSimpleFlow(','bool nsTextFrame::RemoveTextRun(','static bool ClearAllTextRunReferences(','static void UnhookTextRunFromFrames(','void nsTextFrame::ClearTextRun(','void nsTextFrame::SetTextRun(','static inline TextRunMappedFlow* FindFlowForContent('])
helpers=once(helpers,'  MOZ_ASSERT(\n      static_cast<TextRunUserData*>(aTextRun->GetUserData())->mMappedFlows ==\n          flows,\n      "GetMappedFlows should return the same pointer as mMappedFlows.");','', 'release-only debug metadata assertion')
base=base[:start]+structs+'\n'+helpers+'\n'+base[end:]
base+='\nstruct gfxPlatform{static gfxPlatform*GetPlatform(){static gfxPlatform p;return &p;}bool OpenTypeSVGEnabled()const{return false;}};\n'
(OUT/'lifecycle-types.hpp').write_text(base)
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'fresh-{flavor}.cpp').read_text()
 text=once(text,'#include "fresh-types.hpp"','#include "lifecycle-types.hpp"',flavor+' types')
 text=once(text,'T* take() { auto old=p;p=nullptr;return old; }','T* take() { auto old=p;p=nullptr;return old; }operator T*(){return take();}',flavor+' ownership-transfer facade')
 text=once(text,'void AssignTextRun(gfxTextRun*,float){}','void AssignTextRun(gfxTextRun*,float);',flavor+' full assignment')
 source=ROOT/f'source/{flavor}/layout/generic/nsTextFrame.cpp'
 members=full(source,'void ResetRunInfo(')+'\nbool mCanStopOnThisLine=false;AutoTArray<RefPtr<gfxTextRun>,8>mCreatedTextRuns;void FlushFrames(bool,bool);bool IsTextRunValidForMappedFlows(const gfxTextRun*);\n'
 text=once(text,'bool mDoLineBreaking=true,mBidiEnabled=false;',members+'bool mDoLineBreaking=true,mBidiEnabled=false;',flavor+' lifecycle members')
 marker='static std::string traceCase;';start=text.index(marker)
 runner=text[start:];text=text[:start]
 text+='\n'+'\n'.join(full(source,m)for m in ['bool BuildTextRunsScanner::IsTextRunValidForMappedFlows(','void BuildTextRunsScanner::AssignTextRun(','void BuildTextRunsScanner::FlushFrames('])+'\n'
 old='std::vector<char16_t> buildBuffer(scanner.mMaxTextLength+1);auto*created=scanner.BuildTextRunForFrames(buildBuffer.data()).take();assert(created);auto&run=*static_cast<nsTransformedTextRun*>(created);'
 new='scanner.FlushFrames(false,false);auto*created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);auto&run=*static_cast<nsTransformedTextRun*>(created);'
 runner=once(runner,old,new,flavor+' FlushFrames fresh entry')
 (OUT/f'lifecycle-{flavor}.cpp').write_text(text+runner)
(OUT/'lifecycle-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptations':changes,'status':'full fresh/reuse/assignment/unhook source; explicit frame/property/ordinary reference/font providers'},indent=2)+'\n')
