#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <optional>
#include <set>
#include <string>
#include <utility>
#include <vector>

#define MOZ_ASSERT(condition, ...) assert(condition)
#define NS_ASSERTION(condition, ...) assert(condition)
#define MOZ_LIKELY(value) (value)
using nscoord = int32_t;
template<class T> using UniquePtr = std::unique_ptr<T>;
template<class T> using RefPtr = std::shared_ptr<T>;
template<class T> struct Maybe : std::optional<T> {
  using std::optional<T>::optional;
  T extract() { T value = **this; this->reset(); return value; }
};
template<class T> Maybe<T> Some(const T& value) { return Maybe<T>(value); }

using Event = std::vector<int64_t>;
static std::vector<Event> events;
static size_t attemptCount;
struct WritingMode { bool ltr; bool IsBidiLTR() const { return ltr; } };
struct nsPoint { nscoord x, y; };
struct nsSize { nscoord width, height; };
struct nsRect {
  nscoord x, y, width, height;
  nsRect(nsPoint p, nsSize s) : x(p.x), y(p.y), width(s.width), height(s.height) {}
  nsRect(nscoord a, nscoord b, nscoord c, nscoord d) : x(a), y(b), width(c), height(d) {}
  nsRect operator+(nsPoint p) const { return {x+p.x,y+p.y,width,height}; }
};
struct LogicalPoint {
  nscoord i;
  LogicalPoint(WritingMode wm, nsPoint p, nsSize size) : i(wm.ltr ? p.x : size.width-p.x) {}
  nscoord I(WritingMode) const { return i; }
};
struct LogicalRect {
  nscoord i=0,b=0,w=0,h=0;
  LogicalRect() = default;
  LogicalRect(WritingMode, nscoord a, nscoord c, nscoord d, nscoord e) : i(a),b(c),w(d),h(e) {}
  LogicalRect(WritingMode wm, nsRect r, nsSize size) : i(wm.ltr ? r.x : size.width-r.x-r.width),b(r.y),w(r.width),h(r.height) {}
  nscoord& IStart(WritingMode) { return i; }
  nscoord IStart(WritingMode) const { return i; }
  nscoord IEnd(WritingMode) const { return i+w; }
  nscoord& ISize(WritingMode) { return w; }
  nscoord ISize(WritingMode) const { return w; }
  nscoord BStart(WritingMode) const { return b; }
  bool IntersectRect(const LogicalRect& a, const LogicalRect& c) {
    auto ie=std::min(a.i+a.w,c.i+c.w), be=std::min(a.b+a.h,c.b+c.h);
    i=std::max(a.i,c.i); b=std::max(a.b,c.b); w=ie-i; h=be-b;
    if (w<0 || h<0) w=h=0;
    return w>0 && h>0;
  }
};
static void addRect(Event& e, const LogicalRect& r) { e.insert(e.end(), {r.i,r.b,r.w,r.h}); }
struct Atom {
  int id=0, width=0, length=0;
  bool IsEmpty() const { return length==0; }
};
struct StyleAtomString { Atom atom; const Atom* AsAtom() const { return &atom; } };
struct StyleTextOverflowSide {
  int id=0,kind=0;
  StyleAtomString string;
  bool IsClip() const { return kind==0; }
  bool IsEllipsis() const { return kind==1; }
  bool IsString() const { return kind==2; }
  const StyleAtomString& AsString() const { assert(IsString()); return string; }
};
struct StyleBlockEllipsis {
  int id=0,kind=0;
  StyleAtomString string;
  bool IsNoEllipsis() const { return kind==0; }
  bool IsEllipsis() const { return kind==1; }
  bool IsString() const { return kind==2; }
  const StyleAtomString& AsString() const { assert(IsString()); return string; }
};
struct gfxContext {};
struct nsFontMetrics {};
struct gfxTextRun { int width; nscoord GetAdvanceWidth() const { return width; } };
struct nsDependentAtomString { const Atom* atom; explicit nsDependentAtomString(const Atom* a):atom(a){} };
struct PresShellAdapter { UniquePtr<gfxContext> CreateReferenceRenderingContext() { return std::make_unique<gfxContext>(); } };
struct PresContextAdapter { int units=1; int AppUnitsPerDevPixel() const { return units; } };
enum class LayoutFrameType { Container=0, Text=1, Atomic=2, Br=3, Placeholder=4 };
struct Visibility { bool visible=true; bool IsVisible() const { return visible; } };
struct nsIFrame {
  int id=0;
  LayoutFrameType kind=LayoutFrameType::Container;
  Visibility visibility;
  nsPoint offset{0,0};
  nsSize size{0,1};
  nsRect overflow{0,0,0,1};
  std::vector<nsIFrame*> children;
  PresShellAdapter* shell=nullptr;
  PresContextAdapter* context=nullptr;
  int ellipsisWidth=0;
  bool ellipsisFailure=false;
  virtual ~nsIFrame() = default;
  bool IsBlockFrameOrSubclass() const { return false; }
  bool IsBlockOutside() const { return false; }
  bool IsLineParticipant() const { return kind!=LayoutFrameType::Atomic; }
  LayoutFrameType Type() const { return kind; }
  const Visibility* StyleVisibility() const { return &visibility; }
  nsPoint GetOffsetTo(nsIFrame*) const { return offset; }
  nsSize GetSize() const { return size; }
  nsRect ScrollableOverflowRect() const { return overflow; }
  const std::vector<nsIFrame*>& PrincipalChildList() const { return children; }
  PresShellAdapter* PresShell() const { assert(shell); return shell; }
  PresContextAdapter* PresContext() const { assert(context); return context; }
};
struct nsTextFrame : nsIFrame {
  bool nonsuppressed=true;
  std::vector<int> advances;
  bool HasNonSuppressedText() const { return nonsuppressed; }
  bool MeasureCharClippedText(nscoord left, nscoord right, nscoord* a, nscoord* b) {
    int x=0, first=-1,last=-1;
    for (int advance:advances) {
      assert(advance>0);
      if (x>=left && x+advance<=size.width-right) { if (first<0) first=x; last=x+advance; }
      x+=advance;
    }
    assert(x==size.width);
    if (first<0) return false;
    *a=first; *b=size.width-last;
    return true;
  }
};
struct nsBlockFrame : nsIFrame {
  const StyleBlockEllipsis* clamp=nullptr;
  const StyleBlockEllipsis* GetLineClampBlockEllipsis() const { assert(clamp); return clamp; }
};
struct ScrollContainerFrame {
  nsPoint position{0,0};
  nsRect range{0,0,0,1};
  nsPoint GetScrollPosition() const { return position; }
  nsRect GetScrollRange() const { return range; }
};
struct nsLineBox {
  int id=0;
  bool clamp=false, floats=false;
  int startEdge=0,endEdge=0;
  nsRect overflow{0,0,0,1};
  std::vector<nsIFrame*> frames;
  bool HasLineClampEllipsis() const { return clamp; }
  bool GetFloatEdges(nscoord* a, nscoord* b) const { *a=startEdge; *b=endEdge; return floats; }
  nsRect ScrollableOverflowRect() const { return overflow; }
  const std::vector<nsIFrame*>& ChildFrames() const { return frames; }
};
struct nsDisplayList { int id=0; };
struct nsDisplayListBuilder {};
struct nsDisplayListSet {
  nsDisplayList a{0}, b{1};
  nsDisplayList* Content() const { return const_cast<nsDisplayList*>(&a); }
  nsDisplayList* PositionedDescendants() const { return const_cast<nsDisplayList*>(&b); }
};
struct FrameSet {
  std::set<nsIFrame*> values;
  explicit FrameSet(size_t) {}
  void Insert(nsIFrame* f) { values.insert(f); }
  void Clear() { values.clear(); }
  std::vector<int> ids() const { std::vector<int> out; for(auto* f:values)out.push_back(f->id);std::sort(out.begin(),out.end());return out; }
};
static void addHidden(Event& e, const FrameSet& s) { auto ids=s.ids();e.push_back(ids.size());e.insert(e.end(),ids.begin(),ids.end()); }
namespace nsLayoutUtils {
static RefPtr<nsFontMetrics> GetInflatedFontMetricsForFrame(nsIFrame*) { return std::make_shared<nsFontMetrics>(); }
static nscoord AppUnitWidthOfStringBidi(nsDependentAtomString s,nsIFrame*,nsFontMetrics&,gfxContext&) {
  events.push_back({2,s.atom->id,s.atom->width,0});return s.atom->width;
}
}
static RefPtr<gfxTextRun> MakeEllipsisTextRun(nsIFrame* frame) {
  events.push_back({2,-1,frame->ellipsisFailure?0:frame->ellipsisWidth,frame->ellipsisFailure});
  if (frame->ellipsisFailure) return nullptr;
  return std::make_shared<gfxTextRun>(gfxTextRun{frame->ellipsisWidth});
}

