int main(){
 nsIFrame scroll,cb,f;scroll.id=1;cb.id=2;f.id=3;
 cb.parent=&scroll;f.parent=&cb;
 ScrollContainerFrame sf;sf.scrolled=&scroll;sf.size={100,100};
 StickyScrollContainer container(&sf);sf.stickyContainer=&container;
 scroll.nearestScroll=&sf;cb.nearestScroll=&sf;f.nearestScroll=&sf;
 f.position=f.normal={0,200};f.borderBox=f.marginBox={0,200,10,200};
 cb.contentBox={0,0,100,600};scroll.overflow={0,0,100,600};
 f.offsets={NS_AUTOOFFSET,NS_AUTOOFFSET,20,NS_AUTOOFFSET};
 container.mScrollPosition={0,160};
 auto limits=container.ComputeStickyLimits(&f);auto position=container.ComputePosition(&f);
 std::cout<<position.x<<","<<position.y<<"|"<<limits.mStick.y<<","<<limits.mStick.YMost()<<"\n";
 container.PositionContinuations(&f);
 auto ranges=container.GetStickyScrollRangesForAxis(&f,layers::ScrollDirection::eVertical);
 nsRectAbsolute outer,inner;container.GetScrollRanges(&f,&outer,&inner);
 std::cout<<f.position.y<<"|"<<ranges.mEndSide->mScrollPosition<<","<<ranges.mEndSide->mMaxOffset<<"\n";
}
