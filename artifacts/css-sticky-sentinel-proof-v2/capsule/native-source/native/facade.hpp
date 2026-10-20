#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

#define MOZ_ALWAYS_INLINE inline
#define MOZ_ASSERT(c, ...) do { if (!(c)) throw std::runtime_error("assertion"); } while (0)
#define NS_ASSERTION MOZ_ASSERT

std::vector<std::string> trace;
void event(const std::string& s) { trace.push_back(s); }
template<class T> struct Saturate {
  int64_t v;
  explicit Saturate(T a) : v(a) {}
  Saturate operator+(T b) const {
    return Saturate(static_cast<T>(std::clamp<int64_t>(v + b,
        std::numeric_limits<T>::min(), std::numeric_limits<T>::max())));
  }
  T value() const { return static_cast<T>(v); }
};

// EXTRACTED_CONSTANTS

struct nsPoint {
  nscoord x=0, y=0;
  nsPoint()=default;
  nsPoint(nscoord a, nscoord b):x(a),y(b){}
  bool operator==(const nsPoint& b) const { return x==b.x && y==b.y; }
  nsPoint operator+(const nsPoint& b) const { return {x+b.x,y+b.y}; }
  nsPoint operator-(const nsPoint& b) const { return {x-b.x,y-b.y}; }
};
struct nsRect {
  using T=nscoord;
  nscoord x=0,y=0,width=0,height=0;
  nsRect()=default;
  nsRect(nscoord a,nscoord b,nscoord c,nscoord d):x(a),y(b),width(c),height(d){}
  nsPoint TopLeft() const {return {x,y};}
  void MoveTo(nsPoint p) {x=p.x;y=p.y;}
  // EXTRACTED_FAR_METHODS
};
struct nsMargin { nscoord top,right,bottom,left; };
struct NormalTag {};
struct OffsetTag {};
namespace mozilla { class StickyScrollContainer; }
struct nsIFrame {
  int id=-1, depth=0;
  nsIFrame *first=nullptr,*next=nullptr,*parent=nullptr;
  bool hadNormal=true,sticky=true,hasContainer=true,geometryAvailable=true;
  nsPoint normal, fallback;
  nsRect mRect, currentStick,currentContain,ignoreStick,ignoreContain;
  std::optional<nsMargin> offsets,recomputed;
  static OffsetTag ComputedOffsetProperty(){return {};}
  static NormalTag NormalPositionProperty(){return {};}
  const nsMargin* GetProperty(OffsetTag) const {
    event("offset:"+std::to_string(id)+":"+(offsets?"1":"0"));
    return offsets ? &*offsets : nullptr;
  }
  nsPoint GetProperty(NormalTag,bool* present) const {
    event("normal:"+std::to_string(id)+":"+(hadNormal?"1":"0"));
    *present=hadNormal;return normal;
  }
  nsPoint GetPosition() const {return mRect.TopLeft();}
  nsPoint GetNormalPosition(bool* = nullptr) const;
  nsIFrame* GetParent() const {return parent;}
  bool IsStickyPositioned() const {return sticky;}
  nsPoint GetPositionIgnoringScrolling() const {event("fallback:"+std::to_string(id));return fallback;}
  nsPoint GetPositionIgnoringScrollingAndSticky() const;
  void MarkNeedsDisplayItemRebuild(){event("set:"+std::to_string(id)+":"+std::to_string(mRect.x)+":"+std::to_string(mRect.y));}
  void SetPosition(const nsPoint&);
};
namespace nsLayoutUtils {
bool IsFirstContinuationOrIBSplitSibling(const nsIFrame* f){return f==f->first;}
nsIFrame* FirstContinuationOrIBSplitSibling(const nsIFrame* f){event("first:"+std::to_string(f->id)+":"+std::to_string(f->first->id));return f->first;}
nsIFrame* GetNextContinuationOrIBSplitSibling(nsIFrame* f){event("next:"+std::to_string(f->id)+":"+std::to_string(f->next?f->next->id:-1));return f->next;}
}
namespace mozilla {
struct ScrollContainerFrame : nsIFrame {};
struct DepthOrderedFrameList {
  std::vector<nsIFrame*> frames;
  const std::vector<nsIFrame*>& IterFromShallowest() const {
    std::string s="order";for(auto* f:frames)s+=":"+std::to_string(f->id);event(s);return frames;
  }
};
struct OverflowChangedTracker {
  static constexpr int CHILDREN_CHANGED=1;
  void SetSubtreeRoot(nsIFrame* f){event("subtree:"+std::to_string(f?f->id:-1));}
  void AddFrame(nsIFrame* f,int reason){MOZ_ASSERT(reason==CHILDREN_CHANGED);event("overflow:"+std::to_string(f->id));}
  void Flush(){event("flush");}
};
nsIFrame* do_QueryFrame(ScrollContainerFrame* f){return f;}
class StickyScrollContainer {
 public:
  enum class StickyLimitSpace {RelativeToCurrentScroll,IgnoreCurrentScroll};
  struct StickyLimits {nsRect mStick,mContain;};
  ScrollContainerFrame* mScrollContainerFrame;
  nsPoint mScrollPosition;
  DepthOrderedFrameList mFrames;
  static StickyScrollContainer* active;
  static const StickyScrollContainer* GetForFrame(const nsIFrame* f){event("container:"+std::to_string(f->id));return f->hasContainer?active:nullptr;}
  StickyLimits ComputeStickyLimits(nsIFrame*,StickyLimitSpace) const;
  static void ComputeStickyOffsets(nsIFrame* f){event("recompute:"+std::to_string(f->id));f->offsets=f->recomputed;}
  nsPoint ComputePosition(nsIFrame*) const;
  nsPoint ComputePositionIgnoringScrolling(nsIFrame*) const;
  nsPoint DoComputePosition(nsIFrame*,StickyLimitSpace) const;
  nsPoint ComputeTranslationIgnoringScrolling(const nsIFrame*) const;
  bool IsStuckInYDirection(nsIFrame*) const;
  void PositionContinuations(nsIFrame*);
  void UpdatePositions(nsPoint,nsIFrame*);
};
StickyScrollContainer* StickyScrollContainer::active=nullptr;
}
