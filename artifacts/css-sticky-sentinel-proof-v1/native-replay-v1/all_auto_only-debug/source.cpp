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

using nscoord = int32_t;
inline constexpr nscoord nscoord_MAX = (1 << 30) - 1;
inline constexpr nscoord nscoord_MIN = -nscoord_MAX;
inline constexpr nscoord NS_UNCONSTRAINEDSIZE = nscoord_MAX;
inline constexpr nscoord NS_AUTOOFFSET = NS_UNCONSTRAINEDSIZE;

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
  MOZ_ALWAYS_INLINE T XMost() const {
    if constexpr (std::is_integral_v<T>) {
      return (Saturate<T>(x) + width).value();
    } else {
      return x + width;
    }
  }
MOZ_ALWAYS_INLINE T YMost() const {
    if constexpr (std::is_integral_v<T>) {
      return (Saturate<T>(y) + height).value();
    } else {
      return y + height;
    }
  }
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

namespace mozilla {
static constexpr nscoord gUnboundedNegative = nscoord_MIN / 2;
static constexpr nscoord gUnboundedExtent = nscoord_MAX;
static constexpr nscoord gUnboundedPositive =
    gUnboundedNegative + gUnboundedExtent;
static_assert(NS_AUTOOFFSET == 1073741823 && gUnboundedNegative == -536870911 && gUnboundedPositive == 536870912);

StickyScrollContainer::StickyLimits StickyScrollContainer::ComputeStickyLimits(nsIFrame* f,StickyLimitSpace space) const {
  event("limits:"+std::to_string(f->id)+":"+(space==StickyLimitSpace::IgnoreCurrentScroll?"ignore":"current"));
  if(!f->geometryAvailable)throw std::runtime_error("unavailable geometry");
  MOZ_ASSERT(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(f));
  const nsMargin* offsets=f->GetProperty(nsIFrame::ComputedOffsetProperty());
  if(!offsets) {nsRect r(gUnboundedNegative,gUnboundedNegative,gUnboundedExtent,gUnboundedExtent);return {r,r};}
  if(space==StickyLimitSpace::IgnoreCurrentScroll)return {f->ignoreStick,f->ignoreContain};
  return {f->currentStick,f->currentContain};
}
nsPoint StickyScrollContainer::ComputePosition(nsIFrame* aFrame) const {
  return DoComputePosition(aFrame, StickyLimitSpace::RelativeToCurrentScroll);
}

nsPoint StickyScrollContainer::ComputePositionIgnoringScrolling(
    nsIFrame* aFrame) const {
  return DoComputePosition(aFrame, StickyLimitSpace::IgnoreCurrentScroll);
}

nsPoint StickyScrollContainer::DoComputePosition(
    nsIFrame* aFrame, StickyLimitSpace aSpace) const {
  const auto [stick, contain] = ComputeStickyLimits(aFrame, aSpace);

  nsPoint position = aFrame->GetNormalPosition();
  const nsMargin* computedOffsets =
      aFrame->GetProperty(nsIFrame::ComputedOffsetProperty());
  if (!computedOffsets) {
    return position;
  }

  if (computedOffsets->top == NS_AUTOOFFSET && computedOffsets->bottom == NS_AUTOOFFSET && computedOffsets->left == NS_AUTOOFFSET && computedOffsets->right == NS_AUTOOFFSET) return position;

  // For each sticky direction (top, bottom, left, right), move the frame along
  // the appropriate axis, based on the scroll position, but limit this to keep
  // the element's margin box within the containing block.
  position.y = std::max(position.y, std::min(stick.y, contain.YMost()));
  position.y = std::min(position.y, std::max(stick.YMost(), contain.y));
  position.x = std::max(position.x, std::min(stick.x, contain.XMost()));
  position.x = std::min(position.x, std::max(stick.XMost(), contain.x));

  return position;
}

nsPoint StickyScrollContainer::ComputeTranslationIgnoringScrolling(
    const nsIFrame* aFrame) const {
  nsIFrame* first = nsLayoutUtils::FirstContinuationOrIBSplitSibling(aFrame);
  return ComputePositionIgnoringScrolling(first) - first->GetNormalPosition();
}

bool StickyScrollContainer::IsStuckInYDirection(nsIFrame* aFrame) const {
  nsPoint position = ComputePosition(aFrame);
  return position.y != aFrame->GetNormalPosition().y;
}

void StickyScrollContainer::PositionContinuations(nsIFrame* aFrame) {
  NS_ASSERTION(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(aFrame),
               "Should be starting from the first continuation");
  bool hadProperty;
  const nsPoint normalPosition = aFrame->GetNormalPosition(&hadProperty);
  if (!hadProperty) {
    // We have no normal position to stick from. This happens when the frame
    // hasn't been reflowed yet, e.g. it's in a subtree whose contents are
    // skipped by content-visibility property.
    return;
  }

  // Move all continuation frames by the same amount.
  const nsPoint translation = ComputePosition(aFrame) - normalPosition;
  for (nsIFrame* cont = aFrame; cont;
       cont = nsLayoutUtils::GetNextContinuationOrIBSplitSibling(cont)) {
    cont->SetPosition(cont->GetNormalPosition() + translation);
  }
}

void StickyScrollContainer::UpdatePositions(nsPoint aScrollPosition,
                                            nsIFrame* aSubtreeRoot) {
#ifdef DEBUG
  {
    nsIFrame* scrollFrameAsFrame = do_QueryFrame(mScrollContainerFrame);
    NS_ASSERTION(!aSubtreeRoot || aSubtreeRoot == scrollFrameAsFrame,
                 "If reflowing, should be reflowing the scroll frame");
  }
#endif
  mScrollPosition = aScrollPosition;

  OverflowChangedTracker oct;
  oct.SetSubtreeRoot(aSubtreeRoot);
  // We need to position ancestors before children, so iter from shallowest.
  for (nsIFrame* f : mFrames.IterFromShallowest()) {
    // mFrames only contains primary frames, because we only register in
    // nsIFrame::HandlePrimaryFrameStyleChange().
    MOZ_ASSERT(nsLayoutUtils::IsFirstContinuationOrIBSplitSibling(f),
               "Only primary frames should have been registered");
    if (aSubtreeRoot) {
      // Reflowing the scroll frame, so recompute offsets.
      ComputeStickyOffsets(f);
    }
    PositionContinuations(f);

    f = f->GetParent();
    if (f != aSubtreeRoot) {
      for (nsIFrame* cont = f; cont;
           cont = nsLayoutUtils::GetNextContinuationOrIBSplitSibling(cont)) {
        oct.AddFrame(cont, OverflowChangedTracker::CHILDREN_CHANGED);
      }
    }
  }
  oct.Flush();
}
}
using mozilla::StickyScrollContainer;
nsPoint nsIFrame::GetNormalPosition(bool* aHasProperty) const {
  bool hasProperty;
  nsPoint normalPosition = GetProperty(NormalPositionProperty(), &hasProperty);
  if (aHasProperty) {
    *aHasProperty = hasProperty;
  }
  return hasProperty ? normalPosition : GetPosition();
}
void nsIFrame::SetPosition(const nsPoint& aPt) {
  if (mRect.TopLeft() == aPt) {
    return;
  }
  mRect.MoveTo(aPt);
  MarkNeedsDisplayItemRebuild();
}
nsPoint nsIFrame::GetPositionIgnoringScrollingAndSticky() const {
  if (IsStickyPositioned()) {
    if (const auto* ssc = StickyScrollContainer::GetForFrame(this)) {
      return GetNormalPosition() +
             ssc->ComputeTranslationIgnoringScrolling(this);
    }
  }
  return GetPositionIgnoringScrolling();
}
int main() {
  try {
    int count; std::cin>>count;
    for(int c=0;c<count;c++) {
      int action,target,reflow,n,np;nscoord sx,sy;
      std::cin>>action>>target>>reflow>>n>>np>>sx>>sy;
      std::vector<nsIFrame> frames(n);
      mozilla::ScrollContainerFrame root;root.id=n;root.first=&root;
      std::vector<int> first(n),next(n),parent(n);
      auto readPoint=[](nsPoint& p){std::cin>>p.x>>p.y;};
      auto readRect=[](nsRect& r){std::cin>>r.x>>r.y>>r.width>>r.height;};
      auto readOffsets=[](std::optional<nsMargin>& o){int present;nsMargin m;std::cin>>present>>m.top>>m.right>>m.bottom>>m.left;if(present)o=m;else o.reset();};
      for(int i=0;i<n;i++) {
        auto& f=frames[i];f.id=i;nsPoint current;
        std::cin>>first[i]>>next[i]>>parent[i]>>f.depth>>f.hadNormal>>f.sticky>>f.hasContainer>>f.geometryAvailable;
        readPoint(f.normal);readPoint(current);f.mRect.MoveTo(current);readPoint(f.fallback);
        readOffsets(f.offsets);readOffsets(f.recomputed);
        readRect(f.currentStick);readRect(f.currentContain);readRect(f.ignoreStick);readRect(f.ignoreContain);
      }
      auto frame=[&](int id)->nsIFrame* {if(id==-2)return &root;if(id==-1)return nullptr;return &frames.at(id);};
      for(int i=0;i<n;i++){frames[i].first=frame(first[i]);frames[i].next=frame(next[i]);frames[i].parent=frame(parent[i]);}
      mozilla::StickyScrollContainer s;s.mScrollContainerFrame=&root;s.mScrollPosition={sx,sy};mozilla::StickyScrollContainer::active=&s;
      for(int i=0;i<np;i++){int id;std::cin>>id;s.mFrames.frames.push_back(frame(id));}
      if(!std::cin)throw std::runtime_error("input");
      trace.clear();nsPoint value;bool hasValue=true;
      auto* f=frame(target);
      if(action==0)value=s.ComputePosition(f);
      else if(action==1)value=s.ComputePositionIgnoringScrolling(f);
      else if(action==2)value=s.ComputeTranslationIgnoringScrolling(f);
      else if(action==3){s.PositionContinuations(f);hasValue=false;}
      else if(action==4){s.UpdatePositions({sx,sy},reflow?&root:nullptr);hasValue=false;}
      else if(action==5)value=f->GetPositionIgnoringScrollingAndSticky();
      else if(action==6)value={s.IsStuckInYDirection(f)?1:0,0};
      else throw std::runtime_error("action");
      std::cout<<"{\"value\":";
      if(hasValue)std::cout<<"["<<value.x<<","<<value.y<<"]";else std::cout<<"null";
      std::cout<<",\"frames\":[";
      for(int i=0;i<n;i++){if(i)std::cout<<",";auto p=frames[i].GetPosition();std::cout<<"["<<p.x<<","<<p.y<<"]";}
      std::cout<<"],\"trace\":[";
      for(size_t i=0;i<trace.size();i++){if(i)std::cout<<",";std::cout<<"\""<<trace[i]<<"\"";}
      std::cout<<"]}\n";
    }
    std::string extra;if(std::cin>>extra)throw std::runtime_error("trailing input");
  } catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 2;}
}
