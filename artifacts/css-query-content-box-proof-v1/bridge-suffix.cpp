struct Input {
  nsIFrame frame;
  bool present;
  bool contents;
};

bool read(Input& input) {
  unsigned type;
  if (!(std::cin >> type >> input.frame.wm.vertical >>
        input.frame.border.width >> input.frame.border.height >>
        input.frame.content.width >> input.frame.content.height >>
        input.frame.axes.mIContained >> input.frame.axes.mBContained >>
        input.present >> input.contents)) {
    return false;
  }
  input.frame.display.mContainerType = static_cast<StyleContainerType>(type);
  return true;
}

nsSize project(const Input& input) {
  nsSize result{-1, -1};
  if (!input.contents) {
    Element element{input.present ? &input.frame : nullptr};
    Gecko_GetQueryContainerSize(&element, &result.width, &result.height);
  }
  result.width = result.width < 0 ? -1 : result.width;
  result.height = result.height < 0 ? -1 : result.height;
  return result;
}

int main() {
  Input before, after;
  while (read(before)) {
    assert(read(after));
    auto candidate = candidateState(&before.frame);
    auto original = originalState(&before.frame);
    const auto candidateAfter = candidateState(&after.frame);
    const auto originalAfter = originalState(&after.frame);
    const auto first = project(before);
    const auto second = project(after);
    std::cout << candidate.Changed(candidateAfter) << ' '
              << original.Changed(originalAfter) << ' '
              << first.width << ' ' << first.height << ' '
              << second.width << ' ' << second.height << '\n';
  }
}
