void emitPoint(nsPoint p){std::cout<<"["<<p.x<<","<<p.y<<"]";}
void emitRect(nsRect r){std::cout<<"["<<r.x<<","<<r.y<<","<<r.width<<","<<r.height<<"]";}
void emitAbsolute(nsRectAbsolute r){std::cout<<"["<<r.X()<<","<<r.Y()<<","<<r.XMost()<<","<<r.YMost()<<"]";}
void emitMargin(nsMargin r){std::cout<<"["<<r.top<<","<<r.right<<","<<r.bottom<<","<<r.left<<"]";}
void emitRanges(StickyScrollContainer::StickyScrollRanges r){
 std::cout<<"[";
 auto emit=[](Maybe<StickyScrollContainer::StickyScrollRange> x){if(!x){std::cout<<"null";return;}std::cout<<"["<<x->mScrollPosition<<","<<x->mMaxOffset<<"]";};
 emit(r.mStartSide);std::cout<<",";emit(r.mEndSide);std::cout<<"]";
}
void emitStick(nsRect r){std::cout<<"["<<r.X()<<","<<r.Y()<<","<<r.XMost()<<","<<r.YMost()<<"]";}
void emitStick(nsRectAbsolute r){emitAbsolute(r);}
void emitLimits(StickyScrollContainer::StickyLimits r){std::cout<<"[";emitStick(r.mStick);std::cout<<",";emitRect(r.mContain);std::cout<<"]";}
int main(){
 std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream input(line);
  int id,action,cbKind,cbMode,childMode,scrollMode,direction,hasOffsets,hasNormal,viewport,extra;
  if(!(input>>id>>action>>cbKind>>cbMode>>childMode>>scrollMode>>direction>>hasOffsets>>hasNormal>>viewport>>extra))return 21;
  nsIFrame scroll,cb,row,frame,continuation;
  scroll.id=1;cb.id=2;row.id=3;frame.id=4;continuation.id=5;
  scroll.sticky=cb.sticky=row.sticky=false;
  cb.parent=&scroll;row.parent=&cb;row.rowGroup=true;
  frame.parent=cbKind==1?&scroll:cbKind==2?&row:&cb;
  continuation.parent=frame.parent;continuation.first=&frame;
  cb.mWritingMode=WritingMode(cbMode);frame.mWritingMode=WritingMode(childMode);scroll.mWritingMode=WritingMode(scrollMode);
  cb.visibility.mDirection=direction?StyleDirection::Rtl:StyleDirection::Ltr;
  scroll.visibility.mDirection=cb.visibility.mDirection;row.visibility.mDirection=cb.visibility.mDirection;
  ScrollContainerFrame sf;sf.scrolled=&scroll;sf.root=viewport;sf.context.cross=viewport;
  StickyScrollContainer container(&sf);sf.stickyContainer=&container;
  for(auto* f:{&scroll,&cb,&row,&frame,&continuation})f->nearestScroll=&sf;
  auto point=[&](nsPoint& p){input>>p.x>>p.y;};
  auto rect=[&](nsRect& r){input>>r.x>>r.y>>r.width>>r.height;};
  auto margin=[&](nsMargin& m){input>>m.top>>m.right>>m.bottom>>m.left;};
  rect(frame.borderBox);rect(frame.marginBox);rect(cb.contentBox);rect(scroll.overflow);
  margin(scroll.padding);input>>sf.size.width>>sf.size.height>>sf.shell.fixedSize.width>>sf.shell.fixedSize.height;
  point(container.mScrollPosition);point(frame.position);point(frame.normal);point(frame.parent->offsetToScroll);point(scroll.transform);
  margin(frame.offsets);frame.hasComputed=hasOffsets;frame.hasNormal=hasNormal;
  for(int i=0;i<4;i++){int value;input>>value;frame.stylePosition.sides[i]={value==NS_AUTOOFFSET,value};}
  point(continuation.position);point(continuation.normal);rect(continuation.borderBox);rect(continuation.marginBox);
  int excess;if(!input||input>>excess)return 22;
  if(extra)frame.continuation=&continuation;
  container.mFrames.frames={&frame};
  providerTrace.clear();
  const auto originalOffsets=frame.offsets;
  const auto current=container.ComputeStickyLimits(&frame);
  const auto ignoring=container.ComputeStickyLimits(&frame,StickyScrollContainer::StickyLimitSpace::IgnoreCurrentScroll);
  const auto position=container.ComputePosition(&frame);
  const auto zero=container.ComputePositionIgnoringScrolling(&frame);
  const auto translation=container.ComputeTranslationIgnoringScrolling(extra?&continuation:&frame);
  const auto rangeX=container.GetStickyScrollRangesForAxis(extra?&continuation:&frame,layers::ScrollDirection::eHorizontal);
  const auto rangeY=container.GetStickyScrollRangesForAxis(extra?&continuation:&frame,layers::ScrollDirection::eVertical);
  nsRectAbsolute outer,inner;container.GetScrollRanges(extra?&continuation:&frame,&outer,&inner);
  std::cout<<"{\"id\":"<<id<<",\"original_offsets\":";emitMargin(originalOffsets);
  std::cout<<",\"current\":";emitLimits(current);std::cout<<",\"ignoring\":";emitLimits(ignoring);
  std::cout<<",\"position\":";emitPoint(position);std::cout<<",\"zero\":";emitPoint(zero);
  std::cout<<",\"translation\":";emitPoint(translation);
  std::cout<<",\"range_x\":";emitRanges(rangeX);std::cout<<",\"range_y\":";emitRanges(rangeY);
  std::cout<<",\"outer\":";emitAbsolute(outer);std::cout<<",\"inner\":";emitAbsolute(inner);
  std::cout<<",\"trace\":[";
  for(size_t i=0;i<providerTrace.size();i++){if(i)std::cout<<",";std::cout<<providerTrace[i];}
  std::cout<<"]}\n";
 }
}
