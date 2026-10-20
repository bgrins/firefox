#include <cstdint>
#include <optional>
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "mozilla/CheckedInt.h"
using mozilla::CheckedInt;
using nscoord = int32_t;
constexpr nscoord nscoord_MAX = (1<<30)-1;
constexpr nscoord nscoord_MIN = -nscoord_MAX;
constexpr unsigned NS_FRAME_SVG_LAYOUT = 1;
template<typename T> using Maybe=std::optional<T>;
auto Nothing() { return std::nullopt; }
template<typename T> auto Some(T value) { return Maybe<T>(value); }
struct nsRect {
 nscoord x,y,width,height;
 nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}
 nscoord XMost() const { return x+width; }
 nscoord YMost() const { return y+height; }
};
struct Point {nscoord x,y;};
struct nsIFrame {
 const nsIFrame* parent=nullptr;
 int context=1;
 bool transformed=false,svgText=false;
 unsigned states=0;
 Point position{0,0};
 const nsIFrame* GetParent() const { return parent; }
 int PresContext() const { return context; }
 bool IsTransformed() const { return transformed; }
 bool IsInSVGTextSubtree() const { return svgText; }
 bool HasAnyStateBits(unsigned bits) const { return states&bits; }
 Point GetPosition() const { return position; }
};
static int AppUnitsPerCSSPixel() { return 60; }
static double RoundFloat(double value) { return floor(value+0.5); }
struct DOMRect {
 double x,y,width,height;
 void SetX(double v){x=v;} void SetY(double v){y=v;}
 void SetWidth(double v){width=v;} void SetHeight(double v){height=v;}
 void SetLayoutRect(const nsRect&);
};
static void require(bool value, int id) { if(!value) {printf("FAIL %d\n",id);exit(1);} }
static Maybe<nsRect> GetUntransformedRectToAncestor(
    const nsIFrame* aFrame, const nsRect& aRect, const nsIFrame* aAncestor) {
  if (aRect.width < 0 || aRect.height < 0) {
    return Nothing();
  }
  CheckedInt<nscoord> x = aRect.x;
  CheckedInt<nscoord> y = aRect.y;
  for (const nsIFrame* frame = aFrame; frame != aAncestor;
       frame = frame->GetParent()) {
    if (!frame || frame->PresContext() != aAncestor->PresContext() ||
        frame->IsTransformed() || frame->IsInSVGTextSubtree() ||
        frame->HasAnyStateBits(NS_FRAME_SVG_LAYOUT)) {
      return Nothing();
    }
    x += 0;
    y += frame->GetPosition().y;
    if (!x.isValid() || !y.isValid()) {
      return Nothing();
    }
  }
  const auto right = x + aRect.width;
  const auto bottom = y + aRect.height;
  if (!right.isValid() || !bottom.isValid() || x.value() < nscoord_MIN ||
      y.value() < nscoord_MIN || right.value() > nscoord_MAX ||
      bottom.value() > nscoord_MAX) {
    return Nothing();
  }
  return Some(nsRect(x.value(), y.value(), aRect.width, aRect.height));
}
void DOMRect::SetLayoutRect(const nsRect& aLayoutRect) {
  double scale = 65536.0;
  // Round to the nearest 1/scale units. We choose scale so it can be
  // represented exactly by machine floating point.
  double scaleInv = 1 / scale;
  double t2pScaled = scale / AppUnitsPerCSSPixel();
  double x = RoundFloat(aLayoutRect.x * t2pScaled) * scaleInv;
  double y = RoundFloat(aLayoutRect.y * t2pScaled) * scaleInv;
  SetX(x);
  SetY(y);
  SetWidth(RoundFloat(aLayoutRect.XMost() * t2pScaled) * scaleInv - x);
  SetHeight(RoundFloat(aLayoutRect.YMost() * t2pScaled) * scaleInv - y);
}
int main(){
 nsIFrame root,mid,leaf;
 mid.parent=&root; mid.position={700,1100};
 leaf.parent=&mid; leaf.position={-8383188,-1100};
 nsRect box(0,0,8388488,600);
 auto result=GetUntransformedRectToAncestor(&leaf,box,&root);
 require(result && result->x==-8382488 && result->y==0 && result->XMost()==6000,1);
 DOMRect observed;
 observed.SetLayoutRect(*result);
 require(observed.x+observed.width==100,2);
 leaf.transformed=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),3);leaf.transformed=false;
 mid.transformed=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),4);mid.transformed=false;
 leaf.svgText=true;require(!GetUntransformedRectToAncestor(&leaf,box,&root),5);leaf.svgText=false;
 mid.states=NS_FRAME_SVG_LAYOUT;require(!GetUntransformedRectToAncestor(&leaf,box,&root),6);mid.states=0;
 mid.context=2;require(!GetUntransformedRectToAncestor(&leaf,box,&root),7);mid.context=1;
 mid.parent=nullptr;require(!GetUntransformedRectToAncestor(&leaf,box,&root),8);mid.parent=&root;
 leaf.position={INT32_MAX,0};require(!GetUntransformedRectToAncestor(&leaf,box,&root),9);
 leaf.parent=&root;leaf.position={INT32_MAX-10,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,20,1),&root),10);
 leaf.position={nscoord_MAX,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,1,1),&root),11);
 leaf.position={nscoord_MIN-1,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,1,1),&root),12);
 leaf.position={0,0};require(!GetUntransformedRectToAncestor(&leaf,nsRect(0,0,-1,1),&root),13);
 result=GetUntransformedRectToAncestor(&leaf,nsRect(0,0,0,0),&root);require(result && result->x==0,14);
 observed.SetLayoutRect(nsRect(-8382482,0,8388488,1));
 require(fabs(observed.x+observed.width-100.1)<0.00001,15);
 printf("PASS 15 checks\n");
}
