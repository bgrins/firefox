int main(){std::string line;while(std::getline(std::cin,line)){
 std::istringstream in(line);std::string id;unsigned simple,observer,slot,nflows;int start;in>>id>>simple>>observer>>slot>>nflows>>start;
 gfxTextRun target,other;target.flags=(simple?0x10:0)|(observer?0x1000:0);
 std::vector<std::vector<nsTextFrame>>flows;std::vector<nsTextFrame*>flat;
 for(unsigned f=0;f<nflows;f++){unsigned n;in>>n;flows.emplace_back(n+1);auto&flow=flows.back();for(unsigned i=0;i<=n;i++){
  auto&frame=flow[i];frame.next=i<n?&flow[i+1]:nullptr;frame.state=TEXT_HAS_FONT_INFLATION;
  frame.mTextRun=slot?&other:(i<n?&target:&other);frame.uninflated=slot?(i<n?&target:&other):&other;
  if(i==0)frame.state|=slot?TEXT_IN_UNINFLATED_TEXTRUN_USER_DATA:TEXT_IN_TEXTRUN_USER_DATA;
  if(i<n)flat.push_back(&frame);
 }}
 if(simple){assert(nflows==1);target.data=observer?static_cast<void*>(new SimpleTextRunUserData{&flows[0][0]}):static_cast<void*>(&flows[0][0]);}
 else{size_t size=observer?sizeof(ComplexTextRunUserData):sizeof(TextRunUserData);auto storage=::operator new(size+nflows*sizeof(TextRunMappedFlow));auto data=observer?static_cast<TextRunUserData*>(new(storage)ComplexTextRunUserData{}):new(storage)TextRunUserData{};data->mMappedFlowCount=nflows;data->mLastFlowIndex=nflows-1;target.data=data;auto mapped=GetMappedFlows(&target);for(unsigned f=0;f<nflows;f++)mapped[f]={&flows[f][0],0,unsigned(flows[f].size()-1)};}
 nsTextFrame*from=start<0?nullptr:flat.at(start);
 (from?from:flat[0])->ClearTextRun(from,slot?nsTextFrame::eNotInflated:nsTextFrame::eInflated);
 std::cout<<id<<" REFERENCES ";for(auto*frame:flat)std::cout<<(frame->GetTextRun(slot?nsTextFrame::eNotInflated:nsTextFrame::eInflated)==&target);
 std::cout<<" OWNERS ";for(auto&flow:flows)std::cout<<flow[0].HasAnyStateBits(slot?TEXT_IN_UNINFLATED_TEXTRUN_USER_DATA:TEXT_IN_TEXTRUN_USER_DATA);
 std::cout<<" COUNT "<<(target.data?(simple?1:static_cast<TextRunUserData*>(target.data)->mMappedFlowCount):0)<<" LAST "<<(target.data&&!simple?static_cast<TextRunUserData*>(target.data)->mLastFlowIndex:0)<<"\n";
 for(auto&flow:flows)assert(flow.back().mTextRun==&other&&flow.back().uninflated==&other);
 if(target.data)DestroyTextRunUserData(&target);
}}
