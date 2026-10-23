#include <cassert>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

constexpr uint32_t NS_FRAME_IS_DIRTY = 1, NS_FRAME_HAS_DIRTY_CHILDREN = 2;
constexpr uint32_t NS_FRAME_OWNS_ANON_BOXES = 4, NS_FRAME_OUT_OF_FLOW = 8;
constexpr uint32_t NS_FRAME_IN_REFLOW = 16, NS_FRAME_FIRST_REFLOW = 32;
#define MOZ_ASSERT(x, ...) assert(x)
template<class T, int N> struct AutoTArray {
  std::vector<T> v;
  void AppendElement(T value) { v.push_back(value); }
  bool IsEmpty() const { return v.empty(); }
  T PopLastElement() { T value = v.back(); v.pop_back(); return value; }
};
struct nsIFrame;
using nsContainerFrame = nsIFrame;
struct PresShell;
struct ReflowInput;
struct StyleSizeOverrides {};
struct Rect { int32_t x, y, w, h; };
struct LogicalSize {
  int32_t i, b;
  LogicalSize(int, int32_t ii, int32_t bb) : i(ii), b(bb) {}
  int32_t ISize(int) const { return i; }
  LogicalSize ConvertTo(int, int) const { return *this; }
};
template<class T> T Some(T v) { return v; }
struct ReflowOutput {
  int32_t width = 0, height = 0;
  explicit ReflowOutput(const ReflowInput&) {}
};
struct StyleRecord { bool anon = false; bool IsAnonBox() const { return anon; } };
struct ChildList { std::vector<nsIFrame*> mList; };
struct nsIFrame {
  uint32_t state = 0;
  bool hidden = false, table = false, next = false;
  nsIFrame *parent = nullptr, *placeholder = nullptr, *first = nullptr;
  ::PresShell* shell = nullptr;
  StyleRecord style;
  std::vector<ChildList> lists{{}};
  Rect rect{6240, 600, 720, 480};
  bool HasAnyStateBits(uint32_t b) const { return state & b; }
  bool IsSubtreeDirty() const { return HasAnyStateBits(NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN); }
  void AddStateBits(uint32_t b) { state |= b; }
  void RemoveStateBits(uint32_t b) { state &= ~b; }
  bool IsTableColGroupFrame() const { return table; }
  const std::vector<ChildList>& ChildLists() const { return lists; }
  nsIFrame* FirstContinuation() const { return first; }
  static int PlaceholderFrameProperty() { return 1; }
  nsIFrame* GetProperty(int) const { return placeholder; }
  nsContainerFrame* GetParent() const { return parent; }
  nsContainerFrame* GetInFlowParent() const;
  const nsIFrame* GetContent() const { return this; }
  ::PresShell* PresShell() const { return shell; }
  const StyleRecord* Style() const { return &style; }
  bool HidesContent() const { return hidden; }
  bool HidesContentForLayout() const;
  bool IsHiddenByContentVisibilityOfInFlowParentForLayout() const;
  nsIFrame* GetNextContinuation() const { return next ? first : nullptr; }
  void MarkSubtreeDirty();
  void FinishAndStoreOverflow(ReflowOutput*, int) {}
  void Reflow(void*, ReflowOutput&, const ReflowInput&, int&);
  void DidReflow(void*, const ReflowInput*);
  void SetRect(Rect r) { rect = r; }
};
enum class IntrinsicDirty { None };
struct FrameSet {
  std::unordered_set<const nsIFrame*> values;
  bool IsEmpty() const { return values.empty(); }
  void Insert(const nsIFrame* f) { values.insert(f); }
  bool Contains(const nsIFrame* f) const { return values.contains(f); }
};
struct PresShell {
  FrameSet mHiddenContentInForcedLayout;
  int forces = 0;
  void FrameNeedsReflow(nsIFrame*, IntrinsicDirty, uint32_t) { ++forces; }
  void UpdateHiddenContentInForcedLayout(nsIFrame*);
  bool IsForcingLayoutForHiddenContent(const nsIFrame*) const;
};
bool inputDiffers = false;
struct ReflowInput {
  nsIFrame* mFrame = nullptr;
  int mStyleDisplay = 0;
  bool iResize = false;
  ReflowInput() = default;
  ReflowInput(void*, const ReflowInput&, nsIFrame* f, LogicalSize, LogicalSize,
              int, StyleSizeOverrides, int, void*) : mFrame(f) { InitResizeFlag(inputDiffers); }
  void SetIResize(bool b) { iResize = b; }
  void InitResizeFlag(bool);
};

