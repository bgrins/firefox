#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#define MOZ_ASSERT(x, ...) assert(x)
#define MOZ_DIAGNOSTIC_ASSERT(x, ...) assert(x)
#define NS_ASSERTION(x, ...) assert(x)
#define ANCHOR_LOG(...) ((void)0)
#define AUTO_PROFILER_LABEL(...) ((void)0)

using nscoord = int;
struct nsPoint { int x = 0, y = 0; };
struct nsRect {
  int x = 0, y = 0, w = 0, h = 0;
  bool IntersectRect(nsRect a, nsRect b) {
    x = std::max(a.x, b.x); y = std::max(a.y, b.y);
    w = std::min(a.x + a.w, b.x + b.w) - x;
    h = std::min(a.y + a.h, b.y + b.h) - y;
    if (w <= 0 || h <= 0) { w = h = 0; return false; }
    return true;
  }
  bool IsEqualEdges(nsRect b) const {
    return x == b.x && y == b.y && w == b.w && h == b.h;
  }
};
std::vector<std::string> events;
void emit(const std::string& s, int id) { events.push_back(s + std::to_string(id)); }
enum class StylePositionProperty { Static, Relative, Absolute, Fixed, Sticky };
namespace mozilla {
enum class StyleOverflowAnchor { Auto, None };
namespace dom {
struct Content { bool text = false, chrome = false; bool ChromeOnlyAccess() const { return chrome; } };
struct Text {
  static Content* FromNodeOrNull(Content* p) { return p && p->text ? p : nullptr; }
};
}
namespace StaticPrefs {
bool enabled = true, highlight = false;
bool layout_css_scroll_anchoring_enabled() { return enabled; }
bool layout_css_scroll_anchoring_highlight() { return highlight; }
}
}
using namespace mozilla;
using namespace mozilla::dom;
struct nsStyleDisplay {
  StylePositionProperty mPosition = StylePositionProperty::Static;
  StyleOverflowAnchor mOverflowAnchor = StyleOverflowAnchor::Auto;
  bool inlineInside = false;
  bool IsInlineInsideStyle() const { return inlineInside; }
};
struct ComputedStyle {
  bool pseudo = false, anon = false;
  bool IsPseudoElement() const { return pseudo; }
  bool IsAnonBox() const { return anon; }
};
struct WritingMode { bool vertical = false; bool IsVertical() const { return vertical; } };
constexpr int NS_FRAME_HAS_DIRTY_CHILDREN = 1;
enum class FrameChildListID { Principal, Absolute, Float, OverflowFloats, Fixed, Other };
struct nsIFrame;
struct nsFrameList {
  std::vector<nsIFrame*> values;
  auto begin() const { return values.begin(); }
  auto end() const { return values.end(); }
};
namespace mozilla { namespace layout { struct ScrollAnchorContainer; } }
struct ScrollContainerFrame;
struct nsIFrame {
  int id = 0;
  nsIFrame* parent = nullptr;
  nsIFrame* real = nullptr;
  nsIFrame* prev = nullptr;
  nsIFrame* nextContinuation = nullptr;
  nsStyleDisplay display;
  ComputedStyle style;
  Content content;
  bool hasContent = true, sticky = false, br = false, replaced = false;
  bool chain = false, dirty = false, perspective = false, scrollable = false;
  WritingMode wm;
  nsPoint logical{0, 100};
  nsRect bounds{0, 0, 10, 10};
  nsRect viewport{0, 0, 100, 100};
  int offset = 0;
  std::vector<std::pair<nsFrameList, FrameChildListID>> lists;
  nsFrameList empty;
  virtual ~nsIFrame() = default;
  Content* GetContent() const { return hasContent ? const_cast<Content*>(&content) : nullptr; }
  nsIFrame* GetPrevContinuation() const { emit("E", id); return prev; }
  const nsStyleDisplay* StyleDisplay() const { return &display; }
  const ComputedStyle* Style() const { return &style; }
  bool IsStickyPositioned() const { return sticky; }
  bool IsBrFrame() const { return br; }
  bool IsReplaced() const { return replaced; }
  bool IsPlaceholderFrame() const { return real != nullptr; }
  nsIFrame* GetOutOfFlowFrame() const { emit("H", id); return real; }
  nsIFrame* GetParent() const { return parent; }
  bool IsInScrollAnchorChain() const { return chain; }
  void SetInScrollAnchorChain(bool b) { chain = b; events.push_back("F" + std::to_string(id) + ":" + std::to_string(b)); }
  nsIFrame* FirstContinuation() { return this; }
  nsIFrame* GetNextContinuation() const { return nextContinuation; }
  void InvalidateFrame() { emit("I", id); }
  bool HasAnyStateBits(int) const { return dirty; }
  const auto& ChildLists() const { emit("L", id); return lists; }
  const nsFrameList& GetChildList(FrameChildListID kind) const {
    emit("A", id);
    for (const auto& item : lists) if (item.second == kind) return item.first;
    return empty;
  }
  WritingMode GetWritingMode() const { return wm; }
  nsPoint GetLogicalScrollPosition() const { return logical; }
  bool ChildrenHavePerspective() const { return perspective; }
  nsRect GetVisualOptimalViewingRect() const { return viewport; }
};
struct nsPlaceholderFrame : nsIFrame {
  /*PLACEHOLDER_HELPERS*/
};
struct ScrollContainerFrame : nsPlaceholderFrame {
  mozilla::layout::ScrollAnchorContainer* anchor = nullptr;
  nsIFrame* mScrolledFrame = nullptr;
  auto* Anchor() const { return anchor; }
};
ScrollContainerFrame* do_QueryFrame(nsIFrame* f) {
  emit("Q", f->id);
  return f->scrollable ? static_cast<ScrollContainerFrame*>(f) : nullptr;
}
namespace nsLayoutUtils {
bool IsProperAncestorFrame(nsIFrame* owner, nsIFrame* f) {
  bool answer = false;
  for (auto* p = f->parent; p; p = p->parent) if (p == owner) answer = true;
  events.push_back("P" + std::to_string(f->id) + ":" + std::to_string(answer));
  return answer;
}
}
namespace mozilla::layout {
struct ScrollAnchorContainer {
  /*EXAMINE_ENUM*/
  ScrollContainerFrame* owner = nullptr;
  nsIFrame* mAnchorNode = nullptr;
  bool mDisabled = false, mAnchorNodeIsDirty = true, mAnchorMightBeSubOptimal = false;
  int mLastAnchorOffset = 0;
  ScrollContainerFrame* Frame() const { return owner; }
  nsIFrame* AnchorNode() const { return mAnchorNode; }
  bool CanMaintainAnchor() const;
  void SelectAnchor();
  ExamineResult ExamineAnchorCandidate(nsIFrame*) const;
  nsIFrame* FindAnchorIn(nsIFrame*) const;
  nsIFrame* FindAnchorInList(const nsFrameList&) const;
};
nsRect FindScrollAnchoringBoundingRect(const nsIFrame*, nsIFrame* f) {
  emit("B", f->id); return f->bounds;
}
nscoord FindScrollAnchoringBoundingOffset(const ScrollContainerFrame*, nsIFrame* f) {
  emit("O", f->id); return f->offset;
}
/*EXTRACTED_FUNCTIONS*/
}

