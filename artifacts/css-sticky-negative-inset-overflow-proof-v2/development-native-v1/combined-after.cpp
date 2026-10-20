#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>
#define MOZ_ASSERT(...) assert((__VA_ARGS__,true))
#undef MOZ_ASSERT
#define MOZ_ASSERT(x,...) assert(x)
#define NS_ASSERTION(x,...) assert(x)
#define MOZ_ASSERT_UNREACHABLE(...) ((void)0)
#define MOZ_ALWAYS_INLINE inline
#define MOZ_UNLIKELY(x) (x)
using nscoord=int32_t;
constexpr nscoord nscoord_MAX=(1<<30)-1;
constexpr nscoord nscoord_MIN=-nscoord_MAX;
constexpr nscoord NS_AUTOOFFSET=nscoord_MAX;
constexpr nscoord NS_UNCONSTRAINEDSIZE=nscoord_MAX;
constexpr uint32_t SKIP_SCROLLED_FRAME=1;
std::vector<int> providerTrace;
namespace mozilla {
template<class T> struct CheckedInt {
 int64_t value; CheckedInt(T x):value(x){}
 CheckedInt& operator+=(T x){value+=int64_t(x);return *this;}
 bool isValid()const{return value>=std::numeric_limits<T>::min()&&value<=std::numeric_limits<T>::max();}
};
enum Side {eSideTop,eSideRight,eSideBottom,eSideLeft};
enum class LogicalSide {BStart,BEnd,IStart,IEnd};
enum class LogicalEdge {Start,End};
bool IsBlock(LogicalSide s){return s==LogicalSide::BStart||s==LogicalSide::BEnd;}
LogicalEdge GetEdge(LogicalSide s){return s==LogicalSide::BStart||s==LogicalSide::IStart?LogicalEdge::Start:LogicalEdge::End;}
struct StyleWritingMode {
 uint8_t _0=0;
 constexpr explicit operator bool()const{return _0!=0;}
 friend constexpr StyleWritingMode operator&(StyleWritingMode a,StyleWritingMode b){return {uint8_t(a._0&b._0)};}
 static const StyleWritingMode VERTICAL,VERTICAL_LR,INLINE_REVERSED,LINE_INVERTED,RTL;
};
inline constexpr StyleWritingMode StyleWritingMode::VERTICAL{1};
inline constexpr StyleWritingMode StyleWritingMode::INLINE_REVERSED{2};
inline constexpr StyleWritingMode StyleWritingMode::VERTICAL_LR{4};
inline constexpr StyleWritingMode StyleWritingMode::LINE_INVERTED{8};
inline constexpr StyleWritingMode StyleWritingMode::RTL{16};
constexpr uint8_t kWritingModeSidewaysMask=4;
struct WritingMode {
 StyleWritingMode mWritingMode;
 explicit WritingMode(uint8_t raw=0):mWritingMode{raw}{}
 bool IsBidiLTR()const{return !IsBidiRTL();}
 bool IsVertical() const {
    return !!(mWritingMode & StyleWritingMode::VERTICAL);
  }
bool IsInlineReversed() const {
    return !!(mWritingMode & StyleWritingMode::INLINE_REVERSED);
  }
bool IsBidiRTL() const { return !!(mWritingMode & StyleWritingMode::RTL); }
static mozilla::Side PhysicalSideForBlockAxis(uint8_t aWritingModeValue,
                                                LogicalEdge aEdge) {
    // indexes are StyleWritingModeProperty values, which are the same as these
    // two-bit values:
    //   bit 0 = the StyleWritingMode::VERTICAL value
    //   bit 1 = the StyleWritingMode::VERTICAL_LR value
    static const mozilla::Side kLogicalBlockSides[][2] = {
        {eSideTop, eSideBottom},  // horizontal-tb
        {eSideRight, eSideLeft},  // vertical-rl
        {eSideBottom, eSideTop},  // (horizontal-bt)
        {eSideLeft, eSideRight},  // vertical-lr
    };

    // Ignore the SidewaysMask bit of the writing-mode value, as this has no
    // effect on the side mappings.
    aWritingModeValue &= ~kWritingModeSidewaysMask;

    // What's left of the writing-mode should be in the range 0-3:
    NS_ASSERTION(aWritingModeValue < 4, "invalid aWritingModeValue value");

    return kLogicalBlockSides[aWritingModeValue][static_cast<uint8_t>(aEdge)];
  }
mozilla::Side PhysicalSideForInlineAxis(LogicalEdge aEdge) const {
    // indexes are four-bit values:
    //   bit 0 = the StyleWritingMode::VERTICAL value
    //   bit 1 = the StyleWritingMode::INLINE_REVERSED value
    //   bit 2 = the StyleWritingMode::VERTICAL_LR value
    //   bit 3 = the StyleWritingMode::LINE_INVERTED value
    // Not all of these combinations can actually be specified via CSS: there
    // is no horizontal-bt writing-mode, and no text-orientation value that
    // produces "inverted" text. (The former 'sideways-left' value, no longer
    // in the spec, would have produced this in vertical-rl mode.)
    static const mozilla::Side kLogicalInlineSides[][2] = {
        {eSideLeft, eSideRight},  // horizontal-tb               ltr
        {eSideTop, eSideBottom},  // vertical-rl                 ltr
        {eSideRight, eSideLeft},  // horizontal-tb               rtl
        {eSideBottom, eSideTop},  // vertical-rl                 rtl
        {eSideRight, eSideLeft},  // (horizontal-bt)  (inverted) ltr
        {eSideTop, eSideBottom},  // sideways-lr                 rtl
        {eSideLeft, eSideRight},  // (horizontal-bt)  (inverted) rtl
        {eSideBottom, eSideTop},  // sideways-lr                 ltr
        {eSideLeft, eSideRight},  // horizontal-tb    (inverted) rtl
        {eSideTop, eSideBottom},  // vertical-rl      (inverted) rtl
        {eSideRight, eSideLeft},  // horizontal-tb    (inverted) ltr
        {eSideBottom, eSideTop},  // vertical-rl      (inverted) ltr
        {eSideLeft, eSideRight},  // (horizontal-bt)             ltr
        {eSideTop, eSideBottom},  // vertical-lr                 ltr
        {eSideRight, eSideLeft},  // (horizontal-bt)             rtl
        {eSideBottom, eSideTop},  // vertical-lr                 rtl
    };

    // Inline axis sides depend on all three of writing-mode, text-orientation
    // and direction, which are encoded in the StyleWritingMode::VERTICAL,
    // StyleWritingMode::INLINE_REVERSED, StyleWritingMode::VERTICAL_LR and
    // StyleWritingMode::LINE_INVERTED bits.  Use these four bits to index into
    // kLogicalInlineSides.
    static_assert(StyleWritingMode::VERTICAL._0 == 0x01 &&
                      StyleWritingMode::INLINE_REVERSED._0 == 0x02 &&
                      StyleWritingMode::VERTICAL_LR._0 == 0x04 &&
                      StyleWritingMode::LINE_INVERTED._0 == 0x08,
                  "Unexpected values for StyleWritingMode constants!");
    uint8_t index = mWritingMode._0 & 0x0F;
    return kLogicalInlineSides[index][static_cast<uint8_t>(aEdge)];
  }
mozilla::Side PhysicalSide(LogicalSide aSide) const {
    if (IsBlock(aSide)) {
      static_assert(StyleWritingMode::VERTICAL._0 == 0x01 &&
                        StyleWritingMode::VERTICAL_LR._0 == 0x04,
                    "Unexpected values for StyleWritingMode constants!");
      const uint8_t wm =
          ((mWritingMode & StyleWritingMode::VERTICAL_LR)._0 >> 1) |
          (mWritingMode & StyleWritingMode::VERTICAL)._0;
      return PhysicalSideForBlockAxis(wm, GetEdge(aSide));
    }

    return PhysicalSideForInlineAxis(GetEdge(aSide));
  }
};
template<class T> struct Maybe:std::optional<T>{using std::optional<T>::optional; bool isSome()const{return this->has_value();}};
namespace layers {enum class ScrollDirection {eHorizontal,eVertical};}
class ScrollContainerFrame;
class StickyScrollContainer;
}
using namespace mozilla;
struct nsPoint {
 nscoord x=0,y=0;
 nsPoint()=default;nsPoint(nscoord a,nscoord b):x(a),y(b){}
 friend nsPoint operator+(nsPoint a,nsPoint b){return {a.x+b.x,a.y+b.y};}
 friend nsPoint operator-(nsPoint a,nsPoint b){return {a.x-b.x,a.y-b.y};}
};
struct nsSize {nscoord width=0,height=0;};
template<class Coord> struct BaseMargin {
 using SideT=mozilla::Side;
 Coord top,right,bottom,left;
 constexpr BaseMargin() : top(0), right(0), bottom(0), left(0) {}
constexpr BaseMargin(Coord aTop, Coord aRight, Coord aBottom, Coord aLeft)
      : top(aTop), right(aRight), bottom(aBottom), left(aLeft) {}
Coord LeftRight() const { return left + right; }
Coord TopBottom() const { return top + bottom; }
Coord& Side(SideT aSide) {
    // This is ugly!
    return *(&top + int(aSide));
  }
Coord Side(SideT aSide) const {
    // This is ugly!
    return *(&top + int(aSide));
  }
};
struct nsMargin:BaseMargin<nscoord> {
 using BaseMargin::BaseMargin;
 bool operator==(const nsMargin& b)const{return top==b.top&&right==b.right&&bottom==b.bottom&&left==b.left;}
};
struct nsRect {
 using T=nscoord;using MarginT=nsMargin;using Sub=nsRect;
 nscoord x=0,y=0,width=0,height=0;
 nsRect()=default;nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}
 nscoord X()const{return x;}nscoord Y()const{return y;}
 nscoord Width()const{return width;}nscoord Height()const{return height;}
 nscoord XMost()const{return x+width;}nscoord YMost()const{return y+height;}
 nsPoint TopLeft()const{return {x,y};}
 void MoveBy(nsPoint p){x+=p.x;y+=p.y;}
 bool IsEmpty()const{return width<=0||height<=0;}
 bool Overflows()const;
 [[nodiscard]] nsRect SaturatingUnion(const nsRect& aRect) const {
    if (IsEmpty()) {
      return aRect;
    } else if (aRect.IsEmpty()) {
      return *static_cast<const nsRect*>(this);
    } else {
      return SaturatingUnionEdges(aRect);
    }
  }
