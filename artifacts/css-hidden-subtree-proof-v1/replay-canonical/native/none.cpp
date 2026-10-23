#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <unordered_set>
#include <vector>

constexpr uint32_t NS_FRAME_IS_DIRTY = 1;
constexpr uint32_t NS_FRAME_HAS_DIRTY_CHILDREN = 2;
constexpr uint32_t NS_FRAME_OWNS_ANON_BOXES = 4;
#define MOZ_ASSERT(x, ...) assert(x)
template<class T, int N> struct AutoTArray {
  std::vector<T> v;
  void AppendElement(T value) { v.push_back(value); }
  bool IsEmpty() const { return v.empty(); }
  unsigned Length() const { return v.size(); }
  T PopLastElement() { T out = v.back(); v.pop_back(); return out; }
};
class PresShell;
struct StyleRecord { bool IsAnonBox() const { return false; } };
struct nsIFrame;
struct ChildList { std::vector<nsIFrame*> mList; };
struct nsIFrame {
  int id = 0;
  uint32_t state = 0;
  bool hidden = false, table = false;
  nsIFrame* parent = nullptr;
  ::PresShell* shell = nullptr;
  std::vector<ChildList> lists{{}};
  bool HasAnyStateBits(uint32_t bits) const { return state & bits; }
  bool IsSubtreeDirty() const { return HasAnyStateBits(NS_FRAME_IS_DIRTY | NS_FRAME_HAS_DIRTY_CHILDREN); }
  void AddStateBits(uint32_t bits) { state |= bits; }
  bool IsTableColGroupFrame() const { return table; }
  const std::vector<ChildList>& ChildLists() const { return lists; }
  std::vector<ChildList> PrincipalOnly() const { return {lists[0]}; }
  const std::vector<nsIFrame*>& PrincipalChildList() const { return lists[0].mList; }
  nsIFrame* GetInFlowParent() const { return parent; }
  const nsIFrame* GetContent() const { return this; }
  ::PresShell* PresShell() const { return shell; }
  const StyleRecord* Style() const { static StyleRecord s; return &s; }
  bool HidesContent() const { return hidden; }
  bool HidesContentForLayout() const;
  bool IsHiddenByContentVisibilityOfInFlowParentForLayout() const;
  bool IsPlaceholderFrame() const { return false; }
  void MarkIntrinsicISizesDirty() {}
  void MarkSubtreeDirty();
  void MarkPrincipalChildrenDirty();
};
enum class IntrinsicDirty { None };
enum class FlushType { Layout };
struct FrameSet {
  std::unordered_set<const nsIFrame*> values;
  bool IsEmpty() const { return values.empty(); }
  void Insert(const nsIFrame* frame) { values.insert(frame); }
  bool Contains(const nsIFrame* frame) const { return values.contains(frame); }
  void Clear() { values.clear(); }
};
struct Document {
  int flushes = 0;
  void FlushPendingNotifications(FlushType) { ++flushes; }
};
class PresShell {
public:
  FrameSet mHiddenContentInForcedLayout;
  Document* mDocument;
  int forces = 0;
  void FrameNeedsReflow(nsIFrame*, IntrinsicDirty, uint32_t) { ++forces; }
  void UpdateHiddenContentInForcedLayout(nsIFrame*);
  void EnsureReflowIfFrameHasHiddenContent(nsIFrame*);
  bool IsForcingLayoutForHiddenContent(const nsIFrame*) const;
  bool ReflowForHiddenContentIfNeeded();
};
struct nsReflowStatus {};
struct Result { int end; nsReflowStatus status; };
struct CandidateFlex : nsIFrame { Result HiddenGuard(); };

