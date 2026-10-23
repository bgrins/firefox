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