[[nodiscard]] nsRect SaturatingUnionEdges(const nsRect& aRect) const {
    nscoord resultX = std::min(aRect.X(), x);
    int64_t w =
        std::max(int64_t(aRect.X()) + aRect.Width(), int64_t(x) + width) -
        resultX;
    if (MOZ_UNLIKELY(w > nscoord_MAX)) {
      // Clamp huge negative x to nscoord_MIN / 2 and try again.
      resultX = std::max(resultX, nscoord_MIN / 2);
      w = std::max(int64_t(aRect.X()) + aRect.Width(), int64_t(x) + width) -
          resultX;
      if (MOZ_UNLIKELY(w > nscoord_MAX)) {
        w = nscoord_MAX;
      }
    }

    nscoord resultY = std::min(aRect.y, y);
    int64_t h =
        std::max(int64_t(aRect.Y()) + aRect.Height(), int64_t(y) + height) -
        resultY;
    if (MOZ_UNLIKELY(h > nscoord_MAX)) {
      // Clamp huge negative y to nscoord_MIN / 2 and try again.
      resultY = std::max(resultY, nscoord_MIN / 2);
      h = std::max(int64_t(aRect.Y()) + aRect.Height(), int64_t(y) + height) -
          resultY;
      if (MOZ_UNLIKELY(h > nscoord_MAX)) {
        h = nscoord_MAX;
      }
    }
    return nsRect(resultX, resultY, nscoord(w), nscoord(h));
  }
[[nodiscard]] nsRect UnionEdges(const nsRect& aRect) const {
    return SaturatingUnionEdges(aRect);
  }
[[nodiscard]] nsRect Union(const nsRect& aRect) const {
    return SaturatingUnion(aRect);
  }
void UnionRect(const nsRect& aRect1, const nsRect& aRect2) {
    *this = aRect1.Union(aRect2);
  }
void Deflate(const MarginT& aMargin) {
    x += aMargin.left;
    y += aMargin.top;
    width = std::max(T(0), width - aMargin.LeftRight());
    height = std::max(T(0), height - aMargin.TopBottom());
  }
MarginT operator-(const Sub& aRect) const {
    return MarginT(aRect.y - y, XMost() - aRect.XMost(),
                   YMost() - aRect.YMost(), aRect.x - x);
  }
void SetLeftEdge(T aX) {
    width = XMost() - aX;
    x = aX;
  }
void SetRightEdge(T aXMost) { width = aXMost - x; }
void SetTopEdge(T aY) {
    height = YMost() - aY;
    y = aY;
  }
void SetBottomEdge(T aYMost) { height = aYMost - y; }
};
bool nsRect::Overflows() const {
  mozilla::CheckedInt<int32_t> xMost = this->x;
  xMost += this->width;
  mozilla::CheckedInt<int32_t> yMost = this->y;
  yMost += this->height;
  return !xMost.isValid() || !yMost.isValid();
}
template<class T,class Sub,class Point,class Rect>
struct BaseRectAbsolute {
 protected:
  T left, top, right, bottom;

 public:
  BaseRectAbsolute() : left(0), top(0), right(0), bottom(0) {}
  BaseRectAbsolute(T aLeft, T aTop, T aRight, T aBottom)
      : left(aLeft), top(aTop), right(aRight), bottom(aBottom) {}

  MOZ_ALWAYS_INLINE T X() const { return left; }
  MOZ_ALWAYS_INLINE T Y() const { return top; }
  MOZ_ALWAYS_INLINE T Width() const { return right - left; }
  MOZ_ALWAYS_INLINE T Height() const { return bottom - top; }
  MOZ_ALWAYS_INLINE T XMost() const { return right; }
  MOZ_ALWAYS_INLINE T YMost() const { return bottom; }
  MOZ_ALWAYS_INLINE const T& Left() const { return left; }
  MOZ_ALWAYS_INLINE const T& Right() const { return right; }
  MOZ_ALWAYS_INLINE const T& Top() const { return top; }
  MOZ_ALWAYS_INLINE const T& Bottom() const { return bottom; }
  MOZ_ALWAYS_INLINE T& Left() { return left; }
  MOZ_ALWAYS_INLINE T& Right() { return right; }
  MOZ_ALWAYS_INLINE T& Top() { return top; }
  MOZ_ALWAYS_INLINE T& Bottom() { return bottom; }
  // For integer coordinates, widen to 64-bit before multiplying so the area of
  // a large rect does not overflow. Floating-point coordinates are unchanged.
  auto Area() const {
    if constexpr (std::is_integral_v<T>) {
      return int64_t(Width()) * int64_t(Height());
    } else {
      return Width() * Height();
    }
  }

  void Inflate(T aD) { Inflate(aD, aD); }
  void Inflate(T aDx, T aDy) {
    left -= aDx;
    top -= aDy;
    right += aDx;
    bottom += aDy;
  }

  MOZ_ALWAYS_INLINE void SetBox(T aLeft, T aTop, T aRight, T aBottom) {
    left = aLeft;
    top = aTop;
    right = aRight;
    bottom = aBottom;
  }
  void SetLeftEdge(T aLeft) { left = aLeft; }
  void SetRightEdge(T aRight) { right = aRight; }
  void SetTopEdge(T aTop) { top = aTop; }
  void SetBottomEdge(T aBottom) { bottom = aBottom; }

  static Sub FromRect(const Rect& aRect) {
    if (aRect.Overflows()) {
      return Sub();
    }
    return Sub(aRect.x, aRect.y, aRect.XMost(), aRect.YMost());
  }

  [[nodiscard]] Sub Intersect(const Sub& aOther) const {
    Sub result;
    result.left = std::max<T>(left, aOther.left);
    result.top = std::max<T>(top, aOther.top);
    result.right = std::min<T>(right, aOther.right);
    result.bottom = std::min<T>(bottom, aOther.bottom);
    if (result.right < result.left || result.bottom < result.top) {
      result.SizeTo(0, 0);
    }
    return result;
  }

  bool IsEmpty() const { return right <= left || bottom <= top; }

  bool IsEqualEdges(const Sub& aOther) const {
    return left == aOther.left && top == aOther.top && right == aOther.right &&
           bottom == aOther.bottom;
  }

  bool IsEqualInterior(const Sub& aRect) const {
    return IsEqualEdges(aRect) || (IsEmpty() && aRect.IsEmpty());
  }

  MOZ_ALWAYS_INLINE void MoveBy(T aDx, T aDy) {
    left += aDx;
    right += aDx;
    top += aDy;
    bottom += aDy;
  }
  MOZ_ALWAYS_INLINE void MoveBy(const Point& aPoint) {
    left += aPoint.x;
    right += aPoint.x;
    top += aPoint.y;
    bottom += aPoint.y;
  }
  MOZ_ALWAYS_INLINE void SizeTo(T aWidth, T aHeight) {
    right = left + aWidth;
    bottom = top + aHeight;
  }