int main() {
  using mozilla::layout::ScrollAnchorContainer;
  int caseId, mode, count, rootEnabled, rootHighlight, oldId;
  while (std::cin >> caseId >> mode >> count >> rootEnabled >> rootHighlight >> oldId) {
    assert(count >= 2 && count <= 64);
    std::vector<std::unique_ptr<ScrollContainerFrame>> owned;
    std::vector<ScrollAnchorContainer> anchors(static_cast<size_t>(count));
    for (int i = 0; i < count; ++i) owned.push_back(std::make_unique<ScrollContainerFrame>());
    std::vector<int> parents(count), targets(count), previous(count), nested(count);
    for (int i = 0; i < count; ++i) {
      auto& f = *owned[i]; auto& a = anchors[i];
      f.id = i; f.anchor = &a; a.owner = &f;
      int pos, bits, disabled, logx, logy;
      std::cin >> parents[i] >> targets[i] >> previous[i] >> pos >> bits >> nested[i]
        >> disabled >> logx >> logy >> f.bounds.x >> f.bounds.y >> f.bounds.w >> f.bounds.h >> f.offset;
      assert(pos >= 0 && pos <= 4);
      f.display.mPosition = static_cast<StylePositionProperty>(pos);
      f.content.text = bits & 1; f.sticky = bits & 2; f.br = bits & 4;
      f.content.chrome = bits & 8; f.style.pseudo = bits & 16; f.replaced = bits & 32;
      f.display.inlineInside = bits & 64; f.style.anon = bits & 128;
      f.scrollable = bits & 256; f.dirty = bits & 512; f.perspective = bits & 1024;
      f.wm.vertical = bits & 2048; f.hasContent = !(bits & 4096);
      f.display.mOverflowAnchor = bits & 8192 ? StyleOverflowAnchor::None : StyleOverflowAnchor::Auto;
      a.mDisabled = disabled; f.logical = {logx, logy};
    }
    for (int i = 0; i < count; ++i) {
      auto& f = *owned[i];
      auto ptr = [&](int x) -> nsIFrame* { assert(x >= -1 && x < count); return x < 0 ? nullptr : owned[x].get(); };
      f.parent = ptr(parents[i]); f.real = ptr(targets[i]); f.prev = ptr(previous[i]);
      anchors[i].mAnchorNode = ptr(nested[i]);
      int listCount; std::cin >> listCount; assert(listCount >= 0 && listCount <= 6);
      for (int l = 0; l < listCount; ++l) {
        int kind, size; std::cin >> kind >> size; assert(kind >= 0 && kind <= 5 && size >= 0 && size <= 64);
        nsFrameList list;
        for (int j = 0; j < size; ++j) { int id; std::cin >> id; assert(id >= 0 && id < count); list.values.push_back(owned[id].get()); }
        f.lists.emplace_back(std::move(list), static_cast<FrameChildListID>(kind));
      }
    }
    assert(std::cin.good());
    owned[0]->mScrolledFrame = owned[1].get();
    auto& a = anchors[0];
    assert(oldId >= -1 && oldId < count);
    a.mAnchorNode = oldId < 0 ? nullptr : owned[oldId].get();
    for (auto* f = a.mAnchorNode; f && f != owned[1].get(); f = f->parent) f->chain = true;
    StaticPrefs::enabled = rootEnabled; StaticPrefs::highlight = rootHighlight;
    events.clear();
    int result = -1;
    if (mode == 0) { a.SelectAnchor(); result = a.mAnchorNode ? a.mAnchorNode->id : -1; }
    else { assert(mode == 1 && count >= 3); result = static_cast<int>(a.ExamineAnchorCandidate(owned[2].get())); }
    std::cout << caseId << ' ' << result << ' ' << a.mLastAnchorOffset << ' '
      << a.mAnchorNodeIsDirty << ' ' << a.mAnchorMightBeSubOptimal;
    for (auto& f : owned) std::cout << ' ' << f->chain;
    std::cout << '|'; for (const auto& e : events) std::cout << e << ';'; std::cout << '\n';
  }
}
