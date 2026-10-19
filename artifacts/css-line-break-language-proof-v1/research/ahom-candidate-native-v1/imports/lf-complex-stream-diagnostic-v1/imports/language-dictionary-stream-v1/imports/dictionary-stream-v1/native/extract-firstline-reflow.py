import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
h=runpy.run_path(str(ROOT/'native/extract-full.py'));full=h['full'];changes=[]
def once(text,before,after,name):
 assert text.count(before)==1,(name,text.count(before));changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
base=(OUT/'firstline-types.hpp').read_text()
base=once(base,'namespace nsFrameList{using Slice=std::vector<nsIFrame*>;}',(ROOT/'native/firstline-frame-list.hpp').read_text(),'frame-list primitive provider')
base+=(ROOT/'native/firstline-reflow-types.hpp').read_text()+'\n#define DEBUG 1\n'
src=ROOT/'source/providers/layout/generic/nsInlineFrame.cpp'
for marker in ['nsInlineFrame::InlineReflowInput::InlineReflowInput(','bool nsInlineFrame::HasFramesToPull(','nsIFrame* nsInlineFrame::PullOneFrame(','nsIFrame* nsFirstLineFrame::PullOneFrame(','bool nsFirstLineFrame::DrainSelfOverflowList(','void nsFirstLineFrame::Reflow(']:base+=full(src,marker)+'\n'
base+='\n#undef DEBUG\n';(OUT/'firstline-reflow-types.hpp').write_text(base)
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'firstline-{flavor}.cpp').read_text();text=once(text,'#include "firstline-types.hpp"','#include "firstline-reflow-types.hpp"',flavor+' types');text=once(text,'ReparentChildListStyle(&pc,moved,&container);assert(restyle.reparents==moved);',(ROOT/'native/firstline-reflow-invoke.cpp').read_text(),flavor+' complete first-line preparation caller');(OUT/f'firstline-reflow-{flavor}.cpp').write_text(text)
(OUT/'firstline-reflow-extraction.json').write_text(json.dumps({'functions':h['records'],'adaptations':changes,'scope':'Complete nsFirstLineFrame Reflow/PullOneFrame/DrainSelfOverflowList plus base PullOneFrame/HasFramesToPull/InlineReflowInput constructor. ReflowFrames is an entry-recording provider, not actual font/width layout. All supplied moved frames begin on first-fragment overflow or later-fragment principal/overflow lists, then pass through actual reparent/MarkDescendantsDirty and native text-run unhook before consumer entry. Style recomputation and frame-list primitives remain explicit adapters.'},indent=2)+'\n')
