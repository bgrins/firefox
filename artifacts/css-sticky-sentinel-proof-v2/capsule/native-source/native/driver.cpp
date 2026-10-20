int main() {
  try {
    int count; std::cin>>count;
    for(int c=0;c<count;c++) {
      int action,target,reflow,n,np;nscoord sx,sy;
      std::cin>>action>>target>>reflow>>n>>np>>sx>>sy;
      std::vector<nsIFrame> frames(n);
      mozilla::ScrollContainerFrame root;root.id=n;root.first=&root;
      std::vector<int> first(n),next(n),parent(n);
      auto readPoint=[](nsPoint& p){std::cin>>p.x>>p.y;};
      auto readRect=[](nsRect& r){std::cin>>r.x>>r.y>>r.width>>r.height;};
      auto readOffsets=[](std::optional<nsMargin>& o){int present;nsMargin m;std::cin>>present>>m.top>>m.right>>m.bottom>>m.left;if(present)o=m;else o.reset();};
      for(int i=0;i<n;i++) {
        auto& f=frames[i];f.id=i;nsPoint current;
        std::cin>>first[i]>>next[i]>>parent[i]>>f.depth>>f.hadNormal>>f.sticky>>f.hasContainer>>f.geometryAvailable;
        readPoint(f.normal);readPoint(current);f.mRect.MoveTo(current);readPoint(f.fallback);
        readOffsets(f.offsets);readOffsets(f.recomputed);
        readRect(f.currentStick);readRect(f.currentContain);readRect(f.ignoreStick);readRect(f.ignoreContain);
      }
      auto frame=[&](int id)->nsIFrame* {if(id==-2)return &root;if(id==-1)return nullptr;return &frames.at(id);};
      for(int i=0;i<n;i++){frames[i].first=frame(first[i]);frames[i].next=frame(next[i]);frames[i].parent=frame(parent[i]);}
      mozilla::StickyScrollContainer s;s.mScrollContainerFrame=&root;s.mScrollPosition={sx,sy};mozilla::StickyScrollContainer::active=&s;
      for(int i=0;i<np;i++){int id;std::cin>>id;s.mFrames.frames.push_back(frame(id));}
      if(!std::cin)throw std::runtime_error("input");
      trace.clear();nsPoint value;bool hasValue=true;
      auto* f=frame(target);
      if(action==0)value=s.ComputePosition(f);
      else if(action==1)value=s.ComputePositionIgnoringScrolling(f);
      else if(action==2)value=s.ComputeTranslationIgnoringScrolling(f);
      else if(action==3){s.PositionContinuations(f);hasValue=false;}
      else if(action==4){s.UpdatePositions({sx,sy},reflow?&root:nullptr);hasValue=false;}
      else if(action==5)value=f->GetPositionIgnoringScrollingAndSticky();
      else if(action==6)value={s.IsStuckInYDirection(f)?1:0,0};
      else throw std::runtime_error("action");
      std::cout<<"{\"value\":";
      if(hasValue)std::cout<<"["<<value.x<<","<<value.y<<"]";else std::cout<<"null";
      std::cout<<",\"frames\":[";
      for(int i=0;i<n;i++){if(i)std::cout<<",";auto p=frames[i].GetPosition();std::cout<<"["<<p.x<<","<<p.y<<"]";}
      std::cout<<"],\"trace\":[";
      for(size_t i=0;i<trace.size();i++){if(i)std::cout<<",";std::cout<<"\""<<trace[i]<<"\"";}
      std::cout<<"]}\n";
    }
    std::string extra;if(std::cin>>extra)throw std::runtime_error("trailing input");
  } catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 2;}
}
