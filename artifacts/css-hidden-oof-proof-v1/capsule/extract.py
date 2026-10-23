import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def unit(text, signature):
    if text.count(signature) != 1:
        raise ValueError('Nonunique signature: ' + signature)
    start = text.index(signature)
    brace = text.index('{', start)
    depth, mode, i = 0, 'code', brace
    while i < len(text):
        c, pair = text[i], text[i:i + 2]
        if mode == 'line':
            if c == '\n': mode = 'code'
        elif mode == 'block':
            if pair == '*/': mode, i = 'code', i + 1
        elif mode in ('"', "'"):
            if c == '\\': i += 1
            elif c == mode: mode = 'code'
        elif pair == '//': mode, i = 'line', i + 1
        elif pair == '/*': mode, i = 'block', i + 1
        elif c in ('"', "'"): mode = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1] + (';' if text[i + 1:i + 2] == ';' else '')
        i += 1
    raise ValueError('Unclosed source unit')

ROLES = [
 ('overflow_overload', 'native-frame.h', 'bool FinishAndStoreOverflow(ReflowOutput*'),
 ('overflow_body', 'native-frame.cpp', 'bool nsIFrame::FinishAndStoreOverflow(OverflowAreas&'),
 ('output_ctor', 'native-reflow-output.cpp', 'ReflowOutput::ReflowOutput(const ReflowInput& aReflowInput)'),
 ('output_wm_ctor', 'native-reflow-output.h', 'explicit ReflowOutput(WritingMode aWritingMode)'),
 ('logical_zero_ctor', 'native-writing-modes.h', 'explicit LogicalSize(WritingMode aWritingMode)'),
 ('mark', 'native-frame.cpp', 'void nsIFrame::MarkSubtreeDirty()'),
 ('hides', 'native-frame.cpp', 'bool nsIFrame::HidesContentForLayout() const'),
 ('hidden', 'native-frame.cpp', 'bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const'),
 ('parent', 'native-frame-inlines.h', 'nsContainerFrame* nsIFrame::GetInFlowParent() const'),
 ('did', 'native-frame.cpp', 'void nsIFrame::DidReflow('),
 ('query', 'native-pres-shell.cpp', 'void PresShell::UpdateHiddenContentInForcedLayout('),
 ('forcing', 'native-pres-shell.cpp', 'bool PresShell::IsForcingLayoutForHiddenContent('),
 ('resize', 'native-reflow-input.cpp', 'void ReflowInput::InitResizeFlags('),
 ('block', 'native-block.cpp', 'void nsBlockFrame::Reflow('),
 ('original', 'original.cpp', 'void AbsoluteContainingBlock::ReflowAbsoluteFrame('),
 ('candidate', 'candidate.cpp', 'void AbsoluteContainingBlock::ReflowAbsoluteFrame('),
]

def extract():
 values, bindings = {}, []
 for name, file, signature in ROLES:
  path = ROOT / 'input' / file
  value = unit(path.read_text(), signature)
  values[name] = value
  bindings.append({'name': name, 'source': file, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'signature': signature, 'unit_sha256': hashlib.sha256(value.encode()).hexdigest(), 'kind': 'complete unit bound; only mark/hides/hidden/parent/query/forcing execute whole'})
 selected = {
 'mark_guard': ('candidate', 'if (aKidFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout())'),
 'did_guard': ('did', 'if (IsHiddenByContentVisibilityOfInFlowParentForLayout())'),
 'block_guard': ('block', 'if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&'),
 }
 for name, (source, signature) in selected.items():
  values[name] = unit(values[source], signature)
  bindings.append({'name':name,'source_unit':source,'unit_sha256':hashlib.sha256(values[name].encode()).hexdigest(),'kind':'exact branch executes under facade'})
 spans = {
 'resize_statement': ('resize', 'SetIResize(!mFrame->HasAnyStateBits(NS_FRAME_IS_DIRTY) && isIResize);'),
 'did_clear': ('did', 'RemoveStateBits(NS_FRAME_IN_REFLOW | NS_FRAME_FIRST_REFLOW |\n                  NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN);'),
 'input_construct': ('candidate', 'ReflowInput kidReflowInput(aPresContext, aReflowInput, aKidFrame,\n                               availSize.ConvertTo(wm, outerWM),\n                               Some(cbSize.ConvertTo(wm, outerWM)), initFlags,\n                               sizeOverrides, {}, aAnchorPosResolutionCache);'),
 'output_call': ('candidate', 'ReflowOutput kidDesiredSize(kidReflowInput);\n    aKidFrame->Reflow(aPresContext, kidDesiredSize, kidReflowInput, aStatus);'),
 'set_rect': ('candidate', 'aKidFrame->SetRect(r);'),
 'did_call': ('candidate', 'aKidFrame->DidReflow(aPresContext, &kidReflowInput);'),
 }
 for name,(source,span) in spans.items():
  if values[source].count(span)!=1:raise ValueError('Nonunique span '+name)
  values[name]=span
  bindings.append({'name':name,'source_unit':source,'unit_sha256':hashlib.sha256(span.encode()).hexdigest(),'kind':'exact statements execute; neighboring providers supplied'})
 if not values['candidate'].index(values['mark_guard']) < values['candidate'].index(values['input_construct']) < values['candidate'].index(values['output_call']) < values['candidate'].index(values['set_rect']) < values['candidate'].index(values['did_call']):raise ValueError('source ordering')
 return values,bindings