void nsIFrame::MarkSubtreeDirty() {
  if (HasAnyStateBits(NS_FRAME_IS_DIRTY)) {
    return;
  }
  // Unconditionally mark given frame dirty.
  AddStateBits(NS_FRAME_IS_DIRTY);

  // Mark all descendants dirty, unless:
  // - Already dirty.
  // - TableColGroup
  AutoTArray<nsIFrame*, 32> stack;
  for (const auto& childLists : ChildLists()) {
    for (nsIFrame* kid : childLists.mList) {
      stack.AppendElement(kid);
    }
  }
  while (!stack.IsEmpty()) {
    nsIFrame* f = stack.PopLastElement();
    if (f->HasAnyStateBits(NS_FRAME_IS_DIRTY) || f->IsTableColGroupFrame()) {
      continue;
    }

    f->AddStateBits(NS_FRAME_IS_DIRTY);

    for (const auto& childLists : f->ChildLists()) {
      for (nsIFrame* kid : childLists.mList) {
        stack.AppendElement(kid);
      }
    }
  }
}
bool nsIFrame::HidesContentForLayout() const {
  return HidesContent() && !PresShell()->IsForcingLayoutForHiddenContent(this);
}
bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const {
  const auto* parent = GetInFlowParent();
  // The anonymous children owned by parent are important for properly sizing
  // their parents.
  return parent && parent->HidesContentForLayout() &&
         !(parent->HasAnyStateBits(NS_FRAME_OWNS_ANON_BOXES) &&
           Style()->IsAnonBox());
}
nsContainerFrame* nsIFrame::GetInFlowParent() const {
  if (HasAnyStateBits(NS_FRAME_OUT_OF_FLOW)) {
    nsIFrame* ph =
        FirstContinuation()->GetProperty(nsIFrame::PlaceholderFrameProperty());
    return ph->GetParent();
  }

  return GetParent();
}
void PresShell::UpdateHiddenContentInForcedLayout(nsIFrame* aFrame) {
  if (!aFrame || !aFrame->IsSubtreeDirty()) {
    return;
  }

  nsIFrame* topmostFrameWithContentHidden = nullptr;
  for (nsIFrame* cur = aFrame->GetInFlowParent(); cur;
       cur = cur->GetInFlowParent()) {
    if (cur->HidesContent()) {
      topmostFrameWithContentHidden = cur;
      mHiddenContentInForcedLayout.Insert(cur->GetContent());
    }
  }

  if (mHiddenContentInForcedLayout.IsEmpty()) {
    return;
  }

  // Queue and immediately flush a reflow for this node.
  MOZ_ASSERT(topmostFrameWithContentHidden);
  FrameNeedsReflow(topmostFrameWithContentHidden, IntrinsicDirty::None,
                   NS_FRAME_IS_DIRTY);
}
bool PresShell::IsForcingLayoutForHiddenContent(const nsIFrame* aFrame) const {
  return mHiddenContentInForcedLayout.Contains(aFrame->GetContent());
}
void ReflowInput::InitResizeFlag(bool isIResize) {SetIResize(!mFrame->HasAnyStateBits(NS_FRAME_IS_DIRTY) && isIResize);}
void nsIFrame::Reflow(void*, ReflowOutput& aMetrics, const ReflowInput& aReflowInput, int&) {if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&
      !GetNextContinuation()) {
    FinishAndStoreOverflow(&aMetrics, aReflowInput.mStyleDisplay);
    return;
  }
