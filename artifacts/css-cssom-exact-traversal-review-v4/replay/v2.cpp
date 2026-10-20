#define CANDIDATE 1
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
 bool IsInSVGTextSubtree()const{return HasAnyStateBits(NS_FRAME_IS_SVG_TEXT);}
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

Matrix4x4Flagged nsIFrame::GetTransformMatrix(
    ViewportType aViewportType, RelativeTo aStopAtAncestor,
    nsIFrame** aOutAncestor, TransformMatrixFlags aFlags,
    Maybe<AppUnitTranslation>* aAppUnitTranslation) const {
  ++matrixCalls;
  MOZ_ASSERT(aOutAncestor, "Need a place to put the ancestor!");
  if (aAppUnitTranslation) {
    aAppUnitTranslation->reset();
  }

  auto GetPositionMaybeIgnoringScrolling = [aFlags](const nsIFrame* aFrame) {
    return aFlags.contains(TransformMatrixFlag::IgnoreScrolling)
               ? aFrame->GetPositionIgnoringScrollingAndSticky()
               : aFrame->GetPosition();
  };

  /* If we're transformed, we want to hand back the combination
   * transform/translate matrix that will apply our current transform, then
   * shift us to our parent.
   */
  const bool isTransformed = IsTransformed();
  const nsIFrame* zoomedContentRoot = nullptr;
  if (aStopAtAncestor.mViewportType == ViewportType::Visual) {
    zoomedContentRoot = ViewportUtils::IsZoomedContentRoot(this);
    if (zoomedContentRoot) {
      MOZ_ASSERT(aViewportType != ViewportType::Visual);
    }
  }

  if (isTransformed || zoomedContentRoot) {
    MOZ_ASSERT(GetParent());
    Matrix4x4Flagged result;
    int32_t scaleFactor = aFlags.contains(TransformMatrixFlag::InCSSUnits)
                              ? AppUnitsPerCSSPixel()
                              : PresContext()->AppUnitsPerDevPixel();

    /* Compute the delta to the parent, which we need because we are converting
     * coordinates to our parent.
     */
    if (isTransformed) {
      // Note: this converts from Matrix4x4 to Matrix4x4Flagged.
      result = nsDisplayTransform::GetResultingTransformMatrix(
          this, nsPoint(), scaleFactor,
          nsDisplayTransform::INCLUDE_PERSPECTIVE);
    }

    // The offset from a zoomed content root to its parent (e.g. from
    // a canvas frame to a scroll frame) is in layout coordinates, so
    // apply it before applying any layout-to-visual transform.
    *aOutAncestor = GetParent();
    nsPoint delta = GetPositionMaybeIgnoringScrolling(this);
    /* Combine the raw transform with a translation to our parent. */
    result.PostTranslate(NSAppUnitsToFloatPixels(delta.x, scaleFactor),
                         NSAppUnitsToFloatPixels(delta.y, scaleFactor), 0.0f);

    if (zoomedContentRoot) {
      Matrix4x4Flagged layoutToVisual;
      if (aFlags.contains(TransformMatrixFlag::InCSSUnits)) {
        layoutToVisual = ViewportUtils::GetVisualToLayoutTransform(
                             zoomedContentRoot->GetContent())
                             .Inverse()
                             .ToUnknownMatrix();
      } else {
        layoutToVisual =
            ViewportUtils::GetVisualToLayoutTransform<LayoutDevicePixel>(
                zoomedContentRoot->GetContent())
                .Inverse()
                .ToUnknownMatrix();
      }
      result = result * layoutToVisual;
    }

    return result;
  }

  bool canUseAppUnits =
      aAppUnitTranslation && aFlags.isEmpty() &&
      aViewportType == ViewportType::Layout &&
      aStopAtAncestor.mViewportType == ViewportType::Layout &&
      aStopAtAncestor.mFrame &&
      PresContext() == aStopAtAncestor.mFrame->PresContext() && GetParent() &&
      !IsInSVGTextSubtree() && !HasAnyStateBits(NS_FRAME_SVG_LAYOUT);

  // We are not transformed, so the returned transform is just going to be a
  // translation up to whatever ancestor we decide to stop at.

  nsPoint crossdocOffset;
  *aOutAncestor =
      nsLayoutUtils::GetCrossDocParentFrameInProcess(this, &crossdocOffset);

  /* Otherwise, we're not transformed.  In that case, we'll walk up the frame
   * tree until we either hit the root frame or something that may be
   * transformed.  We'll then change coordinates into that frame, since we're
   * guaranteed that nothing in-between can be transformed.  First, however,
   * we have to check to see if we have a parent.  If not, we'll set the
   * outparam to null (indicating that there's nothing left) and will hand back
   * the identity matrix.
   */
  if (!*aOutAncestor) {
    return Matrix4x4Flagged();
  }

  /* Keep iterating while the frame can't possibly be transformed. */
  const nsIFrame* current = this;
  auto shouldStopAt = [](const nsIFrame* aCurrent, RelativeTo& aStopAtAncestor,
                         nsIFrame* aOutAncestor, TransformMatrixFlags aFlags) {
    return aOutAncestor->IsTransformed() ||
           ((aStopAtAncestor.mViewportType == ViewportType::Visual) &&
            ViewportUtils::IsZoomedContentRoot(aOutAncestor)) ||
           (aFlags.contains(
                TransformMatrixFlag::StopAtStackingContextAndDisplayPort) &&
            (aOutAncestor->IsStackingContext() ||
             DisplayPortUtils::FrameHasDisplayPort(aOutAncestor, aCurrent)));
  };

  // We run the GetOffsetToCrossDoc code here as an optimization, instead of
  // walking the parent chain here and then asking GetOffsetToCrossDoc to walk
  // the same parent chain and compute the offset.
  const int32_t finalAPD = PresContext()->AppUnitsPerDevPixel();
  // offset accumulates the offset at finalAPD.
  nsPoint offset = GetPositionMaybeIgnoringScrolling(this);

  int32_t currAPD = (*aOutAncestor)->PresContext()->AppUnitsPerDevPixel();
  // docOffset accumulates the current offset at currAPD, and then flushes to
  // offset at finalAPD when the APD changes or we finish.
  nsPoint docOffset = crossdocOffset;
  MOZ_ASSERT(crossdocOffset == nsPoint(0, 0) || !GetParent());
  CheckedInt<int64_t> wideOffsetX(offset.x), wideOffsetY(offset.y);
  CheckedInt<int64_t> wideDocX(docOffset.x), wideDocY(docOffset.y);
 if(aAppUnitTranslation && injectedState){
  const int slot=(injectedState-1)%4; const int64_t extreme=injectedState>4?INT64_MIN:INT64_MAX;
  if(slot==0)wideDocX=extreme; if(slot==1)wideDocY=extreme;
  if(slot==2)wideOffsetX=extreme; if(slot==3)wideOffsetY=extreme;
 }

  auto addDocOffset = [&] {
    if (!aAppUnitTranslation) {
      offset += docOffset.ScaleToOtherAppUnits(currAPD, finalAPD);
      return true;
    }
    if (currAPD == finalAPD) {
      wideOffsetX += wideDocX;
      wideOffsetY += wideDocY;
    } else {
      if (!CheckedInt<nscoord>(wideDocX.value()).isValid() ||
          !CheckedInt<nscoord>(wideDocY.value()).isValid()) {
        return false;
      }
      const nsPoint scaled =
          nsPoint(nscoord(wideDocX.value()), nscoord(wideDocY.value()))
              .ScaleToOtherAppUnits(currAPD, finalAPD);
      wideOffsetX += scaled.x;
      wideOffsetY += scaled.y;
    }
    return wideOffsetX.isValid() && wideOffsetY.isValid();
  };

  while (*aOutAncestor != aStopAtAncestor.mFrame &&
         !shouldStopAt(current, aStopAtAncestor, *aOutAncestor, aFlags)) {
    const nsPoint position = GetPositionMaybeIgnoringScrolling(*aOutAncestor);
    if (aAppUnitTranslation) {
      wideDocX += position.x;
      wideDocY += position.y;
      if (!wideDocX.isValid() || !wideDocY.isValid()) {
        fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor, aOutAncestor,
                                  aFlags);
      }
      canUseAppUnits = canUseAppUnits &&
                       (*aOutAncestor)->PresContext() == PresContext() &&
                       !(*aOutAncestor)->IsInSVGTextSubtree() &&
                       !(*aOutAncestor)->HasAnyStateBits(NS_FRAME_SVG_LAYOUT);
    } else {
      docOffset += position;
    }

    nsIFrame* parent = (*aOutAncestor)->GetParent();
    if (!parent) {
      canUseAppUnits = false;
      crossdocOffset.x = crossdocOffset.y = 0;
      parent = nsLayoutUtils::GetCrossDocParentFrameInProcess(*aOutAncestor,
                                                              &crossdocOffset);

      int32_t newAPD =
          parent ? parent->PresContext()->AppUnitsPerDevPixel() : currAPD;
      if (!parent || newAPD != currAPD) {
        // Convert docOffset to finalAPD and add it to offset.
        if (!addDocOffset()) {
          fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor,
                                    aOutAncestor, aFlags);
        }
        docOffset.x = docOffset.y = 0;
        wideDocX = wideDocY = 0;
      }
      currAPD = newAPD;
      if (aAppUnitTranslation) {
        wideDocX += crossdocOffset.x;
        wideDocY += crossdocOffset.y;
        if (!wideDocX.isValid() || !wideDocY.isValid()) {
          fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor,
                                    aOutAncestor, aFlags);
        }
      } else {
        docOffset += crossdocOffset;
      }

      if (!parent) {
        break;
      }
    }

    current = *aOutAncestor;
    *aOutAncestor = parent;
  }
  if (!addDocOffset()) {
    fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor, aOutAncestor,
                              aFlags);
  }
  if (canUseAppUnits && *aOutAncestor == aStopAtAncestor.mFrame &&
      currAPD == finalAPD) {
    *aAppUnitTranslation =
        Some(AppUnitTranslation{wideOffsetX.value(), wideOffsetY.value()});
  }

  NS_ASSERTION(*aOutAncestor, "Somehow ended up with a null ancestor...?");

  int32_t scaleFactor = aFlags.contains(TransformMatrixFlag::InCSSUnits)
                            ? AppUnitsPerCSSPixel()
                            : PresContext()->AppUnitsPerDevPixel();
  if (aAppUnitTranslation) {
    return Matrix4x4Flagged::Translation2d(
        float(wideOffsetX.value()) / scaleFactor,
        float(wideOffsetY.value()) / scaleFactor);
  }
  return Matrix4x4Flagged::Translation2d(
      NSAppUnitsToFloatPixels(offset.x, scaleFactor),
      NSAppUnitsToFloatPixels(offset.y, scaleFactor));
}
Matrix4x4Flagged nsLayoutUtils::GetTransformToAncestor(
    RelativeTo aFrame, RelativeTo aAncestor, TransformMatrixFlags aFlags,
    nsIFrame** aOutAncestor, Maybe<AppUnitTranslation>* aAppUnitTranslation) {
  if (aAppUnitTranslation) {
    aAppUnitTranslation->reset();
  }
  nsIFrame* parent;
  Matrix4x4Flagged ctm;
  // Make sure we don't get an invalid combination of source and destination
  // RelativeTo values.
  MOZ_ASSERT(!(aFrame.mViewportType == ViewportType::Visual &&
               aAncestor.mViewportType == ViewportType::Layout));
  if (aFrame == aAncestor) {
    return ctm;
  }
  ctm = aFrame.mFrame->GetTransformMatrix(aFrame.mViewportType, aAncestor,
                                          &parent, aFlags, aAppUnitTranslation);
  if (aAppUnitTranslation && parent != aAncestor.mFrame) {
    aAppUnitTranslation->reset();
  }
  if (!aFrame.mFrame->Combines3DTransformWithAncestors()) {
    ctm.ProjectTo2D();
  }
  while (parent && parent != aAncestor.mFrame &&
         (!aFlags.contains(
              TransformMatrixFlag::StopAtStackingContextAndDisplayPort) ||
          (!parent->IsStackingContext() &&
           !DisplayPortUtils::FrameHasDisplayPort(parent)))) {
    nsIFrame* cur = parent;
    ctm = ctm * cur->GetTransformMatrix(aFrame.mViewportType, aAncestor,
                                        &parent, aFlags);
    if (!cur->Combines3DTransformWithAncestors()) {
      ctm.ProjectTo2D();
    }
  }
  if (aOutAncestor) {
    *aOutAncestor = parent;
  }
  return ctm;
}
static nsRect TransformClientRectToAncestor(const nsIFrame* aFrame,
                                            const nsRect& aRect,
                                            const nsIFrame* aAncestor) {
  if (!aAncestor || aFrame->PresContext() != aAncestor->PresContext() ||
      aFrame->IsInSVGTextSubtree() ||
      aFrame->HasAnyStateBits(NS_FRAME_SVG_LAYOUT) || aRect.width < 0 ||
      aRect.height < 0 || aRect.width > nscoord_MAX ||
      aRect.height > nscoord_MAX) {
    return nsLayoutUtils::TransformFrameRectToAncestor(aFrame, aRect,
                                                       aAncestor);
  }
  Maybe<AppUnitTranslation> translation;
  Maybe<Matrix4x4Flagged> matrix = Some(nsLayoutUtils::GetTransformToAncestor(
      RelativeTo{aFrame}, RelativeTo{aAncestor}, {}, nullptr, &translation));
  if (aFrame == aAncestor) {
    translation = Some(AppUnitTranslation{0, 0});
  }
  if (translation) {
    const auto x = CheckedInt<int64_t>(aRect.x) + translation->x;
    const auto y = CheckedInt<int64_t>(aRect.y) + translation->y;
    const auto right = x + aRect.width;
    const auto bottom = y + aRect.height;
    if (x.isValid() && y.isValid() && right.isValid() && bottom.isValid() &&
        x.value() >= nscoord_MIN && y.value() >= nscoord_MIN &&
        right.value() <= nscoord_MAX && bottom.value() <= nscoord_MAX) {
      return nsRect(nscoord(x.value()), nscoord(y.value()), aRect.width,
                    aRect.height);
    }
  }
  return nsLayoutUtils::TransformFrameRectToAncestor(aFrame, aRect, aAncestor,
                                                     nullptr, &matrix);
}
static Maybe<nsRect> GetUntransformedRectToAncestor(
    const nsIFrame* aFrame, const nsRect& aRect, const nsIFrame* aAncestor) {
  if (!aAncestor || aRect.width < 0 || aRect.height < 0 ||
      aRect.width > nscoord_MAX || aRect.height > nscoord_MAX) {
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
    x += frame->GetPosition().x;
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


nsRect nsLayoutUtils::TransformFrameRectToAncestor(const nsIFrame* frame,const nsRect& r,const nsIFrame* ancestor,bool*,Maybe<Matrix4x4Flagged>* cache) {
 fallbackCalls++;
 Matrix4x4Flagged m;
 if(cache&&*cache){cachedFallbackCalls++;m=cache->value();}
 else m=GetTransformToAncestor(RelativeTo{frame},RelativeTo{ancestor});
 float apd=frame->PresContext()->apd, target=ancestor->PresContext()->apd;
 auto coord=[](double n){return int32_t(std::fmax(nscoord_MIN,std::fmin(nscoord_MAX,std::floor(n+0.5))));};
 return nsRect(coord((float(r.x)/apd*m.sx+m.tx)*target),coord((float(r.y)/apd*m.sy+m.ty)*target),coord(float(r.width)/apd*m.sx*target),coord(float(r.height)/apd*m.sy*target));
}
int main(int argc,char** argv){
 Context context,other;other.apd=30;
#if CANDIDATE
 if(argc>1 && std::string(argv[1]).find("injected-")==0){
  injectedState=std::stoi(std::string(argv[1]).substr(9));
  require(injectedState>=1&&injectedState<=8,450);
  const int sign=injectedState>4?-1:1;
  const bool y=injectedState%2==0;
  nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;
  leaf.parent=&mid;mid.parent=&root;
  leaf.position=mid.position=y?nsPoint(0,sign):nsPoint(sign,0);
  Maybe<AppUnitTranslation> exact=Some(AppUnitTranslation{5,6});
  nsIFrame* stop=nullptr;matrixCalls=0;
  auto m=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},&stop,&exact);
  require(!exact&&matrixCalls==2&&stop==&root,451);
  require(m.tx==(y?0:float(2*sign)/60)&&m.ty==(y?float(2*sign)/60:0),452);
  printf("INJECTED_GUARD_PASS %d\n",injectedState);
  return 0;
 }
#endif
 if(argc>1){
  nsIFrame root,a,b,leaf;root.context=a.context=b.context=leaf.context=&context;
  leaf.parent=&a;a.parent=&b;b.parent=&root;
  bool grouping=std::string(argv[1])=="grouping";
  bool restart=std::string(argv[1])=="crossdoc-restart";
  nsRect box(0,0,1,1);
  if(grouping||restart){leaf.position={-2000000000,0};a.position={1400000000,0};b.position={1400000000,0};}
  else{leaf.position={1500000000,0};a.position={1000000000,0};box.x=-2000000000;}
  if(restart){
   Context targetContext;
   other.apd=29;a.context=b.context=&other;root.context=&targetContext;
   leaf.crossParent=&a;leaf.parent=nullptr;
   b.crossParent=&root;b.parent=nullptr;
#if CANDIDATE
   Maybe<AppUnitTranslation> exact;
   (void)nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},nullptr,&exact);
#else
   (void)nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root});
