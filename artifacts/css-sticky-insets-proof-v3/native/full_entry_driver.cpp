int main(int argc, char** argv) {
  if (argc != 4) return 22;
  const int mode = std::atoi(argv[1]);
  const int guard = std::atoi(argv[2]);
  const bool horizontal = std::atoi(argv[3]);
  nsIFrame scroll, cb, frame;
  scroll.id = 1; cb.id = 2; frame.id = 7;
  scroll.sticky = cb.sticky = false;
  cb.parent = &scroll; frame.parent = &cb;
  ScrollContainerFrame sf; sf.scrolled = &scroll; sf.size = {100, 100};
  StickyScrollContainer container(&sf); sf.stickyContainer = &container;
  for (auto* f : {&scroll, &cb, &frame}) f->nearestScroll = &sf;
  cb.contentBox = scroll.overflow = {0, 0, 500, 500};
  frame.position = {60, 50}; frame.normal = {50, 50};
  frame.borderBox = frame.marginBox = {50, 50, 10, 10};
  frame.offsets = {NS_AUTOOFFSET, 0, NS_AUTOOFFSET, 0};
  if (mode == 1) {
    frame.position.y = std::numeric_limits<int32_t>::max(); frame.normal.y = -1;
    frame.borderBox.y = frame.marginBox.y = frame.position.y;
    frame.borderBox.height = frame.marginBox.height = 0;
  }
  if (mode == 2) {
    sf.size.height = std::numeric_limits<int32_t>::max();
    frame.offsets.top = -1; frame.offsets.bottom = 0;
  }
  if (mode == 3) {
    sf.size.height = nscoord_MAX;
    frame.offsets.top = nscoord_MIN; frame.offsets.bottom = -2;
  }
  if (!horizontal) {
    std::swap(frame.position.x, frame.position.y);
    std::swap(frame.normal.x, frame.normal.y);
    std::swap(frame.borderBox.x, frame.borderBox.y);
    std::swap(frame.borderBox.width, frame.borderBox.height);
    std::swap(frame.marginBox.x, frame.marginBox.y);
    std::swap(frame.marginBox.width, frame.marginBox.height);
    std::swap(frame.offsets.left, frame.offsets.top);
    std::swap(frame.offsets.right, frame.offsets.bottom);
    std::swap(sf.size.width, sf.size.height);
  }
  if (guard == 1) sf.stickyContainer = nullptr;
  if (guard == 2) frame.sticky = false;
  if (guard == 3) cb.sticky = true;
  if (guard == 4) frame.hasComputed = false;
  if (guard == 5) {
    if (horizontal) frame.offsets.left = frame.offsets.right = NS_AUTOOFFSET;
    else frame.offsets.top = frame.offsets.bottom = NS_AUTOOFFSET;
  }
  providerTrace.clear();
  auto value = mozilla::dom::ViewTimeline::ComputeStickyDisplacement(
      &frame, &sf, horizontal ? layers::ScrollDirection::eHorizontal : layers::ScrollDirection::eVertical);
  std::cout << "{\"value\":";
  if (value) {
    auto d = value->second;
    std::cout << "[" << value->first << "," << d.mStartSideStuckAt << "," << d.mStartSideMax
              << "," << d.mEndSideUnstuckAt << "," << d.mEndSideMax << "," << d.Earliest(50) << "," << d.Latest(50) << "]";
  } else {
    std::cout << "null";
  }
  std::cout << ",\"trace\":[";
  for (size_t i = 0; i < providerTrace.size(); ++i) {
    if (i) std::cout << ",";
    std::cout << providerTrace[i];
  }
  std::cout << "]}\n";
}
