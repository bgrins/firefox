#include <cassert>
#include <cstdint>
#include <iostream>

#define MOZ_ASSERT(value) assert(value)
using nscoord = int32_t;

struct nsSize {
  nscoord width;
  nscoord height;
  bool operator==(const nsSize&) const = default;
};

struct WritingMode {
  bool vertical;
  bool IsVertical() const { return vertical; }
};

struct LogicalSize {
  nsSize physical;
  LogicalSize(WritingMode, nsSize size) : physical(size) {}
  nscoord ISize(WritingMode wm) const {
    return wm.IsVertical() ? physical.height : physical.width;
  }
};

enum class StyleContainerType : uint8_t {
  NORMAL = 0,
  INLINE_SIZE = 1,
  SIZE = 2,
  SCROLL_STATE = 4,
};

bool operator&(StyleContainerType a, StyleContainerType b) {
  return (uint8_t(a) & uint8_t(b)) != 0;
}

struct ContainSizeAxes {
  bool mIContained;
  bool mBContained;
  bool IsAny() const { return mIContained || mBContained; }
};

struct Rect {
  nsSize size;
  nsSize Size() const { return size; }
};

struct Display {
  StyleContainerType mContainerType;
};

struct nsIFrame {
  nsSize border;
  nsSize content;
  WritingMode wm;
  ContainSizeAxes axes;
  Display display;
  nsSize GetSize() const { return border; }
  Rect GetContentRectRelativeToSelf() const { return {content}; }
  WritingMode GetWritingMode() const { return wm; }
  ContainSizeAxes GetContainSizeAxes() const { return axes; }
  const Display* StyleDisplay() const { return &display; }
};

struct Element {
  const nsIFrame* frame;
  const nsIFrame* GetPrimaryFrame() const { return frame; }
};
