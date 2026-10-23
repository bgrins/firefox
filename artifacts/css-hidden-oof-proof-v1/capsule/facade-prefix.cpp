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
