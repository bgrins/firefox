#include <initializer_list>
#include <cmath>
#include <cstdio>
#include <cassert>
#include <cstdint>
using std::floor;
struct nsRect {
  int32_t x,y,width,height;
  int32_t XMost() const { return x+width; }
  int32_t YMost() const { return y+height; }
};
static int AppUnitsPerCSSPixel() { return 60; }
static double RoundFloat(double aValue) { return floor(aValue + 0.5); }
struct DOMRect {
 double mX,mY,mWidth,mHeight;
 void SetLayoutRect(const nsRect&);
void SetRect(float aX, float aY, float aWidth, float aHeight) {
    mX = aX;
    mY = aY;
    mWidth = aWidth;
    mHeight = aHeight;
  }
};
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
 for (int32_t width : {7208,8168,8388488,8389448}) {
  for (bool roundtrip : {false,true}) {
   int32_t x = 6000-width;
   int32_t observedX = x, observedWidth = width;
   if (roundtrip) {
    float px = float(x)/60.0f, pw = float(width)/60.0f;
    observedX = int32_t(floor(double(px*60.0f)+0.5));
    observedWidth = int32_t(floor(double(pw*60.0f)+0.5));
   }
   DOMRect rect;
   rect.SetLayoutRect({observedX,0,observedWidth,600});
   double end = rect.mX+rect.mWidth;
   printf("{\"widthAU\":%d,\"xAU\":%d,\"floatRoundTrip\":%s,\"observedXAU\":%d,\"observedWidthAU\":%d,\"x\":%.17g,\"width\":%.17g,\"right\":%.17g}\n",width,x,roundtrip?"true":"false",observedX,observedWidth,rect.mX,rect.mWidth,end);
   if (width==8388488 && roundtrip) {
    assert(observedX==-8382488 && observedWidth==8388489);
    assert(end==100.015625);
   }
   if (!roundtrip || width==8389448) { assert(end==100); }
  }
 }
}
