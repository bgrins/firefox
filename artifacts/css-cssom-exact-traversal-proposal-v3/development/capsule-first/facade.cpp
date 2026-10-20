#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <optional>
#include <string>
#include <vector>
#include "mozilla/CheckedInt.h"
using mozilla::CheckedInt;
using mozilla::SafeAdd;
using nscoord = int32_t;
constexpr nscoord nscoord_MAX=(1<<30)-1, nscoord_MIN=-nscoord_MAX;
constexpr unsigned NS_FRAME_SVG_LAYOUT=1, NS_FRAME_IS_SVG_TEXT=2;
#define MOZ_ASSERT(...) ((void)0)
#define NS_ASSERTION(...) ((void)0)
template<class T> using Maybe=std::optional<T>;
template<class T> auto Some(T value){return Maybe<T>(value);}
auto Nothing(){return std::nullopt;}
struct nsPoint {
 nscoord x=0,y=0;
 nsPoint()=default; nsPoint(nscoord a,nscoord b):x(a),y(b){}
 nsPoint& operator+=(nsPoint b){x+=b.x;y+=b.y;return *this;}
 bool operator==(const nsPoint&) const=default;
 nsPoint ScaleToOtherAppUnits(int32_t a,int32_t b)const {
  if(a!=b)return nsPoint(int32_t(std::floor(double(x)*b/a+0.5)),int32_t(std::floor(double(y)*b/a+0.5)));
  return *this;
 }
};
struct nsRect {nscoord x,y,width,height;nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}};
enum class ViewportType {Layout,Visual};
enum class TransformMatrixFlag {IgnoreScrolling=1,InCSSUnits=2,StopAtStackingContextAndDisplayPort=4};
struct TransformMatrixFlags {
 unsigned value=0;
 bool contains(TransformMatrixFlag f)const{return value&unsigned(f);}
 bool isEmpty()const{return value==0;}
};
static int matrixCalls=0,fallbackCalls=0,cachedFallbackCalls=0;
static int injectedState=0;
struct Matrix4x4Flagged {
 float sx=1,sy=1,tx=0,ty=0;
 std::string trace="I";
 static Matrix4x4Flagged Translation2d(float x,float y){Matrix4x4Flagged m;m.tx=x;m.ty=y;m.trace="T";return m;}
 void PostTranslate(float x,float y,int){tx+=x;ty+=y;trace+="t";}
 void ProjectTo2D(){trace+="p";}
 Matrix4x4Flagged operator*(const Matrix4x4Flagged& b)const {
  Matrix4x4Flagged r;r.sx=sx*b.sx;r.sy=sy*b.sy;r.tx=tx*b.sx+b.tx;r.ty=ty*b.sy+b.ty;r.trace="("+trace+"*"+b.trace+")";return r;
 }
 Matrix4x4Flagged Inverse()const {Matrix4x4Flagged r;r.sx=1/sx;r.sy=1/sy;r.tx=-tx/sx;r.ty=-ty/sy;r.trace="inv";return r;}
 Matrix4x4Flagged ToUnknownMatrix()const{return *this;}
};
struct Context {int apd=60;int AppUnitsPerDevPixel()const{return apd;}};
struct nsIFrame;
struct RelativeTo {
 const nsIFrame* mFrame=nullptr;ViewportType mViewportType=ViewportType::Layout;
 RelativeTo(const nsIFrame* f,ViewportType t=ViewportType::Layout):mFrame(f),mViewportType(t){}
 bool operator==(const RelativeTo&)const=default;
};
struct AppUnitTranslation {int64_t x,y;};
struct nsIFrame {
 nsIFrame* parent=nullptr;nsIFrame* crossParent=nullptr;Context* context=nullptr;
 nsPoint position,ignoredPosition,crossOffset;
 bool transformed=false,svgText=false,zoomed=false,combines=false,stacking=false,displayPort=false;
 unsigned states=0;Matrix4x4Flagged transform;
 nsIFrame* GetParent()const{return parent;}
 Context* PresContext()const{return context;}
 nsPoint GetPosition()const{return position;}
 nsPoint GetPositionIgnoringScrollingAndSticky()const{return ignoredPosition;}
 bool IsTransformed()const{return transformed;}
 bool IsInSVGTextSubtree()const{return svgText;}
 bool HasAnyStateBits(unsigned s)const{return (states|(svgText?NS_FRAME_IS_SVG_TEXT:0))&s;}
 bool Combines3DTransformWithAncestors()const{return combines;}
 bool IsStackingContext()const{return stacking;}
 const nsIFrame* GetContent()const{return this;}
 Matrix4x4Flagged GetTransformMatrix(ViewportType,RelativeTo,nsIFrame**,TransformMatrixFlags={}
#if CANDIDATE
 ,Maybe<AppUnitTranslation>* =nullptr
#endif
 )const;
};
struct LayoutDevicePixel{};
struct ViewportUtils {
 static const nsIFrame* IsZoomedContentRoot(const nsIFrame* f){return f->zoomed?f:nullptr;}
 template<class T=void>static Matrix4x4Flagged GetVisualToLayoutTransform(const nsIFrame*){Matrix4x4Flagged m;m.sx=0.5;m.sy=0.5;m.trace="zoom";return m;}
};
struct nsDisplayTransform {
 static constexpr int INCLUDE_PERSPECTIVE=1;
 static Matrix4x4Flagged GetResultingTransformMatrix(const nsIFrame* f,nsPoint,int,int){return f->transform;}
};
struct DisplayPortUtils {static bool FrameHasDisplayPort(const nsIFrame* f,const nsIFrame* =nullptr){return f->displayPort;}};
static int AppUnitsPerCSSPixel(){return 60;}
static float NSAppUnitsToFloatPixels(nscoord a,int b){return float(a)/b;}
struct nsLayoutUtils {
 static nsIFrame* GetCrossDocParentFrameInProcess(const nsIFrame* f,nsPoint* offset){*offset=f->parent?nsPoint():f->crossOffset;return f->parent?f->parent:f->crossParent;}
 static Matrix4x4Flagged GetTransformToAncestor(RelativeTo,RelativeTo,TransformMatrixFlags={},nsIFrame** =nullptr
#if CANDIDATE
 ,Maybe<AppUnitTranslation>* =nullptr
#endif
 );
 static nsRect TransformFrameRectToAncestor(const nsIFrame*,const nsRect&,const nsIFrame*,bool* =nullptr,Maybe<Matrix4x4Flagged>* =nullptr);
};
static void require(bool b,int id){if(!b){printf("FAIL %d\n",id);exit(1);}}
