
int main() {
  int side, automatic;
  nscoord value, basis;
  while (std::cin >> side >> automatic >> value >> basis) {
    assert(side >= 0 && side < 4 && (automatic == 0 || automatic == 1));
    nsStylePosition position;
    for (int i = 0; i < 4; ++i) position.insets[i] = {false, {7 + i}};
    position.insets[side] = {automatic != 0, {value}};
    queriedSide = -1; queries = resolves = 0; seenBasis = -1;
    nscoord result = ComputeStickySideOffset(static_cast<Side>(side), position, basis);
    std::cout << result << ' ' << queriedSide << ' ' << queries << ' ' << resolves << ' ' << seenBasis << '\n';
  }
}
