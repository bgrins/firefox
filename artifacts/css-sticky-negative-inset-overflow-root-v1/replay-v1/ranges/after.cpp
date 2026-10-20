#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <string>
#include <type_traits>
#define MOZ_ALWAYS_INLINE inline
using nscoord = int32_t;
static constexpr nscoord nscoord_MAX = 1073741823;
static constexpr nscoord nscoord_MIN = -1073741823;
static constexpr nscoord gUnboundedNegative = nscoord_MIN / 2;
static constexpr nscoord gUnboundedExtent = nscoord_MAX;
static constexpr nscoord gUnboundedPositive = gUnboundedNegative + gUnboundedExtent;
struct nsPoint { nscoord x=0,y=0; };
struct nsRect {
 nscoord x,y,width,height;
 nscoord X() const {return x;} nscoord Y() const {return y;}
 nscoord XMost() const {return x+width;} nscoord YMost() const {return y+height;}
 bool Overflows() const {auto a=int64_t(x)+width,b=int64_t(y)+height;return a<INT32_MIN||a>INT32_MAX||b<INT32_MIN||b>INT32_MAX;}
 void SetLeftEdge(nscoord a) {width=XMost()-a;x=a;}
 void SetRightEdge(nscoord a) {width=a-x;}
 void SetTopEdge(nscoord a) {height=YMost()-a;y=a;}
 void SetBottomEdge(nscoord a) {height=a-y;}
};
template <class T, class Sub, class Point, class Rect>
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
struct nsRectAbsolute : BaseRectAbsolute<nscoord,nsRectAbsolute,nsPoint,nsRect> {
 using BaseRectAbsolute::BaseRectAbsolute;
};
struct nsIFrame {nsPoint normal;nsPoint GetNormalPosition() const{return normal;}};
namespace nsLayoutUtils {nsIFrame* FirstContinuationOrIBSplitSibling(nsIFrame* f){return f;}}
struct StickyScrollContainer {
 struct Limits {nsRectAbsolute mStick;nsRect mContain;};
 Limits limits;
 Limits ComputeStickyLimits(nsIFrame*) const {return limits;}
 void GetScrollRanges(nsIFrame*,nsRectAbsolute*,nsRectAbsolute*) const;
};
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
int main(int argc,char** argv) {
 const bool clamp=argc>1 && std::string(argv[1])=="clamp";
 StickyScrollContainer s;
 nsRect initial{gUnboundedNegative,gUnboundedNegative,gUnboundedExtent,gUnboundedExtent};
s.limits.mStick=nsRectAbsolute::FromRect(initial);

 s.limits.mContain={0,0,6000,59400};
 s.limits.mStick.SetTopEdge(-1073741823);
 s.limits.mStick.SetBottomEdge(clamp ? 1073740223 : 1073747223);
 if(clamp){s.limits.mStick.SetLeftEdge(0);s.limits.mStick.SetRightEdge(0);}
 nsIFrame frame{{0,12000}};
 nsRectAbsolute outer,inner;s.GetScrollRanges(&frame,&outer,&inner);
 std::cout<<outer<<" "<<inner<<"\n";
}
