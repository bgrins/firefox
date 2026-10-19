import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full';h=runpy.run_path(str(ROOT/'native/extract-full.py'));full=h['full'];changes=[]
def once(text,before,after,name):
 assert text.count(before)==1,(name,text.count(before));changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
for flavor in ['original','candidate','standalone']:
 source=ROOT/f'source/{flavor}/layout/generic/nsTextFrame.cpp';text=(OUT/f'scan-lifecycle-{flavor}.cpp').read_text()
 text=once(text,'void SetLength(size_t count){','void EnsureLengthAtLeast(size_t count){if(n<count)SetLength(count);}void SetLength(size_t count){',flavor+' ensure scratch capacity')
 declarations=full(source,'struct FindBoundaryState {',True)+'\n'+full(source,'enum FindBoundaryResult {',True)+'\nFindBoundaryResult FindBoundaries(nsIFrame*,FindBoundaryState*);\n'
 text=once(text,'void ScanFrame(nsIFrame*);',declarations+'void ScanFrame(nsIFrame*);',flavor+' full boundary state')
 i=text.index('static std::string traceCase;');text=text[:i]+full(source,'BuildTextRunsScanner::FindBoundaryResult BuildTextRunsScanner::FindBoundaries(')+'\n'+text[i:]
 text=once(text,'assert(in);referenceRun.SetLength(transformed.size());',(ROOT/'native/boundary-invoke.cpp').read_text()+'\nassert(in);referenceRun.SetLength(transformed.size());',flavor+' boundary observation runner')
 (OUT/f'boundary-{flavor}.cpp').write_text(text)
(OUT/'boundary-extraction.json').write_text(json.dumps({'functions':h['records'],'adaptations':changes,'scope':'Complete variant-specific FindBoundaries with actual continuation admission, native UTF16 TransformText, byte fast path and FrameTextTraversal. Scratch array capacity and supplied frame/style tree remain explicit providers. BuildTextRuns line-list/backward/200-line caller scheduling is not supplied by this extension.'},indent=2)+'\n')