  bool Contains(const Sub& aRect) const {
    return aRect.IsEmpty() || (left <= aRect.left && aRect.right <= right &&
                               top <= aRect.top && aRect.bottom <= bottom);
  }
  bool Contains(T aX, T aY) const {
    return (left <= aX && aX < right && top <= aY && aY < bottom);
  }

  bool Intersects(const Sub& aRect) const {
    return !IsEmpty() && !aRect.IsEmpty() && left < aRect.right &&
           aRect.left < right && top < aRect.bottom && aRect.top < bottom;
  }

  void SetEmpty() { left = right = top = bottom = 0; }

  // Returns the smallest rectangle that contains both the area of both
  // this and aRect. Thus, empty input rectangles are ignored.
  // Note: if both rectangles are empty, returns aRect.
  // WARNING! This is not safe against overflow, prefer using SafeUnion instead
  // when dealing with int-based rects.
  [[nodiscard]] Sub Union(const Sub& aRect) const {
    if (IsEmpty()) {
      return aRect;
    } else if (aRect.IsEmpty()) {
      return *static_cast<const Sub*>(this);
    } else {
      return UnionEdges(aRect);
    }
  }
  // Returns the smallest rectangle that contains both the points (including
  // edges) of both aRect1 and aRect2.
  // Thus, empty input rectangles are allowed to affect the result.
  // WARNING! This is not safe against overflow, prefer using SafeUnionEdges
  // instead when dealing with int-based rects.
  [[nodiscard]] Sub UnionEdges(const Sub& aRect) const {
    Sub result;
    result.left = std::min(left, aRect.left);
    result.top = std::min(top, aRect.top);
    result.right = std::max(XMost(), aRect.XMost());
    result.bottom = std::max(YMost(), aRect.YMost());
    return result;
  }

  // Scale 'this' by aScale without doing any rounding.
  void Scale(T aScale) { Scale(aScale, aScale); }
  // Scale 'this' by aXScale and aYScale, without doing any rounding.
  void Scale(T aXScale, T aYScale) {
    right = XMost() * aXScale;
    bottom = YMost() * aYScale;
    left = left * aXScale;
    top = top * aYScale;
  }
  // Scale 'this' by aScale, converting coordinates to integers so that the
  // result is the smallest integer-coordinate rectangle containing the
  // unrounded result. Note: this can turn an empty rectangle into a non-empty
  // rectangle
  void ScaleRoundOut(double aScale) { ScaleRoundOut(aScale, aScale); }
  // Scale 'this' by aXScale and aYScale, converting coordinates to integers so
  // that the result is the smallest integer-coordinate rectangle containing the
  // unrounded result.
  // Note: this can turn an empty rectangle into a non-empty rectangle
  void ScaleRoundOut(double aXScale, double aYScale) {
    right = static_cast<T>(ceil(double(XMost()) * aXScale));
    bottom = static_cast<T>(ceil(double(YMost()) * aYScale));
    left = static_cast<T>(floor(double(left) * aXScale));
    top = static_cast<T>(floor(double(top) * aYScale));
  }
  // Scale 'this' by aScale, converting coordinates to integers so that the
  // result is the largest integer-coordinate rectangle contained by the
  // unrounded result.
  void ScaleRoundIn(double aScale) { ScaleRoundIn(aScale, aScale); }
  // Scale 'this' by aXScale and aYScale, converting coordinates to integers so
  // that the result is the largest integer-coordinate rectangle contained by
  // the unrounded result.
  void ScaleRoundIn(double aXScale, double aYScale) {
    right = static_cast<T>(floor(double(XMost()) * aXScale));
    bottom = static_cast<T>(floor(double(YMost()) * aYScale));
    left = static_cast<T>(ceil(double(left) * aXScale));
    top = static_cast<T>(ceil(double(top) * aYScale));
  }
  // Scale 'this' by 1/aScale, converting coordinates to integers so that the
  // result is the smallest integer-coordinate rectangle containing the
  // unrounded result. Note: this can turn an empty rectangle into a non-empty
  // rectangle
  void ScaleInverseRoundOut(double aScale) {
    ScaleInverseRoundOut(aScale, aScale);
  }
  // Scale 'this' by 1/aXScale and 1/aYScale, converting coordinates to integers
  // so that the result is the smallest integer-coordinate rectangle containing
  // the unrounded result. Note: this can turn an empty rectangle into a
  // non-empty rectangle
  void ScaleInverseRoundOut(double aXScale, double aYScale) {
    right = static_cast<T>(ceil(double(XMost()) / aXScale));
    bottom = static_cast<T>(ceil(double(YMost()) / aYScale));
    left = static_cast<T>(floor(double(left) / aXScale));
    top = static_cast<T>(floor(double(top) / aYScale));
  }
  // Scale 'this' by 1/aScale, converting coordinates to integers so that the
  // result is the largest integer-coordinate rectangle contained by the
  // unrounded result.
  void ScaleInverseRoundIn(double aScale) {
    ScaleInverseRoundIn(aScale, aScale);
  }
  // Scale 'this' by 1/aXScale and 1/aYScale, converting coordinates to integers
  // so that the result is the largest integer-coordinate rectangle contained by
  // the unrounded result.
  void ScaleInverseRoundIn(double aXScale, double aYScale) {
    right = static_cast<T>(floor(double(XMost()) / aXScale));
    bottom = static_cast<T>(floor(double(YMost()) / aYScale));
    left = static_cast<T>(ceil(double(left) / aXScale));
    top = static_cast<T>(ceil(double(top) / aYScale));
  }

  /**
   * Translate this rectangle to be inside aRect. If it doesn't fit inside
   * aRect then the dimensions that don't fit will be shrunk so that they
   * do fit. The resulting rect is returned.
   */
  [[nodiscard]] Sub MoveInsideAndClamp(const Sub& aRect) const {
    T newLeft = std::max(aRect.left, left);
    T newTop = std::max(aRect.top, top);
    T width = std::min(aRect.Width(), Width());
    T height = std::min(aRect.Height(), Height());
    Sub rect(newLeft, newTop, newLeft + width, newTop + height);
    newLeft = std::min(rect.right, aRect.right) - width;
    newTop = std::min(rect.bottom, aRect.bottom) - height;
    rect.MoveBy(newLeft - rect.left, newTop - rect.top);
    return rect;
  }

