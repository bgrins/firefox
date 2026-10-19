#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>

#define MOZ_ASSERT(condition) assert(condition)
namespace nsStyleTransformMatrix {
using nscoord = int32_t;
struct nsRect {
  nscoord x = 0, y = 0, width = 0, height = 0;
  nscoord Width() const { return width; }
  nscoord Height() const { return height; }
};
enum class StyleTransformBox { FillBox, ContentBox, StrokeBox, ViewBox, BorderBox };
constexpr unsigned NS_FRAME_SVG_LAYOUT = 1;
using Counters = std::array<int, 8>;
struct StyleZoom {
  int divisor;
  Counters* counts;
  nsRect Unzoom(const nsRect& r) const {
    ++(*counts)[7];
    return {r.x / divisor, r.y / divisor, r.width / divisor, r.height / divisor};
  }
};
struct ComputedStyle {
  StyleZoom zoom;
  StyleZoom EffectiveZoom() const {
    ++(*zoom.counts)[1];
    return zoom;
  }
};
struct Display {
  StyleTransformBox mTransformBox;
};
struct nsIFrame {
  mutable Counters counts{};
  bool svg;
  nsRect content, border, svgRect;
  ComputedStyle style;
  Display display;
  const ComputedStyle* Style() const { ++counts[0]; return &style; }
  bool HasAnyStateBits(unsigned bits) const { ++counts[2]; return svg && (bits & NS_FRAME_SVG_LAYOUT); }
  const Display* StyleDisplay() const { ++counts[3]; return &display; }
  nsRect GetContentRectRelativeToSelf() const { ++counts[4]; return content; }
  nsRect GetRect() const { ++counts[5]; return border; }
};
nsRect GetSVGBox(const nsIFrame* frame) {
  ++frame->counts[6];
  return frame->svgRect;
}
struct TransformReferenceBox {
  bool mIsCached;
  const nsIFrame* mFrame;
  bool mNeedsUnzooming;
  nsRect mBox;
  void EnsureDimensionsAreCached();
};
