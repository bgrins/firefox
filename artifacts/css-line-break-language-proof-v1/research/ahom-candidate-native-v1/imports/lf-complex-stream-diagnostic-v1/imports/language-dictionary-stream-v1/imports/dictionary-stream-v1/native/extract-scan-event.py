import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
source=ROOT/'native/extract-event.py';program=source.read_text();changes=[]
def once(before,after,name):
 global program
 assert program.count(before)==1,(name,program.count(before));program=program.replace(before,after);changes.append({'name':name,'before':before,'after':after})
once("base=(OUT/'lifecycle-types.hpp').read_text()","base=(OUT/'scan-lifecycle-types.hpp').read_text()",'joined base')
once("methods=full(","fields=[f for f in fields if f not in ['mMozControlCharacterVisibility','mLetterSpacing','mTextJustify','mTextRendering']]\nmethods=full(",'existing typed properties')
once(' virtual~nsIFrame()=default;virtual nsIFrame*GetNextContinuation()', ' virtual nsIFrame*GetNextContinuation()', 'single virtual destructor')
once('bool IsPlaceholderFrame()const{return placeholder;}', '', 'single placeholder predicate')
once("base=prefix+base", "base=prefix+base\nbase=once(base,'bool IsPlaceholderFrame()const{return type==LayoutFrameType::Placeholder;}','bool IsPlaceholderFrame()const{return placeholder||type==LayoutFrameType::Placeholder;}','combined placeholder identity')\nbase=once(base,'struct Value{','struct Value{bool operator==(const Value&)const=default;','length equality provider')", 'same tree predicate and equality')
once('struct nsPlaceholderFrame:nsIFrame{nsIFrame*outOfFlow=nullptr;nsIFrame*GetOutOfFlowFrame()const{return outOfFlow;}};', '', 'single placeholder class')
once("base=prefix+base\n","base=prefix+base\nbase=once(base,'nsTextFrame*GetNextContinuation()const{return next;}','nsTextFrame*GetNextContinuation()const override{return next;}','explicit continuation override')\n",'continuation override annotation')
start=program.index("for flavor in ['original','candidate','standalone']:");end=program.index("(OUT/'event-extraction.json')",start);program=program[:start]+program[end:]
program=program.replace("'event-types.hpp'","'scan-event-types.hpp'").replace("'event-extraction.json'","'scan-event-extraction.json'")
exec(compile(program,str(source), 'exec'),{'__file__':str(source),'__name__':'__main__'})
(OUT/'scan-event-extractor-adaptations.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changes':changes,'purpose':'Reuse complete native event-body extraction against the joined scanner/lifecycle type facade; no native body shortened.'},indent=2)+'\n')
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'scan-lifecycle-{flavor}.cpp').read_text();text=text.replace('#include "scan-lifecycle-types.hpp"','#include "scan-event-types.hpp"')
 old='scanner.ScanFrame(&container);scanner.FlushFrames(false,false);auto*created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);auto&run=*static_cast<nsTransformedTextRun*>(created);'
 assert text.count(old)==1
 text=text.replace(old,(ROOT/'native/scan-event-invoke.cpp').read_text())
 (OUT/f'scan-event-{flavor}.cpp').write_text(text)