  friend std::ostream& operator<<(
      std::ostream& stream,
      const BaseRectAbsolute<T, Sub, Point, Rect>& aRect) {
    return stream << "(l=" << aRect.left << ", t=" << aRect.top
                  << ", r=" << aRect.right << ", b=" << aRect.bottom << ')';
  }
};
struct nsRectAbsolute:BaseRectAbsolute<nscoord,nsRectAbsolute,nsPoint,nsRect>{using BaseRectAbsolute::BaseRectAbsolute;};
struct nsStyleDisplay{};
enum class StyleDirection {Ltr,Rtl};
struct nsStyleVisibility {StyleDirection mDirection=StyleDirection::Ltr;};
enum class PseudoStyleType {Normal,MozScrolledContent};
struct FakeStyle {PseudoStyleType type=PseudoStyleType::Normal;PseudoStyleType GetPseudoType()const{return type;}};
struct LengthPercentage {
 nscoord value;
 bool HasPercent()const{return false;}
 nscoord Resolve(nscoord)const{providerTrace.push_back(950);return value;}
};
struct ResolvedSide {
 bool automatic=true;nscoord length=0;
 bool IsAuto()const{return automatic;}
 LengthPercentage AsLengthPercentage()const{return {length};}
};
struct AnchorPosOffsetResolutionParams {
 struct Params {void* frame;int property;};
 static int UseCBFrameSize(Params){return 0;}
};
struct StylePositionProperty {static constexpr int Sticky=1;};
struct nsStylePosition {
 ResolvedSide sides[4];
 const ResolvedSide* GetAnchorResolvedInset(Side s,int)const{providerTrace.push_back(100+int(s));return &sides[s];}
};
struct nsIFrame {
 int id=0;
 nsIFrame* parent=nullptr;nsIFrame* continuation=nullptr;nsIFrame* first=nullptr;
 ScrollContainerFrame* nearestScroll=nullptr;
 bool rowGroup=false,lineParticipant=false,blockWrapper=false,tableRow=false,absolute=false,sticky=true;
 nsPoint position,normal,offsetToScroll,transform;
 bool hasNormal=true,hasComputed=true;
 nsMargin offsets,padding,border;
 nsRect borderBox,marginBox,contentBox,overflow;
 WritingMode mWritingMode;
 nsStyleDisplay display;nsStyleVisibility visibility;FakeStyle style;nsStylePosition stylePosition;
 const nsStyleVisibility* StyleVisibility()const{return &visibility;}
 nsIFrame* GetParent()const{return parent;}
 bool IsLineParticipant()const{return lineParticipant;}bool IsBlockWrapper()const{return blockWrapper;}bool IsTableRowFrame()const{return tableRow;}
 bool IsBlockContainer()const;
 bool IsAbsolutelyPositioned(const nsStyleDisplay*)const{return absolute;}
 const nsStyleDisplay* StyleDisplay()const{return &display;}
 const FakeStyle* Style()const{return &style;}
 nsIFrame* GetContainingBlock(uint32_t,const nsStyleDisplay*)const;
 nsIFrame* GetContainingBlock()const{providerTrace.push_back(200+id);return GetContainingBlock(0,StyleDisplay());}
 bool IsTableRowGroupFrame()const{return rowGroup;}
 WritingMode GetWritingMode()const{providerTrace.push_back(300+id);return mWritingMode;}
 bool IsStickyPositioned()const{return sticky;}
 nsPoint GetPosition()const{return position;}
 nsPoint GetNormalPosition(bool* has=nullptr)const;
 static int ComputedOffsetProperty(){return 0;}
 static int NormalPositionProperty(){return 1;}
 const nsMargin* GetProperty(int)const{providerTrace.push_back(400+id);return hasComputed?&offsets:nullptr;}
 nsPoint GetProperty(int,bool* has)const{*has=hasNormal;return normal;}
 void SetOrUpdateDeletableProperty(int,nsMargin v){providerTrace.push_back(500+id);hasComputed=true;offsets=v;}
 void SetPosition(nsPoint p){providerTrace.push_back(600+id);auto d=p-position;borderBox.MoveBy(d);marginBox.MoveBy(d);contentBox.MoveBy(d);position=p;}
 nsMargin GetUsedPadding()const{return padding;}nsMargin GetUsedBorder()const{return border;}
 nsRect ScrollableOverflowRectRelativeToSelf()const{return overflow;}
 nsPoint GetOffsetTo(nsIFrame*)const{return offsetToScroll;}
 const nsStylePosition* StylePosition()const{return &stylePosition;}
};
namespace mozilla {
struct FakePresContext {bool cross=false;bool IsRootContentDocumentCrossProcess()const{return cross;}};
struct FakePresShell {nsSize fixedSize;nsSize GetFixedViewportSize()const{return fixedSize;}};
class ScrollContainerFrame {
 public:
 nsIFrame* scrolled=nullptr;StickyScrollContainer* stickyContainer=nullptr;nsSize size;bool root=false;
 FakePresContext context;FakePresShell shell;
 nsIFrame* GetScrolledFrame()const{return scrolled;}
 nsSize GetScrolledFrameSize()const{providerTrace.push_back(700);return size;}
 bool IsRootScrollFrameOfDocument()const{return root;}
 const FakePresContext* PresContext()const{return &context;}
 const FakePresShell* PresShell()const{return &shell;}
 StickyScrollContainer* GetStickyContainer()const{return stickyContainer;}
};
struct OverflowChangedTracker {
 static constexpr int CHILDREN_CHANGED=1;
 void SetSubtreeRoot(nsIFrame*){providerTrace.push_back(800);}
 void AddFrame(nsIFrame* frame,int){providerTrace.push_back(810+frame->id);}
 void Flush(){providerTrace.push_back(899);}
};
struct DepthOrderedFrameList {
 std::vector<nsIFrame*> frames;
 const std::vector<nsIFrame*>& IterFromShallowest()const{return frames;}
};
class StickyScrollContainer {
 public:
 enum class StickyLimitSpace:uint8_t {RelativeToCurrentScroll,IgnoreCurrentScroll};
 struct StickyLimits {
    // Based on the scroll container.
    nsRectAbsolute mStick;
    // Based on the containing block.
    nsRect mContain;
  };
 struct StickyScrollRange {nscoord mScrollPosition=0,mMaxOffset=0;};
 struct StickyScrollRanges {Maybe<StickyScrollRange> mStartSide,mEndSide;};
 ScrollContainerFrame* mScrollContainerFrame;nsPoint mScrollPosition;DepthOrderedFrameList mFrames;
 explicit StickyScrollContainer(ScrollContainerFrame* s):mScrollContainerFrame(s){}
 ScrollContainerFrame* ScrollContainer()const{return mScrollContainerFrame;}
 static StickyScrollContainer* GetForFrame(const nsIFrame*);
 static void ComputeStickyOffsets(nsIFrame*);
 StickyLimits ComputeStickyLimits(nsIFrame*,StickyLimitSpace=StickyLimitSpace::RelativeToCurrentScroll)const;
 nsPoint ComputePosition(nsIFrame*)const;nsPoint ComputePositionIgnoringScrolling(nsIFrame*)const;
 nsPoint DoComputePosition(nsIFrame*,StickyLimitSpace)const;
 nsPoint ComputeTranslationIgnoringScrolling(const nsIFrame*)const;
 bool IsStuckInYDirection(nsIFrame*)const;
 void GetScrollRanges(nsIFrame*,nsRectAbsolute*,nsRectAbsolute*)const;
 StickyScrollRanges GetStickyScrollRangesForAxis(const nsIFrame*,layers::ScrollDirection)const;
 void PositionContinuations(nsIFrame*);void UpdatePositions(nsPoint,nsIFrame*);
};
}
namespace nsLayoutUtils {
constexpr int SCROLLABLE_SAME_DOC=1,SCROLLABLE_STOP_AT_PAGE=2,SCROLLABLE_INCLUDE_HIDDEN=4;
namespace GetAllInFlowRectsFlag {constexpr int UseContentBox=1,UseMarginBoxWithAutoResolvedAsZero=2;}
using GetAllInFlowRectsFlags=int;
bool IsFirstContinuationOrIBSplitSibling(nsIFrame* f){return !f->first||f->first==f;}
bool IsProperAncestorFrame(nsIFrame* a,nsIFrame* f){while(f){if(f==a)return true;f=f->parent;}return false;}
nsIFrame* FirstContinuationOrIBSplitSibling(const nsIFrame* f){return f->first?f->first:const_cast<nsIFrame*>(f);}
nsIFrame* GetNextContinuationOrIBSplitSibling(nsIFrame* f){return f->continuation;}
ScrollContainerFrame* GetNearestScrollContainerFrame(nsIFrame* f,int flags){providerTrace.push_back(900+flags);return f?f->nearestScroll:nullptr;}
static nscoord ComputeCBDependentValue(nscoord aPercentBasis,
                                         const LengthPercentage& aCoord) {
    NS_ASSERTION(aPercentBasis != NS_UNCONSTRAINEDSIZE || !aCoord.HasPercent(),
                 "Have unconstrained percentage basis when percentage "
                 "resolution needed; this should only result from very "
                 "large sizes, not attempts at intrinsic size calculation");
    return aCoord.Resolve(aPercentBasis);
  }
void TransformRect(nsIFrame* frame,nsIFrame*,nsRect& r){providerTrace.push_back(1000+frame->id);r.MoveBy(frame->transform);}
struct RectAccumulator {
 nsRect mResultRect,mFirstRect;bool mSeenFirstRect=false;
 void AddRect(const nsRect&);
};
void GetAllInFlowRects(nsIFrame* f,const nsIFrame*,RectAccumulator* cb,int flags){
 providerTrace.push_back(1100+10*f->id+flags);
 for(auto* c=f;c;c=c->continuation)cb->AddRect(flags==1?c->contentBox:flags==2?c->marginBox:c->borderBox);
}
nsRect GetAllInFlowRectsUnion(nsIFrame*,const nsIFrame*,GetAllInFlowRectsFlags=0);
}
bool nsIFrame::IsBlockContainer() const {
  // The block wrappers we use to wrap blocks inside inlines aren't
  // described in the CSS spec.  We need to make them not be containing
  // blocks.
  // Since the parent of such a block is either a normal block or
  // another such pseudo, this shouldn't cause anything bad to happen.
  // Also the anonymous blocks inside table cells are not containing blocks.
  //
  // If we ever start skipping table row groups from being containing blocks,
  // you need to remove the StickyScrollContainer hack referencing bug 1421660.
  // Table rows are not containing blocks either
  return !IsLineParticipant() && !IsBlockWrapper() && !IsTableRowFrame();
}
static nsIFrame* GetNearestBlockContainer(nsIFrame* frame) {
  while (!frame->IsBlockContainer()) {
    frame = frame->GetParent();
    NS_ASSERTION(
        frame,
        "How come we got to the root frame without seeing a containing block?");
  }
  return frame;
}
nsIFrame* nsIFrame::GetContainingBlock(
    uint32_t aFlags, const nsStyleDisplay* aStyleDisplay) const {
  MOZ_ASSERT(aStyleDisplay == StyleDisplay());

  // Keep this in sync with MightBeContainingBlockFor in ReflowInput.cpp.

  if (!GetParent()) {
    return nullptr;
  }
  // MathML frames might have absolute positioning style, but they would
  // still be in-flow.  So we have to check to make sure that the frame
  // is really out-of-flow too.
  nsIFrame* f;
  if (IsAbsolutelyPositioned(aStyleDisplay)) {
    f = GetParent();  // the parent is always the containing block
  } else {
    f = GetNearestBlockContainer(GetParent());
  }

  if (aFlags & SKIP_SCROLLED_FRAME && f &&
      f->Style()->GetPseudoType() == PseudoStyleType::MozScrolledContent) {
    f = f->GetParent();
  }
  return f;
}
nsPoint nsIFrame::GetNormalPosition(bool* aHasProperty) const {
  bool hasProperty;
  nsPoint normalPosition = GetProperty(NormalPositionProperty(), &hasProperty);
  if (aHasProperty) {
    *aHasProperty = hasProperty;
  }
  return hasProperty ? normalPosition : GetPosition();
}
void nsLayoutUtils::RectAccumulator::AddRect(const nsRect& aRect) {
  mResultRect.UnionRect(mResultRect, aRect);
  if (!mSeenFirstRect) {
    mSeenFirstRect = true;
    mFirstRect = aRect;
  }
}
nsRect nsLayoutUtils::GetAllInFlowRectsUnion(nsIFrame* aFrame,
                                             const nsIFrame* aRelativeTo,
                                             GetAllInFlowRectsFlags aFlags) {
  RectAccumulator accumulator;
  GetAllInFlowRects(aFrame, aRelativeTo, &accumulator, aFlags);
  return accumulator.mResultRect.IsEmpty() ? accumulator.mFirstRect
                                           : accumulator.mResultRect;
}
namespace mozilla {
static constexpr nscoord gUnboundedNegative=nscoord_MIN/2;
static constexpr nscoord gUnboundedExtent=nscoord_MAX;
static constexpr nscoord gUnboundedPositive=gUnboundedNegative+gUnboundedExtent;
static ScrollContainerFrame* GetScrollContainerForStickyFrame(
    const nsIFrame* aFrame) {
  return nsLayoutUtils::GetNearestScrollContainerFrame(
      aFrame->GetParent(), nsLayoutUtils::SCROLLABLE_SAME_DOC |
                               nsLayoutUtils::SCROLLABLE_STOP_AT_PAGE |
                               nsLayoutUtils::SCROLLABLE_INCLUDE_HIDDEN);
}
StickyScrollContainer* StickyScrollContainer::GetForFrame(
    const nsIFrame* aFrame) {
  ScrollContainerFrame* scrollContainerFrame =
      GetScrollContainerForStickyFrame(aFrame);
  return scrollContainerFrame ? scrollContainerFrame->GetStickyContainer()
                              : nullptr;
}
static nscoord ComputeStickySideOffset(Side aSide,
                                       const nsStylePosition& aPosition,
                                       nscoord aPercentBasis) {
  // Guaranteed to resolve any use of anchor function as invalid.
  const auto& side = aPosition.GetAnchorResolvedInset(
      aSide, AnchorPosOffsetResolutionParams::UseCBFrameSize(
                 {nullptr, StylePositionProperty::Sticky}));
  if (side->IsAuto()) {
    return NS_AUTOOFFSET;
  }
  // Reserve NS_AUTOOFFSET for actual auto insets.
  return std::min(NS_AUTOOFFSET - 1,
                  nsLayoutUtils::ComputeCBDependentValue(
                      aPercentBasis, side->AsLengthPercentage()));
}
static nsSize GetScrollContainerSize(
    const ScrollContainerFrame* aScrollContainer) {
  if (aScrollContainer->IsRootScrollFrameOfDocument() &&
      aScrollContainer->PresContext()->IsRootContentDocumentCrossProcess()) {
    return aScrollContainer->PresShell()->GetFixedViewportSize();
  }
  return aScrollContainer->GetScrolledFrameSize();
}
void StickyScrollContainer::ComputeStickyOffsets(nsIFrame* aFrame) {
  ScrollContainerFrame* scrollContainerFrame =
      nsLayoutUtils::GetNearestScrollContainerFrame(
          aFrame->GetParent(), nsLayoutUtils::SCROLLABLE_SAME_DOC |
                                   nsLayoutUtils::SCROLLABLE_INCLUDE_HIDDEN);

  if (!scrollContainerFrame) {
    // Bail.
    return;
  }

  nsSize scrollContainerSize = GetScrollContainerSize(scrollContainerFrame);
  nsMargin computedOffsets;
  const nsStylePosition* position = aFrame->StylePosition();

  computedOffsets.left =
      ComputeStickySideOffset(eSideLeft, *position, scrollContainerSize.width);
  computedOffsets.right =
      ComputeStickySideOffset(eSideRight, *position, scrollContainerSize.width);
  computedOffsets.top =
      ComputeStickySideOffset(eSideTop, *position, scrollContainerSize.height);
  computedOffsets.bottom = ComputeStickySideOffset(eSideBottom, *position,
                                                   scrollContainerSize.height);

  aFrame->SetOrUpdateDeletableProperty(nsIFrame::ComputedOffsetProperty(),
                                       computedOffsets);
}
StickyScrollContainer::StickyLimits StickyScrollContainer::ComputeStickyLimits(
    nsIFrame* aFrame, StickyLimitSpace aSpace) const {
  NS_ASSERTION(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(aFrame),
               "Can't sticky position individual continuations");

  const nsPoint scrollPosition = aSpace == StickyLimitSpace::IgnoreCurrentScroll
                                     ? nsPoint()
                                     : mScrollPosition;

  const nsRect unbounded(gUnboundedNegative, gUnboundedNegative,
                         gUnboundedExtent, gUnboundedExtent);
  StickyLimits limits{nsRectAbsolute::FromRect(unbounded), unbounded};

  const nsMargin* computedOffsets =
      aFrame->GetProperty(nsIFrame::ComputedOffsetProperty());
  if (!computedOffsets) {
    // We haven't reflowed the scroll frame yet, so offsets haven't been
    // computed. Bail.
    return limits;
  }

  nsIFrame* scrolledFrame = mScrollContainerFrame->GetScrolledFrame();
  nsIFrame* cbFrame = aFrame->GetContainingBlock();
  NS_ASSERTION(cbFrame == scrolledFrame ||
                   nsLayoutUtils::IsProperAncestorFrame(scrolledFrame, cbFrame),
               "Scroll frame should be an ancestor of the containing block");

  nsRect rect =
      nsLayoutUtils::GetAllInFlowRectsUnion(aFrame, aFrame->GetParent());

  // FIXME(bug 1421660): Table row groups aren't supposed to be containing
  // blocks, but we treat them as such (maybe it's the right thing to do!).
  // Anyway, not having this basically disables position: sticky on table cells,
  // which would be really unfortunate, and doesn't match what other browsers
  // do.
  if (cbFrame != scrolledFrame && cbFrame->IsTableRowGroupFrame()) {
    cbFrame = cbFrame->GetContainingBlock();
  }

  // Containing block limits for the position of aFrame relative to its parent.
  // The margin box of the sticky element stays within the content box of the
  // containing-block element.
  if (cbFrame == scrolledFrame) {
    // cbFrame is the scrolledFrame, and it won't have continuations. Unlike the
    // else clause, we consider scrollable overflow rect because the union of
    // its in-flow rects doesn't include the scrollable overflow area. We need
    // to subtract the padding however, which _is_ included in the scrollable
    // area, since we want the content box.
    MOZ_ASSERT(cbFrame->GetUsedBorder() == nsMargin(),
               "How did the ::-moz-scrolled-frame end up with border?");
    limits.mContain = cbFrame->ScrollableOverflowRectRelativeToSelf();
    limits.mContain.Deflate(cbFrame->GetUsedPadding());
    nsLayoutUtils::TransformRect(cbFrame, aFrame->GetParent(), limits.mContain);
  } else {
    limits.mContain = nsLayoutUtils::GetAllInFlowRectsUnion(
        cbFrame, aFrame->GetParent(),
        nsLayoutUtils::GetAllInFlowRectsFlag::UseContentBox);
  }

  nsRect marginRect = nsLayoutUtils::GetAllInFlowRectsUnion(
      aFrame, aFrame->GetParent(),
      nsLayoutUtils::GetAllInFlowRectsFlag::UseMarginBoxWithAutoResolvedAsZero);

  // Deflate mContain by the difference between the union of aFrame's
  // continuations' margin boxes and the union of their border boxes, so that
  // by keeping aFrame within mContain, we keep the union of the margin boxes
  // within the containing block's content box.
  limits.mContain.Deflate(marginRect - rect);

  // Deflate mContain by the border-box size, to form a constraint on the
  // upper-left corner of aFrame and continuations.
  limits.mContain.Deflate(nsMargin(0, rect.width, rect.height, 0));

  nsMargin sfPadding = scrolledFrame->GetUsedPadding();
  nsPoint sfOffset = aFrame->GetParent()->GetOffsetTo(scrolledFrame);
  nsSize sfSize = GetScrollContainerSize(mScrollContainerFrame);
  WritingMode writingMode = cbFrame->GetWritingMode();
  nsMargin effectiveOffsets(
      computedOffsets->top == NS_AUTOOFFSET ? 0 : computedOffsets->top,
      computedOffsets->right == NS_AUTOOFFSET ? 0 : computedOffsets->right,
      computedOffsets->bottom == NS_AUTOOFFSET ? 0 : computedOffsets->bottom,
      computedOffsets->left == NS_AUTOOFFSET ? 0 : computedOffsets->left);

  if (computedOffsets->top != NS_AUTOOFFSET ||
      computedOffsets->bottom != NS_AUTOOFFSET) {
    // Decrease the effective end-edge inset of the sticky view rectangle
    // when its height is less than the height of the border-box of the sticky
    // box.
    const int64_t stickyViewHeight =
        int64_t(sfSize.height) - effectiveOffsets.top - effectiveOffsets.bottom;
    if (rect.height > stickyViewHeight) {
      const int64_t delta = int64_t(rect.height) - stickyViewHeight;
      effectiveOffsets.Side(writingMode.PhysicalSide(
          writingMode.IsVertical() ? LogicalSide::IEnd : LogicalSide::BEnd)) -=
          delta;
    }
  }

  if (computedOffsets->left != NS_AUTOOFFSET ||
      computedOffsets->right != NS_AUTOOFFSET) {
    // Decrease the effective end-edge inset of the sticky view rectangle
    // when its width is less than the width of the border-box of the sticky
    // box.
    const int64_t stickyViewWidth =
        int64_t(sfSize.width) - effectiveOffsets.left - effectiveOffsets.right;
    if (rect.width > stickyViewWidth) {
      const int64_t delta = int64_t(rect.width) - stickyViewWidth;
      effectiveOffsets.Side(writingMode.PhysicalSide(
          writingMode.IsVertical() ? LogicalSide::BEnd : LogicalSide::IEnd)) -=
          delta;
    }
  }

  // The limits have so far been computed for the "position" of the union of
  // aFrame and its continuations, but our consumers expect the limits to be
  // on the position of aFrame, so we need to shift the limits by the
  // difference.
  // - For |mContain| we're otherwise done, so we apply the offset directly.
  // - For |mStick| we apply the offset as part of setting |mStick| (applying
  //   it via `MoveBy` after we set |mStick| would trash any sentinel values).
  const nsPoint frameOffset = aFrame->GetPosition() - rect.TopLeft();

  limits.mContain.MoveBy(frameOffset);

  // Top
  if (computedOffsets->top != NS_AUTOOFFSET) {
    limits.mStick.SetTopEdge(scrollPosition.y + sfPadding.top +
                             effectiveOffsets.top - sfOffset.y + frameOffset.y);
  }

  // Bottom
  if (computedOffsets->bottom != NS_AUTOOFFSET) {
    limits.mStick.SetBottomEdge(scrollPosition.y + sfPadding.top +
                                sfSize.height - effectiveOffsets.bottom -
                                rect.height - sfOffset.y + frameOffset.y);
  }

  // Left
  if (computedOffsets->left != NS_AUTOOFFSET) {
    limits.mStick.SetLeftEdge(scrollPosition.x + sfPadding.left +
                              effectiveOffsets.left - sfOffset.x +
                              frameOffset.x);
  }

  // Right
  if (computedOffsets->right != NS_AUTOOFFSET) {
    limits.mStick.SetRightEdge(scrollPosition.x + sfPadding.left +
                               sfSize.width - effectiveOffsets.right -
                               rect.width - sfOffset.x + frameOffset.x);
  }

  return limits;
}
nsPoint StickyScrollContainer::ComputePosition(nsIFrame* aFrame) const {
  return DoComputePosition(aFrame, StickyLimitSpace::RelativeToCurrentScroll);
}
nsPoint StickyScrollContainer::ComputePositionIgnoringScrolling(
    nsIFrame* aFrame) const {
  return DoComputePosition(aFrame, StickyLimitSpace::IgnoreCurrentScroll);
}
nsPoint StickyScrollContainer::DoComputePosition(
    nsIFrame* aFrame, StickyLimitSpace aSpace) const {
  const auto [stick, contain] = ComputeStickyLimits(aFrame, aSpace);

  nsPoint position = aFrame->GetNormalPosition();
  const nsMargin* computedOffsets =
      aFrame->GetProperty(nsIFrame::ComputedOffsetProperty());
  if (!computedOffsets) {
    return position;
  }

  // For each sticky direction (top, bottom, left, right), move the frame along
  // the appropriate axis, based on the scroll position, but limit this to keep
  // the element's margin box within the containing block.
  if (computedOffsets->top != NS_AUTOOFFSET) {
    position.y = std::max(position.y, std::min(stick.Y(), contain.YMost()));
  }
  if (computedOffsets->bottom != NS_AUTOOFFSET) {
    position.y = std::min(position.y, std::max(stick.YMost(), contain.y));
  }
  if (computedOffsets->left != NS_AUTOOFFSET) {
    position.x = std::max(position.x, std::min(stick.X(), contain.XMost()));
  }
  if (computedOffsets->right != NS_AUTOOFFSET) {
    position.x = std::min(position.x, std::max(stick.XMost(), contain.x));
  }

  return position;
}
nsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling(
    const nsIFrame* aFrame) const {
  nsIFrame* first = nsLayoutUtils::FirstContinuationOrIBSplitSibling(aFrame);
  return ComputePositionIgnoringScrolling(first) - first->GetNormalPosition();
}
bool StickyScrollContainer::IsStuckInYDirection(nsIFrame* aFrame) const {
  nsPoint position = ComputePosition(aFrame);
  return position.y != aFrame->GetNormalPosition().y;
}
void StickyScrollContainer::GetScrollRanges(nsIFrame* aFrame,
                                            nsRectAbsolute* aOuter,
                                            nsRectAbsolute* aInner) const {
  // We need to use the first in flow; continuation frames should not move
  // relative to each other and should get identical scroll ranges.
  // Also, ComputeStickyLimits requires this.
  nsIFrame* firstCont =
      nsLayoutUtils::FirstContinuationOrIBSplitSibling(aFrame);

  const auto [stickRect, containRect] = ComputeStickyLimits(firstCont);

  const nsRectAbsolute& stick = stickRect;
  nsRectAbsolute contain = nsRectAbsolute::FromRect(containRect);

  aOuter->SetBox(gUnboundedNegative, gUnboundedNegative, gUnboundedPositive,
                 gUnboundedPositive);
  aInner->SetBox(gUnboundedNegative, gUnboundedNegative, gUnboundedPositive,
                 gUnboundedPositive);

  const nsPoint normalPosition = firstCont->GetNormalPosition();

  // Bottom and top
  if (stick.YMost() != gUnboundedPositive) {
    aOuter->SetTopEdge(contain.Y() - stick.YMost());
    aInner->SetTopEdge(normalPosition.y - stick.YMost());
  }

  if (stick.Y() != gUnboundedNegative) {
    aInner->SetBottomEdge(normalPosition.y - stick.Y());
    aOuter->SetBottomEdge(contain.YMost() - stick.Y());
  }

  // Right and left
  if (stick.XMost() != gUnboundedPositive) {
    aOuter->SetLeftEdge(contain.X() - stick.XMost());
    aInner->SetLeftEdge(normalPosition.x - stick.XMost());
  }

  if (stick.X() != gUnboundedNegative) {
    aInner->SetRightEdge(normalPosition.x - stick.X());
    aOuter->SetRightEdge(contain.XMost() - stick.X());
  }

  // Make sure |inner| does not extend outside of |outer|. (The consumers of
  // the Layers API, to which this information is propagated, expect this
  // invariant to hold.) The calculated value of |inner| can sometimes extend
  // outside of |outer|, for example due to margin collapsing, since
  // GetNormalPosition() returns the actual position after margin collapsing,
  // while |contain| is calculated based on the frame's GetUsedMargin() which
  // is pre-collapsing.
  // Note that this doesn't necessarily solve all problems stemming from
  // comparing pre- and post-collapsing margins (TODO: find a proper solution).
  *aInner = aInner->Intersect(*aOuter);
  if (aInner->IsEmpty()) {
    // This might happen if aInner didn't intersect aOuter at all initially,
    // in which case aInner is empty and outside aOuter. Make sure it doesn't
    // extend outside aOuter.
    *aInner = aInner->MoveInsideAndClamp(*aOuter);
  }
}
StickyScrollContainer::StickyScrollRanges
StickyScrollContainer::GetStickyScrollRangesForAxis(
    const nsIFrame* aFrame, layers::ScrollDirection aAxis) const {
  StickyScrollRanges result;

  nsIFrame* firstCont =
      nsLayoutUtils::FirstContinuationOrIBSplitSibling(aFrame);

  const nsMargin* computedOffsets =
      firstCont->GetProperty(nsIFrame::ComputedOffsetProperty());
  if (!computedOffsets) {
    return result;
  }

  const bool isVertical = aAxis == layers::ScrollDirection::eVertical;
  const nscoord startInset =
      isVertical ? computedOffsets->top : computedOffsets->left;
  const nscoord endInset =
      isVertical ? computedOffsets->bottom : computedOffsets->right;
  if (startInset == NS_AUTOOFFSET && endInset == NS_AUTOOFFSET) {
    return result;
  }

  const auto [stick, contain] =
      ComputeStickyLimits(firstCont, StickyLimitSpace::IgnoreCurrentScroll);

  const nsPoint normalPosition = firstCont->GetNormalPosition();
  const nscoord normal = isVertical ? normalPosition.y : normalPosition.x;

  // Sticking to a side begins/ends at the scroll offset where the
  // (scroll-invariant) stick edge reaches the frame's normal position.
  if (startInset != NS_AUTOOFFSET) {
    const nscoord stickStart = isVertical ? stick.Y() : stick.X();
    MOZ_ASSERT(stickStart != gUnboundedNegative,
               "A non-auto start inset implies a bounded stick edge");
    const nscoord containEnd = isVertical ? contain.YMost() : contain.XMost();
    result.mStartSide.emplace(StickyScrollRange{
        normal - stickStart, std::max(0, containEnd - normal)});
  }

  if (endInset != NS_AUTOOFFSET) {
    const nscoord stickEnd = isVertical ? stick.YMost() : stick.XMost();
    MOZ_ASSERT(stickEnd != gUnboundedPositive,
               "A non-auto end inset implies a bounded stick edge");
    const nscoord containStart = isVertical ? contain.Y() : contain.X();
    result.mEndSide.emplace(StickyScrollRange{
        normal - stickEnd, std::max(0, normal - containStart)});
  }

  if (result.mStartSide && result.mEndSide &&
      result.mEndSide->mScrollPosition > result.mStartSide->mScrollPosition) {
    MOZ_ASSERT_UNREACHABLE(
        "End-side sticking should end before start-side sticking begins");
    result = {};
  }

  return result;
}
void StickyScrollContainer::PositionContinuations(nsIFrame* aFrame) {
  NS_ASSERTION(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(aFrame),
               "Should be starting from the first continuation");
  bool hadProperty;
  const nsPoint normalPosition = aFrame->GetNormalPosition(&hadProperty);
  if (!hadProperty) {
    // We have no normal position to stick from. This happens when the frame
    // hasn't been reflowed yet, e.g. it's in a subtree whose contents are
    // skipped by content-visibility property.
    return;
  }

  // Move all continuation frames by the same amount.
  const nsPoint translation = ComputePosition(aFrame) - normalPosition;
  for (nsIFrame* cont = aFrame; cont;
       cont = nsLayoutUtils::GetNextContinuationOrIBSplitSibling(cont)) {
    cont->SetPosition(cont->GetNormalPosition() + translation);
  }
}
void StickyScrollContainer::UpdatePositions(nsPoint aScrollPosition,
                                            nsIFrame* aSubtreeRoot) {
#ifdef DEBUG
  {
    nsIFrame* scrollFrameAsFrame = do_QueryFrame(mScrollContainerFrame);
    NS_ASSERTION(!aSubtreeRoot || aSubtreeRoot == scrollFrameAsFrame,
                 "If reflowing, should be reflowing the scroll frame");
  }
#endif
  mScrollPosition = aScrollPosition;

  OverflowChangedTracker oct;
  oct.SetSubtreeRoot(aSubtreeRoot);
  // We need to position ancestors before children, so iter from shallowest.
  for (nsIFrame* f : mFrames.IterFromShallowest()) {
    // mFrames only contains primary frames, because we only register in
    // nsIFrame::HandlePrimaryFrameStyleChange().
    MOZ_ASSERT(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(f),
               "Only primary frames should have been registered");
    if (aSubtreeRoot) {
      // Reflowing the scroll frame, so recompute offsets.
      ComputeStickyOffsets(f);
    }
    PositionContinuations(f);

    f = f->GetParent();
    if (f != aSubtreeRoot) {
      for (nsIFrame* cont = f; cont;
           cont = nsLayoutUtils::GetNextContinuationOrIBSplitSibling(cont)) {
        oct.AddFrame(cont, OverflowChangedTracker::CHILDREN_CHANGED);
      }
    }
  }
  oct.Flush();
}
}

