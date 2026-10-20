#include <cstdint>
#include <iostream>
#include <optional>
#include <vector>
using nscoord=int32_t;
constexpr nscoord nscoord_MIN=-1073741823;
struct nsPoint { nscoord x,y; };
struct nsSize {
  nscoord width,height;
  nsSize operator-(nsSize other) const { return {width-other.width,height-other.height}; }
};
namespace mozilla {
struct WritingMode {
  int mode;
  bool reverse;
  bool IsVertical() const { return mode!=0; }
  bool IsVerticalLR() const { return mode==1; }
  bool IsInlineReversed() const { return reverse; }
};
struct LogicalPoint {
  WritingMode mWritingMode{};
  nscoord inlinePosition,blockPosition;
  nscoord& I() { return inlinePosition; }
  nscoord& B() { return blockPosition; }
  nscoord B(WritingMode) const { return blockPosition; }
/* LOGICAL */
};
}
using mozilla::WritingMode;
std::vector<std::pair<size_t,bool>> queried;
struct Rect { nsSize size; nsSize Size() const { return size; } };
struct nsIFrame {
  size_t identity;
  nsPoint actual;
  std::optional<nsPoint> normal;
  Rect mRect;
  nsPoint GetPosition() const { return actual; }
  static int NormalPositionProperty() { return 0; }
  nsPoint GetProperty(int,bool* has) const {
    *has=normal.has_value();queried.emplace_back(identity,*has);
    return normal.value_or(nsPoint{0,0});
  }
  nsPoint GetNormalPosition(bool* aHasProperty=nullptr) const;
  mozilla::LogicalPoint GetLogicalNormalPosition(WritingMode,const nsSize&) const;
  mozilla::LogicalPoint GetLogicalPosition(WritingMode wm,const nsSize& size) const {
    return mozilla::LogicalPoint(wm,GetPosition(),size-mRect.Size());
  }
};
/* NORMAL */
/* NORMAL_LOGICAL */
struct FlexboxAxisTracker { bool reversed; bool IsMainAxisReversed() const { return reversed; } };
struct FlexItem {
  nsIFrame frame;
  nscoord first,last;
  const nsIFrame* Frame() const { return &frame; }
  nscoord ResolvedAscent(bool isFirst) const { return isFirst?first:last; }
};
struct FlexLine {
  std::vector<FlexItem> items;
  bool IsEmpty() const { return items.empty(); }
  const FlexItem& StartmostItem(const FlexboxAxisTracker& axis) const {
    return axis.IsMainAxisReversed()?items.back():items.front();
  }
  const FlexItem& EndmostItem(const FlexboxAxisTracker& axis) const {
    return axis.IsMainAxisReversed()?items.front():items.back();
  }
};
struct Layout { nscoord mAscent,mAscentForLast; FlexLine mLines; };
const FlexLine& StartmostLine(const FlexLine& line,const FlexboxAxisTracker&) { return line; }
const FlexLine& EndmostLine(const FlexLine& line,const FlexboxAxisTracker&) { return line; }
struct Desired {
  nsSize physical;
  nsSize GetPhysicalSize(WritingMode) const { return physical; }
  nscoord BSize(WritingMode mode) const { return mode.IsVertical()?physical.width:physical.height; }
};
void run(size_t id,WritingMode flexWM,bool reverse,nscoord old,FlexLine line) {
  queried.clear();
  Layout aFlr{old,old,line};
  FlexboxAxisTracker aAxisTracker{reverse};
  Desired desiredSizeInFlexWM{{160,80}};
/* FIRST */
/* LAST */
  std::cout << id << '|' << aFlr.mAscent << '|' << aFlr.mAscentForLast << '|';
  for(size_t i=0;i<queried.size();++i) {
    if(i) std::cout << ',';
    std::cout << queried[i].first << ':' << queried[i].second;
  }
  std::cout << '\n';
}
int main() {
/* CASES */
}
