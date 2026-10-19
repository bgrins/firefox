#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#define MOZ_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define MOZ_ASSERT_IF(x,y) assert(!(x) || (y))
#define MOZ_LIKELY(x) (x)

enum class CompositionOp { OP_OVER, OP_OUT, OP_IN, OP_XOR };
enum class StyleMaskComposite { Add, Subtract, Intersect, Exclude };
enum class StyleMaskMode { MatchSource, Alpha, Luminance };
enum class StyleImageLayerAttachment { Scroll, Fixed };
enum class StyleImageLayerRepeat { NoRepeat, Repeat, Round, Space };
enum class StyleBackgroundClip { BorderBox, ContentBox, PaddingBox, Text };
enum class StyleAppearance { None, Widget };
enum class LayoutFrameType { PageContent };
enum class ExtendMode { CLAMP, REPEAT_X, REPEAT_Y, REPEAT };
namespace mozilla {using StyleMaskMode=::StyleMaskMode;namespace gfx {using ExtendMode=::ExtendMode;}}
@@RESULT@@
using nscoord = int;
using nscolor = uint32_t;
struct nsSize { int width=0, height=0; };
struct nsPoint {
  int x=0,y=0;
  nsPoint operator+(nsPoint p)const{return {x+p.x,y+p.y};}
  nsPoint& operator+=(nsPoint p){x+=p.x;y+=p.y;return *this;}
};
struct nsRect {
  int x=0,y=0,width=0,height=0;
  nsRect()=default;
  nsRect(int a,int b,int w,int h):x(a),y(b),width(w),height(h){}
  nsRect(nsPoint p,nsSize s):x(p.x),y(p.y),width(s.width),height(s.height){}
  bool IsEmpty()const{return width<=0 || height<=0;}
  nsPoint TopLeft()const{return {x,y};}
  nsSize Size()const{return {width,height};}
  nsRect operator+(nsPoint p)const{return {x+p.x,y+p.y,width,height};}
  bool IsEqualEdges(nsRect r)const{return x==r.x&&y==r.y&&width==r.width&&height==r.height;}
  void IntersectRect(nsRect a,nsRect b){
    x=std::max(a.x,b.x);y=std::max(a.y,b.y);
    width=std::max(0,std::min(a.x+a.width,b.x+b.width)-x);
    height=std::max(0,std::min(a.y+a.height,b.y+b.height)-y);
    if(width==0 || height==0){width=0;height=0;}
  }
};
using Rect=nsRect;
using gfxRect=nsRect;
struct Matrix {
  std::array<double,6> data{1,0,0,1,0,0};
  bool operator==(const Matrix& m)const{return data==m.data;}
};
std::vector<std::string> trace;
void record(const std::string& s){trace.push_back(s);}
std::string rectText(nsRect r){return std::to_string(r.x)+","+std::to_string(r.y)+","+std::to_string(r.width)+","+std::to_string(r.height);}
std::string matrixText(const Matrix& m){std::ostringstream s;s<<std::setprecision(17);for(size_t i=0;i<6;++i){if(i)s<<",";s<<m.data[i];}return s.str();}
double composite(CompositionOp op,double s,double d){
  switch(op){case CompositionOp::OP_OVER:return s+d*(1-s);
    case CompositionOp::OP_OUT:return s*(1-d);
    case CompositionOp::OP_IN:return s*d;
    case CompositionOp::OP_XOR:return s*(1-d)+d*(1-s);}
  assert(false);return 0;
}
struct DrawTarget {
  Matrix transform; nsRect rect; double alpha=0;
  Matrix GetTransform()const{return transform;}
  void SetTransform(Matrix value){transform=value;record(std::string(value==Matrix()?"identity:":"restore-transform:")+matrixText(value));}
  nsRect GetRect()const{record("get-rect");return rect;}
  void ClearRect(nsRect value){record("clear:"+rectText(value));assert(transform==Matrix());assert(value.IsEqualEdges(rect));alpha=0;}
};
struct sRGBColor { static sRGBColor FromABGR(nscolor){return {};} };
struct gfxContext {
  DrawTarget* target; CompositionOp op=CompositionOp::OP_OVER;
  explicit gfxContext(DrawTarget* t):target(t){}
  DrawTarget* GetDrawTarget(){return target;}
  CompositionOp CurrentOp()const{return op;}
  void SetOp(CompositionOp value){op=value;record("op:"+std::to_string(int(value)));}
  void SetColor(sRGBColor){record("color");}
  void SnappedClip(gfxRect){record("slice-clip");}
};
struct gfxContextAutoSaveRestore {
  gfxContext* ctx=nullptr; Matrix saved;
  void EnsureSaved(gfxContext* c){if(!ctx){ctx=c;saved=c->target->transform;record("save-clip");}}
  ~gfxContextAutoSaveRestore(){if(ctx){ctx->target->transform=saved;record("restore-clip");}}
};
struct Env {
  bool theme=false,themeSupports=false,canvas=false,images=true,color=false;
  bool chrome=false,content=true,paginated=false,transformed=false,page=false,slice=false;
} env;
struct nsStyleDisplay {StyleAppearance EffectiveAppearance()const{return env.theme?StyleAppearance::Widget:StyleAppearance::None;}};
struct nsStyleBorder {};
struct nsIFrame {
  using Sides=int;
  nsStyleDisplay display;
  nsStyleDisplay* StyleDisplay(){return &display;}
  bool IsCanvasFrame(){return env.canvas;}
  Sides GetSkipSides(){return 0;}
};
struct nsITheme {
  bool ThemeSupportsWidget(void*,nsIFrame*,StyleAppearance){record("theme-support");return env.themeSupports;}
  void GetWidgetOverflow(void*,nsIFrame*,StyleAppearance,nsRect*){record("theme-overflow");}
  void DrawWidgetBackground(gfxContext*,nsIFrame*,StyleAppearance,nsRect,nsRect){record("theme-draw");}
};
struct Shell {nsIFrame* root;nsIFrame* GetRootFrame(){return root;}};
struct nsPresContext {
  nsITheme theme; Shell shell;
  nsITheme* Theme(){return &theme;}
  void* DeviceContext(){return nullptr;}
  int AppUnitsPerDevPixel(){return 1;}
  bool IsChrome(){return env.chrome;}
  bool IsPaginated(){return env.paginated;}
  Shell* PresShell(){return &shell;}
};
namespace nsLayoutUtils {
nsIFrame* GetClosestFrameOfType(nsIFrame* f,LayoutFrameType){record("page-frame");return env.page?f:nullptr;}
bool IsTransformed(nsIFrame*,nsIFrame*){record("transformed-query");return env.transformed;}
gfxRect RectToGfxRect(nsRect r,int){return r;}
}
bool XRE_IsContentProcess(){return env.content;}
nscolor NS_RGBA(int,int,int,int){return 0;}
struct StyleImage {
  int id=0;ImgDrawResult prepare=ImgDrawResult::SUCCESS,draw=ImgDrawResult::SUCCESS;
  double alpha=.5;
};
struct CSSSizeOrRatio {};
struct nsStyleImageLayers {
  struct Layer {
    StyleImage mImage;
    StyleMaskComposite mComposite=StyleMaskComposite::Add;
    CompositionOp mBlendMode=CompositionOp::OP_OVER;
    StyleMaskMode mMaskMode=StyleMaskMode::Alpha;
    StyleBackgroundClip mClip=StyleBackgroundClip::BorderBox;
    StyleImageLayerAttachment mAttachment=StyleImageLayerAttachment::Scroll;
    struct {StyleImageLayerRepeat mXRepeat=StyleImageLayerRepeat::NoRepeat,mYRepeat=StyleImageLayerRepeat::NoRepeat;} mRepeat;
    nsSize mSize{40,40};nsPoint mPosition;nsRect clip{0,0,40,40};bool dirty=true;
  };
  std::vector<Layer> mLayers;uint32_t mImageCount=0;
  const Layer& BottomLayer()const{return mLayers[mImageCount?mImageCount-1:0];}
};
struct nsStyleSVGReset {nsStyleImageLayers mMask;};
struct nsStyleBackground {nsStyleImageLayers mImage;};
struct ComputedStyle {
  nsStyleSVGReset reset;nsStyleBackground background;
  const nsStyleSVGReset* StyleSVGReset()const{return &reset;}
  const nsStyleBackground* StyleBackground()const{return &background;}
};
struct nsImageRenderer {
  @@IMAGE_FLAGS@@
  const StyleImage* image;ImgDrawResult mPrepareResult=ImgDrawResult::NOT_READY;
  ExtendMode mExtendMode=ExtendMode::CLAMP;StyleMaskMode mMaskOp=StyleMaskMode::MatchSource;
  nsImageRenderer(nsIFrame*,const StyleImage* p,uint32_t flags):image(p){record("renderer:"+std::to_string(p->id)+":"+std::to_string(flags));}
  bool PrepareImage(){mPrepareResult=image->prepare;record("prepare:"+std::to_string(image->id));return mPrepareResult==ImgDrawResult::SUCCESS;}
  @@READY@@
  CSSSizeOrRatio ComputeIntrinsicSize(){record("intrinsic");return {};}
  void SetPreferredSize(CSSSizeOrRatio,nsSize){record("preferred");}
  static void ComputeObjectAnchorPoint(nsPoint position,nsSize,nsSize,nsPoint* top,nsPoint* anchor){*top=position;*anchor=position;record("anchor");}
  ImgDrawResult DrawLayer(nsPresContext*,gfxContext& ctx,nsRect dest,nsRect fill,nsPoint anchor,nsRect dirty,nsSize repeat,float opacity){
    record("draw:"+std::to_string(image->id)+":"+std::to_string(int(ctx.op))+":"+rectText(dest)+":"+rectText(fill)+":"+std::to_string(anchor.x)+","+std::to_string(anchor.y)+":"+rectText(dirty)+":"+std::to_string(repeat.width)+","+std::to_string(repeat.height)+":"+std::to_string(int(mMaskOp))+":"+std::to_string(int(mExtendMode))+":"+matrixText(ctx.target->transform));
    ctx.target->alpha=composite(ctx.op,image->alpha*opacity,ctx.target->alpha);return image->draw;
  }
};
namespace mozilla {
using nsImageRenderer=::nsImageRenderer;using StyleImage=::StyleImage;using StyleMaskComposite=::StyleMaskComposite;using StyleMaskMode=::StyleMaskMode;
namespace gfx {using CompositionOp=::CompositionOp;using ExtendMode=::ExtendMode;}
}
@@STATE@@
struct ImageLayerClipState {
  nsRect mBGClipArea,mDirtyRectInAppUnits,mDirtyRectInDevPx;
  bool mCustomClip=false,mHasRoundedCorners=false;
};
void SetupDirtyRects(nsRect clip,nsRect dirty,int,nsRect* app,nsRect* dev){app->IntersectRect(clip,dirty);*dev=*app;record("dirty-rects");}
void GetImageLayerClip(const nsStyleImageLayers::Layer& layer,nsIFrame*,const nsStyleBorder&,nsRect,nsRect dirty,bool,int,ImageLayerClipState* state){
  state->mBGClipArea=layer.clip;state->mDirtyRectInAppUnits.IntersectRect(layer.clip,dirty);
  state->mDirtyRectInDevPx=layer.dirty?state->mDirtyRectInAppUnits:nsRect();record("clip:"+std::to_string(layer.mImage.id));
}
void SetupImageLayerClip(const ImageLayerClipState&,gfxContext* ctx,int,gfxContextAutoSaveRestore* save){save->EnsureSaved(ctx);record("setup-clip");}
nscolor DetermineBackgroundColor(nsPresContext*,const ComputedStyle*,nsIFrame*,bool& images,bool& color){images=env.images;color=env.color;record("background-selection");return 0;}
void DrawBackgroundColor(const ImageLayerClipState&,gfxContext*,int){record("background-color");}
nsRect BoxDecorationRectForBackground(nsIFrame*,nsRect r,int,const nsStyleBorder*){return r;}
nsRect BoxDecorationRectForBorder(nsIFrame*,nsRect r,int,const nsStyleBorder*){if(env.slice)r.width+=1;return r;}
nsRect ComputeImageLayerPositioningArea(nsPresContext*,nsIFrame* frame,nsRect r,const nsStyleImageLayers::Layer&,nsIFrame** attached,bool* transformed){*attached=frame;*transformed=env.transformed;record("position-area");return {0,0,r.width,r.height};}
nsSize ComputeDrawnSizeForBackground(CSSSizeOrRatio,nsSize,nsSize size,StyleImageLayerRepeat,StyleImageLayerRepeat){record("drawn-size");return size;}
nscoord ComputeSpacedRepeatSize(nscoord image,nscoord area,bool& repeats){repeats=area>=2*image;record("spaced-repeat");return repeats?area/2:image;}
@@ITERATION@@
struct nsCSSRendering {
  using Sides=nsIFrame::Sides;
  @@FLAGS@@
  @@PARAMS@@
  @@OPERATOR@@
  static CompositionOp GetGFXBlendMode(CompositionOp op){return op;}
  static nsBackgroundLayerState PrepareImageLayer(nsPresContext*,nsIFrame*,uint32_t,const nsRect&,const nsRect&,const nsStyleImageLayers::Layer&,bool*);
  static ImgDrawResult PaintStyleImageLayerWithSC(const PaintBGParams&,gfxContext&,const ComputedStyle*,const nsStyleBorder&);
};