namespace mozilla::dom {
inline std::nullopt_t Nothing(){return std::nullopt;}
template<class T> Maybe<T> Some(T x){return Maybe<T>{x};}
struct ViewTimeline {
 struct StickyDisplacement {
    // The scroll offset at which start-side sticking begins. Over the range
    // [mStartSideStuckAt, mStartSideStuckAt + mStartSideMax], the displacement
    // increases from 0 to |mStartSideMax|.
    nscoord mStartSideStuckAt = 0;
    // The maximum positive displacement caused by start-side sticking. Never
    // negative; 0 means there is no start-side sticking.
    nscoord mStartSideMax = 0;
    // The scroll offset at which end-side sticking ends. Over the range
    // [mEndSideUnstuckAt - mEndSideMax, mEndSideUnstuckAt], the displacement
    // increases from -mEndSideMax to 0.
    nscoord mEndSideUnstuckAt = 0;
    // The maximum magnitude of the negative displacement caused by end-side
    // sticking. Never negative; 0 means there is no end-side sticking.
    nscoord mEndSideMax = 0;

    // While stuck, the subject moves with the scrollport, so the alignment
    // that would occur at a single scroll offset if the subject never stuck
    // can instead persist over a range of actual scroll offsets. These
    // functions do not compute d(s) itself; they invert the mapping from an
    // actual scroll offset |s| to its corresponding offset without sticky
    // positioning:
    //
    //   aOffsetIgnoringSticky = s - d(s)
    //
    // returning the smallest (Earliest) resp. largest (Latest) solution for
    // |s|, which lets timeline range calculations pick out the endpoints of
    // the interval over which the alignment is maintained.
    //
    // |aOffsetIgnoringSticky| is the scroll offset at which the subject would
    // reach the alignment defining a timeline range boundary if sticky
    // positioning were not applied.
    nscoord Earliest(nscoord aOffsetIgnoringSticky) const;
    nscoord Latest(nscoord aOffsetIgnoringSticky) const;