def generate(mutant='none'):
 v,_=extract()
 if mutant=='omit_mark':v['mark_guard']=v['mark_guard'].replace('aKidFrame->MarkSubtreeDirty();','(void)0;')
 elif mutant=='root_only':v['mark_guard']=v['mark_guard'].replace('aKidFrame->MarkSubtreeDirty();','aKidFrame->AddStateBits(NS_FRAME_IS_DIRTY);')
 elif mutant=='physical_parent':v['parent']='nsContainerFrame* nsIFrame::GetInFlowParent() const { return GetParent(); }'
 elif mutant=='ignore_anon':v['hidden']=v['hidden'].replace('!(parent->HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES) &&\n           Style()->IsAnonBox())','true')
 elif mutant=='clear_hidden_dirty':v['did_guard']=v['did_guard'].replace('RemoveStateBits(NS_FRAME_IN_REFLOW);','RemoveStateBits(NS_FRAME_IN_REFLOW | NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN);')
 elif mutant=='skip_continuations':v['block_guard']=v['block_guard'].replace('!GetNextContinuation()','true')
 elif mutant=='query_clean':v['query']=v['query'].replace('!aFrame || !aFrame->IsSubtreeDirty()','!aFrame')
 elif mutant not in ('none','late_mark'):raise ValueError(mutant)
 pre = 'if (timing == 1) {'+v['mark_guard']+'}'
 late = 'if (timing == 2) {'+v['mark_guard']+'}'
 if mutant=='late_mark':pre='';late='if (timing == 1 || timing == 2) {'+v['mark_guard']+'}'
 wrapper = """
 bool Execute(int timing, nsIFrame* aKidFrame) {
 void* aPresContext = nullptr;
 ReflowInput aReflowInput;
 const int outerWM = 0, wm = 0, initFlags = 0;
 const LogicalSize cbSize(outerWM, 12000, 4800), availSize(outerWM, 12000, 4800);
 StyleSizeOverrides sizeOverrides;
 void* aAnchorPosResolutionCache = nullptr;
 int aStatus = 0;
 """+pre+'\n'+v['input_construct']+'\n'+late+'\n'+v['output_call']+"""
 Rect r{600+(12000-kidDesiredSize.width)/2,600,kidDesiredSize.width,kidDesiredSize.height};
 """+v['set_rect']+'\n'+v['did_call']+'\nreturn kidReflowInput.iResize;\n}'
 return '\n'.join([(ROOT/'facade-prefix.cpp').read_text()]+[v[n] for n in ['mark','hides','hidden','parent','query','forcing']]+[
 'void ReflowInput::InitResizeFlag(bool isIResize) {'+v['resize_statement']+'}',
 'void nsIFrame::Reflow(void*, ReflowOutput& aMetrics, const ReflowInput& aReflowInput, int&) {'+v['block_guard']+'\naMetrics.width=720; aMetrics.height=480;\n}',
 'void nsIFrame::DidReflow(void*, const ReflowInput*) {'+v['did_guard']+'\n'+v['did_clear']+'}',wrapper,(ROOT/'facade-main.cpp').read_text()])

if __name__ == '__main__':
 print(json.dumps(extract()[1],indent=2))
