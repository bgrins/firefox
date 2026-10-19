#include <algorithm>
#include <cstdio>
#include <optional>
#define MOZ_UNLIKELY(x) (x)
#define MOZ_ASSERT(x) ((void)0)
constexpr int NS_UNCONSTRAINEDSIZE = 1000000;
enum class LogicalAxis { Inline };
enum class StyleAlignFlags { STRETCH, NORMAL, START };
enum class ComputeSizeFlag { IClampMarginBoxMinSize };
enum class FillCB { No, Stretch, Clamp };
struct Size {
  int keyword;
  bool IsAuto() const { return keyword == 0; }
  bool IsMaxContent() const { return keyword == 1; }
};
struct Flags {
  bool clamp;
  bool contains(ComputeSizeFlag) const { return clamp; }
  void operator-=(ComputeSizeFlag) { clamp = false; }
};
struct LogicalSize {
  int value;
  int ISize(int) const { return value; }
};
struct Parent {
  bool masonry;
  bool IsMasonry(int, LogicalAxis) const { return masonry; }
  int GetWritingMode() const { return 0; }
  int Style() const { return 0; }
};
struct Position {
  StyleAlignFlags alignment;
  StyleAlignFlags UsedSelfAlignment(int, LogicalAxis, int, int) const { return alignment; }
};
struct Margin {
  bool start, end;
  bool HasInlineAxisAuto(int, int) const { return start || end; }
};
struct AnchorPosResolutionParams {
  template<class T> static int From(T*) { return 0; }
};
struct Result {
  bool stretch, fill, clamp, explicitSize;
  int fillSize;
  bool operator==(const Result& b) const {
    return stretch == b.stretch && fill == b.fill && clamp == b.clamp &&
           explicitSize == b.explicitSize && fillSize == b.fillSize;
  }
};
struct Adapter {
  bool grid;
  Size size;
  Parent parent;
  Position position;
  Margin margin;
  bool explicitCalled = false;
  const Margin* StyleMargin() const { return &margin; }
  bool IsTrueOverflowContainer() const { return false; }
  struct Computed { int mISize; };
  template<class... T> Computed ComputeISizeValue(T...) {
    explicitCalled = true;
    return {37};
  }
  Result run(bool definite, bool clamp, int cb, int padding, int margins) {
    const Size* styleISize = &size;
    const Size* styleBSize = &size;
    auto* parentFrame = &parent;
    auto* stylePos = &position;
    bool isGridItem = grid;
    int aWM = 0, aRenderingContext = 0, aspectRatio = 0, iSize = 0;
    LogicalSize aCBSize{definite ? cb : NS_UNCONSTRAINEDSIZE};
    LogicalSize aMargin{margins}, aBorderPadding{padding};
    Flags aFlags{clamp};
    FillCB inlineFillCB = FillCB::No;
    std::optional<int> iSizeToFillCB;
@NATURAL@
@BRANCH@
    return {inlineFillCB == FillCB::Stretch, iSizeToFillCB.has_value(),
            aFlags.clamp, explicitCalled, iSizeToFillCB.value_or(-1)};
  }
};
int main() {
  int cases = 0;
  const int measures[][3] = {{200, 0, 0}, {200, 10, 20}, {0, 0, 0}, {10, 20, 0}, {10, 0, -20}};
  for (int size = 0; size < 5; ++size)
    for (int alignment = 0; alignment < 3; ++alignment)
      for (int mask = 0; mask < 64; ++mask)
        for (const auto& m : measures) {
          bool grid = mask & 1, masonry = mask & 2, definite = mask & 4;
          bool start = mask & 8, end = mask & 16, clamp = mask & 32;
          Adapter a{grid, {size}, {masonry}, {StyleAlignFlags(alignment)}, {start, end}};
          auto actual = a.run(definite, clamp, m[0], m[1], m[2]);
          bool stretch = size == 0 && alignment == 0 && !start && !end && grid && !masonry && definite;
          bool eligible = (size == 0 || size == 1) && grid && !masonry;
          bool fill = stretch || (eligible && definite && clamp);
          Result expected{stretch, fill, clamp && !(eligible && !definite), size >= 2,
                          fill ? std::max(0, m[0] - m[1] - m[2]) : -1};
          if (!(actual == expected)) {
            std::printf("mismatch size=%d alignment=%d mask=%d measure=%td\n", size, alignment, mask, &m - measures);
            return 1;
          }
          ++cases;
        }
  std::printf("%d cases\n", cases);
}