    // The same displacement model expressed for negated scroll offsets, as
    // used for RTL / bottom-to-top axes where GetScrollPosition() is zero or
    // negative. The roles of the two sides swap.
    StickyDisplacement Reversed() const {
      return {-mEndSideUnstuckAt, mEndSideMax, -mStartSideStuckAt,
              mStartSideMax};
    }

    bool operator==(const StickyDisplacement&) const = default;
  };
 static Maybe<std::pair<nscoord,StickyDisplacement>> ComputeStickyDisplacement(const nsIFrame*,const ScrollContainerFrame*,layers::ScrollDirection);
};
nscoord ViewTimeline::StickyDisplacement::Earliest(
    nscoord aOffsetIgnoringSticky) const {
  if (mEndSideMax && aOffsetIgnoringSticky <= mEndSideUnstuckAt) {
    return aOffsetIgnoringSticky - mEndSideMax;
  }
  if (mStartSideMax && aOffsetIgnoringSticky > mStartSideStuckAt) {
    return aOffsetIgnoringSticky + mStartSideMax;
  }
  return aOffsetIgnoringSticky;
}
nscoord ViewTimeline::StickyDisplacement::Latest(
    nscoord aOffsetIgnoringSticky) const {
  if (mEndSideMax && aOffsetIgnoringSticky < mEndSideUnstuckAt) {
    return aOffsetIgnoringSticky - mEndSideMax;
  }
  if (mStartSideMax && aOffsetIgnoringSticky >= mStartSideStuckAt) {
    return aOffsetIgnoringSticky + mStartSideMax;
  }
  return aOffsetIgnoringSticky;
}
Maybe<std::pair<nscoord, ViewTimeline::StickyDisplacement>>
ViewTimeline::ComputeStickyDisplacement(
    const nsIFrame* aSubject, const ScrollContainerFrame* aScrollContainerFrame,
    layers::ScrollDirection aAxis) {
  StickyScrollContainer* stickyContainer =
      aScrollContainerFrame->GetStickyContainer();
  if (!stickyContainer) {
    return Nothing();
  }

  const nsIFrame* scrolledFrame = aScrollContainerFrame->GetScrolledFrame();
  const nsIFrame* sticky = nullptr;
  for (const nsIFrame* f = aSubject; f && f != scrolledFrame;
       f = f->GetParent()) {
    if (!f->IsStickyPositioned()) {
      continue;
    }
    const StickyScrollContainer* container =
        StickyScrollContainer::GetForFrame(f);
    if (!container || container->ScrollContainer() != aScrollContainerFrame) {
      continue;
    }
    if (sticky) {
      // Multiple sticky ancestors would each contribute displacement; we
      // don't try to model that. See
      // https://bugzilla.mozilla.org/show_bug.cgi?id=2066973
      return Nothing();
    }
    sticky = f;
  }
  if (!sticky) {
    return Nothing();
  }

  const auto ranges =
      stickyContainer->GetStickyScrollRangesForAxis(sticky, aAxis);
  if (!ranges.mStartSide && !ranges.mEndSide) {
    return Nothing();
  }

  StickyDisplacement displacement;
  if (ranges.mStartSide) {
    displacement.mStartSideStuckAt = ranges.mStartSide->mScrollPosition;
    displacement.mStartSideMax = ranges.mStartSide->mMaxOffset;
  }
  if (ranges.mEndSide) {
    displacement.mEndSideUnstuckAt = ranges.mEndSide->mScrollPosition;
    displacement.mEndSideMax = ranges.mEndSide->mMaxOffset;
  }

  MOZ_ASSERT(displacement.mStartSideMax >= 0);
  MOZ_ASSERT(displacement.mEndSideMax >= 0);
  MOZ_ASSERT(
      !displacement.mStartSideMax || !displacement.mEndSideMax ||
          displacement.mEndSideUnstuckAt <= displacement.mStartSideStuckAt,
      "End-side sticking should end before start-side sticking begins");

  const nsPoint shift = sticky->GetPosition() - sticky->GetNormalPosition();
  return Some(
      std::pair{aAxis == layers::ScrollDirection::eVertical ? shift.y : shift.x,
                displacement});
}
}

