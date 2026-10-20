int main(int argc, char** argv) {
  if (argc != 2) return 22;
  const int mode = std::atoi(argv[1]);
  nsIFrame scroll, cb, first, later;
  scroll.id = 1;
  cb.id = 2;
  first.id = 7;
  later.id = 8;
  scroll.sticky = cb.sticky = false;
  cb.parent = &scroll;
  first.parent = later.parent = &cb;
  first.continuation = &later;
  later.first = &first;
  ScrollContainerFrame sf;
  sf.scrolled = &scroll;
  sf.size = {100, 100};
  StickyScrollContainer container(&sf);
  sf.stickyContainer = &container;
  for (auto* f : {&scroll, &cb, &first, &later}) f->nearestScroll = &sf;
  cb.contentBox = scroll.overflow = {0, 0, 500, 500};
  first.position = {60, 50};
  first.normal = {50, 50};
  later.position = {90, 70};
  later.normal = {30, 20};
  first.borderBox = first.marginBox = later.borderBox = later.marginBox = {50, 50, 10, 10};
  first.offsets = {NS_AUTOOFFSET, 0, NS_AUTOOFFSET, 0};
  later.hasComputed = false;
  if (mode == 1) later.hasNormal = false;
  if (mode == 2) first.hasNormal = false;
  if (mode >= 3) {
    later.position.y = std::numeric_limits<int32_t>::max();
    later.normal.y = -1;
  }
  if (mode == 3) first.hasComputed = false;
  providerTrace.clear();
  const auto axis = mode == 4 ? layers::ScrollDirection::eVertical
                              : layers::ScrollDirection::eHorizontal;
  auto value = mozilla::dom::ViewTimeline::ComputeStickyDisplacement(&later, &sf, axis);
  std::cout << "{\"value\":";
  if (value) {
    auto d = value->second;
    std::cout << "[" << value->first << "," << d.mStartSideStuckAt << ","
              << d.mStartSideMax << "," << d.mEndSideUnstuckAt << ","
              << d.mEndSideMax << "," << d.Earliest(50) << "," << d.Latest(50) << "]";
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