#endif
   require(false,405);
  }
#if CANDIDATE
  auto r=TransformClientRectToAncestor(&leaf,box,&root);
  require(r.x==(grouping?800000000:500000000)&&fallbackCalls==0,400);
  printf("WIDE_WITNESS_PASS %s %d\n",argv[1],r.x);
#else
  auto r=nsLayoutUtils::TransformFrameRectToAncestor(&leaf,box,&root);
  printf("LEGACY_WITNESS_RETURN %d\n",r.x);
#endif
  return 0;
 }
 int rows=0;
 for(int depth : {1,8,128})for(int mode=0;mode<14;mode++)for(int flags : {0,1,2,4}) {
  std::vector<nsIFrame> frames(depth+1);
  for(int i=0;i<=depth;i++){auto&f=frames[i];f.context=&context;if(i<depth)f.parent=&frames[i+1];f.position={i+1,-i};f.ignoredPosition={i+11,3-i};}
  nsIFrame* leaf=&frames[0];nsIFrame* root=&frames[depth];
  int selected=depth==1?0:depth-1;
  if(mode==1||mode==2){auto&f=frames[mode==1?0:selected];f.transformed=true;f.transform.sx=2;f.transform.sy=3;f.transform.tx=4;f.transform.ty=-5;f.transform.trace="X";}
  if(mode==3)frames[selected].svgText=true;
  if(mode==4)frames[selected].states=NS_FRAME_SVG_LAYOUT;
  if(mode==5)frames[selected].context=&other;
  if(mode==6){frames[selected].crossParent=frames[selected].parent;frames[selected].parent=nullptr;frames[selected].crossOffset={4,8};}
  if(mode==12||mode==13){
   other.apd=mode==12?29:61;
   for(int i=0;i<=selected;i++)frames[i].context=&other;
   frames[selected].crossParent=frames[selected].parent;frames[selected].parent=nullptr;
   frames[selected].crossOffset={5,-7};
  }
  if(mode==7){frames[selected].zoomed=true;}
  if(mode==8){frames[selected].stacking=true;}
  if(mode==9){frames[selected].displayPort=true;}
  if(mode==10){frames[0].combines=true;}
  if(mode==11){root->transformed=true;root->transform.tx=700;root->transform.trace="TARGET";}
  RelativeTo target{root,mode==7?ViewportType::Visual:ViewportType::Layout};
  nsIFrame* stop=nullptr;matrixCalls=0;
#if CANDIDATE
  Maybe<AppUnitTranslation> exact=Some(AppUnitTranslation{123,456});
  auto m=nsLayoutUtils::GetTransformToAncestor(RelativeTo{leaf},target,TransformMatrixFlags{unsigned(flags)},&stop,&exact);
  if(flags||mode==1||mode==2||mode==3||mode==4||mode==5||mode==6||mode==7||mode==12||mode==13)require(!exact,100+mode);
  else {require(bool(exact),200+mode);require(exact->x==depth*(depth+1)/2 && exact->y==-depth*(depth-1)/2,220+mode);}
#else
  auto m=nsLayoutUtils::GetTransformToAncestor(RelativeTo{leaf},target,TransformMatrixFlags{unsigned(flags)},&stop);
#endif
  printf("ROW %d %d %d %.9g %.9g %.9g %.9g %s %d %td\n",depth,mode,flags,m.sx,m.sy,m.tx,m.ty,m.trace.c_str(),matrixCalls,stop?stop-frames.data():-1);
#if CANDIDATE
  int calls=matrixCalls;matrixCalls=0;nsIFrame* noOptStop=nullptr;
  auto noOpt=nsLayoutUtils::GetTransformToAncestor(RelativeTo{leaf},target,TransformMatrixFlags{unsigned(flags)},&noOptStop);
  require(noOpt.sx==m.sx&&noOpt.sy==m.sy&&noOpt.tx==m.tx&&noOpt.ty==m.ty&&noOpt.trace==m.trace&&noOptStop==stop&&matrixCalls==calls,270+mode);
#endif
  rows++;
 }