void emitPoint(nsPoint p){std::cout<<"["<<p.x<<","<<p.y<<"]";}
void emitRect(nsRect r){std::cout<<"["<<r.x<<","<<r.y<<","<<r.width<<","<<r.height<<"]";}
void emitAbsolute(nsRectAbsolute r){std::cout<<"["<<r.X()<<","<<r.Y()<<","<<r.XMost()<<","<<r.YMost()<<"]";}
void emitMargin(nsMargin r){std::cout<<"["<<r.top<<","<<r.right<<","<<r.bottom<<","<<r.left<<"]";}
void emitRanges(StickyScrollContainer::StickyScrollRanges r){
 std::cout<<"[";
 auto emit=[](Maybe<StickyScrollContainer::StickyScrollRange> x){if(!x){std::cout<<"null";return;}std::cout<<"["<<x->mScrollPosition<<","<<x->mMaxOffset<<"]";};
 emit(r.mStartSide);std::cout<<",";emit(r.mEndSide);std::cout<<"]";
}
void emitStick(nsRect r){std::cout<<"["<<r.X()<<","<<r.Y()<<","<<r.XMost()<<","<<r.YMost()<<"]";}
void emitStick(nsRectAbsolute r){emitAbsolute(r);}
void emitLimits(StickyScrollContainer::StickyLimits r){std::cout<<"[";emitStick(r.mStick);std::cout<<",";emitRect(r.mContain);std::cout<<"]";}
int main(){
 std::string line;
 while(std::getline(std::cin,line)){
  std::istringstream input(line);
  int id,action,cbKind,cbMode,childMode,scrollMode,direction,hasOffsets,hasNormal,viewport,extra;
  if(!(input>>id>>action>>cbKind>>cbMode>>childMode>>scrollMode>>direction>>hasOffsets>>hasNormal>>viewport>>extra))return 21;
  nsIFrame scroll,cb,row,frame,continuation;
  scroll.id=1;cb.id=2;row.id=3;frame.id=4;continuation.id=5;
  scroll.sticky=cb.sticky=row.sticky=false;
  cb.parent=&scroll;row.parent=&cb;row.rowGroup=true;
  frame.parent=cbKind==1?&scroll:cbKind==2?&row:&cb;
  continuation.parent=frame.parent;continuation.first=&frame;
  cb.mWritingMode=WritingMode(cbMode);frame.mWritingMode=WritingMode(childMode);scroll.mWritingMode=WritingMode(scrollMode);
  cb.visibility.mDirection=direction?StyleDirection::Rtl:StyleDirection::Ltr;
  scroll.visibility.mDirection=cb.visibility.mDirection;row.visibility.mDirection=cb.visibility.mDirection;
  ScrollContainerFrame sf;sf.scrolled=&scroll;sf.root=viewport;sf.context.cross=viewport;
  StickyScrollContainer container(&sf);sf.stickyContainer=&container;
  for(auto* f:{&scroll,&cb,&row,&frame,&continuation})f->nearestScroll=&sf;
  auto point=[&](nsPoint& p){input>>p.x>>p.y;};
  auto rect=[&](nsRect& r){input>>r.x>>r.y>>r.width>>r.height;};
  auto margin=[&](nsMargin& m){input>>m.top>>m.right>>m.bottom>>m.left;};
  rect(frame.borderBox);rect(frame.marginBox);rect(cb.contentBox);rect(scroll.overflow);
  margin(scroll.padding);input>>sf.size.width>>sf.size.height>>sf.shell.fixedSize.width>>sf.shell.fixedSize.height;
  point(container.mScrollPosition);point(frame.position);point(frame.normal);point(frame.parent->offsetToScroll);point(scroll.transform);
  margin(frame.offsets);frame.hasComputed=hasOffsets;frame.hasNormal=hasNormal;
  for(int i=0;i<4;i++){int value;input>>value;frame.stylePosition.sides[i]={value==NS_AUTOOFFSET,value};}
  point(continuation.position);point(continuation.normal);rect(continuation.borderBox);rect(continuation.marginBox);
  int excess;if(!input||input>>excess)return 22;
  if(extra)frame.continuation=&continuation;
  container.mFrames.frames={&frame};
  providerTrace.clear();
  const auto originalOffsets=frame.offsets;
  const auto current=container.ComputeStickyLimits(&frame);
  const auto ignoring=container.ComputeStickyLimits(&frame,StickyScrollContainer::StickyLimitSpace::IgnoreCurrentScroll);
  const auto position=container.ComputePosition(&frame);
  const auto zero=container.ComputePositionIgnoringScrolling(&frame);
  const auto translation=container.ComputeTranslationIgnoringScrolling(extra?&continuation:&frame);
  const auto rangeX=container.GetStickyScrollRangesForAxis(extra?&continuation:&frame,layers::ScrollDirection::eHorizontal);
  const auto rangeY=container.GetStickyScrollRangesForAxis(extra?&continuation:&frame,layers::ScrollDirection::eVertical);
  nsRectAbsolute outer,inner;container.GetScrollRanges(extra?&continuation:&frame,&outer,&inner);
  std::cout<<"{\"id\":"<<id<<",\"original_offsets\":";emitMargin(originalOffsets);
  std::cout<<",\"current\":";emitLimits(current);std::cout<<",\"ignoring\":";emitLimits(ignoring);
  std::cout<<",\"position\":";emitPoint(position);std::cout<<",\"zero\":";emitPoint(zero);
  std::cout<<",\"translation\":";emitPoint(translation);
  std::cout<<",\"range_x\":";emitRanges(rangeX);std::cout<<",\"range_y\":";emitRanges(rangeY);
  std::cout<<",\"outer\":";emitAbsolute(outer);std::cout<<",\"inner\":";emitAbsolute(inner);
  std::cout<<",\"trace\":[";
  for(size_t i=0;i<providerTrace.size();i++){if(i)std::cout<<",";std::cout<<providerTrace[i];}
  std::cout<<"]}\n";
 }
}
