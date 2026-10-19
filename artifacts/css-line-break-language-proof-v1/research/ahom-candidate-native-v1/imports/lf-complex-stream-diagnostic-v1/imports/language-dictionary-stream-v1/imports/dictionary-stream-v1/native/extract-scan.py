import json,re,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
h=runpy.run_path(str(ROOT/'native/extract-full.py'));full=h['full'];source=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp';changes=[]
def once(text,before,after,name):
 assert text.count(before)==1,(name,text.count(before));changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
text=(OUT/'admission.cpp').read_text();text=text[:text.index('int main(){')]
text=once(text,'struct nsIFrame;struct nsTextFrame;','struct nsIFrame;struct nsTextFrame;enum class LayoutFrameType{Text,Inline,RubyTextContainer,Br,Placeholder,Atomic};enum class FrameChildListID{Overflow};struct FrameList{nsIFrame*first=nullptr;nsIFrame*FirstChild()const{return first;}};', 'frame topology declarations')
text=once(text,'struct nsIFrame{','struct nsIFrame{virtual~nsIFrame()=default;unsigned id=0;LayoutFrameType type=LayoutFrameType::Inline;uint64_t state=0;nsIFrame*sibling=nullptr;FrameList principal,overflow;bool canContinue=true;LayoutFrameType Type()const{return type;}bool HasAnyStateBits(uint64_t b)const{return state&b;}bool IsPlaceholderFrame()const{return type==LayoutFrameType::Placeholder;}bool IsRubyTextContainerFrame()const{return type==LayoutFrameType::RubyTextContainer;}bool CanContinueTextRun()const{return canContinue;}nsIFrame*GetNextSibling()const{return sibling;}FrameList PrincipalChildList()const{return principal;}FrameList GetChildList(FrameChildListID)const{return overflow;}', 'frame topology provider')
text=once(text,'struct CharacterDataBuffer{','struct CharacterDataBuffer{bool doubleByte=false;bool Is2b()const{return doubleByte;}int GetLength()const{return text.size();}', 'character storage encoding')
text=once(text,'struct nsTextFrame:nsIFrame{','struct nsTextFrame:nsIFrame{nsTextFrame*continuation=nullptr;uintptr_t run=0;int GetContentOffset()const{return start;}nsTextFrame*GetNextContinuation()const{return continuation;}void*GetTextRun(int)const{return reinterpret_cast<void*>(run);}', 'continuation and existing-run provider')
extra='\n#define NS_WARNING_ASSERTION(c,...) ((void)0)\nnamespace nsTextFrameUtils{constexpr uint32_t INCOMING_WHITESPACE=1;}\n'
bits=(ROOT/'source/providers/layout/generic/nsFrameStateBits.h').read_text()
for name in ['NS_FRAME_IS_FLUID_CONTINUATION','PLACEHOLDER_FOR_ABSPOS','PLACEHOLDER_FOR_FIXEDPOS']:
 bit=re.search(r'FRAME_STATE_BIT\([^,]+,\s*(\d+),\s*'+name+r'\)',bits)[1];extra+=f'constexpr uint64_t {name}=uint64_t(1)<<{bit};\n'
extra+='struct nsPlaceholderFrame:nsIFrame{nsIFrame*outOfFlow=nullptr;nsIFrame*GetOutOfFlowFrame()const{return outOfFlow;}};\n'
extra+='template<class T>struct FrameArray:std::vector<T>{size_t Length()const{return this->size();}T*AppendElement(){this->emplace_back();return &this->back();}void AppendElement(T t){this->push_back(t);}void Clear(){this->clear();}};\n'
scanner='class BuildTextRunsScanner{public:bool mBidiEnabled=false;bool ContinueTextRunAcrossFrames(nsTextFrame*,nsTextFrame*);};'
replacement='class BuildTextRunsScanner{public:bool mBidiEnabled=false,mDoubleByteText=false,mStartOfLine=true;uint32_t mMaxTextLength=0,mNextRunContextInfo=3,mCurrentRunContextInfo=0;int mWhichTextRun=0;nsTextFrame*mLastFrame=nullptr;nsIFrame*mCommonAncestorWithLastFrame=nullptr;void*mCurrentFramesAllSameTextRun=nullptr;FrameArray<nsTextFrame*>mLineBreakBeforeFrames;\n'
replacement+=full(source,'struct MappedFlow {',True)+'\nFrameArray<MappedFlow>mMappedFlows;\n'+full(source,'void ResetRunInfo()')+'\n'+full(source,'void LiftCommonAncestorWithLastFrameToParent(')+'\n'
replacement+='bool ContinueTextRunAcrossFrames(nsTextFrame*,nsTextFrame*);void ScanFrame(nsIFrame*);void AccumulateRunInfo(nsTextFrame*);void FlushFrames(bool,bool);std::string Snapshot()const;std::vector<std::string>flushes;};\n'
text=once(text,scanner,extra+replacement,'complete scanner state projection')
for marker,semi in [('struct FrameTextTraversal {',True),('static FrameTextTraversal CanTextCrossFrameBoundary(',False),('void BuildTextRunsScanner::AccumulateRunInfo(',False),('void BuildTextRunsScanner::ScanFrame(',False)]:text+=full(source,marker,semi)+'\n'
text+=(ROOT/'native/scan-runner.cpp').read_text()
(OUT/'scan.cpp').write_text(text)
(OUT/'scan-extraction.json').write_text(json.dumps({'functions':h['records'],'adaptations':changes,'scope':'Complete ScanFrame, AccumulateRunInfo, FrameTextTraversal/CanTextCrossFrameBoundary, ResetRunInfo and ancestor lifting joined to complete native continuation admission. FlushFrames is a recording/reset provider here; complete real construction/reuse/flush is covered by the separate lifecycle bridge, not silently inferred from this caller projection. Frame topology/CanContinueTextRun and style primitives remain explicit providers.'},indent=2)+'\n')