aMetrics.width=720; aMetrics.height=480;
}
void nsIFrame::DidReflow(void*, const ReflowInput*) {if (IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
    RemoveStateBits(NS_FRAME_IN_REFLOW | NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN);
    return;
  }
RemoveStateBits(NS_FRAME_IN_REFLOW | NS_FRAME_FIRST_REFLOW |
                  NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN);}

 bool Execute(int timing, nsIFrame* aKidFrame) {
 void* aPresContext = nullptr;
 ReflowInput aReflowInput;
 const int outerWM = 0, wm = 0, initFlags = 0;
 const LogicalSize cbSize(outerWM, 12000, 4800), availSize(outerWM, 12000, 4800);
 StyleSizeOverrides sizeOverrides;
 void* aAnchorPosResolutionCache = nullptr;
 int aStatus = 0;
 if (timing == 1) {if (aKidFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
      aKidFrame->MarkSubtreeDirty();
    }}
ReflowInput kidReflowInput(aPresContext, aReflowInput, aKidFrame,
                               availSize.ConvertTo(wm, outerWM),
                               Some(cbSize.ConvertTo(wm, outerWM)), initFlags,
                               sizeOverrides, {}, aAnchorPosResolutionCache);
if (timing == 2) {if (aKidFrame->IsHiddenByContentVisibilityOfInFlowParentForLayout()) {
      aKidFrame->MarkSubtreeDirty();
    }}
ReflowOutput kidDesiredSize(kidReflowInput);
    aKidFrame->Reflow(aPresContext, kidDesiredSize, kidReflowInput, aStatus);
 Rect r{600+(12000-kidDesiredSize.width)/2,600,kidDesiredSize.width,kidDesiredSize.height};
 aKidFrame->SetRect(r);
aKidFrame->DidReflow(aPresContext, &kidReflowInput);
return kidReflowInput.iResize;
}
int main() {
  int row = 0;
  for (int timing = 0; timing < 3; ++timing)
    for (int dm = 0; dm < 8; ++dm)
      for (int hm = 0; hm < 4; ++hm)
        for (int ph = 0; ph < 2; ++ph)
          for (int next = 0; next < 2; ++next)
            for (int differs = 0; differs < 2; ++differs)
              for (int table = 0; table < 2; ++table)
                for (int owner = 0; owner < 2; ++owner)
                  for (int anon = 0; anon < 2; ++anon) {
                    PresShell shell;
                    nsIFrame root, mid, leaf, flow, host, physicalOwner, placeholder;
                    for (nsIFrame* f : {&root, &mid, &leaf, &flow, &host, &physicalOwner, &placeholder}) {
                      f->shell = &shell;
                      f->first = f;
                    }
                    root.parent = &physicalOwner;
                    root.placeholder = &placeholder;
                    placeholder.parent = &flow;
                    flow.parent = &host;
                    flow.hidden = ph;
                    flow.state = NS_FRAME_OWNS_ANON_BOXES;
                    physicalOwner.hidden = owner;
                    root.state = (dm & 1) | ((hm & 1) << 1) | NS_FRAME_OUT_OF_FLOW;
                    mid.state = (dm >> 1) & 1;
                    leaf.state = ((dm >> 2) & 1) | (hm & 2);
                    mid.table = table;
                    root.next = next;
                    root.style.anon = anon;
                    root.lists[0].mList = {&mid};
                    mid.parent = &root;
                    mid.lists[0].mList = {&leaf};
                    leaf.parent = &mid;
                    inputDiffers = differs;
                    bool resize = Execute(timing, &root);
                    bool rootEligible = root.IsSubtreeDirty(), leafEligible = leaf.IsSubtreeDirty();
                    shell.UpdateHiddenContentInForcedLayout(&leaf);
                    auto r = root.rect;
                    std::cout << row++ << ',' << timing << ',' << dm << ',' << hm << ','
                              << ph << ',' << next << ',' << differs << ',' << table << ','
                              << owner << ',' << anon << ',' << resize << ','
                              << (root.state & 3) << ',' << (mid.state & 3) << ',' << (leaf.state & 3) << ','
                              << rootEligible << ',' << leafEligible << ',' << shell.forces << ','
                              << r.x << ',' << r.y << ',' << r.w << ',' << r.h << '\n';
                  }
}