struct nsPlaceholderFrame : nsIFrame { nsIFrame* GetOutOfFlowFrame() const { return nullptr; } };
namespace nsLayoutUtils { bool IsProperAncestorFrame(nsIFrame*, nsIFrame*) { return false; } }

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
void nsIFrame::MarkPrincipalChildrenDirty() {
  for (nsIFrame* childFrame : PrincipalChildList()) {
    childFrame->MarkSubtreeDirty();
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
void PresShell::EnsureReflowIfFrameHasHiddenContent(nsIFrame* aFrame) {
  MOZ_ASSERT(mHiddenContentInForcedLayout.IsEmpty());

  UpdateHiddenContentInForcedLayout(aFrame);
  ReflowForHiddenContentIfNeeded();
}
bool PresShell::IsForcingLayoutForHiddenContent(const nsIFrame* aFrame) const {
  return mHiddenContentInForcedLayout.Contains(aFrame->GetContent());
}
bool PresShell::ReflowForHiddenContentIfNeeded() {
  if (mHiddenContentInForcedLayout.IsEmpty()) {
    return false;
  }
  mDocument->FlushPendingNotifications(FlushType::Layout);
  mHiddenContentInForcedLayout.Clear();
  return true;
}
void ProduceDirty(nsIFrame* subtreeRoot) { const bool frameAncestorAndDescendantISizesDirty = false; const bool dirty = true; const uint32_t aBitToAdd = NS_FRAME_IS_DIRTY; AutoTArray<nsIFrame*, 4> subtrees; subtreeRoot->AddStateBits(aBitToAdd);
if (frameAncestorAndDescendantISizesDirty || dirty) {
      // Mark all descendants dirty (using an nsTArray stack rather than
      // recursion).
      // Note that ReflowInput::InitResizeFlags has some similar
      // code; see comments there for how and why it differs.
      AutoTArray<nsIFrame*, 32> stack;
      stack.AppendElement(subtreeRoot);

      do {
        nsIFrame* f = stack.PopLastElement();

        if (frameAncestorAndDescendantISizesDirty && f->IsPlaceholderFrame()) {
          // Call `GetOutOfFlowFrame` directly because we can get here from
          // frame destruction and the placeholder might be already torn down.
          if (nsIFrame* oof =
                  static_cast<nsPlaceholderFrame*>(f)->GetOutOfFlowFrame()) {
            if (!nsLayoutUtils::IsProperAncestorFrame(subtreeRoot, oof)) {
              // We have another distinct subtree we need to mark.
              subtrees.AppendElement(oof);
            }
          }
        }

        for (const auto& childList : f->ChildLists()) {
          for (nsIFrame* kid : childList.mList) {
            if (frameAncestorAndDescendantISizesDirty) {
              kid->MarkIntrinsicISizesDirty();
            }
            if (dirty) {
              kid->AddStateBits(NS_FRAME_IS_DIRTY);
            }
            stack.AppendElement(kid);
          }
        }
      } while (stack.Length() != 0);
    }
}
Result CandidateFlex::HiddenGuard() {
if (HidesContentForLayout()) {
    MarkPrincipalChildrenDirty();
    return {0, nsReflowStatus()};
  }
return {1, {}};
}
int main() {
  int id = 0;
  for (int produce = 0; produce < 2; ++produce)
  for (int hidden = 0; hidden < 2; ++hidden)
  for (unsigned mask = 0; mask < 128; ++mask)
  for (unsigned hm = 0; hm < 4; ++hm)
  for (int tm = 0; tm < 3; ++tm) {
    Document document;
    PresShell shell;
    shell.mDocument = &document;
    CandidateFlex root;
    nsIFrame f[10];
    root.shell = &shell;
    root.hidden = hidden;
    root.state = mask & 64 ? NS_FRAME_IS_DIRTY : 0;
    for (int i = 1; i <= 9; ++i) { f[i].id = i; f[i].shell = &shell; }
    for (int i = 1; i <= 6; ++i) f[i].state = mask & (1u << (i - 1)) ? NS_FRAME_IS_DIRTY : 0;
    if (hm & 1) f[1].AddStateBits(NS_FRAME_HAS_DIRTY_CHILDREN);
    if (hm & 2) f[4].AddStateBits(NS_FRAME_HAS_DIRTY_CHILDREN);
    f[1].table = tm == 2;
    f[2].table = tm == 1;
    root.lists = {{{&f[1], &f[6]}}, {{&f[7]}}};
    f[1].lists = {{{&f[2]}}, {{&f[3]}}};
    f[2].lists = {{{&f[4]}}};
    f[3].lists = {{{&f[5]}}};
    f[1].parent = f[6].parent = f[7].parent = &root;
    f[2].parent = f[3].parent = &f[1];
    f[4].parent = &f[2];
    f[5].parent = &f[3];
    if (produce) ProduceDirty(&f[1]);
    root.HiddenGuard();
    std::cout << id++ << ',' << root.HasAnyStateBits(NS_FRAME_IS_DIRTY);
    for (int n : {1, 2, 4, 3, 5, 6, 7, 8, 9}) {
      int before = shell.forces;
      shell.EnsureReflowIfFrameHasHiddenContent(&f[n]);
      std::cout << ',' << n << ',' << f[n].HasAnyStateBits(NS_FRAME_IS_DIRTY)
                << ',' << f[n].IsSubtreeDirty() << ',' << (shell.forces - before);
      assert(shell.mHiddenContentInForcedLayout.IsEmpty());
    }
    std::cout << '\n';
  }
}