#if CANDIDATE
 nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;mid.parent=&root;leaf.parent=&mid;
 mid.position={700,1100};leaf.position={-8383188,-1100};
 matrixCalls=fallbackCalls=cachedFallbackCalls=0;
 auto r=TransformClientRectToAncestor(&leaf,nsRect(0,0,8388488,600),&root);
 require(r.x==-8382488 && r.y==0 && int64_t(r.x)+r.width==6000 && !fallbackCalls && matrixCalls==1,301);
 for(int boundary=0;boundary<8;boundary++){
  mid.transformed=boundary==0;mid.svgText=boundary==1;mid.states=boundary==2?NS_FRAME_SVG_LAYOUT:(boundary==7?NS_FRAME_IS_SVG_TEXT:0);
  mid.context=boundary==3?&other:&context;
  nsRect box=boundary==4?nsRect(nscoord_MAX,0,1,1):nsRect(0,0,8388488,600);
  if(boundary==5)box=nsRect(0,0,nscoord_MAX+1,1);
  if(boundary==6)box=nsRect(0,0,-1,1);
  if(boundary==4){leaf.position={0,0};mid.position={0,0};}
  matrixCalls=fallbackCalls=cachedFallbackCalls=0;
  (void)TransformClientRectToAncestor(&leaf,box,&root);
  require(fallbackCalls==1,310+boundary);
  require(cachedFallbackCalls==((boundary<5||boundary==7)?1:0),320+boundary);
  require(matrixCalls==(boundary==0?2:1),330+boundary);
 }
 matrixCalls=fallbackCalls=0;
 r=TransformClientRectToAncestor(&root,nsRect(-8382488,0,8388488,1),&root);
 require(r.x==-8382488 && int64_t(r.x)+r.width==6000 && !fallbackCalls && matrixCalls==0,339);
 leaf.parent=&root;leaf.position={0,0};
 Maybe<AppUnitTranslation> exact=Some(AppUnitTranslation{5,6});
 (void)nsLayoutUtils::GetTransformToAncestor(RelativeTo{&root},RelativeTo{&root},{},nullptr,&exact);require(!exact,340);
 nsIFrame* stop=nullptr;exact=Some(AppUnitTranslation{5,6});
 (void)root.GetTransformMatrix(ViewportType::Layout,RelativeTo{nullptr},&stop,{},&exact);require(!exact,341);
 mid.states=0;leaf.position={nscoord_MAX+100,0};mid.position={-nscoord_MAX-100,0};leaf.parent=&mid;mid.parent=&root;mid.context=&context;
 matrixCalls=fallbackCalls=0;r=TransformClientRectToAncestor(&leaf,nsRect(0,0,1,1),&root);require(r.x==0 && !fallbackCalls,342);
 leaf.parent=&mid;mid.parent=&root;leaf.position={1500000000,0};mid.position={-2000000000,0};
 nsRect expandedBox(1000000000,0,1,1);
 require(!GetUntransformedRectToAncestor(&leaf,expandedBox,&root),343);
 fallbackCalls=0;r=TransformClientRectToAncestor(&leaf,expandedBox,&root);
 require(r.x==500000000&&!fallbackCalls,344);
 int admitted=0;
 uint32_t random=123456789;
 auto next=[&](){random=random*1664525u+1013904223u;return random;};
 for(int sample=0;sample<2048;sample++){
  int depth=1+next()%16;
  std::vector<nsIFrame> frames(depth+1);
  for(int i=0;i<=depth;i++){frames[i].context=&context;if(i<depth)frames[i].parent=&frames[i+1];
   frames[i].position={int32_t(next()%200000001)-100000000,int32_t(next()%200000001)-100000000};}
  nsRect box(int32_t(next()%200000001)-100000000,int32_t(next()%200000001)-100000000,1+next()%1000,1+next()%1000);
  auto expected=GetUntransformedRectToAncestor(&frames[0],box,&frames[depth]);
  if(!expected)continue;
  fallbackCalls=0;auto actual=TransformClientRectToAncestor(&frames[0],box,&frames[depth]);
  require(actual.x==expected->x&&actual.y==expected->y&&actual.width==expected->width&&actual.height==expected->height&&!fallbackCalls,401);
  admitted++;
 }
 require(admitted>1000,402);
 printf("V1_DOMAIN_PASS %d\n",admitted);
 puts("EXACT_CHECKS_PASS");
#endif
 printf("ROWS %d\n",rows);
}
