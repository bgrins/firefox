import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full'];changes=[]
def once(text,before,after,name):
 n=text.count(before);assert n==1,(name,n);changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
base=(OUT/'event-types.hpp').read_text()
base=once(base,'struct nsPresContext{','class RestyleManager;struct nsPresContext{::RestyleManager*restyle=nullptr;::RestyleManager*RestyleManager()const{return restyle;}', 'prescontext restyle identity')
base=once(base,'nsIFrame*GetOutOfFlowFrame()const{return outOfFlow;}','nsIFrame*GetOutOfFlowFrame()const{return outOfFlow;}static nsIFrame*GetRealFrameForPlaceholder(nsIFrame*f){return static_cast<nsPlaceholderFrame*>(f)->outOfFlow;}', 'placeholder target provider')
base+='\nnamespace nsFrameList{using Slice=std::vector<nsIFrame*>;}\n'
base+='class RestyleManager{public:std::vector<nsIFrame*>reparents;void ReparentComputedStyleForFirstLine(nsIFrame*f){reparents.push_back(f);}};\n'
base+='namespace nsLayoutUtils{void MarkDescendantsDirty(nsIFrame*); }\n'
base+=full(ROOT/'source/providers/layout/base/nsLayoutUtils.cpp','void nsLayoutUtils::MarkDescendantsDirty(')+'\n'
base+=full(ROOT/'source/providers/layout/generic/nsInlineFrame.cpp','static void ReparentChildListStyle(')+'\n'
(OUT/'firstline-types.hpp').write_text(base)
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'event-{flavor}.cpp').read_text()
 text=once(text,'#include "event-types.hpp"','#include "firstline-types.hpp"',flavor+' types')
 text=once(text,'StyleChangeReflow(&container,hint);','RestyleManager restyle;nsPresContext pc;pc.restyle=&restyle;nsFrameList::Slice moved;for(auto&list:container.children)for(auto*f:list.mList)moved.push_back(f);ReparentChildListStyle(&pc,moved,&container);assert(restyle.reparents==moved);',flavor+' first-line dirty caller')
 (OUT/f'firstline-{flavor}.cpp').write_text(text)
(OUT/'firstline-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptations':changes,'scope':'Complete ReparentChildListStyle and MarkDescendantsDirty, actual unhook/rebuild chain. ReparentComputedStyleForFirstLine is an explicit provider recording the moved frames; targeted styles are prepared by the fixture. This does not execute Servo style reparenting, first-line frame pulling or width-dependent frame reconstruction.'},indent=2)+'\n')
