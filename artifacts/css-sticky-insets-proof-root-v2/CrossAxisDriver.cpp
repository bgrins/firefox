int main(int argc, char** argv) {
  const int mode = argc > 1 ? std::atoi(argv[1]) : 0;
  nsIFrame scroll, cb, frame;
  scroll.id=1; cb.id=2; frame.id=7;
  scroll.sticky=cb.sticky=false;
  cb.parent=&scroll; frame.parent=&cb;
  ScrollContainerFrame sf; sf.scrolled=&scroll; sf.size={100,100};
  StickyScrollContainer container(&sf); sf.stickyContainer=&container;
  for (auto* f : {&scroll,&cb,&frame}) f->nearestScroll=&sf;
  cb.contentBox=scroll.overflow={0,0,500,500};
  frame.position={60,50}; frame.normal={50,50};
  frame.borderBox=frame.marginBox={50,50,10,10};
  frame.offsets={NS_AUTOOFFSET,0,NS_AUTOOFFSET,0};
  if (mode == 1) {
    frame.position.y=std::numeric_limits<int32_t>::max(); frame.normal.y=-1;
    frame.borderBox.y=frame.marginBox.y=frame.position.y;
    frame.borderBox.height=frame.marginBox.height=0;
  }
  if (mode == 2) {
    sf.size.height=std::numeric_limits<int32_t>::max();
    frame.offsets.top=-1; frame.offsets.bottom=0;
  }
  if (mode == 3) {
    sf.size.height=nscoord_MAX;
    frame.offsets.top=nscoord_MIN; frame.offsets.bottom=-2;
  }
  auto value=mozilla::dom::ViewTimeline::ComputeStickyDisplacement(
      &frame,&sf,layers::ScrollDirection::eHorizontal);
  if (!value) return 21;
  std::cout << value->first << "," << value->second.Latest(50) << "\n";
}
