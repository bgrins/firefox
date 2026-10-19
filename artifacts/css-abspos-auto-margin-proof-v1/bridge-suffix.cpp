int main() {
  int wm, property;
  while (std::cin >> wm >> property) {
    LogicalSize cb, kid;
    LogicalMargin offsets, margin;
    StyleMargin styleMargin;
    nsIFrame frame;
    for (nscoord& n : cb.values) { std::cin >> n; }
    for (nscoord& n : kid.values) { std::cin >> n; }
    for (nscoord& n : offsets.values) { std::cin >> n; }
    for (nscoord& n : margin.values) { std::cin >> n; }
    for (AutoValue& v : styleMargin.tags) { std::cin >> v.value; }
    for (AutoValue& v : frame.position.resolved) { std::cin >> v.value; }
    frame.hasProperty = property;
    frame.used = {17,19,23,29};
    ReflowInput parent{};
    parent.wm = {wm};
    ReflowInput child{&parent, &styleMargin, &frame, {wm}, {}, 0};
    geometryReads = {0,0};
    AbsoluteContainingBlock abs;
    const auto flags = abs.Caller(child, cb, kid, margin, offsets, &frame, nullptr, {wm});
    for (nscoord n : margin.values) { std::cout << n << ' '; }
    for (nscoord n : child.computed.values) { std::cout << n << ' '; }
    for (nscoord n : frame.used) { std::cout << n << ' '; }
    std::cout << geometryReads[0] << ' ' << geometryReads[1] << ' ' << child.writes << ' '
              << frame.propertyReads << ' ' << frame.position.requestedMask << ' '
              << flags[0] << ' ' << flags[1] << '\n';
  }
}
