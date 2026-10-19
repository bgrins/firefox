struct World {
 Document doc; PresShell shell;
 std::vector<std::unique_ptr<Element>> elements;
 std::vector<std::unique_ptr<ScrollContainerFrame>> frames;
 Element* element(int id)const{for(auto& e:elements)if(e->id==id)return e.get();return nullptr;}
 ScrollContainerFrame* frame(int id)const{for(auto& f:frames)if(f->id==id)return f.get();return nullptr;}
 int type=0,host=0,pseudo=0,axis=0,apz=0;
 void read(){
  int root,scroll,shellPresent,rootFrame,ne,nf;
  std::cin>>type>>host>>pseudo>>axis>>root>>scroll>>shellPresent>>rootFrame>>apz>>ne>>nf;
  std::vector<std::array<int,14>> es(ne);
  std::vector<std::array<int,15>> fs(nf);
  for(auto& row:es){for(auto& n:row)std::cin>>n;elements.push_back(std::make_unique<Element>());elements.back()->id=row[0];}
  for(auto& row:fs){for(auto& n:row)std::cin>>n;frames.push_back(std::make_unique<ScrollContainerFrame>());frames.back()->id=row[0];}
  doc.root=element(root);doc.scrolling=element(scroll);doc.shell=shellPresent?&shell:nullptr;shell.root=frame(rootFrame);
  for(auto& row:es){auto* e=element(row[0]);e->doc=&doc;e->primary=frame(row[1]);e->kind=row[2];e->parent=element(row[3]);e->isElement=row[4];e->apzDisabled=row[5];e->displayport=row[6];for(int j=1;j<8;++j)e->pseudos[j]=element(row[6+j]);}
  for(auto& row:fs){auto* f=frame(row[0]);f->parent=frame(row[1]);f->content=element(row[2]);f->scroll=row[3];f->target=frame(row[4]);f->mode.vertical=row[5];f->mode.reversed=row[14];f->available=row[6];f->position={row[7],row[8]};f->range={0,0,row[9],row[10]};f->styles={StyleOverflow(row[11]),StyleOverflow(row[12])};f->shell=row[13]?&shell:nullptr;assert(row[14]==0 || row[14]==1);}
 }
};
void number(double v){assert(std::isfinite(v));std::cout<<v;}
int main(){
 std::cout.precision(17);
 int cases;std::cin>>cases;
 for(int ci=0;ci<cases;++ci){
  int id,steps,subscribers;std::cin>>id>>steps>>subscribers;
  std::vector<std::unique_ptr<World>> worlds;
  std::unique_ptr<ScrollTimeline> timeline;
  std::vector<std::unique_ptr<Animation>> animations;
  for(int j=0;j<subscribers;++j){animations.push_back(std::make_unique<Animation>());animations.back()->id=3000+j;if(j)animations[j-1]->next=animations[j].get();}
  for(int si=0;si<steps;++si){
   worlds.push_back(std::make_unique<World>());auto& w=*worlds.back();w.read();
   auto pseudo=PseudoStyleRequest(PseudoStyleType(w.pseudo));auto* host=w.element(w.host);
   if(!timeline){
    if(w.type==3)timeline.reset(ScrollTimeline::MakeNamed(&w.doc,host,pseudo,StyleScrollAxis(w.axis)));
    else if(w.type==0)timeline.reset(new ScrollTimeline(&w.doc,ScrollTimeline::Info(w.type,host,pseudo),StyleScrollAxis(w.axis)));
    else timeline.reset(ScrollTimeline::MakeAnonymous(&w.doc,NonOwningAnimationTarget(host,pseudo),StyleScrollAxis(w.axis),w.type==1?StyleScroller::Root:w.type==2?StyleScroller::Nearest:StyleScroller::SelfElement));
    assert(!timeline->GetSnapshot().IsActive());assert(timeline->GetSnapshot().SourceElement()==nullptr);
    timeline->mAnimationOrder.first=subscribers?animations[0].get():nullptr;
   }
   timeline->mScrollerInfo=ScrollTimeline::Info(w.type,host,pseudo);timeline->mAxis=StyleScrollAxis(w.axis);gfxPlatform::enabled=w.apz;
   events.clear();bool changed=timeline->UpdateCachedCurrentTime();
   auto snap=timeline->GetSnapshot();auto* exposed=timeline->GetSource();auto data=timeline->ComputeTimelineData();
   auto duration=timeline->GetCurrentTimeAsDuration();Nullable<OwningCSSNumberish> typed,fallback;
   StaticPrefs::typed=true;timeline->GetCurrentTime(typed);StaticPrefs::typed=false;timeline->GetCurrentTime(fallback);
   std::cout<<"{\"case\":"<<id<<",\"sample\":"<<si<<",\"snapshot\":["<<(snap.SourceElement()?snap.SourceElement()->id:0)<<','<<timeline->snapshotPseudo()<<','<<timeline->snapshotRoot()<<','<<snap.IsActive()<<','<<(snap.IsActive()?int(snap.Axis()):-1)<<','<<snap.ScrollingDirectionIsAvailable()<<','<<(snap.IsActive()?int(snap.SourceScrollStyle()):-1)<<','<<snap.APZIsActiveForSource()<<"],\"raw_axis_style\":["<<int(snap.Axis())<<','<<int(snap.SourceScrollStyle())<<"],\"exposed\":"<<(exposed?exposed->id:0)<<",\"cache\":";
   if(timeline->mCachedCurrentTime)std::cout<<'['<<timeline->mCachedCurrentTime->mPosition<<','<<timeline->mCachedCurrentTime->mMaxScrollOffset<<']';else std::cout<<"null";
   std::cout<<",\"data\":";if(data)std::cout<<'['<<data->mPosition<<','<<data->mStart<<','<<data->mEnd<<']';else std::cout<<"null";
   std::cout<<",\"changed\":"<<changed<<",\"duration\":";if(duration.value)number(duration.value->value);else std::cout<<"null";
   std::cout<<",\"percent\":";if(typed.value)number(typed.value->css->value);else std::cout<<"null";
   std::cout<<",\"fallback\":";if(fallback.value)number(fallback.value->duration);else std::cout<<"null";
   std::cout<<",\"trace\":[";
   for(size_t k=0;k<events.size();++k){if(k)std::cout<<',';auto e=events[k];std::cout<<'['<<e[0]<<','<<e[1]<<','<<e[2]<<','<<e[3]<<']';}
   std::cout<<"]}\n";
  }
 }
 assert(std::cin.good());
}
