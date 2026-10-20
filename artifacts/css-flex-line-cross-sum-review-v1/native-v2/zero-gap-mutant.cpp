#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>
using nscoord = int32_t;
constexpr nscoord nscoord_MAX = 1073741823;
struct FlexLine { nscoord value; nscoord LineCrossSize() const { return value; } };
struct Lines {
  uint32_t count;
  size_t Length() const { return count; }
};
struct FLR { Lines mLines; };
nscoord compute(nscoord aCrossGapSize, uint32_t count, const std::vector<FlexLine>& lines) {
 FLR flr{{count}};
 nscoord sumLineCrossSizes = std::min<int64_t>(
      0, int64_t(aCrossGapSize) * int64_t(flr.mLines.Length() - 1));
 for (const FlexLine& line : lines) {
 sumLineCrossSizes = std::min<int64_t>(
        nscoord_MAX, int64_t(sumLineCrossSizes) + line.LineCrossSize());
 }
 return sumLineCrossSizes;
}

int main() {
  uint64_t count, length;
  int64_t gap;
  while (std::cin >> count >> gap >> length) {
    if (count < 1 || count > UINT32_MAX || gap < 0 || gap > INT32_MAX || length > 100000) return 41;
    std::vector<FlexLine> lines;
    for (size_t i=0; i<length; ++i) {
      int64_t value;
      if (!(std::cin >> value) || value < 0 || value > INT32_MAX) return 42;
      lines.push_back({int32_t(value)});
    }
    if (length && count != length) return 43;
    std::cout << compute(int32_t(gap), uint32_t(count), lines) << '\n';
  }
}
