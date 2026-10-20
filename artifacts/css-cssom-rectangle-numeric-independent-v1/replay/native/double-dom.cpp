
#include <algorithm>
#include <cassert>
#include <cfenv>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#define MOZ_ASSERT assert
#define MOZ_UNLIKELY(x) (x)
using nscoord=int32_t;
constexpr nscoord nscoord_MAX=1073741823, nscoord_MIN=-1073741823;
struct nsRect {
 nscoord x=0,y=0,width=0,height=0;
 nscoord XMost() const { return x+width; }
 nscoord YMost() const { return y+height; }
 void SetWidth(nscoord v) { width=v; }
 void SetHeight(nscoord v) { height=v; }
};
struct Rect {
 using T=float;
 float x,y,width,height;
 float Width() const { return width; }
 float Height() const { return height; }
 void Scale(float v) { Scale(v,v); }
void Scale(T aXScale, T aYScale) {
    x = x * aXScale;
    y = y * aYScale;
    width = width * aXScale;
    height = height * aYScale;
  }
};

struct nsLayoutUtils {
 static void ConstrainToCoordValues(double&,double&);
 template<typename T> static nsRect ScaleThenRoundGfxRectToAppRect(const T&,float);
};
int AppUnitsPerCSSPixel() { return 60; }
struct DOMRect {
 double mX=0,mY=0,mWidth=0,mHeight=0;
 double X() const { return mX; }
 double Width() const { return mWidth; }
 static double NaNSafeMax(double a,double b) { return std::max(a,b); }
 void SetLayoutRect(const nsRect&);
void SetRect(double aX, double aY, double aWidth, double aHeight) {
    mX = aX;
    mY = aY;
    mWidth = aWidth;
    mHeight = aHeight;
  }
double Right() const {
    double x = X(), w = Width();
    return NaNSafeMax(x, x + w);
  }
};
inline float NSAppUnitsToFloatPixels(nscoord aAppUnits,
                                     float aAppUnitsPerPixel) {
  return float(aAppUnits) / aAppUnitsPerPixel;
}
inline nscoord NSToCoordRound(double aValue) {
  return nscoord(floor(aValue + 0.5f));
}
inline nscoord NSToCoordRoundWithClamp(double aValue) {
  // Bounds-check before converting out of double, to avoid overflow
  if (aValue >= double(nscoord_MAX)) {
    return nscoord_MAX;
  }
  if (aValue <= double(nscoord_MIN)) {
    return nscoord_MIN;
  }
  return NSToCoordRound(aValue);
}
static void ConstrainToCoordValues(double& aVal) {
  if (aVal <= nscoord_MIN) {
    aVal = nscoord_MIN;
  } else if (aVal >= nscoord_MAX) {
    aVal = nscoord_MAX;
  }
}
/* static */ void nsLayoutUtils::ConstrainToCoordValues(double& aStart,
                                                        double& aSize) {
  MOZ_ASSERT(std::isnan(aSize) || aSize >= 0);

  double max = aStart + aSize;

  // Clamp the end points to within nscoord range
  ::ConstrainToCoordValues(aStart);
  ::ConstrainToCoordValues(max);

  // Here we try to make sure that the resulting nsRect will continue to cover
  // as much of the area that was covered by the original gfx Rect as possible.

  // We must also clamp aSize to {0,nscoord_MAX} since nsRect::Width/Height()
  // can't return a value greater than nscoord_MAX. If aSize is greater than
  // nscoord_MAX then we reduce it to nscoord_MAX while keeping the rect
  // centered:

  aSize = max - aStart;
  // If the width if still greater than the max nscoord, then bring both
  // endpoints in by the same amount until it fits.
  if (MOZ_UNLIKELY(std::isnan(aSize))) {
    // Can happen if aStart is -inf and aSize is +inf for example.
    // If either aStart or aSize is NaN on entry to this function then the
    // calculations above this will make the other one NaN too, so this check
    // ensures that we do not return NaN for either value.
    aStart = 0.0f;
    aSize = nscoord_MAX;
  } else if (aSize > nscoord_MAX) {
    double excess = aSize - nscoord_MAX;
    excess /= 2;

    aStart += excess;
    aSize = nscoord_MAX;
  } else if (aSize < nscoord_MIN) {
    double excess = aSize - nscoord_MIN;
    excess /= 2;

    aStart -= excess;
    aSize = nscoord_MIN;
  }
}
template <typename T>
nsRect nsLayoutUtils::ScaleThenRoundGfxRectToAppRect(const T& aRect,
                                                     const float aFactor) {
  // Get a new Rect whose units are app units by scaling by the specified
  // factor.
  T scaledRect = aRect;
  scaledRect.Scale(aFactor);

  nsRect retval;

  double start = double(scaledRect.x);
  double size = double(scaledRect.width);
  // We now need to constrain our results to the max and min values for coords.
  ConstrainToCoordValues(start, size);
  // ConstrainToCoordValues ensures converting to nscoord is safe.
  retval.x = NSToCoordRoundWithClamp(start);
  retval.width = NSToCoordRoundWithClamp(size);

  start = double(scaledRect.y);
  size = double(scaledRect.height);
  ConstrainToCoordValues(start, size);
  retval.y = NSToCoordRoundWithClamp(start);
  retval.height = NSToCoordRoundWithClamp(size);

  if (!aRect.Width()) {
    retval.SetWidth(0);
  }

  if (!aRect.Height()) {
    retval.SetHeight(0);
  }

  return retval;
}
static double RoundFloat(double aValue) { return floor(aValue + 0.5); }
void DOMRect::SetLayoutRect(const nsRect& aLayoutRect) {
  double scale = 65536.0;
  // Round to the nearest 1/scale units. We choose scale so it can be
  // represented exactly by machine floating point.
  double scaleInv = 1 / scale;
  double t2pScaled = scale / AppUnitsPerCSSPixel();
  double x = RoundFloat(aLayoutRect.x * t2pScaled) * scaleInv;
  double y = RoundFloat(aLayoutRect.y * t2pScaled) * scaleInv;
  SetRect(x, y, RoundFloat(aLayoutRect.XMost() * t2pScaled) * scaleInv - x,
          RoundFloat(aLayoutRect.YMost() * t2pScaled) * scaleInv - y);
}
int main() {
 static_assert(sizeof(float)==4 && sizeof(double)==8);
 static_assert(std::numeric_limits<float>::is_iec559 && std::numeric_limits<float>::digits==24);
 static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53);
 assert(std::fegetround()==FE_TONEAREST);
 int32_t x,w,f,r;
 std::cout<<std::setprecision(17);
 while(std::cin>>x>>w>>f>>r) {
   Rect input{NSAppUnitsToFloatPixels(x,float(f)),0,
              NSAppUnitsToFloatPixels(w,float(f)),0};
   nsRect a=r ? nsLayoutUtils::ScaleThenRoundGfxRectToAppRect(input,float(f))
              : nsRect{x,0,w,0};
   DOMRect dom;dom.SetLayoutRect(a);
   double b=RoundFloat(a.x*(65536.0/60))* (1.0/65536);
   double e=RoundFloat(a.XMost()*(65536.0/60))* (1.0/65536);
   std::cout<<a.x<<' '<<a.width<<' '<<input.x<<' '<<input.width<<' '
     <<b<<' '<<e<<' '<<dom.mX<<' '<<dom.mWidth<<' '<<dom.Right()<<'\n';
 }
}
