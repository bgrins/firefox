
struct OwnedLine {
  nsLineBox line;
  StyleBlockEllipsis clamp;
  std::vector<std::unique_ptr<nsIFrame>> storage;
};
struct OwnedCase {
  int id=0,seed=0;
  WritingMode wm{true};
  int start=0,width=100,blockWidth=400;
  StyleTextOverflowSide styles[2];
  nsBlockFrame block;
  PresShellAdapter shell;
  PresContextAdapter context;
  ScrollContainerFrame scroll;
  bool canScroll=false,snap=false;
  std::vector<std::unique_ptr<OwnedLine>> lines;
};
static nsRect physical(WritingMode wm,int start,int width,int blockWidth) {
  return {wm.ltr?start:blockWidth-start-width,0,width,1};
}
static int readInt() { int v; if(!(std::cin>>v))std::abort();return v; }
static std::unique_ptr<OwnedCase> readCase() {
  auto c=std::make_unique<OwnedCase>();
  c->id=readInt();int count=readInt();c->wm.ltr=readInt();c->start=readInt();c->width=readInt();c->seed=readInt();
  for(int side=0;side<2;side++) {
    auto& s=c->styles[side];s.id=side;s.kind=readInt();s.string.atom={side,readInt(),readInt()};
  }
  c->block.ellipsisWidth=readInt();c->block.ellipsisFailure=readInt();
  c->canScroll=readInt();int pos=readInt(),lo=readInt(),hi=readInt();
  c->scroll.position={c->wm.ltr?pos:c->blockWidth-pos,0};
  c->scroll.range=physical(c->wm,lo,hi-lo,c->blockWidth);
  c->snap=readInt();c->context.units=readInt();
  c->block.shell=&c->shell;c->block.context=&c->context;
  for(int ln=0;ln<count;ln++) {
    auto line=std::make_unique<OwnedLine>();line->line.id=ln;
    int kind=readInt();line->line.clamp=kind>=0;line->clamp.id=ln+2;line->clamp.kind=std::max(0,kind);
    line->clamp.string.atom={ln+2,readInt(),readInt()};
    line->line.floats=readInt();line->line.startEdge=readInt();line->line.endEdge=readInt();
    int overflowStart=readInt(),overflowEnd=readInt();line->line.overflow=physical(c->wm,overflowStart,overflowEnd-overflowStart,c->blockWidth);
    int n=readInt();std::vector<int> parents;
    for(int i=0;i<n;i++) {
      int parent=readInt(),role=readInt(),visible=readInt(),nonsuppressed=readInt();
      int start=readInt(),size=readInt(),os=readInt(),oe=readInt(),nc=readInt();
      std::unique_ptr<nsIFrame> f=role==1?std::unique_ptr<nsIFrame>(std::make_unique<nsTextFrame>()):std::make_unique<nsIFrame>();
      f->id=i;f->kind=LayoutFrameType(role);f->visibility.visible=visible;
      auto border=physical(c->wm,start,size,c->blockWidth);auto overflow=physical(c->wm,os,oe-os,c->blockWidth);
      f->offset={border.x,border.y};f->size={size,1};f->overflow={overflow.x-border.x,0,overflow.width,1};
      f->shell=&c->shell;f->context=&c->context;
      std::vector<int> advances;for(int j=0;j<nc;j++)advances.push_back(readInt());
      if(role==1) {
        auto* text=static_cast<nsTextFrame*>(f.get());text->nonsuppressed=nonsuppressed;
        if(!c->wm.ltr)std::reverse(advances.begin(),advances.end());
        text->advances=std::move(advances);
      } else assert(nc==0);
      parents.push_back(parent);line->storage.push_back(std::move(f));
    }
    for(int i=0;i<n;i++) {
      int parent=parents[i];assert(parent<i);
      if(parent<0)line->line.frames.push_back(line->storage[i].get());
      else line->storage[parent]->children.push_back(line->storage[i].get());
    }
    c->lines.push_back(std::move(line));
  }
  return c;
}
static void configure(TextOverflow& t,OwnedCase& c) {
  t.mBlock=&c.block;t.mBlockWM=c.wm;t.mBlockSize={c.blockWidth,1};
  t.mContentArea=LogicalRect(c.wm,c.start,0,c.width,1);
  t.mScrollContainerFrame=&c.scroll;t.mCanHaveInlineAxisScrollbar=c.canScroll;t.mAdjustForPixelSnapping=c.snap;
  t.mIStart.Init(c.styles[0]);t.mIEnd.Init(c.styles[1]);
  if(c.seed)for(auto* marker:{&t.mIStart,&t.mIEnd}) {
    auto* s=marker->mTextOverflowStyle;
    int width=s->IsClip()?0:s->IsEllipsis()?(c.block.ellipsisFailure?0:c.block.ellipsisWidth):s->string.atom.width;
    marker->mISize=marker->mIntrinsicISize=width;marker->mInitialized=true;
  }
}
static void printEvents(int id,int line,const char* mode) {
  std::cout<<id<<'\t'<<line<<'\t'<<mode<<'\t'<<'[';
  for(size_t i=0;i<events.size();i++) {
    if(i)std::cout<<',';std::cout<<'[';
    for(size_t j=0;j<events[i].size();j++){if(j)std::cout<<',';std::cout<<events[i][j];}
    std::cout<<']';
  }
  std::cout<<"]\n";
}
static void invoke(TextOverflow& t,OwnedCase& c,OwnedLine& line,const char* mode) {
  events.clear();attemptCount=0;c.block.clamp=line.line.clamp?&line.clamp:nullptr;
  Event before{0};t.AddMarkers(before);events.push_back(before);
  nsDisplayListSet lists;
  t.ProcessLine(lists,&line.line,line.line.id);
  Event after{9};t.AddMarkers(after);events.push_back(after);
  printEvents(c.id,line.line.id,mode);
}
int main() {
  int count=readInt();
  for(int i=0;i<count;i++) {
    auto c=readCase();TextOverflow reused;configure(reused,*c);
    for(auto& line:c->lines) {
      TextOverflow fresh;configure(fresh,*c);
      fresh.mIStart=reused.mIStart;fresh.mIEnd=reused.mIEnd;
      fresh.mIStart.mISize=fresh.mIStart.mIntrinsicISize;fresh.mIStart.Reset();
      fresh.mIEnd.mISize=fresh.mIEnd.mIntrinsicISize;fresh.mIEnd.Reset();
      invoke(reused,*c,*line,"reuse");invoke(fresh,*c,*line,"fresh");
    }
  }
}
