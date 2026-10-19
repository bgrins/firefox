#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <iomanip>
#include <memory>
#include <string>
#include <vector>
#define MOZ_ASSERT assert
#define MOZ_UNLIKELY(x) (x)

enum class CompositionOp { OP_OVER, OP_OUT, OP_IN, OP_XOR };
enum class StyleMaskMode { MatchSource, Alpha, Luminance };
enum class StyleMaskType { Alpha, Luminance };
enum class StyleColorInterpolation { Srgb, Linearrgb };
enum class SurfaceFormat { A8, B8G8R8A8 };
enum class LuminanceType { LUMINANCE, LINEARRGB };
enum class StyleMaskComposite { Add, Subtract, Intersect, Exclude };
namespace mozilla {using StyleMaskComposite=::StyleMaskComposite;}
enum class ImgDrawResult { SUCCESS = 7 };
ImgDrawResult& operator&=(ImgDrawResult& x, ImgDrawResult y) { x = y; return x; }
struct Rect { double x=0, y=0, w=40, h=40; bool IsEmpty() const { return w<=0 || h<=0; } void RoundOut() {} };
using gfxRect = Rect;
struct Point { double x=0, y=0; Point()=default; Point(double a,double b):x(a),y(b){} Point operator-() const {return {-x,-y};} };
struct Matrix { double x=0,y=0; Matrix()=default; Matrix(double a,double b):x(a),y(b){} Rect TransformBounds(Rect r) const {return r;} static Matrix Translation(Point p){return {p.x,p.y};} };
Matrix operator*(Matrix a, Matrix b){return {a.x+b.x,a.y+b.y};}
using gfxMatrix = Matrix;
using gfxPoint = Point;
struct nsPoint { double x=0,y=0; };
Rect ToRect(Rect r){return r;}
Point ToPoint(Point p){return p;}
struct SourceSurface { double alpha; };
template<class T> using already_AddRefed = T*;
template<class T> struct RefPtr { T* p=nullptr; RefPtr()=default; RefPtr(T* a):p(a){} T* operator->()const{return p;} operator T*() const{return p;} T* forget(){auto v=p;p=nullptr;return v;} };
struct Env { bool ref=true, empty=false, alloc=true, valid=true, snapshot=true; bool linear=false; StyleMaskType type=StyleMaskType::Alpha; double alpha=.5; int children=1; };
Env* active;
std::vector<std::string> trace;
struct DeviceColor { double alpha; DeviceColor(double,double,double,double a):alpha(a){} static DeviceColor MaskWhite(double a){return {0,0,0,a};} };
struct ColorPattern { DeviceColor value; ColorPattern(DeviceColor v):value(v){} };
struct DrawOptions { double opacity; CompositionOp op; DrawOptions(double a,CompositionOp o):opacity(a),op(o){} };
double composite(CompositionOp op,double s,double d){switch(op){case CompositionOp::OP_OVER:return s+d*(1-s);case CompositionOp::OP_OUT:return s*(1-d);case CompositionOp::OP_IN:return s*d;case CompositionOp::OP_XOR:return s*(1-d)+d*(1-s);}return -1;}
struct DrawTarget {
  Matrix transform{17,23}; Rect rect{9,13,40,40}; double alpha=0; bool valid=true; bool temporary=false;
  SurfaceFormat format=SurfaceFormat::A8;
  Matrix GetTransform()const{return transform;}
  void SetTransform(Matrix m){transform=m;trace.push_back("transform:"+std::to_string(int(m.x))+","+std::to_string(int(m.y)));}
  SurfaceFormat GetFormat()const{return format;}
  Rect GetRect()const{return rect;}
  struct Size { double w,h; }; Size GetSize()const{return {rect.w,rect.h};}
  bool IsValid()const{return valid;}
  DrawTarget* CreateClippedDrawTarget(Rect,SurfaceFormat f){trace.push_back("allocate");if(!active->alloc)return nullptr;auto d=new DrawTarget;d->temporary=true;d->valid=active->valid;d->format=f;return d;}
  SourceSurface* Snapshot(){trace.push_back("snapshot");return active->snapshot?new SourceSurface{alpha}:nullptr;}
  SourceSurface* IntoLuminanceSource(LuminanceType,double opacity){trace.push_back("luminance");return active->snapshot?new SourceSurface{alpha*opacity}:nullptr;}
  void FillRect(Rect,ColorPattern p,DrawOptions o){alpha=composite(o.op,p.value.alpha,alpha);}
  void MaskSurface(ColorPattern p,SourceSurface* s,Point,DrawOptions o){trace.push_back("mask:"+std::to_string(int(o.op)));alpha=composite(o.op,s->alpha*p.value.alpha*o.opacity,alpha);}
  void ClearRect(Rect r){trace.push_back("clear:"+std::to_string(int(r.x))+","+std::to_string(int(r.y))+","+std::to_string(int(r.w))+","+std::to_string(int(r.h)));alpha=0;}
};
namespace gfx {using DrawTarget=::DrawTarget;}
struct gfxContext { DrawTarget* target; gfxContext(DrawTarget* t,bool):target(t){} DrawTarget* GetDrawTarget(){return target;} void Multiply(Matrix m){target->transform=target->transform*m;} };
struct gfxContextMatrixAutoSaveRestore { gfxContext* ctx;Matrix saved;gfxContextMatrixAutoSaveRestore(gfxContext* c):ctx(c),saved(c->target->transform){} ~gfxContextMatrixAutoSaveRestore(){ctx->target->transform=saved;} };
struct imgDrawingParams {ImgDrawResult result=ImgDrawResult::SUCCESS;};
struct Image {bool resolved=false;bool IsResolved()const{return resolved;}};
struct Layer {StyleMaskComposite mComposite=StyleMaskComposite::Add;StyleMaskMode mMaskMode=StyleMaskMode::Alpha;Image mImage;};
struct nsStyleSVGReset {struct {std::vector<Layer> mLayers;}mMask;StyleMaskType mMaskType=StyleMaskType::Alpha;};
struct StyleSVGData {StyleColorInterpolation mColorInterpolation=StyleColorInterpolation::Srgb;};
struct ComputedStyle {nsStyleSVGReset reset;const nsStyleSVGReset* StyleSVGReset()const{return &reset;}};
struct nsPresContext {int AppUnitsPerDevPixel(){return 60;}};
struct nsIFrame {nsPresContext pc;nsPresContext* PresContext(){return &pc;}int border=1;int* StyleBorder(){return &border;}};
struct Builder {int GetBackgroundPaintFlags(){return 0;}};
struct PaintFramesParams {nsIFrame* frame;imgDrawingParams& imgParams;Rect dirtyRect,borderArea;Builder* builder;};
template<class T> struct nsTArray:std::vector<T>{using std::vector<T>::vector; bool IsEmpty()const{return this->empty();}size_t Length()const{return this->size();}};
struct Kid {};
struct ISVGDisplayableFrame {enum class ChangeFlag{TransformChanged};void NotifySVGChanged(ChangeFlag){}};
ISVGDisplayableFrame* do_QueryFrame(Kid*){return nullptr;}
namespace nsLayoutUtils {Point PointToGfxPoint(nsPoint p,int){return {p.x,p.y};}}
namespace SVGUtils {
Matrix GetCSSPxToDevPxMatrix(nsIFrame*){return {3,7};}
Matrix GetTransformMatrixInUserSpace(Kid*){return {};}
void PaintFrameWithEffects(Kid*,gfxContext& ctx,Matrix,imgDrawingParams&){trace.push_back("child");ctx.target->alpha=active->alpha;}
}
struct SVGMaskFrame {
  Env env;bool mInUse=false;Matrix mMatrixForChildren;std::vector<Kid*>mFrames;nsStyleSVGReset reset;StyleSVGData svg;
@@PARAMS@@
@@DECLARATION@@
  gfxRect GetMaskArea(nsIFrame*){trace.push_back("area");return {0,0,env.empty?0.:40.,40};}
  Matrix GetMaskTransform(nsIFrame*){return {};}
  const nsStyleSVGReset* StyleSVGReset(){reset.mMaskType=env.type;return &reset;}
  const StyleSVGData* StyleSVG(){svg.mColorInterpolation=env.linear?StyleColorInterpolation::Linearrgb:StyleColorInterpolation::Srgb;return &svg;}
};
struct AutoReferenceChainGuard {static const int16_t noChain=0;Env* env;AutoReferenceChainGuard(SVGMaskFrame* f,bool*,int16_t*):env(&f->env){active=env;}bool Reference(){trace.push_back("reference");return env->ref;}};
struct nsCSSRendering {
@@OPERATOR@@
  static const int PAINTBG_MASK_IMAGE=1;
  struct PaintBGParams {template<class... T>static PaintBGParams ForSingleLayer(T...){return {};}};
  static ImgDrawResult PaintStyleImageLayerWithSC(PaintBGParams,gfxContext&,const ComputedStyle*,int){trace.push_back("image-provider");return ImgDrawResult::SUCCESS;}
};

