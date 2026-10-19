container.id=1;
for(size_t flow=0;flow<frames.size();flow++){ancestors[flow]->id=10+flow;for(size_t i=0;i<frames[flow].size();i++)frames[flow][i].id=1000*(flow+1)+i;}
for(unsigned barrier=0;barrier<3;barrier++){
 for(auto&p:ancestors)p->canContinue=true;
 if(barrier)ancestors[barrier==1?0:ancestors.size()-1]->canContinue=false;
 for(unsigned bits=0;bits<8;bits++)for(unsigned choice=0;choice<5;choice++){
  nsIFrame*stop=choice==1?&container:choice==2?static_cast<nsIFrame*>(&frames.front().front()):choice==3?static_cast<nsIFrame*>(&frames.back().back()):choice==4?ancestors.front().get():nullptr;
  nsTArray<char16_t>scratch;BuildTextRunsScanner::FindBoundaryState boundary{stop,nullptr,nullptr,bool(bits&1),bool(bits&2),bool(bits&4),scratch};
  auto result=scanner.FindBoundaries(&container,&boundary);
  std::cout<<id<<" BOUNDARY "<<barrier<<' '<<bits<<' '<<choice<<' '<<unsigned(result)<<' '<<(boundary.mFirstTextFrame?boundary.mFirstTextFrame->id:0)<<' '<<(boundary.mLastTextFrame?boundary.mLastTextFrame->id:0)<<' '<<boundary.mSeenTextRunBoundaryOnLaterLine<<' '<<boundary.mSeenTextRunBoundaryOnThisLine<<' '<<boundary.mSeenSpaceForLineBreakingOnThisLine<<"\n";
 }
}
for(auto&p:ancestors)p->canContinue=true;
