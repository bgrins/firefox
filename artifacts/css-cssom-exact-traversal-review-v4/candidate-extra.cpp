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

  auto traverse = [&]<bool TrackWide, bool CommonLayout>() {
    auto getPosition = [&](const nsIFrame* aFrame) {
      if constexpr (CommonLayout) {
        return aFrame->GetPosition();
      } else {
        return GetPositionMaybeIgnoringScrolling(aFrame);
      }
    };
    const auto* sourceContext = PresContext();
    bool canUseAppUnits =
        TrackWide && aFlags.isEmpty() &&
        aViewportType == ViewportType::Layout &&
        aStopAtAncestor.mViewportType == ViewportType::Layout &&
        aStopAtAncestor.mFrame &&
        sourceContext == aStopAtAncestor.mFrame->PresContext() && GetParent() &&
        !HasAnyStateBits(NS_FRAME_IS_SVG_TEXT | NS_FRAME_SVG_LAYOUT);

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
     * outparam to null (indicating that there's nothing left) and will hand
     * back the identity matrix.
     */
    if (!*aOutAncestor) {
      return Matrix4x4Flagged();
    }

    /* Keep iterating while the frame can't possibly be transformed. */
    const nsIFrame* current = this;
    auto shouldStopAt = [](const nsIFrame* aCurrent,
                           RelativeTo& aStopAtAncestor, nsIFrame* aOutAncestor,
                           TransformMatrixFlags aFlags) {
      if constexpr (CommonLayout) {
        return aOutAncestor->IsTransformed();
      } else {
        return aOutAncestor->IsTransformed() ||
               ((aStopAtAncestor.mViewportType == ViewportType::Visual) &&
                ViewportUtils::IsZoomedContentRoot(aOutAncestor)) ||
               (aFlags.contains(
                    TransformMatrixFlag::StopAtStackingContextAndDisplayPort) &&
                (aOutAncestor->IsStackingContext() ||
                 DisplayPortUtils::FrameHasDisplayPort(aOutAncestor,
                                                       aCurrent)));
      }
    };

    // We run the GetOffsetToCrossDoc code here as an optimization, instead of
    // walking the parent chain here and then asking GetOffsetToCrossDoc to walk
    // the same parent chain and compute the offset.
    const int32_t finalAPD = PresContext()->AppUnitsPerDevPixel();
    // offset accumulates the offset at finalAPD.
    nsPoint offset = getPosition(this);

    int32_t currAPD = (*aOutAncestor)->PresContext()->AppUnitsPerDevPixel();
    // docOffset accumulates the current offset at currAPD, and then flushes to
    // offset at finalAPD when the APD changes or we finish.
    nsPoint docOffset = crossdocOffset;
    MOZ_ASSERT(crossdocOffset == nsPoint(0, 0) || !GetParent());
    int64_t wideOffsetX = offset.x, wideOffsetY = offset.y;
    int64_t wideDocX = docOffset.x, wideDocY = docOffset.y;
 if(aAppUnitTranslation && injectedState){
  const int slot=(injectedState-1)%4; const int64_t extreme=injectedState>4?INT64_MIN:INT64_MAX;
  if(slot==0)wideDocX=extreme; if(slot==1)wideDocY=extreme;
  if(slot==2)wideOffsetX=extreme; if(slot==3)wideOffsetY=extreme;
 }

    auto addDocOffset = [&] {
      if constexpr (!TrackWide) {
        offset += docOffset.ScaleToOtherAppUnits(currAPD, finalAPD);
        return true;
      } else {
        int64_t x = wideDocX, y = wideDocY;
        if (currAPD != finalAPD) {
          if (!CheckedInt<nscoord>(x).isValid() ||
              !CheckedInt<nscoord>(y).isValid()) {
            return false;
          }
          const nsPoint scaled = nsPoint(nscoord(x), nscoord(y))
                                     .ScaleToOtherAppUnits(currAPD, finalAPD);
          x = scaled.x;
          y = scaled.y;
        }
        int64_t nextX, nextY;
        if (!SafeAdd(wideOffsetX, x, &nextX) ||
            !SafeAdd(wideOffsetY, y, &nextY)) {
          return false;
        }
        wideOffsetX = nextX;
        wideOffsetY = nextY;
        return true;
      }
    };

    while (*aOutAncestor != aStopAtAncestor.mFrame &&
           !shouldStopAt(current, aStopAtAncestor, *aOutAncestor, aFlags)) {
      const nsPoint position = getPosition(*aOutAncestor);
      if constexpr (TrackWide) {
        int64_t nextX, nextY;
        if (!SafeAdd(wideDocX, int64_t(position.x), &nextX) ||
            !SafeAdd(wideDocY, int64_t(position.y), &nextY)) {
          fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor,
                                    aOutAncestor, aFlags);
        }
        wideDocX = nextX;
        wideDocY = nextY;
        canUseAppUnits =
            canUseAppUnits && (*aOutAncestor)->PresContext() == sourceContext &&
            !(*aOutAncestor)
                 ->HasAnyStateBits(NS_FRAME_IS_SVG_TEXT | NS_FRAME_SVG_LAYOUT);
      } else {
        docOffset += position;
      }

      nsIFrame* parent = (*aOutAncestor)->GetParent();
      if (!parent) {
        canUseAppUnits = false;
        crossdocOffset.x = crossdocOffset.y = 0;
        parent = nsLayoutUtils::GetCrossDocParentFrameInProcess(
            *aOutAncestor, &crossdocOffset);

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
        if constexpr (TrackWide) {
          int64_t nextX, nextY;
          if (!SafeAdd(wideDocX, int64_t(crossdocOffset.x), &nextX) ||
              !SafeAdd(wideDocY, int64_t(crossdocOffset.y), &nextY)) {
            fprintf(stderr, "NUMERIC_RESTART\n"); return GetTransformMatrix(aViewportType, aStopAtAncestor,
                                      aOutAncestor, aFlags);
          }
          wideDocX = nextX;
          wideDocY = nextY;
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
      *aAppUnitTranslation = Some(AppUnitTranslation{wideOffsetX, wideOffsetY});
    }

    NS_ASSERTION(*aOutAncestor, "Somehow ended up with a null ancestor...?");

    int32_t scaleFactor = aFlags.contains(TransformMatrixFlag::InCSSUnits)
                              ? AppUnitsPerCSSPixel()
                              : PresContext()->AppUnitsPerDevPixel();
    if constexpr (TrackWide) {
      return Matrix4x4Flagged::Translation2d(float(wideOffsetX) / scaleFactor,
                                             float(wideOffsetY) / scaleFactor);
    }
    return Matrix4x4Flagged::Translation2d(
        NSAppUnitsToFloatPixels(offset.x, scaleFactor),
        NSAppUnitsToFloatPixels(offset.y, scaleFactor));
  };
  if (aFlags.isEmpty() && aViewportType == ViewportType::Layout &&
      aStopAtAncestor.mViewportType == ViewportType::Layout) {
    if (!aAppUnitTranslation) {
      return traverse.operator()<false, true>();
    }
    return traverse.operator()<true, true>();
  }
  if (!aAppUnitTranslation) {
    return traverse.operator()<false, false>();
  }
  return traverse.operator()<true, false>();
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
int main() {
 Context context;
 int rows=0;
 for(unsigned flags=0;flags<8;flags++)for(int view=0;view<3;view++)for(int transformed=0;transformed<2;transformed++) {
  nsIFrame root,mid,leaf;
  root.context=mid.context=leaf.context=&context;leaf.parent=&mid;mid.parent=&root;
  leaf.position={13,-7};mid.position={19,23};leaf.ignoredPosition={101,103};mid.ignoredPosition={107,109};
  mid.transformed=transformed;mid.stacking=true;mid.displayPort=true;
  mid.transform.sx=2;mid.transform.sy=3;mid.transform.tx=11;mid.transform.ty=-17;mid.transform.trace="X";
  RelativeTo from{&leaf,view==2?ViewportType::Visual:ViewportType::Layout};
  RelativeTo to{&root,view?ViewportType::Visual:ViewportType::Layout};
  Maybe<AppUnitTranslation> exact=Some(AppUnitTranslation{7,8});nsIFrame* stop=nullptr;
  matrixCalls=0;auto m=nsLayoutUtils::GetTransformToAncestor(from,to,TransformMatrixFlags{flags},&stop,&exact);
  require(bool(exact)==(!flags&&!view&&!transformed),600);
  if(exact)require(exact->x==32&&exact->y==16,601);
  int calls=matrixCalls;matrixCalls=0;nsIFrame* other=nullptr;
  auto n=nsLayoutUtils::GetTransformToAncestor(from,to,TransformMatrixFlags{flags},&other);
  require(m.sx==n.sx&&m.sy==n.sy&&m.tx==n.tx&&m.ty==n.ty&&m.trace==n.trace&&stop==other&&calls==matrixCalls,602);
  printf("DISPATCH %u %d %d %.9g %.9g %.9g %.9g %s %d %d\n",flags,view,transformed,m.sx,m.sy,m.tx,m.ty,m.trace.c_str(),calls,stop==&root);
  rows++;
 }
 for(unsigned bits : {0u,1u,2u,3u,8u,9u,10u,11u})for(int atLeaf=0;atLeaf<2;atLeaf++) {
  nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;leaf.parent=&mid;mid.parent=&root;
  (atLeaf?leaf:mid).states=bits;
  Maybe<AppUnitTranslation> exact;nsIFrame* stop=nullptr;
  nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},&stop,&exact);
  require(bool(exact)==!(bits&(NS_FRAME_IS_SVG_TEXT|NS_FRAME_SVG_LAYOUT)),603);
 }
 nsIFrame root,a,b,leaf;for(auto*f:{&root,&a,&b,&leaf})f->context=&context;
 leaf.parent=&a;a.parent=&b;b.parent=&root;
 auto check=[&](nsRect box,int x,int y,int id){fallbackCalls=0;auto r=TransformClientRectToAncestor(&leaf,box,&root);require(r.x==x&&r.y==y&&!fallbackCalls,id);};
 leaf.position={-2000000000,-2000000000};a.position={1400000000,1400000000};b.position={1400000000,1400000000};
 check(nsRect(0,0,1,1),800000000,800000000,604);
 leaf.position={-1500000000,-1500000000};a.position={-1000000000,-1000000000};b.position={0,0};
 check(nsRect(2000000000,2000000000,1,1),-500000000,-500000000,605);
 leaf.position={1500000000,1500000000};a.position={-2000000000,-2000000000};
 nsRect expanded(1000000000,1000000000,1,1);require(!GetUntransformedRectToAncestor(&leaf,expanded,&root),606);
 check(expanded,500000000,500000000,607);
 leaf.position={6000,6000};a.position={0,0};
 fallbackCalls=cachedFallbackCalls=matrixCalls=0;
 (void)TransformClientRectToAncestor(&leaf,nsRect(0,nscoord_MAX,1,1),&root);
 require(fallbackCalls==1&&cachedFallbackCalls==1&&matrixCalls==1,608);

 {
  nsIFrame root,mid,leaf;root.context=mid.context=leaf.context=&context;
  leaf.parent=&mid;mid.parent=&root;leaf.position={13,-7};mid.position={19,23};
  leaf.ignoredPosition={101,103};mid.ignoredPosition={107,109};
  nsIFrame* stop=nullptr;matrixCalls=0;
  auto ignored=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},TransformMatrixFlags{1},&stop);
  require(ignored.tx==float(208)/60&&ignored.ty==float(212)/60&&stop==&root&&matrixCalls==1,620);
  mid.stacking=true;matrixCalls=0;
  auto stopped=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},TransformMatrixFlags{4},&stop);
  require(stopped.tx==float(13)/60&&stopped.ty==float(-7)/60&&stop==&mid&&matrixCalls==1,621);
  mid.stacking=false;mid.zoomed=true;matrixCalls=0;
  auto visual=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root,ViewportType::Visual},{},&stop);
  require(visual.sx==2&&visual.sy==2&&stop==&root&&matrixCalls==2,622);
  matrixCalls=0;
  auto layout=nsLayoutUtils::GetTransformToAncestor(RelativeTo{&leaf},RelativeTo{&root},{},&stop);
  require(layout.sx==1&&layout.sy==1&&layout.tx==float(32)/60&&layout.ty==float(16)/60&&stop==&root&&matrixCalls==1,623);
  printf("NULL_BOUNDARIES_PASS %.9g %.9g %.9g %.9g\n",ignored.tx,stopped.tx,visual.tx,layout.tx);
 }
 const int64_t values[]={INT64_MIN,INT64_MIN+1,-4294967295LL,-1,0,1,4294967295LL,INT64_MAX-1,INT64_MAX};
 int arithmetic=0;
 for(int64_t x:values)for(int64_t y:values){
  int64_t output=123;
  bool success=SafeAdd(x,y,&output);
  auto old=CheckedInt<int64_t>(x)+CheckedInt<int64_t>(y);
  require(success==old.isValid(),609);
  if(success)require(output==old.value(),610);
  arithmetic++;
 }
 printf("INDEPENDENT_PASS dispatch=%d masks=16 geometry=4 arithmetic=%d\n",rows,arithmetic);
}
