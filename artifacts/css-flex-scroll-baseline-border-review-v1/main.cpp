int main(){int group,context,kind,contain,present,wm;nscoord outer,inner,bstart,bend,baseline,synth;
 while(std::cin>>group>>context>>kind>>contain>>present>>wm>>outer>>inner>>bstart>>bend>>baseline>>synth){
 counts={};Frame plain;nsBlockFrame block;block.button=kind==2;Frame* child=kind?static_cast<Frame*>(&block):&plain;
 child->present=present;child->baseline=baseline;child->inner=inner;
 ScrollContainerFrame frame{child,outer,bstart,bend,synth,{bool(contain)}};
 auto result=frame.GetNaturalBaselineBOffset(wm,BaselineSharingGroup(group),BaselineExportContext(context));
 std::cout<<bool(result.v)<<' '<<result.v.value_or(0)<<' '<<counts.style<<' '<<counts.query<<' '<<counts.natural<<' '<<counts.inner<<' '<<counts.border<<' '<<counts.outer<<' '<<counts.fallback<<' '<<counts.wm<<' '<<counts.group<<' '<<counts.context<<"\n";
 }
}
